# BIT BY BIT - Game Mechanics & Formulas

## Core Systems

### Currency Generation

#### Base Formula
```
production_per_second = Σ(generator_count[i] × base_production[i] × multipliers)
```

Where multipliers include:
- Upgrade bonuses
- Token bonuses
- Synergy effects
- Era-specific modifiers

#### Update Tick Rate
- **Default**: 1 tick per second (1 Hz)
- **Upgrade**: "Sampling Rate" increases to 2 Hz, 4 Hz, 10 Hz
- **Benefit**: Smoother numbers, faster compound growth perception

### Generator Cost Scaling

#### Formula
```
cost(n) = base_cost × (growth_rate ^ n)
```

**Example** (Random Number Generator):
- base_cost = 10 bits
- growth_rate = 1.15
- cost(0) = 10 bits
- cost(1) = 11.5 bits → rounds to 12 bits
- cost(10) = 40.46 bits
- cost(100) = 11,739 bits

#### Bulk Buy Calculation
```
total_cost_for_n = base_cost × (growth_rate^current_count) × 
                   ((growth_rate^n) - 1) / (growth_rate - 1)
```

This is geometric series sum formula.

### Click Power

#### Formula
```
click_value = 10 × (1 + click_upgrade_level)
```

#### Click Reward Scaling
At high production rates, clicks become negligible. Design intent: Clicks matter early, fade into background.

**Auto-clicker consideration**: Not worth it after ~10 minutes of play.

---

## Rebirth Systems

### First Rebirth: Compression Tokens

#### Token Calculation
```
tokens = floor(log2(total_bits_lifetime) - 20)
```

**Reasoning**:
- 2^20 bits = 1 MB (minimum threshold)
- 2^27 bits = 128 MB → 7 tokens (first rebirth point)
- Log scale rewards exponential growth

#### Optimal Rebirth Timing
**First rebirth**: 128-256 MB
- Too early: Waste time for 1 extra token
- Too late: Slow grinding when reset would speed up

**Subsequent rebirths**: 2-3x previous threshold
- Meta-upgrades provide more value than grinding

### Compression Era Currency

#### Dual Currency System
```
compressed_bits_per_sec = Σ(algorithm_production[i])
overhead_bits_per_sec = Σ(algorithm_overhead[i])

efficiency = compressed / (compressed + overhead)
```

#### Net Value Calculation
```
net_value_per_sec = compressed_bps - (overhead_bps × overhead_penalty)
```

Where `overhead_penalty` starts at 1.0, reduced by upgrades.

### Efficiency Mechanics

#### Why Efficiency Matters
- Below 90% efficiency: Production slows
- Below 70% efficiency: 10% production penalty
- Below 50% efficiency: 25% production penalty
- Below 30% efficiency: Game warns player

**Design**: Encourages balanced generator purchases.

---

## Channel Era Mechanics

### Signal-to-Noise Ratio (SNR)

#### Formula (AWGN Channel)
```
SNR_dB = 10 × log10(signal_power / noise_power)

capacity_bps = bandwidth × log2(1 + SNR)
```

This is **Shannon-Hartley theorem** - the theoretical maximum data rate.

#### Practical Implementation
```
effective_throughput = bandwidth × (1 - error_rate) × modulation_efficiency
```

**Example** (AWGN at 10 dB SNR, 10 MHz bandwidth):
```
SNR_linear = 10^(10/10) = 10
capacity = 10,000,000 × log2(1 + 10) = 34.6 Mbps
```

In-game: We simplify to ~30 Mbps effective for gameplay.

### Error Correction Overhead

#### Hamming Code
```
overhead = 15%
error_correction = 90%
net_throughput = bandwidth × 0.85 × 0.9 = 0.765 × bandwidth
```

#### Reed-Solomon
```
overhead = 30%
error_correction = 99.9%
net_throughput = bandwidth × 0.70 × 0.999 = 0.699 × bandwidth
```

**Trade-off**: More overhead = better reliability, but lower raw speed.

### Modulation Efficiency

| Modulation | Bits/Symbol | Throughput Multiplier | Noise Increase |
|-----------|-------------|----------------------|----------------|
| BPSK | 1 | 1x | 0% |
| QPSK | 2 | 2x | +5% |
| 16-QAM | 4 | 4x | +20% |
| 64-QAM | 6 | 6x | +50% |

**Formula**:
```
effective_bandwidth = base_bandwidth × modulation_multiplier × (1 - noise_increase)
```

---

## Quantum Era Mechanics

### Qubit Decoherence

#### Time-Based Decay
```
coherence(t) = initial_coherence × e^(-t / T2)
```

Where:
- `T2` = coherence time (10 seconds base)
- `t` = time since qubit creation

**Simplified for gameplay**:
```
coherence(t) = max(0, 1 - (t / T2))
```

Linear decay for easier player understanding.

#### Measurement Value
```
classical_bits = qubit_count × coherence × measurement_efficiency
```

**Strategy**: Measure at ~80% coherence for optimal balance.

### Entanglement Bonus

#### Formula
```
if (qubit_A and qubit_B entangled):
    measurement_bonus = 2x
    
if (all_entangled_measured_together):
    measurement_bonus = n × 1.5
```

Where `n` = number of entangled qubits.

**Example**: 4-qubit GHZ state measured together:
```
bonus = 4 × 1.5 = 6x classical bits
```

### Quantum Algorithms

