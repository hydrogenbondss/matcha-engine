# =========================================================
# KITE - INTERACTION 1
# =========================================================

# Unused as a show. Int3 plays the file via play_cutscene.
# A Movie() here can paint an empty video box if shown or predicted.
image kite_smoking_video = Null()

# Evidence images
image evidence kite_tattoo = "images/evidence/kite_tattoo.png"
image evidence fake_rat_photo = "images/evidence/fake_rat_photo.png"

# Aug-31 static asset gate: wire only the matching transparent plates whose
# alpha geometry stays close to neutral. Soft/smoking/crossed_arms retain
# opaque/edge-risk regions, so those script contracts use the safest clean
# plate with the same on-shift/off-duty silhouette.
image kite_male neutral = _kite_sprite("kite_male_neutral.png")
image kite_male gentle = _kite_sprite("kite_male_gentle.png")
image kite_male relaxed = _kite_sprite("kite_male_relaxed.png")
image kite_male smoking = _kite_sprite("kite_male_smoking.png")
image kite_male soft = _kite_sprite("kite_male_soft.png")
image kite_male stressed = _kite_sprite("kite_male_stressed.png")
image kite_male tired = _kite_sprite("kite_male_tired.png")
image kite_male warm = _kite_sprite("kite_male_warm.png")
image kite_male withdrawn = _kite_sprite("kite_male_withdrawn.png")
image kite_male angry = _kite_sprite("kite_male_neutral.png")
image kite_male crossed_arms = _kite_sprite("kite_male_crossed_arms.png")
image kite_female neutral = _kite_sprite("kite_female_neutral.png")
## Wave 2: white-matte relaxed quarantined from live — use warm until regen
image kite_female relaxed = _kite_sprite("kite_female_warm.png")
image kite_female stressed = _kite_sprite("kite_female_stressed.png")
image kite_female tired = _kite_sprite("kite_female_tired.png")
## Wave 2: white-matte withdrawn → neutral until regen
image kite_female withdrawn = _kite_sprite("kite_female_neutral.png")
image kite_female angry = _kite_sprite("kite_female_angry.png")
image kite_female warm = _kite_sprite("kite_female_warm.png")

init python:
    def _kite_optional_sprite(name, fallback):
        filename = name + ".png"
        path = "images/" + filename
        return filename if renpy.loadable(path) else fallback

## Lane2: kite_female_date.png stays quarantined (wrong identity). Never optional-restore.
image kite_female date = _kite_sprite("kite_female_warm.png")

label kite_interaction_1:
    ## ASSET STATUS: IN PRODUCTION — Kite M/F opening plates not Jeffrey-locked yet.
    ## Presentation motion may run; do not treat sprites as final.

    $ save_name = "First night"
    $ kite_progress = 1
    $ play_story_music("kite_theme", fadeout=1.0, fadein=2.0, if_changed=True)
    $ quick_menu = True

    ## Street → Copper Room arrival (location, not a warp).
    scene black
    with open_hold_black
    $ play_story_sfx("door_open")
    pause open_copper_door_hold
    $ play_story_ambience("bar_murmur", fadeout=0.5, fadein=1.2, if_changed=True)
    scene bg bar_warm_night at open_copper_reveal, bg_breathe
    with open_street_to_copper
    window hide
    ## Outside → door → room — hold so depth can read. Kite first; Buddy after.
    pause 1.28
    narrator "Warm air. Copper light. The street noise drops behind the door."
    pause 0.62

    if kite_variant == "male":
        ## First impression: bartender body before mascot / talk.
        show kite_male neutral at kite_first_night
        with open_soft_x
        pause 0.55
        narrator "He finishes wiping a glass that was already clean."
        pause 0.4
        narrator "Then he looks up. Not startled. Just registering."
        pause 0.35
        window auto
        kite "Kite. You don't have to talk."

        menu:
            "Sit.":
                $ kite_int1_stool = "sat"
                show buddy neutral at buddy_first_night
                $ play_story_sfx("buddy_collar")
                narrator "You take the stool beside him. A dog under the rail keeps one eye open."
                kite "That's Buddy. He'll move if he likes you."
                kite "That's approval. More or less."

            "Stand for now.":
                $ kite_int1_stool = "stood"
                show buddy neutral at buddy_first_night
                $ play_story_sfx("buddy_collar")
                narrator "You leave the stool empty. The room carries on around it."
                kite "That's Buddy under the rail. No rush."

        kite "There's an open pour. For the rail — not for the room."

        menu:
            "I'll mix it. Show me the bottles.":
                if not persistent.minigame_cocktail_tutorial_seen:
                    kite "Grab whatever pulls. The glass will tell you if you're wrong."
                    $ persistent.minigame_cocktail_tutorial_seen = True
                window hide
                with open_soft_x
                $ reset_echo_cocktail_game()
                $ result_key, delta = renpy.call_screen("echo_cocktail_minigame", kite_variant=kite_variant, story_mode=True, teach_regular=False, allow_kite_interlude=True)
                ## First pour may yield kite_interlude once: Copper Room beat, then resume SAME mix (no reset).
                while result_key == "kite_interlude":
                    scene bg bar_warm_night at bg_breathe
                    show buddy neutral at buddy_first_night
                    show kite_male neutral at kite_first_night
                    with open_handoff
                    window auto
                    kite "Easy. Let it settle."
                    pause 0.55
                    window hide
                    $ cocktail_kite_interlude_pending = False
                    $ result_key, delta = renpy.call_screen("echo_cocktail_minigame", kite_variant=kite_variant, story_mode=True, teach_regular=False, allow_kite_interlude=True)
                $ persistent.minigame_cocktail_unlocked = True
                $ kite_cocktail_result = result_key
                if kite_first_cocktail_result is None:
                    $ kite_first_cocktail_result = result_key
                ## Keep the number in the save; don't flash arcade meter chrome on first pour.
                if delta:
                    $ kite_meter += delta

                scene bg bar_warm_night at bg_breathe
                show buddy neutral at buddy_first_night
                show kite_male neutral at kite_first_night
                with open_handoff
                window auto
                pause 0.42
                $ play_story_sfx("glass_set")
                if result_key in ("balanced", "interesting"):
                    show kite_male soft at kite_first_night
                    with open_expr_x
                    narrator "He turns the glass once under the rail light. Does not rush the sip."
                elif result_key in ("messy_twice", "bitter_meaning"):
                    show kite_male warm at kite_first_night
                    with open_expr_x
                    narrator "He raises an eyebrow at the color. Drinks anyway."
                elif result_key in ("safe", "old_fashioned_safe"):
                    narrator "He tastes it. Sets it down square. No speech yet."
                else:
                    narrator "He takes the glass. Looks at you over the rim before he drinks."
                $ reaction = get_cocktail_reaction_text(result_key, kite_variant)
                kite "[reaction]"

            "You pour. I'll watch.":
                $ kite_cocktail_result = "watched"
                kite "Then don't blink. I hate a bored audience."

            "Just water. I'm not here to date.":
                $ kite_cocktail_result = None
                $ kite_int1_glass = "water"
                kite "Not dating. Got it. Stool's still a stool."

        if kite_cocktail_result is not None:
            $ play_story_sfx("glass_set")
            show kite_male warm at kite_first_night, li_lean_in
            window hide
            menu:
                "Take the glass.":
                    window auto
                    $ kite_int1_glass = "took"
                    $ meter_bump("kite")
                    narrator "He slides it to your hand. Warm. Exact."
                    show kite_male soft at kite_first_night
                    kite "Don't thank me. Drink it before it goes polite."

                "Push it back. Not ready.":
                    window auto
                    $ kite_int1_glass = "pushed"
                    narrator "He leaves it on the rail. Turns to the sink."
                    show kite_male neutral at kite_first_night
                    kite "Fair. It'll wait."

                "Ask him to taste it first.":
                    window auto
                    $ kite_int1_glass = "taste"
                    $ meter_bump("kite")
                    narrator "He does. Small. Professional. Then pushes it to you."
                    show kite_male soft at kite_first_night
                    kite "Still good. Take it."
        else:
            ## Water path: respect the not-dating boundary — no intimacy glass menu.
            $ play_story_sfx("glass_set")
            narrator "He sets a water glass on the rail. No pour. No performance."

        show kite_male soft at kite_first_night
        kite "You can finish it here. No need to make a night of it."
        pause 0.45
        narrator "Buddy thumps once under the rail. Settles."
        kite "If you come back, stool's the same."
        kite "We outlast whatever pinged you out there."

        hide kite_male
        hide buddy
        with open_soft_x

    else:
        ## First impression parity: bartender before Buddy.
        show kite_female neutral at kite_first_night
        with open_soft_x
        pause 0.55
        narrator "She sets a glass down square. Checks the rim. Then you."
        pause 0.45
        window auto
        kite "Kite. You don't have to talk."

        menu:
            "Sit.":
                $ kite_int1_stool = "sat"
                show buddy neutral at buddy_first_night
                $ play_story_sfx("buddy_collar")
                narrator "You take the open stool. A dog shifts closer to your shoe."
                kite "Buddy. He usually charges for that."

            "Stand for now.":
                $ kite_int1_stool = "stood"
                show buddy neutral at buddy_first_night
                $ play_story_sfx("buddy_collar")
                narrator "The rail is cool under your hand. The stool stays open."
                kite "Buddy's under there. Take your time."

        kite "There's an open pour. For the rail — not for the room."

        menu:
            "I'll mix it. Show me the bottles.":
                if not persistent.minigame_cocktail_tutorial_seen:
                    kite "Grab whatever pulls. The glass will tell you if you're wrong."
                    $ persistent.minigame_cocktail_tutorial_seen = True
                window hide
                with open_soft_x
                $ reset_echo_cocktail_game()
                $ result_key, delta = renpy.call_screen("echo_cocktail_minigame", kite_variant=kite_variant, story_mode=True, teach_regular=False, allow_kite_interlude=True)
                ## First pour may yield kite_interlude once: Copper Room beat, then resume SAME mix (no reset).
                while result_key == "kite_interlude":
                    scene bg bar_warm_night at bg_breathe
                    show buddy neutral at buddy_first_night
                    show kite_female neutral at kite_first_night
                    with open_handoff
                    window auto
                    kite "Easy. Let it settle."
                    pause 0.55
                    window hide
                    $ cocktail_kite_interlude_pending = False
                    $ result_key, delta = renpy.call_screen("echo_cocktail_minigame", kite_variant=kite_variant, story_mode=True, teach_regular=False, allow_kite_interlude=True)
                $ persistent.minigame_cocktail_unlocked = True
                $ kite_cocktail_result = result_key
                if kite_first_cocktail_result is None:
                    $ kite_first_cocktail_result = result_key
                ## Keep the number in the save; don't flash arcade meter chrome on first pour.
                if delta:
                    $ kite_meter += delta

                scene bg bar_warm_night at bg_breathe
                show buddy neutral at buddy_first_night
                show kite_female neutral at kite_first_night
                with open_handoff
                window auto
                pause 0.42
                $ play_story_sfx("glass_set")
                if result_key in ("balanced", "interesting"):
                    show kite_female relaxed at kite_first_night
                    with open_expr_x
                    narrator "She turns the glass once under the rail light. Does not rush the sip."
                elif result_key in ("messy_twice", "bitter_meaning"):
                    show kite_female warm at kite_first_night
                    with open_expr_x
                    narrator "She raises an eyebrow at the color. Drinks anyway."
                elif result_key in ("safe", "old_fashioned_safe"):
                    narrator "She tastes it. Sets it down square. No speech yet."
                else:
                    narrator "She takes the glass. Looks at you over the rim before she drinks."
                $ reaction = get_cocktail_reaction_text(result_key, kite_variant)
                kite "[reaction]"

            "You pour. I'll watch.":
                $ kite_cocktail_result = "watched"
                kite "Then watch like you mean it. I notice."

            "Just water. I'm not here to date.":
                $ kite_cocktail_result = None
                $ kite_int1_glass = "water"
                kite "Not dating. Fine. Water still counts as sitting here."

        if kite_cocktail_result is not None:
            $ play_story_sfx("glass_set")
            show kite_female warm at kite_first_night, li_lean_in
            window hide
            menu:
                "Take the glass.":
                    window auto
                    $ kite_int1_glass = "took"
                    $ meter_bump("kite")
                    narrator "She slides it to your hand. Warm. Exact."
                    show kite_female relaxed at kite_first_night
                    kite "Good. I hate wasting a clean pour."

                "Push it back. Not ready.":
                    window auto
                    $ kite_int1_glass = "pushed"
                    narrator "She leaves it on the rail. Turns to the sink."
                    show kite_female neutral at kite_first_night
                    kite "Fair. It'll wait."

                "Ask her to taste it first.":
                    window auto
                    $ kite_int1_glass = "taste"
                    $ meter_bump("kite")
                    narrator "She does. Small. Professional. Then pushes it to you."
                    show kite_female relaxed at kite_first_night
                    kite "Still good. Take it."
        else:
            ## Water path: respect the not-dating boundary — no intimacy glass menu.
            $ play_story_sfx("glass_set")
            narrator "She sets a water glass on the rail. No pour. No performance."

        show kite_female relaxed at kite_first_night
        kite "You can finish it here. No need to make a night of it."
        pause 0.45
        narrator "Buddy sighs under the stool. Settles against the rail."
        kite "Same stool tomorrow if you want it."
        kite "We outlast whatever pinged you out there."

        hide kite_female
        hide buddy
        with open_soft_x

    $ met_kite = True
    $ stop_story_ambience(fadeout=0.8)
    narrator "Copper stays warm behind you. Outside is still the same night — not a menu."
    jump love32_between_nights


label kite_int1_echo:
    ## 31 Aug: Int1 delayed callback — stool / glass. Also called from
    ## kite_interaction_2_dense so New Game (kite_dd_slice) hears it.
    if kite_int1_stool == "sat":
        narrator "[kite_subj!c] nods at the same stool without announcing it."
        kite "Still free."
    elif kite_int1_stool == "stood":
        narrator "[kite_subj!c] leaves the stool empty a beat longer than [kite_subj] needs to."
        kite "You can take it this time. Or not."
    if kite_cocktail_result == "watched":
        narrator "[kite_subj!c] starts the pour slower than usual, angled so you can see every step."
        kite "Front row. You earned it last time."
    if kite_int1_glass == "took":
        narrator "[kite_subj!c] sets The Regular where your hand was on night one."
        kite "Same place."
    elif kite_int1_glass == "pushed":
        narrator "[kite_subj!c] parks a glass on the rail and walks away from it."
        kite "It'll wait."
    elif kite_int1_glass == "taste":
        narrator "[kite_subj!c] tastes first again. Same small professional sip. Then slides it over."
        kite "Still good."
    elif kite_int1_glass == "named":
        kite "Still mine. Don't write it down."
    elif kite_int1_glass == "water":
        narrator "A glass of water is already on the rail before you ask. No garnish. Nothing on the menu about it."
        kite "Still not dating? Stool doesn't mind."
    return


label kite_int2_echo:
    ## 31 Aug: Int2 delayed callback — hang verb or app line, one scene later.
    if kite_int2_verb == "scratch":
        kite "You scratched him harder. Don't make it a habit."
    elif kite_int2_verb == "rail":
        kite "Rail's still sticky. Family rates stand."
    elif kite_int2_verb == "glass":
        kite "You polished one wrong. I put it back."
    elif kite_int2_verb == "deleted":
        kite "Phone still face-down, I hope."
    elif kite_int2_verb == "trying":
        kite "Stool still takes debriefs. If you're still trying."
    elif kite_int2_verb == "dates":
        kite "A few more dates. I figured then. I figure now."
    return


label kite_int5_echo:
    ## 31 Aug: Int5 delayed callback — stay / time. Only the stay path
    ## reaches lockin. Time returns. Silent if a hub jump skipped Int5.
    if kite_int5_help == "stay":
        if kite_variant == "male":
            kite "You stayed. Dustpan first."
        else:
            kite "You stayed. Cloths first."
    return


# =========================================================
# KITE - BIRTHDAY SCENE
# =========================================================

