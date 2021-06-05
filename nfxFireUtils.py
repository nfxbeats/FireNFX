# name= nfxFireUtils
#
#  Edit device_fire to import nfxFireUtils
# nfxOnInit(fire)
# copy the python files from 
#  C:\Program Files (x86)\Image-Line\Shared\Python\Lib\*
#    to
#  The folder with this code.


import time
import device
import ui
import transport
import general
#import midi
from midi import *
widPlugin = 5  #missing from midi.py

import channels
import mixer
import playlist
import patterns
import general
import plugins

import device_Fire
from device_Fire import TMidiEvent

from nfxFireColors import * 

class TnfxMixer:
    def __init__(self):
        self.Name = ""
        self.FLIndex = -1
        self.SelectPad = -1
        self.MutePad = -1
        self.isMuted = 0 

class TnfxChannel:
    def __init__(self):
        self.Name = ""
        self.FLIndex = -1
        self.Mixer = TnfxMixer()
        self.LoopSize = 0

class TnfxPattern:
    def __init__(self):
        self.Name = ""
        self.FLIndex = -1
        self.Channel = TnfxChannel()
        self.Mixer = TnfxMixer()




class TFirePadMap:
    def __init__(self):
        self.Name = ""
        self.Mixer = TnfxMixer()
        self.Channel = TnfxChannel()
        self.Patterns = list()

        self.PadIndex = -1      # the pad num 0..63
        self.MacroIndex = -1    # the macro index 0..7
        self.ChannelIndex = -1
        self.PatternIndex = -1
        self.Color = 0x000000   # the color that looks right on Fire
        self.FLColor = 0x000000     # the color that looks like above color best in FL
        self.MIDINote = -1          # the midi Note for this pad



class TFireMacro:
    def __init__(self):
        self.index = -1
        self.name = ""
        self.color = 0x000000
        self.padindex = -1


#pads to display the plalist patterns - top row
PatternPads = [8, 9, 10, 11, 12, 13, 14, 15]

# FL Patterns to associate with the above pads
PatternChannels = [1,2,3,4,5,6,7,8]

#default colors for the patterns row
PatternColors = [cGreen, cCyan, cYellow, cOrange, cRed, cMagenta, cPurple, cBlue]

#fl specific colors for coloring the patterns in FL
PatternFLColors = [cFLGreen, cFLCyan, cYellow, cFLOrange, cFLRed, cMagenta, cFLPurple, cFLBlue ]

#
ChannelPads = [24, 25, 26, 27, 28, 29, 30 , 31]

MacroPads = [40, 41, 42, 43, 
             44, 45, 46, 47]

MacroColors = [cOff, cRed, cOff, cBlue, cOff, cCyan, cOff, cOrange]

MacroNames = ['', 'Clear MIDI', '', 'ResetUI', '', '', '', '']

ProgressPads = [60, 61, 62, 63]
ProgressPadsDim = cDimWhite
ProgressPadsOn = cWhite 

FPC_APads = [0,1,2,3,
             16, 17, 18, 19,
             32, 33, 34, 35,
             48, 49, 50 , 51]

FPC_BPads = [4, 5, 6, 7,
             20, 21, 22, 23,
             36, 37, 38, 39, 
             52, 53, 54, 55]

FPC_APadColors = [cPurple, cPurple, cPurple, cYellow,
                  cRed, cRed, cYellow, cYellow,
                  cRed, cRed, cRed, cRed,
                  cBlue, cBlue, cBlue, cBlue]

FPC_BPadColors = [cGreen, cGreen, cGreen, cGreen,
                  cCyan, cCyan, cCyan, cCyan,
                  cSilver, cSilver, cSilver, cSilver,
                  cOrange, cOrange, cOrange, cOrange]  

#
_Fire = device_Fire.TFire() 
_selectedPattern = -1
_subpattern = 0

fireMacros = list()
firePadMap = list() 
isClearing = False
nfxBlinkTimer = 0
nfxBlinkSpeed = 5
nfxUpdateTimer = 9999
LoopSizes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

lastevent = device_Fire.TMidiEvent()
lastknobmode = -1
lastpat = -1
nfxRepeatNote = False
nfxIsRepeating = False

