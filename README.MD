# Bit by Bit - Pygame Implementation

A desktop game about information theory where players generate bits, unlock compression algorithms, and discover the fundamental nature of information.

## How to Play

1. **Install requirements**: `pip install pygame` (or run requirements.txt)
2. **Start the game**: Run `python bitbybit_game.py` or use the launcher scripts
3. **Generate bits**: Click the accumulator to generate your first bits
4. **Buy generators**: Purchase automated generators to produce bits passively
5. **Get upgrades**: Buy permanent upgrades to boost production
6. **Progress**: Unlock new generators and features as you generate more information
7. **Reach milestones**: Work toward 128 MB to unlock compression (available in full version)

## Quick Start

### Original Pygame Version:
```bash
# Double-click start_game.bat
# Or run in terminal:
python bitbybit_game.py
```

### TOON Edition (Recommended):
```bash
# Double-click start_toon_game.bat
# Or run in terminal:
python bitbybit_toon.py
```

### Virtual Environment:
```bash
# Create virtual environment
python -m venv bitbybit_env

# Activate
# Windows:
bitbybit_env\Scripts\activate
# macOS/Linux:
source bitbybit_env/bin/activate

# Install requirements
pip install pygame

# Run game
python bitbybit_toon.py
```

## Features Implemented (MVP)

### Core Gameplay
- ✅ Click-to-generate mechanism with visual feedback
- ✅ 3 generators: Random Number Generator, Biased Coin, Dice Roller
- ✅ 1.15x cost scaling for balanced progression
- ✅ Bulk purchasing (buy x1, buy x10)

### Upgrade System
- ✅ Entropy Amplification: 2x production multiplier
- ✅ Click Power: +10 bits per click per level
- ✅ Max levels and cost scaling

### User Interface
- ✅ Beautiful dark theme with cyberpunk aesthetics
- ✅ Animated accumulator with visual bit representation
- ✅ Responsive design for desktop and mobile
- ✅ Smooth animations and particle effects
- ✅ Progress tracking toward rebirth (compression)

### Quality of Life
- ✅ Auto-save every 30 seconds
- ✅ Manual save/export functionality
- ✅ Offline progress (75% efficiency, capped at 24 hours)
- ✅ Statistics tracking
- ✅ Settings panel with toggles
- ✅ Tutorial system for new players
- ✅ Number formatting (K, M, B notation)

### Technical Features
- ✅ LocalStorage save system
- ✅ Pause when tab is inactive
- ✅ Responsive design
- ✅ Sound effects (toggleable)
- ✅ Particle effects (toggleable)
- ✅ Keyboard accessibility

## Game Balance

The MVP is balanced for the first 30 minutes of gameplay:

- **First generator**: Immediate (tutorial)
- **Second generator**: ~2-3 minutes (100 bits)
- **Third generator**: ~10-15 minutes (1,000 bits)
- **First upgrade**: ~5-7 minutes (1,000 bits)
- **Rebirth available**: ~30-45 minutes (128 MB)

## File Structure

```
bit by bit/
├── bitbybit_toon.py   # TOON-powered game (RECOMMENDED)
├── bitbybit_game.py   # Original Pygame version
├── toon_parser.py      # TOON format parser
├── config/             # TOON configuration files
│   ├── game.toon       # Main game settings
│   ├── generators.toon  # Generator definitions
│   └── upgrades.toon   # Upgrade definitions
├── start_toon_game.bat # TOON game launcher (Windows)
├── start_game.bat       # Original game launcher
├── requirements.txt     # Python dependencies
├── index.html          # Original web version (non-working)
├── styles.css          # Original web styles
├── script.js           # Original web script
├── DESIGN.MD           # Original game design document
├── MECHANICS.MD        # Technical mechanics documentation
└── README.MD           # This file
```

## Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## How to Run Locally

### Method 1: Direct Launch (Recommended)
```bash
# Install pygame
pip install pygame

# Run the game
python bitbybit_game.py
```

### Method 2: Using Launcher Scripts
- **Windows**: Double-click `start_game.bat`
- **macOS/Linux**: Run `./start_game.sh`

