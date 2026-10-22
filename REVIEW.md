# Gameplay review

## Evaluation

The computing-history theme, era-specific accumulator art, and active/idle blend are strong foundations. The biggest problem is consistency: historical eras and motherboard generations share an index even though their names and thresholds differ. Several documented systems exist in the model but were disconnected from the actual player interface.

## Fixes in the first change

- Route idle and offline income to the active currency, not always bits.
- Save pebble totals, inventions, efficiency and historical upgrades; merge missing generator defaults on load.
- Use Unix wall time for offline progress (75%, capped at 24 hours, no negative time). Ignore unconvertible legacy process-tick timestamps.
- Recover complete state through the normal loader when a backup is needed, including when the main save is missing.
- Resolve historical generator and upgrade costs correctly, filter generators/upgrades by era, and align purchase hitboxes with drawn buttons.
- Enforce historical upgrade caps and prevent click upgrades multiplying idle income.
- Preserve earned pebble totals when defining bits.
- Reset shard collection tracking on rebirth/prestige, respect Quick Collect's reduced threshold, retain shard upgrade definitions and reject unknown upgrade purchases.
- Keep save feedback visible for three seconds and use the configured save path for deletion.

## Suggested progression (second change)

Expose a guided research track: Define Bit -> Boolean Algebra -> Logic Gates, alongside an explicit next-era goal. Show requirements and rewards before unlocking, and let players claim inventions and advance eras from the main screen. Use post-binary earnings for Boolean Algebra so defining bits early cannot permanently lock it out. Keep a meaningful reason to complete research before moving on.

## Implemented progression

The second change adds the Research roadmap (now in the bottom discovery bar, or R), clickable one-time invention claims, readiness indicators, progress bars, and explicit no-reset era advancement. Boolean Algebra now uses post-binary earnings instead of a pebble counter that stops growing. Two new ordered milestones extend the track: Stored Programs (Vacuum Tubes, 8M earned, 1.5x efficiency) and Integrated Circuits (Transistors, 50M earned, 2x efficiency). All five projects together grant 24x clicks and production, persist through resets, and are saved immediately on claim. Later era advancement retains unlocked hardware categories rather than disabling existing production.

## Visual refresh

A new dashboard replaces the old layered neon presentation rather than recoloring its individual widgets. The art direction is warm charcoal, sage, restrained amber, readable sans-serif text, generous spacing and static, era-specific counting machines. The balance is the visual anchor; consistent shop cards and a bottom discovery bar provide the two next actions. Settings, statistics, onboarding, reset confirmations and research use the same design language.

Drawing and hit-testing share shop and dialog geometry. The minimum window is 960 × 640; overflowing cards remain scrollable and cannot be purchased outside the viewport. Truncated descriptions have full-text hover cards. Effects are opt-in, reduced motion pauses animations, and the standard body/secondary/action text combinations meet 4.5:1 contrast in normal and high-contrast palettes. Visual preferences persist; older saves receive a one-time quiet-default migration without changing progression.

`python -m unittest test_gameplay test_visual_refresh -v` now runs 13 tests, including four supported sizes, every era and modal, resize/scroll purchases, hidden/clipped card guards, shard-upgrade geometry, dialog routing, contrast and preference migration. Native Windows rendering is checked separately from the headless tests. The legacy compression configuration/parser and incomplete effects remain outside this presentation-only change.

## Era continuity and entry pacing

The era-equality filters introduced with historical purchasing were too strict: they hid earlier machines and excluded their income immediately after advancement, despite retaining the counts in the save. Replaced the per-current-era production branches with a sum of every owned machine introduced at or before the current era. Each family retains its own production upgrades; research, prestige and the advertised Entropy Amplification multiplier apply once. Legacy basic generators also contribute in modern eras. Owned machines never depend on re-earning a shop unlock threshold to keep running.

Earlier machines/upgrades remain visible and purchasable using the current currency; future-era machines and hardware upgrades remain guarded at the purchase boundary as well as in the shop. Earlier click bonuses now accumulate rather than being replaced by the current era's bonus. Abacus unlocks retain lifetime pebble evidence after Define Bit. Shop cards show actual owned output and mark earlier-era sources, with current-era technology first.

Added an entry-level Thermionic Diode at the existing Vacuum Tubes entry threshold (500K earned, 1M cost, 50K/s base), rather than nerfing or repricing existing Triodes (still 10M cost, 500K/s). No migration or new save fields are needed. Explicit resets still clear machine counts.

`playtest_era_progression.py` uses ten initial clicks, no subsequent clicking or injected money, one-second steps and a documented purchase policy: save for the entry machine immediately after advancing, otherwise choose affordable production/cost, at most 12 purchases per step. With only Define Bit, starter waits were **19 / 19 / 31 / 0 seconds** for eras 1–4; with research claimed as available they were **19 / 10 / 13 / 0 seconds**. No simulated second had zero income, and no transition reduced production. This is a bounded deterministic probe, not a universal balance guarantee or a late-game rebirth/prestige simulation.

`python -m unittest test_era_progression test_machines test_gameplay test_visual_refresh -v` runs **37 regressions**. Continuity tests cover all six advances, mixed-family multipliers, prior purchases/click bonuses, unlock preservation, future-tech guards, bulk costs, unchanged Triodes, bounded entry-saving pacing, explicit resets, pre-Diode saves, offline carryover and resized/scrolled real purchase events. Native Windows smoke additionally advances through Research into eras 1–4, verifies identical income/counts at the transition, purchases earlier hardware through its painted button, runs 120 frames per scenario at 960x640/1200x800, and saves only to a temporary directory.

Working Mechanical/Electromechanical illustrations are documented in `docs/MACHINE_DESIGN.md`. BobRoss.bot supplied art-direction consultation in WIL-164. Rendered sign-off in WIL-165 is still pending: Paperclip attachment publication encountered ownership/run restrictions. Neither implementation tests nor our native smoke are claimed as BobRoss's visual approval.

## Further recommendations

- Separate historical era and motherboard generation before adding more historical content; rebirth and era advancement currently move the same index.
- Reconcile README/design documents with the live historical start and revisit non-monotonic late-game rebirth thresholds.
- Finish or remove compression upgrades whose effects are not yet consumed by production logic; do not advertise them as complete.
- Move player saves outside the checkout with a migration path, remove tracked caches/sample saves in a separate cleanup, and unify resource paths for launching outside the project directory.
- Add full-run balance simulations and broader GUI layout tests before expanding endgame multipliers.

## Verification

`python -m unittest test_gameplay -v` covers currency routing, costs, upgrade caps, shard resets, save/load, offline earnings, legacy clocks, backup recovery, and headless GUI rendering using temporary save files. `python playtest.py` exercises the existing deterministic progression checks. The expanded suite has six tests, including research ordering, duplicate claims, persistence, GUI keyboard/mouse routing, three window sizes and rendering across all seven historical eras. A native Windows display smoke test also opened and rendered the main screen and research screen. Neither smoke test is a substitute for a long-run balance/playability session.