_Patterns = list()
_Channels = list()
_Mixers = list() 
_MutedTracks = list()

def BuildMixers():
    global _Mixers 
    #print ("...mixer tracks...")
    empty = 0    
    _Mixers.clear() 
    trkCount = mixer.trackCount()
    for trkNum in range(0, trkCount):
        newMixer = TnfxMixer()
        newMixer.FLIndex = trkNum 
        newMixer.Name = mixer.getTrackName(trkNum)
        newMixer.isMuted = mixer.isTrackMuted(trkNum)
        muteval = 0
        if(mixer.isTrackMuted(trkNum)):
            muteval = 1
        _MutedTracks.append(muteval)
        _Mixers.append(newMixer)
        #print('Mixer added:', newMixer.Name, newMixer.FLIndex)
        #I don't know how to detect a maxTracknumber
        if(newMixer.Name.startswith('Insert ')): # stop if we get 5 of these...
            empty += 1
            if(empty == 5):
                return

def BuildChannels():
    global _Channels
    #print ("...channels...")
    # Build a list of FL patterns
    chanCount = channels.channelCount()
    for chanNum in range(0, chanCount):
        newChan = TnfxChannel()
        newChan.FLIndex = chanNum
        newChan.Name = channels.getChannelName(chanNum)
        trk = channels.getTargetFxTrack(chanNum) 
        newChan.Mixer = next(x for x in _Mixers if x.FLIndex == trk) # next gets single element
        _Channels.append(newChan)
        #print('Channel added:', newChan.Name, newChan.FLIndex, 'Mixer:', newChan.Mixer.Name, newChan.Mixer.FLIndex)
    

def BuildPatterns():
    global _Patterns 
    #print ("...patterns...")
    # Build a list of FL patterns
    patcount = patterns.patternCount()
    for patnum in range(1, patcount+1): #start at 1
        newPat = TnfxPattern()
        newPat.FLIndex = patnum 
        newPat.Name = patterns.getPatternName(patnum)
        patterns.jumpToPattern(patnum) # this will activate a channel
        chan = channels.selectedChannel(0,0,1)
        trk = getMixerTrackForPattern(patnum)
        newPat.Channel = next(x for x in _Channels if x.FLIndex == chan) # next gets single element
        newPat.Mixer = next(x for x in _Mixers if x.FLIndex == trk) # next gets single element
        _Patterns.append(newPat)
        print('......Pattern:', patnum, newPat.Name, newPat.FLIndex,
              '-->Channel:', newPat.Channel.Name, newPat.Channel.FLIndex,
              '-->Mixer:', newPat.Mixer.Name, newPat.Mixer.FLIndex)


# call this from the end of TFire.OnInit
def OnInit(fire):
    print("nfxOnInit")

    print('...Initializing')
    Update_Fire(fire) 

    #set the default mode for me
    fire.CurrentMode = device_Fire.ModeDrum 
    lastknobmode = fire.CurrentKnobsMode
    print('...Syncing FL Track data')
    BuildMixers()
    BuildChannels()
    BuildPatterns()    

    print('...Syncing FIRE Pad data')
    InitMacros()    
    ResetPadMaps()
    ResetMutes()
    ActivatePattern(_Patterns[0].FLIndex)
    RefreshFirePads(fire, False)

def Update_Fire(fire):
    global _Fire
    _Fire = fire

# called from TFire.OnIdle
def OnIdle(fire):
    global nfxBlinkTimer
    global nfxUpdateTimer
    global lastknobmode
    global lastpat 

    Update_Fire(fire) 
    UpdateProgress(fire)

    refresh = False
    
    #not needed? 
    #if(lastknobmode != fire.CurrentKnobsMode):
    #    lastknobmode = fire.CurrentKnobsMode
    #    refresh = True 

    # check if user selected a new pattern in FL and follow...
    newPatNum = patterns.patternNumber() 
    if(newPatNum != _selectedPattern) and (_selectedPattern != -1): #if the pattern was picked in FL, handle..
        ActivatePattern(newPatNum)
        refresh = True 

    if(refresh):
        RefreshFirePads(fire, False) 
        
    nfxBlinkTimer += 1
    if nfxBlinkTimer >= nfxBlinkSpeed * 6:
        nfxBlinkTimer = 0

