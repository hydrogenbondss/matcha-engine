# =========================================================
# CHARACTER DEFINITIONS
# =========================================================
#
# Naming convention:
# - Blake and Kite use one Character() each — names are unisex,
#   only the sprite art and pronouns differ between variants.
#   Pronouns flow through [blake_subj]/[blake_obj]/[blake_pos]
#   and [kite_subj]/[kite_obj]/[kite_pos].
# - Neo / Nia use two Character()s because the *display name* forks.
#   Display names are fixed on the Character (Neo / Nia) so a female-branch
#   `nia "..."` line cannot inherit a stale neo_name="Neo" on the nameplate.
#   Pronouns still flow through [neo_subj]/[neo_obj]/[neo_pos] via
#   apply_li_variants. neo_name remains for UI copy / archive that needs it.
#
# When writing dialogue:
#   - Blake/Kite: always `blake "..."` / `kite "..."`.
#   - Neo: `neo "..."` in male branch, `nia "..."` in female branch.

init python:
    def sideb_dialogue_click(event, interact=True, **kwargs):
        # Jul 4 audit: this fired the button-hover tick on EVERY dialogue
        # line (~5,000 identical 40ms ticks per playthrough, same cue as UI
        # hover). Silenced. The callback plumbing stays so a purpose-made,
        # sub-audible advance cue can be dropped in later without rewiring
        # every Character().
        return


define narrator = Character(what_italic=False)
define p = Character("[player_name]", callback=other_presence_callback)
## 2026-07-17: remy gets the Remy presence mode-switch (zz_remy_presence.rpy);
## every other speaker dissolves it. Both compose with sideb_dialogue_click.
define remy = Character("Remy", callback=remy_presence_callback)

define blake = Character("[blake_name]", callback=other_presence_callback)
## 2026-08-20 visual gate P0: fixed display names (not [neo_name]). Live
## capture showed `nia` dialogue with Neo nameplate when neo_name was stale.
define neo = Character("Neo", callback=other_presence_callback)
define nia = Character("Nia", callback=other_presence_callback)
define kite = Character("[kite_name]", callback=other_presence_callback)

define derek = Character("Derek", callback=other_presence_callback)
define barbie = Character("Barbie", callback=other_presence_callback)
define dad = Character("Dad", callback=other_presence_callback)
define marcus = Character("Marcus", callback=other_presence_callback)
define may = Character("May", callback=other_presence_callback)
## Spoken Buddy lines take the nameplate. Planted sprite stays buddy_center.
define buddy = Character("Buddy", callback=other_presence_callback)
