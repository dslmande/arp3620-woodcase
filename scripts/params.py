# -*- coding: utf-8 -*-
"""All dimensions of the ARP 3620 wooden case, in mm.

Coordinate system (whole case):
  x  left -> right, 0 = outer face of the left wall
  y  front -> rear, 0 = outer face of the front wall
  z  up, 0 = underside of the base (feet are below z = 0)
"""

REV = "Rev0.5"
NAME = "ARP3620_Woodcase_" + REV

# ---------------------------------------------------------------- material
T_WALL = 12.0        # birch plywood: front, rear and end walls, cheeks
T_BASE = 9.0         # base
T_CHEEK = 12.0       # keyboard cheeks
T_STRIP = 9.0        # raised strip behind the keys (removable)
T_APRON = 9.0        # apron under the rear edge of the strip
T_FILL = 9.0         # filler behind the control panel
T_RISER = 20.0       # keybed on two aluminium Z profiles 20 x 20 x 2 (height)
T_PLATE = 2.0        # aluminium rear plate
TOLEX = 1.0          # allowance for tolex plus glue on every covered face
# The joints use these nominal thicknesses. Measure the sheets before cutting
# and enter the real values: slot widths and joint depths follow from them.
DENSITY_PLY = 0.68e-3    # g/mm^3, birch plywood
DENSITY_ALU = 2.70e-3

# ---------------------------------------------------------------- keybed
# Fatar TP/9S, 49 keys, datasheet Rev. 0.6, p. 3-4
KB_W = 683.0
KB_D = 161.5
KB_WHITE = 47.5          # mounting plane -> top of white keys
KB_BLACK = 57.77         # mounting plane -> top of black keys
KB_LIP = 39.0            # mounting plane -> lower edge of the white key front
                         # Fatar drawing 49TP9 (1:1, 2004): 39.3 at rest, 29.5 pressed;
                         # measured on the keybed: 30 pressed, 47.5 top at rest (11.11.2026)
KB_TRAVEL = 10.0
KB_REAR_FRAME = 24.0     # rear frame behind the keys (Fig. 2)
KB_BLACK_Y = (50.0, 136.0)   # black keys, measured from the front edge of the keys
KB_HOLE_D = 4.5
KB_HOLE_X = (20.65, 157.72, 322.61, 502.20, 667.40)   # from the left edge
KB_HOLE_Y = (71.5, 147.0)                             # from the front edge

# ---------------------------------------------------------------- control panel
PANEL_W, PANEL_D = 170.0, 230.0      # x, y (panel y runs from its front edge)
PANEL_T = 1.6                        # front panel is a PCB (FR4 1.6)
PANEL_HOLES = [(12.5, 12.5), (157.5, 12.5), (12.5, 217.5), (157.5, 217.5)]
PANEL_HOLE_D = 3.2
BOARD_SPACER = 12.0                  # panel -> 3620 board (clone, check with the parts)
BOARD_PARTS_BELOW = 25.0             # parts plus KK plugs under the 3620 board (envelope; measured 18, 11.11.2026)

# ---------------------------------------------------------------- clearances
GAP_PANEL = 2.0          # panel -> wood, each side, includes tolex
GAP_KB_SIDE = 3.0        # keybed -> cheek, each side, includes tolex
GAP_KB_FRONT = 3.0       # key fronts -> front wall
STRIP_OVERLAP = 15.0     # strip reaches this far over the rear frame of the keybed
LIP_ABOVE_WALL = 1.0     # lower edge of the key front sits this much above the wall top
STRIP_ABOVE_BLACK = 3.2  # strip top above the black keys

# ---------------------------------------------------------------- layout in x
X_PANEL_IN = T_WALL                                   # 12
PANEL_OPEN = PANEL_W + 2 * GAP_PANEL                  # 174
X_CHEEK_L = X_PANEL_IN + PANEL_OPEN                   # 186
X_KEYS_IN = X_CHEEK_L + T_CHEEK                       # 198
KEYS_OPEN = KB_W + 2 * GAP_KB_SIDE                    # 689
X_CHEEK_R = X_KEYS_IN + KEYS_OPEN                     # 887
X_WALL_R = X_CHEEK_R + T_CHEEK                        # 899
W = X_WALL_R + T_WALL                                 # 911