def InitMacros():
    #initialize tha macro list
    global fireMacros
    for i in range(len(MacroPads)):
        m = TFireMacro()
        m.index = i
        m.color = MacroColors[i]
        m.padindex = MacroPads[i]
        m.name = MacroNames[i]
        fireMacros.append(m)

def UpdateProgress(fire):
    UpdateSongPos(fire)     # 4 step progess
    UpdatePatternPads(fire) # blink if muted 

def UpdateSongPos(fire):
    if(transport.isPlaying()):
        i = 0
        songpos = transport.getSongPos()
        nfxSetFIRELEDCol(fire, ProgressPads[0], ProgressPadsDim, 0)
        nfxSetFIRELEDCol(fire, ProgressPads[1], ProgressPadsDim, 0)
        nfxSetFIRELEDCol(fire, ProgressPads[2], ProgressPadsDim, 0)
        nfxSetFIRELEDCol(fire, ProgressPads[3], ProgressPadsDim, 0)
        if(0.0 <= songpos <= 0.25):
            nfxSetFIRELEDCol(fire, ProgressPads[0], cWhite, 0)
        if(0.25 <= songpos <= 0.50 ):
            nfxSetFIRELEDCol(fire, ProgressPads[1], cWhite, 0)
        if(0.50 <= songpos <= 0.75 ):
            nfxSetFIRELEDCol(fire, ProgressPads[2], cWhite, 0)
        if(0.75 <= songpos <= 1 ):
            nfxSetFIRELEDCol(fire, ProgressPads[3], cGreen, 0)

    else:
        nfxSetFIRELEDCol(fire, ProgressPads[0], cOff, 0)
        nfxSetFIRELEDCol(fire, ProgressPads[1], cOff, 0)
        nfxSetFIRELEDCol(fire, ProgressPads[2], cOff, 0)
        nfxSetFIRELEDCol(fire, ProgressPads[3], cOff, 0)

def UpdatePatternPads(fire):
    #Pattern Pads -- top row
    for trk in PatternChannels:  # list of 8 channels, 1...8
        nfxPat = _Patterns[trk-1] # 0 based
        pad = PatternPads[trk-1] # pad index
        color = PatternColors[trk-1] # color index
        mixer = nfxPat.Mixer #get mixer for track
        #print('Pad:', pad, 'Pattern:', nfxPat.Name, nfxPat.Mixer.Name, color, trk, _selectedPattern)
        if(_selectedPattern == trk):
            nfxSetFIRELEDCol(fire, pad, color ,0)
        else:
            nfxSetFIRELEDCol(fire, pad, color, 3)

        #if (not fire.CurrentKnobsMode in [] != device_Fire.KnobsModeMixer:
        if(_MutedTracks[nfxPat.Mixer.FLIndex]):
            if nfxBlinkTimer < nfxBlinkSpeed:
                nfxSetFIRELEDCol(fire, pad, cOff, 0)

def RefreshChannelPads(fire):
    global LoopSizes
    global _Patterns
    print("RefreshChannelPads")
    selPat = getSelPat()
    isMixerMode = fire.CurrentKnobsMode == device_Fire.KnobsModeMixer

    for padNum in ChannelPads:
        trkIdx = ChannelPads.index(padNum) # gets the 'track' index (0..7), should align with PatterPads
        padIdx = PatternChannels[trkIdx] # returns 1..8
        trkPat = _Patterns[padIdx-1]
        loopsize = selPat.Channel.LoopSize
        isMuted = _MutedTracks[trkPat.Mixer.FLIndex]
        #print('...ChannelPad:', chanIdx, '..Mixer Mode:' , isMixerMode, '..MixPattern:', trkPat.Name, '..SelPattern:' + selPat.Name, 'loopSize:', selPat.Channel.LoopSize )
        #print('...ChannelPad:', chanIdx, '...Muted: ', isMuted)

        if(isMixerMode == False):
            
            if(_selectedPattern > -1):
                # determine the color to use 
                flcol = patterns.getPatternColor(selPat.FLIndex) & 0xFFFFFF
                if(flcol in PatternFLColors):
                    col = PatternColors[PatternFLColors.index(flcol) ]
                else:
                    col = flcol

                # dim factor 2
                nfxSetFIRELEDCol(fire, padNum, col, 2)

                # set loop size indicator with no dim factor
                if(loopsize == 16):
                    nfxSetFIRELEDCol(fire,  ChannelPads[1], col, 0)
                if(loopsize == 32):
                    nfxSetFIRELEDCol(fire, ChannelPads[2], col, 0)
                if(loopsize == 64):
                    nfxSetFIRELEDCol(fire, ChannelPads[3], col, 0)

                if (_MutedTracks[selPat.Mixer.FLIndex]):
                    nfxSetFIRELEDCol(fire, ChannelPads[4], cDimWhite, 0)
        else: # mixer mode
            # set channel pattern color - second row
            if(_MutedTracks[trkPat.Mixer.FLIndex]):
                nfxSetFIRELEDCol(fire, padNum, cOff, 0)        
            else:
                nfxSetFIRELEDCol(fire, padNum, cDimWhite, 0)        

