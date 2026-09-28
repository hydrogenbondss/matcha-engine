# Side B — Kite Arc: Animation & Asset Master List

> **Scope:** Every animation, background, and effect needed for Kite's complete route (male + female variants).  
> **Pipeline:** Midjourney → base scene image → Seedance → cinematic video → Ren'Py integration.  
> **Quality bar:** Cinematic, emotionally specific, cannot look AI-generated.  
> **Last updated:** 2026-05-01

---

## TECHNICAL SPECIFICATIONS (Apply to Everything)

### Dimensions
| Stage | Resolution | Aspect Ratio | Format |
|-------|-----------|--------------|--------|
| **Midjourney output** | 1920 × 1080 | 16:9 | PNG |
| **Seedance input** | 1920 × 1080 | 16:9 | PNG |
| **Seedance output** | 1920 × 1080 | 16:9 | MP4 (H.264) |
| **Ren'Py display** | 1920 × 1080 | 16:9 | — |

### Midjourney Parameters (append to every prompt)
```
--ar 16:9 --s 250 --style raw --q 2
```
Then upscale and crop to exactly **1920 × 1080**.

### Seedance Parameters
- **Output resolution:** 1920 × 1080
- **Frame rate:** 24 fps
- **Motion strength:** Medium–High (specified per prompt)
- **Camera:** First-person POV for all narrative videos. Locked off. No zoom. No pan.
- **Duration rule:** Story moments minimum 6–8 seconds. 3–4 seconds is too short to register a scene emotionally. Endings can be 5.0 seconds (they have the popup book to extend the moment).
- **Audio:** NO music / score in any video. All sound design added in Ren'Py via `play sound` / `play music` channels.

### File Size Targets
| Asset | Target Size |
|-------|-------------|
| Still backgrounds | 1–3 MB PNG |
| Character sprites | 500 KB – 1.5 MB PNG (transparent) |
| Seedance videos | 3–6 MB per clip (H.264, ~10 Mbps) |

---

## THE GOLDEN RULES

1. **One image per Seedance prompt.** Never feed separate BG + sprite.
2. **Interesting ELEMENT motion + locked camera = cinematic.** Boring elements + camera zoom = cheap Ken Burns.
3. **Endings only:** Static hold for 1.5 sec (becomes popup book BG). **Story moments:** Motion through full clip.
4. **Every prompt must specify exact duration in seconds.**
5. **Environmental motion is mandatory.** Steam, dust, rain, light flicker — something must move independently of the character.
6. **Character motion must be specific and mechanical.** "Shoulders rise 2cm, hold, fall." Not "he looks sad."

---

## TIER 1 — ENDING CINEMATICS (Popup Book Transition)

These play **before** the popup book sequence. They are the **only** videos that need a static hold at the end.

**Flow:**
```
Video plays (motion)
    ↓
Video holds on final frame (completely static, 1.5 sec)
    ↓
Ren'Py extracts that frame → popup book background
    ↓
Crossfade to paper diorama → elements pop up → grimoire closes
```

---

### END-01: Good Ending — "The Regular" (Male Kite)
**Duration:** 5.0 seconds total (3.5 sec motion + 1.5 sec static hold)  
**Camera:** Low angle, looking slightly up at Kite across the bar. Locked off.  
**Motion strength:** Medium

**Midjourney Prompt:**
```
Low angle shot from across a polished mahogany bar. A man with a shaved head and intense amber eyes stands behind the bar, wearing a black turtleneck with sleeves pushed up. His hand rests on the counter near a crystal old fashioned glass glowing amber with a large ice cube. Expression: unguarded, almost smiling, tired but genuine. Behind him, shelves of bottles catch warm golden light. A small dachshund with a red bandana sleeps on a bar stool. Fresh sage-green paint on the walls. Customers blurred in soft bokeh. Dust motes drift in a shaft of amber light. Intimate, earned peace. Cinematic anime painting style, soft realism, shallow depth of field, warm Hong Kong bar interior, film grain, 1920x1080 --ar 16:9 --s 250 --style raw --q 2
```

**Seedance Prompt:**
```
Low angle from across a polished mahogany bar. A man with a shaved head and amber eyes stands behind the bar in a black turtleneck. His hand pushes a crystal old fashioned glass slowly across the counter toward camera. The glass contains amber liquid and one large ice cube.

MOTION (3.5 seconds, then hold):
- The glass slides smoothly across the polished wood. The ice cube shifts gently inside, catching the amber light. Liquid laps against the glass edge.
- His hand withdraws slowly, fingers lingering on the counter edge for one extra beat before releasing.
- His shoulders drop -- tension visibly leaving his body, spine settling.
- The sleeping dog's ear twitches once. His tail thumps once against the stool leg.
- Background: one blurred customer raises a glass in toast, then lowers it.
- A hanging Edison bulb flickers almost imperceptibly, casting a brief moving shadow across the bottles.
- Dust motes swirl in the shaft of amber light above the counter.

SECOND 3.5–5.0 (STATIC HOLD):
- Absolutely zero motion. Frame is frozen. This frame becomes the popup book background.

CAMERA: Locked off. Zero camera movement for entire 5.0 seconds.
ATMOSPHERE: Warm, quiet, earned peace. The storm is finally over.
STYLE: Cinematic anime, soft realism, amber bar lighting, shallow depth of field.
```

**Ren'Py:**
```renpy
show movie "videos/kite_good_male_ending.mp4"
pause 5.0
scene expression "images/endings/kite_good_male_final.png"
pause 0.5
$ pb_elements = [{"image": "kite_male relaxed", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]
call screen popup_book_ending(Solid("#b89a6a"), pb_elements, ending_title="Good Ending: The Regular")
```

