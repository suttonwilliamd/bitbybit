# BIT BY BIT - Information Theory Game

## Quick Start

### Option 1: Double-click `start_game.bat`
This launches the full game with all features:
- Entropy Era (bits and generators)
- Rebirth system with Data Shards
- Compression Era (dual currency, efficiency mechanics)
- Motherboard Upgrade System (10 generations)
- Prestige System (Quantum Fragments)
- Calm charcoal-and-sage dashboard with optional visual effects
- Save/load with offline progress

### Option 2: Run from command line
```bash
python main.py
```

## Game Progression

1. **Start**: Click the abacus to earn pebbles and buy early generators.
2. **Research**: Click the discovery bar at the bottom (or press R) to see goals, rewards and the next era.
3. **Define Bit**: At 500 lifetime pebbles, convert your remaining balance 100:1 and gain 2x clicks and production. Owned generators continue producing in the new currency.
4. **Advance eras**: After defining bits, earn the displayed total and select **ADVANCE** in Research. This does not spend your balance or reset progress. **All owned machines from earlier eras keep producing in your current currency**, with their existing upgrades. Earlier machines and upgrades stay in the scrollable shops; new-era technology is listed first. Historical click upgrades also carry forward.
5. **More research**: Claim the permanent milestones below in order. Claims are free, one-time, saved immediately, and survive rebirth and prestige.
6. **Rebirth / prestige**: Existing resets award Data Shards or Quantum Fragments. See `REVIEW.md` for remaining inconsistencies between historical eras and motherboard generations.

### Research milestones

| Project | Minimum era | Earned total | Reward |
| --- | --- | --- | --- |
| Define Bit | Abacus | 500 pebbles | 2x clicks and production; balance conversion |
| Boolean Algebra | Mechanical | 50K post-binary units | 2x clicks and production |
| Logic Gates | Electromechanical | 5M post-binary units | 2x clicks and production |
| Stored Programs | Vacuum Tubes | 8M post-binary units | 1.5x clicks and production |
| Integrated Circuits | Transistors | 50M post-binary units | 2x clicks and production |

Post-binary units are the cumulative `total_bits_earned` field across historical currency names, reset by rebirth/prestige. Spent currency still counts. Completed projects remain completed after a reset; their multipliers stack to 24x. Era advancement retains existing hardware categories, preventing later eras from disabling already-unlocked production.

### No empty era transitions

The Vacuum Tubes era now starts with a **Thermionic Diode**: visible at 500K earned, costing 1M and producing 50K/s before bonuses. Existing Triodes and their costs/output are unchanged. This bridges the old jump directly to a 10M starter. Shop cards show each owned machine's actual total contribution, including upgrades and research, rather than only its base rate. Entropy Amplification now applies its advertised global production multiplier.

A deterministic entry-saving probe starts with ten clicks and then uses idle income only. With research claimed as it becomes available, its waits after entering Mechanical / Electromechanical / Vacuum Tubes were **19 / 10 / 13 seconds**, with production continuing throughout. These are a specific simulated policy, not guaranteed timing for every play style. Run `python playtest_era_progression.py` to reproduce both research and Define-Bit-only policies.

No save reset is required: saved earlier machines begin contributing again automatically. Explicit rebirth/prestige still reset machine counts.

## Progression Systems

### Motherboard Upgrades (10 Generations)
- Mainframe (1960s) → Apple II → IBM PC → Multimedia → Internet → Mobile → AI → Quantum → Hyper → Singularity
- Each unlocks new hardware categories and increases production

### Data Shards (formerly Compression Tokens)
- Collect at 10K+ bits without resetting
- Based on log10(total_bits_earned) - 3
- Used for compression era mechanics

### Prestige System
- Unlocks at Hardware Generation 3 (Multimedia) + 1M bits
- Awards Quantum Fragments based on sqrt(total_bits) × generation bonus
- Each prestige grants +10% production and +1 click power (stacks infinitely)

## Features

### ✅ Completed
- Complete idle gameplay loop
- 10 motherboard generations with unique hardware categories
- Hardware generators (CPU, RAM, Storage, GPU, Network, Mobile, AI, Quantum, Hyper, Singularity)
- Upgrade system with category-specific bonuses
- Rebirth mechanics with Data Shards rewards
- Compression era with dual currency and efficiency mechanics
- Data Shards collection system (separate from rebirth)
- Prestige system with permanent bonuses
- Readable dashboard, consistent shop cards and era-specific machine illustrations
- Save/load with offline progress
- TOON configuration system
- Visual notifications for upgrades

## Interface

The dashboard uses a quiet charcoal background, sage actions, warm accents and a large currency counter. Hardware and upgrades use matching cards; bright purchase buttons indicate affordability. Hover over a card's text for its full description. The machine illustration is also a click target.

Mechanical now has a working brass gear train, crank and guided carriage, plus a **hinged split-flap register** showing the **low eight digits of your actual balance**. Digits fold around the center seam instead of scrolling vertically. Clicking either historical machine briefly increases its drive speed without changing rewards.

Electromechanical's **8-bit demo tape** runs counting, addition, multiplication, XOR, shifting, Fibonacci, ASCII and parity tasks with changing inputs. **READ → RUN → PUNCH → HOLD** ties the relay scan and punch head to each computed result; program names, inputs and results explain what is happening. The tape holes encode completed demo results, **not player earnings**. A very rare cosmetic message is hidden among the programs, without a currency or progression reward. The fully inset **LOW BYTE** strip separately shows your actual balance modulo 256, bit 7 at left.

Transistors now has a full discrete-logic card instead of a generic chip: six metal-can transistors, color-banded resistors, ceramic capacitors, copper traces and gold edge contacts. A restrained **demo flow** follows the traces. The binary register and hexadecimal readout show the **actual balance modulo 256**, bit 7 at left; they are not simulated earnings. The board remains a normal click target and fits the minimum window.

Reduced Motion freezes gears, relays, signals and tape programs and updates readings instantly without flipping. Motion is independent of the optional particle/background effects. The abacus, Vacuum Tubes and later-era illustrations are unchanged.

The window supports resizing down to **960 × 640**. Shops scroll with the mouse wheel or scrollbar, keeping purchases clipped to the visible area. The bottom discovery bar opens the research journal.

Binary rain, click particles and CRT texture are **off by default**, including a one-time migration for older saves. Settings can re-enable them; reduced motion pauses animated effects. High contrast and visual preferences are saved. No progression or balance is reset by the visual refresh.

## Controls

- **Mouse**: Click buttons, navigate menus
- **R**: Open/close Research roadmap
- **ESC**: Close modals (including Research, settings, rebirth confirmation)
- **Numbers 1-9**: Quick-buy generators (planned)

## Configuration

Game uses TOON format files in `/config/`:
- `game.toon` - Core settings
- `generators.toon` - Generator definitions
- `upgrades.toon` - Upgrade definitions
- `compression_generators.toon` - Compression era generators
- `compression_upgrades.toon` - Compression token upgrades

## Requirements

- Python 3.11+
- Pygame 2.6+

## Save Location

Saves are stored in `bitbybit_save.json` in the game directory.

---

Enjoy discovering the fundamental nature of information! 🎲⭐