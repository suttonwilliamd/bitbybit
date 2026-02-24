"""
Accumulator drawing functions
"""

import pygame
import math
import random
from constants import COLORS, CONFIG, FPS, format_number, ERAS


class AccumulatorDisplayState:
    """Holds display state for smooth number animations"""
    def __init__(self):
        self.display_compressed_bits = 0
        self.display_rate = 0
        self.display_bits = 0


_accumulator_state = AccumulatorDisplayState()


def draw_accumulator(screen, state, bit_grid, compression_panel, compression_meter,
                     token_display, compression_progress, current_width, current_height,
                     base_width, base_height, monospace_font, medium_font, small_font, COLORS):
    """Draw accumulator based on era"""
    global _accumulator_state
    
    # Check computing era for early-game visuals (Abacus, Mechanical, etc.)
    current_computing_era = getattr(state, 'current_era', 0)
    
    # Draw era-specific accumulator for early eras
    if current_computing_era == 0:
        draw_abacus_accumulator(screen, state, current_width, current_height,
                              base_width, base_height, monospace_font, medium_font, small_font, COLORS,
                              _accumulator_state)
        return
    elif current_computing_era == 1:
        draw_mechanical_accumulator(screen, state, current_width, current_height,
                                  base_width, base_height, monospace_font, medium_font, small_font, COLORS,
                                  _accumulator_state)
        return
    
    if state.era == "compression":
        draw_compression_accumulator(
            screen, state, compression_panel, compression_meter, token_display,
            compression_progress, current_width, current_height, monospace_font, medium_font, COLORS,
            _accumulator_state
        )
    else:
        draw_standard_accumulator(
            screen, state, bit_grid, current_width, current_height,
            base_width, base_height, monospace_font, medium_font, small_font, COLORS,
            _accumulator_state
        )


def draw_compression_accumulator(screen, state, compression_panel, compression_meter,
                                 token_display, compression_progress, current_width, current_height,
                                 monospace_font, medium_font, COLORS, display_state):
    """Draw enhanced accumulator for compression era"""
    production_rate = state.get_production_rate()
    
    compression_panel.draw(
        screen,
        getattr(state, 'compressed_bits', 0),
        getattr(state, 'data_shards', 0),
        getattr(state, 'efficiency', 1.0) * 100,
        production_rate
    )
    
    compression_meter.draw(screen, getattr(state, 'efficiency', 1.0) * 100)
    
    token_display.draw(screen, getattr(state, 'compression_tokens', 0), medium_font)
    
    compression_ratio = getattr(state, 'efficiency', 1.0)
    compression_progress.set_progress(min(compression_ratio / 10, 1.0))
    compression_progress.draw(screen)
    
    smoothing_factor = 0.1
    display_state.display_compressed_bits += (
        getattr(state, 'compressed_bits', 0) - display_state.display_compressed_bits
    ) * smoothing_factor
    display_state.display_rate += (
        state.get_production_rate() - display_state.display_rate
    ) * smoothing_factor

    scale_x = current_width / 1920
    scale_y = current_height / 1080
    center_x = current_width // 2
    
    bits_y = int(320 * scale_y)
    bits_str = f"{format_number(int(display_state.display_compressed_bits))} COMPRESSED BITS"
    bits_text = monospace_font.render(bits_str, True, COLORS["neon_purple"])
    bits_rect = bits_text.get_rect(center=(center_x, bits_y))

    for offset, alpha in [((3, 3), 20), ((2, 2), 40), ((1, 1), 60), ((-1, -1), 50), ((-2, -2), 30)]:
        glow_pos = (bits_rect.x + offset[0], bits_rect.y + offset[1])
        glow_surface = bits_text.copy()
        glow_surface.set_alpha(alpha)
        screen.blit(glow_surface, glow_pos)

    screen.blit(bits_text, bits_rect)

    rate_y = int(350 * scale_y)
    efficiency = getattr(state, 'efficiency', 1.0) * 100
    rate_str = f"+{format_number(int(display_state.display_rate))} cb/s @ {efficiency:.1f}% efficiency"
    rate_text = medium_font.render(rate_str, True, COLORS["electric_cyan"])
    rate_rect = rate_text.get_rect(center=(center_x, rate_y))

    for offset, alpha in [((2, 2), 30), ((-1, -1), 60)]:
        glow_pos = (rate_rect.x + offset[0], rate_rect.y + offset[1])
        glow_surface = rate_text.copy()
        glow_surface.set_alpha(alpha)
        screen.blit(glow_surface, glow_pos)

    screen.blit(rate_text, rate_rect)


