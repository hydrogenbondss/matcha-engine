# Match Engine — Strategy & v1 Spec

*Drafted 2026-07-16 from a three-track research pass (competitors, VN-dev pain
points + platform AI policy, monetization). Claims are tagged: plain statements
were verified against fetched sources this session; "Likely" = inferred or
snippet-level evidence; "Assumption" = supplied judgment. Source links inline.*

---

## 1. What Match Engine is

**The Ren'Py-native character pipeline.** Define a character once in a YAML
config; get a consistent pose × expression × outfit sprite matrix generated on
your own GPU (ComfyUI / Stable Diffusion + LoRA) and deployed straight into
your Ren'Py project — correct folders, correct naming, and the `image` /
`layeredimage` / `Character` definitions written for you.

The moat is **orchestration + the last mile**, not generation. Generation is
already free (see VNCCS below).

## 2. Who it's for, and the priced pain

The zero-to-low-budget VN / indie 2D dev who cannot afford commissioned art.

- Commission prices (Lemma Soft commission threads, snippet-level — **Likely,
  re-verify before quoting publicly**): $35–$295 per character sprite, **+$5–15
  per additional expression**, +$10–12 per pose/outfit.
  ([t=65693](https://lemmasoft.renai.us/forums/viewtopic.php?t=65693),
  [t=65642](https://lemmasoft.renai.us/forums/viewtopic.php?t=65642),
  [t=66136](https://lemmasoft.renai.us/forums/viewtopic.php?t=66136))
- Derived: a 3-character cast × ~10 expressions plausibly runs **$300–$1,500+**
  commissioned.
- VNs typically need 10–28 expressions per character; consistency across 20+
  images is the acknowledged hard part *even for human artists*
  ([vnpaths.com](https://vnpaths.com/how-to-create-visual-novel-sprites/), snippet-level).
- An AI-using VN dev's own words: AI "is currently not very good at taking a
  character and replicating them in slightly different poses"
  ([itch.io t=2433560](https://itch.io/t/2433560/advice-for-using-ai-artworks-in-visual-novels), fetched).
- Devs in that space say plainly AI art is the only reason their game exists
  ([itch.io t=5022559](https://itch.io/t/5022559/how-do-you-feel-about-ai-generated-assets-being-sold-here), fetched).

## 3. Competitive landscape (July 2026)

| Who | What they solve | What they don't |
|---|---|---|
| **Scenario** (~$15–75/mo, cloud) | Custom-trained style/character models; Unity plugin | No Ren'Py, no local, credits per iteration |
| **Leonardo / Layer** (cloud) | Style + reference-based face consistency | No pose×expression matrix, no engine deploy |
| **TavernSprite** (cloud credits) | 28 expressions from one portrait | One pose only, ZIP download, "Ren'Py-ready" = PNG format only |
| **PixelLab / Retro Diffusion** | Pixel art (Aseprite plugin) | Different niche entirely |
| **VNCCS** (ComfyUI ext., MIT, free) | **Genuinely consistent character across outfits/emotions/poses** | Raw node graphs: no CLI, no config file, no reproducible batch runs, **no Ren'Py export** (verified against README) |
| Non-AI itch.io sprite assemblers | Consistency by construction | Fixed art style, fully manual |

Star-count reports for VNCCS conflicted this session (~390 vs ~1.4k) — traction
unverified; existence and active development verified
([github.com/AHEKOT/ComfyUI_VNCCS](https://github.com/AHEKOT/ComfyUI_VNCCS)).

**The gap:** nobody found does config → consistent sprite matrix → deploy into
project → generated engine code. Every competitor's "Ren'Py-ready" means
"transparent PNG." (**Likely** — searched, not exhaustively provable.)

**Strategic call:** don't compete with VNCCS on generation — evaluate building
*on* it (MIT license permits). Match's value over raw VNCCS is declarative
config, reproducibility, batch runs, and the deploy step.

## 4. v1 feature set

The paid wedge. Everything here exists because of a verified pain or risk:

1. **YAML character config** → full pose × expression × outfit matrix.
   Checkpoint + LoRA are **config fields, not hardcoded** (lesson from the
   2026-07-15 debugging session).
2. **Consistency pipeline** — benchmark VNCCS vs. own workflow; pick or wrap.
3. **Ren'Py deploy** — correct folders/naming + generated `layeredimage`,
   side-image, and `Character` scaffolding. The differentiator; over-invest here.
4. **Preflight validation** — check checkpoint/LoRA against ComfyUI
   `/object_info`, sanity-check model file sizes, **before** queueing. One
   check would have collapsed an hour of debugging into one error message.
5. **Loud failure** — surface ComfyUI `execution_error` messages per pose,
   exit non-zero, never write `.rpy` definitions for images that don't exist.
   The current CLI reports success on total failure; that's the first bug to fix.
6. **Per-model license surfacing** — output-commercial-use terms vary per
   checkpoint: Anything-series outputs are commercially usable (Fair AI PL —
   "output… not covered by this license",
   [Civitai licensing article](https://civitai.com/articles/18619/what-the-license), fetched);
   **NoobAI-XL claims to prohibit commercialization**. Show status in-app.
7. **Disclosure helper** — generate Steam AI Content Survey text and an
   itch.io AI-tag reminder. Both platforms allow AI assets **with mandatory
   disclosure**; undisclosed AI assets get de-indexed on itch
   ([Steam survey](https://partner.steamgames.com/doc/gettingstarted/contentsurvey),
   [itch thread](https://itch.io/t/4309690/generative-ai-disclosure-tagging), fetched).
   Turns the scariest market risk into a feature no competitor has.

**Later:** backgrounds/CGs, simple GUI wrapper, preset character/style packs,
Godot/Unity formatters, hosted version.

## 5. Business model

Precedent: **Retro Diffusion** — solo dev, AI game-art tool, **$20 Lite / $65
full, one-time, itch.io + Gumroad** (prices verified on listings).

1. **Free open CLI** — funnel + community trust.
2. **Pro package, ~$19–29 one-time** (itch.io + Gumroad): packaged installer,
   preset library, one-command deploy, priority fixes.
3. **Free VN-style LoRAs on Civitai**, branded "made for Match Engine," as the
   acquisition loop; sell curated packs later.
4. **Hosted credits version only after ~100 Pro sales.** Unit economics work —
   ~$0.20 compute per full character set at Replicate SDXL ~$0.0049/image →
   ~80%+ gross margin on a $12 credit pack — but auth/billing/abuse burden is
   real. Defer.

**Honest revenue expectation:** year one on the itch.io path is hundreds to
low thousands of dollars (**Likely** — inferred from itch.io earnings
distributions). Portfolio side-bet, not a startup; the hosted version is the
only subscription-scale upside found.

## 6. Timeline (at 10–25 hrs/week shared across five projects)

| Phase | Target | Work |
|---|---|---|
| Month 1 | Pipeline demo works | Correct anime checkpoint (match the LoRA's base — SD1.5 vs SDXL), fix the four product bugs (§4.1, .4, .5), evaluate VNCCS, dogfood on LOVE32 |
| Months 2–3 | Free release | Deploy polish, license + disclosure features, announce on Lemma Soft, Ren'Py Discord, r/comfyui, Civitai — **not** artist-heavy general VN forums |
| Months 3–4 | **First dollar** | Pro package on itch.io/Gumroad |
| Month 6+ | Hosted (conditional) | Only if ≥~100 Pro sales; serverless inference (Replicate/fal) |

## 7. Blockers & mitigations

1. **Community backlash lands on users, not the tool.** Verified: review-bombing
   on *suspicion* of AI art; a dev deleting his game over "soulless" criticism.
   Mitigation: sell to devs who've already chosen AI; ship disclosure tooling;
   never market a hide-it angle — non-disclosure is where social damage becomes
   platform damage.
2. **VNCCS undercuts generation at $0.** Mitigation: orchestrate it, don't
   fight it; the config-reproducibility + Ren'Py last mile is what it lacks.
3. **Founder attention** (five projects, ≤25 hrs/wk). Mitigation: Match gets a
   minority share until Spector/ECHO ship; month-1 scope is "make the demo
   work," not "build the business."
4. **Legal residue:** purely AI-generated sprites are likely uncopyrightable in
   the US (**Likely** — CRS overview surfaced, not fully fetched); output
   licenses vary per checkpoint. Mitigation: surface both honestly in-app.

## 8. Open verification items

- Competitor prices: **vendor-verified** (2026-07-17) for Scenario
  ($15/$45/$75/mo), Layer.ai ($10/300CU +$60/1000CU), and Retro Diffusion
  ($20 Lite/$65 full). **Do NOT quote** PixelLab (~$8 tier suspect) or
  Rosebud ($12/$36/$120 unconfirmed) — both are behind JS/login checkouts
  and need a real-browser read before public use.
- Lemma Soft commission figures are search-snippet-level (forum 403'd).
- "No one does Ren'Py deploy" — searched, not exhaustively provable.
- VNCCS traction (conflicting star counts).
- Which base model `small_hours_style_v1` LoRA was trained on (SD1.5 vs SDXL)
  — determines the correct checkpoint for the pipeline.
