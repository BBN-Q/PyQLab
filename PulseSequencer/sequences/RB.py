'''
Single qubit randomized benchmarking
'''

#Imports necessary for compiling sequences
from Channels import load_channel_info
from PulseSequencer import compile_sequences
from PulseSequencePlotter import plot_pulse_seqs

from csv import reader

def RB(targetQubit = 'q1', fileName='RB', plotSeqs=True, readoutPulseLength=6.66e-6, AWGList=['TekAWG1','BBNAPS1']):

    #Load the channel information
    channelObjs, channelDicts = load_channel_info('ChannelParams.json') 
    channelDicts['AWGList'] = AWGList
    
    #Assign the channels
    targetQ = channelObjs[targetQubit]
    digitizerTrig = channelObjs['digitizerTrig']
    measChannel = channelObjs['measChannel']
    readoutBlock = digitizerTrig.gatePulse(100e-9)+measChannel.gatePulse(readoutPulseLength)

    #Load the sequences from file
    with open('sequences/RB_ISeqs.txt','r') as FID:
        fileReader = reader(FID, delimiter='\t')
        
        pulseSeqs = []
        for pulseSeqStr in fileReader:
            tmpSeq = []
            for tmpPulseStr in pulseSeqStr:
                tmpSeq.append(getattr(targetQ, tmpPulseStr)())
            tmpSeq.append(readoutBlock)
            pulseSeqs.append(tmpSeq)
        
        #Add some calibrations (two ground; two excited)
        groundCal = [targetQ.QId(), readoutBlock]
        excitedCal = [targetQ.Xp(), readoutBlock]
        pulseSeqs.append(groundCal)
        pulseSeqs.append(groundCal)
        pulseSeqs.append(excitedCal)
        pulseSeqs.append(excitedCal)
        
                
        
        #Complile and write to file
        AWGWFs, _LLs, _WFLibrary = compile_sequences(pulseSeqs, channelDicts, fileName, 'RB')  
        
        #If asked then call the plot GUI
        if plotSeqs:
            plotterWin = plot_pulse_seqs(AWGWFs)
            return plotterWin

if __name__ == '__main__':
    plotWin = RB()