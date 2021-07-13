# name= nfxFireUtils
#
#  Edit device_fire to import nfxFireUtils
# nfxOnInit(fire)
# copy the python files from 
#  C:\Program Files (x86)\Image-Line\Shared\Python\Lib\*
#    to
#  The folder with this code.

# yes this code is messy and redundant on places. its in a constant state of refactor
# and development. get used to it ;)

#region imports
import time
import device
import ui
import transport
import general
from midi import *
widPlugin = 5  #missing from midi.py
from harmonicScales import *
import utils 

import channels
import mixer
import playlist
import patterns
import general
import plugins

import device_Fire
from device_Fire import TMidiEvent

from nfxFireColors import * 
#endregion

#region Classes
class TnfxMixer:
    def __init__(self):
        self.Name = ""
        self.FLIndex = -1
        self.SelectPad = -1
        self.MutePad = -1
        self.Muted = 0 

class TnfxChannel:
    def __init__(self):
        self.Name = ""
        self.FLIndex = -1
        self.Mixer = TnfxMixer()
        self.LoopSize = 0
        self.Muted = 0

class TnfxPattern:
    def __init__(self):
        self.Name = ""
        self.FLIndex = -1
        self.Channel = TnfxChannel()
        self.Mixer = TnfxMixer()
        self.Muted = 0
        self.ShowChannelEditor = 0
        self.ShowPianoRoll = 0
        self.ShowChannelSettings = 0
        self.Color = cOff 

class TnfxPadMap:
    def __init__(self):
        self.Name = ""
        self.Mixer = TnfxMixer()
        self.Channel = TnfxChannel()
        self.Patterns = list()

        self.PadIndex = -1          # the pad num 0..63
        self.MacroIndex = -1        # if it belongs to 3rd row macro pad, the macro index will be 0..7
        self.ChannelIndex = -1      # if it belongs second row  to a channel pad group this will be > -1  
        self.PatternIndex = -1      # if > -1 it will be top row 
        self.Color = 0x000000       # the color that looks right on Fire
        self.FLColor = 0x000000     # the color that looks like above color best in FL
        self.MIDINote = -1          # the midi Note for this pad
        self.IsRootNote = False 

class TnfxMacro:
    def __init__(self):
        self.index = -1
        self.name = ""
        self.color = 0x000000
        self.padindex = -1

#endregion 

#region PAD Definitions and colors

#pads to display the plalist patterns - top row
PatternPads = [8, 9, 10, 11, 12, 13, 14, 15]
# FL Patterns to associate with the above pads
PatternChannels = [1,2,3,4,5,6,7,8]

# these go under the  PatternPads
ChannelPads = [24, 25, 26, 27, 28, 29, 30 , 31]
#value of below relate to index of above
_cpPatLen0 = 0
_cpPatLen1 = 1
_cpPatLen2 = 2
_cpPatLen3 = 3
_cpMute = 4
_cpShowCE = 5
_cpShowPR = 6
_cpShowCS = 7
_lsLen1 = 32
_lsLen2 = 64
_lsLen3 = 96

_snapModesList = [Snap_Beat, Snap_HalfBeat, Snap_FourthBeat, Snap_Step, Snap_HalfStep, Snap_FourthStep, Snap_None]
_snapIdx = 3 #initial value

MacroPads = [40, 41, 42, 43, 44, 45, 46, 47]
MacroColors = [cGreen,     cMagenta, cOrange, cBlue, cRed,        cYellow,        cCyan, cOrange]
MacroNames = ['Save Undo', 'Undo',   'Repeat', 'Snap', 'Clear MIDI', 'Reset UI/ALL', 'TEST', 'Re-INIT']

ProgressPads = [56, 57, 58, 59, 60, 61, 62, 63]
ProgressPadsDim = cDimWhite
ProgressPadsOn = cWhite 

#note these are referenced via the AKAI PadIndex (0..63)
# and NOT the FPC Pad num. AKAI runs top left to bottom right
# whereas FPC runs bottom left to top right
FPC_APads = [0,1,2,3,
             16, 17, 18, 19,
             32, 33, 34, 35,
             48, 49, 50 , 51]
FPC_BPads = [4, 5, 6, 7,
             20, 21, 22, 23,
             36, 37, 38, 39, 
             52, 53, 54, 55]

             

# color scheme for my default kit
FPC_APadColors = [cPurple, cPurple, cYellow, cYellow,
                  cRed, cRed, cYellow, cYellow,
                  cRed, cRed, cRed, cRed,
                  cBlue, cBlue, cBlue, cBlue]
FPC_BPadColors = [cGreen, cGreen, cGreen, cGreen,
                  cCyan, cCyan, cCyan, cCyan,
                  cSilver, cSilver, cSilver, cSilver,
                  cOrange, cOrange, cOrange, cOrange]  
# used to unencode the translation, so when we repeat not it sends the untralslated value
# if I didnt do this, the note would get re-translated into the wrong note.
_PAD_Notes = [52, 53, 54, 55, 56, 57, 58, 59, 
              36, 37, 38, 39, 40, 41, 42, 43, 
              20, 21, 22, 23, 24, 25, 26, 27,
               4,  5,  6,  7,  8,  9, 10, 11, -1]
