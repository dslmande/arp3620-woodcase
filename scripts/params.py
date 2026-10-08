# -*- coding: utf-8 -*-
"""All dimensions of the ARP 3620 wooden case, in mm.

Coordinate system (whole case):
  x  left -> right, 0 = outer face of the left wall
  y  front -> rear, 0 = outer face of the front wall
  z  up, 0 = underside of the base (feet are below z = 0)
"""

REV = "Rev0.1"
NAME = "ARP3620_Woodcase_" + REV

# ---------------------------------------------------------------- material
T_WALL = 12.0        # birch plywood: front, rear and end walls, cheeks
T_BASE = 9.0         # base
T_CHEEK = 12.0       # keyboard cheeks
T_STRIP = 9.0        # raised strip behind the keys (removable)
T_APRON = 9.0        # apron under the rear edge of the strip
T_FILL = 9.0         # filler behind the control panel
T_RISER = 12.0       # keybed risers
T_LID_WALL = 9.0
T_LID_TOP = 6.0
T_PLATE = 2.0        # aluminium rear plate
TOLEX = 1.0          # allowance for tolex plus glue on every covered face
DENSITY_PLY = 0.68e-3    # g/mm^3, birch plywood
DENSITY_ALU = 2.70e-3

# ---------------------------------------------------------------- keybed
# Fatar TP/9S, 49 keys, datasheet Rev. 0.6, p. 3-4
KB_W = 683.0
KB_D = 161.5
KB_WHITE = 47.5          # mounting plane -> top of white keys
KB_BLACK = 57.77         # mounting plane -> top of black keys
KB_LIP = 39.0            # mounting plane -> lower edge of the white key front
                         # (scaled from Fig. 2, check on the real keybed)
KB_TRAVEL = 10.0
KB_REAR_FRAME = 24.0     # rear frame behind the keys (Fig. 2)
KB_BLACK_Y = (50.0, 136.0)   # black keys, measured from the front edge of the keys
KB_HOLE_D = 4.5
KB_HOLE_X = (20.65, 157.72, 322.61, 502.20, 667.40)   # from the left edge
KB_HOLE_Y = (71.5, 147.0)                             # from the front edge

# ---------------------------------------------------------------- control panel
PANEL_W, PANEL_D = 170.0, 230.0      # x, y (panel y runs from its front edge)
PANEL_HOLES = [(12.5, 12.5), (157.5, 12.5), (12.5, 217.5), (157.5, 217.5)]
PANEL_HOLE_D = 3.2
BOARD_SPACER = 12.0                  # panel -> 3620 board (clone, check with the parts)
BOARD_PARTS_BELOW = 25.0             # parts plus KK plugs under the 3620 board (estimate)

# ---------------------------------------------------------------- clearances
GAP_PANEL = 2.0          # panel -> wood, each side, includes tolex
GAP_KB_SIDE = 3.0        # keybed -> cheek, each side, includes tolex
GAP_KB_FRONT = 3.0       # key fronts -> front wall
STRIP_OVERLAP = 15.0     # strip reaches this far over the rear frame of the keybed
LIP_ABOVE_WALL = 1.0     # lower edge of the key front sits this much above the wall top
STRIP_ABOVE_BLACK = 3.2  # strip top above the black keys
LID_INSIDE = 30.0        # clear height in the lid above the wall top

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
BAY_D = 121.5            # electronics bay behind the keybed (emulator is 110 deep)
Y_REAR_IN = Y_KB1 + BAY_D                             # 298
D = Y_REAR_IN + T_WALL                                # 310
Y_PANEL0 = Y_IN + GAP_PANEL                           # 14
Y_PANEL1 = Y_PANEL0 + PANEL_D                         # 244
Y_FILL0 = Y_PANEL1 + GAP_PANEL                        # 246
Y_STRIP0 = Y_KB1 - STRIP_OVERLAP                      # 161.5