# ---------------------------------------------------------------- layout in y
Y_IN = T_WALL                                         # 12, inner face front wall
Y_KB0 = Y_IN + GAP_KB_FRONT                           # 15, front of the keys
Y_KB1 = Y_KB0 + KB_D                                  # 176.5
BAY_D = 121.5            # electronics bay behind the keybed (emulator 86 deep, 34 free behind it)
Y_REAR_IN = Y_KB1 + BAY_D                             # 298
D = Y_REAR_IN + T_WALL                                # 310
Y_PANEL0 = Y_IN + GAP_PANEL                           # 14
Y_PANEL1 = Y_PANEL0 + PANEL_D                         # 244
Y_FILL0 = Y_PANEL1 + GAP_PANEL                        # 246
Y_STRIP0 = Y_KB1 - STRIP_OVERLAP                      # 161.5

# ---------------------------------------------------------------- layout in z
Z_BASE = T_BASE                                       # 9, top of the base
Z_KB = Z_BASE + T_RISER                               # 29, keybed mounting plane
Z_TOP = Z_KB + KB_LIP - LIP_ABOVE_WALL                # 67, top of all outer walls
WALL_H = Z_TOP - Z_BASE                               # 58
Z_PANEL0 = Z_TOP - PANEL_T                            # 65.4, underside of the panel
Z_STRIP = round(Z_KB + KB_BLACK + STRIP_ABOVE_BLACK)  # 90, top of the strip
Z_STRIP0 = Z_STRIP - T_STRIP                          # 81
H_TOTAL = Z_STRIP                                     # 90 without feet (no lid since Rev0.4)

# ---------------------------------------------------------------- CNC joints
# All wooden parts are cut on a CNC router and plugged together (glued):
# finger joints at the wall corners, tabs into notches along the base,
# tabs through slots for the cheeks, the filler and the strip cleats.
FIT = 0.15               # play per joint: notches and slots this much wider than the tab
DOG_R = 3.2              # dogbone radius in inside corners, end mills up to 6.35 mm
N_FINGER = 5             # fingers over the wall height (58 mm -> 11.6 mm each)
TAB_W = 40.0             # tabs of the walls into the base
CHEEK_TAB_V = (12.0, 38.0)   # cheek tabs through the front/rear wall, height above the base
CLEAT_TAB_W = 25.0
FILLER_TAB_W = 24.0

# ---------------------------------------------------------------- cheeks
CHEEK_KNEE_R = 200.0     # large radius where the slope meets the flat top
CABLE_NOTCH = (178.0, 278.0, 30.0)   # left cheek: y from/to (cheek coords), height
CABLE_NOTCH_R = 8.0

# ---------------------------------------------------------------- strip, cleats, apron, filler
CLEAT_W, CLEAT_H = 15.0, 12.0        # strip cleats on the cheeks
Y_CLEAT0, Y_CLEAT1 = 180.0, Y_REAR_IN - T_APRON      # 180 .. 289
Z_APRON0 = Z_TOP - 10.0                              # apron reaches 10 mm below the wall top
STRIP_SCREW_Y = (195.0, 235.0, 275.0)
FCLEAT = 12.0                        # filler cleats 12 x 12

# ---------------------------------------------------------------- risers
# Keybed frame: two aluminium Z profiles 20 x 20 x 2 (as on the MS2600 clone).
# The keybed is screwed onto the top flanges from above (keys over the holes
# taken off), then the unit is screwed to the base from below. Top flange
# centred on the row of keybed holes, bottom flanges point inwards under the
# keybed (clear of the emulator behind it). Rivet nuts M4 in both flanges.
Z_FLANGE, Z_H, Z_T = 20.0, T_RISER, 2.0
RISER_X0, RISER_X1 = 210.0, 880.0
Z_BOTTOM_OFF = Z_FLANGE - Z_T                         # 18, bottom flange centre from the hole row