_FPC_Notes = [37, 36, 42, 54, 60, 61, 62, 63, 
              40, 38, 46, 44, 64, 65, 66, 67, 
              48, 47, 45, 43, 68, 69, 70, 71, 
              49, 55, 51, 53, 72, 73, 74, 75, -1]



#endregion

#region Globals
_Fire = device_Fire.TFire() 
_selectedPattern = -1
_subpattern = 0
_isClearing = False
_nfxBlinkTimer = 0
_nfxBlinkSpeed = 5
_showFPCColors = False
_drumMixerTrk = -1
_lastEvent = device_Fire.TMidiEvent()
_lastKnobMode = -1
_lastPattern = -1
_RepeatNote = False
_IsRepeating = False
_IsActivating = False 
#lists of things
_Macros = list()
_PadMaps = list() 
_Patterns = list()
_Channels = list()
_Mixers = list() 
_MutedTracks = list()

# snap defs are in MIDI.py aka Snap_Cell, Snap_line, etc
_snapModes = ["Default", "Line", "?", "Cell", "None", 
    "1/6 Step", "1/4 Step", "1/3 Step", "1/2 Step", "Step", 
    "1/6 Beat", "1/4 Beat", "1/3 Beat", "1/2 Beat", "Beat", 
    "Bar"]
 
#endregion

#region nfx/FL/FIRE Helpers
def BuildMixers():
    global _Mixers 
    #print ("...mixer tracks...")
    empty = 0    
    _Mixers.clear() 
    _MutedTracks.clear()
    trkCount = mixer.trackCount()
    for trkNum in range(0, trkCount):
        newMixer = TnfxMixer()
        newMixer.FLIndex = trkNum 
        newMixer.Name = mixer.getTrackName(trkNum)
        newMixer.Muted = mixer.isTrackMuted(trkNum)
        #muteval = 0
        #if(mixer.isTrackMuted(trkNum)):
        #    muteval = 1
        #_MutedTracks.append(muteval)
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
    global _drumMixerTrk

    #print ("...patterns...")
    # Build a list of FL patterns
    patcount = patterns.patternCount()
    
    if patcount > 20:  # on a new track it might return a patternCount every track 0..999 (Pattern1..Pattern999)
        patcount = 20  # so enforce a max of 20 for now

    for patnum in range(1, patcount+1): #start at 1
        newPat = TnfxPattern()
        newPat.FLIndex = patnum 
        newPat.Name = patterns.getPatternName(patnum)
        patterns.jumpToPattern(patnum) # this will activate a channel
        chan = channels.selectedChannel(0,0,1)
        trk = channels.getTargetFxTrack(chan)
        newPat.Channel = next(x for x in _Channels if x.FLIndex == chan) # next gets single element
        newPat.Mixer = next(x for x in _Mixers if x.FLIndex == trk) # next gets single element
        newPat.Color = getColorFromFL(patterns.getPatternColor(patnum))
        if(newPat.Name.startswith("FPC") ):
            _drumMixerTrk = trk
        _Patterns.append(newPat)
        print('......Pattern #', patnum, newPat.Name,  #newPat.FLIndex,
              '-->Channel #', newPat.Channel.FLIndex, newPat.Channel.Name, 
              '-->Mixer #', trk, newPat.Mixer.FLIndex, newPat.Mixer.Name)

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

def getSelPat():
    return _Patterns[_selectedPattern-1] # 0 based

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

def GetTempoDiv(div):
    tempo = mixer.getCurrentTempo(0) / 1000
    beat = 60/tempo * 1000
    halfbeat = 30/tempo * 1000
    step = 15/tempo * 1000
    halfstep = 7.5/tempo * 1000
    divs = [beat, halfbeat, step, halfstep]
    return divs[div]

def MuteMixerTrack(trk, newVal = -1):
    global _Patterns
    pat = next(x for x in _Patterns if x.Mixer.FLIndex == trk) 
    patIdx = pat.FLIndex - 1 # 0 based
    currVal = _Patterns[patIdx].Muted

    print('MuteMixerTrack: ', _Patterns[patIdx].Muted, newVal, trk, patIdx)

    if(newVal == -1):
        if(currVal == 0):
            newVal = 1
        elif(currVal == 1):
            newVal = 0

    _Patterns[patIdx].Muted = newVal
    #mixer.muteTrack(trk, newVal) #explicit set
    MutePlaylistTrack(pat.FLIndex, newVal )
    
    print('MuteMixerTrack: ', _Patterns[patIdx].Muted, newVal, trk, _Patterns[patIdx].Mixer.FLIndex)
    #print('MuteMixerTrack', trk, _Patterns[patIdx].FLIndex, 'M:', newVal, currVal)

def MutePlaylistTrack(pltrk, newVal = -1):
    currVal = 0
    if (playlist.isTrackMuted(pltrk)):
        currVal = 1

    if(newVal == -1):
        if(currVal == 0):
            newVal = 1
        elif(currVal == 1):
            newVal = 0

    print('MutePLTrack', pltrk, newVal)
    if(currVal != newVal):
        playlist.muteTrack(pltrk) #explicit set
    
    # the following lines will force FL to 'refresh' the 
    # playlist and thus it will cut or start the notes better.
    # unfortunately it takes longer because it sets the pattern twice
    patterns.jumpToPattern(-1)
    patterns.jumpToPattern(pltrk)
    
