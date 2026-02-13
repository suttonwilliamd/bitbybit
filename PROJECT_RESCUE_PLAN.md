# BIT BY BIT - PROJECT RESCUE PLAN

## Strategic Direction
- **Visual Style**: Sleek futuristic terminal (cyberpunk/neon aesthetic)
- **Priority**: Fix visuals first, then content
- **Compatibility**: Breaking saves is acceptable for proper architecture

---

## EXECUTIVE SUMMARY

This is an idle/incremental game about information theory with a "computer hardware evolution" theme. The game has substantial systems in place but suffers from significant visual/design issues that make it feel broken. This plan addresses the core problems and provides a path to a polished, cohesive game.

---

## CURRENT STATE

### ✅ Working Systems
- Game state management with full progression tracking
- Two eras: Entropy Era → Compression Era
- 10 Hardware Generations: Mainframe → Singularity
- Motherboard Bit Grid visual component system
- Rebirth System with Data Shards
- Prestige System with Quantum Fragments
- TOON Configuration System (custom parser)
- Save/Load with offline progress
- Visual effects: binary rain, particles, bit visualizations

### ❌ Critical Visual Issues
1. Panel titles floating (not integrated with panels)
2. Orphaned BUY buttons (not attached to cards)
3. Icon rendering (emojis showing as vertical bars)
4. Card layout cramped with overlapping text
5. No rounded corners (sharp edges look dated)
6. Panel backgrounds unclear (blending into background)
7. Three competing visual centers (Information Core, Bit Grid, Compression Panel)

---

## PHASE 1: VISUAL FOUNDATION (Priority Fixes)

### 1.1 Replace Panel Rendering
**Files**: gui/cards.py, gui/__init__.py

**Changes**:
- Create `draw_panel_with_integrated_title()` function
- Title text INSIDE the panel in dedicated title bar
- Title bar uses slightly lighter background color
- Separator line under title
- Replace all `draw_panel_toggle()` calls

### 1.2 Fix Card System
**Files**: gui/cards.py

**Changes**:
- Each card owns its own BUY x1/x10 buttons
- Icon rendered as 48px emoji in dedicated left area (60x60 square)
- Clear text hierarchy: Name (bright white) → Quantity/Rate (muted blue) → Cost (gold)
- Proper spacing between elements
- Rounded corners (border_radius=8)

### 1.3 Add Rounded Corners System
**Apply to**: All UI elements
- Cards: border_radius=8
- Panels: border_radius=10
- Buttons: border_radius=4

### 1.4 Fix Icon Rendering
- Use larger font size (42px minimum)
- Center emoji in dedicated icon area
- Provide text fallback if emoji rendering fails

---

## PHASE 2: ARCHITECTURE REFACTOR

### 2.1 Unify Configuration System
**Problem**: TOON config files exist but constants.py has hardcoded fallbacks that override them

**Solution**:
- Make TOON the single source of truth
- Remove duplicate hardcoded CONFIG in constants.py
- Load all game data from config files

### 2.2 Streamline Visual Systems
**Problem**: Three competing centers distract from core gameplay

**Solution**:
- Entropy Era: Focus on Information Core + Bit Grid
- Compression Era: Focus on Compression Panel only
- Remove redundant visual elements

### 2.3 Component Unification
**Problem**: Bit Grid, generators, and upgrades are disconnected

**Solution**:
- Integrate hardware categories with Bit Grid components
- Visual feedback when purchasing connects to grid

---

## PHASE 3: POLISH

### 3.1 Enable CRT Effects By Default
- Currently off by default - enable for aesthetic
- Add to visual settings toggle

### 3.2 Consistent Color Palette
- All elements use COLORS dictionary from constants.py
- Remove hardcoded RGB tuples scattered in code

### 3.3 Particle/Animation Polish
- Satisfying click effects with visual feedback
- Purchase feedback with particles flying to accumulator
- Smooth transitions between states

### 3.4 Typography System
- Define font hierarchy (title, heading, body, caption)
- Consistent sizing throughout

---

## IMPLEMENTATION ORDER

```
1. gui/cards.py      - Panel and card rendering fixes
2. gui/__init__.py   - Update draw calls to use new system
3. constants.py      - Remove duplicate hardcoded configs
4. visual_effects.py - Polish particle effects
5. Testing          - Verify all systems work correctly
```

---

## SUCCESS CRITERIA

1. All panels have integrated title bars
2. All cards contain their own action buttons
3. Icons render properly as emojis
4. Consistent rounded corners throughout
5. Visual hierarchy is clear (background → panel → card → action)
6. No orphaned UI elements
7. Game runs at 60fps without visual glitches

---

## RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing saves | Medium | Document save format changes; provide migration path |
| Visual changes too drastic | Low | User asked for breaking changes |
| Performance issues | Low | Keep particle limits, test on lower-end systems |

---

## FUTURE ENHANCEMENTS (Post-Rescue)

- Achievement system
- Animated tutorial system
- Sound effects and music
- Cloud saves
- Multiplayer (stretch goal)
- Additional hardware generations beyond Singularity

---

*Plan created: 2026-02-13*
*Status: IN PROGRESS - Phase 1*
