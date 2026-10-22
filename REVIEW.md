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

The second change adds the Research roadmap (click below the title, or R), clickable one-time invention claims, readiness indicators, progress bars, and explicit no-reset era advancement. Boolean Algebra now uses post-binary earnings instead of a pebble counter that stops growing. Two new ordered milestones extend the track: Stored Programs (Vacuum Tubes, 8M earned, 1.5x efficiency) and Integrated Circuits (Transistors, 50M earned, 2x efficiency). All five projects together grant 24x clicks and production, persist through resets, and are saved immediately on claim. Later era advancement retains unlocked hardware categories rather than disabling existing production.

## Further recommendations

- Separate historical era and motherboard generation before adding more historical content; rebirth and era advancement currently move the same index.
- Reconcile README/design documents with the live historical start and revisit non-monotonic late-game rebirth thresholds.
- Finish or remove compression upgrades whose effects are not yet consumed by production logic; do not advertise them as complete.
- Move player saves outside the checkout with a migration path, remove tracked caches/sample saves in a separate cleanup, and unify resource paths for launching outside the project directory.
- Add full-run balance simulations and broader GUI layout tests before expanding endgame multipliers.

## Verification

`python -m unittest test_gameplay -v` covers currency routing, costs, upgrade caps, shard resets, save/load, offline earnings, legacy clocks, backup recovery, and headless GUI rendering using temporary save files. `python playtest.py` exercises the existing deterministic progression checks. The expanded suite has six tests, including research ordering, duplicate claims, persistence, GUI keyboard/mouse routing, three window sizes and rendering across all seven historical eras. A native Windows display smoke test also opened and rendered the main screen and research screen. Neither smoke test is a substitute for a long-run balance/playability session.