---

### END-02: Good Ending — "The Regular" (Female Kite)
**Duration:** 5.0 seconds total (3.5 sec motion + 1.5 sec static hold)  
**Camera:** Over-the-shoulder of player, looking at Kite behind the bar. Locked off.  
**Motion strength:** Medium

**Midjourney Prompt:**
```
Over-the-shoulder shot from a seated patron's POV. A woman with black hair pulled up in a loose messy bun — scattered loose strands, subtle blue highlights — stands behind a warm wooden bar. She wears a black satin button-up shirt with collar open, dark high-waisted trousers, black bartender's apron, pearl necklace, blue-teal drop earrings. A floral botanical tattoo covers her right forearm. She leans forward, one hand gently covering an unseen person's hand on a cocktail shaker. Expression focused, soft, teaching — not showing off. Amber light from hanging Edison bulbs warms her face. Bottles catch the glow behind her. A small dachshund with a red bandana watches from the counter. The bar is closed, chairs stacked, intimate. Dust motes in amber light. Cinematic anime painting style, soft realism, shallow depth of field, warm palette, film grain, 1920x1080 --ar 16:9 --s 250 --style raw --q 2
```

**Seedance Prompt:**
```
Over-the-shoulder shot. A woman with black hair pulled up in a loose messy bun — scattered loose strands, subtle blue highlights — stands behind a wooden bar, her hand covering another person's hand on a cocktail shaker. She wears a black satin button-up shirt, collar open, dark high-waisted trousers, black bartender's apron. Pearl necklace. Blue-teal drop earrings. Floral botanical tattoo on her right forearm. She guides the shaker in a slow, deliberate figure-eight motion. Expression focused and soft.

MOTION (3.5 seconds, then hold):
- The shaker moves in a slow figure-eight under her guidance. Liquid sloshes gently inside, visible through the metal gaps.
- Her thumb shifts slightly, adjusting the other person's grip with gentle pressure.
- She looks up from the shaker toward the unseen person -- her eyes soften for just a moment, then return to the shaker.
- Her free hand reaches for a glass on the back shelf, pauses, decides against it, and returns to her side.
- The dog's tail thumps twice against the stool leg. His ears perk, then relax.
- A hanging Edison bulb flickers once, casting a brief moving shadow across her collarbone and the shaker.

SECOND 3.5–5.0 (STATIC HOLD):
- Absolutely zero motion. Frame frozen.

CAMERA: Locked off. Zero camera movement.
ATMOSPHERE: Intimate, patient, domestic. Learning to be together.
STYLE: Cinematic anime, soft realism, warm amber bar light.
```

---

### END-03: Bittersweet Ending — "The Key" (Male Kite)
**Duration:** 5.0 seconds total (3.5 sec motion + 1.5 sec static hold)  
**Camera:** Eye-level, medium shot from the customer's side of the bar. Locked off.  
**Motion strength:** Low–Medium

**Midjourney Prompt:**
```
Eye-level medium shot from the customer side of a dimly lit wooden bar. A man with a shaved head and amber eyes stands behind the bar, head slightly down. One hand holds a white towel. The other rests near an old fashioned glass on the counter. Expression: neutral, guarded hope held carefully. Warm but muted light -- fewer customers, quieter night. A small dachshund sleeps in the corner. The bar feels like it's waiting. Dust motes in a thin shaft of light. Cinematic anime painting style, soft realism, muted amber palette, shallow depth of field, film grain, 1920x1080 --ar 16:9 --s 250 --style raw --q 2
```

**Seedance Prompt:**
```
Eye-level medium shot from the customer side of a dim bar. A man with a shaved head and amber eyes stands behind the bar. He looks up from wiping a glass -- his gaze finds the camera. His expression doesn't change much, but something in his eyes shifts. Hope, held carefully.

MOTION (3.5 seconds, then hold):
- He sets the towel down on the counter with deliberate slowness.
- His hand moves to an old fashioned glass. He slides it slowly across the counter -- slower than before, deliberate, like an offering.
- His fingers release the glass one at a time, the pinky lingering longest, unwilling to let go.
- He looks back down at the counter. Picks up the towel. Starts wiping again -- the same spot, over and over, circular motion.
- His jaw tightens, then releases on the third circle.
- Background: one customer gets up to leave, coat sweeping across the frame in soft motion blur.
- The dog in the corner lifts his head, looks at the man, puts it back down.

SECOND 3.5–5.0 (STATIC HOLD):
- Frame frozen. Towel mid-wipe. Eyes downcast.

CAMERA: Locked off. Zero camera movement.
ATMOSPHERE: Patience worn thin. A door held open too long.
STYLE: Cinematic anime, muted amber, quieter than the good ending.
```

---

### END-04: Bittersweet Ending — "The Key" (Female Kite)
**Duration:** 5.0 seconds total (3.5 sec motion + 1.5 sec static hold)  
**Camera:** Slightly low angle, looking up at Kite across the bar. Locked off.  
**Motion strength:** Low–Medium

**Midjourney Prompt:**
```
Slightly low angle shot looking up at a woman with black hair pulled up in a loose messy bun — scattered loose strands, subtle blue highlights — behind a dimly lit wooden bar. She wears a black satin button-up shirt with collar open, dark high-waisted trousers, black bartender's apron, pearl necklace, blue-teal drop earrings. A floral botanical tattoo covers her right forearm. She looks up from pouring a drink, expression composed but vulnerable. One hand holds a bottle. The other rests on the counter near a sliding glass. Warm but subdued light. The bar is half-empty. A small dachshund watches from under a stool. Dust motes drift. Cinematic anime painting style, soft realism, muted warm palette, film grain, 1920x1080 --ar 16:9 --s 250 --style raw --q 2
```

