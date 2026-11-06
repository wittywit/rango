# Rango code and file index

Quick map for editing. Current-state rules live in CLAUDE.md; history in BUILDLOG.md.

## Files
| Path | Role | Edit? |
|---|---|---|
| `index.html`, `style.css`, `appmanifest.json`, `workermain.js` | loader, page style, PWA manifest, worker bootstrap | rarely |
| `scripts/c3runtime.js`, `scripts/main.js` | Construct 3 engine and loader | never |
| `data.json` | whole game: objects, layouts, event sheets, audio list | yes (only gameplay surface) |
| `sw.js`, `offline.json` | service worker and its cache manifest (bump `offline.json` version after any edit) | version only |
| `images/*.webp` | sprite sheets. `shared-0-sheet14.webp` (1024x2048) holds Level_ drops and HUD arrow art | via `tools/bubble.py` |
| `media/` | about 45 webm audio files | no |
| `tools/bubble.py` | Pillow/numpy generator for the Selectlevel drop frames | run from repo root |
| `data.orig.json`, `data.prem.json`, `data.previs.json` | backups: original, before HUD resize, before visible touch buttons (last two gitignored) | no |

## data.json (`{"project":[...]}`)
- `[3]` object types (230). `[5]` layouts. `[6]` event sheets (`eGame`, `eMenu`, `eLevel`). `[7]` audio, `[8]` media folder.
- Layout: layers at `L[11]`, instances at `layer[14]`. Instance = `[[x,y,z,w,h,angle,...], typeIdx, uid, ...]`. `inst[5][0]` is the initially-visible flag.
- Event: `[0,0,false,null,id,sid,[conditions],[actions],[subevents]]`. Platform simulated-control actions look like `[3,64,"Platform",...]`.
- Edit with `python3 -I` json load/modify/dump, compact separators (`(',',':')`, `ensure_ascii=False`), backup first.

## Object type indices (position in `[3]`)
- `Keyboard` 4, `Touch` 24, `HUD_left/right/jump` 34/35/36, `Level_bg` 62, `Level_` 63 (23 instances), `Lev_num` 65, `TobeDeleted` 224 (removed from Selectlevel).
- `Dude` (player) has Platform behavior id 454753445950263.

## Layouts
- Levels "1" to "24" (24000 or 36000 wide, 1080 high), extras `night02`, `B2`, `bw1`, `bw02`, `Pink01`, `Temp_01`, `temp03`. `Menu` and `Selectlevel` are 1920 wide.
- Layers usually: Sound effects, Background, Particles, Ground/Game/Dude, Leaf layer, HUD, Popup, Touchcontrols. HUD and Touchcontrols have parallax 0,0 (screen-fixed).

## HUD and mobile
- HUD_music/sound/home: 100px at y=70, x 1620/1735/1850 in every level layout.
- Touch buttons: 320px hit boxes, now visible, bottom corners (left+right bottom-left, jump bottom-right). Driven by Touch "is touching object" events.
- Viewport 1920x1080, letterboxed on other aspect ratios.

## Globals
- eGame: `Gem`, `Playerhealth` (3), `State`, `Sound`, `Music`. eLevel: `Level`.
- eGame has about 72 top-level events shared by all levels, plus keyboard handlers that look like debug or cheats (unverified).

## Gotchas
- The C3 runtime runs in a worker, so `c3_runtimeInterface` is not reachable from page JS.
- Serve over HTTP (python3 -m http.server 8765). Opening via `file:` shows an alert.
- Stale cache after edits: bump `offline.json`, unregister service workers, delete caches, `fetch(url,{cache:'reload'})` each edited file, reload.
- Synthetic Chrome-MCP keys and clicks never move Dude. Test controls on a real phone or DevTools touch emulation.
- Chrome MCP: `browser_batch` actions use `{"name":"computer","input":{...,"tabId":...}}`; no hold_key (use key with `repeat`).

## Open items
Selectlevel drops small and crowded on phones, no portrait rotate prompt, no safe-area margins, levels 2 to 24 and extra layouts unplayed.
