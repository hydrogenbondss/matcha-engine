# Matcha Engine — sample pose lineup.
#
# One character, four expressions: the point of the demo is consistency, not
# plot. Starter Placeholder art works before you generate; run
# `matcha character … --deploy` to replace images under game/images/characters/
# (and redefine the character block in matcha_characters.rpy).

label start:
    scene black
    with dissolve

    "Matcha Engine sample — one YAML character, several expressions, deployed into Ren'Py."

    show sakura idle at center
    with dissolve
    sakura "Idle. Same face, same outfit — this is the identity lock."

    show sakura happy
    with dissolve
    sakura "Happy. Expression changes; the look should stay put."

    show sakura sad
    with dissolve
    sakura "Sad. Still the same character — that's the pipeline's job."

    show sakura surprised
    with dissolve
    sakura "Surprised. Four poses from one config seed."

    hide sakura
    with dissolve

    "Optional: regenerate with --side-image (or side_image: true) for dialogue portraits beside the text box."

    "That's the lineup. Quit from the menu when you're done — or edit configs/example_character.yaml and redeploy."
    return