**Seedance Prompt:**
```
Slightly low angle looking up at a woman with black hair in a loose messy bun — scattered loose strands, subtle blue highlights — behind a dim bar. She wears a black satin button-up shirt, collar open, dark trousers, black bartender's apron. Pearl necklace, blue-teal drop earrings. Floral botanical tattoo on her right forearm. She looks up from a bottle she's holding -- her gaze finds the camera. She doesn't smile. Doesn't speak. Her hand moves the bottle away and reaches for a glass.

MOTION (3.5 seconds, then hold):
- She pours slowly. Amber liquid catches the light, filling the glass to exactly the right level. She stops the pour with a practiced wrist flick.
- She slides the glass with two fingers -- a short, precise push across the wood.
- Her thumb taps the counter once after releasing the glass. A nervous habit.
- She looks back down at the bottle in her hand, but her eyes stay unfocused for a long moment before blinking.
- Her shoulders rise with a deep breath, then fall.
- The dog under the stool shifts, pressing closer to her ankle.

SECOND 3.5–5.0 (STATIC HOLD):
- Frame frozen. Eyes down. Hand on bottle.

CAMERA: Locked off. Zero camera movement.
ATMOSPHERE: Quiet forgiveness. The space between almost and enough.
STYLE: Cinematic anime, muted warm light, stillness.
```

---

### END-05: Bad Ending — "Last Call" (Male Kite)
**Duration:** 5.0 seconds total (3.5 sec motion + 1.5 sec static hold)  
**Camera:** Eye-level, medium-close. Kite centered. Locked off.  
**Motion strength:** Low

**Midjourney Prompt:**
```
Eye-level medium-close shot. A man with a shaved head and amber eyes stands behind a busy bar, head down, wiping a glass with a white towel. His face is partially hidden. Expression unreadable. The bar is active enough -- customers in soft bokeh behind him, warm light -- but he is isolated in his own space. A small dachshund with a red bandana sits on the floor, looking toward a door just out of frame left. The glass in his hands is already clean. He's wiping it anyway. Dust motes. Cinematic anime painting style, soft realism, warm but lonely palette, film grain, 1920x1080 --ar 16:9 --s 250 --style raw --q 2
```

**Seedance Prompt:**
```
Eye-level medium-close. A man with a shaved head stands behind a bar, head down, wiping a glass that is already clean. He doesn't look up. His jaw is tight. In the background left, a door closes -- just a subtle shift in light as it shuts. He doesn't react. Keeps wiping. The same circular motion, over and over.

MOTION (3.5 seconds, then hold):
- The towel moves in slow, mechanical circles around the glass. Same spot, no change in pressure, no purpose.
- His thumb grips the glass tighter for one moment, knuckles whitening, then relaxes.
- A customer in the background raises a hand to order. He doesn't see it.
- The door in the background left swings closed. The light from the doorway narrows to a sliver, then disappears completely.
- His shoulders don't move. He doesn't breathe visibly. Just the arm, circling.
- The dog on the floor watches the door, then looks back at the man, then puts his head down on his paws.

SECOND 3.5–5.0 (STATIC HOLD):
- Frame frozen. Arm mid-circle. Door closed. Light gone.

CAMERA: Locked off. Zero camera movement.
ATMOSPHERE: Absence. The worst kind of loneliness -- the kind that looks like routine.
STYLE: Cinematic anime, warm light, cold emotional distance.
```

---

### END-06: Bad Ending — "Last Call" (Female Kite)
**Duration:** 5.0 seconds total (3.5 sec motion + 1.5 sec static hold)  
**Camera:** Eye-level, medium shot. Locked off.  
**Motion strength:** Low

**Midjourney Prompt:**
```
Eye-level medium shot. A woman with black hair pulled up in a loose messy bun — scattered loose strands, subtle blue highlights — stands behind a wooden bar, carefully setting down a polished glass. She wears a black satin button-up shirt with collar open, dark high-waisted trousers, black bartender's apron, pearl necklace, blue-teal drop earrings. A floral botanical tattoo covers her right forearm. Her movements are precise, controlled. She reaches for another glass. Doesn't look up. The bar stool in front of her is empty. The bar is moderately busy but she is contained within her own ritual. A small dachshund lies near the empty stool, not moving. Warm light, but the space in front of her feels cold. Dust motes in a shaft of light. Cinematic anime painting style, soft realism, film grain, 1920x1080 --ar 16:9 --s 250 --style raw --q 2
```

**Seedance Prompt:**
```
Eye-level medium shot. A woman with black hair in a loose messy bun — scattered loose strands, subtle blue highlights — stands behind a bar. She wears a black satin button-up shirt, collar open, dark trousers, black bartender's apron. Pearl necklace, blue-teal drop earrings. Floral botanical tattoo on her right forearm. She carefully sets down a polished glass. Picks up another. Starts polishing it with a white cloth. Her movements are slow and deliberate, ritualistic. She doesn't look up at the empty stool in front of her.

MOTION (3.5 seconds, then hold):
- The cloth moves in slow, even circles around the glass.
- She sets the glass down with a soft, deliberate placement. Picks up the next one.
- Her eyes stay downcast. Her breathing is steady, controlled.
- A customer in the background moves to sit in the empty stool. She doesn't look up, but her hand pauses for half a second. The customer changes their mind and moves to another seat.
- The dog near the empty stool doesn't move. Just watches her.
- Dust motes drift through a shaft of amber light above the empty space.

SECOND 3.5–5.0 (STATIC HOLD):
- Frame frozen. Cloth in hand. Eyes down. Empty stool waiting.

CAMERA: Locked off. Zero camera movement.
ATMOSPHERE: Controlled grief. The empty space maintained like a shrine.
STYLE: Cinematic anime, warm bar, cold absence.
```

