from midi import *
from nfxFireColors import * 

_globalDimDef = 2
_globalDimMax = 0

#AKAI Pads  0..63 starts from top left  to right bottom

#pads to display the playlist patterns - top row, last 8
PatternPads = [8, 9, 10, 11, 12, 13, 14, 15]

# FL Patterns to associate with the above pads - 
PatternChannels = [1,2,3,4,5,6,7,8]

# these go under the  PatternPads - second row, last 8
ChannelPads = [24, 25, 26, 27, 28, 29, 30 , 31]

# set which channel pad does what.  value of below relate to index of above 
_cpPatLen0 = 0
_cpPatLen1 = 1
_cpPatLen2 = 2
_cpPatLen3 = 3
_cpMute = 4
_cpShowCE = 5
_cpShowPR = 6
_cpShowCS = 7

# define the length of the pattern sizes.
_lsLen1 = 32
_lsLen2 = 64
_lsLen3 = 128

#define the pads to use for macros and their colors and names
MacroPads = [40, 41, 42, 43, 44, 45, 46, 47]
MacroColors = [cWhite, cWhite, cCyan, cMagenta, cRed, cDimWhite, cDimWhite, cBlueDark]
MacroNames    = ['Set Velocity', 'Set Octave',  'Set Snap', 'Copy MIDI',  'Clear MIDI',     'Mute Preset1',     'Mute Preset2',     'Toggle Mute']
MacroAltNames = ['Set Root',     'Set Scale',   'Note Rpt', 'Paste MIDI', 'Clear ALL MIDI', 'Set Mute Preset1', 'Set Mute Preset2', '']

#these define the pads to use for the progress indicator
ProgressPads = [56, 57, 58, 59, 60, 61, 62, 63]
ProgressPadsDim = cDimWhite
ProgressPadsOn = cWhite 

#note these are referenced via the AKAI PadIndex (0..63)
# and NOT the FPC Pad num. AKAI runs top left to bottom right
FPC_APads = [0, 1, 2, 3, 16, 17, 18, 19,32, 33, 34, 35, 48, 49, 50, 51]
FPC_BPads = [4, 5, 6, 7, 20, 21, 22, 23,36, 37, 38, 39, 52, 53, 54, 55]

#these define the FL Studio index running from bottom left to top right for the A Pads and B Pads separately
FPC_APads_FL = [48, 49, 50, 51, 32, 33, 34, 35, 16, 17, 18, 19, 0, 1, 2, 3]
FPC_BPads_FL = [52, 53, 54, 55, 36, 37, 38, 39, 20, 21, 22, 23, 4, 5, 6, 7]
 
Perf_Pads = [0,1,2,3, 4, 5, 6, 7,
             16, 17, 18, 19, 20, 21, 22, 23,
             32, 33, 34, 35, 36, 37, 38, 39, 
             48, 49, 50 , 51, 52, 53, 54, 55]

# arrays are used to unencode the translation, so when we do a "repeat note" it sends the untranslated value
# if I didnt do this, the note would get re-translated into the wrong note. 
# im sure there is a better way but my brain is tired.
_PAD_Notes = [52, 53, 54, 55, 56, 57, 58, 59, 
              36, 37, 38, 39, 40, 41, 42, 43, 
              20, 21, 22, 23, 24, 25, 26, 27,
               4,  5,  6,  7,  8,  9, 10, 11, -1]

_FPC_Notes = [49, 55, 51, 53, 
              48, 47, 45, 43, 
              40, 38, 46, 44,
              37, 36, 42, 54, 

              72, 73, 74, 75,
              68, 69, 70, 71, 
              64, 65, 66, 67,
              60, 61, 62, 63, -1]

_FPC_Notes2 = [37, 36, 42, 54, 60, 61, 62, 63, 
              40, 38, 46, 44, 64, 65, 66, 67, 
              48, 47, 45, 43, 68, 69, 70, 71, 
              49, 55, 51, 53, 72, 73, 74, 75, -1]

_SplashOverlay = [1,4,6,7,8,9,11,14,17,18,20,22,28,29,33,35,36,38,39,40,43,46,49,52,54,59,62]
