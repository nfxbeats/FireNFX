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
import channels
import mixer
import playlist
import patterns
import general

import device_Fire

from device_Fire import TMidiEvent


class TFirePadMap:
    def __init__(self):
        self.Name = ""
        self.FirePadIndex = -1      # the pad num 0..63
        self.FireMacroIndex = -1    # the macro index 0..8
        self.FireChannelIndex = -1  # the channel bar buttons 0..8   
        self.FLPatternNum = -1      # the FL Pattern number
        self.FLChannelNum = -1      # the FL Channel number
        self.FLMixerTrackNum = -1   # the FL Mixer Track number
        self.FireColor = 0x000000
        self.FLColor = 0x000000

class TFireMacro:
    def __init__(self):
        self.index = -1
        self.name = ""
        self.color = 0x000000
        self.padindex = -1

cOff        = 0x000000
cWhite      = 0xFFFFFF
cSilver     = 0X606060
cDimWhite   = 0x101010

cMagenta    = 0x7F0040

cRed        = 0xFF0000
cFLRed      = 0xA00000

cOrange     = 0xFf2000
cFLOrange  = 0xFF8000

cYellow     = 0xFFFF00

cPurple         = 0x1000FF
cFLPurple       = 0x6238A9

cPurpleLight    = 0x20207F

cBlue       = 0x0000FF
cFLBlue     = 0x204080

cCyan       = 0x00FFFF
cFLCyan     = 0x008080

cGreen      = 0x00FF00
cFLGreen    = 0x008000

cBlueDark  = cBlue & 0x001010
cBlueMed   = 0x0020FF
cBlueLight = cBlue | 0x004040 

cX1 = cPurple & 0x100010
cX2 = cPurple | 0x100010 
cX3 = cPurple | 0x7f007f


#pads to display the plalist patterns - top row
PatternPads = [8, 9, 10, 11, 12, 13, 14, 15]

# FL Patterns to associate with the above pads
PatternChannels = [1,2,3,4,5,6,7,8]

#default colors for the patterns row
PatternColors = [cGreen, cCyan, cYellow, cOrange, cRed, cMagenta, cPurple, cBlue]

#fl specific colors for coloring the patterns in FL
PatternFLColors = [cFLGreen, cFLCyan, cYellow, cFLOrange, cFLRed, cMagenta, cFLPurple, cFLBlue ]

ChannelPads = [24, 25, 26, 27, 28, 29, 30 , 31]

MacroPads = [40, 41, 42, 43, 
             44, 45, 46, 47]

MacroColors = [cDimWhite, cRed, cDimWhite, cBlue, cDimWhite, cCyan, cDimWhite, cOrange]

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

fireMacros = list()
firePadMap = list() 
isClearing = False
nfxBlinkTimer = 0
nfxBlinkSpeed = 5
nfxUpdateTimer = 9999
LoopSizes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
Muted =     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
lastevent = device_Fire.TMidiEvent()
lastknobmode = -1
lastpat = -1
nfxRepeatNote = False
nfxIsRepeating = False

# call this from the end of TFire.OnInit
def OnInit(fire):
    print("OnInit")
    #set the default mode for me
    fire.CurrentMode = device_Fire.ModeDrum 
    lastknobmode = fire.CurrentKnobsMode
    InitMacros()    
    ResetPadMaps()
    ShowMacroButtons(fire, False)

# called from TFire.OnIdle
def OnIdle(fire):
    global nfxBlinkTimer
    global nfxUpdateTimer
    global lastknobmode
    global lastpat 

    
    UpdateProgress(fire)

    refresh = False
    
    if(lastknobmode != fire.CurrentKnobsMode):
        lastknobmode = fire.CurrentKnobsMode
        refresh = True 

    if(lastpat != patterns.patternNumber()):
        #print('pat change')
        lastpat = patterns.patternNumber()
        refresh = True 

    if(refresh):
        ShowMacroButtons(fire, False) 
        
    nfxBlinkTimer += 1
    if nfxBlinkTimer >= nfxBlinkSpeed * 4:
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
    patPads = [x for x in firePadMap if x.FLPatternNum > 0] 
    for p in patPads: # PatternPads:
        trk = p.FLMixerTrackNum
        pat = p.FLPatternNum
        patcol = p.FireColor # PatternColors[pat - 1]

        if (patterns.isPatternSelected(pat)):
            nfxSetFIRELEDCol(fire, p.FirePadIndex, patcol ,0)
        else:
            nfxSetFIRELEDCol(fire, p.FirePadIndex, patcol, 3)
        
        if fire.CurrentKnobsMode != device_Fire.KnobsModeMixer:
            if(Muted[trk] == 1):
                if nfxBlinkTimer < nfxBlinkSpeed:
                    nfxSetFIRELEDCol(fire, p.FirePadIndex, cOff, 0)