def getColorFromFL(FLColor):
    #FLColor = channels.getChannelColor(n)
    h, s, v = utils.RGBToHSVColor(FLColor)
    FLColor, h, s, v = _Fire.ScaleColor(1.0, h, s, v)
    r = ((FLColor >> 16) & 0xFF) // 2
    b = (FLColor & 0xFF) // 2
    g = ((FLColor >> 8) & 0xFF) // 2
    return utils.RGBToColor(r, g, b)

def getPadMapFromPadNum(padnum):
    return _PadMaps[padnum]

def getPadMapFromPatternNum(patnum):
    padnum = -1
    patPads = [x for x in _PadMaps if x.Mixer.FLIndex == patnum] 
    for pMap in patPads: # PatternPads:
        padnum = pMap.FirePadIndex
    return _PadMaps[padnum]

def getPadMapFromChannelNum(channum):
    padnum = -1
    patPads = [x for x in _PadMaps if x.FLChannelNum == channum] 
    for pMap in patPads: # PatternPads:
        padnum = pMap.FirePadIndex
    return _PadMaps[padnum]


def setSnapMode(newmode):
    mode = ui.getSnapMode()
    while(mode < newmode):
        ui.snapMode(1) #inc by 1
        mode = ui.getSnapMode()
    while(mode > newmode):
        ui.snapMode(-1) #inc by 1
        mode = ui.getSnapMode()
    
    _Fire.DisplayTimedText('Snap: ' + _snapModes[mode+1] )


def ResetMutes():
    for mix in _Mixers:
        mixer.muteTrack(mix.FLIndex, 0)

def isModeMixer():
    return _Fire.CurrentKnobsMode == device_Fire.KnobsModeMixer

def isModeChannel():
    return _Fire.CurrentKnobsMode == device_Fire.KnobsModeChannelRack

def isModeUser1():
    return _Fire.CurrentKnobsMode == device_Fire.KnobsModeUser1

def isModeUser2():
    return _Fire.CurrentKnobsMode == device_Fire.KnobsModeUser2

def isAllowed():
    return _Fire.CurrentDrumMode == device_Fire.DrumModeFPC

def ShowPianoRoll(showVal):
    global _Patterns
    selPatIdx = _selectedPattern-1 # 0 based
    selPat = _Patterns[selPatIdx] #0 based 
    currVal = selPat.ShowPianoRoll

    #print('ShowPR: ', _Patterns[selPatIdx].ShowPianoRoll)

    ui.showWindow(device_Fire.widChannelRack)
    chanNum = channels.selectedChannel(0,0,1)
    ui.openEventEditor(channels.getRecEventId(chanNum) + REC_Chan_PianoRoll, EE_PR)

    if(showVal==-1): #toggle
        if(currVal==0):
            showVal = 1
        else:
            showVal = 0

    if(showVal == 1):
        ui.showWindow(device_Fire.widPianoRoll)
        _Patterns[selPatIdx].ShowPianoRoll = 1
    else:
        ui.hideWindow(device_Fire.widPianoRoll)
        _Patterns[selPatIdx].ShowPianoRoll = 0

    #print('ShowPR: ', _Patterns[selPatIdx].ShowPianoRoll)

def ShowChannelSettings(showVal):
    global _Patterns
    selPatIdx = _selectedPattern-1 # 0 based
    selPat = _Patterns[selPatIdx] #0 based 
    currVal = selPat.ShowChannelSettings


    if(showVal==-1): #toggle
        if(currVal==0):
            showVal = 1
        else:
            showVal = 0

    #print('ShowCS: ', _Patterns[selPatIdx].ShowChannelSettings)
    ui.showWindow(device_Fire.widChannelRack)
    chanNum = channels.selectedChannel(0,0,1)
    channels.showCSForm(chanNum, showVal)
    _Patterns[selPatIdx].ShowChannelSettings = showVal
    #print('ShowCS: ', _Patterns[selPatIdx].ShowChannelSettings)

def ShowChannelEditor(showVal):
    global _Patterns
    selPatIdx = _selectedPattern-1 # 0 based
    selPat = _Patterns[selPatIdx] #0 based 
    currVal = selPat.ShowChannelEditor
    
    if(showVal==-1): #toggle
        if(currVal==0):
            showVal = 1
        else:
            showVal = 0    

    #print('ShowCE: ', _Patterns[selPatIdx].ShowChannelEditor)
    ui.showWindow(device_Fire.widChannelRack)
    chanNum = channels.selectedChannel(0,0,1)
    channels.showEditor(chanNum, showVal)
    _Patterns[selPatIdx].ShowChannelEditor = showVal
    #print('ShowCE: ', _Patterns[selPatIdx].ShowChannelEditor)

#endregion

#region FL MIDI Events
# call this from the end of TFire.OnInit
def OnInit(fire):

    #set the default modes for my own preference
    fire.CurrentMode = device_Fire.ModeDrum 
    setSnapMode(_snapIdx)

    if(not isAllowed()):
        return 

    InitAll(fire)

