# KD-55X80K pre-build community project survey — 2026-10-31
No verified flashable custom ROM for the exact KD-55X80K was found in the scoped public search. Absence in search is not proof none exists.

## Reuse ranking
1. CleanYourTV: https://github.com/Gathin23/cleanyourtv — BRAVIA_VH21 platform examples including KD-65X85K, XR-75X91K. Launcher and debloat only; packages differ by region and firmware.
2. tv-launcher: https://github.com/yurchornyi/tv-launcher — device examples and Android TV HOME behavior; no replacement boot image.
3. sony-bravia-launcher: https://github.com/udeshvirk/sony-bravia-launcher — tested KD-55X80J (VH2), Android TV 12; useful UI/CEC practices, not ROM hardware support.
4. Sony OSS: https://oss.sony.net/Products/Linux/TV/category02.html — manufacturer source family explicitly covers KD-55X80K; match source release to installed build before deriving drivers.

## Engineering decisions
- Reuse only well-understood open licensed app components and test fixtures; separately review licenses.
- Do not flash any VH21 sibling ROM or generic system image on KD-55X80K.
- Investigate the exact KD-55X80K board, bootloader, partitions, signing and recovery before ROM feasibility claims.
- Next: map Sony source archives to on-device kernel version; inspect repo's existing BRAVIA_VH21 data for reusable capability tests; compare model-specific I/O and boot metadata.
- Status: research index committed, no actual hardware tests or ROM flashing conducted.