label kite_birthday_scene:
    $ save_name = "The Birthday Old Fashioned"
    $ stop_story_music(fadeout=0.8)
    $ play_story_ambience("bar_murmur", fadeout=0.8, fadein=1.0, if_changed=True)

    scene bg bedroom_night
    with fade

    narrator "Saturday. Your birthday."
    narrator "You almost stay home."

    # Kite's own leather accent (#8B5A3C — the same brown used for his
    # dialogue portrait ring and route-select card) reinforced here instead
    # of the shared generic blue every other LI's texts use.
    call phone_text("Kite", "Are you free tonight? I'm at the bar after closing.", accent="#8B5A3C")

    scene bg bar_night
    with fade

    narrator "The Copper Room is closed. Chairs stacked. Lights down."
    narrator "You knock twice. The door unlocks."

    if kite_variant == "male":
        show kite_male warm at li_center
        with dissolve

        narrator "He stands behind the bar with a glass already waiting."

        kite "I wasn't sure if I should text you."
        kite "I don't really know how birthdays work."

    else:
        show kite_female tired at center
        with dissolve

        narrator "She's behind the bar when you come in. Doesn't look up."
        narrator "A glass already on the counter."

        kite "Lock it behind you."

    if kite_variant == "male":
        menu:
            "I'm glad you did.":
                $ meter_bump("kite")
                kite "Yeah?"
                kite "Good."

            "You didn't have to.":
                kite "I know."
                kite "That's exactly why I wanted to."
    else:
        menu:
            "Of course I came.":
                $ meter_bump("kite")
                kite "Yeah."
                kite "Good."

            "You asked me to.":
                kite "I know."
                kite "Come in."

    # Jul 5 fix: this used the exact same ingredients as The Regular
    # (bourbon/honey/ginger/bitters, Interaction 1) — which contradicted
    # "I practiced it three times this week" a line later, since Int 1
    # establishes he makes The Regular on total autopilot, no practice
    # needed. Different components so this reads as something he actually
    # had to work out, not a recipe he already has memorized.
    kite "Birthday Old Fashioned. Bourbon, brown sugar, orange bitters, a burnt orange twist."

    if kite_variant == "male":
        kite "I practiced it three times this week."
    else:
        kite "The fourth attempt. Don't ask about the other three."

    # Birthday drink cinematic
    if video_exists("videos/kite_birthday_drink.mp4"):
        $ play_cutscene("videos/kite_birthday_drink.mp4", 8.2)
        scene bg bar_night
    else:
        narrator "[kite_subj!c] slides the glass across the bar. The drink glows amber over a single large ice cube."
        $ play_story_sfx("glass_set")

    if kite_variant == "male":
        kite "The first two attempts were terrible. This one came out right."

        menu:
            "To my birthday.":
                kite "To your birthday."
                kite "And to people who show up when they don't have to."

            "To birthdays.":
                kite "To birthdays."
                kite "Even the ones that don't go as planned."

            "To showing up.":
                kite "...Yeah."
                kite "To that."
    else:
        narrator "She watches you look at the drink instead of drinking it."
        kite "It's not going to taste better if you stare at it."

        menu:
            "To tonight.":
                kite "To tonight."

            "To making something out of nothing.":
                kite "...Yeah."
                kite "To that."

            "To people who show up.":
                kite "That's the one."

    if kite_variant == "male":
        kite "Buddy. Customer."

        show buddy neutral at buddy_center
        with dissolve
        narrator "Buddy lifts his head from behind the bar and blinks at you slowly. His tail thumps once against the wood."
        $ play_story_sfx("buddy_collar")

        kite "That's his birthday greeting. You're honored."

        menu:
            "I'll take it.":
                $ meter_bump("kite")
                kite "You should. That's a first, actually."

            "Does he know it's my birthday?":
                kite "He knows. Dogs understand cake and attention. Tonight you get one of those."

        narrator "Buddy pushes himself up from the floor behind the bar and trots over. He sniffs your shoes and curls up on your foot."

        kite "He's claiming you."
        kite "In his head, you're his now."

        menu:
            "I feel special.":
                kite "You should."

            "My foot is going numb.":
                kite "Small dog, big gravity."

    else:
        show buddy neutral at buddy_center
        with dissolve
        narrator "Buddy appears from behind the bar without being called. He trots over and sniffs your shoes, then curls up on your foot."
        $ play_story_sfx("buddy_collar")

        narrator "She watches him without saying anything."

        kite "He did that the second night too. I wasn't sure what to do with it."

        menu:
            "Neither was I.":
                $ meter_bump("kite")
                narrator "She almost smiles."
                kite "Didn't think you'd just let him."

            "He's got good instincts.":
                $ meter_bump("kite")
                kite "He's particular. That's not nothing, coming from him."

            "What did you do with it?":
                kite "Let him."
                pause 0.5
                kite "Figured if he trusted you, that was enough."

    if kite_variant == "male":
        show kite_male neutral at li_center
        with dissolve
        p "You said you don't know how birthdays work."
        kite "I don't."
        kite "I never had the kind people make a big deal about."
    else:
        show kite_female neutral at center
        with dissolve
        p "Fourth attempt. You said not to ask about the other three."
        kite "Don't."
        kite "I never had the kind people make a big deal about."

    if kite_variant == "male":
        menu:
            "What do you mean?":
                kite "The birth date on my ID is fake."
                kite "My father... he had me hidden away. I don't know the real date."
                kite "So every year on March seventh, people text me happy birthday. And I smile and say thank you."
                kite "But it doesn't mean anything."

            "You don't have to explain.":
                kite "I want to."
                kite "The date on my ID is arbitrary. I don't know my real birthday."
                kite "My father hid me away when I was young. March seventh is just paperwork."

        kite "I wanted you to have something real tonight."
        kite "Because I know what it's like to have a day that should matter... and it doesn't."

    else:
        menu:
            "What do you mean?":
                kite "March seventh."
                kite "People text. I smile. I say thank you."
                kite "The date isn't real. My father had me hidden — I don't know when I was actually born."
                narrator "She says it the way you'd describe something you stopped being upset about a long time ago."
                kite "I didn't want you to have a night that doesn't mean anything."

            "You don't have to explain.":
                kite "I know."
                kite "March seventh on my ID. My father's paperwork, not mine."
                show kite_female tired at center
                narrator "She doesn't look at you when she says it. Sets a glass down instead."
                kite "I just didn't want tonight to be the same kind of nothing."

            "What does today mean to you then?":
                $ meter_bump("kite")
                narrator "She's quiet for a moment."
                kite "That I made you a drink I practiced. And you came when I asked."
                pause 0.5
                kite "That's enough for a day to count."

    narrator "[kite_subj!c] still can't whistle, after years of trying. It's the one thing about [kite_obj]self that [kite_subj] finds genuinely funny."

    if kite_variant == "male":
        show kite_male soft at li_center
        with dissolve
    else:
        show kite_female relaxed at center
        with dissolve

    if kite_variant == "male":
        kite "I don't do gifts."
        pause 0.3
        kite "But that stool is yours. And next year, if you come back, the drink will already be waiting."

        menu:
            "That's enough.":
                $ meter_bump("kite")
                narrator "Your hand rests on the stool back."
                kite "Yeah?"
                kite "Good. It's all I've got."

            "I'll hold you to that.":
                $ meter_bump("kite", 2)
                narrator "You tap the bar where a glass would sit."
                show kite_male soft at li_center, li_expression_beat
                kite "I hope you do."
    else:
        kite "I don't do gifts."
        pause 0.3
        kite "But that stool is yours."
        pause 0.5
        kite "Next year, if you come back — I already know what you drink."
        narrator "She stops. Something slips."
        kite "Forget that last part."

        menu:
            "That's enough.":
                $ meter_bump("kite")
                kite "Good."

            "I'll hold you to that.":
                $ meter_bump("kite", 2)
                kite "The last part or the stool?"

            "Both.":
                $ meter_bump("kite")
                narrator "Almost a smile. She turns back to the bottles."

    hide kite_male
    hide kite_female
    hide buddy
    with dissolve

    return


# =========================================================
# KITE - INTERACTION 2
# =========================================================

label kite_interaction_2:
    $ save_name = "You Came Back"
    $ kite_progress = 2
    $ play_story_music("kite_theme", fadeout=1.0, fadein=2.0, if_changed=True)
    $ play_story_ambience("bar_murmur", fadeout=0.8, fadein=1.0, if_changed=True)

    ## Room first. Nobody talking yet. Hide the leftover box from the first night.
    window hide
    scene bg bar_evening
    with fade

    ## Aug-8 denser: skip return-talk / birthday / lease corridor on DD slice.
    if kite_dd_slice:
        jump kite_interaction_2_dense

    narrator "You're back in The Copper Room."
    narrator "Staunton Street is not on the way to anything you need. You knew that was a lie."

    if kite_variant == "male":
        show kite_male neutral at li_center
        with dissolve

        kite "You came back."

        menu:
            "I was thirsty.":
                narrator "You reach for the empty glass still on the rail."
                kite "Plenty of bars closer to where you were."
                p "None with Buddy."
                kite "...Fair point."

            "I missed your cocktail.":
                $ meter_bump("kite")
                narrator "You pick up the napkin from night one. Still there."
                kite "You don't even know what I make yet."
                kite "But I'll take it."

            "I wanted to see you.":
                $ meter_bump("kite", 2)
                ## Jul-21 expression pass: the directness catches him off guard.
                narrator "You don't sit yet. He sets a glass down anyway."
                show kite_male soft at li_center, li_expression_beat
                kite "..."
                kite "Okay. Door's open."

        if persistent.corruption_tier >= 2:
            show kite_male stressed at li_center, li_flinch, corrupt_tier2
            ## Jul-22 P0: Remy mode cue before LI glitch.
            remy "{i}Return confirmed.{/i}"
            kite "..."
            kite "You came back."
            kite "..."
            kite "{glitch}I knew you would.{/glitch}"
            kite "..."
            kite "{stutter}W-why did I s-say that?{/stutter}"
            show kite_male stressed at li_center
            kite "I didn't know you would. I don't know anything."

        if persistent.corruption_tier >= 3:
            show kite_male stressed at li_center, glitch_flicker, corrupt_tier3
            with dissolve
            narrator "Kite's hand is shaking. He doesn't seem to notice."
            kite "..."
            kite "{stutter}I c-can't—{/stutter}"
            narrator "He reaches for a glass. Stops. Reaches again. Stops."
            kite "My hand won't."

        if birthday_choice == "kite":
            ## Jul-21: relief he's playing down — warm, still apron (relaxed is henley).
            show kite_male warm at li_center
            kite "You came back after your birthday."
            kite "Good. I was wondering if I scared you off with the sentimental bartender act."

            menu:
                "Not even close.":
                    $ meter_bump("kite")
                    narrator "You take the stool without asking."
                    kite "Good."

                "You were kind.":
                    narrator "You look at the bar top. Not at him."
                    show kite_male soft at li_center, li_look_away
                    kite "Don't spread that around."

        elif birthday_choice == "skip":
            show kite_male stressed at li_center
            kite "I texted you on your birthday."
            kite "You didn't answer."

            menu:
                "I just needed a quiet day.":
                    kite "That's fine. Not every year needs a flag on it."

                "I didn't feel like celebrating.":
                    kite "Yeah."
                    kite "Some birthdays are just a day."

                "I forgot about it, honestly.":
                    kite "Genuinely?"
                    kite "That's almost impressive."

        elif birthday_choice is not None:
            show kite_male stressed at li_center
            kite "I texted you on your birthday."
            kite "You didn't answer."

            menu:
                "I stayed in. Didn't feel like going out.":
                    kite "Sometimes that's the right choice."

                "I was with someone.":
                    show kite_male stressed at li_center, li_look_away
                    kite "Figured."
                    kite "Hope they were worth it."

                "It was just another day.":
                    kite "Fine."
                    kite "Fine is a word people use when they don't want to explain."

        show kite_male neutral at li_center
        kite "Your stool's open."

        narrator "You settle in. The Copper Room is quiet tonight."
        call kite_int1_echo

        show buddy neutral at buddy_center
        with dissolve

        kite "Buddy."
        show buddy neutral at buddy_center
        $ play_story_sfx("buddy_collar")
        $ play_story_sfx("dog_bark")
        narrator "Buddy lifts his head and thumps his tail once."
        kite "He remembers you."

        ## Aug-4 hang-law: hang before ECHO/lease dump.
        menu:
            "Scratch Buddy again.":
                $ play_story_sfx("buddy_collar")
                narrator "He settles under the stool like he's clocked in."
                kite "Don't let it go to your head."

            "Trace a finger along the copper rail.":
                narrator "Cool metal. Sticky in one spot. Lived-in."
                kite "Wipe it yourself next time. You're family rates now."

            "Watch the fridge light blink once.":
                narrator "Hum. Pause. Hum again. The bar keeps its own time."
                kite "It's older than the lease. Don't tell the landlord."

        hide buddy
        with dissolve

        $ play_story_sfx("glass_set")
        narrator "Same pour. No question."
        kite "Smart."

        kite "How's the app life? Still outsourcing your taste to algorithms?"

        menu:
            "Deleted it.":
                $ kite_int2_verb = "deleted"
                $ meter_bump("kite")
                narrator "You put the phone face-down on the bar."
                kite "Finally saw sense?"
                p "Finally saw sense."
                kite "Took you long enough."

            "Still trying.":
                $ kite_int2_verb = "trying"
                narrator "You leave the phone out. He wipes around it."
                kite "Good luck. The stool takes debriefs."

        narrator "[kite_name] wipes down the counter again."

        ## Aug-4: compress ECHO+lease résumé — hang already did the work.
        show kite_male tired at li_center, li_look_away
        kite "I tried Remy when I took over this place. They matched with the liquor license."
        kite "Lease is up in eight months. Landlord's been sniffing around."
        show kite_male tired at li_center
        kite "Belonging somewhere doesn't mean it belongs back."

        show kite_male neutral at li_center
        narrator "A loud group comes in. [kite_name] glances at them."

        kite "I gotta serve these people."
        kite "Stick around if you want."

        menu:
            "I'll come back.":
                $ meter_bump("kite", 2)
                kite "Okay."
                kite "Come early. Before the crowd."

            "I don't know when.":
                kite "Whenever."

        hide kite_male
        hide buddy
        with dissolve

    else:
        # Female variant (Kite)
        show kite_female neutral at center
        with dissolve

        kite "You found the place again."

        menu:
            "I was thirsty.":
                kite "There's room if you want it."

            "I missed your cocktail.":
                $ meter_bump("kite")
                kite "I poured you one the first night."
                kite "Sit. I'll do it again."

            "I wanted to see you.":
                $ meter_bump("kite", 2)
                ## Jul-21 expression pass: directness lands — guard drops a notch.
                show kite_female warm at center, li_expression_beat
                kite "..."
                kite "I'm here."

        if persistent.corruption_tier >= 2:
            show kite_female withdrawn at center, li_flinch, corrupt_tier2
            ## Jul-22 P0: Remy mode cue before LI glitch.
            remy "{i}Return confirmed.{/i}"
            kite "..."
            kite "You came back."
            narrator "She looks at you for a moment too long."
            kite "{glitch}I've been thinking about what you'd say when you did.{/glitch}"
            kite "..."
            kite "{stutter}I d-don't know why I said that.{/stutter}"
            show kite_female stressed at center
            kite "I was just... thinking."

        if persistent.corruption_tier >= 3:
            show kite_female withdrawn at center, glitch_flicker, corrupt_tier3
            with dissolve
            narrator "Kite's hand is shaking. She doesn't seem to notice."
            kite "..."
            kite "{stutter}I c-can't—{/stutter}"
            narrator "She reaches for a glass. Stops. Reaches again. Stops."
            kite "My hand won't."

        if birthday_choice == "kite":
            show kite_female relaxed at center
            kite "You came back after your birthday."
            kite "I wasn't sure you would."

            menu:
                "Of course I did.":
                    $ meter_bump("kite")
                    kite "Don't say it like it was obvious."
                    kite "It wasn't obvious to me."

                "You made it hard not to.":
                    kite "Good. I can be persuasive when I panic."

        elif birthday_choice == "skip":
            show kite_female stressed at center
            kite "I messaged you on your birthday."
            kite "I wasn't sure you'd want to hear from me."

            menu:
                "I just needed a quiet day.":
                    kite "That's fine. Quiet's on the menu too."

                "I didn't feel like celebrating.":
                    kite "Okay."
                    kite "Some days you need to be nowhere."

                "I saw it. I didn't know what to say back.":
                    kite "That's an answer, too."
                    kite "Just a slow one."

        elif birthday_choice is not None:
            show kite_female stressed at center
            kite "I messaged you on your birthday."
            kite "I wasn't sure you'd want to hear from me."

            menu:
                "I just stayed in.":
                    kite "Sometimes that's the only right choice."

                "I was out with someone.":
                    show kite_female withdrawn at center, li_look_away
                    kite "Figured."
                    narrator "She goes back to wiping down the counter."

                "It wasn't anything special.":
                    kite "Come back when you want one that is."

        show kite_female neutral at center
        kite "Your spot's still here."

        narrator "You settle in. The Copper Room is quiet tonight."
        call kite_int1_echo

        show buddy neutral at buddy_center
        with dissolve

        show kite_female relaxed at center
        kite "Buddy. Look who's here."
        narrator "Buddy lifts his head and wags his tail when he sees you."
        $ play_story_sfx("buddy_collar")

        kite "He's been waiting for you."
        narrator "She says it like she didn't mean to say it out loud."
        show kite_female neutral at center, li_look_away

        ## Aug-4 hang-law: hang before ECHO/lease dump.
        menu:
            "Scratch Buddy again.":
                $ play_story_sfx("buddy_collar")
                narrator "He settles under the stool like he's clocked in."
                kite "He remembers everyone. He doesn't wait for everyone."

            "Watch her wipe the glass.":
                narrator "Circle. Shine. Shelf. Repeat. The bar does half the talking."
                kite "I don't tell Buddy what to expect. He just knows."

            "Notice the sticky spot on the rail.":
                narrator "Someone's ring left a mark years ago. She doesn't sand it out."
                kite "Character. Or laziness. Jury's out."

        hide buddy
        with dissolve

        ## Aug-5 Block B: early toy — one dart (female Int2, same board).
        kite "Dartboard's free. One throw."
        menu:
            "One throw.":
                $ meter_bump("kite")
                call love32_story_dart
                $ kite_dart_result = "early"
                $ kite_dart_early = "threw"
                kite "Okay."
                kite "You're allowed back."

            "Maybe later.":
                $ kite_dart_result = "passed"
                $ kite_dart_early = "passed"
                kite "Fine. It isn't going anywhere."

        ## Aug-8 DD: early-dart memory before the quiet beat.
        if kite_dart_early == "threw":
            kite "You hit something true. Don't get used to compliments."
        elif kite_dart_early == "passed":
            kite "Board's still ugly. Your call stays on file."

        narrator "She doesn't ask about the app. She starts cleaning a glass instead."
        narrator "You wonder if she already knows."

        menu:
            "I deleted Remy.":
                $ kite_int2_verb = "deleted"
                $ meter_bump("kite")
                kite "Good."
                show kite_female tired at center
                narrator "She doesn't look up."

            "I've been on a few more dates.":
                $ kite_int2_verb = "dates"
                kite "Were any of them worth it?"
                narrator "Something in your expression answers before you do."
                kite "I figured."

        ## Aug-4: compress ECHO+lease.
        show kite_female withdrawn at center, li_look_away
        kite "I tried it once. Someone matched with the bar. Not me."
        kite "Lease is up in eight months. Landlord's been checking in."
        show kite_female tired at center
        kite "I keep waiting to find out if I'm losing another place I needed."

        show kite_female neutral at center

        narrator "A group pushes in from the street, loud and undecided."
        narrator "[kite_name] looks at them, then back at you."

        kite "I need to deal with these."
        narrator "She doesn't ask if you're staying. She moves toward them."
        narrator "You realize it's assumed."

        menu:
            "Stay and wait.":
                $ meter_bump("kite", 2)
                narrator "She glances back once. Doesn't say anything."
                narrator "You stay."

            "Head out.":
                narrator "She hasn't looked back."
                kite "Come back when it's quiet."
                kite "It's different then."

        hide kite_female
        hide buddy
        with dissolve

    call remy_commitment_check("kite")
    jump kite_warm_scene