# called from TFire.OnIdle
def OnIdle(fire):
    global _nfxBlinkTimer
    #OBS global nfxUpdateTimer
    global _lastKnobMode
    global _lastPattern 
    Update_Fire(fire) 

    if(not isAllowed()):
        return 


    RefreshProgress(fire)
    #RefreshPatternPads(fire) # causes crash on changing tracks - no idea why.

    refresh = False
    
    # these lines force the Fire to use only channel and mixer modes
    if fire.CurrentKnobsMode == device_Fire.KnobsModeUser1:
       fire.CurrentKnobsMode = device_Fire.KnobsModeChannelRack
    if fire.CurrentKnobsMode == device_Fire.KnobsModeUser2:
       fire.CurrentKnobsMode = device_Fire.KnobsModeMixer

    #force refresh on mode change       
    if(_lastKnobMode != fire.CurrentKnobsMode):
        _lastKnobMode = fire.CurrentKnobsMode

        if(fire.CurrentKnobsMode == device_Fire.KnobsModeMixer): # if mixer, bring it forward
            print('Mixer Mode')
            mixer.setTrackNumber(_Patterns[_selectedPattern-1].Mixer.FLIndex) 
            ui.showWindow(device_Fire.widMixer)
            
        if(fire.CurrentKnobsMode == device_Fire.KnobsModeChannelRack): # if mixer, bring it forward
            print('Channel Mode')
            mixer.setTrackNumber(_Patterns[_selectedPattern-1].Mixer.FLIndex) 
            ui.showWindow(device_Fire.widChannelRack)
            
        refresh = True 

    # check if user selected a new pattern in FL and follow...
    newPatNum = patterns.patternNumber() 
    if(newPatNum != _selectedPattern) and (_selectedPattern > -1): #if the pattern was picked in FL, handle..
        ActivatePattern(newPatNum)
        refresh = True 

    if(refresh):
        RefreshFirePads(fire, False) 

    if(_RepeatNote):
        RefreshMacroPads(fire)

    _nfxBlinkTimer += 1
    _nfxBlinkSpeed = GetTempoDiv(2)
    if _nfxBlinkTimer >= _nfxBlinkSpeed * 6:
        _nfxBlinkTimer = 0

# called from OnMidiMsg, right before the last line
def OnMidiMsg(fire, event):
    global _IsRepeating
    global _RepeatNote
    origevent = event
    wasHandled = False
    Update_Fire(fire)

    if(not isAllowed()):
        return 


    if event.midiId in [MIDI_NOTEON, MIDI_NOTEOFF]:
        if (event.data1 >= device_Fire.PadFirst) & (event.data1 <= device_Fire.PadLast):
            event.data1 -= device_Fire.PadFirst # event.data1 is now 0..63    
            
            PadIndex = event.data1

            if (event.midiId == MIDI_NOTEON):
                print('MidiMsg.PadOn=', PadIndex)
            
            if (event.midiId == MIDI_NOTEOFF):
                print('MidiMsg.PadOff=', PadIndex)
                
                
            event.handled = wasHandled

        RefreshFirePads(fire, False)

#endregion

#region Refresh
def RefreshProgress(fire):
    if not isAllowed():
        return

    RefreshSongPos(fire)     # 4 step progess
    RefreshPatternPads(fire) # blink if muted 

def RefreshSongPos(fire):
    if not isAllowed():
        return

    if(transport.isPlaying()):
        colorOn = cWhite
        colorDim = cWhite 
        if(transport.isRecording()):
            colorDim = getSelPat().Color 
            colorOn = getSelPat().Color 
        idx = 0
        songpos = transport.getSongPos()
        padCnt = len(ProgressPads)
        for p in range(0, padCnt):
            padDiv = 1/padCnt # 1 is max songpos
            padLimit = padDiv * p
            #print(songpos, padDiv, padLimit)
            if(songpos > padLimit):
                nfxSetFIRELEDCol(fire, ProgressPads[p], colorOn, 0)
            else:
                nfxSetFIRELEDCol(fire, ProgressPads[p], colorDim, 3)
    else: 
        for p in ProgressPads:
            nfxSetFIRELEDCol(fire, p, cOff, 0)

def RefreshPatternPads(fire):
    global _Patterns 
    if not isAllowed():
        return
    #Pattern Pads -- top row
    for trk in PatternChannels:  # list of 8 channels, 1...8
        patIdx = trk - 1 # 0 based
        nfxPat = _Patterns[patIdx] 
        pad = PatternPads[patIdx] # pad index
        #color = PatternColors[patIdx] # color index
        color = nfxPat.Color

        if(_selectedPattern == trk):
            nfxSetFIRELEDCol(fire, pad, color ,_subpattern)
        else:
            nfxSetFIRELEDCol(fire, pad, color, 2)

        #if (not fire.CurrentKnobsMode in [] != device_Fire.KnobsModeMixer:
        if(nfxPat.Muted == 1):
            if _nfxBlinkTimer < _nfxBlinkSpeed:
                nfxSetFIRELEDCol(fire, pad, color, 4)

