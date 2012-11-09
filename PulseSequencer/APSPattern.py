"""
Port of APSPattern.m to create APS h5 files from LLs and WFLibraries

Created on Wed May 16 22:43:13 2012

@author: cryan
"""


import h5py
import numpy as np


#Some constants
ADDRESS_UNIT = 4 #everything is done in units of 4 timesteps
MIN_LL_ENTRY_COUNT = 2 #minimum length of mini link list
MAX_WAVEFORM_PTS = 2**14 #maximum size of waveform memory
MAX_WAVEFORM_VALUE = 2**13-1 #maximum waveform value i.e. 14bit DAC
MAX_LL_ENTRIES = 4096 #maximum number of LL entries in a bank
MAX_REPEAT_COUNT = 2^10-1;

#APS bit masks
START_MINILL_BIT = 15;
END_MINILL_BIT = 14;
WAIT_TRIG_BIT = 13;
TA_PAIR_BIT = 12;
        
chanStrs = ['ch1','ch2','ch3','ch4']
mrkStrs = ['ch1m1', 'ch2m1', 'ch3m1', 'ch4m1']
chanStrs2 = ['chan_1','chan_2','chan_3','chan_4']

def calc_offset(entry, offsets):
    '''
    Helper function to calculate offset byte word from an entry.
    '''
    #First divide by the APS units
    offset = offsets[entry.key]//ADDRESS_UNIT
    
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
        triggerVal = 49152

    return triggerVal
    
def create_empty_bank():
    '''
    Helper function to initialize an empty bank.
    '''
    return {'offset':np.zeros(MAX_LL_ENTRIES, dtype=np.uint16), 'count':np.zeros(MAX_LL_ENTRIES, dtype=np.uint16),
            'trigger1':np.zeros(MAX_LL_ENTRIES, dtype=np.uint16), 'trigger2':np.zeros(MAX_LL_ENTRIES, dtype=np.uint16),
            'repeat':np.zeros(MAX_LL_ENTRIES, dtype=np.uint16)}
 

def write_bank_to_file(FID, bank, bankGroupStr, trimct=MAX_LL_ENTRIES):
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
    with h5py.File(fileName, 'w') as FID:  
    
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
                if AWGData[chanStr]['WFLibrary']:
                    for key, WF in AWGData[chanStr]['WFLibrary'].items():
                        #Scale the WF
                        WF[WF>1] = 1.0
                        WF[WF<-1] = -1.0
                        #TA pairs need to be repeated ADDRESS_UNIT times
                        if WF.size == 1:
                            WF = WF.repeat(ADDRESS_UNIT)
                        #Ensure the WF is an integer number of ADDRESS_UNIT's 
                        trim = WF.size%ADDRESS_UNIT
                        if trim:
                            WF = WF[:-trim]
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
                numMiniLLs = len(AWGData[chanStr]['LLs'])
                for miniLLct, miniLL in enumerate(AWGData[chanStr]['LLs']):
                    LLlength = len(miniLL)
                    #The minimum miniLL length is two 
                    assert LLlength >= 3, 'Oops! mini LL''s needs to have at least three elements.'
                    assert LLlength < MAX_BANK_SIZE, 'Oops! mini LL''s cannot have length greater than {0}, you have {1} entries'.format(MAX_BANK_SIZE, len(miniLL))
                    #If we need to allocate a new bank
                    if entryct + len(miniLL) > MAX_BANK_SIZE:
                        #Fix the final entry as we no longer have to indicate the next enty is the start of a miniLL
                        tmpBank['offset'][entryct-1] -= ELL_FIRST_ENTRY
                        #Write the current bank to file
                        write_bank_to_file(FID, tmpBank, '/{0}/linkListData/bank{1}'.format(chanStrs2[chanct], bankct), entryct)
                        #Allocate a new bank
                        tmpBank = create_empty_bank()
                        bankct += 1
                        #Reset the entry count
                        entryct = 0
                    
                    #Otherwise enter each LL entry into the bank arrays
                    for ct, LLentry in enumerate(miniLL):
                        tmpBank['offset'][entryct] = calc_offset(LLentry, offsets, entryct==0 or (ct==LLlength-1 and miniLLct<numMiniLLs-1) , ct==LLlength-2)
                        tmpBank['count'][entryct] = LLentry.length//ADDRESS_UNIT-1
                        tmpBank['trigger'][entryct] = calc_trigger(LLentry)
                        tmpBank['repeat'][entryct] = LLentry.repeat-1
                        entryct += 1
                        
                #Write the final bank
                write_bank_to_file(FID, tmpBank, '/{0}/linkListData/bank{1}'.format(chanStrs2[chanct], bankct), entryct)
                
                LLGroup.attrs['numBanks'] = np.uint16(bankct)
                LLGroup.attrs['repeatCount'] = np.uint16(0)
                    
                        
            
        FID['/'].attrs['Version'] = 2.0
        FID['/'].attrs['channelDataFor'] = np.int16(channelDataFor)
    
    
