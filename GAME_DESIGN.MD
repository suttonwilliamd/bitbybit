# BIT BY BIT - Complete Game Design Document

## Table of Contents
1. [Game Overview](#game-overview)
2. [What the Player Sees](#what-the-player-sees)
3. [Game Progression](#game-progression)
4. [Core Mechanics](#core-mechanics)
5. [Currency Systems](#currency-systems)
6. [Generators and Hardware](#generators-and-hardware)
7. [Upgrade Systems](#upgrade-systems)
8. [Rebirth and Prestige](#rebirth-and-prestige)
9. [Visual Systems](#visual-systems)
10. [UI and Controls](#ui-and-controls)
11. [Save System](#save-system)

---

## Game Overview

**Bit by Bit** is a desktop idle/incremental game built with Python and Pygame, themed around information theory. Players generate "bits" (the fundamental unit of information), unlock increasingly advanced computing hardware, and discover the fundamental nature of information through gameplay mechanics inspired by real information theory concepts like entropy, compression, and channel capacity.

The game features a cyberpunk/terminal aesthetic with deep blue backgrounds, electric cyan highlights, neon purple accents, and matrix green success indicators.

---

## What the Player Sees

### Initial Launch Screen

When the player first launches the game, they see:

**1. Title Bar**
- Window title: "Bit by Bit - A Game About Information"
- Standard window controls (minimize, maximize, close)

**2. Top Header Area**
- Current currency display (bits, compressed bits, etc.)
- Production rate (bits per second)
- Hardware generation indicator (e.g., "Mainframe Era", "Apple II Era")
- Prestige currency display (if applicable)

**3. Center: Information Core / Accumulator**
- A large circular or rectangular clickable area
- Animated visual showing data accumulation
- Current bit count prominently displayed
- Production rate shown below
- Click button for manual generation

**4. Motherboard Bit Grid (Center-Upper)**
- A grid of hardware components arranged in a motherboard-style layout
- Components: CPU → BUS → RAM/GPU/STORAGE
- Each component displays:
  - Component name (e.g., "CPU Lv.1")
  - Description (e.g., "64-bit Registers")
  - Individual bit cells that fill up as progress is made
  - Progress bar showing level advancement
- Locked components show a lock icon with grayed-out appearance
- Connected components have animated data flow lines between them

**5. Left Panel: Hardware Generators**
- Scrollable panel titled "HARDWARE"
- Lists all available generators organized by category
- Each generator card displays:
  - Generator icon (emoji)
  - Generator name
  - Current owned count
  - Production rate contribution
  - Cost for next purchase
  - Buy buttons (x1, x10)
  - Progress bar to next affordable purchase
- Locked generators show unlock requirements

**6. Right Panel: Upgrades**
- Scrollable panel titled "UPGRADES"
- Lists all available upgrades
- Each upgrade card displays:
  - Upgrade icon (emoji)
  - Upgrade name
  - Current level
  - Effect description
  - Cost for next level
  - Buy button

**7. Bottom: Rebirth Progress Bar**
- Shows progress toward next rebirth/compression
- Displays threshold (e.g., "COMPRESS AT 128 MB")
- Progress percentage and current/target values
- "COMPRESS DATA" button appears when ready

**8. Header Buttons**
- ⚙️ CONFIG (settings)
- 📊 STATUS (statistics)

### Visual Theme and Colors

**Primary Colors:**
- Deep Space Blue: `#0a0e27` (background)
- Electric Cyan: `#00aadc` (active data, highlights)
- Neon Purple: `#a05ae6` (compressed data, premium elements)
- Matrix Green: `#39ff14` (generation rates, positive)
- Signal Orange: `#ff8c5a` (overhead, warnings)
- Gold: `#ffd700` (tokens, premium currency)

**UI Layers:**
- Panel backgrounds: `#161923`
- Card backgrounds: `#1c2030`
- Text: Soft white `#f0f5ff`

---

## Game Progression

### Phase 1: Entropy Era (Initial Gameplay)

**Starting Point:**
- Player begins with 0 bits
- Can manually click to generate bits (+1 per click initially)
- Only Random Number Generator (RNG) is available

**Early Progression (0-1,000 bits):**
1. Click accumulator to generate first bits
2. Buy Random Number Generator (RNG) at 10 bits
3. RNG produces 1 bit/second passively
4. Reach 100 bits → unlock Biased Coin
5. Reach 1,000 bits → unlock Upgrades panel and Dice Roller

**Mid-Game Progression (1,000 - 100,000 bits):**
1. Purchase generators for passive income
2. Buy Entropy Amplification upgrade (doubles all production)
3. Buy Click Power upgrade (+1 bit per click)
4. Unlock additional generators as total bits earned increases
5. Progress through hardware categories by earning more bits

**Hardware Category Unlocks:**
- CPU: Available from start
- RAM: Unlocks at 10% of rebirth threshold
- Storage: Unlocks at 5-10% of rebirth threshold (varies by generation)
- GPU: Unlocks at higher thresholds
- Network, Mobile, AI, Quantum, Hyper, Singularity: Unlock at later generations

### Phase 2: Compression Era (After First Rebirth)

After performing the first rebirth (compression):

**New Currency Display:**
- Compressed bits (primary, shown in neon purple)
- Overhead (secondary, shown in signal orange)
- Efficiency percentage (compression ratio)

**New Generator Types:**
- Compression algorithms replace basic generators
- Each algorithm produces compressed bits but generates overhead
- Efficiency = compressed / (compressed + overhead)

**Data Shard System:**
- Collect shards without resetting (at 10K+ bits earned since last collection)
- Formula: shards = floor(log10(bits_since_collect)) - 3
- Spend shards on powerful meta-upgrades

**Efficiency Mechanics:**
- 90%+ efficiency: Full production
- 70-90% efficiency: 10% penalty
- 50-70% efficiency: 25% penalty
- Below 50%: 50% penalty
- Efficiency floor upgrades can mitigate penalties

### Phase 3: Hardware Generations

The game features 10 hardware generations representing computing history:

| Generation | Name | Unlock Categories | Rebirth Threshold |
|------------|------|-------------------|-------------------|
| 0 | Mainframe Era (1960s) | CPU | 9,728 bits |
| 1 | Apple II Era (1977) | CPU, RAM | 150,016 bits |
| 2 | IBM PC Era (1981) | CPU, RAM, Storage | 1,114,112 bits |
| 3 | Multimedia Era (1990s) | CPU, RAM, Storage, GPU | 46,137,344 bits |
| 4 | Internet Era (2000s) | + Network | 10,884,218,880 bits |
| 5 | Mobile Era (2010s) | + Mobile | 1,832,519,377,920 bits |
| 6 | AI Era (2020s) | + AI | 111,669,149,696 bits |
| 7 | Quantum Era | + Quantum | 43,980,465,111,040 bits |
| 8 | Hyper Era | + Hyper | 175,921,860,444,160 bits |
| 9 | Singularity Era | + Singularity | 703,687,441,776,640 bits |

Each advancement:
- Unlocks new hardware categories
- Increases rebirth threshold
- Awards bonus tokens on rebirth

### Phase 4: Prestige System

Available after Hardware Generation 3 (Multimedia Era) + 1 million total bits:

**Prestige Reset:**
- Resets all progress completely
- Awards Quantum Fragments based on sqrt(total_bits) × generation bonus

**Prestige Bonuses:**
- +10% production per prestige (stacks infinitely)
- +1 click power per prestige (stacks infinitely)

---

## Core Mechanics

### Bit Generation

**Manual Generation (Clicking):**
```
click_power = 1 + (click_upgrade_level × 1) + prestige_click_bonus
```
- Base: 1 bit per click
- Each Click Power upgrade level: +1 bit
- Each prestige: +1 additional bit

**Passive Generation:**
```
production_per_second = Σ(generator_count × base_production × multipliers)
```

Multipliers applied (multiplicative):
- Entropy Amplification: 2^level (Level 10 = 1024×)
- Hardware category upgrades: 2^level per category
- Prestige bonus: 1 + (prestige_count × 0.1)
- Achievement multipliers (if any)

### Generator Cost Scaling

Standard formula for all generators:
```
cost(n) = base_cost × (cost_multiplier ^ n)
```

Where:
- n = current quantity owned
- cost_multiplier = 1.15 (standard) or 1.12 (compression era)

**Bulk Purchase Cost:**
```
total_cost = base_cost × (growth_rate^count) × ((growth_rate^quantity) - 1) / (growth_rate - 1)
```

### Upgrade System

**Basic Upgrades:**

| Upgrade | Effect | Max Level | Cost Multiplier |
|---------|--------|-----------|-----------------|
| Entropy Amplification | 2× production per level | 10 | 10× |
| Click Power | +1 bit per click per level | 15 | 3× |

**Hardware Category Upgrades:**
Each hardware category has an associated upgrade that doubles production for that category:

| Category | Upgrade Name | Max Level |
|----------|-------------|-----------|
| CPU | CPU Overclock | 5 |
| RAM | Memory Optimization | 5 |
| Storage | Data Compression | 5 |
| GPU | Ray Tracing | 5 |
| Network | Bandwidth Boost | 5 |
| Mobile | Battery Efficiency | 5 |
| AI | Neural Network | 5 |
| Quantum | Quantum Entanglement | 5 |
| Hyper | Hyper Parallelism | 5 |
| Singularity | Transcendence | 5 |

**Data Shard Upgrades (Compression Era):**

| Upgrade | Effect | Cost Scale |
|---------|--------|------------|
| Compression Mastery | +X% compressed production | Linear |
| Parallel Streams | +X% per generator type | Linear |
| Efficiency Shield | +X% minimum efficiency floor | Linear |
| Entropy Barrier | -X% penalty threshold | Linear |
| Quick Collect | -X% collection threshold | Linear |
| Shard Doubler | +X% rebirth shard bonus | Linear |

---

## Currency Systems

### Primary Currency: Bits

**Generation Sources:**
- Manual clicking
- Entropy generators (RNG, Biased Coin, Dice Roller, etc.)
- Hardware generators (CPU Core, Memory Stick, etc.)

**Display:**
- Format: Whole numbers, K (thousands), M (millions), B (billions), T (trillions)
- Threshold for K: 1,000
- Threshold for M: 1,000,000
- Threshold for B: 1,000,000,000
- Threshold for T: 1,000,000,000,000

### Secondary Currency: Compressed Bits (Compression Era)

**Generation:**
- Produced by compression algorithm generators
- Represents actual information content (after compression)

**Overhead:**
- Generated alongside compressed bits
- Represents inefficiency in compression
- Reduces efficiency percentage

**Efficiency Calculation:**
```
efficiency = compressed_bits / (compressed_bits + overhead)
```

### Tertiary Currency: Data Shards

**Earning Methods:**

1. **On Rebirth:**
   ```
   shards = floor(log2(total_bits_lifetime) - 20)
   ```
   - 128 MB = 7 shards
   - 1 GB = 10 shards
   - 10 GB = 13 shards

2. **Collection (No Reset):**
   ```
   shards = floor(log10(bits_since_collect)) - 3
   ```
   - Requires 10,000+ bits since last collection
   - Can collect multiple times per run

### Prestige Currency: Quantum Fragments

**Earning Formula:**
```
fragments = sqrt(total_bits_earned) / 100 × (1 + generation × 0.5)
```

**Requirements:**
- Hardware Generation ≥ 3
- Total bits earned ≥ 1,000,000

---

## Generators and Hardware

### Basic Generators (Entropy Era)

| Generator | Base Cost | Production | Unlock Threshold | Flavor Text |
|-----------|-----------|------------|-----------------|-------------|
| Random Number Generator | 10 | 1 b/s | None | "Pure chaos. Maximum entropy." |
| Biased Coin | 100 | 8 b/s | 100 bits | "Not all outcomes are equal." |
| Dice Roller | 1,200 | 100 b/s | 1,000 bits | "Six possible states." |

### Hardware Generators (By Category)

**CPU Category:**
| Generator | Base Cost | Production |
|-----------|-----------|------------|
| CPU Core | 50 | 5 b/s |
| CPU Cache | 500 | 50 b/s |

**RAM Category:**
| Generator | Base Cost | Production |
|-----------|-----------|------------|
| Memory Stick | 200 | 20 b/s |
| Memory Bank | 2,000 | 200 b/s |

**Storage Category:**
| Generator | Base Cost | Production |
|-----------|-----------|------------|
| Hard Drive | 1,000 | 100 b/s |
| Solid State (SSD) | 10,000 | 1,000 b/s |

**GPU Category:**
| Generator | Base Cost | Production |
|-----------|-----------|------------|
| Graphics Card | 5,000 | 500 b/s |
| Tensor Core | 50,000 | 5,000 b/s |

**Network Category:**
| Generator | Base Cost | Production |
|-----------|-----------|------------|
| Ethernet Card | 3,000 | 300 b/s |
| Fiber Optic | 30,000 | 3,000 b/s |

**Mobile Category:**
| Generator | Base Cost | Production |
|-----------|-----------|------------|
| Mobile Chip | 15,000 | 1,500 b/s |

**AI Category:**
| Generator | Base Cost | Production |
|-----------|-----------|------------|
| AI Accelerator | 100,000 | 10,000 b/s |

**Quantum Category:**
| Generator | Base Cost | Production |
|-----------|-----------|------------|
| Quantum Processor | 500,000 | 50,000 b/s |
| Qubit Register | 1,000,000 | 100,000 b/s |

**Hyper Category:**
| Generator | Base Cost | Production |
|-----------|-----------|------------|
| Hyper Cluster | 5,000,000 | 500,000 b/s |
| Dimension Gate | 10,000,000 | 1,000,000 b/s |

**Singularity Category:**
| Generator | Base Cost | Production |
|-----------|-----------|------------|
| Singularity Core | 50,000,000 | 5,000,000 b/s |

### Compression Generators (Post-Rebirth)

These generate compressed bits but produce overhead:

| Generator | Base Cost | Production | Overhead |
|-----------|-----------|------------|----------|
| Run-Length Encoder | 5 cb/s | +2 cb/s | -0.5 b/s |
| Huffman Tree | 80 cb/s | +20 cb/s | -2 b/s |
| LZ77 Dictionary | 1,000 cb/s | +300 cb/s | -15 b/s |
| Arithmetic Coder | 15,000 cb/s | +5,000 cb/s | -200 b/s |
| Context Mixer | 250,000 cb/s | +80,000 cb/s | -4,000 b/s |
| Neural Compressor | 4,000,000 cb/s | +1,500,000 cb/s | -80,000 b/s |

---

## Upgrade Systems

### Basic Upgrades

**Entropy Amplification:**
- Cost: 1,000 bits × 10^level
- Effect: Multiplies ALL production by 2^level
- Max Level: 10 (total 1024× multiplier)

**Click Power:**
- Cost: 500 bits × 3^level
- Effect: +1 bit per click per level
- Max Level: 15

### Hardware Upgrades

Each hardware category has a category-specific upgrade that doubles production for that category:

- Cost: Category base × 5^level
- Effect: 2× multiplier per level for that category
- Max Level: 5 (total 32× for that category)

### Data Shard Upgrades

Purchased with Data Shards (Compression Era meta-upgrades):

| Upgrade | Effect Per Level | Base Cost |
|---------|-----------------|-----------|
| Compression Mastery | +10% production | 1 shard |
| Parallel Streams | +5% all streams | 2 shards |
| Efficiency Shield | +5% minimum efficiency | 3 shards |
| Ententropy Barrier | -5% penalty threshold | 3 shards |
| Quick Collect | -10% collection threshold | 2 shards |
| Shard Doubler | +25% rebirth shards | 5 shards |

---

## Rebirth and Prestige

### Rebirth (Compression Cycle)

**Trigger Condition:**
- Accumulate bits equal to current era's threshold
- Achieve 99.9%+ completion on motherboard bit grid

**What Happens:**
1. Lose all bits, generators, and upgrades
2. Gain Data Shards (tokens) based on lifetime bits
3. Advance to next hardware generation (if available)
4. Enter Compression Era mechanics (first rebirth only)

**Token Formula:**
```
tokens = floor(log2(total_bits_lifetime) - 20) + (generation × 5) × (1 + shard_bonus)
```

**Rebirth Thresholds by Generation:**
- Gen 0 (Mainframe): 9,728 bits
- Gen 1 (Apple II): 150,016 bits
- Gen 2 (IBM PC): 1,114,112 bits
- Gen 3 (Multimedia): 46,137,344 bits
- Gen 4 (Internet): 10.8 billion bits
- Gen 5 (Mobile): 1.8 trillion bits
- And so on...

### Prestige (Quantum Fragments)

**Trigger Condition:**
- Hardware Generation ≥ 3
- Total bits earned ≥ 1,000,000

**What Happens:**
1. Full reset of all progress
2. Award Quantum Fragments
3. Keep prestige currency permanently

**Prestige Currency Formula:**
```
fragments = sqrt(total_bits_earned) / 100 × (1 + generation × 0.5)
```

**Prestige Bonuses (Permanent):**
- Production: +10% per prestige
- Click Power: +1 per prestige

---

## Visual Systems

### CRT Effects
- Scanline overlay
- Subtle screen curvature effect
- Phosphor glow on bright elements

### Binary Rain
- Background animation of falling binary digits (0s and 1s)
- Slow-moving, atmospheric effect
- Can be toggled in settings

### Particle Effects

**Click Particles:**
- Burst of green particles on click
- Floating "+X" text showing click value

**Purchase Particles:**
- Cyan particles when buying generators
- Purple particles when buying upgrades

### Motherboard Bit Grid

**Visual Representation:**
- Components as colored rectangles
- Individual bit cells (small squares) within each component
- Data flow animations along connection lines

**Component States:**
- Locked: Gray background, lock icon
- Unlocked: Colored background, functional
- Full: All bit cells filled

**Bit Cell Behavior:**
- Fill based on progress toward rebirth threshold
- Distribute across unlocked components
- Higher level = more bit capacity

### Compression Era Visuals

**Dual Currency Display:**
- Split display showing compressed bits and overhead
- Color-coded (purple for compressed, orange for overhead)

**Efficiency Meter:**
- Animated bar showing compression efficiency
- Color changes based on efficiency level:
  - 80%+: Green
  - 50-80%: Cyan
  - Below 50%: Orange/Red

**Token Display:**
- Gold star icon with pulse animation
- Particle effects on collection

---

## UI and Controls

### Mouse Controls

**Left Click:**
- Generate bits (on accumulator)
- Purchase generators
- Purchase upgrades
- Interact with buttons
- Click confirmation dialogs

**Mouse Wheel:**
- Scroll hardware panel
- Scroll upgrades panel

**Scrollbar Interaction:**
- Click track to jump
- Drag thumb to scroll
- Hover for highlight

### Keyboard Controls

| Key | Action |
|-----|--------|
| Up Arrow | Scroll panels up |
| Down Arrow | Scroll panels down |
| Page Up | Scroll panels up 5× |
| Page Down | Scroll panels down 5× |
| Home | Scroll to top |
| End | Scroll to bottom |
| ESC | Close modals/settings |

### Modal Dialogs

**Settings Panel:**
- CRT Effects toggle
- Binary Rain toggle
- Particle Effects toggle
- Export/Import Save
- Reset Progress button

**Statistics Panel:**
- Current run stats (time, bits, efficiency)
- Lifetime stats (rebirths, tokens, play time)
- Hardware generation info

**Rebirth Confirmation:**
- Shows what will be lost
- Shows what will be gained (tokens)
- Confirm/Cancel buttons

**Prestige Confirmation:**
- Shows Quantum Fragments to be earned
- Explains permanent bonuses
- Confirm/Cancel buttons

### Layout

**Responsive Design:**
- Minimum window: 1200×800
- Resizable with proper scaling
- Panels adjust to window size

**Panel Organization:**
- Left: Hardware/Generators (22% width)
- Center: Motherboard, Accumulator, Rebirth bar
- Right: Upgrades (22% width)

---

## Save System

### Auto-Save

- **Interval:** Every 30 seconds
- **Location:** `bitbybit_save.json`
- **Triggers:** On interval, on window close

### Save Data Structure

```json
{
  "version": "1.0.0",
  "timestamp": 1738887600,
  "bits": 15293,
  "total_bits_earned": 134217728,
  "total_clicks": 1234,
  "era": "entropy",
  "hardware_generation": 2,
  "generators": {
    "rng": {"count": 12, "total_bought": 15},
    "cpu_core": {"count": 5, "total_bought": 5}
  },
  "upgrades": {
    "entropy_amplification": {"level": 3},
    "overclock": {"level": 2}
  },
  "data_shards": 15,
  "total_data_shards": 23,
  "prestige_currency": 5,
  "prestige_count": 2,
  "bit_grid": {...},
  "visual_settings": {...}
}
```

### Offline Progress

- **Calculation:** min(offline_time, 24 hours) × production_rate × 0.75
- **Efficiency:** 75% of online rate
- **Maximum:** 24 hours of offline progress

### Backup System

- Automatic backup on each save
- Keeps 3 backup files
- `bitbybit_save.json.backup`

---

## Achievement System

Achievements track milestones and reward players:

**Categories:**
- Clicking: Click-related achievements
- Generators: Generator ownership achievements
- Upgrades: Upgrade-related achievements
- Progression: Bit milestone achievements
- Compression: Rebirth achievements
- Prestige: Prestige achievements
- Special: Hidden/special achievements

**Example Achievements:**
- "Hello World": Click for the first time
- "RNG Enthusiast": Buy first generator
- "Kilobit": Earn 1,000 total bits
- "Megabit": Earn 1,000,000 total bits
- "Data Compression": Complete first rebirth
- "Quantum Leap": Perform first prestige

---

## Quest System

**Tutorial Quests:**
- Guided introduction to game mechanics
- Progressive unlocks
- Rewards for completion

**Quest Structure:**
- Objectives (with progress tracking)
- Rewards (bits, generators, upgrades)
- Prerequisites (previous quests)

**Example Tutorial Quests:**
1. "Generate Bits": Click accumulator to generate 1 bit
2. "Automate It": Buy first RNG
3. "Growing Pains": Reach 100 total bits
4. "Power Up": Buy first upgrade
5. "Kilobit Club": Earn 1,000 total bits

---

## Configuration System

The game uses TOON (Token-Oriented Object Notation) for configuration:

**Config Files:**
- `config/game.toon` - Main settings
- `config/generators.toon` - Generator definitions
- `config/upgrades.toon` - Upgrade definitions
- `config/compression_generators.toon` - Compression algorithms
- `config/compression_upgrades.toon` - Data shard upgrades
- `config/balance.toon` - Balance values
- `config/achievements.toon` - Achievement definitions
- `config/quests.toon` - Quest definitions

---

## Technical Details

**Engine:** Python 3.11+ with Pygame 2.6+

**Performance Targets:**
- 60 FPS
- Max 100 particles
- Efficient number formatting

**Window:**
- Default size: 1200×800
- Resizable
- Minimum size enforced

**Input:**
- Mouse (click, hover, scroll)
- Keyboard (navigation, shortcuts)

---

## Design Philosophy and Justifications

### Core Design Principles

**1. Educational Yet Entertaining**

The game bridges abstract information theory concepts with tangible gameplay. Every mechanic (entropy, compression, channel capacity) is grounded in real computer science principles, but abstracted enough to remain fun. The player learns about Shannon entropy, Huffman coding, and LZ77 compression without feeling like they're reading a textbook.

*Justification:* This creates a unique identity among idle games. Players come for the gameplay, but leave understanding why compression works and how information is measured.

**2. Fair Free-to-Play Without Paywalls**

The game is entirely single-player with no microtransactions. All content is accessible through normal play. There are no "energy" systems, no waiting for regeneration, and no paid advantages.

*Justification:* This design philosophy respects player time and creates genuine satisfaction in progression. The dopamine hits come from achievement, not purchase.

**3. Respects Player Time**

- Auto-save every 30 seconds prevents losing progress
- Offline progress at 75% efficiency allows meaningful gains while away
- Bulk purchase options (x1, x10) reduce click fatigue
- Clear milestone markers show progress

*Justification:* Idle games are often played in background while doing other things. Respecting this by not forcing active engagement while still rewarding it creates a healthy game-play loop.

**4. Meaningful Choices Over Optimal Path**

Players must decide between:
- Buying more generators vs. upgrading existing ones
- Rebirthing early for faster progress vs. waiting for more tokens
- Focusing on one hardware category vs. diversifying

*Justification:* True idle game satisfaction comes from strategic decisions, not just number go up. The prestige system rewards different approaches.

**5. Visibility of Progress**

Multiple progress indicators ensure players always know where they stand:
- Motherboard bit grid shows visual progress toward rebirth
- Progress bars on generators show distance to next purchase
- Efficiency meter in compression era shows mathematical progress
- Statistics panel tracks historical performance

*Justification:* Seeing progress, not just the goal, is what makes incremental games satisfying.

### Number Design Choices

**Cost Multiplier: 1.15**

A 15% cost increase per purchase is aggressive enough to prevent trivial accumulation but forgiving enough to allow steady progress. This creates the classic idle game "treadmill" feel.

*Justification:* 1.15× is the standard in the genre ( Cookie Clicker, A Dark Room) because it creates exponential cost growth that eventually outpaces linear production gains, forcing players to rebirth.

**Upgrade Multiplier: 2× Per Level**

Each Entropy Amplification level doubles production. At max level (10), this is 1024× total - a massive boost that feels transformative.

*Justification:* Large, impactful upgrades feel more rewarding than small incremental boosts. The 2× power makes each purchase exciting.

**Rebirth Threshold: Exponential Growth**

Each hardware generation increases rebirth threshold by approximately 15.5×, creating dramatic difficulty spikes that require rebirths to overcome.

*Justification:* Without exponential thresholds, players would eventually reach a "stuck" state where progress is impossible. The threshold increase ensures each generation feels meaningfully different.

---

## Information Theory Connections

### Entropy Era

**Shannon Entropy as Gameplay**

In information theory, entropy measures the uncertainty/information content of a message. The formula:

```
H = -Σ p(x) × log₂(p(x))
```

In the game:
- Random Number Generator represents maximum entropy (1 bit per outcome)
- Biased Coin represents reduced entropy (predictable outcomes = less surprise = less information per flip, but more flips needed)
- Dice Roller with 6 states produces log₂(6) ≈ 2.58 bits per roll

*Design Note:* This isn't just flavor - understanding entropy helps players optimize by preferring higher-entropy sources.

### Compression Era

**Redundancy Removal as Mechanic**

Real compression algorithms work by finding and removing redundancy. The game simulates this:

- Run-Length Encoding: Simple repetition removal (AAAAAAA → 7A)
- Huffman Coding: Variable-length codes for frequency
- LZ77: Dictionary-based compression
- Neural Compression: Learn patterns, then compress

The overhead system simulates real compression trade-offs:
- Better compression algorithms often have higher "setup costs"
- The efficiency metric mirrors real compression ratios

### Channel Era (Planned)

**Shannon-Hartley Theorem**

The planned channel era would implement:

```
C = B × log₂(1 + S/N)
```

Where:
- C = Channel capacity (maximum data rate)
- B = Bandwidth
- S/N = Signal-to-noise ratio

This represents actual communication theory - you can't push more data through a channel than its capacity, regardless of encoding tricks.

### Quantum Era (Planned)

**Qubit Mechanics**

Planned quantum mechanics would implement:
- Superposition: Probabilistic states
- Entanglement: Correlated measurements
- Decoherence: Time-limited coherence
- No-Cloning Theorem: Quantum states can't be copied

---

## Technical Architecture

### Module Structure

```
bit by bit/
├── main.py              # Entry point
├── game_loop.py         # Main game loop
├── game_state.py        # Core game state management
├── constants.py         # Configuration and constants
├── visual_effects.py    # Particle systems, animations
├── ui_components.py     # UI building blocks
├── bit_grid.py          # Motherboard visualization
├── input_handler.py     # Input processing
├── balance.py           # Balance configuration loader
├── achievements.py      # Achievement system
├── quests.py            # Quest system
├── compression_ui.py   # Compression era UI
├── toon_parser.py      # Custom config format parser
├── gui/
│   ├── __init__.py     # Main GUI class
│   ├── panels.py       # Scrollable panels
│   ├── cards.py        # Generator/upgrade cards
│   ├── modals.py       # Dialog windows
│   ├── accumulator.py  # Click target
│   ├── effects.py      # Visual effects
│   ├── top_bar.py      # Header display
│   ├── rebirth_bar.py  # Rebirth progress
│   └── ...
└── config/
    ├── game.toon       # Main settings
    ├── generators.toon # Generator definitions
    ├── upgrades.toon   # Upgrade definitions
    └── ...
```

### Class Responsibilities

**GameState**
- Holds all mutable game data
- Calculates production rates
- Manages generators and upgrades
- Handles rebirth/prestige logic

**BitByBitGame (GUI)**
- Window management
- Event handling
- Drawing/rendering
- UI interaction

**MotherboardBitGrid**
- Visual representation of progress
- Component layout and rendering
- Animation of data flow

**ScrollablePanel**
- Content scrolling
- Scrollbar interaction

### Data Flow

```
User Input → Event Handler → GameState.update() → State Change → UI Update → Render
```

The game runs at 60 FPS, but production calculates per-second and applies via delta-time accumulation to avoid floating-point drift.

### State Management

Game state is entirely client-side (single-player). State includes:
- Current currencies
- Generator/upgrade counts
- Unlocked content
- Lifetime stats
- Visual preferences

### Save Format

JSON-based with versioning:
```json
{
  "version": "1.0.0",
  "timestamp": 1738887600,
  ...
}
```

Version field allows future migration if save format changes.

---

## Balance Philosophy

### Progression Pacing

**First 30 Minutes**

The game is designed to reach first rebirth in 30-45 minutes of active play. This is:
- Long enough to understand mechanics
- Short enough to not feel tedious
- Rewarding enough to want to continue

**Rebirth Value**

First rebirth grants 7-10 tokens. This is designed to:
- Provide meaningful upgrade choices
- Not be so many that choices don't matter
- Allow noticeable progression difference

**Generator Tiers**

Each generator tier is ~10× the cost and production of the previous:
- Allows gradual upgrading
- Creates natural progression milestones
- Prevents skipping tiers entirely

### Efficiency vs. Power

The dual-currency compression system creates an interesting choice:
- High power generators often have overhead
- Must balance compressed bits (good) vs. overhead (bad)
- Efficiency upgrades become valuable

This prevents the "just buy the most expensive thing" problem seen in simpler idle games.

### Prestige Balance

Prestige bonuses (+10% production, +1 click) are small enough that:
- First prestige doesn't break the game
- Multiple prestiges create meaningful scaling
- Late-game remains challenging

The requirement (Gen 3+ and 1M bits) ensures players understand all systems before prestige complexity.

---

## Accessibility Considerations

### Visual Accessibility

**High Contrast Mode**
- Black/white color scheme
- Increased border thickness
- Solid colors instead of gradients

**Reduced Motion**
- Disable particle effects
- Disable binary rain
- Instant transitions

**Colorblind-Friendly Colors**
- Avoid red/green only distinctions
- Use shapes + colors for indicators
- Matrix green + cyan + purple are distinguishable

### Input Accessibility

**Keyboard Navigation**
- Full keyboard support for all actions
- Tab navigation through panels
- ESC to close modals
- Arrow keys for scrolling

**Mouse Alternatives**
- Click, not hold
- Scrollbar for fine control
- Clear hover states

### Cognitive Accessibility

**Clear Information Hierarchy**
- Currency prominently displayed
- Production rates near currency
- Secondary info in panels

**Tutorial System**
- Guided first steps
- Contextual hints
- Clear unlock messages

---

## Performance Considerations

### Frame Rate Target

60 FPS with graceful degradation:
- Max 100 particles
- Efficient text caching
- Lazy UI updates

### Number Handling

Python integers are arbitrary precision, but display formatting handles large numbers:
- Under 1000: Show whole number
- 1K-1M: Show with K suffix
- 1M-1B: Show with M suffix
- And so on...

This prevents UI overflow while maintaining accuracy.

### Memory Management

- Save file is minimal JSON
- No asset loading (procedural graphics)
- Particle pooling
- Text surface caching

### Delta Time

Production uses delta-time accumulation:
```
accumulator += production_rate × dt
if accumulator >= 1:
    bits += int(accumulator)
    accumulator -= int(accumulator)
```

This ensures accurate production regardless of frame rate.

---

## Configuration System: TOON Format

### Why TOON?

The game uses a custom "Token-Oriented Object Notation" format for configuration:

**Advantages over JSON:**
- Line-oriented (easier to read/edit)
- Indentation-based structure
- No closing braces
- Comments allowed
- Explicit array headers

**Example:**
```toon
generators[3]:
  - id: rng
    name: Random Number Generator
    base_cost: 10
    base_production: 1
```

### Loading Flow

```
config/*.toon → toon_parser.py → Python dicts → GameState/CONFIG
```

This allows:
- Easy balancing without code changes
- Modding support
- A/B testing
- Community customization

### Fallback System

If TOON parsing fails, hardcoded defaults in constants.py ensure the game still runs.

---

## Implementation Notes

### Floating Point Precision

The game uses standard Python float for production, but:
- Currencies stored as integers where possible
- Display formatting handles precision
- Delta-time accumulation prevents drift

### Event Processing

Events processed in priority order:
1. Window events (quit, resize)
2. Modal events (rebirth, settings, stats)
3. Game events (clicks, purchases)
4. Scroll events

### Rendering Order

1. Background gradient
2. Circuit board background
3. Binary rain (if enabled)
4. Bit grid visualization
5. UI panels
6. Particles/effects
7. CRT overlay (if enabled)

This ensures proper layering and no visual glitches.

### Save Safety

- Write to temp file first
- Atomic rename on success
- Keep 3 backups
- Validate on load

---

## Future Considerations

### Planned but Not Fully Implemented

**Channel Era**
- 6 channel types (BSC, AWGN, Burst, Fading, MIMO, Quantum)
- Signal-to-noise ratio mechanics
- Forward error correction
- Modulation schemes (BPSK, QPSK, QAM)

**Quantum Era**
- Qubit mechanics
- Entanglement bonuses
- Decoherence timers
- Grover's/Shor's algorithm mini-games

**Enhanced Achievements**
- More achievement categories
- Achievement-based rewards
- Achievement tracking UI

**Multiplayer (Considered but Unlikely)**
- Leaderboards
- Challenges
- Shared prestige

### Known Limitations

- No cloud save
- No mod loader (config editing required)
- Single window only
- No fullscreen mode
- Windows-focused (some font issues on Linux/Mac)

### Potential Improvements

- Sound effects (partially implemented in design)
- Music/soundtrack
- More detailed statistics graphs
- Export/import to different formats
- Achievement showcase
- Quest tracking UI

---

## Conclusion

Bit by Bit represents a thoughtful take on the idle game genre, combining:
- Educational information theory themes
- Deep progression systems
- Respect for player time
- Accessible design
- Technical robustness
- Extensive configurability

The game can be played casually for hours or deeply optimized for maximum efficiency. Whether players engage with the educational aspects or just enjoy watching numbers grow, the core loop provides satisfying progression through computing history.

The use of actual information theory concepts creates a unique identity - players inadvertently learn about entropy, compression, and channel capacity while enjoying a well-crafted idle game. This educational aspect, combined with the technical implementation using TOON configuration and modular architecture, makes Bit by Bit both a fun game and an interesting technical project.