def draw_standard_accumulator(screen, state, bit_grid, current_width, current_height,
                              base_width, base_height, monospace_font, medium_font, small_font, COLORS, display_state):
    """Draw accumulator focused on the bit grid (motherboard components)"""
    global _accumulator_state
    
    dt = 1 / FPS

    scale_x = current_width / base_width
    scale_y = current_height / base_height

    side_panel_width = int(current_width * 0.22)
    center_x = side_panel_width + 20
    center_width = current_width - (side_panel_width * 2) - 40

    # Make accumulator fill more space for the bit grid
    acc_width = int(min(750 * scale_x, center_width - 20))
    acc_height = int(480 * scale_y)
    acc_x = center_x + (center_width - acc_width) // 2
    acc_y = int(95 * scale_y)

    # Position bit grid to fill the accumulator
    grid_padding = int(50 * scale_x)
    bit_grid.x = acc_x + grid_padding
    bit_grid.y = acc_y + int(50 * scale_y)
    bit_grid.width = acc_width - grid_padding * 2
    bit_grid.height = acc_height - int(70 * scale_y)
    bit_grid.update_dimensions(bit_grid.x, bit_grid.y, bit_grid.width, bit_grid.height)

    bit_grid.update(
        state.bits,
        state.total_bits_earned,
        CONFIG.get("VISUAL_FILL_THRESHOLD", 1024 * 1024),
        state.hardware_generation,
        dt,
        state.get_production_rate(),
    )

    acc_rect = pygame.Rect(acc_x, acc_y, acc_width, acc_height)
    cx = center_x + center_width // 2

    # Clean dark background
    pygame.draw.rect(screen, (5, 8, 18), acc_rect, border_radius=8)

    # ===== TITLE =====
    title_text = small_font.render("◈ MOTHERBOARD ◈", True, COLORS["muted_blue"])
    title_rect = title_text.get_rect(center=(cx, acc_y + int(20 * scale_y)))
    screen.blit(title_text, title_rect)

    # ===== BIT GRID (THE STAR) =====
    # Draw connections and components - this is what matters
    bit_grid.draw(screen)

    # ===== PROGRESS TO REBIRTH =====
    bit_percent = bit_grid.get_bit_completeness_percentage()
    
    # Progress bar at bottom
    bar_w = int(300 * scale_x)
    bar_h = 6
    bar_x = cx - bar_w // 2
    bar_y = acc_y + acc_height - int(25 * scale_y)
    
    # Bar background
    pygame.draw.rect(screen, (20, 25, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
    
    # Bar fill with color based on progress
    fill_w = int(bar_w * bit_percent / 100)
    if fill_w > 0:
        bar_color = COLORS["matrix_green"]
        if bit_percent > 50:
            bar_color = (80, 255, 80)
        if bit_percent > 80:
            bar_color = COLORS["gold"]
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill_w, bar_h), border_radius=3)
    
    # Progress text
    pct_text = small_font.render(f"REBIRTH PROGRESS: {bit_percent:.1f}%", True, COLORS["muted_blue"])
    pct_rect = pct_text.get_rect(center=(cx, bar_y - 12))
    screen.blit(pct_text, pct_rect)