def RefreshMacroPads(fire):
    # Macro Pads - Third row
    for macPad in MacroPads:
        macIdx = MacroPads.index(macPad)
        macCol = MacroColors[macIdx]
        nfxSetFIRELEDCol(fire, macPad, macCol, 2)

# called from OnMidiMsg, right before the last line
def OnMidiMsg(fire, event):
    global nfxIsRepeating
    #print("nfxOnMidiMsg", event.data1)
    RefreshFirePads(fire, False)
    return 

    wasHandled = False
    Update_Fire(fire) 

    if event.midiId in [MIDI_NOTEON, MIDI_NOTEOFF]:
        if (event.data1 >= device_Fire.PadFirst) & (event.data1 <= device_Fire.PadLast):
                    
            event.data1 -= device_Fire.PadFirst # event.data1 is now 0..63    

            if (event.midiId == MIDI_NOTEON):
                print('MidiMsg.PadOn=', event.data1)

                if(nfxRepeatNote) and (not nfxIsRepeating):
                    print('repeating...')
                    nfxIsRepeating = True
                    tempo = mixer.getCurrentTempo(0) / 1000

                    beat = 60/tempo * 1000
                    halfbeat = 30/tempo * 1000
                    step = 15/tempo * 1000
                    halfstep = 7.5/tempo * 1000
                    print(tempo, beat, halfbeat, step, halfstep)
                    device.repeatMidiEvent(event, 0, int(step) )
            
            if (event.midiId == MIDI_NOTEOFF):
                print('MidiMsg.PadOff=', event.data1)
                if(nfxRepeatNote):
                    print('...stop')
                    device.stopRepeatMidiEvent()
                    nfxIsRepeating = False 
                
            event.handled = wasHandled

    #ShowMacroButtons(fire, False)

def nfxSetFIRELEDCol(fire, idx, col, dimFactor):
    #print('SetLEDCol', idx, col)
    r = (col & 0x7F0000) >> 16
    g = (col & 0x007F00) >> 8
    b = (col & 0x7F)

    #reduce brightness by half time dimFactor
    if(dimFactor > 0):
        for i in range(dimFactor): 
            r = r >> 1
            g = g >> 1
            b = b >> 1

    nfxSetFIRELED(fire, idx, r, g, b)

def nfxSetFIRELED(fire, idx, r, g, b):  # (x, y, r, g, b):
    #print('SetLED', idx, r, g, b)
    dataOut = bytearray(4)
    i = 0
    dataOut[i] = idx
    dataOut[i + 1] = r
    dataOut[i + 2] = g
    dataOut[i + 3] = b
    fire.SendMessageToDevice(device_Fire.MsgIDSetRGBPadLedState, len(dataOut), dataOut)