label kite_interaction_2_dense:
    ## Aug-8: stool → Buddy → toy → one wound line → warm. No app interview.
    narrator "Back. Stool still open."

    if kite_variant == "male":
        show kite_male warm at li_center
        with dissolve
    else:
        show kite_female relaxed at center
        with dissolve

    show buddy neutral at buddy_center
    with dissolve
    $ play_story_sfx("buddy_collar")
    $ play_story_sfx("dog_bark")
    kite "Buddy. Look who."
    narrator "Buddy lifts his head, thumps his tail once, and settles again."

    menu:
        "Scratch Buddy. Harder this time.":
            $ kite_int2_verb = "scratch"
            $ play_story_sfx("buddy_collar")
            $ meter_bump("kite")
            narrator "He rolls. The bell on his collar clinks. Kite pretends not to watch."
            kite "Don't spoil him."

        "Wipe the sticky spot on the rail yourself.":
            $ kite_int2_verb = "rail"
            $ meter_bump("kite")
            narrator "You scrub. It's worse. Then better."
            kite "Family rates. Congrats."

        "Steal a clean glass and polish it wrong.":
            $ kite_int2_verb = "glass"
            $ play_story_sfx("glass_set")
            narrator "Circle. Smear. [kite_subj!c] takes it out of your hand."
            kite "Stop helping."

    hide buddy
    with dissolve

    call kite_int1_echo

    if kite_variant == "male":
        $ play_story_sfx("glass_set")
        narrator "Same pour. No question."
        kite "Smart."
    else:
        if kite_dart_early == "threw":
            kite "Board again. Or are you done showing off?"
            menu:
                "One more throw.":
                    call love32_story_dart
                    kite "Okay. Sit down before you get cocky."
                "Sit. Drink instead.":
                    $ play_story_sfx("glass_set")
                    narrator "Same pour. No question."
                    kite "Smart."
        else:
            kite "Dartboard's free. Prove something."
            menu:
                "One throw.":
                    $ meter_bump("kite")
                    call love32_story_dart
                    $ kite_dart_result = "early"
                    $ kite_dart_early = "threw"
                    kite "Not terrible."
                "Pass. Stool's enough.":
                    $ kite_dart_early = "passed"
                    kite "Chicken. Fine."

    if kite_variant == "male":
        show kite_male tired at li_center, li_look_away
    else:
        show kite_female tired at center, li_look_away
    kite "Lease is bad. Eight months. Don't make me explain it tonight."
    if kite_variant == "male":
        show kite_male soft at li_center
    else:
        show kite_female warm at center
    kite "Come early next time. Before the noise."

    hide kite_male
    hide kite_female
    with dissolve
    jump love32_between_nights


# =========================================================
# KITE - WARM SCENE (The Perfect Night)
# =========================================================
# This scene goes BEFORE the tragedy hits
# Earned happiness: Regulars, warm light, Buddy asleep, no crisis

label kite_warm_scene:
    $ save_name = "The Quiet Hour"
    $ kite_warm_seen = True
    $ play_story_music("kite_theme", fadeout=1.0, fadein=2.0, if_changed=True)
    $ play_story_ambience("bar_murmur", fadeout=0.8, fadein=1.0, if_changed=True)

    ## New Game uses the shorter quiet hour. Do not flash the unused night plate first.
    if kite_dd_slice:
        jump kite_warm_scene_dense

    scene bg bar_warm_night
    with fade

    narrator "Three nights later."
    narrator "You come early, like [kite_name] asked."

    scene bg bar_interior
    with dissolve

    narrator "The Copper Room changes before the crowd arrives."
    narrator "The heater blasts against the windows and the lights dim to a glow."
    narrator "Regulars occupy the corners. No one puts on a show."

    if kite_variant == "male":
        show kite_male warm at li_center
        with dissolve

        kite "You came early."
        kite "Good. The bar's honest for another hour."

        narrator "He nods toward the regulars."

        kite "The gentleman in the grey coat. He's been nursing the same Scotch for an hour."
        kite "The two women by the window. Tuesday tradition. They never miss it."
        kite "And..."

        show buddy neutral at buddy_center
        with dissolve
        narrator "Buddy sleeps on the floor behind the bar."

        kite "He's useless when it's quiet."
        kite "But he's happy."

        menu:
            "He knows how to relax.":
                $ meter_bump("kite")
                $ play_story_sfx("buddy_collar")
                narrator "You scratch Buddy's ear. He doesn't move."
                kite "You want his spot?"
                kite "On the floor behind the bar. It's warmer than it looks."

            "I like it when it's quiet like this.":
                $ meter_bump("kite", 2)
                narrator "You lean on the rail. Don't order."
                kite "Yeah."
                kite "Before the crowd shows up. Before anyone needs anything."
                kite "Just... people who already know what they want."

            "You should take a break sometime.":
                $ meter_bump("kite", 2)
                narrator "You take the towel from his side. He takes it back."
                $ play_story_sfx("glass_set")
                kite "I can't. I'm working."
                kite "...Maybe I should try it sometime."

    else:
        show kite_female relaxed at center
        with dissolve

        kite "You're early."
        kite "Smart. This is when the bar is actually good."

        narrator "She slides a drink across the counter without explanation."
        $ play_story_sfx("glass_set")

        kite "Same as the first night."
        kite "I make this for myself when it's slow."
        kite "Thought you might want one."

        menu:
            "You didn't have to.":
                kite "I know."
                kite "That's why I did."

            "Thank you.":
                kite "Don't thank me yet."
                kite "Try it first."

    narrator "The Regular."
    narrator "The drink [kite_name] made that first night."
    narrator "Bourbon, honey, ginger, and bitters."

    if kite_variant == "male":
        kite "I make this one different when it's just us."
        kite "More honey. Less bite."
        kite "The regulars want consistency."
        kite "You... I don't know what you want yet."

        $ meter_bump("kite", 2)
        p "I want this. The quiet version."
        kite "Yeah?"
        kite "Me too."

        narrator "He smiles, and this time it reaches his eyes."
        show kite_male warm at li_center
        with dissolve
        narrator "He stops playing the bartender. Just Kite remains."

    else:
        kite "I don't usually make this for people."
        kite "It's mine."
        pause 0.4
        kite "But you keep coming back."

        $ meter_bump("kite", 2)
        p "I'm honored."
        kite "Don't be."
        pause 0.3
        kite "Just drink it."

    call kite_int2_echo

    if kite_variant == "male":
        kite "Your turn."
        kite "Show me what you'd make."
        jump kite_warm_cocktail
    jump love32_between_nights


label kite_warm_scene_dense:
    ## Aug-8 denser warm: hang verb → cocktail. No regulars tour.
    window hide
    scene bg bar_interior
    with dissolve
    narrator "Early. Quiet hour. Buddy is already at the stools."

    if kite_variant == "male":
        show kite_male warm at li_center
        with dissolve
    else:
        show kite_female relaxed at center
        with dissolve
    show buddy neutral at buddy_center
    with dissolve

    kite "Honest hour. Start with your hands."
    call kite_int2_echo

    menu:
        "Sit on the floor next to Buddy.":
            $ meter_bump("kite")
            $ play_story_sfx("buddy_collar")
            narrator "Warm. Dog breath. Kite doesn't stop you."
            kite "His spot. Temporary lease."

        "Wipe three glasses without being asked.":
            $ meter_bump("kite")
            narrator "Circle. Shelf. [kite_subj!c] watches once, then pretends not to."
            kite "You're hired. Pay is tips Buddy doesn't want."

        "Set a clean glass on the counter.":
            $ play_story_sfx("glass_set")
            narrator "Kite turns it once, checking the rim."
            kite "That one. Keep it there."

    if kite_variant == "male":
        $ play_story_sfx("glass_set")
        kite "Bottles are there if you want them."
        jump kite_warm_cocktail
    jump love32_between_nights


label kite_warm_cocktail:
    ## Stay on the Copper Room warm plate. bar_counter_night was the weaker night twin.
    scene bg bar_interior
    with fade

    kite "Want to make one?"

    menu:
        "Yes.":
            if not persistent.minigame_cocktail_tutorial_seen:
                kite "Grab whatever pulls. The glass will tell you if you're wrong."
                $ persistent.minigame_cocktail_tutorial_seen = True

        "No.":
            $ kite_cocktail_result = None
            kite "Fine. I'll keep the dangerous bottles on my side."
            jump kite_warm_after_cocktail

    window hide
    $ reset_echo_cocktail_game()
    $ result_key, delta = renpy.call_screen("echo_cocktail_minigame", kite_variant=kite_variant, story_mode=True)
    $ persistent.minigame_cocktail_unlocked = True
    $ kite_cocktail_result = result_key
    ## Story pour: keep the meter quiet; Kite's line is the feedback.
    if delta:
        $ kite_meter += delta
    pause 0.25
    $ play_story_sfx("glass_set")
    $ reaction = get_cocktail_reaction_text(result_key, kite_variant)
    kite "[reaction]"

label kite_warm_after_cocktail:
    ## Aug-8 DD: cocktail choice changes the quiet-hour banter (not just meter).
    if kite_cocktail_result in ("balanced", "interesting"):
        kite "That one stays on the board. Quiet-hour special."
    elif kite_cocktail_result in ("messy_twice", "bitter_meaning"):
        kite "Messy. Honest. I'll remember the mess."
    elif kite_cocktail_result in ("safe", "old_fashioned_safe"):
        kite "Safe pour. I make those when I'm not sure yet."
    elif kite_cocktail_result:
        kite "Weird recipe. Weird's allowed here."

    if kite_dart_early == "threw":
        kite "And you already owed the board one. Tonight you paid the glass."
    elif kite_dart_early == "passed":
        kite "Still skipping darts. At least you showed up for the shaker."

    scene bg bar_interior
    with dissolve

    show buddy neutral at buddy_center
    with dissolve

    if kite_variant == "male":
        ## Jul-21 expression pass: the late-night confession is the route's
        ## first real exposure — soft, and the slip gets a look-away.
        show kite_male soft at li_center
        with dissolve
        kite "Someone to pour for."
        kite "That's... new."

        window hide
        menu:
            "I'll keep coming.":
                window auto
                $ meter_bump("kite", 2)
                show kite_male warm at li_center, li_expression_beat
                kite "Promise?"
                show kite_male soft at li_center, li_look_away
                kite "Sorry. That was-"
                p "I promise."

            "I can't promise that.":
                window auto
                kite "I know. Nobody can."
                kite "But you're here now. That's enough."

            "Only if you keep making mistakes like this.":
                window auto
                $ meter_bump("kite", 2)
                show kite_male warm at li_center, li_lean_in
                kite "The drink?"
                kite "Or who made it?"
                narrator "You say nothing. He does not ask again."

    else:
        show kite_female warm at center
        with dissolve

        narrator "She refills your glass without asking. Doesn't say anything for a moment."

        kite "This is my favourite hour."
        pause 0.5
        kite "Don't tell the regulars."

        menu:
            "I won't say a word.":
                $ meter_bump("kite")
                ## Jul-21: the narration says she looks away — so does she.
                show kite_female relaxed at center, li_look_away
                narrator "She almost smiles. Looks away first."

            "Why not?":
                kite "They'll all want it."
                kite "Then it won't be quiet anymore."

            "It's mine too, now.":
                $ meter_bump("kite", 2)
                narrator "She doesn't answer right away."
                show kite_female warm at center, li_expression_beat
                kite "Yeah."
                pause 0.4
                kite "Maybe it is."

    hide kite_male
    hide kite_female
    hide buddy
    with dissolve

    jump love32_between_nights


label kite_interaction_3:
    ## 2026-09-01: birthday moved to love32_between_nights after Int2.
    ## Male Int3 is a sleepover; Int4 is that morning. Do not return to
    ## the street hub in between.
    $ stop_story_music(fadeout=0.8)
    if kite_variant == "male":
        call kite_interaction_3_male
        jump kite_interaction_4
    else:
        call kite_interaction_3_female
        jump love32_between_nights


