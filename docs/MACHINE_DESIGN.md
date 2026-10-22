# Working historical machines

Art direction was consulted with **BobRoss.bot**, the Paperclip company's Creative Director / UI/UX Lead, in **WIL-164**. His initial consultation was based on the proposed direction, not inspection of rendered art; it was not visual approval.

Applied priorities:
- Distinct mounted instruments, not disconnected gear/relay icons.
- A single connected mechanical drive: an open five-gear chain, pitch-radius/tooth-count ratios, counter-rotation and initial tooth/gap phase, equal-pulley belt, crank, fixed-length offset connecting rod and guided reciprocating carriage. The carriage is not falsely meshed to the continuously rotating gears.
- A pale decimal register shows the low eight digits of real currency. Only small increases flip (240 ms); rapid changes coalesce, and spending/large jumps settle immediately.
- An enamel cabinet holds a 4x2 bank of copper-wound relays with visible pivot/contact geometry. One restrained scan closes, holds and releases each contact; a wire segment brightens after closure.
- Eight labeled output lamps reflect floor(actual currency) modulo 256, bit 7 at left. Filled pale centers distinguish ON without relying only on hue.
- Clearly labeled 8-bit demo tape computes varied teaching programs and punches completed results, never fictitious earnings history.
- Minimum-window composition removes secondary lettering and coil detail and reallocates space to the mechanism. Ordinary dashboard balance and production remain authoritative and legible.

`gui/machines.py` owns procedural drawing and a bounded, delta-time-driven per-game presentation clock. Static plates are cached with bounded caches; draw routines neither read wall time nor mutate gameplay. Click impulses decay analytically and behave consistently at different frame rates. No new dependencies or save fields are needed.

Reduced Motion freezes all decorative geometry, scan, signal and tape phases; counter/lamp readings still change immediately. High-contrast mode retains the shared palette for output information. Abacus, Vacuum Tubes and later-era art remains unchanged.

## Relay program tape and inset LOW BYTE strip

`gui/tape_program.py` replaces the four-byte decorative repeat with eight deterministic teaching programs: COUNT, ADD, MULT, XOR, SHIFT, FIB, ASCII and PARITY. Each pass varies operands; ASCII spells a greeting and Fibonacci advances its pair. All results are eight-bit values (COUNT/SHIFT explicitly wrap). The visible equation uses decimal operands/results. This is a teaching demonstration, not an electrical circuit simulator or player-income log.

Each six-phase-unit job has READ (0–0.5), RUN (0.5–4.5, exactly one eight-contact scan), PUNCH (4.5–5) and HOLD (5–6) stages. The relay bank is open outside RUN. Inputs precede computation; answers appear only after the scan. PUNCH advances one 14-pixel row, with a matching eight-pin head stroke, then the result remains readable. Paper starts blank and shows a deterministic demo timeline: rows retain their program tag and actual computed byte rather than rearranging a decorative pattern. Feed holes remain distinct from result holes. Jobs have a bounded 128-entry immutable cache; rendering preserves parent clipping.

A cosmetic ASCII-message burst has approximately **1-in-65,536 start odds per job**. One 64-bit presentation seed is drawn at GUI initialization, never inside rendering, never saved, and never used for gameplay. A two-byte BLAKE2s hash of seed/job selects a rare start; a bounded backward check reconstructs its subsequent characters consistently even after skipped frames. The same seed also determines historical tape rows. Standalone rendering defaults to seed zero for determinism. Tests/native previews use a genuine known-hit seed, not increased production odds or a shipped cheat switch. No reward, save fields or dependencies are introduced; Reduced Motion freezes the demo timeline along with its mechanisms, while real balance lamps stay live.

The old LOW BYTE strip extended four design pixels below the inner cabinet. It is now a single full-width inset strip, including the numeric balance, with eight design pixels of bottom clearance and shared housing/lamp/label geometry. The relay bank and tape housing stop above it; compact relay sockets are slightly shorter to avoid moving the overlap elsewhere. All bit labels, lamp rings, LOW BYTE text and the numeric value fit inside this strip at both reference sizes.

