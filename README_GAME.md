# BIT BY BIT - Information Theory Game

## Quick Start

### Option 1: Double-click `start_game.bat`
This launches the full game with all features:
- Entropy Era (bits and generators)
- Rebirth system with Data Shards
- Compression Era (dual currency, efficiency mechanics)
- Motherboard Upgrade System (10 generations)
- Prestige System (Quantum Fragments)
- Rich visual effects and animations
- Save/load with offline progress

### Option 2: Run from command line
```bash
python main.py
```

## Game Progression

1. **Start**: Click to generate bits, buy first generator
2. **Entropy Era**: Build up hardware, unlock categories
3. **Rebirth**: Reset for Data Shards, advance motherboard generation
4. **Data Shards**: Collect at 10K+ bits (separate from rebirth)
5. **Hardware Generations**: 10 levels from Mainframe to Singularity
6. **Prestige** (at Gen 3+): Full reset for Quantum Fragments + permanent bonuses

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
- Spectacular visual effects and animations
- Save/load with offline progress
- TOON configuration system
- Visual notifications for upgrades

## Controls

- **Mouse**: Click buttons, navigate menus
- **ESC**: Close modals (settings, rebirth confirmation)
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