def RefreshFirePads(fire, clearfirst): 
    #print('ShowMacroButtons')
    
    if(clearfirst):
        for p in range(0, 63):
            nfxSetFIRELED(fire, p, cOff, 0)

    if (True): # Default PAT/GRID on
        # default these lights to ON
        fire.SendCC(device_Fire.IDBankL, device_Fire.SingleColorHalfBright)
        fire.SendCC(device_Fire.IDBankR, device_Fire.SingleColorHalfBright)
        # patterns
        fire.SendCC(device_Fire.IDPatternUp, device_Fire.SingleColorHalfBright)
        fire.SendCC(device_Fire.IDPatternDown, device_Fire.SingleColorHalfBright)

    #Pattern Pads -- top row
    UpdatePatternPads(fire)

    #Channel Pads -- second row
    RefreshChannelPads(fire)

    # turn on the needed macro buttons - third row
    RefreshMacroPads(fire)


    if(False): #Show Custom FPC Colors
        #FPC A Pads
        for p in FPC_APads:
            nfxSetFIRELEDCol(fire, p, FPC_APadColors[FPC_APads.index(p)],3)

        for p in FPC_BPads:
            nfxSetFIRELEDCol(fire, p, FPC_BPadColors[FPC_BPads.index(p)],3)

    if(False): #if true, will hide FPC 
        #FPC A Pads
        for p in FPC_APads:
            nfxSetFIRELEDCol(fire, p, cOff,3)

        for p in FPC_BPads:
            nfxSetFIRELEDCol(fire, p, cOff,3)


def HandleControlPress(fire, event):
    global lastevent
    #print('ControlPress')
    Update_Fire(fire)     
    RefreshFirePads(fire, False)

# needs to be called from OnMidiMsg NOTE ON /OFF section of device_Fire
def HandlePadPress(fire, event):
    global lastevent
    global firePadMap
    #print('HandlePadPress', event.data1, event.data2)
    Update_Fire(fire)     
    lastevent.status = event.status

    #do this before getting the padIndex
    if (fire.CurrentDrumMode == device_Fire.DrumModeFPC):
        event.data1 -= 4 # reset the offset to get the correct pad index  - bug in the device_Fire code??

    padIndex = event.data1
    if (event.midiId in [MIDI_NOTEON]):

        nfxSetFIRELEDCol(fire, padIndex, cWhite, 1) #turn led white when pressed.

        # check the pattern pads first in case they change something
        if(padIndex in PatternPads):
            HandlePatternPads(fire, padIndex) 
            event.handled = True 

        if(padIndex in ChannelPads):
            HandleChannelPads(fire, padIndex)
            event.handled = True 

        if(padIndex in MacroPads):
            HandleMacros(fire, event, padIndex)
            event.handled = True 

    if (event.midiId in [MIDI_NOTEOFF]):
        #print("HandlePadPress.NOTEOFF --->", event.data1, event.data2, event.midiId)
        nfxSetFIRELED(fire, padIndex, 0, 0, 0)
 
    # refresh the buttons
    RefreshFirePads(fire, False)

def getSelPat():
    return _Patterns[_selectedPattern-1] # 0 based

def HandleChannelPads(fire, PadIndex):
    global LoopSizes
    global _MutedTracks 
    global _Patterns

    #print('HandleChannelPads', PadIndex)
    selPat = getSelPat()
    isMixerMode = (fire.CurrentKnobsMode == device_Fire.KnobsModeMixer)
    chanPadIdx = ChannelPads.index(PadIndex) # will be the buttons number from  0..7
    nfxPat = _Patterns[chanPadIdx] # get the associated pattern 
    trkNum = nfxPat.Mixer.FLIndex 
    loopsize = selPat.Channel.LoopSize 

    #print('...ChannelPad:', chanPadIdx, '..Mixer Mode:' , isMixerMode, '..MixPattern:', nfxPat.Name, '..SelPattern:' + selPat.Name, loopsize )

    if(isMixerMode):
        MuteMixerTrack(trkNum, -1)        
    else: # channel mode uses selected
        
        if (chanPadIdx == 0):
            loopsize = 0
        if (chanPadIdx == 1):
            loopsize = 16
        if (chanPadIdx == 2):
            loopsize = 32
        if (chanPadIdx == 3):
            loopsize = 64

        if(loopsize > -1):
            fire.DisplayTimedText('Pat Loop: ' + str(loopsize) )
            patterns.setChannelLoop(selPat.Channel.FLIndex, loopsize)
            selPat.Channel.LoopSize = loopsize

        if(chanPadIdx == 4): # mute channel
            trk = selPat.Mixer.FLIndex
            print('x1', _MutedTracks[trk], selPat.Mixer.FLIndex)
            MuteMixerTrack(trk, -1)
            print('x2', _MutedTracks[trk], selPat.Mixer.FLIndex)