---

## TIER 2 — KEY STORY MOMENT ANIMATIONS

**NO static hold.** These play mid-route and dissolve/cut back to gameplay. Motion runs the full duration.

---

### INT3-01: Smoking Scene (Male Kite)
**Duration:** 8.0 seconds (full motion, no hold)  
**Camera:** First-person POV, player standing at the end of the street. Locked off.  
**Motion strength:** Low–Medium  
**Audio:** NO music. Environmental sound design only.

**Why 8 seconds:** 4 seconds is too short to register a scene, understand the emotional state, and feel the moment. 8 seconds gives the viewer time to absorb the environment, notice Kite, and experience the interaction.

**Midjourney Prompt:**
```
First-person POV looking down a narrow Hong Kong street at night from roughly 15 meters away. The street is empty, wet cobblestones reflecting ambient light. In the middle distance, a man with a shaved head and amber eyes sits on a concrete curb, small in frame, forearms resting on his knees. He wears an oversized off-white sweatshirt. A thin wisp of smoke rises near him. Behind him, wooden bar doors glow warm amber. Neon signs blur in the far background. A red taxi is parked down the street with headlights OFF -- dark, still. Green ivy climbs stone walls. No fire. No sparks. No steam vents. Calm, quiet street. The viewer is standing at the end of the street, seeing him from afar. Cinematic anime painting style, soft realism, Hong Kong noir, film grain, 1920x1080 --ar 16:9 --s 250 --style raw --q 2
```

**Seedance Prompt:**
```
First-person POV standing at the end of a narrow Hong Kong street at night, looking down the street. The street is empty, wet cobblestones reflecting ambient light. In the middle distance, a man with a shaved head sits on a concrete curb, small in frame. He wears an oversized off-white sweatshirt. A thin wisp of smoke rises near him. Behind him, wooden bar doors glow warm amber. Neon signs blur in the far background. A red taxi sits parked with headlights OFF, completely still.

MOTION (full 8.0 seconds):
- SECOND 0.0--2.0 (THE APPROACH): The viewer is still. The scene breathes. Smoke rises from the man's cigarette in a thin, slow stream. His shoulders rise and fall with slow breathing. The cigarette ember pulses bright orange, then dims. Wet cobblestones shimmer with faint reflections. A neon sign flickers in the background. Nothing else moves. The viewer has time to see him, register the loneliness, understand the scene.

- SECOND 2.0--3.0 (THE WALK): The viewer begins walking forward. Very subtle -- the camera moves forward slowly, 1 meter over this second. The man grows slightly larger in frame. The smoke becomes more visible. The bar doors behind him become clearer. The viewer is approaching. The man does not notice yet.

- SECOND 3.0--4.0 (HE NOTICES): The man turns his head slowly toward the viewer. Not fast -- a tired, reluctant turn, like someone who sensed a presence but doesn't want to acknowledge it yet. His eyes find the viewer's POV. He holds the gaze for one beat. His expression shifts from distant to guarded recognition. He says nothing.

- SECOND 4.0--5.5 (THE MOMENT): He looks back down at the cigarette in his hand. Brings it to his lips for one slow drag. Exhales. The smoke drifts left-to-right across the frame on a light breeze, billowing and thinning out. His shoulders drop slightly. He is tired. He is here. He is seen.

- SECOND 5.5--7.0 (THE INVITATION): He holds the cigarette at his knee. He looks up at the viewer again. This time, his expression is softer. Not welcoming, but not closed either. The space next to him on the curb is visible. Empty. Waiting. The viewer has time to feel the invitation.

- SECOND 7.0--8.0 (THE HANG): He looks back down at the cigarette. Smoke continues to rise. The moment hangs. The street breathes. Frame ends here -- no fade, just a clean end point. The viewer has arrived.

ENVIRONMENTAL MOTION (continuous):
- Background neon signs stutter intermittently -- one flickers off for half a second, then back on.
- Wet cobblestones shimmer with faint, shifting reflections.
- A single leaf detaches from an ivy vine and drifts down in the foreground, passing close to camera.
- The taxi remains completely still. No lights. No motion. Parked.
- Very subtle camera breathing throughout -- 1mm shift, mimicking a person standing still, then walking, then standing again.

CAMERA: First-person POV. Locked off except for the slow forward walk at second 2.0--3.0. No zoom. No pan. The viewer IS the player.
ATMOSPHERE: Intimate, lonely, immersive. You found him. He knows you're there. Now what?
STYLE: Cinematic anime, Hong Kong noir, soft realism.

AUDIO DIRECTION (for sound design, not Seedance):
- NO music. No score. No ambient drone.
- Distant traffic hum, out of focus.
- Occasional car passing, tires on wet pavement, doppler effect.
- Raindrop splashing on cobblestone (one distinct drop at second 1.5).
- Cigarette paper crackle on inhale (at second 4.5).
- Soft exhale breath (at second 5.0).
- Neon sign electrical buzz, intermittent.
- Bar door muffled voices and clinking glasses, very faint.
- Footsteps on cobblestone -- soft, slow, the player's walk at second 2.0--3.0.
- Brief silence as he notices the viewer -- all sound drops for half a second at second 3.0.
```