def UpdateChannelPads(fire):
    global LoopSizes

    chan = channels.selectedChannel(0,0,1)
    channame = channels.getChannelName(chan)
    loopsize = LoopSizes[chan]

    for s in ChannelPads:
        pMap = firePadMap[s]
        pMapPat = firePadMap[PatternPads[pMap.FireChannelIndex]]
        trk = pMapPat.FLMixerTrackNum

        # determine the color to use
        flcol = patterns.getPatternColor(patterns.patternNumber()) & 0xFFFFFF
        if(flcol in PatternFLColors):
            col = PatternColors[PatternFLColors.index(flcol) ]
        else:
            col = flcol

        if fire.CurrentKnobsMode != device_Fire.KnobsModeMixer:
            nfxSetFIRELEDCol(fire, s, col, 2)
            # dim factor 2,    # set loop size indicator with no dim factor
            if(loopsize == 16):
                nfxSetFIRELEDCol(fire,  ChannelPads[1], col, 0)
            if(loopsize == 32):
                nfxSetFIRELEDCol(fire, ChannelPads[2], col, 0)
            if(loopsize == 64):
                nfxSetFIRELEDCol(fire, ChannelPads[3], col, 0)
            if (Muted[trk] == 1):
                nfxSetFIRELEDCol(fire, ChannelPads[4], cDimWhite, 0)

        else: # mixer mode
            # set channel pattern color - second row
            if(Muted[trk]):
                nfxSetFIRELEDCol(fire, s, cOff, 0)        
            else:
                nfxSetFIRELEDCol(fire, s, cDimWhite, 0)        

def UpdateMacroPads(fire):
    # Macro Pads - Third row
    macPads = [x for x in firePadMap if x.FireMacroIndex > -1 ] 
    for m in macPads:
        nfxSetFIRELEDCol(fire, m.FirePadIndex, m.FireColor, 2)

# called from OnMidiMsg, right before the last line
def OnMidiMsg(fire, event):
    global nfxIsRepeating
    print("OnMidiMsg", event.data1)
    wasHandled = False

    if event.midiId in [midi.MIDI_NOTEON, midi.MIDI_NOTEOFF]:
        if (event.data1 >= device_Fire.PadFirst) & (event.data1 <= device_Fire.PadLast):
                    
            event.data1 -= device_Fire.PadFirst # event.data1 is now 0..63    

            if (event.midiId == midi.MIDI_NOTEON):
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
            
            if (event.midiId == midi.MIDI_NOTEOFF):
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

def ShowMacroButtons(fire, clearfirst): 
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
    UpdateChannelPads(fire)

    # turn on the needed macro buttons - third row
    UpdateMacroPads(fire)


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
    print('ControlPress')
    ShowMacroButtons(fire, False)

# needs to be called from OnMidiMsg NOTE ON /OFF section of device_Fire
def HandlePadPress(fire, event):
    global lastevent
    global firePadMap

    lastevent.status = event.status

    if (fire.CurrentDrumMode == device_Fire.DrumModeFPC):
        event.data1 -= 4 # reset the offset to get the correct pad index  - bug in the device_Fire code??

    print('HandlePadPress', event.data1, event.data2)

    # this is where the magic happens...
    if (event.midiId in [midi.MIDI_NOTEON]):
        print("HandlePadPress.NOTEON --->", event.data1, event.data2, event.midiId)
        nfxSetFIRELEDCol(fire, event.data1, cWhite, 1) #turn led white when pressed.
        PadIndex = event.data1

        pMap = TFirePadMap()
        
        if(len(firePadMap) > PadIndex):
            pMap = firePadMap[PadIndex]
            #print('pMap', PadIndex, pMap.Name, pMap.FirePadIndex)

            # check the pattern pads first in case they change something
            if(pMap.FLPatternNum > -1):
                HandlePatternPads(fire, pMap) 

            if(pMap.FireChannelIndex > -1):
                HandleChannelPads(fire, pMap)

            if(pMap.FireMacroIndex > -1):
                HandleMacros(fire, event, pMap.FirePadIndex)

    if (event.midiId in [midi.MIDI_NOTEOFF]):
        print("HandlePadPress.NOTEOFF --->", event.data1, event.data2, event.midiId)
        nfxSetFIRELED(fire, event.data1, 0, 0, 0)
 
    # refresh the buttons
    ShowMacroButtons(fire, False)

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
                OnInit(fire)
                RecolorPatterns()
            else:
                ResetUI(fire)

        if(MacroIndex == 5):
            print('repeat mode')
            nfxRepeatNote = not nfxRepeatNote

        if(MacroIndex == 7):
            print("Macro-7")