def HandleMacros(fire, event, PadIndex):
    global firePadMap
    global nfxRepeatNote

    # check if a macro pad is pressed
    if PadIndex in MacroPads:
        #convert the padnum to a macronum
        MacroIndex = MacroPads.index(PadIndex)
        print("MacroIndex", MacroIndex)
        MacroCol = MacroColors[MacroIndex]
        
        # If the macro color = cOff, it should not be handled.   
        if(MacroCol == cOff):
            return
        
        # Macro 1 - Clear MIDI
        if(MacroIndex == 1):
            ClearMidi(fire)

        # Macro 3 - ResetUI, +Alt=Recolor FL Patterns
        if(MacroIndex == 3):
            if(fire.AltHeld):
                RecolorPatterns()
                OnInit(fire)
            else:
                ResetUI(fire)

        if(MacroIndex == 5):
            print('repeat mode')
            nfxRepeatNote = not nfxRepeatNote

        if(MacroIndex == 7):
            print("Macro-7")
            BuildMixers()
            BuildChannels()
            BuildPatterns()

def ResetPadMaps():
    global firePadMap
    #print('ResetPadMaps')
    # map the pads
    patidx = -1
    firePadMap.clear()
    #print('Pattern Pads...' , PatternPads)
    for padNum in range(0, 64): # the pads
        pMap = TFirePadMap()
        pMap.FirePadIndex = padNum

        #iterates the FIRE pads defined for patterns - top row
        if padNum in PatternPads:
            patidx = PatternPads.index(padNum) # ex.  Pad[0] = nfxPattern[1]
            patNum = PatternChannels[patidx]
            #print('patNum', patNum)
            
            nfxPat = _Patterns[patNum-1]

            ##print('...added pad:', patNum, nfxPat.Name, nfxPat.FLIndex, '-->Channel:', nfxPat.Channel.Name, nfxPat.Channel.FLIndex,             '-->Mixer:', nfxPat.Mixer.Name, nfxPat.Mixer.FLIndex)

            pMap.Name = nfxPat.Name
            pMap.Mixer = nfxPat.Mixer
            pMap.Channel = nfxPat.Channel
            colIdx = nfxPat.FLIndex-1 # 0 based
            #print('ColorIdx:', colIdx, 'pMap:', pMap.Name, pMap.Mixer.Name, pMap.Channel.Name)
            pMap.Color = PatternColors[colIdx] 

        if padNum in MacroPads:                 # is the pad in the list of Macro Pads?
            macIdx = MacroPads.index(padNum)    # get the Macro Index
            pMap.FireMacroIndex = macIdx
            pMap.Color = MacroColors[macIdx]
            

        if(len(pMap.Name) > 1 ):
            print('...Pad Mapped: ', pMap.FirePadIndex, pMap.Mixer.Name, _MutedTracks[pMap.Mixer.FLIndex])

def getMixerTrackForPattern(pat):
    trkNum = -1
    #patterns.jumpToPattern(pat)
    ui.showWindow(widChannelRack)
    c = channels.selectedChannel(0,0,1)
    if(c > -1):
        trkNum = channels.getTargetFxTrack(c)
    #print('pattern', pat, 'mixer', trkNum )
    return trkNum 

def getMixerTrackForChannel(chan):
    return channels.getTargetFxTrack(chan) 

def MuteMixerTrack(trk, muteval = -1):
    global _MutedTracks
    print('MueMixterTrack', trk, muteval, _MutedTracks[trk])
    
    if(muteval == -1) and (_MutedTracks[trk] == 0):
        _MutedTracks[trk] = 1
    elif(muteval == -1) and (_MutedTracks[trk] == 1):
        _MutedTracks[trk] = 0
    else:
        _MutedTracks[trk] = muteval

    mixer.muteTrack(trk, _MutedTracks[trk]) #explicit set

    print('MueMixterTrack', trk, muteval, _MutedTracks[trk])


def MutePlaylistTrack(pltrk, muteval = -1):
    print('MuteTrack', pltrk, muteval)
    playlist.muteTrack(pltrk, muteval) #explicit set