### Method 3: Virtual Environment
```bash
# Create virtual environment
python -m venv bitbybit_env

# Activate
# Windows:
bitbybit_env\Scripts\activate
# macOS/Linux:
source bitbybit_env/bin/activate

# Install requirements
pip install -r requirements.txt

# Run game
python bitbybit_game.py
```

## Game Controls

- **Mouse**: Navigate menus and click buttons
- **Left Click**: Generate bits, buy generators, purchase upgrades
- **ESC**: Quit game (auto-saves automatically)
- **Close Window**: Quit and save progress

## Pygame Features

### Fully Functional
- ✅ **Working click button** with collision detection
- ✅ **Generator system** with bulk purchasing
- ✅ **Upgrade system** with level progression
- ✅ **Visual effects** (particles, floating text)
- ✅ **Tutorial system** for new players
- ✅ **Save/load system** with offline progress
- ✅ **Responsive UI** with cyberpunk aesthetics

### Technical Improvements Over Web Version
- **Reliable clicking** - No JavaScript issues
- **Smooth performance** - 60 FPS gameplay
- **Better controls** - Native mouse handling
- **File-based saves** - Easy backup and sharing
- **Desktop experience** - Full-screen capable

## Future Development

This MVP implements the first era (Entropy Era). Future versions will include:

- **Compression System**: Full rebirth mechanics with compression tokens
- **Additional Generators**: 3 more entropy era generators
- **Compression Era**: New generators and dual currency system
- **Channel Era**: Communication channels with noise mechanics
- **Quantum Era**: Qubits and quantum mechanics
- **Achievement System**: 80+ achievements with rewards
- **Enhanced Statistics**: Graphs and detailed analytics

## Technical Notes

- **Pygame 2.6.1** for graphics and input
- **Python 3.11+** compatible
- **JSON save system** with offline progress
- **60 FPS** smooth gameplay
- **Cross-platform** (Windows, macOS, Linux)
- **No external assets** - procedurally generated graphics

## Game Philosophy

Bit by Bit is designed around the core concepts of information theory:
- **Entropy**: Raw, random data generation
- **Compression**: Finding patterns and removing redundancy
- **Communication**: Transmitting information efficiently
- **Quantum**: The fundamental limits of information

Each era represents a paradigm shift in how we understand and manipulate information, making abstract concepts tangible through gameplay.

## TOON Configuration System

The game now uses the **TOON (Token-Oriented Object Notation)** format for configuration:

#### What is TOON?
- **Line-oriented** format with indentation-based structure
- **Human-readable** - Minimal quoting, clear syntax
- **Explicit structure** - Array headers declare length and fields
- **Deterministic** - Consistent encoding and parsing

#### Configuration Files:
- **`config/game.toon`** - Main settings, colors, display options
- **`config/generators.toon`** - Generator definitions with unlock thresholds
- **`config/upgrades.toon`** - Upgrade definitions and costs

#### Example Generator Configuration:
```toon
generators[3]:
  - id: rng
    name: Random Number Generator
    base_cost: 10
    base_production: 1
    cost_multiplier: 1.15
    icon: 🎲
    flavor: Pure chaos. Maximum entropy.
```

#### Benefits:
- **Easy Balancing** - Edit TOON files to adjust costs/production
- **Add Content** - Add new generators by editing `generators.toon`
- **Version Control** - Track changes in text format with Git
- **Mod Support** - Community can create mod configurations

### Technical Notes

- **TOON Parser** - Custom parser for loading configuration
- **Pygame 2.6.1** for graphics and input
- **Python 3.11+** compatible
- **JSON save system** with offline progress
- **60 FPS** smooth gameplay
- **Cross-platform** (Windows, macOS, Linux)
- **No external assets** - Procedurally generated graphics
- **Configuration-driven** - All values loaded from TOON files

---

Enjoy discovering the nature of information, one bit at a time! 🎲✨

**Two Versions Available:**
- **TOON Edition** (`bitbybit_toon.py`) - Uses TOON configuration (Recommended)
- **Original Version** (`bitbybit_game.py`) - Hardcoded configuration