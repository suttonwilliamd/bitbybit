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
4. **Advance eras**: After defining bits, earn the displayed total and select **ADVANCE** in Research. This does not spend your balance or reset progress. Historical generators only produce in their own era, so buy the new era's hardware.
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