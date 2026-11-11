# -*- coding: utf-8 -*-
"""German texts for the drawing (drawing.py writes it in English and German).

DATA: exact strings. TEMPLATES: English with %s for every value (%d: digits
only), German with {0}, {1} ... in any order. Values are translated again, so
'%s  -  %s x' takes the part name from DATA. A text missing here stays English
and is listed when the drawing is made."""

DATA = {
    'CC BY-SA 4.0  (c) 2026 Dsl-man.de  -  github.com/dslmande/arp3620-woodcase':
        'CC BY-SA 4.0  (c) 2026 Dsl-man.de  -  github.com/dslmande/arp3620-woodcase',
    # title block, sheets
    'ARP 3620 replica - wooden case': 'ARP 3620 Nachbau – Holzgehäuse',
    'renders not to scale': 'Bilder ohne Maßstab',
    'detail 1:1, renders not to scale': 'Detail 1:1, Bilder o. M.',
    'Overview': 'Übersicht',
    'General arrangement': 'Gesamtansicht',
    'Sections': 'Schnitte',
    'Base': 'Boden',
    'Walls': 'Wände',
    'Cheeks': 'Wangen',
    'Strip, cleats, filler, Z profiles': 'Leiste, Träger, Füllbrett, Z-Profile',
    'Lid': 'Deckel',
    'Rear plate': 'Rückplatte',
    'Joints, CNC, assembly order': 'Verbindungen, CNC, Montagereihenfolge',
    'Cut list, hardware, assembly': 'Zuschnittliste, Beschläge, Montage',
    # overview
    'Key data': 'Eckdaten',
    'CNC-cut, plugged together: finger joints, tabs and slots, glued':
        'CNC-gefräst und gesteckt: Fingerzinken, Zapfen und Schlitze, verleimt',
    'Birch plywood 12 / 9 / 6 mm, covered in black tolex, lid with 4 latches':
        'Birke-Multiplex 12 / 9 / 6 mm, schwarz mit Tolex bezogen, Deckel mit 4 Verschlüssen',
    'Keybed Fatar TP/9S 49 on two aluminium Z profiles 20 x 20 x 2, control panel 170 x 230 flush with the walls':
        'Keybed Fatar TP/9S 49 auf zwei Alu-Z-Profilen 20 x 20 x 2, Frontplatte 170 x 230 bündig mit den Wänden',
    'Electronics bay under the removable strip: bus emulator 160 x 110, power supply 126 x 80':
        'Elektronikfach unter der abnehmbaren Leiste: Bus-Emulator 160 x 110, Netzteil 126 x 80',
    'Rear plate (aluminium 2 mm): USB (option), DC IN, POWER, SUPPLY 2600/INT, MIDI IN, MIDI OUT':
        'Rückplatte (Aluminium 2 mm): USB (Option), DC IN, POWER, SUPPLY 2600/INT, MIDI IN, MIDI OUT',
    'without lid': 'ohne Deckel',
    'with lid': 'mit Deckel',
    'rear: connector plate': 'hinten: Anschlussplatte',
    'strip lifted: electronics bay (emulator, power supply)': 'Leiste abgehoben: Elektronikfach (Emulator, Netzteil)',
    'plugged together: finger joints, tabs and slots (exploded)':
        'gesteckt: Fingerzinken, Zapfen und Schlitze (Explosionsansicht)',
    'front left corner, parts pulled apart': 'Ecke vorne links, Teile auseinandergezogen',
    # general arrangement
    'Top view, lid removed': 'Draufsicht, Deckel abgenommen',
    'control panel': 'Frontplatte',
    'filler': 'Füllbrett',
    'strip (removable)': 'Leiste (abnehmbar)',
    'keybed': 'Keybed',
    'bay': 'Fach',
    'Front view with lid': 'Vorderansicht mit Deckel',
    'Rear view, lid removed': 'Rückansicht, Deckel abgenommen',
    'Right side, with lid': 'Seitenansicht rechts, mit Deckel',
    # sections
    'Fatar TP/9S 49 (simplified)': 'Fatar TP/9S 49 (vereinfacht)',
    'Z profile 20 x 20 x 2': 'Z-Profil 20 x 20 x 2',
    'power supply (envelope)': 'Netzteil (Hüllkörper)',
    'strip 9 (removable)': 'Leiste 9 (abnehmbar)',
    'apron': 'Schürze',
    'rear plate + socket': 'Rückplatte + Buchse',
    'lid': 'Deckel',
    'rear wall (window)': 'Rückwand (Fenster)',
    '3620 board (envelope)': '3620-Board (Hüllkörper)',
    'standoff M3 (panel corner)': 'Abstandsbolzen M3 (Ecke Frontplatte)',
    # parts
    'Apron under the strip': 'Schürze unter der Leiste',
    'Cheek left': 'Wange links',
    'Cheek right': 'Wange rechts',
    'End wall left': 'Seitenwand links',
    'End wall right': 'Seitenwand rechts',
    'Filler behind the panel': 'Füllbrett hinter der Frontplatte',
    'Front wall': 'Vorderwand',
    'Keybed Z profile': 'Z-Profil Keybed',
    'Lid end': 'Deckel Seite',
    'Lid front/rear': 'Deckel vorn/hinten',
    'Lid top': 'Deckelplatte',
    'Rear wall': 'Rückwand',
    'Strip behind the keys': 'Leiste hinter den Tasten',
    'Strip cleat': 'Träger der Leiste',
    'birch plywood 12': 'Birke-Multiplex 12',
    'birch plywood 9': 'Birke-Multiplex 9',
    'birch plywood 6': 'Birke-Multiplex 6',
    'aluminium 2': 'Aluminium 2',
    'seen from above': 'von oben gesehen',
    'seen from below': 'von unten gesehen',
    'seen from the front': 'von vorn gesehen',
    'seen from the rear': 'von hinten gesehen',
    'seen from the right': 'von rechts gesehen',
    'seen from the left': 'von links gesehen',
    'black anodised, engraved white (or printed)': 'schwarz eloxiert, weiß graviert (oder gedruckt)',
    'black paint': 'schwarz lackiert',
    'black paint, glued into the strip': 'schwarz lackiert, in die Leiste geleimt',
    'tolex on both faces and the top edge': 'Tolex auf beiden Seiten und der Oberkante',
    'tolex on top and front edge': 'Tolex oben und an der Vorderkante',
    'tolex on top, front edge and ends': 'Tolex oben, an der Vorderkante und den Enden',
    'tolex outside': 'Tolex außen',
    'tolex outside and over the lower edge': 'Tolex außen und über die Unterkante',
    'tolex outside, over the top edge': 'Tolex außen, über die Oberkante',
    'tolex outside, over the top edge, 20 mm down the inside': 'Tolex außen, über die Oberkante, 20 mm innen herunter',
    'underside painted black, edges covered by the tolex of the walls':
        'Unterseite schwarz lackiert, Kanten vom Tolex der Wände bedeckt',
    # hole notes
    'Z profile M4 x 12': 'Z-Profil M4 x 12',
    '10 x pan head screw M4 x 10 with washer, 10 x rivet nut M4 in the top flanges':
        '10 x Linsenkopfschraube M4 x 10 mit Scheibe, 10 x Einnietmutter M4 in den oberen Schenkeln',
    'panel standoff M3': 'Bolzen Frontplatte M3',
    'emulator standoff M3': 'Bolzen Emulator M3',
    'power supply standoff M3': 'Bolzen Netzteil M3',
    'foot': 'Fuß',
    'rear plate, screw 3.5 x 16': 'Rückplatte, Schraube 3.5 x 16',
    'screw 3.5 x 20 into cleat': 'Schraube 3.5 x 20 in den Träger',
    'keybed screw': 'Keybed-Schraube',
    'screw 3.5 x 16': 'Schraube 3.5 x 16',
    # base, walls, cheeks
    'seen from above (inside). Countersinks: dashed = on the underside. Coordinates x/y from the front left corner.':
        'von oben (innen) gesehen. Senkungen: gestrichelt = auf der Unterseite. Koordinaten x/y ab der Ecke vorne links.',
    'Seen from outside. Fingers at both ends, tabs into the base, slot for the left cheek. '
    'The right end takes end wall and right cheek together (24 deep).':
        'Von außen gesehen. Zinken an beiden Enden, Zapfen in den Boden, Schlitz für die linke Wange. '
        'Das rechte Ende nimmt Seitenwand und rechte Wange zusammen auf (24 tief).',
    'Seen from inside. Notches in the top edge for the filler tabs, slot for the left cheek, '
    'window for the bodies of the rear plate parts.':
        'Von innen gesehen. Kerben in der Oberkante für die Zapfen des Füllbretts, Schlitz für die linke Wange, '
        'Fenster für die Bauteile der Rückplatte.',
    'End walls seen from the right. Fingers at both ends (bottom, middle and top finger belong to the '
    'end wall), tabs into the base;':
        'Seitenwände von rechts gesehen. Zinken an beiden Enden (unterer, mittlerer und oberer Zinken gehören '
        'zur Seitenwand), Zapfen in den Boden;',
    'the left end wall has a notch in its top edge for the filler tab. Heights: 0 = top of the base, '
    'the tabs reach 9 below it.':
        'die linke Seitenwand hat oben eine Kerbe für den Zapfen des Füllbretts. Höhen: 0 = Oberseite Boden, '
        'die Zapfen reichen 9 darunter.',
    'Seen from the right. u = 0 at the inner face of the front wall,':
        'Von rechts gesehen. u = 0 an der Innenseite der Vorderwand,',
    'v = 0 at the top of the base; the tabs reach 9 below it.':
        'v = 0 an der Oberseite des Bodens; die Zapfen reichen 9 darunter.',
    'Two slots for the strip cleats. Tolex on both faces and the top edge.':
        'Zwei Schlitze für die Träger der Leiste. Tolex auf beiden Seiten und der Oberkante.',
    'Tabs: front and rear through the walls, down through the base.':
        'Zapfen: vorn und hinten durch die Wände, unten durch den Boden.',
    'Slot at the rear for the filler tab.': 'Schlitz hinten für den Zapfen des Füllbretts.',
    'from the electronics bay to the panel section.': 'vom Elektronikfach zum Teil mit der Frontplatte.',
    'Stands against the right end wall and shares its joints:':
        'Steht an der rechten Seitenwand und teilt deren Verbindungen:',
    'same fingers into the front/rear wall, same tabs into the base.':
        'gleiche Zinken in Vorder- und Rückwand, gleiche Zapfen in den Boden.',
    # strip, risers, cleats, filler
    'seen from above; notches at the rear edge for the apron; screws into the cleats, countersunk on top (black screws)':
        'von oben gesehen; Kerben an der Hinterkante für die Schürze; Schrauben in die Träger, oben versenkt '
        '(schwarze Schrauben)',
    'tabs up into the strip notches, glued; reaches 10 mm below the wall top':
        'Zapfen nach oben in die Kerben der Leiste, verleimt; reicht 10 mm unter die Wandoberkante',
    'top flanges centred under the rows of keybed holes, bottom flanges point inwards; rivet nuts M4 in both flanges':
        'obere Schenkel mittig unter den Lochreihen des Keybeds, untere Schenkel zeigen nach innen; '
        'Einnietmuttern M4 in beiden Schenkeln',
    'keybed screwed onto the profiles from above, then the unit screwed to the base from below':
        'Keybed von oben auf die Profile schrauben, dann die Einheit von unten mit dem Boden verschrauben',
    'lying flat, tabs through the cheek;': 'liegend, Zapfen durch die Wange;',
    'tabs into the left end wall, the rear wall and through the left cheek;':
        'Zapfen in die linke Seitenwand, die Rückwand und durch die linke Wange;',
    'flush with the wall top': 'bündig mit der Wandoberkante',
    # lid
    'Finger joints at the corners (the ends own the lower and the upper finger),':
        'Fingerzinken an den Ecken (unterer und oberer Zinken an den Seitenteilen),',
    'the wall tabs go into notches in the top. Glue; tolex outside and around the lower edge.':
        'die Zapfen der Wände sitzen in Kerben der Deckelplatte. Verleimen; Tolex außen und um die Unterkante.',
    'The lid sits on the case walls, flush outside. 4 latches centred on the joint (2 front, 2 rear)':
        'Der Deckel sitzt außen bündig auf den Gehäusewänden. 4 Verschlüsse mittig über der Fuge (2 vorn, 2 hinten)',
    'keep it in place; the latches also locate it sideways.': 'halten ihn und führen ihn auch seitlich.',
    # rear plate
    'Aluminium 2 mm, black anodised, legend engraved or printed white.':
        'Aluminium 2 mm, schwarz eloxiert, Beschriftung weiß graviert oder gedruckt.',
    'Seen from outside (from the rear of the case).': 'Von außen gesehen (von hinten auf das Gehäuse).',
    'Mounted on the outside of the rear wall, over the tolex,': 'Außen auf die Rückwand montiert, über dem Tolex,',
    'with 4 countersunk screws 3.5 x 16 (pilot holes in the rear wall).':
        'mit 4 Senkschrauben 3.5 x 16 (Vorbohrungen in der Rückwand).',
    'The window in the rear wall takes the bodies of the parts.':
        'Das Fenster in der Rückwand nimmt die Bauteilkörper auf.',
    'Behind the emulator only 25 mm depth is free; the deep USB':
        'Hinter dem Emulator sind nur 25 mm Tiefe frei; die tiefe USB-',
    'extension sits at the left end, behind the power supply.':
        'Verlängerung sitzt am linken Ende hinter dem Netzteil.',
    'Hole sizes are placeholders until the parts are chosen.':
        'Lochgrößen sind Platzhalter, bis die Bauteile gewählt sind.',
    # lists
    'Cut list (finished sizes, mm)': 'Zuschnittliste (Fertigmaße, mm)',
    'part': 'Teil', 'qty': 'Anz.', 'material': 'Material', 'length': 'Länge', 'width': 'Breite',
    'covering / finish': 'Bezug / Oberfläche',
    'Hardware': 'Beschläge',
    'outside, see covering notes': 'außen, siehe Hinweise zum Bezug',
    'contact cement for tolex, wood glue (PVAc), wood filler': 'Kontaktkleber für Tolex, Holzleim (PVAc), Holzspachtel',
    'all joints glued; filler for dogbones and joint lines under the tolex':
        'alle Verbindungen verleimt; Spachtel für Dogbones und Fugen unter dem Tolex',
    'base -> Z profiles (from below)': 'Boden -> Z-Profile (von unten)',
    'keybed frame (not CNC)': 'Keybed-Rahmen (nicht CNC)',
    'keybed -> Z profiles, from above through the keybed holes (take the keys over the holes off)':
        'Keybed -> Z-Profile, von oben durch die Keybed-Löcher (Tasten über den Löchern abnehmen)',
    '6 x countersunk wood screw 3.5 x 20, black': '6 x Senkkopf-Holzschraube 3.5 x 20, schwarz',
    'strip -> cleats (removable strip)': 'Leiste -> Träger (Leiste abnehmbar)',
    '4 x countersunk screw 3.5 x 16, black': '4 x Senkschraube 3.5 x 16, schwarz',
    'rear plate': 'Rückplatte',

    'length ~ 21 mm + thread in the keybed foot; type to be confirmed on the keybed (hole 4.5)':
        'Länge ~ 21 mm + Gewinde im Keybed-Fuß; Typ am Keybed prüfen (Loch 4.5)',
    'emulator (6), power supply (4)': 'Emulator (6), Netzteil (4)',
    '4 x draw latch (case latch), small, ~40 mm wide': '4 x Kistenverschluss (Spannverschluss), klein, ~40 mm breit',
    'lid: 2 front, 2 rear, centre on the lid joint': 'Deckel: 2 vorn, 2 hinten, mittig über der Deckelfuge',
    'rear plate parts: 2 x DIN 5-pin panel socket, DC jack 5.5/2.1, 2 x toggle switch, USB extension (option)':
        'Teile der Rückplatte: 2 x DIN-Buchse 5-polig, DC-Buchse 5.5/2.1, 2 x Kippschalter, USB-Verlängerung (Option)',
    'hole sizes on the plate are placeholders - confirm with the chosen parts':
        'Lochgrößen der Platte sind Platzhalter – mit den gewählten Teilen prüfen',
    'optional: 8 x case corner, carrying handle': 'optional: 8 x Kofferecke, Tragegriff',
    'Assembly': 'Montage',
    'CNC: cut all parts as per DXF, drill and countersink (CSK_BACK = countersink on the far face).':
        'CNC: alle Teile nach DXF fräsen, bohren und senken (CSK_BACK = Senkung auf der Rückseite).',
    'Screw the keybed onto the Z profiles first (keys over the holes off); fit the unit into the case dry.':
        'Zuerst das Keybed auf die Z-Profile schrauben (Tasten über den Löchern abnehmen); die Einheit trocken einpassen.',
    'Strip unit: apron tabs up into the strip, glued; the strip stays removable (screws into the cleats).':
        'Leiste: Zapfen der Schürze nach oben in die Leiste, verleimt; die Leiste bleibt abnehmbar '
        '(Schrauben in die Träger).',
    'Lid: front and rear onto the top, ends from the sides; glue.':
        'Deckel: vorn und hinten an die Deckelplatte, Seitenteile von der Seite; verleimen.',
    'Fill dogbones and joint lines on the outside, sand flush, round all outside edges to about R2.':
        'Dogbones und Fugen außen spachteln, bündig schleifen, alle Außenkanten auf etwa R2 runden.',
    'Paint the inside black, then tolex outside with contact cement; wrap 20 mm over the top edges.':
        'Innen schwarz lackieren, dann außen Tolex mit Kontaktkleber; 20 mm über die Oberkanten umschlagen.',
    'Rear plate, latches, feet; panel on its standoffs, electronics on the base, keybed unit screwed from below.':
        'Rückplatte, Verschlüsse, Füße; Frontplatte auf die Bolzen, Elektronik auf den Boden, Keybed-Einheit von '
        'unten verschrauben.',
    'Open points': 'Offene Punkte',
    'Sheet thickness: measure the plywood, enter it in params.py (T_*) and regenerate.':
        'Plattenstärke: Multiplex messen, in params.py (T_*) eintragen und neu erzeugen.',
    'Keybed screws: check length against the keys (foot hole 4.5).':
        'Keybed-Schrauben: Länge gegen die Tasten prüfen (Loch im Fuß 4.5).',
    'Rear plate parts and their hole sizes.': 'Teile der Rückplatte und ihre Lochgrößen.',
    'Latch type; optional handle and case corners.': 'Typ der Verschlüsse; optional Griff und Kofferecken.',
    # assembly order (parts.py)
    'base on the bench, inside up': 'Boden auf die Werkbank, Innenseite oben',
    'Z profiles (with the keybed on them): screw from below through the base':
        'Z-Profile (mit dem Keybed darauf): von unten durch den Boden verschrauben',
    'left cheek: tabs down into the slots of the base': 'linke Wange: Zapfen von oben in die Schlitze des Bodens',
    'right cheek: tabs down into the notches at the right edge of the base':
        'rechte Wange: Zapfen von oben in die Kerben am rechten Bodenrand',
    'strip cleats: from the inside through the cheeks': 'Träger der Leiste: von innen durch die Wangen',
    'filler: right tab into the left cheek, hold it level':
        'Füllbrett: rechten Zapfen in die linke Wange, waagerecht halten',
    'front wall: over the cheek tabs, tabs into the base': 'Vorderwand: über die Zapfen der Wangen, Zapfen in den Boden',
    'rear wall: over the cheek tabs and the filler tabs': 'Rückwand: über die Zapfen der Wangen und des Füllbretts',
    'end walls from the sides: fingers, base tabs, filler tab':
        'Seitenwände von der Seite: Zinken, Zapfen in den Boden, Zapfen des Füllbretts',
    # joints sheet
    'front wall, left end (seen from outside)': 'Vorderwand, linkes Ende (von außen gesehen)',
    'left end wall, front end (seen from inside)': 'linke Seitenwand, vorderes Ende (von innen gesehen)',
    '(split over both parts at the fingers). Joint depth = sheet thickness:':
        '(bei den Zinken auf beide Teile verteilt). Verbindungstiefe = Plattenstärke:',
    'measure the plywood and enter it before cutting (params.py, T_*).':
        'Multiplex messen und vor dem Fräsen eintragen (params.py, T_*).',
    'Tab ends sit flush with the outside, under the tolex.': 'Die Zapfenenden sitzen außen bündig unter dem Tolex.',
    'Joints in the 3D model: no part overlaps another, every joint touches,':
        'Geprüft im 3D-Modell: kein Teil überschneidet ein anderes, jede Fuge hat Kontakt,',
    'each part slides into place in the order below (model/check.txt).':
        'jedes Teil lässt sich in der Reihenfolge rechts einschieben (model/check.txt).',
    'Assembly order (carcass)': 'Montagereihenfolge (Korpus)',
    'down': 'nach unten', 'up': 'nach oben', 'to the right': 'nach rechts', 'to the left': 'nach links',
    'to the rear': 'nach hinten', 'to the front': 'nach vorn',
}