init python:
    def kite_derive_relationship_identity():
        """Phase 4 repair 2A. Descriptive Kite relationship identity, not a
        score: no value is better, none gates an ending, kite_meter is
        unchanged. Pure: reads Int1 opening + Int3 turn, returns one of
        leaned_in / chosen_slowly / warm_clear / unhurried, or None when a
        required input is missing (old saves, skipped route). No side effects.
        kite_int1_glass may be None (mix path with no result skips the glass
        menu); the opening then follows the stool alone."""
        stool = getattr(store, "kite_int1_stool", None)
        glass = getattr(store, "kite_int1_glass", None)
        stay = getattr(store, "kite_int3_stay", None)
        if stool not in ("sat", "stood") or stay is None:
            return None
        opening_guarded = (stool == "stood") or (glass in ("water", "pushed"))
        if getattr(store, "kite_variant", "male") == "male":
            kiss = getattr(store, "kite_int3_kiss", None)
            if kiss is None:
                return None
            turn_toward = (kiss == "yes") and (stay != "look")
        else:
            turn_toward = (stay == "stay")
        if turn_toward:
            return "chosen_slowly" if opening_guarded else "leaned_in"
        return "unhurried" if opening_guarded else "warm_clear"


label kite_interaction_4:
    $ stop_story_music(fadeout=0.8)
    ## Phase 4 repair 2A: derive once here (shared router; re-entry recomputes
    ## the same value because Int1/Int3 inputs are frozen by now).
    $ kite_relationship_identity = kite_derive_relationship_identity()
    if kite_variant == "male":
        call kite_interaction_4_male
    else:
        call kite_interaction_4_female
    jump love32_between_nights


label kite_interaction_3_male:
    $ save_name = "Smoke Break"
    $ kite_progress = 3
    $ stop_story_music(fadeout=0.8)
    $ play_story_ambience("title_day_roomtone", fadeout=0.8, fadein=1.0, if_changed=True, volume=0.42)

    scene bg bedroom_night
    with fade

    call phone_text("Kite", "Outside. You free?", accent="#8B5A3C")

    narrator "No context. That's the whole message."
    narrator "You go anyway."

    $ play_story_music("kite_theme", fadeout=1.0, fadein=2.0, if_changed=True)
    $ stop_story_ambience(fadeout=0.8)
    scene bg bar_exterior with fade

    # Cinematic opening - use Ren'Py's movie player directly so the clip appears
    # reliably before the static dialogue scene.
    if video_exists("videos/kite_smoking_scene.mp4"):
        $ play_cutscene("videos/kite_smoking_scene.mp4", 8.4)
    else:
        narrator "Kite stands on the wet street, smoke curling around his hand in the streetlight dark."

    # Video ends — now static background + sprite
    scene bg bar_exterior
    show kite_male smoking at li_center
    with dissolve

    p "I didn't know you smoked."

    kite "Yeah. Old habit."
    kite "Trying to quit."

    menu:
        "Can I have one?":
            kite "You don't smoke."
            kite "...Fine. But don't make it a habit."
            narrator "The smoke burns. You cough."
            kite "Told you."
            kite "Stick to bourbon. You're better at it."
            $ meter_bump("kite")

        "You should quit for real.":
            kite "When the bar's safe, maybe."
            kite "Right now it feels like counting days until I can."

        "I'll just sit with you.":
            kite "Suit yourself."
            kite "The stones are cold."

    ## Aug-24: alley first. Come inside (apron + hands) vs stay outside (henley).
    window hide
    menu:
        "Come inside.":
            ## Hide through the alley→bar dissolve. window auto first paints one empty box.
            window hide
            $ kite_came_inside_after_smoke = True
            $ play_story_music("kite_theme", fadeout=1.0, fadein=2.0, if_changed=True)
            $ play_story_ambience("bar_murmur", fadeout=0.8, fadein=1.0, if_changed=True)
            scene bg bar_interior
            show kite_male neutral at li_center
            with dissolve
            window auto
            kite "Your stool's open."
            kite "Want to make one?"
            menu:
                "Yes.":
                    window hide
                    if not persistent.minigame_cocktail_tutorial_seen:
                        kite "Grab whatever pulls. The glass will tell you if you're wrong."
                        $ persistent.minigame_cocktail_tutorial_seen = True
                    $ reset_echo_cocktail_game()
                    $ result_key, delta = renpy.call_screen("echo_cocktail_minigame", kite_variant=kite_variant, story_mode=True)
                    $ persistent.minigame_cocktail_unlocked = True
                    $ kite_cocktail_result = result_key
                    if delta > 0:
                        $ meter_bump("kite", delta)
                    else:
                        $ kite_meter += delta
                    $ reaction = get_cocktail_reaction_text(result_key, kite_variant)
                    kite "[reaction]"
                    scene bg bar_interior
                    show kite_male neutral at li_center
                    with dissolve

                "No.":
                    kite "Fine. I'll keep the dangerous bottles on my side."

        "Stay outside.":
            window auto
            $ kite_came_inside_after_smoke = False
            kite "Suit yourself."

    if let_down_li == "kite" or exploring_others:
        if kite_variant == "male":
            if kite_came_inside_after_smoke:
                ## He noticed. Stay in the apron. Do not cut the dark shirt into this bar beat.
                show kite_male stressed at li_center
            else:
                ## Still in the alley. Off duty. The dark shirt is allowed here.
                show kite_male withdrawn at li_center
        else:
            show kite_female withdrawn at center
        with dissolve
        kite "You've been busy."
        kite "That's fine."
        kite "I just noticed."
        menu:
            "I have been.":
                kite "Mm."
            "You noticed?":
                $ meter_bump("kite")
                kite "I notice most things."
                kite "I just don't usually say them."

    $ stop_story_music(fadeout=1.2)
    if kite_came_inside_after_smoke:
        ## Tax letters. Do not keep the welcome smile.
        show kite_male tired at li_center
    kite "They sent letters for two weeks. I didn't open them."
    kite "Bureau thinks I paid the wrong amounts. Not by a little."

    menu:
        "Shit.":
            kite "Yeah."
        "What do you need?":
            kite "Three months of invoices. I thought I had copies at my place."
        "Why didn't you open them?":
            kite "Because I thought I had it handled."
            kite "I was wrong."

    window hide
    menu:
        "Let's go to your place.":
            window auto
            kite "You don't have to."
            p "I know."
            kite "...Fine. Two blocks."
        "We should check the bar first.":
            window auto
            kite "I looked already. Nothing."
            kite "My place. Two blocks. If you're serious."
        "Two blocks. I can walk that far.":
            window auto
            kite "...Yeah. Two blocks."

    $ stop_story_music(fadeout=1.2)
    $ play_story_ambience("title_day_roomtone", fadeout=0.8, fadein=1.2, if_changed=True, volume=0.42)
    window hide
    scene bg street_night with fade
    show kite_male relaxed at li_center
    with dissolve
    window auto
    narrator "Two blocks. The street is wet and mostly empty."
    kite "This is it."

    ## Aug-23: male Int3 night at his place. Night plate already on disk.
    ## Do not use day kite_apartment here (letters / search / drink).
    scene bg player_apartment_night at bg_fill with dissolve
    show kite_male relaxed at li_center
    with dissolve

    ## Aug-24: arrival line matches the night living-room plate (no record player / mural).
    narrator "Open room. Warm lamps. A leather couch. The city through the glass."

    show buddy neutral at buddy_center
    with dissolve
    narrator "Buddy barrels past his legs and nearly trips you."

    kite "Buddy. Down."

    ## Aug-4 hang-law: apartment verbs before paper hunt.
    menu:
        "Pet Buddy / let him claim your shoes.":
            $ play_story_sfx("buddy_collar")
            $ meter_bump("kite")
            narrator "Buddy circles your ankles like rent is paid."
            kite "He decides who's allowed. You're in."

        "Flip through a book on the shelf.":
            narrator "Dust. A spine half-pulled. Something he hasn't opened in weeks."
            kite "Later. If we find the papers."

        "Check Remy once in the apartment light.":
            $ remy_phone_soft_open()
            show kite_male relaxed at li_center
            show buddy neutral at buddy_center
            with None
            kite "Phone. Fine. Then help me dig."

    ## Hunt names bedroom / closet / bed. Stay in the living room for the ask.
    ## Cut to bedroom_night after they pick — do not stand in the bedroom and walk into it.
    kite "Alright. Papers should be in the bedroom. Or the closet. Or under the bed. I don't know anymore."

    menu:
        "I'll check the bedroom.":
            scene bg bedroom_night with dissolve
            show kite_male relaxed at li_center
            narrator "You search the bedroom drawer. Old menus. Receipts from 2022. Nothing."
        "I'll take the coats.":
            scene bg bedroom_night with dissolve
            show kite_male relaxed at li_center
            narrator "You pull coats off the rack. A bag. Old books. Nothing."
        "Under the bed?":
            scene bg bedroom_night with dissolve
            show kite_male relaxed at li_center
            narrator "You pull out the box. Dusty napkins. A spare apron. Nothing."

    show buddy neutral at buddy_center
    with dissolve
    narrator "Thirty minutes. An hour. Kite's movements get sharper. He dumps everything onto the floor."

    kite "I know I kept them."

    ## Henley only at the apartment. tired is the apron — do not use it here.
    show kite_male relaxed at li_center
    with dissolve
    narrator "He kicks the box. It splinters. Buddy flinches."

    kite "They're not here."
    $ stop_story_music(fadeout=0.8)

    ## Couch + cabinet are the living room. bedroom_night has neither.
    scene bg player_apartment_night at bg_fill with dissolve
    show kite_male relaxed at li_center
    show buddy neutral at buddy_center
    with dissolve
    narrator "He sinks onto the couch. Puts his head in his hands."

    menu:
        "We'll find them.":
            kite "You don't know that."
            p "I know we're not stopping."
        "Hey. Stop.":
            narrator "He looks up. Surprised."
            p "Breaking things won't help."
            kite "Nothing's helping."
        "Come here.":
            narrator "You sit next to him. He tenses."
            kite "I don't need comfort."
            p "Too bad."

    menu:
        "Let's have a drink.":
            kite "Yeah. Okay."
        "Should we keep looking?":
            kite "I can't look anymore. Not tonight."
        "You need to calm down.":
            kite "I'm calm. I'm perfectly fucking calm."

    narrator "Kite goes to a cabinet. Tequila. Two shot glasses. Salt. Lime. He slices the lime."
    $ play_story_sfx("glass_set")

    kite "To this absolute disaster."

    narrator "Salt. Tequila. Lime. The first shot burns. By the third, his shoulders drop."
    show kite_male relaxed at li_center
    with dissolve

    kite "I always thought I was careful."
    kite "I'm a discrepancy."

    p "You're not a discrepancy."

    kite "No? What am I?"

    menu:
        "Someone who doesn't give up.":
            kite "I'm sitting here drinking tequila and feeling sorry for myself."
            p "Heroic would be giving up."
            narrator "He laughs. Surprised."
        "Someone who let me in.":
            narrator "He reaches out. Touches your hand."
            kite "I don't let people in."
            kite "There's a couch in the back nobody's allowed on. Customers ask, I tell them it's broken. It's not broken."
            p "You let Buddy in."
            kite "Buddy's a dog. He doesn't judge."
            p "I'm not judging."
        "My favorite bartender.":
            kite "...That's pathetic."
            p "It's true."
            narrator "He looks away. Almost smiles."

    ## Aug-24: tattoo / kiss on the night bedroom plate, not the living-room picture.
    scene bg bedroom_night with dissolve
    show kite_male relaxed at li_center

    narrator "Kite stands. His hand finds the henley at his left hip and stays there."

    kite "You want to hear something?"

    window hide
    menu:
        "Always.":
            window auto
            kite "Don't say that."
        "Is it a drink order?":
            window auto
            kite "It isn't."
        "Are you okay?":
            window auto
            kite "No. But listen anyway."

    narrator "He doesn't take the shirt off. Two fingers tap the cloth above his hip."

    # Shirt stays on. Do not play kite_tattoo_reveal / the tattoo mp4.
    # A Movie() there paints an empty video box. Words only. No replacement art.

    p "What's that?"

    kite "{font=fonts/HiraginoSansGB.ttc}勇{/font}. Courage."
    kite "I got it as a reminder."

    p "For what?"

    # Jul 5 fix (cold-read finding): birthday_beat fires at the top of this
    # same interaction, and if the player chose Kite for it, his birthday
    # scene already disclosed "my father hid me away" minutes ago — this
    # line used to re-disclose it cold, as if for the first time. Now it
    # only plays as a fresh reveal when the player genuinely hasn't heard
    # it yet (different birthday choice, or birthday_beat already spent on
    # an earlier route).
    if birthday_choice == "kite":
        kite "You know the part already. My father, sending me away."
        kite "This is the part after. What I did with it."
        kite "Reminds me that being scared and being brave are the same thing."
        kite "So... thanks, Dad."
    else:
        kite "My father sent me away when I was a kid."
        kite "I got this a few years ago."
        kite "Reminds me that being scared and being brave are the same thing."
        kite "So... thanks, Dad."

    kite "Hurt like hell, for the record. Whoever tells you the hip doesn't hurt is lying."

    menu:
        "I'm sorry.":
            kite "Don't. Pity's not a drink I stock."
        "It suits you.":
            narrator "He looks at you."
            kite "You don't know me."
            p "You keep letting me."
        "Can I touch it?":
            narrator "He nods."

    narrator "You cover his hand over the shirt. He breathes in sharp."

    kite "Don't look at me like that."

    p "Like what?"

    kite "Like I matter."

    window hide
    menu:
        "You do.":
            window auto
            $ kite_int3_stay = "matter"
            kite "Stop."
        "Like you owe me rent.":
            window auto
            $ kite_int3_stay = "rent"
            kite "Don't."
        "Look somewhere else.":
            window auto
            $ kite_int3_stay = "look"
            kite "I can't."

    kite "Can I kiss you?"

    menu:
        "Yes.":
            $ kite_int3_kiss = "yes"
            narrator "He kisses you. Rough at first. Then slower."
            kite "I don't bring people home."
            p "You brought me."
            kite "I know. That's the problem."
            narrator "He kisses you again. Buddy whines from the other room. Kite looks toward the door, then back at you."

            scene bg bedroom_night at bg_fill with dissolve
            narrator "Later, the room is quiet enough to hear Buddy settle outside."
            kite "You should sleep."
            p "So should you."
            kite "I don't sleep well."

            menu:
                "Stay a little longer.":
                    narrator "He tenses. Then relaxes. His head finds your shoulder."
                    show kite_male relaxed at li_center
                    with dissolve
                "Tell him to try.":
                    narrator "He closes his eyes. Within minutes, he's out."
                "Steal the pillow.":
                    narrator "He snorts. Then he moves closer."

        "No.":
            $ kite_int3_kiss = "no"
            kite "Okay."
            narrator "He lets his hand fall. You stay beside him until the tension leaves the room."
            kite "Thanks for being clear."


    $ remy_midroute_armed = True
    if kite_int3_kiss == "yes":
        $ remy_midroute_reason = "kite_kiss"
    elif kite_int3_stay:
        $ remy_midroute_reason = "kite_stay"
    else:
        $ remy_midroute_reason = "kite_private_night"

    $ kite_friendship += 1

    return


