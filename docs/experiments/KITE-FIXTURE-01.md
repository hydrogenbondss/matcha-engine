# KITE-FIXTURE-01 — Frozen Kite production evidence fixture

This is not an experiment result. It records what the fixture at `fixtures/kite-production/` contains and where it came from.

## 1. Purpose

A frozen, read-only snapshot of real LOVE32 production state for the character Kite (`kite_male`). A later task will use it to answer: "If Kite's canonical visual design changes, which existing production assets and game references are actually affected?" This fixture only captures the evidence. It does not answer the question.

Scope: `kite_male` only. Female Kite (`kite_female_*`) is a separate character and is not in `configs/kite_male.yaml`. She is excluded; see §4.

## 2. Source

- Project: LOVE32 (Ren'Py visual novel, public Steam title "I Said I Didn't Wanna Date Anymore")
- Source root: `/Users/jeffreytse/Desktop/LOVE32/LOVE32`. All relative paths below are relative to this root.
- Source git HEAD: `f4816ca90c9a15bc927a63df5148050199ad2842` (2026-09-26T20:59:12+08:00, "Phase 4 repair 5F: carry Remy boundary memory into climax")
- The working tree was already dirty at capture (53 `status --porcelain` lines, recorded in `/tmp/kite_fixture_audit/love32_status_before.txt` on the Mac). The Kite-relevant changes are:
  - ` D game/images/kite_male_neutral.png`, `kite_male_relaxed.png`, `kite_male_smoking.png`, `kite_male_soft.png`, `kite_male_tired.png`. These are unstaged deletions. The files are still in HEAD and in the index.
  - Untracked: `game/route_kite.rpy.bak_kite_m_wire_20260923`, `game/credits.rpy.bak_kite_m_credits_20260923`, `game/images/side_treated/side_kite_male.png.bak_before_v66_20260922_150722`, `_quarantine_backups_20260922/`
  - Every copied `.rpy` file is identical to HEAD (`git diff --stat HEAD -- game/*.rpy` is empty).
- Captured: 2026-09-28 (HKT). Matcha base: `origin/main` = `65bb0f54193920c79b4324c925a665048354796a`.

## 3. Included Evidence

| Fixture path | What it is | Why included |
|---|---|---|
| `reference/kite_male_neutral.png` | Production `game/images/kite_male_neutral.png` as committed at HEAD. Copied from the byte-identical `_quarantine_backups_20260922/_asset_backups/kite_male_neutral_pre_softA_2026_09_14/kite_male neutral.png`. | Default/neutral image and the `angry` alias. Its name matches the YAML reference `./refs/kite_male_neutral.png`. |
| `reference/KEEP_kite_male.png` | The approved v19g neutral plate as installed on 2026-09-09 (a KEEP copy) | Canonical-reference candidate (see §5 "Canonical reference") |
| `reference/kite_male_bust_neutral_credits_v19g.png` | The source plate Jeffrey approved ("jeffrey_yes") | Only image with a recorded explicit approval |
| `assets/kite_male_{gentle,stressed,warm,withdrawn,crossed_arms}.png` | Live plates. Present in the working tree and identical to HEAD. | Declared expressions |
| `assets/kite_male_{relaxed,smoking,soft,tired}.png` | Plates from HEAD that are deleted in the working tree. `smoking`/`soft` were copied from byte-identical quarantine `.bak` files. `relaxed`/`tired` were extracted with `git --no-optional-locks cat-file blob HEAD:...`, because no identical copy exists on disk. | Declared and shown by the game |
| `assets/kite_male_{dark,dark_relaxed,dark_withdrawn}.png` | Live `game/images` plates with no `.rpy` reference found | These files ship, so leaving them out would create a blind spot |
| `assets/side_kite_male.png` | Side portrait | Side image, route-card portrait, and the stand-in shown when a plate is missing |
| `assets/kite_tattoo.png` | Evidence close-up of Kite's kanji tattoo | The only non-sprite still that shows Kite's body design. It is declared in the game. |
| `game/route_kite.rpy`, `game/li_sprite_normalization.rpy`, `game/side_portraits.rpy`, `game/characters.rpy` | Full verbatim copies | Image declarations, the `_kite_sprite` helper, the missing-file fallback, and the Character definition |
| `game/{credits,screens,route_select,route_friendships,route_neo,minigames,options}.rpy.excerpt.txt` | Evidence excerpts. Each header gives the source path, line ranges, the SHA-256 of the full original, and the excerpt's limitation. | Kite usage inside large files where most content is about other things |
| `metadata/KITE_ASSET_MASTERLIST.md` | Verbatim copy. It is Kite-specific and contains no secrets. | The only production-side description of what the Kite videos show |
| `metadata/INSTALL_REPORT_MALEKITE_V19G.json` | Verbatim copy | Provenance for the approval and install |
| `metadata/fixture-manifest.json` | Authoritative provenance | Paths, hashes, sizes, dimensions, and usage for every item |

`configs/kite_male.yaml` is deliberately not copied.

## 4. Excluded Evidence

Folder exclusions are based on project evidence. `game/options.rpy:233-243` (excerpted) keeps `game/**/_archive*/**`, `_legacy*`, `_originals`, `_pre_baseline*`, `_replaced*`, `_unused*`, `**.md`, `**.bak`, `game/test_hub.rpy`, `game/kite_demo_quickstart.rpy` and `game/dev_sprite_lineup.rpy` out of built distributions. No `.rpy` file references an `images/_…` path. `_asset_backups/`, `_quarantine_backups_20260922/` and `review/` are outside `game/`, so the game cannot load them.

- **Female Kite (separate character):** `game/images/kite_female_{angry,neutral,stressed,tired,warm}.png`, `game/images/side_treated/side_kite_female.png`, `game/images/_backup_kite_female_{relaxed,withdrawn}_*.png`, the female files under `_originals/defringe_jul17/`, `_replaced_2026_09_07_femalekite_promote/` and `_wave1_quarantine_outliers/`, and `review/kite_female_candidates/`. Her declarations are in `route_kite.rpy:28-45` and `image_aliases.rpy:131,193`, which are included only because they sit in the same file.
- **`kite_male` backups/replaced/originals (not shipped under options.rpy):**
  - `_originals/…` (defringe_jul17 `kite_male crossed_arms.png`, `kite_male soft.png`, `kite_male_soft_white_bg_jul16.png`, `kite_relaxed_pre_jul04`, `legacy_duplicates_jun05`, `side_portraits_pre_jul17`, `style_uniform_*`)
  - `_replaced_2026_06_10`, `_replaced_2026_06_18`, `_replaced_2026_07_17_outliers`, `_replaced_2026_09_09_malekite_v19g/*`
  - `_unused_archive_2026_06_19/kite_male_angry.png`
  - `_legacy_side_root_unused_2026_06_19/side kite_male.png`
  - `side_kite_male.png.bak_before_v66_20260922_150722`
- **Outside `game/`:** everything under `_asset_backups/` and `_quarantine_backups_20260922/` except the three byte-identical HEAD copies used as copy sources above. Everything under `review/` except the v19g source, the KEEP plate and the install report: over 250 Kite review/iteration images, raw generations, contact sheets and job JSONs.
- **Kite UI art `game/gui/resense/namebox_kite.png`** (300×64, 465 B, sha256 `e84fb8139c8b87fddc4268c6026ff10f072a50e77e1b4e0f70f93b8b2d845775`). It is a flat brown rounded plate with no character depiction, used at `screens.rpy:436-437`. A change to hair, accessories or outfit cannot affect it, so it is excluded under the minimality test. Its only link to Kite is the colour accent.
- **Background `game/images/bg/kite_apartment.png`** (1920×1080, 3,508,080 B, sha256 `df90f6bdc13e941bf8f96892c54c95f4360e0f10ba8fd8c80c71955f62030257`). It shows an empty room with no Kite. It is used at `image_aliases.rpy:85-86`, `route_kite.rpy:1946,2990`, `credits.rpy:170`, `premium_media.rpy:162`. Excluded under minimality.
- **Audio:** `game/audio/music/kite_theme.ogg` and `_originals/kite_theme_pre_jul04.ogg`. Not visual.
- **Scripts:**
  - `game/kite_demo_quickstart.rpy` and `game/dev_sprite_lineup.rpy` (dev/QA, not shipped). `dev_sprite_lineup.rpy:67` shows `kite_male neutral`.
  - `game/route_kite.rpy.bak_kite_m_wire_20260923` and `game/credits.rpy.bak_kite_m_credits_20260923` (untracked backups).
  - `*.rpyc` compiled files.
  - `game/KITE_VIDEO_PROMPTS_WAN.md`.
  - `transforms.rpy`: its `kite_male` mentions at 248-311 are comments only. `kite_first_night` (43) and `kite_smoking_scene_pose` (242) are positioning transforms.
  - `image_aliases.rpy`, `video_definitions.rpy`, `premium_media.rpy`: these contain only female/bg/video Kite references. Their line numbers are listed here and in §6.
- **Videos: all excluded.** No copied `.rpy` source shows what a video depicts. It only shows where each video is played. The only description of video content is the pre-generation prompt text in `metadata/KITE_ASSET_MASTERLIST.md` (dated 2026-05-01), which may not match the final clips. The videos were not rendered or viewed. Sizes: the four existing male-gated clips total 15,131,984 B (~15.1 MB); all eight existing non-female Kite clips total 50,863,992 B (~50.9 MB). Male-gated calls are marked with â.

| Path | Bytes | SHA-256 | Game reference |
|---|---|---|---|
| game/videos/kite_bad_male_ending.mp4 ♂ | 2,102,476 | 99340812a45200d766b157f7377d55cad800eed27f5d6828c01c76434d63e76e | route_kite.rpy:3581-3582; video_definitions.rpy:118 |
| game/videos/kite_bittersweet_male_ending.mp4 ♂ | 2,210,842 | b1d686b2b0c9c88ba81ac8e9921094ff8eb6a4fd8e73320dfa5b275be1145488 | route_kite.rpy:3505-3506; video_definitions.rpy:114 |
| game/videos/kite_smoking_scene.mp4 ♂ | 6,669,063 | 3053c34c3847e96d3fd99e84849bfc2f0e76c2373a93259c5c284948a68aa2e2 | route_kite.rpy:1543-1544 (label kite_interaction_3_male) |
| game/videos/kite_glass_shatter.mp4 ♂ | 4,149,603 | 9cb177ac12c973c8ed6fd6fcd9a995e10ca41c1864a5af5096caf3bd9456af0a | route_kite.rpy:2135-2136 (kite_interaction_5_male); video_definitions.rpy:147 |
| game/videos/kite_birthday_drink.mp4 | 2,500,462 | fca770e43e1d5e7985f8aeb6e9b03a28d370e33ce3ee77ccdc700f43a1899e0b | route_kite.rpy:475-476; video_definitions.rpy:136 |
| game/videos/kite_invoice_discovery.mp4 | 11,419,584 | 215625fe0ddf80dbf4b45d1977126e2ba4653e91d33c5486b3fa93552e12621e | route_kite.rpy:2052-2053; video_definitions.rpy:139 |
| game/videos/kite_tattoo_reveal.mp4 | 2,531,212 | ee8654e8acd33ba5626a6e535e499b73e88c91d7f3cb95ec95f4e1ace06eaca9 | video_definitions.rpy:144 declares `Null()`; route_kite.rpy:1830 says do not play |
| game/videos/kite_bedroom_loop.mp4 | 19,280,750 | 9a030859834c8efebb97ac6a48bbb47ba105ee6ac7595c81053913b556fdf2a9 | premium_media.rpy:161-163 (bg kite_bedroom loop) |
| game/videos/kite_good_male_ending.mp4 ♂ | MISSING ON DISK | — | route_kite.rpy:3422-3423 (guarded by `video_exists`); video_definitions.rpy:110 |
| game/videos/kite_{good,bittersweet,bad}_female_ending.mp4, kite_dart_scene.mp4 | 3,558,680 / 2,229,175 / 2,664,804 / 3,382,463 | a37d34fa… / 2d5a6ff8… / e42493b1… / 784a7910… | Female Kite (excluded character) |
| game/videos/_originals_respec_jul16/*, game/videos/_pre_baseline_20260624/*, game/_archive_unused_media_2026_06_20/videos/kite_smoking_scene_old_backup.mp4 | — | — | Not shipped (options.rpy:233,236,237) |

## 5. Asset Inventory

Pose = the attribute in the explicit `image kite_male <pose>` statement. Outfit is UNKNOWN throughout: no LOVE32 source or directory structure establishes an outfit per file, and the YAML's outfit families are not used as evidence. All `kite_male` stage plates are 928×1232.

| Source path | Filename | Type | Character | Pose | Outfit | Other role | Used by game? |
|---|---|---|---|---|---|---|---|
| game/images/kite_male_neutral.png (HEAD; deleted in WT) | kite_male_neutral.png | sprite | kite_male | neutral (+ alias angry) | UNKNOWN | default image; canonical-ref candidate | Yes (declared route_kite:17,26; 16 shows in route_kite; cameos). The file is missing in WT. |
| game/images/kite_male_gentle.png | kite_male_gentle.png | sprite | kite_male | gentle | UNKNOWN | — | Yes |
| game/images/kite_male_relaxed.png (HEAD; deleted in WT) | kite_male_relaxed.png | sprite | kite_male | relaxed | UNKNOWN | credits polaroid 2nd choice; minigame gallery | Yes (file missing in WT) |
| game/images/kite_male_smoking.png (HEAD; deleted in WT) | kite_male_smoking.png | sprite | kite_male | smoking | UNKNOWN | — | Yes, 1 show (file missing in WT) |
| game/images/kite_male_soft.png (HEAD; deleted in WT) | kite_male_soft.png | sprite | kite_male | soft | UNKNOWN | — | Yes (file missing in WT) |
| game/images/kite_male_stressed.png | kite_male_stressed.png | sprite | kite_male | stressed | UNKNOWN | popup-book ending element | Yes |
| game/images/kite_male_tired.png (HEAD; deleted in WT) | kite_male_tired.png | sprite | kite_male | tired | UNKNOWN | — | Yes (file missing in WT) |
| game/images/kite_male_warm.png | kite_male_warm.png | sprite | kite_male | warm | UNKNOWN | credits polaroid 1st choice; popup-book element | Yes |
| game/images/kite_male_withdrawn.png | kite_male_withdrawn.png | sprite | kite_male | withdrawn | UNKNOWN | — | Yes |
| game/images/kite_male_crossed_arms.png | kite_male_crossed_arms.png | sprite | kite_male | crossed_arms | UNKNOWN | — | Yes |
| game/images/kite_male_dark.png | kite_male_dark.png | sprite | kite_male (filename) | UNKNOWN | UNKNOWN | unreferenced | No reference found |
| game/images/kite_male_dark_relaxed.png | kite_male_dark_relaxed.png | sprite | kite_male (filename) | UNKNOWN | UNKNOWN | unreferenced | No reference found |
| game/images/kite_male_dark_withdrawn.png | kite_male_dark_withdrawn.png | sprite | kite_male (filename) | UNKNOWN | UNKNOWN | unreferenced | No reference found |
| game/images/side_treated/side_kite_male.png | side_kite_male.png | side portrait 400×400 | kite_male | UNKNOWN | UNKNOWN | route card; missing-plate fallback | Yes |
| game/images/evidence/kite_tattoo.png | kite_tattoo.png | evidence close-up 864×922 | kite_male (inferred) | — | bare torso | tattoo detail | Declared only (route_kite:10); no show found |
| review/…/_compare/KEEP_kite_male.png | KEEP_kite_male.png | approved installed plate copy | kite_male | neutral | UNKNOWN | reference | No |
| review/…/male_kite/kite_male_bust_neutral_credits_v19g.png | kite_male_bust_neutral_credits_v19g.png | approved source 1440×1920 | kite_male | neutral | UNKNOWN (install notes say "uniform apron") | reference | No |

No `layeredimage`, CG, or ending-still exists for Kite. `credits.rpy:147` (outside the excerpt range) says "Kite has no ending still — live sprite polaroid". Poses found beyond the YAML's ten: the `angry` alias resolves to the **neutral** file (`route_kite.rpy:26`, `li_sprite_normalization.rpy:189`), whereas the YAML says `angry: stressed`. The three `dark*` plates are extra, and so are the side portrait and the tattoo image. The YAML's note that files use spaces (`kite_male <pose>.png`) and have mixed canvases does not match the live files: they use underscores and are all 928×1232.

### Canonical reference

- The YAML's `reference: ./refs/kite_male_neutral.png` does not exist in matcha-engine (`refs/` contains only `.gitkeep`).
- The production file with that name is `game/images/kite_male_neutral.png` (fixture `reference/kite_male_neutral.png`): 928×1232, 1,418,374 B, sha256 `b3469eeed8510f5ae0807cafc8564b21b9be617a3a27027f7eca6d230c0da07d`. It is declared and used by the game (route_kite.rpy:17 and 26). It is committed at HEAD but deleted in the current working tree.
- A more authoritative candidate, with evidence: `INSTALL_REPORT_MALEKITE_V19G.json` records `jeffrey_yes: MaleKite_new_v19g` (2026-09-09 01:48 HKT). Its source is `kite_male_bust_neutral_credits_v19g.png` (1440×1920, 1,954,658 B, sha256 `c185dd5887013d71…`). That plate was installed as the neutral and side portrait, and a KEEP copy was written to `_compare/KEEP_kite_male.png` (928×1232, 729,490 B, sha256 `4dc0e718ecfb4449…`, mtime equal to the install time).
- The HEAD neutral does **not** match the KEEP plate. The HEAD bytes sit in a quarantine folder named `…neutral_pre_softA_2026_09_14`, next to `kite_male_neutral_OLD.png`, which is byte-identical to KEEP. So the neutral was changed after the approved install, and the files read here record no approval for that change. Which one is "canonical" is not settled by the evidence; all three images are included.

## 6. Game Usage

Every relationship below is established by copied source, either full files or excerpts.

- **Declaration mechanism:** `route_kite.rpy:17-27` declares `image kite_male <attr> = _kite_sprite("kite_male_<attr>.png")`. These are explicit declarations. `_kite_sprite` (`li_sprite_normalization.rpy:300-312`) loads `images/<filename>` and applies a scale from `LI_CHAR_SCALE["kite_male"]` (line 75), per-file `LI_ALIGN` tuning (lines 101-106) and a +19 baseline offset.
- **Missing-file behaviour:** `_normalized_li_sprite` (268-290) shows `side_kite_male.png` in a circle (via `_li_circle_path` 165-166 and `_li_circle_lock`) whenever the plate is not loadable. In the current working tree this applies to neutral/angry, relaxed, smoking, soft and tired. This is read from code; the game was not launched.
- **Ren'Py auto-declaration:** Ren'Py also auto-declares images from filenames under `game/images`. The name is lowercased, the directory is dropped, and spaces (not underscores) separate tags. So `kite_male_gentle.png` would auto-register as the single-tag image `kite_male_gentle`, not `kite_male gentle`. No Kite usage found depends on auto-declaration: every `show kite_male <attr>` resolves through the explicit statements. The `dark*` plates would exist only as auto-declared names (`kite_male_dark`, …), and no reference to those names was found. `config.automatic_images` is not set in any `.rpy` file.
- **Show sites in `route_kite.rpy` (line numbers):**
  - neutral: 72, 113, 131, 177, 568, 698, 798, 861, 1585, 1607, 2591, 2625, 3131, 3200, 3428, 3510
  - soft: 137, 170, 185, 192, 622, 643, 720, 760, 1160, 1405, 1417
  - warm: 141, 162, 423, 748, 1088, 1201, 1281, 1314, 1415, 1429
  - stressed: 725, 734, 738, 764, 781, 790, 1622, 2231, 2290, 2435, 2563, 3180, 3568, 3586
  - tired: 855, 858, 1155, 1643, 2013, 2026, 2056, 3150, 3498, 3521
  - relaxed: 1675, 1684, 1710, 1722, 1726, 1730, 1740, 1749, 1781, 1810, 1913, 1952, 2008
  - smoking: 1550
  - withdrawn: 1625, 2633
  - crossed_arms: 2148, 2179, 2242
  - gentle: 2207, 2262, 2265
  - Popup-book ending elements: warm 3478, neutral 3554, stressed 3624.
- **Other files:**
  - `route_friendships.rpy:62,159,248,345,652` and `route_neo.rpy:2614`: `show kite_male neutral`
  - `credits.rpy:106-120`: polaroid tries `kite_male_warm` > `relaxed` > `neutral`
  - `minigames.rpy:5206`: gallery uses `kite_male relaxed`
  - `route_select.rpy:58`: route card uses `side_kite_male.png`
  - `side_portraits.rpy:24`: `image side kite_male`
  - `screens.rpy:213-240`: the say chip detects any `kite_male*` tag on stage
  - `characters.rpy:41`: `define kite = Character("[kite_name]", …)` has no `image=`, so the side image is not attached through Character
- **Tattoo:** `image evidence kite_tattoo` is declared (`route_kite.rpy:10`); no `show` was found.

## 7. Provenance

`fixtures/kite-production/metadata/fixture-manifest.json` is authoritative. For each item it gives source path, original filename where renamed, production path and state, git blob where relevant, bytes, sha256, dimensions, role, relationship and game usage. Renames:
- `kite_male neutral.png` → `reference/kite_male_neutral.png`
- `kite_male smoking.png.bak` → `assets/kite_male_smoking.png`
- `kite_male soft.png.bak` → `assets/kite_male_soft.png`

Each of these was verified byte-identical to the HEAD blob of the production path. All images are byte-exact copies, with no conversion or resizing.

## 8. Integrity

LOVE32 was read only. Nothing was written in it. The only git commands used were `--no-optional-locks` reads (`status --porcelain`, `rev-parse`, `log`, `ls-files`, `cat-file`, `diff --stat`). Ren'Py was not launched, and no Python ran inside the LOVE32 tree. Before and after the fixture work, the following were recorded under `/tmp/kite_fixture_audit/` on the Mac and found identical: `status --porcelain`, HEAD, and SHA-256 + size + mtime for 118 Kite-candidate source files. No Matcha production file was changed. The work was done in a separate worktree, and the original dirty checkout was left untouched.

## 9. Known Blind Spots

- **Videos are not in the fixture** (see the §4 table). Whether they show Kite's hair, accessories or outfit has not been verified. `kite_good_male_ending.mp4` is referenced but missing from disk.
- **The working tree and HEAD disagree** for five plates. What a player would see depends on which state is built.
- **Outfit per plate is UNKNOWN.** Nothing was inferred from pixels or filenames.
- **Post-approval edit is undocumented.** The change between the approved neutral (KEEP) and the HEAD neutral, and the later "softA" pass whose output is not on disk, are not described in any file read.
- **Excerpt coverage:** excerpts cover only their stated line ranges. Other Kite references in those files outside the ranges are not included. Grep covered `game/**/*.rpy` only; `game/tools/*.py` references (not shipped) were not examined.
- **Build assumption:** the claim that backup folders do not ship rests on `options.rpy` build rules. Runtime loadability of the in-`game/` backup files in an SDK run was not tested.
- **Female Kite:** she shares route code, videos and the side-circle helper. Any change affecting her is out of scope.

## 10. Fixture Freeze Rule

After this commit, the fixture must not be changed during Evidence Protocol #1 or the controlled experiment.