TEMPLATES = [
    ('sheet %s', 'Blatt {0}'),
    ('scale %s', 'Maßstab {0}'),
    ('ARP 3620 wooden case %s', 'ARP 3620 Holzgehäuse {0}'),
    ('%s  -  %s x', '{0}  -  {1} x'),
    ('%s mm, %s   [%s]', '{0} mm, {1}   [{2}]'),
    ('dia %s csk %s this face  (%s x)  %s', 'Ø {0}, Senkung {1} auf dieser Seite  ({2} x)  {3}'),
    ('dia %s csk %s far face  (%s x)  %s', 'Ø {0}, Senkung {1} auf der Rückseite  ({2} x)  {3}'),
    ('dia %s  (%s x)  %s', 'Ø {0}  ({1} x)  {2}'),
    ('pilot %s  (%s x)  %s', 'Vorbohrung {0}  ({1} x)  {2}'),
    ('- %s', '- {0}'),
    ('%d. %s', '{0}. {1}'),
    ('Outside: %s x %s mm, height %s (walls) / %s (strip) / %s with lid, plus feet %s',
     'Außen: {0} x {1} mm, Höhe {2} (Wände) / {3} (Leiste) / {4} mit Deckel, dazu Füße {5}'),
    ('Section A-A at x = %s (keyboard, power supply), seen from the right',
     'Schnitt A-A bei x = {0} (Tastatur, Netzteil), von rechts gesehen'),
    ('Section B-B at x = %s (control panel)', 'Schnitt B-B bei x = {0} (Frontplatte)'),
    ('control panel (PCB %s)', 'Frontplatte (Leiterplatte {0})'),
    ('Heights follow from the keybed: the lower edge of the white key fronts (%s above the mounting plane,',
     'Die Höhen folgen aus dem Keybed: Die Unterkante der weißen Tastenfronten ({0} über der Auflage,'),
    ('Fatar drawing 1:1, checked on the keybed) sits %s above the wall top. The keybed stands on Z profiles %s high -',
     'Fatar-Zeichnung 1:1, am Keybed geprüft) liegt {0} über der Wandoberkante. Das Keybed steht auf {1} hohen Z-Profilen –'),
    ('all heights follow from both (params.py: KB_LIP, T_RISER). Board spacer %s and %s for parts and plugs under the',
     'alle Höhen hängen daran (params.py: KB_LIP, T_RISER). Abstand Board–Frontplatte {0} und {1} für Bauteile und Stecker unter dem'),
    ('3620 board are estimates. Electronics are simplified boxes (parts height emulator %s, power supply %s).',
     '3620-Board sind Schätzwerte. Elektronik als vereinfachte Quader (Bauhöhe Emulator {0}, Netzteil {1}).'),
    ('window, corners R %s', 'Fenster, Ecken R {0}'),
    ('%s to the corner (rounded R %s)', '{0} bis zur Ecke (gerundet R {1})'),
    ('Slope from %s to %s high, blending into the', 'Schräge von {0} auf {1} Höhe, geht in die flache'),
    ('flat top with R %s (tangent points in the DXF).', 'Oberkante über, R {0} (Tangentenpunkte in der DXF).'),
    ('Cable notch %s x %s, corners R %s: cables', 'Kabelausschnitt {0} x {1}, Ecken R {2}: Kabel'),
    ('top %s below the strip top', 'Oberkante {0} unter der Leistenoberkante'),
    ('Walls %s mm, inside height %s above the case walls (%s clear above the strip).',
     'Wände {0} mm, innen {1} hoch über den Gehäusewänden ({2} frei über der Leiste).'),
    ('Seen from the rear, the plate starts %s from the left end of the case;',
     'Von hinten gesehen beginnt die Platte {0} vom linken Gehäuseende;'),
    ('its lower edge is %s above the underside of the base.', 'ihre Unterkante liegt {0} über der Unterseite des Bodens.'),
    ('net area: %s', 'Nettofläche: {0}'),
    ('%s mm: %s m2', '{0} mm: {1} m²'),
    ('Tolex, black (vinyl case covering), approx. %s m2 incl. 25 % waste',
     'Tolex schwarz (Vinyl-Kofferbezug), ca. {0} m² inkl. 25 % Verschnitt'),
    ('%s x countersunk wood screw 4 x 20', '{0} x Senkkopf-Holzschraube 4 x 20'),
    ('2 x aluminium Z profile 20 x 20 x 2, length %s', '2 x Alu-Z-Profil 20 x 20 x 2, Länge {0}'),
    ('%s x countersunk screw M4 x 12, %s x rivet nut M4 in the bottom flanges',
     '{0} x Senkkopfschraube M4 x 12, {1} x Einnietmutter M4 in den unteren Schenkeln'),
    ('Keybed frame: two aluminium Z profiles 20 x 20 x 2, length %s (bought, not CNC)',
     'Keybed-Rahmen: zwei Alu-Z-Profile 20 x 20 x 2, Länge {0} (Kaufteil, nicht CNC)'),
    ('4 x M3 standoff, total length %s mm (e.g. 40 + 8 and a washer)',
     '4 x Abstandsbolzen M3, Gesamtlänge {0} mm (z. B. 40 + 8 und eine Scheibe)'),
    ('panel corners (panel PCB %s), M3 x 12 countersunk from below, M3 x 6 black from the top',
     'Ecken der Frontplatte (Leiterplatte {0}), M3 x 12 Senkkopf von unten, M3 x 6 schwarz von oben'),
    ('10 x M3 standoff %s mm, 10 x M3 x 12 countersunk', '10 x Abstandsbolzen M3 {0} mm, 10 x M3 x 12 Senkkopf'),
    ('6 x rubber foot dia %s x %s with screw', '6 x Gummifuß Ø {0} x {1} mit Schraube'),
    ('Dry fit the whole case first (order on sheet %s), then take it apart and glue.',
     'Das ganze Gehäuse erst trocken stecken (Reihenfolge auf Blatt {0}), dann zerlegen und verleimen.'),
    ('KB_LIP %s (key front lower edge) scaled from the Fatar drawing - measure.',
     'KB_LIP {0} (Unterkante Tastenfront) aus der Fatar-Zeichnung abgegriffen – messen.'),
    ('Board spacer %s and parts height under the 3620 board.', 'Abstand Board {0} und Bauhöhe unter dem 3620-Board.'),
    ('Dogbones R %s in every inside corner (end mill up to 6.35 mm).',
     'Dogbones R {0} in jeder Innenecke (Fräser bis 6.35 mm).'),
    ('%s fingers over %s mm: bottom, middle and top finger on the end wall.',
     '{0} Zinken über {1} mm: unterer, mittlerer und oberer Zinken an der Seitenwand.'),
    ('Play per joint: notches and slots %s mm wider than the tab',
     'Spiel je Verbindung: Kerben und Schlitze {0} mm breiter als der Zapfen'),
]