def _draw_binary_stream(screen, x, y_start, char_height, COLORS):
    """Draw animated binary digits streaming down the side of accumulator"""
    time_ms = pygame.time.get_ticks()
    
    num_digits = 8
    binary_font = pygame.font.Font(None, 18)
    
    for i in range(num_digits):
        offset = (time_ms // 300 + i * 50) % 300
        y_pos = y_start + i * char_height - (offset / 10)
        
        seed = (time_ms // 1000 + i) % 2
        digit = "1" if seed else "0"
        
        color = COLORS["matrix_green"] if digit == "1" else (30, 80, 30)
        alpha = 180 if digit == "1" else 80
        
        text_surface = binary_font.render(digit, True, color)
        text_surface.set_alpha(alpha)
        screen.blit(text_surface, (x, y_pos))


class DataShardUpgradeCard:
    """Clickable data shard upgrade card"""
    def __init__(self, x, y, width, height, upgrade_id, upgrade_data):
        self.rect = pygame.Rect(x, y, width, height)
        self.upgrade_id = upgrade_id
        self.upgrade_data = upgrade_data
        self.hovered = False
    
    def contains(self, pos):
        return self.rect.collidepoint(pos)


def draw_data_shard_upgrades(screen, state, panel_rect, small_font, medium_font, COLORS):
    """Draw data shard upgrade cards in the compression panel"""
    upgrades = getattr(state, 'data_shard_upgrades', {})
    data_shards = getattr(state, 'data_shards', 0)
    
    if not upgrades:
        return []
    
    cards = []
    card_width = int(panel_rect.width / 3) - 10
    card_height = 80
    start_y = panel_rect.y + 130
    spacing = 5
    
    upgrade_list = list(upgrades.items())
    for i, (upgrade_id, upgrade) in enumerate(upgrade_list):
        row = i // 3
        col = i % 3
        
        card_x = panel_rect.x + col * (card_width + spacing)
        card_y = start_y + row * (card_height + spacing)
        
        card = DataShardUpgradeCard(card_x, card_y, card_width, card_height, upgrade_id, upgrade)
        cards.append(card)
        
        current_level = upgrade.get("level", 0)
        max_level = upgrade.get("max_level", 1)
        is_maxed = current_level >= max_level
        
        cost = state.get_data_shard_upgrade_cost(upgrade_id) if not is_maxed else None
        can_afford = cost is not None and data_shards >= cost
        
        bg_color = (30, 35, 50) if not is_maxed else (40, 45, 60)
        if card.hovered and can_afford:
            bg_color = (40, 50, 70)
        elif card.hovered:
            bg_color = (25, 28, 40)
        
        pygame.draw.rect(screen, bg_color, card.rect, border_radius=8)
        
        border_color = COLORS["gold"] if can_afford else (80, 80, 100)
        if is_maxed:
            border_color = COLORS["matrix_green"]
        pygame.draw.rect(screen, border_color, card.rect, 2, border_radius=8)
        
        icon = upgrade.get("icon", "💎")
        icon_surface = medium_font.render(icon, True, COLORS["soft_white"])
        screen.blit(icon_surface, (card.rect.x + 8, card.rect.y + 5))
        
        name = upgrade.get("name", upgrade_id)
        name_surface = small_font.render(name, True, COLORS["soft_white"])
        screen.blit(name_surface, (card.rect.x + 35, card.rect.y + 5))
        
        level_text = f"{current_level}/{max_level}"
        level_surface = small_font.render(level_text, True, COLORS["muted_blue"])
        screen.blit(level_surface, (card.rect.x + 35, card.rect.y + 22))
        
        effect_type = upgrade.get("effect_type", "")
        effect_per_level = upgrade.get("effect_per_level", 0)
        effect_desc = upgrade.get("description", "")
        
        if effect_per_level > 0:
            bonus = current_level * effect_per_level
            if "percent" in effect_type:
                bonus_text = f"+{bonus}%"
            else:
                bonus_text = f"+{bonus}"
            bonus_surface = small_font.render(bonus_text, True, COLORS["matrix_green"])
            screen.blit(bonus_surface, (card.rect.x + 8, card.rect.y + 45))
        
        if is_maxed:
            max_text = "MAX"
            max_surface = small_font.render(max_text, True, COLORS["matrix_green"])
            screen.blit(max_surface, (card.rect.x + card_width - 35, card.rect.y + card_height - 18))
        elif cost is not None:
            cost_text = f"💎{cost}"
            cost_color = COLORS["gold"] if can_afford else COLORS["signal_orange"]
            cost_surface = small_font.render(cost_text, True, cost_color)
            screen.blit(cost_surface, (card.rect.x + card_width - 50, card.rect.y + card_height - 18))
    
    return cards


# =============================================================================
# ERA-SPECIFIC ACCUMULATORS
# Abacus Era and Mechanical Era visual rendering
# =============================================================================

def draw_abacus_accumulator(screen, state, current_width, current_height,
                           base_width, base_height, monospace_font, medium_font, small_font, COLORS, display_state):
    """Draw abacus-style accumulator for Era 0"""
    
    scale_x = current_width / base_width
    scale_y = current_height / base_height
    
    # Calculate positions
    side_panel_width = int(current_width * 0.22)
    center_x = side_panel_width + 20
    center_width = current_width - (side_panel_width * 2) - 40
    
    acc_width = int(min(700 * scale_x, center_width - 20))
    acc_height = int(500 * scale_y)
    acc_x = center_x + (center_width - acc_width) // 2
    acc_y = int(80 * scale_y)
    
    cx = acc_x + acc_width // 2
    
    # Draw wooden frame background with wood grain effect
    frame_color = (101, 67, 33)  # Dark wood
    pygame.draw.rect(screen, frame_color, (acc_x, acc_y, acc_width, acc_height), border_radius=8)
    
    # Wood grain lines
    for i in range(0, acc_height, 8):
        pygame.draw.line(screen, (90, 55, 25), (acc_x, acc_y + i), (acc_x + acc_width, acc_y + i), 1)
    
    pygame.draw.rect(screen, (70, 45, 20), (acc_x, acc_y, acc_width, acc_height), 4, border_radius=8)
    
    # Title - "ABACUS" with nicer styling
    title_surf = small_font.render("◈ ABACUS ◈", True, (210, 180, 140))
    title_rect = title_surf.get_rect(center=(cx, acc_y + int(25 * scale_y)))
    screen.blit(title_surf, title_rect)
    
    # Draw the abacus frame (inner rectangle) with shadow
    abacus_inner_x = acc_x + int(30 * scale_x)
    abacus_inner_y = acc_y + int(60 * scale_y)
    abacus_inner_w = acc_width - int(60 * scale_x)
    abacus_inner_h = acc_height - int(120 * scale_y)
    
    # Inner background (cream/parchment color)
    pygame.draw.rect(screen, (240, 225, 195), (abacus_inner_x, abacus_inner_y, abacus_inner_w, abacus_inner_h))
    pygame.draw.rect(screen, (80, 55, 25), (abacus_inner_x, abacus_inner_y, abacus_inner_w, abacus_inner_h), 4)
    
    # Draw vertical frame pieces (left and right)
    pygame.draw.rect(screen, (90, 60, 30), (abacus_inner_x - 8, abacus_inner_y, 12, abacus_inner_h))
    pygame.draw.rect(screen, (90, 60, 30), (abacus_inner_x + abacus_inner_w - 4, abacus_inner_y, 12, abacus_inner_h))
    
    # Draw horizontal frame pieces (top and bottom)
    pygame.draw.rect(screen, (90, 60, 30), (abacus_inner_x - 8, abacus_inner_y - 8, abacus_inner_w + 20, 12))
    pygame.draw.rect(screen, (90, 60, 30), (abacus_inner_x - 8, abacus_inner_y + abacus_inner_h - 4, abacus_inner_w + 20, 12))
    
    # Draw 4 horizontal rods (metallic look)
    rod_spacing = abacus_inner_h / 5
    for i in range(1, 5):
        rod_y = abacus_inner_y + i * rod_spacing
        # Rod shadow
        pygame.draw.line(screen, (100, 90, 70), (abacus_inner_x + 25, rod_y + 2), 
                       (abacus_inner_x + abacus_inner_w - 25, rod_y + 2), 5)
        # Rod
        pygame.draw.line(screen, (180, 160, 120), (abacus_inner_x + 25, rod_y), 
                       (abacus_inner_x + abacus_inner_w - 25, rod_y), 3)
        # Rod highlight
        pygame.draw.line(screen, (210, 190, 150), (abacus_inner_x + 25, rod_y - 1), 
                       (abacus_inner_x + abacus_inner_w - 25, rod_y - 1), 1)
    
    # Calculate beads based on bits
    max_beads = 40  # 4 rods * 10 beads
    beads_filled = min(max_beads, int(state.bits / 100))
    
    bead_radius = int(min(rod_spacing, abacus_inner_w / 25) / 2) - 3
    
    # Draw beads on each rod
    for bead_idx in range(max_beads):
        rod = bead_idx // 10
        bead = bead_idx % 10
        rod_y = abacus_inner_y + (rod + 1) * rod_spacing
        
        left_x = abacus_inner_x + 35
        right_x = abacus_inner_x + abacus_inner_w - 35 - bead_radius * 2
        bead_spacing = (right_x - left_x) / 9
        
        # Position: left side if not filled, right side if filled
        if bead_idx < beads_filled:
            bx = right_x - (9 - bead) * bead_spacing
        else:
            bx = left_x + bead * bead_spacing
        
        by = rod_y - bead_radius
        
        # Draw bead shadow
        pygame.draw.ellipse(screen, (80, 60, 30), (bx + 2, by + 2, bead_radius * 2, bead_radius * 2))
        
        # Draw bead with gradient effect
        bead_rect = (bx, by, bead_radius * 2, bead_radius * 2)
        
        if bead_idx < beads_filled:
            # Darker wood for moved beads
            pygame.draw.ellipse(screen, (140, 90, 40), bead_rect)
        else:
            # Lighter wood for unmoved beads
            pygame.draw.ellipse(screen, (205, 165, 105), bead_rect)
        
        # Bead highlight
        pygame.draw.ellipse(screen, (230, 200, 140), (bx + 3, by + 2, bead_radius, bead_radius))
        
        # Bead outline
        pygame.draw.ellipse(screen, (60, 40, 20), bead_rect, 2)
    
    # Click instruction with pulsing effect
    pulse = (math.sin(pygame.time.get_ticks() / 300.0) + 1) / 2  # 0 to 1
    click_color = (150 + int(pulse * 50), 120 + int(pulse * 30), 70)
    click_text = small_font.render("[ CLICK ABACUS TO ADD PEBBLES ]", True, click_color)
    click_rect = click_text.get_rect(center=(cx, acc_y + acc_height - int(25 * scale_y)))
    screen.blit(click_text, click_rect)
    
    # Show pebbles count with nice formatting
    pebble_count = getattr(state, 'pebbles', state.bits)
    currency_text = monospace_font.render(f"{format_number(pebble_count)}", True, (60, 40, 15))
    currency_rect = currency_text.get_rect(center=(cx, acc_y + int(42 * scale_y)))
    
    # Currency background
    curr_bg_w = currency_rect.width + 40
    curr_bg_h = currency_rect.height + 16
    curr_bg_x = cx - curr_bg_w // 2
    curr_bg_y = currency_rect.y - 8
    pygame.draw.rect(screen, (220, 200, 160), (curr_bg_x, curr_bg_y, curr_bg_w, curr_bg_h), border_radius=6)
    pygame.draw.rect(screen, (80, 55, 25), (curr_bg_x, curr_bg_y, curr_bg_w, curr_bg_h), 2, border_radius=6)
    screen.blit(currency_text, currency_rect)
    
    # Currency label
    label_text = small_font.render("pebbles", True, (100, 80, 50))
    label_rect = label_text.get_rect(center=(cx, currency_rect.y + currency_rect.height + 12))
    screen.blit(label_text, label_rect)
    
    # Show production rate
    rate = state.get_production_rate()
    rate_text = small_font.render(f"+{format_number(int(rate))} / sec", True, (120, 100, 60))
    rate_rect = rate_text.get_rect(center=(cx, acc_y + acc_height - int(50 * scale_y)))
    screen.blit(rate_text, rate_rect)
    
    # Store clickable area for interactivity
    state._abacus_click_area = pygame.Rect(abacus_inner_x, abacus_inner_y, abacus_inner_w, abacus_inner_h)


def draw_mechanical_accumulator(screen, state, current_width, current_height,
                                base_width, base_height, monospace_font, medium_font, small_font, COLORS, display_state):
    """Draw mechanical gear-style accumulator for Era 1"""
    
    scale_x = current_width / base_width
    scale_y = current_height / base_height
    
    # Calculate positions
    side_panel_width = int(current_width * 0.22)
    center_x = side_panel_width + 20
    center_width = current_width - (side_panel_width * 2) - 40
    
    acc_width = int(min(700 * scale_x, center_width - 20))
    acc_height = int(500 * scale_y)
    acc_x = center_x + (center_width - acc_width) // 2
    acc_y = int(80 * scale_y)
    
    cx = acc_x + acc_width // 2
    
    # Draw metallic frame with rivets
    frame_color = (50, 48, 45)
    pygame.draw.rect(screen, frame_color, (acc_x, acc_y, acc_width, acc_height), border_radius=8)
    
    # Draw rivets
    rivet_color = (100, 95, 85)
    for rx in [acc_x + 15, acc_x + acc_width - 15]:
        for ry in [acc_y + 15, acc_y + acc_height - 15]:
            pygame.draw.circle(screen, rivet_color, (rx, ry), 5)
            pygame.draw.circle(screen, (70, 68, 60), (rx, ry), 5, 1)
    
    pygame.draw.rect(screen, (140, 130, 100), (acc_x, acc_y, acc_width, acc_height), 4, border_radius=8)
    
    # Title
    title_text = small_font.render("◈ MECHANICAL COMPUTER ◈", True, (218, 165, 32))
    title_rect = title_text.get_rect(center=(cx, acc_y + int(25 * scale_y)))
    screen.blit(title_text, title_rect)
    
    # Draw inner panel with bolts
    inner_x = acc_x + int(20 * scale_x)
    inner_y = acc_y + int(50 * scale_y)
    inner_w = acc_width - int(40 * scale_x)
    inner_h = acc_height - int(100 * scale_y)
    pygame.draw.rect(screen, (35, 33, 30), (inner_x, inner_y, inner_w, inner_h), border_radius=4)
    
    # Bolts on inner panel
    for bx in [inner_x + 10, inner_x + inner_w - 10]:
        for by in [inner_y + 10, inner_y + inner_h - 10]:
            pygame.draw.circle(screen, (80, 78, 70), (bx, by), 4)
    
    # Draw gears with better visuals
    gears = [
        {"x": 0.3, "y": 0.38, "radius": 0.15, "teeth": 12, "speed": 1.0, "color": (200, 160, 60)},
        {"x": 0.7, "y": 0.38, "radius": 0.12, "teeth": 10, "speed": -1.3, "color": (180, 140, 50)},
        {"x": 0.5, "y": 0.68, "radius": 0.18, "teeth": 15, "speed": 0.7, "color": (160, 120, 40)},
    ]
    
    production = state.get_production_rate()
    rotation_offset = (pygame.time.get_ticks() / 1000.0) * (1 + production / 500)
    
    for gear in gears:
        gx = inner_x + gear["x"] * inner_w
        gy = inner_y + gear["y"] * inner_h
        radius = gear["radius"] * min(inner_w, inner_h)
        
        # Gear shadow
        pygame.draw.circle(screen, (20, 18, 15), (int(gx + 3), int(gy + 3)), int(radius + 5))
        
        # Gear body
        pygame.draw.circle(screen, gear["color"], (int(gx), int(gy)), int(radius))
        pygame.draw.circle(screen, (100, 80, 30), (int(gx), int(gy)), int(radius), 3)
        
        # Draw teeth
        teeth = gear["teeth"]
        rotation = rotation_offset * gear["speed"]
        for t in range(teeth):
            angle = rotation + (t / teeth) * 2 * 3.14159
            tx = gx + math.cos(angle) * (radius + 6)
            ty = gy + math.sin(angle) * (radius + 6)
            pygame.draw.circle(screen, gear["color"], (int(tx), int(ty)), 5)
            pygame.draw.circle(screen, (80, 60, 20), (int(tx), int(ty)), 5, 1)
        
        # Center axle
        pygame.draw.circle(screen, (60, 55, 45), (int(gx), int(gy)), int(radius * 0.3))
        pygame.draw.circle(screen, (30, 28, 25), (int(gx), int(gy)), int(radius * 0.15))
    
    # Lever/handle area (clickable)
    lever_x = cx
    lever_y = acc_y + acc_height - int(55 * scale_y)
    
    # Lever base
    lever_base_w = 80
    lever_base_h = 40
    pygame.draw.rect(screen, (40, 38, 35), (lever_x - lever_base_w//2, lever_y, lever_base_w, lever_base_h), border_radius=4)
    pygame.draw.rect(screen, (120, 110, 80), (lever_x - lever_base_w//2, lever_y, lever_base_w, lever_base_h), 2, border_radius=4)
    
    # Lever arm (animated)
    lever_offset = math.sin(pygame.time.get_ticks() / 150.0) * 8
    pygame.draw.line(screen, (100, 95, 70), (lever_x, lever_y + 10), 
                    (lever_x + lever_offset, lever_y - 15), 8)
    pygame.draw.line(screen, (150, 140, 100), (lever_x, lever_y + 10), 
                    (lever_x + lever_offset, lever_y - 15), 4)
    
    # Lever handle
    pygame.draw.circle(screen, (200, 160, 60), (int(lever_x + lever_offset), int(lever_y - 15)), 12)
    pygame.draw.circle(screen, (120, 100, 40), (int(lever_x + lever_offset), int(lever_y - 15)), 12, 2)
    
    # Show ticks with better styling
    ticks_count = getattr(state, 'ticks', state.bits)
    
    # Currency background
    curr_bg_w = 200
    curr_bg_h = 50
    curr_bg_x = cx - curr_bg_w // 2
    curr_bg_y = acc_y + int(48 * scale_y)
    pygame.draw.rect(screen, (30, 28, 25), (curr_bg_x, curr_bg_y, curr_bg_w, curr_bg_h), border_radius=6)
    pygame.draw.rect(screen, (218, 165, 32), (curr_bg_x, curr_bg_y, curr_bg_w, curr_bg_h), 2, border_radius=6)
    
    currency_text = monospace_font.render(f"{format_number(ticks_count)}", True, (218, 165, 32))
    currency_rect = currency_text.get_rect(center=(cx, curr_bg_y + curr_bg_h // 2))
    screen.blit(currency_text, currency_rect)
    
    # Label
    label_text = small_font.render("ticks", True, (150, 130, 80))
    label_rect = label_text.get_rect(center=(cx, curr_bg_y + curr_bg_h + 12))
    screen.blit(label_text, label_rect)
    
    # Production rate
    rate_text = small_font.render(f"+{format_number(int(production))} ticks/sec", True, (140, 120, 70))
    rate_rect = rate_text.get_rect(center=(cx, acc_y + acc_height - int(25 * scale_y)))
    screen.blit(rate_text, rate_rect)
    
    # Click instruction
    pulse = (math.sin(pygame.time.get_ticks() / 300.0) + 1) / 2
    click_color = (180 + int(pulse * 40), 150 + int(pulse * 30), 80)
    click_text = small_font.render("[ CLICK TO CRANK THE MACHINE ]", True, click_color)
    click_rect = click_text.get_rect(center=(cx, acc_y + acc_height - int(45 * scale_y)))
    screen.blit(click_text, click_rect)
    
    # Store clickable area
    state._abacus_click_area = pygame.Rect(inner_x, inner_y, inner_w, inner_h)
    
    rate_text = small_font.render(f"+{format_number(int(production))} ticks/sec", True, (180, 150, 100))
    rate_rect = rate_text.get_rect(center=(cx, acc_y + acc_height - int(25 * scale_y)))
    screen.blit(rate_text, rate_rect)