def RefreshFirePads(fire, clearfirst): 
    #print('ShowMacroButtons')
    if not isAllowed():
        return
        
    
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
    RefreshPatternPads(fire)

    #Channel Pads -- second row
    RefreshChannelPads(fire)

    # turn on the needed macro buttons - third row
    RefreshMacroPads(fire)


    RefreshFPCPads(fire)


    if(False): #if true, will hide FPC 
        #FPC A Pads
        for p in FPC_APads:
            nfxSetFIRELEDCol(fire, p, cOff,3)

        for p in FPC_BPads:
            nfxSetFIRELEDCol(fire, p, cOff,3)

def RefreshFPCPads(fire):
    if not isAllowed():
        return
        

    if(_showFPCColors): #Show Custom FPC Colors
        #FPC A Pads
        for p in FPC_APads:
            nfxSetFIRELEDCol(fire, p, FPC_APadColors[FPC_APads.index(p)],2)
        for p in FPC_BPads:
            nfxSetFIRELEDCol(fire, p, FPC_BPadColors[FPC_BPads.index(p)],2)
    else:
        for p in FPC_APads:
            if(_PadMaps[p].IsRootNote):
                col = cWhite
            else:
                col = cDimWhite
            nfxSetFIRELEDCol(fire, p, col, 0)
        for p in FPC_BPads:
            if(_PadMaps[p].IsRootNote):
                col = cWhite
            else:
                col = cDimWhite
            nfxSetFIRELEDCol(fire, p, col, 0)

def RefreshChannelPads(fire):
    global LoopSizes
    global _Patterns
    if not isAllowed():
        return
        
    #print("RefreshChannelPads")
    selPat = getSelPat()

    for padNum in ChannelPads:
        trkIdx = ChannelPads.index(padNum) # gets the 'track' index (0..7), should align with PatterPads
        padIdx = PatternChannels[trkIdx] # returns 1..8
        trkPat = _Patterns[padIdx-1]
        loopsize = selPat.Channel.LoopSize
        #print('...ChannelPad:', trkIdx, '..Mixer Mode:' , isMixerMode, '..MixPattern:', trkPat.Name, '..SelPattern:' + selPat.Name, 'loopSize:', selPat.Channel.LoopSize )
        #print('...ChannelPad:', trkIdx, trkPat.Name, trkPat.ShowPianoRoll, trkPat.ShowChannelEditor )

        if(isModeMixer() == False):
            
            if(_selectedPattern > -1):
                selPat = getSelPat()
                # determine the color to use 
                #flcol = patterns.getPatternColor(selPat.FLIndex)

                #if(flcol in PatternFLColors):
                #    col = PatternColors[PatternFLColors.index(flcol) ]
                #else:
                #    col = flcol
                
                col = selPat.Color 

                # dim factor 2
                #print('ChanPad', padNum, col)
                nfxSetFIRELEDCol(fire, padNum, col, 2)

                # set loop size indicator with no dim factor
                if(loopsize == _lsLen1 ):
                    nfxSetFIRELEDCol(fire,  ChannelPads[_cpPatLen1], col, 0)
                if(loopsize == _lsLen2):
                    nfxSetFIRELEDCol(fire, ChannelPads[_cpPatLen2], col, 0)
                if(loopsize == _lsLen3):
                    nfxSetFIRELEDCol(fire, ChannelPads[_cpPatLen3], col, 0)

                if (selPat.Muted):
                    nfxSetFIRELEDCol(fire, ChannelPads[_cpMute], col, 4)

                if(selPat.ShowChannelEditor == 0):
                    nfxSetFIRELEDCol(fire, ChannelPads[_cpShowCE], col, 4)
                else:
                    nfxSetFIRELEDCol(fire, ChannelPads[_cpShowCE], col, 2)


                if(selPat.ShowPianoRoll == 0):
                    nfxSetFIRELEDCol(fire, ChannelPads[_cpShowPR], col, 4)
                else:
                    nfxSetFIRELEDCol(fire, ChannelPads[_cpShowPR], col, 2)

                if(selPat.ShowChannelSettings == 0):
                    nfxSetFIRELEDCol(fire, ChannelPads[_cpShowCS], col, 4)
                else:
                    nfxSetFIRELEDCol(fire, ChannelPads[_cpShowCS], col, 2)

        else: # mixer mode
            # set channel pattern color - second row
            if(trkPat.Muted == 1):
                nfxSetFIRELEDCol(fire, padNum, cOff, 0)        
            else:
                nfxSetFIRELEDCol(fire, padNum, cDimWhite, 0)  
            
def GetScaleGrid(rootNote = 0, startOctave = 2, scale = HARMONICSCALE_MINORPENTATONIC):
    global _PadMaps
    #get lowest octave line
    lineGrid = [[0] for y in range(8)]    
    notesInScale = GetScaleNoteCount(scale)    
    BuildNoteGrid(lineGrid, 8, 1, rootNote, startOctave, scale)
    for colOffset in range(0,8):
        for row in range(0,4):
            noteVal = lineGrid[colOffset][0] + (12*row)
            revRow = 3-row # reverse to go from bottom to top
            rowOffset = 16 * revRow # 0,16,32,48
            padIdx = rowOffset + colOffset
            _PadMaps[padIdx].MIDINote = noteVal
            _PadMaps[padIdx].IsRootNote = (colOffset == 0) or (colOffset == notesInScale) 
            #print('...pMap.MIDINote', _PadMaps[padIdx].MIDINote, _PadMaps[padIdx].IsRootNote)            
    
