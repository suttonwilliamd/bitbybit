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

Reduced Motion freezes all decorative geometry, scan, signal and tape phases; counter/lamp readings still change immediately. High-contrast mode retains the shared palette for output information. Existing abacus/other-era art remains unchanged.

Verification:
```powershell
python -m unittest test_machines test_gameplay test_visual_refresh -v
python playtest.py
```

Tests cover gear engagement/ratios, rod length and guide bounds over 360 angles, scan ordering, indexed feed, truthful outputs, carry/spending/large jumps, rapid updates, frame-rate independence, clipping, click routing after resize, pure rendering and Reduced Motion pixel stability. Native smoke runs use temporary saves, both eras and both 1200x800/960x640 windows; stills and short APNG captures are submitted separately for rendered design review. Screenshots alone do not establish correct motion.