label kite_interaction_4_male:
    $ save_name = "The Real Invoice"
    $ kite_progress = 4
    $ stop_story_music(fadeout=0.8)
    $ play_story_ambience("title_day_roomtone", fadeout=0.8, fadein=1.0, if_changed=True, volume=0.42)
    ## Aug-23: Int4 morning. Day kite_apartment. Night plate stays on Int3.
    scene bg kite_apartment with fade

    "Morning. Coffee smell. Kite's talking to Buddy, two mugs already poured."

    "He comes over. Yesterday's pants. Same henley."

    show kite_male relaxed at li_center
    show buddy neutral at buddy_center
    with dissolve

    if kite_int3_stay == "matter":
        kite "You said I mattered last night. Coffee first. Argument later."
    elif kite_int3_stay == "rent":
        kite "You mentioned rent. Your share is carrying a box."
    elif kite_int3_stay == "look":
        kite "You told me to look somewhere else. Still working on it."

    ## Phase 4 repair 2A/2B: identity beat (Int4 male opener), director copy. Added after the
    ## Int3 callback; fallback adds nothing. Existing lines below play for everyone.
    if kite_relationship_identity == "leaned_in":
        # IDENTITY BEAT: leaned_in (Int4 male opener) — director copy (Repair 2B)
        narrator "Kite nudges your mug closer with [kite_pos] wrist."
        kite "You're getting comfortable here."
    elif kite_relationship_identity == "chosen_slowly":
        # IDENTITY BEAT: chosen_slowly (Int4 male opener) — director copy (Repair 2B)
        narrator "Kite looks at your mug, then at you."
        kite "You took your time. Then you stayed."
    elif kite_relationship_identity == "warm_clear":
        # IDENTITY BEAT: warm_clear (Int4 male opener) — director copy (Repair 2B)
        narrator "He taps the second mug once, then leaves it there."
        kite "You usually say what you mean."
    elif kite_relationship_identity == "unhurried":
        # IDENTITY BEAT: unhurried (Int4 male opener) — director copy (Repair 2B)
        narrator "He leaves the space between the two mugs alone."
        kite "We don't have to fill every silence."
    else:
        # IDENTITY FALLBACK: None / unset (Int4 male opener) — no extra beat
        pass

    menu:
        "Morning.":
            kite "Morning."
        "How's the hip.":
            kite "Sore. That's the point."
        "Did you sleep?":
            kite "Four hours. Normal for me."

    kite "Drink this. We're going to the bar."

    menu:
        "We should check the bar.":
            kite "I was too fried yesterday. Yeah."
        "You sure the invoices are there?":
            kite "No. But I didn't look properly."
        "Can we eat first?":
            kite "After. I need to know."

    window hide
    $ stop_story_music(fadeout=1.5)
    $ stop_story_ambience(fadeout=1.0)
    ## Aug-24: two-block walk. Henley until the bar. Apron on the bar plate.
    scene bg street_day with fade
    show kite_male relaxed at li_center
    with dissolve
    window auto
    narrator "Two blocks."
    scene bg bar_backroom with dissolve
    show kite_male tired at li_center
    with dissolve

    "The bar before service. Smaller. Dustier. Kite pulls the tax box off the shelf and tears through it for the third time this week."

    kite "They're not here."
    kite "They were never here."

    "He reaches for the lid. You look through the doorway into the bar instead."
    "Where would a man who writes his number on napkins keep paper that matters?"

    ## Aug-24: hunt on the floor plate. Name what that plate shows.
    scene bg bar_interior with dissolve
    show kite_male tired at li_center

    # Jul 4 agency fix: the route's plot climax used to resolve entirely by
    # Kite ("You sort together. Fifteen minutes in, Kite freezes.") while the
    # player watched. Now the PLAYER finds January. All three picks succeed
    # with different texture — the agency is being the finder, not a puzzle.
    menu:
        "Check the supplier binder behind the bar.":
            "Laminated pages, tacky with syrup. Between a rum price list and a complaint about a broken pump: a yellow carbon copy."
            p "Kite. January."

        "Check under the bar.":
            "Bottle openers. Dead pens. A dog treat, ancient. Folded into a warped booklet: a yellow carbon copy."
            p "Kite. January."

        "Check the shift rotas on the wall.":
            "Three layers of shift rotas, shoved behind the last frame. Under the last one: a yellow carbon copy, soft at the edges."
            p "Kite. January."

    "His head comes around slowly, like the words might change if he moves too fast."

    kite "...That's my handwriting on the corner."
    kite "I paid it. I {i}paid{/i} it."

    "He takes it with both hands. Then he's tearing through the same spot you found it on."

    if video_exists("videos/kite_invoice_discovery.mp4"):
        $ play_cutscene("videos/kite_invoice_discovery.mp4", 15.0)
        window auto
        scene bg bar_interior
        show kite_male tired at li_center
        with dissolve

    kite "February. March."
    kite "All three. They're all here."

    $ play_story_music("kite_theme", fadeout=1.0, fadein=2.0, if_changed=True)
    "He stares at them. Laughs — loud, relieved."

    menu:
        "I knew it.":
            $ kite_int4_response = "knew"
            kite "You didn't know. You just didn't quit."
        "Now you fight back.":
            $ kite_int4_response = "fight"
            kite "Yeah. I'm going to bury them."
        "We should celebrate.":
            $ kite_int4_response = "celebrate"
            "He grins."
            kite "Yeah. We should."

    "He pulls you into a hug."

    kite "We did it. We actually fucking did it."

    kite "Breakfast. I'm starving. It's on me."

    window hide
    menu:
        "You pick.":
            window auto
            kite "Fine. I know a place."
        "Pancakes.":
            window auto
            kite "Pancakes. Yeah."
        "You're paying? I'm ordering everything.":
            window auto
            "He almost smiles."
            kite "Order everything. I don't care."

    kite "Let's get out of here."

    $ kite_friendship += 1

    return


# =========================================================
# KITE - INTERACTION 5
# =========================================================

label kite_interaction_5:
    $ play_story_music("kite_theme", fadeout=1.0, fadein=2.0, if_changed=True)
    $ kite_int5_stayed = False
    if kite_variant == "male":
        call kite_interaction_5_male
    else:
        call kite_interaction_5_female
    jump love32_between_nights


# ---------------------------------------------------------
# KITE - INTERACTION 5 (MALE)
# ---------------------------------------------------------

label kite_interaction_5_male:
    $ save_name = "What Arrived"
    $ kite_progress = 5
    $ play_story_music("kite_theme", fadeout=1.0, fadein=2.0, if_changed=True)
    $ play_story_ambience("bar_murmur", fadeout=0.8, fadein=1.0, if_changed=True)

    ## Aug-24: approach is outside. Crash, then the night bar plate.
    scene bg bar_exterior
    with fade

    $ stop_story_music(fadeout=1.2)
    narrator "The street is wet. You hear a crash from The Copper Room."

    # Glass shatter cinematic (Int 5)
    if video_exists("videos/kite_glass_shatter.mp4"):
        $ play_cutscene("videos/kite_glass_shatter.mp4", 3.0)
    else:
        $ play_story_sfx("glass_shatter")
        show black with fade
        narrator "The sharp sound of glass breaking against wood."

    scene bg bar_night
    with fade

    # 2026-07-12 gesture pilot: crossed-arms replaces the plain "angry" bust
    # for this guarded stretch -- see kite_male crossed_arms definition
    # above.
    show kite_male crossed_arms at li_center
    with dissolve

    if kite_int4_response == "knew":
        kite "You said you knew we'd find it. I keep trying to borrow that certainty."
    elif kite_int4_response == "fight":
        kite "You said fight back. I was ready for paperwork. This is different."
    elif kite_int4_response == "celebrate":
        kite "You said celebrate. Apparently whoever sent this missed the invitation."

    narrator "Kite is standing behind the bar. He doesn't say anything when you come in."
    show buddy neutral at buddy_center
    with dissolve
    narrator "Buddy is by the wall. He doesn't move."

    menu:
        "Hey, Buddy.":
            $ play_story_sfx("buddy_collar")
            narrator "Buddy keeps his head down, watching Kite instead of you."
            kite "Leave him. He can tell when I'm pissed. He's not stupid."

        "Kite?":
            kite "Yeah. I'm here. Unfortunately."

        "What happened?":
            pass

    kite "Someone sent me this."

    call screen email_message(sender="Verrerie Accounts", subject="", body="You think this is over? I'm always watching.")

    show kite_male crossed_arms at li_center
    with dissolve

    kite "Got it ten minutes ago. Knocked a glass off the bar when I read it."
    kite "Bar's been closed while I sent the copies. Tomorrow we open."
    kite "That's not random."
    kite "The sender name was a joke. 'Verrerie Accounts.'"
    kite "My father's company used to put that word on everything."

    menu:
        "The accuser?":
            kite "Maybe. Still bitter. Wants the last word."

        "Verrerie?":
            kite "Maybe."
            kite "Or someone knows enough to make me look in that direction."

        "What are you going to do?":
            kite "Open tomorrow. That's what I'm going to do. I don't care who sent this."

    "Buddy stays by the wall. Kite still doesn't look at him."

    kite "I built this place by myself. When the letters came, I handled that by myself too."
    "He stops. Looks at you."
    pause 0.4
    # 2026-07-12 gesture pilot: arms uncross here -- the visual thaw lands
    # on the same beat as the emotional one, instead of the guarded pose
    # holding through his own admission that he's not alone in this.
    show kite_male gentle at li_center
    with dissolve
    $ play_story_music("kite_theme", fadeout=1.0, fadein=2.0, if_changed=True)
    kite "But you're here. So I'm not."
    kite "Thanks for that."

    # Jul 4 audit fix: corruption-tier blocks were copy-pasted verbatim
    # across the male/female variants (identical except pronoun swaps).
    # "The Regular" and "I'm not real" stay as Remy's recurring signature —
    # that repetition is correct horror design — but each variant now
    # anchors the intrusion to what just happened in ITS OWN scene, so the
    # corruption reads as her reacting to this moment, not a reused insert.
    if persistent.corruption_tier >= 2 and not kite_dd_slice:
        ## Jul-22 P0: Remy mode cue — "The Regular" is her fingerprint.
        remy "{i}The Regular.{/i}"
        kite "..."
        kite "The Regular."
        kite "..."
        kite "I haven't poured anything since the glass broke. I can taste it anyway."
        kite "In my mouth. Right now."
        kite "..."
        kite "What's happening to me?"

    if persistent.corruption_tier >= 3:
        show kite_male stressed at li_center, glitch_flicker, corrupt_tier3
        with dissolve
        kite "{glitch}I'M NOT REAL.{/glitch}"
        kite "..."
        kite "I didn't—"
        kite "..."
        kite "{stutter}I d-didn't say that.{/stutter}"
        narrator "Kite looks at his own hands like they belong to someone else."
        kite "Who's saying these things?"
        kite "..."
        kite "The email said 'watching.' So did whatever just said that in my own voice."
        show kite_male crossed_arms at li_center
        with dissolve

    window hide
    menu:
        "I can stay and help tonight.":
            window auto
            $ kite_int5_help = "stay"
            $ meter_bump("kite", 2)
            kite "Good. Because I wasn't asking you to leave."
            kite "Now help me sweep up that glass."
            $ play_story_sfx("glass_set")
            window hide
            menu:
                "Sweep it.":
                    window auto
                    $ play_story_sfx("glass_set")
                    ## Painted gray bin sits left behind the bar on bar_night.
                    ## Center bartender covers it — step aside, then restore.
                    ## Keep an expression tag (bare show kite_male is fragile).
                    show kite_male gentle at li_right
                    with dissolve
                    narrator "You sweep the glass into the bin. He watches once, then pretends not to."
                    show kite_male gentle at li_center
                    with dissolve

                "Pour the next one.":
                    window hide
                    if not persistent.minigame_cocktail_tutorial_seen:
                        kite "Grab whatever pulls. The glass will tell you if you're wrong."
                        $ persistent.minigame_cocktail_tutorial_seen = True
                    $ reset_echo_cocktail_game()
                    $ result_key, delta = renpy.call_screen("echo_cocktail_minigame", kite_variant=kite_variant, story_mode=True)
                    $ persistent.minigame_cocktail_unlocked = True
                    $ kite_cocktail_result = result_key
                    if delta > 0:
                        $ meter_bump("kite", delta)
                    else:
                        $ kite_meter += delta
                    $ reaction = get_cocktail_reaction_text(result_key, kite_variant)
                    kite "[reaction]"
            jump kite_route_lockin

        "I need time.":
            window auto
            $ kite_int5_help = "time"
            $ stop_story_music(fadeout=1.2)
            ## He asked for time. Do not keep the gentle smile on a refusal.
            show kite_male stressed at li_center
            kite "You have it."
            kite "But if you figure out who sent that email, let me know. I want to break their nose."
            hide buddy
            return


# ---------------------------------------------------------
# KITE - INTERACTION 5 (FEMALE)
# ---------------------------------------------------------

label kite_interaction_5_female:
    $ save_name = "What Arrived"
    $ kite_progress = 5
    $ play_story_ambience("bar_murmur", fadeout=0.8, fadein=1.0, if_changed=True)

    scene bg bar_evening
    with fade

    # Atmospheric loop — bar interior
    if video_exists("videos/bar_interior_loop.mp4"):
        show bar_interior_loop at bg_fill behind kite_female

    narrator "The Copper Room is closed for tomorrow's reopening. Kite is restocking glasses. She moves slower than usual."

    show kite_female tired at center
    with dissolve

    if kite_int4_response == "earned":
        kite "You called the appeal a win. I'm still deciding if I believe you."
    elif kite_int4_response == "regret":
        kite "You told me to make them regret it. I sent the side-by-side twice."
    elif kite_int4_response == "breathe":
        kite "You made me stop for one breath before I hit send. I remembered today."

    kite "You're early."

    menu:
        "You look tired.":
            kite "I am. I don't sleep well before openings. Or reopenings. Or Tuesdays."

        "Need help?":
            kite "You can wipe glasses. I'm on my last nerve and I don't trust myself not to drop one."

        "Hey, Buddy.":
            show buddy neutral at buddy_center
            with dissolve
            "Buddy is asleep at Kite's feet. He doesn't wake up."
            kite "He hasn't left my side all day. I think he knows I'm nervous."
            kite "Either that or he smells the ham I dropped behind the bar."

    "Kite puts down a glass. Looks at the door."

    kite "I sent the appeal. They cleared us. Tomorrow we reopen."
    kite "And I keep thinking — what if I open the doors and nobody walks through them?"
    kite "Not because of the scandal. Just because... they forgot."
    kite "The complaint came through a shell account. Display name said 'Verrerie Public.'"
    kite "Could be nothing. Could be someone using a word they knew would make me stupid."
    kite "I hate that it worked."

    menu:
        "They didn't forget.":
            kite "You don't know that."
            p "I know I didn't."
            "She looks at you."
            kite "That's one person. I need more than one person to run a bar."

        "Then give them a reason to come.":
            kite "I thought I did. For five years."
            pause 0.4
            kite "Maybe I need to try something different."

        "Sounds like you need a break.":
            kite "I don't take breaks. That's the problem."

    "She reaches for a glass on the shelf. Her sleeve catches the one next to it. It tips. She catches it without looking — one smooth motion. Then she stares at her hand."

    kite "See? Last nerve."

    # Jul 4 audit fix: see the parallel comment in the male branch above —
    # same principle, this scene's own anchors (the shell-account complaint,
    # the catch-without-looking reflex) instead of copy-pasted filler.
    if persistent.corruption_tier >= 2 and not kite_dd_slice:
        ## Jul-22 P0: Remy mode cue — "The Regular" is her fingerprint.
        remy "{i}The Regular.{/i}"
        kite "..."
        kite "The Regular."
        kite "..."
        kite "My hands are still full of glasses I haven't set down. I can taste it anyway."
        kite "In my mouth. Right now."
        kite "..."
        kite "What's happening to me?"

    if persistent.corruption_tier >= 3:
        show kite_female withdrawn at center, glitch_flicker, corrupt_tier3
        with dissolve
        kite "{glitch}I'M NOT REAL.{/glitch}"
        kite "..."
        kite "I didn't—"
        kite "..."
        kite "{stutter}I d-didn't say that.{/stutter}"
        narrator "Kite looks at her own hands like they belong to someone else."
        kite "Who's saying these things?"
        kite "..."
        kite "'Verrerie Public.' That's not a person. That's not anyone. Then why did it sound like someone?"
        show kite_female neutral at center
        with dissolve

    "She picks up another glass. Puts it down without cleaning it."

    kite "I'm not asking you to save me. I'm not in danger."
    kite "I just hate realizing how fast a place can stop feeling like shelter."
    kite "I'm just saying... if you're free tomorrow. And the day after. And possibly the day after that."
    "She looks at you."
    kite "I'd like the company."

    window hide
    menu:
        "I can stay and help tonight.":
            window auto
            $ kite_int5_help = "stay"
            $ meter_bump("kite")
            "She smiles. Small. Real."
            kite "Okay. Then help me wipe these glasses. My hands are still shaking."
            jump kite_route_lockin

        "I need time.":
            window auto
            $ kite_int5_help = "time"
            kite "You have it. All of it."
            kite "But the door's unlocked when you decide."
            hide buddy
            return