# ---------------------------------------------------------------- electronics (envelopes)
STANDOFF = 6.0           # board standoffs on the base
# Bus emulator Rev0.3 (160 x 86): KiCad x = 0 at the left cheek, KiCad y = 0 at the rear wall.
# Holes here in case direction (y from the keybed side): y = 86 - y_kicad. The Pico's USB goes
# to the rear plate through a panel-mount extension (Adafruit 3258); its plug lies over the board,
# the socket 15 in front of the rear edge, and the cable bends down behind the edge.
EMU_W, EMU_D = 160.0, 86.0
EMU_X0, EMU_Y0 = 206.0, 178.0
EMU_PARTS = 22.0         # tallest parts (Pico on long pin headers 15-20, TO-220 upright, plugs)
EMU_HOLES = [(5, 81), (155, 81), (5, 5), (155, 5), (118.11, 81), (96.52, 5)]
NT_W, NT_D = 126.0, 80.0
NT_X0, NT_Y0 = 376.0, 195.0
NT_PARTS = 36.0          # heat sinks SK104 35 mm
# Power supply Rev0.1 turned 180 deg about the centre of its place (Patrick 2026-11-13): connectors
# J2-J4 at the left edge towards the emulator, J1 (DC in) front right. Holes from KiCad (x right,
# y down from the top edge), turned into case direction (x from the left, y from the keybed side).
NT_ROT = 180
NT_HOLES_KICAD = [(3.81, 3.81), (121.92, 3.81), (3.81, 76.2), (121.92, 76.2)]
NT_HOLES = [(NT_W - x, y) if NT_ROT == 180 else (x, NT_D - y) for x, y in NT_HOLES_KICAD]
PCB_T = 1.6

# ---------------------------------------------------------------- rear plate (aluminium 2 mm, outside)
PLATE_L, PLATE_H = 251.0, 40.0
PLATE_X_RIGHT = 460.0    # case x of the plate's left end seen from the rear
PLATE_Z0 = Z_BASE + 5.0  # 14
PLATE_R = 3.0
WINDOW = (12.0, 239.0, 26.0, 5.0)    # plate coords u0, u1, height (centred), corner radius
PLATE_SCREWS = [(6.0, 6.0), (245.0, 6.0), (6.0, 34.0), (245.0, 34.0)]
PLATE_SCREW_D, PLATE_SCREW_CSK = 3.5, 7.0
# u along the plate seen from the rear, v from the lower edge.
# The USB panel-mount socket sits at the left end, behind the power supply board;
# behind the emulator 34 mm depth are free.
# Hole sizes are placeholders until the parts are chosen (see README).
PLATE_ITEMS = [
    # u,    v,   label top,     label bottom, holes [(du, dv, d)]
    (26.0,  20.0, "USB",        "",          [(-8.65, 0, 3.2), (8.65, 0, 3.2)]),   # Adafruit 3258, cut-out below
    (54.0,  20.0, "DC IN",      "12-24 V",   [(0, 0, 11.0)]),
    (78.0,  20.0, "POWER",      "OFF",       [(0, 0, 6.5)]),
    (102.0, 20.0, "SUPPLY 2600", "INT",      [(0, 0, 6.5)]),
    (141.0, 20.0, "MIDI IN",    "",          [(0, 0, 16.0), (-12.5, 0, 3.2), (12.5, 0, 3.2)]),
    (181.0, 20.0, "MIDI OUT",   "",          [(0, 0, 16.0), (-12.5, 0, 3.2), (12.5, 0, 3.2)]),
    (221.0, 20.0, "MIDI THRU",  "",          [(0, 0, 16.0), (-12.5, 0, 3.2), (12.5, 0, 3.2)]),
]
PLATE_TEXT_H = 2.5
# rounded cut-outs (u, v, width, height, radius): Micro-B socket of the panel-mount cable
# Adafruit 3258 between its two M3 screws 17.3 apart (size not in the data: placeholder, check on the part)
PLATE_CUTOUTS = [(26.0, 20.0, 10.0, 6.0, 1.5)]

# ---------------------------------------------------------------- base holes
FEET = [(40.0, 40.0), (W / 2, 40.0), (W - 40.0, 40.0),
        (40.0, D - 40.0), (W / 2, D - 40.0), (W - 40.0, D - 40.0)]
FOOT_D, FOOT_H = 25.0, 12.0
SCREW_PITCH = 140.0      # assembly screws from below into walls and cheeks