**Ren'Py:**
```renpy
scene bg street_night
with fade

# Sound design layers
play sound "sfx/street_night_ambience.ogg" loop fadein 2.0
queue sound "sfx/neon_buzz.ogg" loop

# The footstep that makes him turn
$ renpy.pause(0.5)
play sound "sfx/footstep_cobblestone.ogg"

show movie "videos/kite_smoking_scene.mp4"
pause 8.0
hide movie
with dissolve

# Continue ambience under dialogue
```

---

### INT3-02: Dart Scene (Female Kite)
**Duration:** 4.0 seconds (full motion, no hold)  
**Camera:** First-person POV from the doorway of a dark bar, watching her. Locked off.  
**Motion strength:** High  
**Audio:** NO music. Environmental sound design only.

**Midjourney Prompt:**
```
First-person POV from the doorway of a dark, closed bar. A woman with black hair pulled up in a loose messy bun — scattered loose strands, subtle blue highlights — stands in profile, roughly 6 meters away, in throwing stance, arm cocked back, holding a dart. She wears a black satin button-up shirt with collar open, dark high-waisted trousers, black bartender's apron untied and hanging loose. Pearl necklace. Blue-teal drop earrings. A floral botanical tattoo covers her right forearm — her throwing arm. Behind her, a worn cork dartboard on the back wall. Three darts already stick in the board. Bottles line shelves behind her, catching amber light. Chairs are stacked on tables. No music. Her expression is focused, tense, channeling stress into precision. Dust motes in a shaft of light. The viewer is in the doorway, watching without being seen yet. Cinematic anime painting style, soft realism, film grain, 1920x1080 --ar 16:9 --s 250 --style raw --q 2
```

**Seedance Prompt:**
```
First-person POV from the doorway of a dark, closed bar. A woman with black hair in a loose messy bun stands in profile roughly 6 meters away, throwing arm cocked back, holding a dart. Her right forearm — the throwing arm — shows a floral botanical tattoo. She is unaware of the viewer. Chairs stacked. No music. Only the sound of her breathing and the dartboard.

MOTION (full 4.0 seconds):
- SECOND 0.0--1.0: She holds the throwing stance. Still. Focused. A dart in her cocked hand. Dust motes drift through a shaft of amber light.
- SECOND 1.0--1.5: Her throwing arm releases forward in a sharp, practiced whip -- the dart leaves her hand and travels toward the board (subtle motion blur on the dart).
- SECOND 1.5--2.0: The dart hits the board. The surrounding darts wobble briefly from the impact. She lowers her arm.
- SECOND 2.0--2.5: She rolls her shoulder once, tension releasing. She reaches for another dart from a nearby table -- rhythmic, mechanical.
- SECOND 2.5--3.5: She catches the next dart, weighs it in her hand, resets her stance. The loop begins again. But this time -- she pauses. Her head turns slightly toward the doorway. She sensed something. She doesn't see the viewer yet. She turns back to the board.
- SECOND 3.5--4.0: She raises the dart again. Frame ends on the poised moment.

ENVIRONMENTAL MOTION (continuous):
- A ceiling fan above spins lazily, casting slow-moving shadows across her back and the bottles.
- Dust motes drift through the shaft of amber light.
- A bottle on the shelf behind her catches a brief flicker of light from an unseen source.

CAMERA: First-person POV. Locked off. The viewer is standing in the doorway, watching her private ritual.
ATMOSPHERE: Controlled, repetitive, meditative. Caught in a private moment.
STYLE: Cinematic anime, warm bar lighting, soft realism.

AUDIO DIRECTION (for sound design, not Seedance):
- NO music. No score.
- Sharp inhale before the throw.
- Dart release -- soft whoosh.
- Thunk of dart hitting corkboard.
- Darts wobbling against each other.
- Foot shifting on wooden floor.
- Ceiling fan slow creak.
- Very faint street noise through closed door.
```

---

### BD-01: Birthday Old Fashioned
**Duration:** 4.0 seconds (full motion, no hold)  
**Camera:** First-person POV seated at the bar, looking at Kite. Locked off.  
**Motion strength:** Medium  
**Audio:** NO music. Environmental sound design only.

**Midjourney Prompt:**
```
First-person POV seated at a bar counter in a closed, dimly lit Hong Kong bar at night. Chairs stacked on tables. Only one stool is down -- the one the viewer is sitting on. Across the counter, a bartender stands holding a crystal old fashioned glass with amber liquid and one large ice cube. Their expression is nervous but earnest -- this matters. Behind them, shelves of bottles catch low amber light. A small dachshund peeks over the bar counter, ears perked, looking toward the viewer. Warm, intimate, private celebration. Dust motes in amber light. Cinematic anime painting style, soft realism, film grain, 1920x1080 --ar 16:9 --s 250 --style raw --q 2
```

**Seedance Prompt:**
```
First-person POV seated at a bar counter in a closed bar at night. Across the counter, a bartender holds a crystal old fashioned glass with amber liquid and one large ice cube. They slide the glass slowly across the polished counter toward the viewer's POV. A small dachshund peeks over the bar counter, watching the viewer.

MOTION (full 4.0 seconds):
- SECOND 0.0--1.0: The bartender holds the glass, looking at the viewer. Nervous. Earnest. They take a small breath.
- SECOND 1.0--2.5: The glass slides smoothly across the polished wood toward camera, the large ice cube shifting gently inside, catching the amber light. The motion is slow, deliberate, like an offering.
- SECOND 2.5--3.0: The bartender's hand releases the glass one finger at a time, lingering longest on the pinky. They withdraw their hand to their side, thumb hooking into their pocket -- a nervous gesture.
- SECOND 3.0--3.5: The dog's tail thumps twice against the wood of the bar, visible just over the edge. The dog's ears perk up, then relax.
- SECOND 3.5--4.0: The bartender looks down, then back up at the viewer. A small, uncertain smile. Frame ends.

ENVIRONMENTAL MOTION (continuous):
- A single hanging bulb flickers slightly, casting a moving shadow across the bottles.
- Dust motes swirl in the shaft of amber light.
- The ice cube in the glass shifts again, settling.

CAMERA: First-person POV. Locked off. The viewer IS the player receiving the drink.
ATMOSPHERE: Earned intimacy. Someone practiced this three times.
STYLE: Cinematic anime, warm amber, soft realism.

AUDIO DIRECTION (for sound design, not Seedance):
- NO music. No score.
- Glass sliding across polished wood -- smooth, low friction sound.
- Ice cube clinking gently inside the glass.
- Dog tail thumping against wood (two beats).
- Soft breath from the bartender before sliding the glass.
- Very faint clock ticking in the background.
- Bar fridge compressor hum.
```

