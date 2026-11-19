# -*- coding: utf-8 -*-
"""Which board files of the ARP 3620 project the fit check uses (read only)."""
from pathlib import Path

ARP = Path('/Users/patrickjoricke/Claude/code/Arp3620')
BOARDS = {
    'board': ARP / 'board' / 'ARP3620_Rev0.5.kicad_pcb',
    'panel': ARP / 'frontplatte_pcb' / 'ARP3620_Front_Rev0.3.kicad_pcb',
    'emu': ARP / 'emulator' / 'Emulator3620_Rev0.3.kicad_pcb',             # released 19.11.2026
    # Rev0.2 is still being routed in the power supply session's worktree (claude/jovial-germain-16ab9b),
    # not committed yet: switch to ARP / 'netzteil' once it is on main
    'psu': ARP / '.claude' / 'worktrees' / 'jovial-germain-16ab9b' / 'netzteil' / 'Netzteil3620_Rev0.2.kicad_pcb',
}