label kite_route_lockin:
    $ kite_int5_stayed = True
    $ save_name = "Stay"

    # Theme already entered at Int1. if_changed keeps the lock-in from restarting it.
    $ play_story_music("kite_theme", fadeout=1.0, fadein=2.5, if_changed=True)

    ## Aug-24: male stay is still the night-before plate. Female keeps her evening plate.
    if kite_variant == "male":
        scene bg bar_night
        show kite_male stressed at li_center
    else:
        scene bg bar_evening
        show kite_female stressed at center
    with dissolve

    if kite_variant == "male":
        kite "Okay. Grab the dustpan."
    else:
        kite "Okay. Take the clean cloths."

    show buddy neutral at buddy_center
    with dissolve
    $ play_story_sfx("buddy_collar")
    narrator "Buddy noses the broom toward your shoe."

    call kite_int5_echo

    if kite_variant == "male":
        kite "Thanks. For tonight."
    else:
        kite "You were useful. Don't look pleased with yourself."

    ## Phase 4 repair 2B: lock-in kiss-ask identity line, immediately before
    ## the (unchanged, shared) ask. Yes/No menu and outcomes are unchanged.
    if kite_relationship_identity in ("leaned_in", "chosen_slowly"):
        # IDENTITY BEAT: turn toward (lock-in kiss ask) — director copy (Repair 2B)
        kite "I think I know. I still want to ask."
    elif kite_relationship_identity in ("warm_clear", "unhurried"):
        # IDENTITY BEAT: measured turn (lock-in kiss ask) — director copy (Repair 2B)
        kite "I'm asking. I'm not assuming."
    else:
        # IDENTITY FALLBACK: None / unset (lock-in kiss ask) — no extra line
        pass

    kite "Can I kiss you?"

    menu:
        "Yes.":
            if kite_variant == "male":
                narrator "He leans across the bar and kisses you."
                narrator "Bourbon and relief. Brief, careful, real."
            else:
                narrator "She closes the distance and kisses you."
                narrator "Warm, direct, and over before either of you can overthink it."
            kite "Okay."

        "No.":
            if kite_variant == "male":
                kite "All right. Thanks for saying it."
            else:
                kite "Good. Clear is easy."

    kite "Help me finish the floor, then go get some sleep."

    hide kite_male
    hide kite_female
    hide buddy
    with dissolve

    return



# =========================================================
# KITE - INTERACTION 3 (FEMALE)
# =========================================================

label kite_interaction_3_female:
    $ save_name = "The Dartboard"
    $ kite_progress = 3

    scene bg bedroom_night
    with fade

    call phone_text("Kite", "Closed tonight. Back door's open if you feel like company.", accent="#8B5A3C")

    narrator "Not a question. Not an invitation exactly."
    narrator "You go anyway."

    scene bg bar_night with dissolve

    "The front door is locked. Closed sign up."
    "But the back door is propped open — maybe for air. You hear something from inside."

    "Thunk. Thunk."

    "You walk in. The bar is dark. No music. Chairs up."

    # Dart throw cinematic (Female Int 3)
    if video_exists("videos/kite_dart_scene.mp4"):
        $ play_cutscene("videos/kite_dart_scene.mp4", 4.0)
        scene bg bar_night
    else:
        narrator "Kite is at the back wall, throwing darts. Same board. She doesn't turn around."

    show kite_female neutral at center
    with dissolve

    p "You're on that board again."

    kite "Yeah."
    kite "It's still not for customers."

    p "Who's it for?"

    kite "Me."
    narrator "She lines up another throw. Releases it. Thunk."
    kite "When I took over, the previous owner left it. I almost threw it out."
    kite "Now it's... the only thing in this place that doesn't need me to fix it."
    kite "You just throw. It either hits or it doesn't."

    menu:
        "Can I try?":
            kite "You sure?"
            kite "I'm not great company right now. But I'm worse when I'm not doing something with my hands."
            $ meter_bump("kite")

        "You're good at this.":
            kite "I'm consistent. Not the same thing."
            kite "Same spot every time. Control. Not skill."

        "Does it help?":
            kite "For about thirty seconds after each throw."
            narrator "[kite_subj!c] reaches for another dart."
            kite "Then I reach for another one."

    if kite_variant == "male":
        show kite_male stressed at li_center
    else:
        show kite_female stressed at center
    with dissolve

    kite "Something happened."
    narrator "[kite_subj!c] turns to face you. First time since you walked in."
    kite "I need one throw before I can talk about it."
    kite "Want one too?"

    menu:
        "Yes. One throw.":
            call love32_story_dart
            if dart_hits and dart_hits[-1][3] >= 42:
                $ kite_dart_result = "clean"
                $ meter_bump("kite")
            elif dart_hits and dart_hits[-1][3] > 0:
                $ kite_dart_result = "hit"
            else:
                $ kite_dart_result = "miss"
            narrator "The dart settles in the board. Kite watches it stop moving."

        "No.":
            $ kite_dart_result = "passed"
            kite "Fine. Just let me take mine."
            narrator "Her dart lands with a dry thunk. She watches it stop moving."

    if kite_variant == "male":
        show kite_male neutral at li_center
    else:
        show kite_female neutral at center
    with dissolve

    kite "Huh."

    menu:
        "You're getting better.":
            kite "I'm just not shaking anymore."

        "Feel better?":
            ## Aug-4: joke over soft-diagnosis.
            kite "I feel like I hit something. That's close enough."

        "Again?":
            kite "No. I need to think now."

    "[kite_subj!c] sits on the edge of a table. You sit across from [kite_obj]."

    ## Aug-4 hang-law: one more room verb after darts, before rat-phone dump.
    menu:
        "Pull a stool over the wrong way and sit.":
            $ meter_bump("kite")
            narrator "You sit backwards on it. She almost smiles."
            kite "Customers aren't allowed to do that."

        "Pick up a dart she left on the board.":
            narrator "Plastic wrap still on half the board. Sticky from someone else's night."
            kite "Leave it. I need my hands free."

        "Check Remy once — face away from her phone.":
            $ remy_phone_soft_open()
            if kite_variant == "male":
                show kite_male neutral at li_center
            else:
                show kite_female neutral at center
            with None
            kite "Yours, not mine. Good."

    if let_down_li == "kite" or exploring_others:
        if kite_variant == "male":
            show kite_male withdrawn at li_center
        else:
            show kite_female withdrawn at center
        with dissolve
        kite "You've had a lot going on."
        kite "So have I."
        menu:
            "You could say that.":
                kite "Mm."
                kite "Me too."
            "Is it that obvious?":
                $ meter_bump("kite")
                kite "To me."
                kite "I'm usually right."

    p "Okay. What happened?"

    "[kite_subj!c] pulls out [kite_pos] phone. Turns it toward you."

    kite "Someone posted this in a food group. It went viral. Health department saw it. Shut me down."

    "The photo: the bar floor. Two rats on the tiles. Familiar space. In the background, customers still drinking."

    kite "That's my bar. My floor. My stools. But look at the timestamp."
    kite "People don't remember the cocktails after something like this."
    kite "They remember the rats."
    kite "One image, and suddenly every glass I ever washed looks dirty."

    "She zooms in. Bottom corner: 3:25 AM."

    kite "That night was quiet. I closed at two. I remember because it was dead and I was tired and I just wanted to go home."
    kite "This says 3:25. With customers still inside. That didn't happen."

    menu:
        "So the timestamp is wrong.":
            kite "Or the whole thing is. I don't know. I keep staring at it, wondering if I missed something."

        "You were there. You know.":
            kite "I know. But my word against a photo doesn't win appeals."

        "Who would do this?":
            kite "I don't know. I honestly have no clue."

    "She hands you the phone. You look at the photo together."

    kite "I need to pull the CCTV. Check the timestamp against the register."
    kite "But I don't even know where to start. I just... I can't look at it anymore."

    "She walks behind the bar. Pulls out tequila and two shot glasses. Pours."

    kite "I don't say thank you well. But thank you. For showing up when the door was open."

    "You clink. It goes down smooth."

    kite "My name isn't in any of the Verrerie records."
    kite "My mother helped build that company. Fifteen years."
    kite "He made sure she couldn't prove it."

    p "So you built something they can't erase."

    kite "I tried."
    kite "And then someone points a camera at the floor and suddenly I'm back to proving I exist."

    narrator "She looks at the empty shot glass."

    kite "I'm not going to let a fake photo be the thing that decides what this place is."
    kite "I just... needed to say that out loud."

    kite "I'll pull the CCTV tonight. Figure out the rest."
    kite "I'll let you know when there's something to look at."

    menu:
        "I'll wait.":
            $ kite_int3_stay = "wait"
            kite "You don't have to."
            p "I know."

        "Let me know when you're ready.":
            $ kite_int3_stay = "ready"
            kite "I will."

        "Want me to stay?":
            $ kite_int3_stay = "stay"
            kite "Sure. But I don't know when I'll be done."
            "You stay. She finishes her drink. Doesn't say much. Doesn't need to."

    $ remy_midroute_armed = True
    if kite_int3_stay == "stay":
        $ remy_midroute_reason = "kite_stay"
    elif kite_int3_stay:
        $ remy_midroute_reason = "kite_wait"
    else:
        $ remy_midroute_reason = "kite_private_night"

    $ kite_friendship += 1

    hide kite_female
    with dissolve

    return


# =========================================================
# KITE - INTERACTION 4 (FEMALE)
# =========================================================

label kite_interaction_4_female:
    $ save_name = "Paper Storm"
    $ kite_progress = 4
    $ play_story_ambience("bar_murmur", fadeout=0.8, fadein=1.0, if_changed=True)
    window auto
    scene bg bar_backroom with dissolve

    "Your phone buzzes."

    "Kite: I'm at the bar. Back door's open. Come when you can."

    show kite_female neutral at center
    with dissolve

    kite "You came."

    if kite_int3_stay == "wait":
        kite "You said you'd wait. I tried not to make that mean anything."
    elif kite_int3_stay == "ready":
        kite "I said I'd tell you when I was ready. This is as close as I get."
    elif kite_int3_stay == "stay":
        kite "You stayed while I pulled the CCTV. I noticed."

    ## Phase 4 repair 2A/2B: identity beat (Int4 female opener), director copy. Added after the
    ## Int3 callback; fallback adds nothing. Existing lines below play for everyone.
    if kite_relationship_identity == "leaned_in":
        # IDENTITY BEAT: leaned_in (Int4 female opener) — director copy (Repair 2B)
        narrator "She makes room beside her without looking up."
        kite "Come here. You're already part of this."
    elif kite_relationship_identity == "chosen_slowly":
        # IDENTITY BEAT: chosen_slowly (Int4 female opener) — director copy (Repair 2B)
        narrator "She waits until you're beside her."
        kite "You gave me room. Then you stayed."
    elif kite_relationship_identity == "warm_clear":
        # IDENTITY BEAT: warm_clear (Int4 female opener) — director copy (Repair 2B)
        narrator "She points to the chair beside her."
        kite "You make asking easy."
    elif kite_relationship_identity == "unhurried":
        # IDENTITY BEAT: unhurried (Int4 female opener) — director copy (Repair 2B)
        narrator "She leaves the chair beside her open."
        kite "Take your time. I will."
    else:
        # IDENTITY FALLBACK: None / unset (Int4 female opener) — no extra beat
        pass

    "She has everything now. The fake photo taped to the wall. CCTV on the laptop — 3:25 AM, empty bar, locked door."

    kite "I wrote the appeal. Timestamp mismatch. Lighting discrepancy."
    kite "I want to go through it once more before I send it. Look at this with me."

    menu:
        "It looks solid.":
            kite "I think so too. But I want to be sure."

        "What if they don't believe you?":
            kite "Then I need to be absolutely sure. Tell me if you see anything I missed."

        "Let me look at their photo again.":
            kite "Sure."

    "She hands you the phone with the health department's photo."

    show evidence fake_rat_photo at truecenter
    with dissolve

    "You're looking at the rats, the customers at the bar, the man with his hand in the air. The timestamp. And then —"

    show evidence fake_rat_photo:
        subpixel True
        ease 1.5 crop (1000, 50, 600, 338)

    pause 0.5

    p "Wait. Look at this hand."

    kite "What about it?"

    p "That man at the bar. His hand. Count the fingers."

    "She takes the phone. Zooms in closer."

    kite "One... two... three... four."
    kite "That's not right."

    # 2026-07-12 fix: options 2/3 used to have the PLAYER ask Kite to
    # explain the anomaly the player themselves had just pointed out two
    # lines earlier ("Count the fingers") — a backward non-choice. Rewritten
    # as three genuine reactions to the same discovery instead.
    menu:
        "We can go public with this.":
            p "We can go public with this."
            kite "That's the plan. But I want to be sure first."

        "That's not a real hand.":
            p "That's not a real hand."
            kite "...No. No, it's not."

        "Someone built this on purpose.":
            p "Someone built this on purpose."
            kite "Yeah. Someone sat down and did this. To me."

    p "AI image generators do that. Merge fingers. This isn't a real photo — it's generated."

    "She stares at the screen. Her breath catches."

    kite "Oh my god."
    kite "I was so busy looking at the rats I didn't even look at the people."

    "She looks at you. The panic is gone. Something colder, clearer."

    kite "Someone sat down and made a photo of rats in my bar."
    kite "And I can prove it. Not with my word. Not with my CCTV. Their own evidence has a four-fingered hand in it."
    kite "They wanted me scrubbing shame off the floor while everyone watched."
    kite "I'm not giving them that."

    # 2026-07-12 density pass: this scene ran the reveal, the vindication,
    # the appeal send, AND the tonal pivot into a dinner invitation — a full
    # scene change to the restaurant — with zero player input between the
    # "count the fingers" menu above and the "you look beautiful" menu at
    # the restaurant. One reaction beat at the vindication moment, same
    # flavor-branch/converge idiom used throughout this file.
    menu:
        "You earned this one.":
            $ kite_int4_response = "earned"
            $ meter_bump("kite")
            kite "Maybe."
            kite "Feels less like earning something and more like not losing, for once."

        "Make them regret it.":
            $ kite_int4_response = "regret"
            kite "That's the plan."

        "Just breathe for a second.":
            $ kite_int4_response = "breathe"
            kite "..."
            kite "Yeah. Okay. One second."

    "She pulls up the appeal document. Adds a new paragraph. Fast."

    kite "I can email this tonight. If they don't reopen the investigation, I'll post the side-by-side publicly."
    kite "The CCTV and timestamp are backup. This is the case."

    "She hits send. Closes the laptop."

    kite "I don't know how to thank you."
    kite "I don't say thank you well."
    pause 0.4
    kite "So — dinner."

    p "At the bar?"

    kite "Absolutely not."
    kite "I need to wear something that hasn't heard the word inspection today."

    scene bg restaurant_night at bg_breathe
    with fade
    show screen location_card("Low Room", "After Hours")

    $ kite_has_date_sprite = renpy.loadable("images/kite_female_date.png")
    show kite_female date at center
    with dissolve

    if kite_has_date_sprite:
        narrator "That evening, Kite is waiting outside a low-lit restaurant tucked above the street, all smoked glass, warm lamps, and quiet music."
        narrator "She has changed out of the black work uniform. Softer fabric. A warmer colour. The same guarded posture, less armor around it."
    else:
        narrator "That evening, Kite is waiting outside a low-lit restaurant tucked above the street, all smoked glass, warm lamps, and quiet music."
        narrator "She has changed out of the bar in every way except the part of her that still checks exits and clocks the staff."

    p "I thought all you owned were black tops."

    narrator "For one terrifying second, you think you've gone too far."
    narrator "Then she looks down at herself, like she forgot she was allowed to be seen."

    kite "Work camouflage."

    p "And this?"

    kite "This is me pretending I know how to leave work at work."

    menu:
        "You look beautiful.":
            $ meter_bump("kite", 2)
            narrator "Her eyes move away first. Her mouth does not quite manage to hide the smile."
            kite "Dangerous opening statement."
            p "True one."
            kite "Worse."

        "I like this side of you.":
            $ meter_bump("kite", 2)
            kite "It's not a side."
            pause 0.3
            kite "It's just usually closed."

        "Should I be scared?":
            kite "Of dinner?"
            p "Of you having a life outside The Copper Room."
            kite "Reasonable. I'm also adjusting."

    narrator "Inside, the room is narrow but polished, the kind of place where conversations stay low and every table gets its own pool of amber light."
    narrator "Kite chooses the seat facing the door, then notices herself doing it."

    kite "Habit."

    menu:
        "Take the seat with your back to the door.":
            narrator "You take the exposed seat without comment."
            narrator "Something in her face softens because you understood without making her explain."

        "Ask if she wants to swap.":
            kite "No."
            pause 0.3
            kite "But thank you for asking."

        "Let her have it.":
            narrator "You sit across from her."
            narrator "She notices you noticing. For once, neither of you turns it into a joke."

    narrator "She orders too fast. Then, embarrassed by the efficiency of it, asks what you wanted."

    p "I trust you."

    kite "That's unwise."
    pause 0.3
    kite "But noted."

    narrator "Dinner arrives in a constellation of small plates. Charred bread, roasted vegetables, something bright with citrus, something smoky enough to make Kite stop talking for a second."
    narrator "Kite reaches for the serving spoon, stops, and offers it to you first."
    narrator "A ridiculous gesture. A tiny one. Somehow more intimate than if she had taken your hand."

    kite "I'm bad at this."

    p "Dinner?"

    kite "Being outside my own territory."

    menu:
        "You're doing fine.":
            $ meter_bump("kite")
            kite "You have a generous grading curve."

        "I like seeing you here.":
            $ meter_bump("kite")
            narrator "She lowers her eyes to her bowl."
            kite "Then don't make a big thing of it."

        "We can go if it's too much.":
            kite "No."
            pause 0.4
            kite "I want to stay."

    scene bg kite_apartment
    with fade

    show kite_female date at center
    with dissolve

    narrator "Later, her apartment is quiet in a way the bar never is."
    narrator "Small place. Clean counters. One plant on the windowsill. A stack of bar towels folded too neatly on a chair."

    show buddy neutral at buddy_center
    with dissolve

    narrator "Buddy meets you at the door with the offended dignity of someone abandoned for an entire dinner."

    kite "He'll pretend I left forever."

    p "You were gone for two hours."

    kite "Unforgivable, apparently."

    hide buddy
    with dissolve

    narrator "She makes tea at the small table by the window. The cups don't match."
    narrator "Her nicer clothes look almost out of place here among the folded towels and stacked coasters."
    narrator "Or maybe the apartment is the thing learning how to make room for them."
    narrator "For a while, the city does the talking. Tires on wet pavement. A bus sighing at the curb. Someone laughing two floors down."

    kite "That photo made me feel dirty."
    kite "Not guilty. I knew it wasn't real."
    kite "Just..."
    kite "Like someone could point a camera at this place, invent a version of it, and everyone would believe the invention first."

    menu:
        "That's why proving it mattered.":
            $ meter_bump("kite")
            kite "Yeah."
            kite "Proof is cleaner than begging people to trust you."

        "They wanted you ashamed.":
            $ meter_bump("kite")
            kite "I know."
            kite "That's the part that makes me want to break something."

        "The bar is still yours.":
            kite "Today."
            kite "I'm trying to let today count."

    narrator "She pushes her cup away, then pulls it back like she regrets the retreat."

    kite "When I was a kid, Verrerie could make anything look expensive."
    kite "Glass, light, people."
    kite "You learn young that a good display can hide a lot of rot."

    p "Is that why the photo got to you?"

    kite "Maybe."
    kite "Maybe I hate that I still panic when a fake surface looks convincing."

    narrator "Her hand rests on the table between you."
    narrator "Not reaching. Not withdrawn either."

    menu:
        "Cover her hand with yours.":
            $ meter_bump("kite", 2)
            narrator "You cover her hand with yours."
            narrator "She goes still. Then turns her palm up."

        "Stay near without touching.":
            narrator "You stay where you are."
            narrator "She notices the restraint. Something in her shoulders lowers."

        "Tell her she saw through it.":
            p "You saw through it."
            kite "Eventually."
            p "Eventually counts."

    kite "Stay a little longer?"
    kite "No speech. No rescue mission."
    kite "Just... stay."

    menu:
        "Stay.":
            $ meter_bump("kite", 2)
            narrator "You stay."
            narrator "Kite rinses the cups. You dry them. Buddy falls asleep in the doorway."

        "Tell her you need to go, but gently.":
            narrator "You tell her you need to go."
            narrator "She nods once."
            kite "Okay."
            kite "Thanks for being honest."

    $ kite_friendship += 1

    hide kite_female
    with dissolve

    return

