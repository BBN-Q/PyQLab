"""
Port of APSPattern.m to create APS h5 files from LLs and WFLibraries

Created on Wed May 16 22:43:13 2012

@author: cryan
"""


import h5py
import numpy as np


#Some constants
ADDRESS_UNIT = 4 #everything is done in units of 4 timesteps
MIN_LL_ENTRY_COUNT = 3 #minimum length of mini link list
MAX_WAVEFORM_PTS = 8192 #maximum size of waveform memory
MAX_WAVEFORM_VALUE = 8191 #maximum waveform value i.e. 14bit DAC
MAX_BANK_SIZE = 512 #maximum number of LL entries in a bank

ELL_TIME_AMPLITUDE     = 2**15
ELL_ZERO              = 2**14
ELL_LL_TRIGGER         = 2**13
ELL_FIRST_ENTRY        = 2**12;
ELL_LAST_ENTRY         = 2**11;

#ELL_TA_MAX             = hex2dec('FFFF');
#ELL_TRIGGER_DELAY      = hex2dec('3FFF');
#ELL_TRIGGER_MODE_SHIFT = 14;
#ELL_TRIGGER_DELAY_UNIT = 3.333e-9;



chanStrs = ['ch1','ch2','ch3','ch4']
chanStrs2 = ['chan_1','chan_2','chan_3','chan_4']

def calc_offset(entry, offsets, isFirst=False, isLast=False):
    '''
    Helper function to calculate offset byte word from an entry.

    From APSPattern.m    
    % offset register format
    %  15  14  13   12   11  10 9 8 7 6 5 4 3 2 1 0
    % | A | Z | T | LS | LE |      Offset / 4      |
    %
    %  Address - Address of start of waveform / 4
    %  A       - Time Amplitude Pair
    %  Z       - Output is Zero
    %  T       - Entry has valid output trigger delay
    %  LS      - Start of Mini Link List
    %  LE      - End of Mini Link List
    '''
    
    
    
    #First divide by the APS units
    if entry.isZero:
        offset = 0
    else:
        offset = offsets[entry.key]/4
    
    #Now add in each of the bitflags in turn
    if entry.isTimeAmplitude:
        offset += ELL_TIME_AMPLITUDE
    if entry.isZero:
        offset += ELL_ZERO
    if entry.hasTrigger:
        offset += ELL_LL_TRIGGER
    if isFirst:
        offset += ELL_FIRST_ENTRY
    if isLast:
        offset += ELL_LAST_ENTRY
    
    return offset
    
def calc_trigger(entry):
    '''
    Helper function to calculate trigger LL entries
    
    From APSPattern.m
    % handle trigger values
    %% Trigger Delay
    %  15  14  13   12   11  10 9 8 7 6 5 4 3 2 1 0
    % | Mode |                Delay                |
    % Mode 0 0 = short pulse (0)
    %      0 1 = rising edge (1)
    %      1 0 = falling edge (2)
    %      1 1 = no change (3)
    % Delay = time in 4 sample increments ( 0 - 54.5 usec at max rate)
    '''
    if entry.hasTrigger:
        assert entry.triggerDelay < 65536, 'Oops, maximum trigger delayis 65536 timesteps and you have asked for {0}'.format(entry.triggerDelay)
        triggerVal = 49152 + entry.triggerDelay//ADDRESS_UNIT
    else:
        triggerVal = 0

    return triggerVal
    
def create_empty_bank():
    '''
    Helper function to initialize an empty bank.
    '''
    return {'offset':np.zeros(MAX_BANK_SIZE, dtype=np.uint16), 'count':np.zeros(MAX_BANK_SIZE, dtype=np.uint16), 'trigger':np.zeros(MAX_BANK_SIZE, dtype=np.uint16), 'repeat':np.zeros(MAX_BANK_SIZE, dtype=np.uint16)}
 

