# Working historical machines

Art direction was consulted with **BobRoss.bot**, the Paperclip company's Creative Director / UI/UX Lead, in **WIL-164**. His initial consultation was based on the proposed direction, not inspection of rendered art; it was not visual approval.

Applied priorities:
- Distinct mounted instruments, not disconnected gear/relay icons.
- A single connected mechanical drive: an open five-gear chain, pitch-radius/tooth-count ratios, counter-rotation and initial tooth/gap phase, equal-pulley belt, crank, fixed-length offset connecting rod and guided reciprocating carriage. The carriage is not falsely meshed to the continuously rotating gears.
- A pale decimal register shows the low eight digits of real currency. Only small increases roll (240 ms); rapid changes coalesce, and spending/large jumps settle immediately.
- An enamel cabinet holds a 4x2 bank of copper-wound relays with visible pivot/contact geometry. One restrained scan closes, holds and releases each contact; a wire segment brightens after closure.
- Eight labeled output lamps reflect floor(actual currency) modulo 256, bit 7 at left. Filled pale centers distinguish ON without relying only on hue.
- Clearly labeled demo tape uses a fixed illustrative timing pattern and indexed feed, not fictitious earnings history.
- Minimum-window composition removes secondary lettering and coil detail and reallocates space to the mechanism. Ordinary dashboard balance and production remain authoritative and legible.

`gui/machines.py` owns procedural drawing and a bounded, delta-time-driven per-game presentation clock. Static plates are cached with bounded caches; draw routines neither read wall time nor mutate gameplay. Click impulses decay analytically and behave consistently at different frame rates. No new dependencies or save fields are needed.

Reduced Motion freezes all decorative geometry, scan, signal and tape phases; counter/lamp readings still change immediately. High-contrast mode retains the shared palette for output information. Abacus, Vacuum Tubes and later-era art remains unchanged.

## Transistors centerpiece

`gui/transistors.py` replaces the era-4 generic chip with a discrete solid-state logic card. Metal-can NPN packages have visible leads, locating tabs and restrained machined highlights; color-banded resistors, ceramic capacitors, through-hole pads, right-angle copper traces and gold edge contacts establish a different instrument from the later integrated-circuit eras. Compact layout reserves room for the board rather than squeezing a tiny chip into empty space.

One short sage segment travels along existing copper traces, behind the components. It uses the shared presentation clock, including click impulses and Reduced Motion. **DEMO SIGNAL / DEMO FLOW** labels distinguish illustrative switching from production; this is not a circuit simulator. The binary register and `0x` readout show actual currency modulo 256, bit 7 at left, even while decorative motion is frozen. Fixed board/parts layers have an eight-entry palette-aware cache. No gameplay, save schema or dependencies changed.

Six new regressions cover connected trace endpoints, bounded on-trace motion, pure deterministic rendering with parent clipping, truthful byte/spending/jump output, palette caching and empty targets. Existing real-click and Reduced Motion GUI regressions now include era 4. Native Windows checks render 180 frames at each of 1200x800 and 960x640, verify a visible Windows window, spending/large jumps, frozen geometry with live readings, high contrast and temporary-save isolation. Stills are retained outside the repository under `Projects/transistor-review`. These checks do not constitute BobRoss rendered approval.

Verification:
```powershell
python -m unittest test_transistors test_era_progression test_machines test_gameplay test_visual_refresh -v
python playtest.py
```

Tests cover gear engagement/ratios, rod length and guide bounds over 360 angles, scan ordering, indexed feed, truthful outputs, carry/spending/large jumps, rapid updates, frame-rate independence, clipping, click routing after resize, pure rendering and Reduced Motion pixel stability. Native smoke runs use temporary saves, both eras and both 1200x800/960x640 windows; stills and short APNG captures are collected separately for rendered design review. Follow-up WIL-165 was requested, but rendered sign-off is pending because Paperclip attachment delivery encountered ownership/run restrictions. Initial consultation is not visual approval; screenshots alone do not establish correct motion.