Eight new regressions in `test_program_tape.py` cover program math/variety, stage/scan/feed ordering, decoded punched bytes and history, cabinet/readout bounds, text fit, real rare-message fixtures, pure clipped rendering and actual GUI Reduced Motion/session-only seed behavior. The combined suite has **58 tests**; both playtests and compilation pass. Native Windows previews run 360 frames per reference size, exercise a real machine click, spending/large jumps, high contrast, Reduced Motion/live output and the rare fixture with temporary saves. Two 120-frame APNGs at 20 fps, task/stage filmstrips and stills are retained outside Git under `Projects/program-tape-review`. All unrelated eras are pixel-identical to baseline at both illustration sizes. These checks are not BobRoss rendered sign-off.

## Stepped Reckoner split-flap register

The original register moved whole glyphs vertically, which looked like a scrolling reel rather than split flaps. Each digit now has fixed upper/lower backing leaves and a center hinge with side pivots. In the first half of the transition, the old upper leaf foreshortens into the hinge, revealing the new upper half; in the second half, the new lower leaf opens downward over the old lower half. Only the folding leaf is scaled/shaded. The backing glyph halves never translate, and unchanged digits stay still.

`flap_projection` derives the two half-turn projections from the existing eased 240 ms presentation transition. `FLAP_SECONDS` replaces the old scrolling-duration name. Ten fixed faces at each reference size use a bounded 20-entry cache; animated frames are not cached. Carries and eight-digit wrapping retain real old/new values. Initial readings, spending, large jumps and Reduced Motion still settle immediately. No gameplay or save fields changed.

Seven regressions in `test_split_flap.py` verify projection bounds/order, stationary backing halves, exact endpoints/unchanged digits, carries/wrapping without mutation, instant settlement, parent clipping and cache immutability. The combined suite has **50 tests**. Native Windows previews run 240 frames at each of 1200x800/960x640 with temporary saves, capture 120-frame APNGs at 30 fps plus a hinge-transition filmstrip, and check Reduced Motion stability/live readings, spending, large jumps and high contrast. Pixel hashes confirm all other eras' art is unchanged at both illustration sizes. Artifacts are outside the repository in `Projects/split-flap-review`; these checks do not imply BobRoss rendered sign-off.

## Transistors centerpiece

`gui/transistors.py` replaces the era-4 generic chip with a discrete solid-state logic card. Metal-can NPN packages have visible leads, locating tabs and restrained machined highlights; color-banded resistors, ceramic capacitors, through-hole pads, right-angle copper traces and gold edge contacts establish a different instrument from the later integrated-circuit eras. Compact layout reserves room for the board rather than squeezing a tiny chip into empty space.

One short sage segment travels along existing copper traces, behind the components. It uses the shared presentation clock, including click impulses and Reduced Motion. **DEMO SIGNAL / DEMO FLOW** labels distinguish illustrative switching from production; this is not a circuit simulator. The binary register and `0x` readout show actual currency modulo 256, bit 7 at left, even while decorative motion is frozen. Fixed board/parts layers have an eight-entry palette-aware cache. No gameplay, save schema or dependencies changed.

Six new regressions cover connected trace endpoints, bounded on-trace motion, pure deterministic rendering with parent clipping, truthful byte/spending/jump output, palette caching and empty targets. Existing real-click and Reduced Motion GUI regressions now include era 4. Native Windows checks render 180 frames at each of 1200x800 and 960x640, verify a visible Windows window, spending/large jumps, frozen geometry with live readings, high contrast and temporary-save isolation. Stills are retained outside the repository under `Projects/transistor-review`. These checks do not constitute BobRoss rendered approval.

Verification:
```powershell
python -m unittest test_program_tape test_split_flap test_transistors test_era_progression test_machines test_gameplay test_visual_refresh -v
python playtest.py
```

Tests cover gear engagement/ratios, rod length and guide bounds over 360 angles, scan ordering, indexed feed, truthful outputs, carry/spending/large jumps, rapid updates, frame-rate independence, clipping, click routing after resize, pure rendering and Reduced Motion pixel stability. Native smoke runs use temporary saves, both eras and both 1200x800/960x640 windows; stills and short APNG captures are collected separately for rendered design review. Follow-up WIL-165 was requested, but rendered sign-off is pending because Paperclip attachment delivery encountered ownership/run restrictions. Initial consultation is not visual approval; screenshots alone do not establish correct motion.