# ---------------------------------------------------------------- layout in z
Z_BASE = T_BASE                                       # 9, top of the base
Z_KB = Z_BASE + T_RISER                               # 21, keybed mounting plane
Z_TOP = Z_KB + KB_LIP - LIP_ABOVE_WALL                # 59, top of all outer walls
WALL_H = Z_TOP - Z_BASE                               # 50
Z_PANEL0 = Z_TOP - 2.0                                # 57, underside of the panel
Z_STRIP = round(Z_KB + KB_BLACK + STRIP_ABOVE_BLACK)  # 82, top of the strip
Z_STRIP0 = Z_STRIP - T_STRIP                          # 73
Z_LID0 = Z_TOP                                        # lid sits on the walls
Z_LID1 = Z_TOP + LID_INSIDE                           # 89, underside of the lid top
H_LID = LID_INSIDE + T_LID_TOP                        # 36
H_TOTAL = Z_LID1 + T_LID_TOP                          # 95 without feet

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
RISER_W = 30.0
RISER_X0, RISER_X1 = 210.0, 880.0

# ---------------------------------------------------------------- electronics (envelopes)
STANDOFF = 6.0           # board standoffs on the base
EMU_W, EMU_D = 160.0, 110.0
EMU_X0, EMU_Y0 = 206.0, 178.0
EMU_PARTS = 22.0         # tallest parts (TO-220 upright, plugs)
EMU_HOLES = [(5, 5), (99.6, 5), (155, 5), (5, 105), (99.6, 105), (155, 105)]
NT_W, NT_D = 126.0, 80.0
NT_X0, NT_Y0 = 376.0, 195.0
NT_PARTS = 36.0          # heat sinks SK104 35 mm
NT_HOLES = [(3.81, 3.81), (121.92, 3.81), (3.81, 76.2), (121.92, 76.2)]
PCB_T = 1.6

# ---------------------------------------------------------------- rear plate (aluminium 2 mm, outside)
PLATE_L, PLATE_H = 211.0, 40.0
PLATE_X_RIGHT = 460.0    # case x of the plate's left end seen from the rear
PLATE_Z0 = Z_BASE + 5.0  # 14
PLATE_R = 3.0
WINDOW = (12.0, 199.0, 26.0, 5.0)    # plate coords u0, u1, height (centred), corner radius
PLATE_SCREWS = [(6.0, 6.0), (205.0, 6.0), (6.0, 34.0), (205.0, 34.0)]
PLATE_SCREW_D, PLATE_SCREW_CSK = 3.5, 7.0
# u along the plate seen from the rear, v from the lower edge.
# Deep parts (USB) sit at the left end, behind the power supply board;
# behind the emulator only parts up to 25 mm deep fit.
# Hole sizes are placeholders until the parts are chosen (see README).
PLATE_ITEMS = [
    # u,    v,   label top,     label bottom, holes [(du, dv, d)]
    (26.0,  20.0, "USB",        "(option)",  [(0, 0, 24.0), (-9.5, 12.0, 3.2), (9.5, -12.0, 3.2)]),
    (54.0,  20.0, "DC IN",      "12-24 V",   [(0, 0, 11.0)]),
    (78.0,  20.0, "POWER",      "OFF",       [(0, 0, 6.5)]),
    (102.0, 20.0, "SUPPLY 2600", "INT",      [(0, 0, 6.5)]),
    (141.0, 20.0, "MIDI IN",    "",          [(0, 0, 16.0), (-12.5, 0, 3.2), (12.5, 0, 3.2)]),
    (181.0, 20.0, "MIDI OUT",   "",          [(0, 0, 16.0), (-12.5, 0, 3.2), (12.5, 0, 3.2)]),
]
PLATE_TEXT_H = 2.5

# ---------------------------------------------------------------- base holes
FEET = [(40.0, 40.0), (W / 2, 40.0), (W - 40.0, 40.0),
        (40.0, D - 40.0), (W / 2, D - 40.0), (W - 40.0, D - 40.0)]
FOOT_D, FOOT_H = 25.0, 12.0
SCREW_PITCH = 140.0      # assembly screws from below into walls and cheeks

# ---------------------------------------------------------------- lid hardware
LATCH_FRONT_X = (150.0, W - 150.0)
LATCH_REAR_X = (150.0, W - 150.0)
LATCH = (40.0, 12.0, 50.0)   # width, depth, height (envelope, half on the lid, half on the case)