def MuteTrack(pMap, muteval):
    global _MutedTracks 

    name    = pMap.Name
    trk     = pMap.FLMixerTrackNum
    pltrk   = pMap.FLPatternNum
    currval = _MutedTracks[trk]

    if(currval == 0) and (muteval == -1):
        muteval = 1

    if(currval == 1) and (muteval == -1):
        muteval = 0

    _MutedTracks[trk] = muteval
    MuteMixerTrack(trk, muteval)

    if (_MutedTracks[trk] == 0): 
        _Fire.DisplayTimedText('Mute: ' + name)
    else:
        _Fire.DisplayTimedText('Un-Mute: ' + name)
    print('mute val now', _MutedTracks)

def HandlePatternPads(fire, padIndex):
    # activate a pattern - top row
    padIdx = PatternPads.index(padIndex)
    patNum = PatternChannels[padIdx]
    ActivatePattern(patNum, True, True)
    RefreshFirePads(fire, False)
    return 

def ActivatePattern(patNum, showPlugin = False, setMixer = True):
    global firePadMap
    global _selectedPattern
    global _subpattern

    nfxPat = _Patterns[patNum-1] # 0 based
    mixerNum = nfxPat.Mixer.FLIndex 

    if(_selectedPattern > -1): # to close the previous channel plugin
        nfxPrevPat = _Patterns[_selectedPattern]
        #print(_selectedPattern, nfxPrevPat.FLIndex)
        channels.showEditor(nfxPrevPat.Channel.FLIndex, 0)

    #gets a list of patterns associated to the mixer chan
    nfxPatterns = [x for x in _Patterns if x.Mixer.FLIndex == mixerNum]
    nfxPat = nfxPatterns[0] #use first result only for now
    #print('IN->Pattern:', _subpattern,  patNum, nfxPat.FLIndex,  nfxPat.Name, '_Sel:', _selectedPattern, 'Mixer:', mixerNum, )

    if(len(nfxPatterns) > 1): # if there are sub patterns
        for pat in nfxPatterns:
            print('has sub pattern:', pat.Name)

        # if same button pressed, see if there is an alternate pat to use
        if(_selectedPattern == nfxPat.FLIndex): 
            _subpattern += 1
            print('sub', _subpattern, 'of', len(nfxPatterns))
            if(_subpattern < len(nfxPatterns)):
                nfxPat = nfxPatterns[_subpattern]
        else:
            #print("reset")
            _subpattern = 0
    else:
        _subpattern = 0

    patterns.jumpToPattern(nfxPat.FLIndex)
    ui.showWindow(widChannelRack)
    chanNum = channels.selectedChannel(0,0,1)
    _selectedPattern = nfxPat.FLIndex - _subpattern
    channels.showEditor(chanNum, 1)

    if(showPlugin):
        ui.showWindow(widPlugin) 
    
    if(setMixer):
        mixer.setTrackNumber(mixerNum) 

    if(True): #show Piano Roll
        ui.openEventEditor(channels.getRecEventId(chanNum) + REC_Chan_PianoRoll, EE_PR)
        ui.showWindow(widPianoRoll)

    #ui.openEventEditor(mixer.getTrackPluginId(trkNum,0) + REC_Mixer_Vol, EE_EE)
    #ui.openEventEditor(channels.getRecEventId(trkNum) + REC_Mixer_Vol, EE_EE)
    #ui.openEventEditor(channels.getRecEventId(chanNum) + REC_Chan_Pitch, EE_EE)
    #print('OUT->Pattern:', nfxPat.FLIndex, '_Sel:', _selectedPattern, 'Mixer:', mixerNum, )
    
def getPadMapFromPadNum(padnum):
    return firePadMap[padnum]

def getPadMapFromPatternNum(patnum):
    padnum = -1
    patPads = [x for x in firePadMap if x.Mixer.FLIndex == patnum] 
    for pMap in patPads: # PatternPads:
        padnum = pMap.FirePadIndex
    return firePadMap[padnum]

def getPadMapFromChannelNum(channum):
    padnum = -1
    patPads = [x for x in firePadMap if x.FLChannelNum == channum] 
    for pMap in patPads: # PatternPads:
        padnum = pMap.FirePadIndex
    return firePadMap[padnum]