# =========================================================
# KITE - INTERACTION 6 (THREE ENDINGS)
# =========================================================

label kite_interaction_6:
    $ stop_story_music(fadeout=0.8)
    ## Jump, do not call. Credits ends with return; a leftover call
    ## falls through into the Int6 toy menu (Wipe a glass / One throw).
    ## I-need-time already jumps to aftertaste, so its stack is empty.
    if kite_variant == "male":
        jump kite_interaction_6_male
    else:
        jump kite_interaction_6_female


# ---------------------------------------------------------
# KITE - INTERACTION 6 (MALE)
# ---------------------------------------------------------

label kite_interaction_6_male:
    $ save_name = "Reopening Night"
    $ kite_progress = 6

    ## Aug-24: New Game slice. Leftover Remy homework on an empty bedroom
    ## claimed an email the plate does not show. Designed Remy is the
    ## aftertaste after the picture. Non-slice keeps the home beat.
    if not kite_dd_slice:
        $ stop_story_music(fadeout=0.8)
        $ play_story_ambience("title_day_roomtone", fadeout=0.8, fadein=1.0, if_changed=True, volume=0.42)
        scene bg bedroom_night
        with fade
        narrator "Home. The email wasn't sent to you, and you still can't put it down."
        remy "{i}Entry drafted: 'Someone is threatening the bar.'{/i}"
        remy "{i}Whoever sent it knew the timing.{/i}"

    $ play_story_music("kite_theme", fadeout=1.0, fadein=2.0, if_changed=True)
    $ play_story_ambience("bar_murmur", fadeout=0.8, fadein=1.0, if_changed=True)

    scene bg bar_evening
    with fade

    show kite_male neutral at li_center
    show buddy neutral at buddy_center
    with dissolve
    window hide
    $ play_story_sfx("buddy_collar")
    pause 1.2
    window auto
    narrator "The bar reopens."
    narrator "The same stool."

    kite "You're late."

    p "I got stuck at work."

    kite "Excuses."

    if kite_meter >= 4:
        narrator "He says it like a greeting he practiced into a habit."
    else:
        show kite_male tired at li_center
        narrator "He wipes the bar without looking up."

    kite "Saved you a stool. Like always."

    if kite_int5_help == "stay":
        kite "You swept the glass last night. I left the email on the bar."
    elif kite_int5_help == "time":
        kite "You walked out after the email. I opened anyway."

    $ play_story_sfx("glass_set")
    narrator "You sit down."

    kite "I never found out who sent that email."
    kite "We're here now. That's what actually matters."

    # Jul 4 audit fix: same principle as Interaction 5 — "Who made me?"
    # stays as Remy's recurring existential signature, but the lead-in now
    # anchors to something specific to THIS variant (the stool he never
    # gives away) instead of a block reused verbatim from the female branch.
    if persistent.corruption_tier >= 2:
        kite "..."
        kite "{stutter}Y-you sat down.{/stutter}"
        kite "You just sat down. I saw you."
        kite "..."
        kite "The stool. Did I save it, or has it always just been yours?"
        kite "..."
        kite "I don't know when you got here."

    if persistent.corruption_tier >= 3:
        show kite_male stressed at li_center, glitch_flicker, corrupt_tier3
        with dissolve
        narrator "Kite picks up a glass. Puts it down. Picks it up. Puts it down."
        narrator "Kite doesn't seem to notice."
        kite "..."
        kite "{glitch}You're not real.{/glitch}"
        kite "..."
        kite "{stutter}I-I didn't mean—{/stutter}"
        kite "You are real. I'm not."
        kite "I'm just a story."
        kite "..."
        kite "Who's telling it?"
        p "Kite."
        kite "..."
        kite "{glitch}Who made me?{/glitch}"
        kite "..."
        kite "Don't answer. I don't want to know."
        kite "Take the stool."
        kite "Pretend with me."
        kite "Please."
        show kite_male neutral at li_center
        with dissolve

    ## Aug-23: male Int6 hands before confession. Existing toys only.
    window hide
    menu:
        "Wipe a glass.":
            window auto
            $ play_story_sfx("glass_set")
            kite "Yeah."

        "Take the stool.":
            window auto
            narrator "You sit. Kite leaves the stool exactly where it is."

    kite "There's something I need to say."
    "He puts down the rag. Actually looks at you."
    kite "I'm bad at this."
    kite "Not the bar. Not the work."
    kite "This."
    kite "I get busy. I get mean when I'm scared. I break glasses instead of saying what I mean."
    ## Phase 4 repair 2B: identity-selected realization after the original
    ## self-disclosure (director copy). Fallback adds nothing.
    if kite_relationship_identity == "leaned_in":
        kite "You got comfortable here before I was ready for you to."
        kite "I hated how quickly that started feeling normal."
    elif kite_relationship_identity == "chosen_slowly":
        kite "You took your time. I trusted that."
        kite "Then one day you were just here."
    elif kite_relationship_identity == "warm_clear":
        kite "You never made me guess."
        kite "That made it easier to leave the door open."
    elif kite_relationship_identity == "unhurried":
        kite "You never pushed."
        kite "I kept making room for you anyway."
    else:
        pass
    kite "But I keep saving your stool before I know you're coming."
    kite "So there. That's the honest version."

    window hide
    menu:
        "Take the stool. Stay after close.":
            ## 2026-07-11 CONSEQUENCE GATE: the good ending is earned, not
            ## menu-picked. Threshold Option C (warm intimate ~18-28;
            ## light/joke-heavy should struggle vs gate 16). Fails LOUDLY into a fair
            ## in-voice scene — never silently (the old M1 sin).
            window auto
            if kite_meter < 16:
                jump kite_ending_unearned
            $ meter_bump("kite")
            jump kite_ending_good_male

        "Finish the drink. Don't answer yet.":
            window auto
            jump kite_ending_bittersweet_male

        "Leave the stool empty.":
            window auto
            jump kite_ending_bad_male


# ---------------------------------------------------------
# KITE - INTERACTION 6 (FEMALE)
# ---------------------------------------------------------

label kite_interaction_6_female:
    $ save_name = "Reopening Night"
    $ kite_progress = 6
    $ play_story_ambience("bar_murmur", fadeout=0.8, fadein=1.0, if_changed=True)

    scene bg bar_evening
    with fade

    narrator "The bar reopens."
    narrator "Kite puts a Reserved sign on the third stool from the end. She doesn't explain it to anyone."
    narrator "The extra cushion is already on it. She doesn't mention that either."
    narrator "The bar fills up fast. People who weren't there before and people who were. Kite works the room like she's been doing it for twenty years."

    show kite_female tired at center
    with dissolve

    narrator "She doesn't look relieved. She looks like herself again."

    pause 1.2

    show buddy neutral at buddy_center
    with dissolve
    narrator "Buddy is at the door when you walk in. She doesn't react."

    if kite_int5_help == "stay":
        kite "You wiped glasses last night. Tonight you get a stool."
    elif kite_int5_help == "time":
        kite "You left. Door was unlocked. You used it."
    else:
        kite "You're here."

    "She slides the drink toward you."

    kite "Stool's saved."

    kite "I never found out who made that photo. The health department closed the case. No leads."
    kite "Verrerie sent a lawyer letter two weeks later. Nothing actionable. Just enough to make sure I saw the letterhead."
    "She shrugs."
    kite "I stopped looking for one clean culprit. Some people don't need a conspiracy. They just smell weakness and call it business."
    "She looks at you."
    kite "We're here now. That's what matters."

    # Jul 4 audit fix: see the parallel comment in the male branch above —
    # anchored here to the cushion, her own established unique detail,
    # instead of the male branch's reused text.
    if persistent.corruption_tier >= 2:
        kite "..."
        kite "{stutter}Y-you sat down.{/stutter}"
        kite "You just sat down. I saw you."
        kite "..."
        kite "The cushion. I don't remember buying it. It's just always been there when you needed it."
        kite "..."
        kite "I don't know when you got here."

    if persistent.corruption_tier >= 3:
        show kite_female withdrawn at center, glitch_flicker, corrupt_tier3
        with dissolve
        narrator "Kite picks up a glass. Puts it down. Picks it up. Puts it down."
        narrator "Kite doesn't seem to notice."
        kite "..."
        kite "{glitch}You're not real.{/glitch}"
        kite "..."
        kite "{stutter}I-I didn't mean—{/stutter}"
        kite "You are real. I'm not."
        kite "I'm just a story."
        kite "..."
        kite "Who's telling it?"
        p "Kite."
        kite "..."
        kite "{glitch}Who made me?{/glitch}"
        kite "..."
        kite "Don't answer. I don't want to know."
        kite "Take the stool."
        kite "Pretend with me."
        kite "Please."

    show kite_female neutral at center
    with dissolve

    kite "There's something I need to say."
    "She puts down the glass she's holding. Actually looks at you."
    kite "I spent five years making this place exactly what I wanted. Every detail. Every routine."
    ## Phase 4 repair 2B: identity-selected confession middle (director copy).
    ## Fallback plays the original three lines unchanged.
    if kite_relationship_identity == "leaned_in":
        kite "Then you showed up and made the routine feel small."
        kite "I hated that at first."
        kite "Then I started leaving room for you without noticing."
    elif kite_relationship_identity == "chosen_slowly":
        kite "You gave me time."
        kite "Then, when I finally opened the door, you were still there."
    elif kite_relationship_identity == "warm_clear":
        kite "You never made me wonder what you meant."
        kite "That made it easier to leave the door open."
    elif kite_relationship_identity == "unhurried":
        kite "You never hurried me."
        kite "I kept expecting you to. You didn't."
    else:
        kite "Then you showed up and made the routine feel small."
        kite "I hated that at first."
        kite "Then I kept waiting for you anyway."
    "She pauses."
    kite "But I'm willing to learn. If you are."

    window hide
    menu:
        "Take the stool. Stay after close.":
            window auto
            if kite_meter < 16:
                jump kite_ending_unearned
            $ meter_bump("kite")
            jump kite_ending_good_female

        "Finish the drink. Don't answer yet.":
            window auto
            jump kite_ending_bittersweet_female

        "Leave the stool empty.":
            window auto
            jump kite_ending_bad_female


# ---------------------------------------------------------
# MALE ENDINGS
# ---------------------------------------------------------

label kite_ending_unearned:
    $ save_name = "Not Yet"
    $ stop_story_music(fadeout=1.2)
    p "I think I'd like that too."
    kite "..."
    narrator "[kite_subj!c] picks the rag back up. Wipes a spot that was already clean."
    kite "I count regulars by what they do. Not what they order."
    kite "You sat in my bar with your coat on. Every time."
    kite "I'd rather have the honest version of you than the polite one."
    kite "Ask me again when the stool feels like yours."
    ## Jeffrey 2026-09-21: distinct Not Yet — do not soft-redirect to bittersweet.
    jump ending_not_yet_return


