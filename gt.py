import fl

# Global Transport indexes
FPT_Jog = 0 # (jog) generic jog (can be used to select stuff)
FPT_Jog2 = 1 # (jog) alternate generic jog (can be used to relocate stuff)
FPT_Strip = 2 # touch-sensitive jog strip, value will be in -65536..65536 for leftmost..rightmost
FPT_StripJog = 3 # (jog) touch-sensitive jog in jog mode
FPT_StripHold = 4 # value will be 0 for release, 1,2 for 1,2 fingers centered mode, -1,-2 for 1,2 fingers jog mode (will then send FPT_StripJog)
FPT_Previous = 5 # (button)
FPT_Next = 6 # (button)
FPT_PreviousNext = 7 # (jog) generic track selection
FPT_MoveJog = 8 # (jog) used to relocate items

FPT_Play = 10 # (button) play/pause
FPT_Stop = 11 # (button)
FPT_Record = 12 # (button)
FPT_Rewind = 13 # (hold)
FPT_FastForward = 14 # (hold)
FPT_Loop = 15 # (button)
FPT_Mute = 16 # (button)
FPT_Mode = 17 # (button) generic or record mode

FPT_Undo = 20 # (button) undo/redo last, or undo down in history
FPT_UndoUp = 21 # (button) undo up in history (no need to implement if no undo history)
FPT_UndoJog = 22 # (jog) undo in history (no need to implement if no undo history)

FPT_Punch = 30 # (hold) live selection
FPT_PunchIn = 31 # (button)
FPT_PunchOut = 32 # (button)
FPT_AddMarker = 33 # (button)
FPT_AddAltMarker = 34 # (button) add alternate marker
FPT_MarkerJumpJog = 35 # (jog) marker jump
FPT_MarkerSelJog = 36 # (jog) marker selection

FPT_Up = 40 # (button)
FPT_Down = 41 # (button)
FPT_Left = 42 # (button)
FPT_Right = 43 # (button)
FPT_HZoomJog = 44 # (jog)
FPT_VZoomJog = 45 # (jog)
FPT_Snap = 48 # (button) snap on/off
FPT_SnapMode = 49 # (jog) snap mode

FPT_Cut = 50 # (button)
FPT_Copy = 51 # (button)
FPT_Paste = 52 # (button)
FPT_Insert = 53 # (button)
FPT_Delete = 54 # (button)
FPT_NextWindow = 58 # (button) TAB
FPT_WindowJog = 59 # (jog) window selection

FPT_F1 = 60 # button
FPT_F2 = 61 # button
FPT_F3 = 62 # button
FPT_F4 = 63 # button
FPT_F5 = 64 # button
FPT_F6 = 65 # button
FPT_F7 = 66 # button
FPT_F8 = 67 # button
FPT_F9 = 68 # button
FPT_F10 = 69 # button

FPT_Enter = 80 # (button) enter/accept
FPT_Escape = 81 # (button) escape/cancel
FPT_Yes = 82 # (button) yes
FPT_No = 83 # (button) no

FPT_Menu = 90 # (button) generic menu
FPT_ItemMenu = 91 # (button) item edit/tool/contextual menu
FPT_Save = 92 # (button)
FPT_SaveNew = 93 # (button) save as new version

FPT_PatternJog = 100 # (jog) pattern
FPT_TrackJog = 101 # (jog) mixerr track
FPT_ChannelJog = 102 # (jog) channel

FPT_TempoJog = 105 # (jog) tempo (in 0.1BPM increments)
FPT_TapTempo = 106 # (button) tempo tapping
FPT_NudgeMinus = 107 # (hold) tempo nudge -
FPT_NudgePlus = 108 # (hold) tempo nudge +

FPT_Metronome = 110 # (button) metronome
FPT_WaitForInput = 111 # (button) wait for input to start playing
FPT_Overdub = 112 # (button) overdub recording
FPT_LoopRecord = 113 # (button) loop recording
FPT_StepEdit = 114 # (button) step edit mode
FPT_CountDown = 115 # (button) countdown before recording

FPT_NextMixerWindow = 120 # (button) tabs between plugin windows in the current mixer track
FPT_MixerWindowJog = 121 # (jog) mixer window selection
FPT_ShuffleJog = 122 # main shuffle (in increments of 1)

FPT_ArrangementJog = 123 # to switch between PL arrangements

FPT_AnyJog = [
	FPT_Jog, FPT_Jog2, FPT_StripJog, FPT_PreviousNext, FPT_MoveJog, FPT_UndoJog, FPT_MarkerJumpJog, FPT_MarkerSelJog,
  FPT_HZoomJog, FPT_VZoomJog, FPT_SnapMode, FPT_WindowJog, FPT_PatternJog, FPT_TrackJog, FPT_ChannelJog, FPT_TempoJog
	]
	
# ProcessMIDIEvent flags
PME_LiveInput			= 0x0001
PME_System				= 0x0002	# can do system stuff (play/pause.. mostly safe things)
PME_System_Safe		= 0x0004	# can do critical system stuff (add markers.. things that can't be done when a modal window is shown)
PME_PreviewNote		= 0x0008	# note trigger previews notes or controls stuff
PME_FromHost			= 0x0010	# when the app is hosted
PME_FromMIDI			= 0x0020	# coming from MIDI event
PME_Default				= PME_LiveInput|PME_System|PME_System_Safe|PME_PreviewNote|PME_FromMIDI

# flags & results for GlobalTransport
GT_Cannot				= -1
GT_None					= 0
GT_Plugin				= 1 # focused plugin
GT_Form					= 2 # focused form
GT_Menu					= 4 # menu
GT_Global				= 8 # global
GT_All					= GT_Plugin|GT_Form|GT_Menu|GT_Global

def GlobalTransport(action, value, PMEFlags=PME_Default, Flags=GT_All):
	if not (action in FPT_AnyJog):
		value = 2 if value else 0
	fl.globaltransport(action, value, PMEFlags, Flags)
	
def Play(IsPressed=True):
	GlobalTransport(FPT_Play, IsPressed)

def Stop(IsPressed=True):
	GlobalTransport(FPT_Stop, IsPressed)

def Record(IsPressed=True):
	GlobalTransport(FPT_Record, IsPressed)

def Rewind(IsPressed=True):
	GlobalTransport(FPT_Rewind, IsPressed)

def FastForward(IsPressed=True):
	GlobalTransport(FPT_FastForward, IsPressed)

def Loop(IsPressed=True):
	GlobalTransport(FPT_Loop, IsPressed)

def LoopRecord(IsPressed=True):
	GlobalTransport(FPT_LoopRecord, IsPressed)
	
def AddMarker(IsPressed=True):
	GlobalTransport(FPT_AddMarker, IsPressed)

def Jog(offset):
	GlobalTransport(FPT_Jog, offset)

def MarkerJump(offset):
	GlobalTransport(FPT_MarkerJumpJog, offset)
