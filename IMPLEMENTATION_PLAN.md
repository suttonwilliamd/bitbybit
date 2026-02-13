# Motherboard Upgrade System - Implementation Plan

## Overview
- Replace "Eras" system with **Motherboard Upgrades** as rare thresholds
- Rename "Rebirth" to a new concept (full restart prestige mechanic)
- Convert compression tokens to a separate progression system with new name
- **NOTE: pygame_gui cannot be installed due to pygame version incompatibility (pygame 2.6.1 too new)**
- Will fix existing custom UI code instead

## Phase 1: Visual Fixes (Priority)

- [x] 1.1 Fix ASCII/Unicode character rendering (arrows in panels)
- [x] 1.2 Fix button hover states
- [x] 1.3 Fix hardcoded positions that break on resize
- [x] 1.4 Add missing COLORS["white"] reference in compression_ui.py
- [x] 1.5 Consolidate duplicate format_number() functions

## Phase 2: Motherboard Upgrade System

- [x] 2.1 Define new motherboard generations (10 total, more granular than old eras)
  - [x] Mainframe (1960s) - starting point
  - [x] Apple II (1977)
  - [x] IBM PC (1981)
  - [x] Multimedia (1990s)
  - [x] Internet (2000s)
  - [x] Mobile (2010s)
  - [x] AI Era (2020s)
  - [x] Quantum (future)
  - [x] Hyper (far future)
  - [x] Singularity (endgame)
- [x] 2.2 Create threshold system (like old eras)
- [x] 2.3 Implement hardware category unlocks per motherboard
- [x] 2.4 Add visual upgrade notification UI

## Phase 3: Rebirth/Prestige System

- [x] 3.1 Create prestige mechanic (full restart with bonuses)
- [x] 3.2 Define prestige multipliers/bonuses
- [x] 3.3 Add prestige currency
- [x] 3.4 Track prestige count and apply bonuses
- [x] 3.5 Add rebirth confirmation UI

## Phase 4: Compression Tokens → New System

- [x] 4.1 Rename compression tokens to new name (suggest: "Data Shards")
- [x] 4.2 Make it a separate progression from motherboard upgrades
- [x] 4.3 Keep compression mechanics but detach from rebirth

## Phase 5: Testing & Polish

- [x] 5.1 Test save/load with new systems
- [x] 5.2 Verify game balance with new thresholds
- [x] 5.3 Clean up old code
- [x] 5.4 Add documentation