---

### INT4-01: Invoice Discovery
**Duration:** 4.0 seconds (full motion, no hold)  
**Camera:** First-person POV, the player's hands reaching toward Kite's trembling hands. Locked off.  
**Motion strength:** Medium  
**Audio:** NO music. Environmental sound design only.

**Midjourney Prompt:**
```
First-person POV looking down at a dusty wooden table. Two pairs of hands sort through a cardboard box of papers. The hands closest to camera -- the viewer's -- are steady, reaching toward a crumpled paper invoice held by the other pair. Those hands are masculine, weathered, slightly trembling. The paper is crumpled at the edges. Dust motes float in a shaft of daylight from a high window. The background is a cluttered bar backroom -- shelves, cleaning supplies, stacked boxes. Cinematic anime painting style, soft realism, dusty daylight, tactile, film grain, 1920x1080 --ar 16:9 --s 250 --style raw --q 2
```

**Seedance Prompt:**
```
First-person POV looking down at a dusty wooden table. The viewer's steady hands reach toward a crumpled paper invoice held by another pair of trembling hands. The paper is pulled from a cardboard box.

MOTION (full 4.0 seconds):
- SECOND 0.0--1.0: The invoice is pulled from the box slowly. Dust falls from its creases in tiny particles, catching the daylight.
- SECOND 1.0--2.0: The fingers holding it tremble -- not dramatically, but visibly, the paper quivering. The viewer's steady hand reaches in closer.
- SECOND 2.0--2.5: The viewer's hand makes contact, steadying the trembling wrist with gentle pressure. Both pairs of hands hold the paper together.
- SECOND 2.5--3.0: The trembling hand releases the paper and covers the mouth -- a laugh starting, surprised, relieved.
- SECOND 3.0--3.5: The viewer's hand still holds the invoice. The other hand drops to the table, palm flat, grounding itself.
- SECOND 3.5--4.0: Both hands on the table now. The invoice between them. Still. Frame ends.

ENVIRONMENTAL MOTION (continuous):
- Dust motes swirl in the shaft of daylight as the movement disturbs the air.
- A single loose receipt drifts off the table and floats toward the floor, spinning slowly.
- Light from the window shifts subtly as a cloud passes outside.

CAMERA: First-person POV. Locked off. The viewer IS the player reaching out to steady Kite.
ATMOSPHERE: Relief so sharp it feels like pain. The proof they needed.
STYLE: Cinematic anime, dusty daylight, tactile realism.

AUDIO DIRECTION (for sound design, not Seedance):
- NO music. No score.
- Cardboard box shifting on wood.
- Paper rustling, crinkling.
- Dust particles -- almost silent, but a faint whisper.
- Sharp inhale from Kite as the paper is found.
- Surprised laugh -- short, breathy, disbelieving.
- Hand slapping the table in relief.
- Faint street noise through a high window.
```

---

### INT3-03: Tattoo Reveal
**Duration:** 4.0 seconds (full motion, no hold)  
**Camera:** First-person POV, the player's hand reaching toward Kite's tattoo. Extreme close-up, macro. Locked off.  
**Motion strength:** Low (intimate, subtle)  
**Audio:** NO music. Environmental sound design only.

**Midjourney Prompt:**
```
First-person POV extreme close-up macro. The viewer's feminine hand reaches toward a man's left side, above the hip. One black kanji character -- 勇 -- in bold brushstroke tattoo style. The skin is warm, slightly flushed. The viewer's fingers are almost touching the tattoo. The background is a dim bedroom -- rumpled sheets, soft lamplight, out of focus. Intimate, vulnerable. Shallow depth of field. Cinematic anime painting style, soft realism, warm skin tones, film grain, 1920x1080 --ar 16:9 --s 250 --style raw --q 2
```