def ResetUI(fire):
    fire.DisplayTimedText("Reset UI...")
    transport.globalTransport(FPT_F12, 1) #close all...
    ui.showWindow(widMixer)

    # todo: scroll to master channel or FX channel and showMIDI, etc
    mixer.setTrackNumber(0)

    ui.showWindow(widPlaylist)
    # todo: press 4 to fill screen

    ui.showWindow(widChannelRack)
    #todo: bring up any other windows.. ie control surface, etc

    #open the piano roll
    chan = channels.selectedChannel(0,0,1)
    ui.openEventEditor(channels.getRecEventId(chan) + REC_Chan_PianoRoll, EE_PR)
    ui.showWindow(widPianoRoll)

def ClearMidi(fire):
    global isClearing

    if isClearing:
        return

    isClearing = True 
    isRec = transport.isRecording()
    if(isRec):
        transport.record() #turn off

    if(fire.AltHeld):

        fire.DisplayTimedText('Clearing ALL')
        patcount = patterns.patternCount()
        for p in range(1, patcount+1):
            pName = patterns.getPatternName(p)
            print('...Pattern:', pName, p)
            patterns.jumpToPattern(p)
            time.sleep(0.2)
            ClearPattern()

    else:
        print('Clearing Pattern')
        ClearPattern()

    if(isRec):
        transport.record() 
    
    time.sleep(0.5)
    isClearing = False

def ClearPattern():
    ui.showWindow(widChannelRack)
    #channels.selectAll()
    ui.cut()
    time.sleep(0.1)
    #channels.deselectAll()#turn on

def RecordMIDINote(name, mixerch, note, vel, dur, midich):
    # NOTES:
    #  requires that the recording filter for 'Audio' be checked.
    #

    #init a few basic requirements
    print('RecordMIDINote', 'starting', name)
    transport.stop()
    mixer.setTrackNumber(mixerch)
    mixer.setTrackName(mixerch, name)

    if (not mixer.isTrackEnabled(mixerch)):
        mixer.enableTrack(mixerch)
    if (not mixer.isTrackArmed(mixerch)):
        mixer.armTrack(mixerch)
    if (not transport.isRecording()):
        transport.record()

    #start recording
    transport.start()

    #play the note
    t1 = time.process_time()
    channels.midiNoteOn(midich, note, vel)
    time.sleep(dur)
    channels.midiNoteOn(midich, note, 0)

    #wait for silence
    while (mixer.getTrackPeaks(mixerch, PEAK_LR) >= 0.001):
        time.sleep(0.01)

    transport.stop()
    t2 = time.process_time()
    elapsed = (t2-t1)
    print('elapsed', elapsed)
    if (elapsed < 0.08):
        print('** silence?? ** ')

    filename = mixer.getTrackRecordingFileName(mixerch)

    #done
    print('RecordMIDINote', 'done', filename)
    return filename

def RecolorPatterns():

    # do the patterns
    patcount = patterns.patternCount()
    #print('pattern count', patcount)
    patcol = PatternFLColors[0]
    offset = 1
    plcount = playlist.trackCount()
    chan = -1

    for p in range(1,patcount+1):
        patterns.jumpToPattern(p)
        pName = patterns.getPatternName(p)
        c = channels.selectedChannel(0,0,1)

        print('Pattern:', pName, p, patcol, chan, c)
        if(pName.startswith('...')): #use prev color
            patterns.setPatternColor(p, patcol)
            PatternChannels[c] = chan
            offset += 1
        else:# use new color
            patcol = PatternFLColors[p-offset]
            patterns.setPatternColor(p, patcol)
            ui.showWindow(widChannelRack)
            print('Channel/FX', chan, c)
            if(c > -1):
                chan = c 
                chname = channels.setChannelName(c, pName)
                channels.setChannelColor(c, patcol)
                trkNum = channels.getTargetFxTrack(c)
                mixer.setTrackColor(trkNum, patcol)
                mixer.setTrackName(trkNum, pName)

                if c < len(PatternChannels):
                    PatternChannels[c] = chan 

        for pl in range(1, plcount):
            plName = playlist.getTrackName(pl)
            if (plName == pName):
                playlist.setTrackColor(pl, patcol)

    print(PatternChannels)

def ResetMutes():
    for mix in _Mixers:
        mixer.muteTrack(mix.FLIndex, 0)
        

        


        
    


















