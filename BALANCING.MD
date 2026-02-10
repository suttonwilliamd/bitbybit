# BIT BY BIT - Balance & Economy Design

## Core Balancing Philosophy

**Exponential growth with logarithmic effort**
- Player power grows exponentially (2^n, 10^n)
- Time required grows logarithmically (log n)
- Never feel stuck, always progressing

**Soft caps, not hard walls**
- Cost scaling discourages over-investing in one strategy
- No content is impossible to reach
- Multiple viable paths through each era

---

## Cost Curve Analysis

### Generator Cost Growth

Why 1.15x multiplier?

```
At 1.10x: Too shallow - players buy hundreds too easily
At 1.20x: Too steep - feels bad to buy expensive generators
At 1.15x: Sweet spot - sustainable but meaningful scaling
```

**Costs at key quantities (1.15x growth, 10 base)**:
```
1st:     10
10th:    40
25th:    131
50th:    1,083
100th:   11,739
200th:   1,377,564
300th:   161,703,007
```

**Design intent**: First 50 are "cheap", 50-100 "moderate", 100+ "expensive"

### Upgrade Cost Growth

#### Linear Bonuses (Click Power, Synergy)
```
Growth: 3x-5x per level
Max levels: 15-20
```

Diminishing returns prevent infinite scaling.

#### Multiplicative Bonuses (Entropy Amplification)
```
Growth: 10x per level
Effect: 2x production
Max levels: 10
```

**Why 10x cost for 2x production?**
- Prevents dominant strategy
- Encourages diversification
- Each level still worth it, but barely

---

## Production Balancing

### Target: 1000x Growth Per Era

**Entropy Era** (0 → First Rebirth):
- Start: 1 b/s
- End: ~50 Mb/s
- Growth: ~400,000,000x in 30-45 minutes

**Compression Era** (First → Second Rebirth):
- Start: 2 cb/s
- End: ~2 Gb/s compressed
- Growth: ~1,000,000,000x in 30-60 minutes

**Design check**: Does this feel good?
- Yes: Massive power spikes
- Concern: May be too fast - playtest and adjust

### Generator Balance Within Era

Each tier should be ~10-15x stronger than previous:

| Generator | Production | Cost Ratio to Previous |
|-----------|------------|------------------------|
| Tier 1 | 1 | - |
| Tier 2 | 8-10 | 10x |
| Tier 3 | 100-125 | 12x |
| Tier 4 | 1,500-1,800 | 12-15x |
| Tier 5 | 25,000-30,000 | 15x |
| Tier 6 | 400,000-500,000 | 16-20x |

**Rule**: Later tiers more cost-efficient per b/s, but harder to afford

---

## Rebirth Balancing

### Token Earning Rate

**Goal**: 7-15 tokens per rebirth cycle

```
Rebirth 1: 7 tokens  (128 MB)
Rebirth 2: 9 tokens  (512 MB with better production)
Rebirth 3: 11 tokens (2 GB)
Rebirth 4: 13 tokens (8 GB)
```

**Logarithmic formula** ensures:
- Early rebirths worth it (7 tokens meaningful)
- Late rebirths not dramatically better (diminishing returns)
- Encourages frequent rebirths over grinding

### Token Spending Strategy

**New player trap**: Spending all tokens on one upgrade

**Optimal strategy**: Spread across 2-3 key upgrades
- Compression Ratio (2 tokens)
- Parallel Streams (3 tokens)
- Adaptive Learning (5 tokens)

**Total**: 10 tokens for core upgrades
**Implies**: Need ~2 rebirths to get foundation

---

## Efficiency Mechanics

### Overhead Scaling

Base efficiency per generator:
```
Run-Length: 80% (high overhead, cheap)
Huffman: 91% (balanced)
LZ77: 95% (good efficiency)
Arithmetic: 96% (very efficient)
Context Mixer: 95% (slight drop for power)
Neural: 95% (balanced at endgame)
```

**Design**: No generator is "strictly better"
- Early: Cheap + low efficiency
- Late: Expensive + high efficiency
- Tradeoff meaningful

### Efficiency Penalties

| Efficiency | Penalty |
|-----------|---------|
| 90-100% | None |
| 70-89% | -10% production |
| 50-69% | -25% production |
| <50% | -50% production |

**Why penalties?**
- Prevents "ignore efficiency, spam generators" strategy
- Encourages balanced builds
- Makes overhead reduction upgrades valuable