def RefreshMacroPads(fire):
    # Macro Pads - Third row
    if not isAllowed():
        return

    for macPad in MacroPads:
        macIdx = MacroPads.index(macPad)
        macCol = MacroColors[macIdx]
        nfxSetFIRELEDCol(fire, macPad, macCol, 2)

        if(macIdx == 2): # special case for repeat button
            if(_RepeatNote):
                if _nfxBlinkTimer < _nfxBlinkSpeed:
                    nfxSetFIRELEDCol(fire, macPad, cWhite, 0)        
                else:
                    nfxSetFIRELEDCol(fire, macPad, macCol, 0)
    
#endregion

#region Pad Handlers
def HandleControlPress(fire, event):
    global _lastEvent
    #print('ControlPress')
    Update_Fire(fire)     
    RefreshFirePads(fire, False)

def HandleFPCPress(fire, event, m):
    global _RepeatNote
    global _IsRepeating
    wasHandled = False
    chan = channels.channelNumber()
    #print("---------------------------")
    #print('HandleFPCPress', event.data1, event.data2, m)
    padIdx = event.data1-4 # +4 from 0 based pads I normally refer to....
    note = _PadMaps[padIdx].MIDINote
    vel = event.data2
    tdiv = 3
    rptTime = int(GetTempoDiv(tdiv))
    
    
    if(_showFPCColors):
        note = m 
        fpcNoteIdx = _FPC_Notes.index(note)
        padNoteVal = _PAD_Notes[fpcNoteIdx] + device_Fire.PadFirst - 4 # -4 is the FPC offset
    else:
        padNoteVal = note

    if event.midiId == MIDI_NOTEON:

        #print('.......FPC', event.data1, 'PadIdx', padIdx,'m', m,  'Note', note, 
        #   'MIDINote', _PadMaps[padIdx].MIDINote, 'RPT:', _RepeatNote, rptTime)

        channels.midiNoteOn(chan, note, 112)

        if(_RepeatNote) and (not _IsRepeating):
            _IsRepeating = True 
            #print('-----------> Note', note, 'NewNote', padNoteVal)
            event.data1 = padNoteVal
            device.repeatMidiEvent(event, rptTime, rptTime)        
            event.handled = True 
    else:
        print('FPC', event.data1, 'OFF', _RepeatNote)
        channels.midiNoteOn(chan, note, 0)
        if(_RepeatNote) and (_IsRepeating):
            _IsRepeating = False 
            device.stopRepeatMidiEvent()
    
    #print("---------------------------")
    return True #wasHandled  

# needs to be called from OnMidiMsg NOTE ON /OFF section of device_Fire
def HandlePadPress(fire, event):
    global _lastEvent
    global _PadMaps
    #print('HandlePadPress', event.data1, event.data2)
    Update_Fire(fire)     
    _lastEvent.status = event.status

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

        if(padIndex in ProgressPads):
           padOffs = ProgressPads.index(padIndex) 
           padDiv = 1/len(ProgressPads) 
           padLimit = padDiv * padOffs
           print(padOffs, padDiv, padLimit)
           transport.setSongPos(padLimit)

    if (event.midiId in [MIDI_NOTEOFF]):
        #print("HandlePadPress.NOTEOFF --->", event.data1, event.data2, event.midiId)
        nfxSetFIRELED(fire, padIndex, 0, 0, 0)
 
    # refresh the buttons
    RefreshFirePads(fire, False)

def HandleChannelPads(fire, PadIndex):
    global LoopSizes
    global _MutedTracks 
    global _Patterns

    #print('HandleChannelPads', PadIndex)
    selPat = getSelPat()
    #isMixerMode = (fire.CurrentKnobsMode == device_Fire.KnobsModeMixer)
    chanPadIdx = ChannelPads.index(PadIndex) # will be the buttons number from  0..7
    nfxPat = _Patterns[chanPadIdx] # get the associated pattern 
    trkNum = nfxPat.Mixer.FLIndex 
    loopsize = selPat.Channel.LoopSize 

    #print('...ChannelPad:', chanPadIdx, nfxPat.Muted, '..MixPattern:', nfxPat.Name, '..SelPattern:' + selPat.Name, loopsize, selPat.Muted )

    if(isModeMixer()):
        MuteMixerTrack(trkNum, -1)        
    else: # channel mode uses selected

        #region loop size
        if (chanPadIdx == _cpPatLen0):
            loopsize = 0
        if (chanPadIdx == _cpPatLen1):
            loopsize = _lsLen1
        if (chanPadIdx == _cpPatLen2):
            loopsize = _lsLen2
        if (chanPadIdx == _cpPatLen3):
            loopsize = _lsLen3
        if(loopsize > -1):
            fire.DisplayTimedText('Pat Loop: ' + str(loopsize) )
            patterns.setChannelLoop(selPat.Channel.FLIndex, loopsize)
            selPat.Channel.LoopSize = loopsize
            #patterns.selectPattern(selPat.FLIndex, 0, 1)
        #endregion

        if(chanPadIdx == _cpMute): # mute channel
            trk = selPat.Mixer.FLIndex
            MuteMixerTrack(trk, -1)
        
        if(chanPadIdx == _cpShowCE): # toggle generator
            ShowChannelEditor(-1)
             #print('show gen', ui.getFocusedPluginName() )
        
        if(chanPadIdx == _cpShowPR): # toggle piano roll
            ShowPianoRoll(-1)
            
        if(chanPadIdx == _cpShowCS): # toggle ChannelSettings
            ShowChannelSettings(-1)