#### Grover's Algorithm (Mini-game)
```
speedup = sqrt(N)
```

Player searches for "marked state" in database of size N.
- Classical: N steps average
- Quantum: sqrt(N) steps

**Reward**: Bonus bits equal to speedup factor × base production.

#### Shor's Algorithm (Passive)
Runs in background, occasionally factors large numbers.
- Each factorization: +10% quantum production for 30 seconds
- Cooldown: 2 minutes

---

## Upgrade Interaction & Stacking

### Multiplicative Bonuses
```
total_multiplier = base × upgrade_1 × upgrade_2 × ... × token_bonus
```

**Example**:
- Base production: 100 bps
- Entropy Amplification level 3: ×8
- Synergy upgrade level 2: ×1.2
- Token bonus: ×1.5
- **Total**: 100 × 8 × 1.2 × 1.5 = 1,440 bps

### Additive Bonuses (Efficiency)
```
total_efficiency = base - overhead_reduction_1 - overhead_reduction_2 - ...
```

**Example**:
- Base efficiency: 85%
- Compression Ratio (token): -10% overhead → 87.8% efficiency
- Overhead Reduction upgrade: -5% overhead → 89.9% efficiency

---

## Save System

### Auto-Save
- **Frequency**: Every 30 seconds
- **Location**: Browser localStorage
- **Format**: JSON

#### Save Data Structure
```json
{
  "version": "1.0.0",
  "timestamp": 1738887600,
  "era": "compression",
  "currencies": {
    "bits": 0,
    "compressed_bits": 15293,
    "overhead": 847,
    "tokens": 8
  },
  "generators": {
    "rng": { "count": 12, "level": 0 },
    "huffman": { "count": 5, "level": 2 }
  },
  "upgrades": {
    "entropy_amp": 4,
    "click_power": 8
  },
  "meta": {
    "total_rebirths": 1,
    "lifetime_bits": 134217728,
    "total_tokens": 23,
    "time_played": 3847
  }
}
```

### Offline Progress
```
offline_time_seconds = current_time - last_save_time
max_offline = 24 hours (86400 seconds)

offline_production = min(offline_time, max_offline) × production_rate × 0.75
```

**75% efficiency** for offline to encourage active play without punishing breaks.

---

## Number Formatting

### Display Formats

#### Standard Notation (Default)
- 0 - 999: "0", "1", ..., "999"
- 1,000 - 999,999: "1,000", "1.5K", "999K"
- 1M - 999M: "1.00M", "1.50M"
- 1B+: "1.00B", "1.50B", etc.

Suffixes: K, M, B, T, Qa, Qi, Sx, Sp, Oc, No, Dc

#### Scientific Notation (Option)
```
1.23e6 (1,230,000)
4.56e12 (4,560,000,000,000)
```

#### Engineering Notation (Option)
```
1.23 × 10^6
4.56 × 10^12
```

#### Data Size Notation (Fits theme!)
```
8,192 bits = 1 KB
8,388,608 bits = 1 MB
8,589,934,592 bits = 1 GB
```

**Conversion**:
```
1 byte = 8 bits
1 kilobyte = 1,024 bytes = 8,192 bits
1 megabyte = 1,024 KB
```

### Precision Rules
- < 10: Show 2 decimal places
- 10-100: Show 1 decimal place
- 100+: Show 0 decimal places (whole numbers)

---

## Balance Targets

### Time to Milestones

| Milestone | Target Time | Notes |
|-----------|-------------|-------|
| First generator | Immediate | Tutorial |
| Second generator | 2-3 minutes | Early engagement |
| First upgrade | 5-7 minutes | Teach upgrade system |
| First rebirth available | 30-45 minutes | Main gameplay loop |
| First rebirth taken | 35-50 minutes | Player chooses timing |
| Second era mastery | +30-60 minutes | Learning compression |
| Second rebirth | +45-90 minutes | Channel era unlock |
| Third rebirth | +60-120 minutes | Quantum era |
| End-game idle | 10-20 hours | Passive optimization |

### Production Growth Rate
```
production_per_rebirth_cycle ≈ 1000x - 10,000x
```

Each rebirth should feel like massive jump in power.

### Cost Growth vs Production Growth
```
cost_growth_rate (1.15^n) < production_growth_rate
```

Ensures player always progressing, never permanently stuck.

---

## Anti-Exploit Measures

### Save Scumming Prevention
- Timestamp validation on load
- Production capped at theoretical max
- Offline progress formula can't be manipulated

### Auto-Clicker Handling
- Click power diminishes in value quickly
- No achievements tied to click count
- No "hold to click" mechanics

### Browser Console Cheating
- Save data checksummed
- Tampering detection logs to analytics (for dev insight)
- No multiplayer = no enforcement needed (single-player game)

**Philosophy**: Let players cheat if they want - it's their experience. But don't make it required or advantageous.

---

## Performance Optimization

### Calculation Frequency
- **Core production**: Every tick (1-10 Hz)
- **UI updates**: Capped at 60 FPS
- **Particle animations**: Budget of 200 particles max
- **Auto-save**: Every 30 seconds (background thread)

### Big Number Library
Use library like `break_infinity.js` or `decimal.js` for:
- Numbers > 1e308 (JavaScript limit)
- Precise calculation
- Exponential notation support

**Critical**: Needed beyond ~1e15 (quadrillion) to avoid precision loss.