label kite_ending_good_male:
    $ ending_route = "kite"
    $ ending_kind = "good"

    p "I think I'd like that too. All of it."
    "He exhales. Like he's been holding his breath."
    kite "Okay."
    kite "Then come here."
    kite "You're going to regret this. I'm an asshole before opening."
    p "I know."
    kite "Okay. Then... we're doing this."

    # Ending cinematic — Good (Male)
    # The clip is a garnish, not the ending: the epilogue dialogue and its
    # minigame callbacks always play. (Previously the whole epilogue lived in
    # the else-branch, so installing the videos silently deleted it.)
    if video_exists("videos/kite_good_male_ending.mp4"):
        $ play_cutscene("videos/kite_good_male_ending.mp4", 8.0)

    $ play_story_music("kite_theme", fadeout=1.0, fadein=2.0, if_changed=True)
    scene bg bar_evening
    with fade
    show kite_male neutral at li_center
    with dissolve

    narrator "Six months later."
    kite "You're late."
    p "Traffic."
    kite "Same excuse as yesterday."
    p "Same traffic."
    "He almost smiles."
    kite "Stool's saved. Drink's getting warm."
    $ play_story_sfx("glass_set")
    narrator "The Regular tastes exactly right."
    if kite_first_cocktail_result == "balanced":
        narrator "You can still taste the first night he said you paid attention."
    elif kite_first_cocktail_result in ("messy_twice", "bitter_meaning", "interesting"):
        narrator "The edge is still there. Honest. A little dangerous. Entirely his."
    elif kite_first_cocktail_result in ("safe", "old_fashioned_safe"):
        narrator "The safe version is gone now. What stayed was the attention."
    elif kite_first_cocktail_result:
        narrator "Whatever you made back then, he still won't copy it. He just keeps yours on the rail."

    if kite_int3_kiss == "yes":
        kite "You kissed me the night I showed you the tattoo."
        kite "I still don't bring people home."
        p "You brought me."
        kite "I know. That's still the problem."
    elif kite_int3_kiss == "no":
        kite "You said no. In the apartment. After the tattoo."
        kite "I didn't make it a test. I just kept the stool."

    kite "Still don't know who sent the email."
    kite "The invoices are in a drawer. I don't open it on Tuesdays."

    ## Jul-24 ending micro-verb.
    window hide
    menu:
        "Say you'll keep showing up on ordinary nights.":
            window auto
            p "Not just the big ones. The Tuesday ones too."
            $ meter_bump("kite", 2)
        "Ask what saved means to [kite_obj].":
            window auto
            p "Is the stool saved, or am I?"
        "Order The Regular without naming it.":
            window auto
            narrator "You nod at the glass. That is enough."

    window auto
    $ stop_story_ambience(fadeout=0.8)

    $ pb_elements = [{"image": "kite_male warm", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]
    call screen popup_book_ending("bg bar_evening", pb_elements, ending_title="Good Ending: The Regular")
    pause 0.15
    call popup_book_close_sequence(cover_color="#3d1e0f", accent_color="#e8c547")
    $ kite_aftertaste_line = "Kite saved a stool. You sat down by choice."
    jump kite_male_aftertaste


label kite_ending_bittersweet_male:
    $ ending_route = "kite"
    $ ending_kind = "bittersweet"
    $ stop_story_music(fadeout=1.5)

    p "I need time. This is a lot."
    "He nods. Picks up the rag again."
    kite "Yeah. Fair."
    "Long pause."
    kite "I'm not going anywhere. You know where to find me."
    p "I'm not saying no—"
    kite "I know. You're saying not yet."
    show kite_male tired at li_center
    "He doesn't look at you."
    kite "Just... don't take too long. I'm not patient. I'm just waiting for you."

    narrator "Two months later."

    # Ending cinematic — Bittersweet (Male)
    if video_exists("videos/kite_bittersweet_male_ending.mp4"):
        $ play_cutscene("videos/kite_bittersweet_male_ending.mp4", 5.0)

    scene bg bar_evening
    with fade
    show kite_male neutral at li_center
    with dissolve

    $ play_story_sfx("glass_set")
    "You walk in. Kite looks up. Pours The Regular. Slides it across the bar."
    kite "Stool's still saved."
    if kite_int1_stool == "stood":
        kite "You stood the first night. Sit if you want."
    elif kite_int1_stool == "sat":
        kite "Same stool as night one. I didn't retire it."
    ## Back to the glasses. Do not keep the welcome face on a man who will not ask.
    show kite_male tired at li_center
    "He goes back to wiping glasses. Doesn't ask where you've been."
    if kite_int4_response == "fight":
        kite "I filed the invoices. Like you said. The email still has no name."
    elif kite_int4_response == "knew":
        kite "We found the invoices. You were right. The email's the part nobody found."
    elif kite_int4_response == "celebrate":
        kite "We celebrated the invoices. Then someone sent that email. Still no name."
    else:
        kite "Still no name on that email."
    if kite_int5_help == "time":
        kite "You left after the email too. Don't do the long version again."
    elif kite_int5_help == "stay":
        kite "You swept the glass. Then you wouldn't stay after close."
    kite "Don't make me wait again."

    ## Jul-24 ending micro-verb.
    window hide
    menu:
        "Promise you'll come back soon.":
            window auto
            p "I won't make you wait without a word."
            $ meter_bump("kite", 2)
        "Ask for one clear boundary.":
            window auto
            p "Tell me what you need from me. One thing."
        "Take the drink and leave it at that.":
            window auto
            narrator "You drink. You don't make it a speech."

    window auto
    $ stop_story_ambience(fadeout=0.8)

    $ pb_elements = [{"image": "kite_male neutral", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]
    call screen popup_book_ending("bg bar_evening", pb_elements, ending_title="Bittersweet Ending: The Open Door")
    pause 0.15
    call popup_book_close_sequence(cover_color="#3d1e0f", accent_color="#e8c547")
    $ kite_aftertaste_line = "Waiting without closing the door."
    jump kite_male_aftertaste


label kite_ending_bad_male:
    $ ending_route = "kite"
    $ ending_kind = "bad"
    $ stop_story_music(fadeout=1.2)

    p "I can't. This is too much."
    show kite_male stressed at li_center
    with dissolve
    "He doesn't flinch."
    kite "Okay."
    "He picks up the rag. Starts wiping a glass that doesn't need wiping."
    kite "I thought... doesn't matter."
    p "Kite—"
    kite "Take care of yourself."
    "He watches you stand, cross to the door, and leave. The latch settles without him moving."

    narrator "Six months later."

    # Ending cinematic — Bad (Male)
    if video_exists("videos/kite_bad_male_ending.mp4"):
        $ play_cutscene("videos/kite_bad_male_ending.mp4", 5.0)

    scene bg bar_evening
    with fade
    show kite_male stressed at li_center
    show buddy neutral at buddy_center
    with dissolve

    "The Copper Room, months on."
    "Same paint. Buddy by the wall. Kite behind the bar. Same apron. Same hand on his head."
    "The bar reopened. You weren't in it."
    if kite_int5_help == "time":
        narrator "You left him with the email the night before. He swept the glass himself."
    elif kite_int5_help == "stay":
        narrator "You swept that glass. Then you left the stool empty."
    if kite_int1_glass == "pushed":
        narrator "The first glass you pushed back is not on the rail. Someone else drinks here."
    elif kite_int1_glass == "taste":
        narrator "He still tastes first. The glass goes to whoever sits down."
    elif kite_int1_glass == "took":
        narrator "He still makes The Regular. It goes to whoever sits down."
    narrator "You don't sit down."
    narrator "Buddy watches the door, then Kite. He stays with Kite."

    ## Jul-24 ending micro-verb.
    window hide
    menu:
        "Almost sit down.":
            window auto
            narrator "You look at the stool. You don't take it."
        "Think of one thing worth saying.":
            window auto
            narrator "You can think of one true line. You swallow it anyway."
        "Accept that leaving is also a choice.":
            window auto
            narrator "You don't stay. You don't pretend that costs nothing."

    window auto
    $ stop_story_ambience(fadeout=0.8)

    # Refusal Remy is this label only. Stay and time never jump here once
    # the choice panel is the click target (see screen choice).
    $ pb_elements = [{"image": "kite_male stressed", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]
    call screen popup_book_ending("bg bar_evening", pb_elements, ending_title="Bad Ending: Last Call")
    pause 0.15
    call popup_book_close_sequence(cover_color="#3d1e0f", accent_color="#e8c547")
    $ kite_aftertaste_line = "Door closed. Subject preserved self by refusing access."
    jump kite_male_aftertaste




# After the Kite picture has landed. Remy is the software that was
# watching, not a third date in that shot. demo_end sends the first
# completed LI path into Remy's hijack; later endings get scrapbook credits.
label kite_male_aftertaste:
    $ ending_route = "kite"
    $ kite_finale_complete = True
    jump demo_end


# ---------------------------------------------------------
# FEMALE ENDINGS
# ---------------------------------------------------------

label kite_ending_good_female:
    $ ending_route = "kite"
    $ ending_kind = "good"

    p "I think I'd like that too."
    "She exhales."
    kite "Okay."
    kite "I'm going to be terrible at this. I'll forget anniversaries. I'll cancel plans when the ice machine breaks."
    p "I know."
    kite "Okay. Then... we're doing this."

    # Ending cinematic — Good (Female)
    if video_exists("videos/kite_good_female_ending.mp4"):
        $ play_cutscene("videos/kite_good_female_ending.mp4", 8.0)

    $ play_story_music("kite_theme", fadeout=1.0, fadein=2.0, if_changed=True)
    scene bg bar_evening
    with fade
    show kite_female neutral at center
    show buddy neutral at buddy_center
    with dissolve

    narrator "Six months later."
    "The Copper Room is closed for the night. Just you, Kite, and Buddy."
    kite "You're doing it wrong."
    p "You're a terrible teacher."
    kite "I'm an excellent teacher. You're a terrible student."
    "She puts her hand over yours on the shaker. Guides it."
    kite "Like that. See?"
    if kite_dart_result in ("win", "clean"):
        kite "And don't start acting smug about darts."
        p "I beat you once."
        narrator "She smiles like she still hasn't decided whether to call that flirting or fraud."
    elif kite_dart_result in ("tie", "hit"):
        kite "Still think that count was generous."
        p "Still think you're lying."
        narrator "She bumps her shoulder against yours and does not deny it."
    elif kite_dart_result in ("loss", "miss"):
        kite "Your aim's still terrible."
        p "You keep asking me to play."
        narrator "That makes her laugh before she remembers to hide it."
    elif kite_dart_result in ("passed", "early"):
        kite "You skipped the board. I still keep a dart out in case you change your mind."
        narrator "She does not look at the board when she says it."

    if kite_int3_stay == "stay":
        kite "You stayed while I pulled the CCTV. I kept the Reserved sign after that."
    elif kite_int3_stay == "wait":
        kite "You said you'd wait. I stopped pretending that was nothing."
    elif kite_int3_stay == "ready":
        kite "I said I'd tell you when I was ready. I put the cushion out instead."

    kite "I never found out who made the photo."
    kite "The lawyer letter is in the office. I don't open it."
    narrator "The Regular tastes exactly right."

    ## Jul-24 ending micro-verb (female good).
    window hide
    menu:
        "Say you'll keep showing up on ordinary nights.":
            window auto
            p "Not just the big ones. The Tuesday ones too."
            $ meter_bump("kite", 2)
        "Ask what saved means to [kite_obj].":
            window auto
            p "Is the stool saved, or am I?"
        "Stay behind the bar a minute longer.":
            window auto
            narrator "You don't rush the quiet. She doesn't either."

    window auto

    $ stop_story_ambience(fadeout=0.8)
    $ pb_elements = [{"image": "kite_female relaxed", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]
    call screen popup_book_ending("bg bar_evening", pb_elements, ending_title="Good Ending: The Regular")
    pause 0.15
    call popup_book_close_sequence(cover_color="#3d1e0f", accent_color="#e8c547")
    ## Parity with male endings: same Remy-watcher funnel (existing label). No new story text.
    $ kite_aftertaste_line = "Kite saved a stool. You sat down by choice."
    jump kite_male_aftertaste


label kite_ending_bittersweet_female:
    $ ending_route = "kite"
    $ ending_kind = "bittersweet"

    p "I need time. This is a lot."
    "She nods once."
    p "I'm not saying no—"
    kite "I know."
    "She doesn't finish the sentence for you. Just lets it sit between you."
    "Goes back to the glass she was already pouring. Sets it down in front of you."
    kite "You'll know when you're ready."
    show kite_female tired at center
    "She doesn't look up."
    kite "I'll be here."
    "Not a promise. A fact."

    narrator "Two months later."

    # Ending cinematic — Bittersweet (Female)
    if video_exists("videos/kite_bittersweet_female_ending.mp4"):
        $ play_cutscene("videos/kite_bittersweet_female_ending.mp4", 8.0)

    scene bg bar_evening
    with fade
    show kite_female neutral at center
    with dissolve

    "You walk in. Kite looks up. She doesn't say anything. Just pours The Regular and slides it across the bar."
    kite "You're late."
    p "I know."
    if kite_int1_stool == "stood":
        kite "Reserved is for people who stand around first. Sit if you want."
    elif kite_int1_stool == "sat":
        kite "Reserved. The cushion stays even when you don't."
    if kite_int4_response == "earned":
        kite "You called the appeal a win. I still don't have a name."
    elif kite_int4_response == "regret":
        kite "I sent the side-by-side. Like you wanted. They closed the case anyway."
    elif kite_int4_response == "breathe":
        kite "You made me stop before I hit send. I remembered. Still no leads."
    kite "..."
    kite "I'm glad you're here."
    if kite_int5_help == "time":
        kite "You needed time the night before we opened. I sent the appeal anyway."
    elif kite_int5_help == "stay":
        kite "You wiped glasses with me. Then you wouldn't stay after close."

    ## Jul-24 ending micro-verb (female bittersweet).
    window hide
    menu:
        "Promise you'll come back soon.":
            window auto
            p "I won't make you wait without a word."
            $ meter_bump("kite", 2)
        "Ask for one clear boundary.":
            window auto
            p "Tell me what you need from me. One thing."
        "Take the drink and leave it at that.":
            window auto
            narrator "You drink. You don't make it a speech."

    window auto

    $ stop_story_ambience(fadeout=0.8)
    $ pb_elements = [{"image": "kite_female neutral", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]
    call screen popup_book_ending("bg bar_evening", pb_elements, ending_title="Bittersweet Ending: The Open Door")
    pause 0.15
    call popup_book_close_sequence(cover_color="#3d1e0f", accent_color="#e8c547")
    ## Parity with male endings: same Remy-watcher funnel (existing label). No new story text.
    $ kite_aftertaste_line = "Waiting without closing the door."
    jump kite_male_aftertaste


label kite_ending_bad_female:
    $ ending_route = "kite"
    $ ending_kind = "bad"

    p "I can't. This is too much."
    show kite_female stressed at center
    with dissolve
    "She doesn't flinch. But her hand stills on the glass."
    kite "Okay."
    "She sets the glass down. Carefully."
    kite "I kept the seat warm. Guess that's it, then."
    p "Kite—"
    kite "Take care of yourself."
    "She picks up another glass and keeps polishing while you stand and leave, eyes fixed on the rim."
    "The door closes. The bell doesn't ring."

    narrator "Six months later."

    # Ending cinematic — Bad (Female)
    if video_exists("videos/kite_bad_female_ending.mp4"):
        $ play_cutscene("videos/kite_bad_female_ending.mp4", 5.0)

    scene bg bar_evening
    with fade
    show kite_female withdrawn at center
    show buddy neutral at buddy_center
    with dissolve

    "You pass The Copper Room once, months on."
    "Same paint. Same bandana on Buddy. Kite behind the bar, same calm, same steady hands."
    "The Reserved sign is still on the third stool. The extra cushion too. Nobody sits there."

    narrator "You don't go in."
    if kite_int5_help == "time":
        narrator "You left her the night before reopen. She unlocked the door anyway."
    elif kite_int5_help == "stay":
        narrator "You wiped glasses with her. Then you left the stool empty."
    if kite_int1_glass == "taste":
        narrator "She still calls the drink hers. She still won't write it down."
    elif kite_int1_glass == "pushed":
        narrator "The first glass you pushed back is not waiting. Someone else ordered."
    elif kite_int1_glass == "took":
        narrator "She still pours The Regular. It goes to whoever sits down."
    narrator "The four-fingered hand is still in a folder somewhere. She stopped hunting."
    narrator "Buddy is at the door. He watches you pass. He doesn't follow."

    ## Jul-24 ending micro-verb (female bad).
    window hide
    menu:
        "Almost turn around at the door.":
            window auto
            narrator "Your hand finds the handle. You don't open it."
        "Think of one thing worth saying.":
            window auto
            narrator "You can think of one true line. You swallow it anyway."
        "Accept that leaving is also a choice.":
            window auto
            narrator "You don't go in. You don't pretend that costs nothing."

    window auto

    $ stop_story_ambience(fadeout=0.8)
    $ pb_elements = [{"image": "kite_female neutral", "x": 0.5, "y": 0.55, "delay": 0.2, "zoom": 0.85}]
    call screen popup_book_ending("bg bar_evening", pb_elements, ending_title="Bad Ending: Last Call")
    pause 0.15
    call popup_book_close_sequence(cover_color="#3d1e0f", accent_color="#e8c547")
    ## Parity with male endings: same Remy-watcher funnel (existing label). No new story text.
    $ kite_aftertaste_line = "Door closed. Subject preserved self by refusing access."
    jump kite_male_aftertaste