def ResetPadMaps():
    global firePadMap
    print('ResetPadMaps')

    # map the pads
    patidx = -1
    firePadMap.clear()
    for pNum in range(0, 64): # the pads
        pMap = TFirePadMap()
        pMap.FirePadIndex = pNum

        if pNum in PatternPads:
            pMap.FLPatternNum = PatternPads.index(pNum)+1
            patterns.jumpToPattern(pMap.FLPatternNum) #force channel to change
            pMap.Name = "Pattern Num-" + str(pMap.FLPatternNum)
            pMap.FLMixerTrackNum = getMixerTrackForPattern(pMap.FLPatternNum)
            pMap.FLChannelNum = channels.selectedChannel(0,0,1)
            mixer.muteTrack(pMap.FLMixerTrackNum, 0)
            Muted[pMap.FLChannelNum] = 0
            pMap.FireColor = PatternColors[pMap.FLPatternNum-1]
            pMap.FLColor = PatternFLColors[pMap.FLPatternNum-1]

            

        if pNum in ChannelPads:
            pMap.FireChannelIndex = ChannelPads.index(pNum)
            pMap.FLChannelNum = -1
            pMap.Name = "Channel Idx-" + str(pMap.FireChannelIndex)
            

        if pNum in MacroPads:
            pMap.FireMacroIndex = MacroPads.index(pNum)
            pMap.Name = "Macro Idx-" + str(pMap.FireMacroIndex)
            pMap.FireColor = MacroColors[pMap.FireMacroIndex]
        
        firePadMap.append(pMap)

        if(len(pMap.Name) > 1 ):
            print('Pad Mapped: ', pMap.FirePadIndex, pMap.Name, 'flpat', pMap.FLPatternNum, 'flmixer', pMap.FLMixerTrackNum, 'flchan', pMap.FLChannelNum, 'macro', pMap.FireMacroIndex)

def getMixerTrackForPattern(pat):
    trkNum = -1
    #patterns.jumpToPattern(pat)
    ui.showWindow(midi.widChannelRack)
    c = channels.selectedChannel(0,0,1)
    if(c > -1):
        trkNum = channels.getTargetFxTrack(c)
    #print('pattern', pat, 'mixer', trkNum )
    return trkNum 

def getMixerTrackForChannel(chan):
    return channels.getTargetFxTrack(chan) 

def HandleChannelPads(fire, pMap):
    global LoopSizes
    global Muted 

    print('HandleChannelPads', pMap.FireChannelIndex)
    if(pMap.FireChannelIndex > -1):

        ChanIndex = channels.selectedChannel(0,0,1)
        ChanName = channels.getChannelName(ChanIndex)
        trk = getMixerTrackForChannel(ChanIndex)

        if fire.CurrentKnobsMode != device_Fire.KnobsModeMixer:
            loopsize = -1
            if (pMap.FireChannelIndex == 0):
                loopsize = 0
            if (pMap.FireChannelIndex == 1):
                loopsize = 16
            if (pMap.FireChannelIndex == 2):
                loopsize = 32
            if (pMap.FireChannelIndex == 3):
                loopsize = 64

            if(loopsize > -1):
                fire.DisplayTimedText('Pat Loop: ' + str(loopsize) )
                patterns.setChannelLoop(ChanIndex, loopsize)
                LoopSizes[ChanIndex] = loopsize
            
            if(pMap.FireChannelIndex == 4): # mute channel
                MuteTrack(fire, trk)

        else: # mixer mode
            # get the Pattern Pads mixer number
            pMapPat = firePadMap[PatternPads[pMap.FireChannelIndex]]
            trk = pMapPat.FLMixerTrackNum
            MuteTrack(fire, trk)

def MuteTrack(fire, trk):
    global Muted 
    #print('Mute Track:', trk)
    mixer.muteTrack(trk)
    name = mixer.getTrackName(trk)
    if (Muted[trk] == 0): 
        fire.DisplayTimedText('Mute: ' + name)
        Muted[trk] = 1
    else:
        fire.DisplayTimedText('Un-Mute: ' + name)
        Muted[trk] = 0

def HandlePatternPads(fire, pMap):
    # activate a pattern - top row
    patterns.jumpToPattern(pMap.FLPatternNum)
    ui.showWindow(midi.widChannelRack)
    mixer.setTrackNumber(pMap.FLMixerTrackNum)    
    #print(pMap.Name)
           
def ResetUI(fire):
    fire.DisplayTimedText("Reset UI...")
    transport.globalTransport(midi.FPT_F12, 1) #close all...
    ui.showWindow(midi.widMixer)

    # todo: scroll to master channel or FX channel and showMIDI, etc
    mixer.setTrackNumber(0)

    ui.showWindow(midi.widPlaylist)
    # todo: press 4 to fill screen

    ui.showWindow(midi.widChannelRack)
    #todo: bring up any other windows.. ie control surface, etc

    #open the piano roll
    chan = channels.selectedChannel(0,0,1)
    ui.openEventEditor(channels.getRecEventId(chan) + midi.REC_Chan_PianoRoll, midi.EE_PR)
    ui.showWindow(midi.widPianoRoll)

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
    ui.showWindow(midi.widChannelRack)
    #channels.selectAll()
    time.sleep(0.2)
    ui.cut()
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
    while (mixer.getTrackPeaks(mixerch, midi.PEAK_LR) >= 0.001):
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
            ui.showWindow(midi.widChannelRack)
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
    for p in range(1, patterns.patternCount() ):
        #print('Pat', p)
        trk = getMixerTrackForPattern(p)
        mixer.muteTrack(trk, 0)
        Muted[trk] = 0
        #print(Muted)


        
    


