**Concern**: Too punishing? Playtest!

---

## Click vs Idle Balance

### Click Value Decay

```
Time: 0 min    Click: 10b   Idle: 1 b/s     Click value: 10 seconds of idle
Time: 5 min    Click: 50b   Idle: 100 b/s   Click value: 0.5 seconds
Time: 10 min   Click: 100b  Idle: 10k b/s   Click value: 0.01 seconds
```

**Target**: Clicks obsolete by 10 minutes

**Why?**
- This is an idle game - idling should be optimal
- Prevent RSI / auto-clicker meta
- Clicks for engagement early only

---

## Offline Progress

### 75% Efficiency

**Example**:
- Production: 100 Mb/s
- Offline: 8 hours (28,800 seconds)
- Full production: 2,880,000 Mb = 2.88 TB
- **Actual**: 2.88 TB × 0.75 = 2.16 TB

**Rationale**:
- Reward active play (100% efficiency)
- Don't punish taking breaks (75% is good!)
- Prevent "close tab, come back in a week" being optimal

### 24 Hour Cap

Max offline accumulation: 24 hours

**Why cap?**
- Prevents month-long offline = instant win
- Encourages checking in daily
- Balances active vs passive players

---

## Meta-Progression Power

### Token Upgrades Impact

**Compression Ratio** (-5% overhead per level):
```
Level 0: 90% efficiency baseline
Level 1: 90.5% → 5.5% more net production
Level 5: 92.5% → 32% more production
Level 10: 95% → 100% more production (double!)
```

**At 2 tokens per level, 10 levels = 20 tokens**

**Design check**: Is 100% production boost worth 20 tokens?
- Across 3-4 rebirths: YES, excellent value
- But can't afford it early - good pacing

### Parallel Streams

**Value proposition**:
```
Cost: 3, 4, 5, 6 tokens (for streams 2-5)
Benefit: 4 independent generators = ~4x production potential
```

**BUT**: Requires management, costs scale
**Reality**: ~2.5x-3x production in practice

**Worth it?** Yes, if player likes active play

---

## Economy Simulation Results

### Simulated Playthrough (Optimal Strategy)

```
0:00 - Start game
0:03 - First RNG
0:05 - Second RNG
0:10 - First Biased Coin
0:15 - First upgrade (Entropy Amp 1)
0:25 - Unlock Dice Roller
0:35 - REBIRTH at 150 MB (8 tokens)

0:40 - Compression Era start
0:45 - Unlock Huffman
0:55 - Buy Compression Ratio (2 tokens)
1:10 - Unlock LZ77
1:25 - Buy Parallel Streams (3 tokens)
1:50 - Unlock Arithmetic Coder
2:30 - REBIRTH at 40 GB (13 tokens)

2:35 - Channel Era start
3:15 - Unlock AWGN channel
4:00 - Unlock Burst Error
5:00 - REBIRTH at 1.5 TB (15 tokens)

Total time to 3 rebirths: ~5 hours
Total tokens earned: 36
```

**Feels good?** Hard to say without playtesting
**Adjustment knobs**: Cost scaling, production values

---

## Known Balance Risks

### Risk: "Dead Zones"

Periods where player has no meaningful decisions:
- All generators too expensive
- No upgrade affordable
- Just waiting

**Mitigation**:
- Unlock new content regularly
- Ensure always 1-2 affordable options
- Rebirth should be available before dead zone

### Risk: "One True Build"

If one strategy dominates:
- Everyone buys same generators in same order
- No experimentation

**Mitigation**:
- Make multiple generators viable
- Synergies reward diversity
- Personal preference matters (active vs idle)

### Risk: "Runaway Scaling"

If production grows faster than cost:
- Reach endgame in 30 minutes
- No challenge

**Current protection**:
- 1.15x cost growth > production growth rate
- Logarithmic rebirth formula
- Manual tuning of generator values

**Must playtest** to confirm!

---

## Tuning Recommendations

### If Progression Too Slow:
- Reduce cost multiplier: 1.15 → 1.12
- Increase generator production: +20%
- Increase token rewards: +1 per rebirth

### If Progression Too Fast:
- Increase cost multiplier: 1.15 → 1.18
- Reduce generator production: -20%
- Reduce offline efficiency: 75% → 60%

### If Rebirth Timing Off:
- Adjust token formula constant
- Change minimum threshold (128 MB → 256 MB)

**Golden rule**: Make small changes, test frequently