def write_bank_to_file(FID, bank, bankGroupStr, trimct=MAX_BANK_SIZE):
    '''
    Helper functionto write a bank dictionary to a group.
    '''
    #First create the group
    bankGroup = FID.create_group(bankGroupStr)
    
    #Write the length attribute
    bankGroup.attrs['length'] = np.int16(trimct)

    #Trim the bank if necessary and write to file
    for key in bank.keys():
        bank[key].resize(trimct)
        FID.create_dataset(bankGroupStr + '/' + key, data=bank[key])
        
def write_APS_file(AWGData, fileName):
    '''
    Main function to pack a bunch of LLs into an APS h5 file
    '''

    #Open the HDF5 file
    FID = h5py.File(fileName, 'w')  
    
    #List of which channels we have data for
    channelDataFor = []
    
    #Loop over the channels
    for chanct, chanStr in enumerate(chanStrs):
        if chanStr in AWGData:
            channelDataFor.append(chanct+1)

            #Create the group
            chanGroup = FID.create_group('/'+chanStrs2[chanct])
            chanGroup.attrs['isLinkListData'] = np.int16(1)
            #Create the waveform data
            idx = 0
            offsets = {}
            waveformLib = np.zeros(MAX_WAVEFORM_PTS, dtype=np.int16)
            for key, WF in AWGData[chanStr]['WFLibrary'].items():
                #Scale the WF
                WF[WF>1] = 1.0
                WF[WF<-1] = -1.0
                waveformLib[idx:idx+WF.size] = np.uint16(MAX_WAVEFORM_VALUE*WF)
                offsets[key] = idx
                idx += WF.size
                
            #Trim the waveform 
            waveformLib = waveformLib[0:idx] 
            
            #Write the waveformLib to file
            FID.create_dataset('/'+chanStrs2[chanct]+'/waveformLib', data=waveformLib)
            
            #Create the LL data group
            LLGroup = FID.create_group('/'+chanStrs2[chanct] + '/linkListData')
            
            #Create the necessary number of banks as we step through the mini LL
            entryct = 0
            tmpBank = create_empty_bank()
            bankct = 1
            for miniLL in AWGData[chanStr]['LLs']:
                LLlength = len(miniLL)
                #The minimum miniLL length is two 
                assert LLlength > 1, 'Oops! mini LL''s needs to have more than 1 element'
                assert LLlength < MAX_BANK_SIZE, 'Oops! mini LL''s cannot have length greater than {0}, you have {1} entries'.format(MAX_BANK_SIZE, len(miniLL))
                #If we need to allocate a new bank
                if entryct + len(miniLL) > MAX_BANK_SIZE:
                    #Write the current bank to file                    
                    write_bank_to_file(FID, tmpBank, '/{0}/linkListData/bank{1}'.format(chanStrs2[chanct], bankct), entryct)
                    #Allocate a new bank
                    tmpBank = create_empty_bank()
                    bankct += 1
                    #Reset the entry count
                    entryct = 0
                
                #Otherwise enter each LL entry into the bank arrays
                for ct, LLentry in enumerate(miniLL):
                    tmpBank['offset'][entryct] = calc_offset(LLentry, offsets, ct==0, ct==LLlength)
                    tmpBank['count'][entryct] = LLentry.length//ADDRESS_UNIT
                    tmpBank['trigger'][entryct] = calc_trigger(LLentry)
                    tmpBank['repeat'][entryct] = LLentry.repeat
                    entryct += 1
                    
            #Write the final bank
            write_bank_to_file(FID, tmpBank, '/{0}/linkListData/bank{1}'.format(chanStrs2[chanct], bankct), entryct)
            
            LLGroup.attrs['numBanks'] = np.int16(bankct)
            LLGroup.attrs['repeatCount'] = np.int16(0)
                
                    
        
    FID['/'].attrs['Version'] = 1.6
    FID['/'].attrs['channelDataFor'] = np.int16(channelDataFor)
    
        
    FID.close()
            
            
                
            
            
            
            
            
            
    
          
    
    

if __name__ == '__main__':

    pass
        
