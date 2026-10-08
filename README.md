# ARP 3620 replica — wooden case

Wooden enclosure for a DIY replica of the **ARP 3620** duophonic keyboard (the
keyboard of the ARP 2600P), built around a current **Fatar TP/9S 49-key** keybed
instead of the original ARP key mechanism.

**Status: in design.** No manufacturing files yet — this repository starts with
the design basis below. Drawings, cut list and 3D model follow here.

## Design basis

| | Value | Source |
|---|---|---|
| Keybed | Fatar TP/9S, 49 keys: 683 × 161.5 mm, 47.5 mm frame, 57.77 mm over the keys | Fatar datasheet TP/9S Rev. 0.6, p. 3 |
| Keybed mounting | 10 × Ø 4.5 mm, 5 columns × 2 rows, rows 75.5 mm apart | Fatar datasheet, p. 3–4 |
| Control panel | 170 × 230 mm aluminium, 4 corner holes, left of the keybed | panel layout of the 2014 clone |
| Layout | flat case, panel on the left, keybed on the right, strip behind the keys, optional lid | 2014 clone (see below) |

Parts that go inside the case: the 3620 electronics board behind the panel, a bus
emulator board (controller that scans the keybed), a power supply board, two DIN
jacks for MIDI In/Out, a DC jack 5.5/2.1 mm, a power switch and a toggle switch
for supply from the ARP 2600 or the internal supply. The connection to the
2600 is a 6-pin GX16 socket on the control panel.

### Reference: the 2014 clone

The DIY clone from 2014 (Muffwiggler group buy) used a black MDF case,
915 × 257 mm, with a lid. Its drawings were made for a Kimber Allen keybed and
are **not part of this repository** — they are third-party work and stay with
their author. They are attached to the project page in the wiki:
[ARP 3620 Keyboard Clone](https://diysynth.wiki.dsl-man.de/wiki/spaces/DSO/pages/1146915).
This design only takes the overall concept from them; all dimensions here are
derived anew from the Fatar keybed and the panel.

## License

© 2026 Dsl-man.de

Licensed under [Creative Commons Attribution-ShareAlike 4.0 International](LICENSE)
(CC BY-SA 4.0), including any generator scripts. You may build, modify and
redistribute this design, commercially too, as long as you credit the source and
share your changes under the same license.

Not covered by this license: third-party documents referred to above (the 2014
case drawings, the Fatar datasheet), which keep their own rights.

ARP and ARP 3620 are names of ARP Instruments, Inc. This is an independent
DIY project, not affiliated with or endorsed by ARP or its successors.