def HandleMacros(fire, event, PadIndex):
    global _PadMaps
    global _RepeatNote
    global _IsRepeating
    global _snapIdx 

    # check if a macro pad is pressed
    if PadIndex in MacroPads:
        #convert the padnum to a macronum
        MacroIndex = MacroPads.index(PadIndex)
        #print("MacroIndex", MacroIndex)
        MacroCol = MacroColors[MacroIndex]
        
        # If the macro color = cOff, it should not be handled.   
        if(MacroCol == cOff):
            return
        
        if MacroIndex == 0:
            SaveUndo()
        if MacroIndex == 1:
            UndoPattern()
        if MacroIndex == 2:
            _RepeatNote = not _RepeatNote
            print('repeat mode', _RepeatNote)
            if(not _RepeatNote):
                device.stopRepeatMidiEvent()
                _IsRepeating = False 
                setSnapMode(Snap_Step)
            else: 
                setSnapMode(Snap_FourthStep)
        if MacroIndex == 3:
            _snapIdx += 1
            if(_snapIdx > len(_snapModesList) - 1):
                _snapIdx = 0
            setSnapMode( _snapModesList[_snapIdx])
#            transport.globalTransport(FPT_Snap, 48) #snap toggle
        if MacroIndex == 4:
            ClearMidi(fire)
        if MacroIndex == 5:
            if(fire.AltHeld):
                RecolorPatterns()
                OnInit(fire)
            else:
                ResetUI(fire)
        if MacroIndex == 6:
            GetScaleGrid(0, 3, HARMONICSCALE_BLUES)
        if MacroIndex == 7:
            if(fire.AltHeld):
                OnInit(fire)

def HandlePatternPads(fire, padIndex):
    # activate a pattern - top row
    padIdx = PatternPads.index(padIndex)
    patNum = PatternChannels[padIdx]
    ActivatePattern(patNum, True, True)
    RefreshFirePads(fire, False)

def ActivatePattern(patNum, showPlugin = False, setMixer = True):
    global _PadMaps
    global _selectedPattern
    global _subpattern
    global _subPat
    global _showFPCColors
    global _drumMixerTrk
    global _IsActivating

    if(_IsActivating):
        return
    
    _IsActivating = True 

    nfxPat = _Patterns[patNum-1] # 0 based
    mixerNum = nfxPat.Mixer.FLIndex 
    selPat = getSelPat()
    mixerNumPrev = selPat.Mixer.FLIndex

    # close the previous channel plugin
    if(_selectedPattern > -1): 
        channels.showEditor(selPat.Channel.FLIndex, 0)

    if(mixerNum != mixerNumPrev): #mixer changed, so reset subs
        _subpattern = 0

    #gets a list of patterns associated to the mixer chan
    subPatterns = [x for x in _Patterns if x.Mixer.FLIndex == mixerNum]
    numOfChannels = len(subPatterns)

    #determine sub index limit and reset if needed
    if(_subpattern >= numOfChannels) or (numOfChannels == 1): 
        _subpattern = 0

    #use subchannel index from results
    nfxPat = subPatterns[_subpattern] 
    
    print('IN->Pattern:', _subpattern,  '_Sel:', _selectedPattern, 'Mixer:', mixerNum, )

     # increment sub pattern ie +0 (master), +1, +2 when needed
    if(numOfChannels > 1 ):
        _subpattern += 1
    if(_subpattern >= numOfChannels): 
        _subpattern = 0

    patterns.jumpToPattern(nfxPat.FLIndex)
    _selectedPattern = nfxPat.FLIndex
    isFPC = nfxPat.Name.startswith('FPC') or nfxPat.Name.startswith('...FPC')

    if (isFPC): # show FPC colors
        #print('fpc', mixerNum, _drumMixerTrk)
        _showFPCColors = True
    else:
        #print('not fpc', mixerNum, _drumMixerTrk)
        _showFPCColors = False

    RefreshFPCPads(_Fire)

    if(setMixer):
        mixer.setTrackNumber(mixerNum) 
    if(showPlugin):
        ui.showWindow(widPlugin) #wid was missing from midi.py
    
    ShowChannelEditor(nfxPat.ShowChannelEditor)
    ShowPianoRoll(nfxPat.ShowPianoRoll)

    _IsActivating = False

    #ui.openEventEditor(mixer.getTrackPluginId(trkNum,0) + REC_Mixer_Vol, EE_EE)
    #ui.openEventEditor(channels.getRecEventId(trkNum) + REC_Mixer_Vol, EE_EE)
    #ui.openEventEditor(channels.getRecEventId(chanNum) + REC_Chan_Pitch, EE_EE)
    print('OUT->Pattern:', nfxPat.FLIndex, '_Sel:', _selectedPattern, 'Mixer:', mixerNum, )
#endregion

  
    