**Seedance Prompt:**
```
First-person POV extreme close-up macro. The viewer's feminine hand reaches toward a man's left side. A black kanji tattoo -- 勇 -- in bold brushstroke. The viewer's fingers hover for a moment, then make contact.

MOTION (full 4.0 seconds):
- SECOND 0.0--1.0: The viewer's fingers hover millimeters above the skin, casting a tiny shadow that shifts slightly. The skin is warm, slightly flushed.
- SECOND 1.0--1.5: The fingers make contact -- the skin flinches slightly, goosebumps rising in a wave, then relaxes under the touch.
- SECOND 1.5--2.5: The fingers trace the first horizontal stroke of the character slowly, following the brushstroke's direction. The pressure is light, exploratory.
- SECOND 2.5--3.0: The man's chest rises with a sharp inhale, visible at the edge of frame, then holds for a beat, then releases.
- SECOND 3.0--3.5: The fingers complete tracing the character and rest flat against the skin for a moment. Still. Connected.
- SECOND 3.5--4.0: The fingers begin to withdraw slowly, reluctantly. The skin where they touched remains slightly flushed. Frame ends.

ENVIRONMENTAL MOTION (continuous):
- Background: bedsheets shift slightly out of focus, suggesting movement beyond the frame.
- A single strand of hair falls into the frame from above and drifts slowly past the tattoo.
- Soft lamplight flickers almost imperceptibly, casting a warm shift across the skin.

CAMERA: First-person POV. Locked off. The viewer IS the player touching Kite.
ATMOSPHERE: Vulnerability offered and accepted. Touch as confession.
STYLE: Cinematic anime, warm skin tones, extreme intimacy.

AUDIO DIRECTION (for sound design, not Seedance):
- NO music. No score.
- Skin-on-skin contact -- soft, barely audible.
- Sharp inhale from Kite as fingers make contact.
- Held breath.
- Slow exhale.
- Bedsheets shifting.
- Very faint heartbeat -- ambiguous whose.
```

---

### INT5-01: Glass Shatter
**Duration:** 3.0 seconds (full motion, no hold)  
**Camera:** First-person POV from behind the bar, the player's perspective watching the glass fall. Locked off.  
**Motion strength:** High  
**Audio:** NO music. Environmental sound design only.

**Midjourney Prompt:**
```
First-person POV from behind a wooden bar, looking down at the floor. A champagne flute in mid-fall above, dropping toward the viewer's POV. The glass is still mostly whole but cracks are beginning to spiderweb across it. Amber light catches the fractures. In the background, out of focus, a man with a shaved head stands behind the bar, head down, jaw tight. A small dachshund presses against the wall under a stool, ears flat. Frozen moment of impact. Cinematic anime painting style, soft realism, Hong Kong bar, film grain, 1920x1080 --ar 16:9 --s 250 --style raw --q 2
```

**Seedance Prompt:**
```
First-person POV from behind a wooden bar, looking down at the floor. A champagne flute falls through the air toward the viewer's POV. The glass catches amber light as it tumbles. In the background, a man stands behind the bar, head down, not watching. A small dog presses against the wall under a stool.

MOTION (full 3.0 seconds):
- SECOND 0.0--1.0: The glass tumbles slowly end-over-end, rotating as it falls toward camera. Light refracts through it, casting a moving prismatic spot on the wood below.
- SECOND 1.0--1.3: The glass makes contact with the floor. It shatters -- shards spray outward in slow motion, some toward camera, some away.
- SECOND 1.3--2.0: Fragments scatter across the wood, some spinning, some sliding to a stop. One shard bounces once, twice.
- SECOND 2.0--2.5: In the background, the man's shoulders tense but he does not look up. His jaw tightens.
- SECOND 2.5--3.0: The dog flinches, ears flattening further, but stays put against the wall. One large shard continues to spin on its edge before settling flat on the wood. A drop of spilled champagne spreads slowly across the floorboards.

ENVIRONMENTAL MOTION (continuous):
- The prismatic light spot from the falling glass moves across the wood and shatters with the glass.
- Amber light from behind the bar flickers slightly.

CAMERA: First-person POV. Locked off. The viewer IS the player standing behind the bar, watching the glass fall.
ATMOSPHERE: Controlled destruction. Anger made silent.
STYLE: Cinematic anime, slow-motion impact, soft realism.

AUDIO DIRECTION (for sound design, not Seedance):
- NO music. No score.
- Sharp glass ring as it leaves the bar (the moment before the fall).
- Wind rush as the glass falls.
- Impact -- sharp crack, not an explosion.
- Shards scattering across wood -- tinkling, skittering.
- One shard spinning on its edge -- high-pitched whine slowing down.
- Champagne droplets hitting wood -- soft patter.
- Dog whimper, very faint.
- Man's sharp exhale, controlled.
```

**Ren'Py:**
```renpy
play sound "sfx/glass_shatter.ogg"
show movie "videos/kite_glass_shatter.mp4"
pause 3.0
hide movie
with hpunch
```

---

## TIER 3 — ATMOSPHERIC LOOPS

**NO static end.** These loop forever behind dialogue. First and last frame must match.

---

### ATM-01: Bar Interior — Warm Night Loop
**Duration:** 4.0 seconds (seamless loop)  
**Camera:** First-person POV seated at the bar, looking down the counter. Locked off.  
**Motion strength:** Low  
**Audio:** NO music. Environmental sound design only.

**Midjourney Prompt:**
```
First-person POV seated at a bar counter in a cozy Hong Kong bar interior at night. Warm amber light from Edison bulbs. Wooden bar counter polished to a glow stretches ahead. Bottles on shelves catching light. Empty stools. A ceiling fan overhead. Steam from a coffee machine. Rain on windows. No people. The viewer is sitting, waiting. Cinematic anime painting style, soft realism, loopable atmosphere, film grain, 1920x1080 --ar 16:9 --s 250 --style raw --q 2
```

**Seedance Prompt:**
```
First-person POV seated at a bar counter in a cozy Hong Kong bar interior at night. Warm amber light. Empty stools. No people. The viewer is sitting, looking down the counter.

MOTION (4.0 second seamless loop):
- A ceiling fan spins lazily overhead, casting slow-moving shadows across the bar counter toward the viewer.
- Steam from an unseen coffee machine drifts left-to-right across the mid-ground.
- Rain streaks down the windows in the background, droplets merging and splitting.
- Light from a hanging Edison bulb flickers almost imperceptibly.
- Dust motes drift through a shaft of amber light near the bottles.
- The reflection in the polished bar counter shimmers slightly from the rain's light shift.
- FIRST AND LAST FRAME MUST BE NEARLY IDENTICAL for seamless looping.

CAMERA: First-person POV. Completely static. The viewer IS the player sitting at the bar.
ATMOSPHERE: Waiting. The bar breathing between customers.
STYLE: Cinematic anime, warm amber, soft realism.

AUDIO DIRECTION (for sound design, not Seedance):
- NO music. No score.
- Rain on windows -- steady, soft.
- Ceiling fan slow creak and whoosh.
- Coffee machine steam hiss, periodic.
- Fridge compressor hum.
- Very faint street noise through windows.
- Clock ticking somewhere behind the bar.
```

