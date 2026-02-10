# Bit by Bit - TOON Configuration Guide

This guide explains how to modify the game using TOON configuration files.

## Configuration Files

### `config/game.toon`
Main game settings including colors, display options, and progression parameters.

### `config/generators.toon`
Defines all available generators with their properties:
- `id` - Unique identifier used in code
- `name` - Display name for UI
- `base_cost` - Initial cost
- `base_production` - Base bits per second
- `cost_multiplier` - Growth rate per purchase (1.15 = 15%)
- `icon` - Emoji/symbol for display
- `flavor` - Tooltip/description text
- `unlock_threshold` - Bits needed to unlock (optional)

### `config/upgrades.toon`
Defines all available upgrades:
- `id` - Unique identifier
- `name` - Display name
- `icon` - Symbol for UI
- `base_cost` - Initial cost
- `cost_multiplier` - Growth per level
- `effect` - Numerical effect value
- `max_level` - Maximum purchase level
- `description` - Help text
- `type` - "multiplier" or "additive"
- `unlock_threshold` - Bits needed to unlock (optional)

## Adding New Content

### Adding a New Generator

1. Open `config/generators.toon`
2. Add new entry to the `generators[N]` array:
```toon
  - id: quantum_computer
    name: Quantum Computer
    base_cost: 50000000
    base_production: 5000000
    cost_multiplier: 1.15
    icon: 🖥
    flavor: Leverage quantum superposition for massive computation.
    unlock_threshold: 1073741824  # 1 GB
```

### Adding a New Upgrade

1. Open `config/upgrades.toon`
2. Add new entry to the `upgrades[N]` array:
```toon
  - id: quantum_entanglement
    name: Quantum Entanglement
    icon: 🌌
    base_cost: 1000000
    cost_multiplier: 5
    effect: 25
    max_level: 5
    description: +25% production from quantum generators
    type: multiplier
    unlock_threshold: 1073741824
```

## Balancing Tips

### Generator Balance
- **Cost Multiplier**: 1.10-1.20 (lower = easier progression)
- **Production Tiers**: Each tier should be 8-15x stronger than previous
- **Unlock Thresholds**: Space them every 2-5 minutes of gameplay

### Upgrade Balance
- **Cost Growth**: 3x-10x per level (higher = slower progression)
- **Effect Power**: Match upgrade cost to production benefit
- **Max Levels**: 5-15 levels (prevents infinite scaling)

### Colors
Edit colors in `config/game.toon` using hex format:
```toon
colors:
  electric_cyan: "#00ffff"  # Brighter cyan
  matrix_green: "#00ff00"   # Pure green
  neon_purple: "#ff00ff"   # Magenta instead of purple
```

## Game Balance Presets

### Faster Progression
```toon
progression:
  first_generator: immediate
  second_generator: 60000     # 1 minute at 1 b/s
  third_generator: 300000      # 5 minutes at 1 b/s
  first_rebirth: 900000       # 15 minutes
```

### Slower Progression
```toon
progression:
  first_generator: immediate
  second_generator: 300000     # 5 minutes at 1 b/s  
  third_generator: 1800000     # 30 minutes at 1 b/s
  first_rebirth: 3600000      # 1 hour
```

## Advanced Configuration

### Custom Generators Array
Use TOON arrays for complex generator definitions:
```toon
advanced_generators[3]:
  - id: compression_engine
    name: Compression Engine
    tiers[3]:
      - level: 1
        cost_multiplier: 1.2
        production_bonus: 1.1
      - level: 2
        cost_multiplier: 1.5
        production_bonus: 1.3
      - level: 3
        cost_multiplier: 2.0
        production_bonus: 1.5
```

### Conditional Unlocks
Use TOON objects for complex unlock conditions:
```toon
unlock_conditions:
  rng:
    requirement: click_count >= 5
    reward: tutorial_complete
  biased_coin:
    requirement: bits >= 100
    reward: show_efficiency_tip
```

## Testing Your Changes

1. Save your TOON files
2. Run `python bitbybit_toon.py`
3. Verify new content appears and functions correctly
4. Check console for any parsing errors

## Best Practices

- **Backup Files**: Keep copies of working configurations
- **Test Incrementally**: Change one value at a time
- **Use Comments**: TOON doesn't support comments, but keep notes separate
- **Validate Syntax**: Ensure proper TOON formatting (arrays, objects, primitives)
- **Check Unlock Logic**: Make sure thresholds and progression make sense

## Troubleshooting

### Common TOON Syntax Errors
- **Missing Colons**: Every object key needs `:` 
- **Array Length Mismatch**: `[N]:` must have exactly N items
- **Incorrect Indentation**: Use consistent spaces (default 2)
- **Unescaped Quotes**: Quote strings containing special characters

### Loading Issues
- Check that TOON files are in `config/` directory
- Verify Python can access the files (permissions)
- Check console for parsing error messages
- Ensure all required fields are present

The TOON system makes Bit by Bit highly modular and easy to customize. Experiment with different configurations to create unique gameplay experiences!