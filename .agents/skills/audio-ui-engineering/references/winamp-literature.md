# Winamp evidence and reuse matrix (accessed 2026-11-01)

- Winamp official desktop help, Skins/Classic/Modern, docking and per-skin controls: https://support.winamp.com/winamp-desktop-player-for-windows
- Classic skin component inventory, BMP sprites and fallback mechanics: https://winampskins.neocities.org/base
- Original classic skin forum component inventory: https://forums.winamp.com/forum/skinning-and-design/classic-skins/29331-how-can-i-make-my-own-skin/page4
- Modern Wasabi component and XML grouping architecture: https://forums.winamp.com/forum/skinning-and-design/modern-skins/78266-how-to-skin-components
- Open-source classic renderer implementation to study, not copy without license review: https://github.com/WalksWithASwagger/winamp
- NullPlayer modern skin guide (community material, inspect implementation/license before reuse): https://github.com/ad-repo/nullplayer
- Classic WSZ creator UX example: https://www.skinsforwinamp.com/

## Architecture decision
V1 original native modular skin packs with independently replaceable panel assets; v2 WSZ classic adapter; v3 optional limited XML declarative import. WAL/Wasabi/MAKI full compatibility not part of V1–V2. All referenced assets require independent rights verification before distribution.
