# -*- coding: utf-8 -*-
"""Which board files of the ARP 3620 project the fit check uses (read only)."""
from pathlib import Path

ARP = Path('/Users/patrickjoricke/Claude/code/Arp3620')
BOARDS = {
    'board': ARP / 'board' / 'ARP3620_Rev0.5.kicad_pcb',
    'panel': ARP / 'frontplatte_pcb' / 'ARP3620_Front_Rev0.3.kicad_pcb',
    'emu': ARP / 'emulator' / 'Emulator3620_Rev0.2.kicad_pcb',
    'psu': ARP / 'netzteil' / 'Netzteil3620_Rev0.1.kicad_pcb',
}
