# Native skin package v1

Proposed extension: .rskin (ZIP containing skin.json and raster assets). This is our format, not a claim of Winamp compatibility.

Example skin.json:
```json
{
  "schema_version": 1,
  "id": "example.original.dark",
  "name": "Original Dark",
  "author": "Example",
  "panels": {
    "player": {"background": "assets/player.png"},
    "playlist": {"background": "assets/playlist.png"},
    "equalizer": {"background": "assets/eq.png"}
  },
  "palette": {"text": "#E6E6E6", "background": "#151515"},
  "scale_mode": "pixel_nearest",
  "fallback": "built-in"
}
```

Renderer determines control geometry and semantic actions from trusted app components; skins cannot declare arbitrary code or change transport permissions. Later manifest versions may support per-element sprite rectangles and constrained anchor/layout tokens. Keep the schema backwards compatible.

Validate: canonical relative paths only; no symlinks/path traversal; bounded compressed and uncompressed sizes, entry count, image pixel area and decompression ratio; reject executable scripts and external URLs; unique normalized paths; no remote fetch; safe atomic install; preview sandbox; user-controlled reset. Never run MAKI scripts from imported WAL. Preserve color contrast and semantic fallback in accessible mode.

WSZ adapter: parse classic ZIP/BMP resources including main.bmp, titlebar.bmp, cbuttons.bmp, shufrep.bmp, volume.bmp, balance.bmp, posbar.bmp, numbers.bmp, text.bmp, eqmain.bmp, pledit.bmp, pledit.txt, viscolor.txt where available. Sprite geometry follows researched classic conventions; validate per image and distinguish missing optional resources from invalid archives.