#region nfxFuncs
def InitMacros():
    #initialize tha macro list
    global _Macros
    for i in range(len(MacroPads)):
        m = TnfxMacro()
        m.index = i
        m.color = MacroColors[i]
        m.padindex = MacroPads[i]
        m.name = MacroNames[i]
        _Macros.append(m)

def ResetPadMaps():
    global _PadMaps
    print('...Reset PadMaps')
    # map the pads
    patidx = -1
    _PadMaps.clear()
    #print('Pattern Pads...' , PatternPads)
    for padNum in range(0, 64): # the pads
        pMap = TnfxPadMap()
        pMap.FirePadIndex = padNum
        pMap.MIDINote = -1

        if(padNum in FPC_APads):
            pMap.Name = 'FPC-A'
            pMap.MIDINote = -1

        if(padNum in FPC_BPads):
            pMap.Name = 'FPC-B'
            pMap.MIDINote = -1

        #iterates the FIRE pads defined for patterns - top row
        if padNum in PatternPads:
            patidx = PatternPads.index(padNum) # ex.  Pad[0] = _Patterns[1]
            patNum = PatternChannels[patidx]
            nfxPat = _Patterns[patNum-1] #0 based
            #print('...added pad:', patNum, nfxPat.Name, nfxPat.FLIndex, '-->Channel:', nfxPat.Channel.Name, nfxPat.Channel.FLIndex,
            #              '-->Mixer:', nfxPat.Mixer.Name, nfxPat.Mixer.FLIndex)
            pMap.Name = nfxPat.Name
            pMap.Mixer = nfxPat.Mixer
            pMap.Channel = nfxPat.Channel
            pMap.Color = nfxPat.Color
            #colIdx = nfxPat.FLIndex-1 # 0 based
            #print('ColorIdx:', colIdx, 'pMap:', pMap.Name, pMap.Mixer.Name, pMap.Channel.Name)
            #pMap.Color = PatternColors[colIdx] 

        if padNum in MacroPads:                 # is the pad in the list of Macro Pads?
            macIdx = MacroPads.index(padNum)    # get the Macro Index
            pMap.FireMacroIndex = macIdx
            pMap.Color = MacroColors[macIdx]

        _PadMaps.append(pMap)

        if(len(pMap.Name) > 1 ) and (False): #todo logic for showing
            print('......Pad Mapped: ', pMap.Name, pMap.FirePadIndex, pMap.MIDINote)

def Update_Fire(fire):
    global _Fire
    _Fire = fire

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
    global _isClearing

    if _isClearing:
        return

    _isClearing = True 
    isRec = transport.isRecording()
    if(isRec):
        transport.record() #turn off

    if(fire.AltHeld): 
        fire.DisplayTimedText('Clearing ALL')
        pNow = _selectedPattern
        patcount = patterns.patternCount()
        for p in range(1, patcount+1):
            ActivatePattern(p)
            ClearPattern()
    else:
        #print('Clearing Pattern')
        ClearPattern()

    if(isRec):
        transport.record() 
    
    #time.sleep(0.2)
    _isClearing = False

def ClearPattern():
    ui.showWindow(widChannelRack)
    ui.cut()

def SaveUndo():
    _Fire.DisplayTimedText("Save Undo")
    general.saveUndo("nfxFIRE", UF_EEPR)

def UndoPattern():
    _Fire.DisplayTimedText("Undo...")
    general.undo()

def RecordMIDINote(name, mixerch, note, vel, dur, midich):
    # I use this to sample MIDI hardware like a roland TD-30 
    # It plays and samples a series of notes to a folder
    #
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
    #patcol = PatternFLColors[0]
    offset = 1
    plcount = playlist.trackCount()
    chan = -1
    patcol = patterns.getPatternColor(1)

    for patIdx in range(1,patcount+1):
        patterns.jumpToPattern(patIdx)
        patcol = patterns.getPatternColor(patIdx)
        pName = patterns.getPatternName(patIdx)
        c = channels.selectedChannel(0,0,1)
        print('Pattern:', pName, patIdx, patcol, chan, c)
        if(pName.startswith('...')): #use prev color
            patterns.setPatternColor(patIdx, patcol)
            PatternChannels[c] = chan
            offset += 1
        else:# use new color
            #patcol = getSelPat().Color # PatternFLColors[patIdx-offset]
            patcol = patterns.getPatternColor(patIdx)
            patterns.setPatternColor(patIdx, patcol)
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

def InitAll(fire):
    #show the banner....
    print("_______________nfxFIRE v 0.0.pre-alpha - warbeats.com_______________")
    _Fire.DisplayTimedText("nfxFIRE v0.0...")
    print('...Initializing')
    Update_Fire(fire) 
    
    # read the FL tracks info...
    lastknobmode = fire.CurrentKnobsMode
    print('...Syncing FL Track data')
    BuildMixers()
    BuildChannels()
    BuildPatterns()    
    ResetMutes()

    # read our pad defs and colors and assign as needed
    print('...Syncing FIRE Pad data')
    InitMacros()    
    ResetPadMaps()

    # set the C minor Penta for now...
    GetScaleGrid(0,3, HARMONICSCALE_MINORPENTATONIC) # must Call after resetting Pad maps
    
    RefreshFirePads(fire, False)
    print("____________________________________________________________________")





#endregion        

        


        
    


