def read_APS_file(fileName):
    '''
    Helper function to read back in data from a H5 file and reconstruct the sequence
    '''
    AWGData = {}
    #APS bit masks
    START_MINILL_MASK = 2**START_MINILL_BIT;
    TA_PAIR_MASK = 2**TA_PAIR_BIT;
    REPEAT_MASK = 2**10-1
            
    
    with h5py.File(fileName, 'r') as FID:
        chanct = 0
        for chanct, chanStr in enumerate(chanStrs2):
            #If we're in IQ mode then the Q channel gets its linkListData from the I channel
            if FID[chanStr].attrs['isIQMode'][0]:
                tmpChan = 2*(chanct//2)
                curLLData = FID[chanStrs2[tmpChan]]['linkListData']
            else:
                curLLData = FID[chanStr]['linkListData']
            #Pull out the LL data
            tmpAddr = curLLData['addr'].value
            tmpCount = curLLData['count'].value
            tmpRepeat = curLLData['repeat'].value
            tmpTrigger1 = curLLData['trigger1'].value
            tmpTrigger2 = curLLData['trigger2'].value
            numEntries = curLLData.attrs['length'][0]
   
            #Pull out and scale the waveform data
            wfLib =(1.0/MAX_WAVEFORM_VALUE)*FID[chanStr]['waveformLib'].value.flatten()
            
            #Initialize the lists of sequences
            AWGData[chanStrs[chanct]] = []
            AWGData[mrkStrs[chanct]] = []

            #Loop over LL entries
            for entryct in range(numEntries):
                #If we are starting a new entry push back an empty array
                if START_MINILL_MASK & tmpRepeat[entryct]:
                    AWGData[chanStrs[chanct]].append(np.array([], dtype=np.float64))
                    AWGData[mrkStrs[chanct]].append(np.array([], dtype=np.bool))
                #If it is a TA pair or regular pulse
                curRepeat = (tmpRepeat[entryct] & REPEAT_MASK)+1
                if TA_PAIR_MASK & curLLData['repeat'][entryct][0]:
                    AWGData[chanStrs[chanct]][-1] = np.hstack((AWGData[chanStrs[chanct]][-1], 
                                                    np.tile(wfLib[tmpAddr[entryct]*ADDRESS_UNIT:tmpAddr[entryct]*ADDRESS_UNIT+4], curRepeat*(tmpCount[entryct]+1))))
                else:
                    AWGData[chanStrs[chanct]][-1] = np.hstack((AWGData[chanStrs[chanct]][-1], 
                                                    np.tile(wfLib[tmpAddr[entryct]*ADDRESS_UNIT:tmpAddr[entryct]*ADDRESS_UNIT+4*(tmpCount[entryct]+1)], curRepeat)))
                #Add the trigger pulse
                tmpPulse = np.zeros(ADDRESS_UNIT*curRepeat*(tmpCount[entryct]+1), dtype=np.bool)
                if chanct//2 == 0:
                    if tmpTrigger1[entryct] > 0:
                        tmpPulse[4*tmpTrigger1[entryct]] = True
                else:
                    if tmpTrigger2[entryct] > 0:
                        tmpPulse[4*tmpTrigger2[entryct]] = True
                AWGData[mrkStrs[chanct]][-1] = np.hstack((AWGData[mrkStrs[chanct]][-1], tmpPulse)) 
                
    return AWGData


if __name__ == '__main__':

    pass
        