---

### ATM-02: Hong Kong Street — Night Loop
**Duration:** 4.0 seconds (seamless loop)  
**Camera:** First-person POV standing on the sidewalk, looking down the street. Locked off.  
**Motion strength:** Low–Medium  
**Audio:** NO music. Environmental sound design only.

**Midjourney Prompt:**
```
First-person POV standing on a narrow Hong Kong street at night, street level. Wet cobblestones reflecting warm bar light and cool neon signs. Stone buildings with green awnings and ivy. A red taxi parked at the curb with headlights OFF. Steam rising from a vent in the sidewalk. Light rain falling. Moody, cinematic, noir atmosphere. The viewer is standing, looking down the street. Cinematic anime painting style, soft realism, film grain, 1920x1080 --ar 16:9 --s 250 --style raw --q 2
```

**Seedance Prompt:**
```
First-person POV standing on a narrow Hong Kong street at night, street level. Wet cobblestones. Warm bar light and cool neon reflections. Light rain falling. Steam rising from a sidewalk vent. The viewer is standing, looking down the street.

MOTION (4.0 second seamless loop):
- Rain falls steadily, droplets hitting the cobblestones and creating expanding ripples in puddles.
- Steam from the vent rises in a turbulent column, catching the neon light and dissipating.
- A neon sign in the background flickers -- off for 0.3 seconds, then stutters back on.
- The reflection of the bar light in a puddle shimmers as raindrops hit it.
- A single leaf detaches from an ivy vine and drifts down, landing in a puddle.
- Distant traffic light changes from red to green, casting a brief color shift on the wet street.
- FIRST AND LAST FRAME MUST BE NEARLY IDENTICAL for seamless looping.

CAMERA: First-person POV. Completely static. The viewer IS the player standing on the street.
ATMOSPHERE: Noir, lonely, alive.
STYLE: Cinematic anime, Hong Kong night, soft realism.

AUDIO DIRECTION (for sound design, not Seedance):
- NO music. No score.
- Rain on cobblestones -- steady, textured.
- Steam vent -- low hiss, periodic gusts.
- Neon sign electrical buzz.
- Distant traffic hum.
- Occasional car passing, tires on wet pavement.
- Wind through the street -- soft, intermittent.
```

---

## REN'PY EFFECTS & CODE ANIMATIONS (Non-Video)

These are code-driven effects that supplement the videos. No Seedance needed.

| Effect | Location | Implementation |
|--------|----------|----------------|
| **Glitch flicker** | Corruption tier 2+ | `show kite at center, glitch_flicker` — already in `transforms.rpy` |
| **Color invert** | Corruption tier 3 | `show kite at center, color_invert` — already in `transforms.rpy` |
| **Screen shake** | Glass shatter (Int 5) | `show black with hpunch` — already implemented |
| **Email popup** | Int 5 threat | `show screen email_message(...)` — custom screen |
| **Cocktail minigame** | Warm scene | `call_screen cocktail_mixing_game` — already implemented |
| **Dart minigame** | Int 3 Female | `call play_dart_minigame` — already implemented |
| **Evidence zoom** | Int 4 Female | `ease 1.5 crop (1000, 50, 600, 338)` — already implemented |
| **Popup book ATL** | All endings | `popup_element_appear`, `popup_book_close` — already in `popup_book.rpy` |

---

## SUMMARY: GENERATION CHECKLIST

### Videos to Generate (Seedance)
**Tier 1 — Endings (6 videos, 5.0 sec each with 1.5s static hold):**
- [ ] END-01: Good Ending — "The Regular" (Male)
- [ ] END-02: Good Ending — "The Regular" (Female)
- [ ] END-03: Bittersweet — "The Key" (Male)
- [ ] END-04: Bittersweet — "The Key" (Female)
- [ ] END-05: Bad — "Last Call" (Male)
- [ ] END-06: Bad — "Last Call" (Female)

**Tier 2 — Story Moments (6 videos, full motion):**
- [ ] INT3-01: Smoking Scene (Male) — 4.0 sec
- [ ] INT3-02: Dart Scene (Female) — 4.0 sec
- [ ] BD-01: Birthday Old Fashioned — 4.0 sec
- [ ] INT4-01: Invoice Discovery — 4.0 sec
- [ ] INT3-03: Tattoo Reveal — 4.0 sec
- [ ] INT5-01: Glass Shatter — 3.0 sec

**Tier 3 — Atmosphere Loops (2 videos, seamless loop):**
- [ ] ATM-01: Bar Interior Loop — 4.0 sec
- [ ] ATM-02: Street Night Loop — 4.0 sec

**Total: 14 narrative videos + 2 loops = 16 Seedance generations**
**Total video runtime: ~62 seconds of unique footage**
**Estimated total file size: ~64 MB**

### Base Images to Generate (Midjourney)
One per video = **16 images** at exactly 1920 × 1080.

---

*Master list compiled: 2026-05-01*  
*Next step: Generate Midjourney base images for Tier 1 (endings) first.*
