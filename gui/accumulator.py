"""
Accumulator drawing functions
"""

import pygame
import math
from constants import COLORS, CONFIG, FPS, format_number


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
    acc_y = int(70 * scale_y)

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
        CONFIG.get("VISUAL_FILL_THRESHOLD", 1024 * 1024),  # Use lower threshold for visuals
        state.hardware_generation,
        dt,
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
