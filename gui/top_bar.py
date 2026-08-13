"""
Top bar drawing function
"""

import pygame
from constants import COLORS, format_number


class TopBarDisplayState:
    """Holds display state for smooth number animations"""
    def __init__(self):
        self.display_bits = 0


_top_bar_state = TopBarDisplayState()


def draw_top_bar(screen, current_width, current_height, base_width, base_height,
                 state, bit_counter_font, large_font, small_font, medium_font, COLORS):
    """Draw the top bar with title and bit counter"""
    global _top_bar_state
    
    scale_x = current_width / base_width
    scale_y = current_height / base_height
    
    top_bar_rect = pygame.Rect(0, 0, current_width, int(80 * scale_y))
    
    for i in range(int(80 * scale_y)):
        color_ratio = i / (80 * scale_y)
        color = (
            int(15 + color_ratio * 10),
            int(20 + color_ratio * 12),
            int(35 + color_ratio * 20)
        )
        pygame.draw.line(screen, color, (0, i), (current_width, i))
    
    border_color = COLORS["electric_cyan"]
    pygame.draw.line(screen, border_color, 
                    (0, int(80 * scale_y)), 
                    (current_width, int(80 * scale_y)), 2)
    for i in range(1, 4):
        pygame.draw.line(screen, border_color, 
                        (0, int(80 * scale_y) + i), 
                        (current_width, int(80 * scale_y) + i), 1)
    
    title_text = large_font.render(
        "BIT BY BIT", True, COLORS["electric_cyan"]
    )
    for offset, alpha in [((2, 2), 30), ((1, 1), 50)]:
        glow_surface = title_text.copy()
        glow_surface.set_alpha(alpha)
        screen.blit(glow_surface, (int(20 * scale_x) + offset[0], int(12 * scale_y) + offset[1]))
    screen.blit(title_text, (int(20 * scale_x), int(12 * scale_y)))
    
    subtitle_text = small_font.render(
        "Information Accumulator", True, COLORS["muted_blue"]
    )
    screen.blit(subtitle_text, (int(20 * scale_x), int(50 * scale_y)))
    
    # For small values, use actual value to avoid display lag confusion
    if state.bits < 10:
        display_bits = state.bits
    else:
        smoothing_factor = 0.15
        _top_bar_state.display_bits += (state.bits - _top_bar_state.display_bits) * smoothing_factor
        display_bits = _top_bar_state.display_bits
    
    bits_str = f"{round(display_bits)}"
    if display_bits < 1000:
        bits_str = str(round(display_bits))
    elif display_bits < 1000000:
        bits_str = f"{display_bits / 1000:.1f}K"
    elif display_bits < 1000000000:
        bits_str = f"{display_bits / 1000000:.1f}M"
    elif display_bits < 1000000000000:
        bits_str = f"{display_bits / 1000000000:.1f}B"
    else:
        bits_str = f"{display_bits / 1000000000000:.1f}T"
    
    bits_text = bit_counter_font.render(bits_str, True, COLORS["matrix_green"])
    
    for offset, alpha in [((4, 4), 15), ((3, 3), 25), ((2, 2), 40), ((1, 1), 60)]:
        glow_surface = bits_text.copy()
        glow_surface.set_alpha(alpha)
        glow_pos = (current_width // 2 - bits_text.get_width() // 2 + offset[0],
                   int(25 * scale_y) + offset[1])
        screen.blit(glow_surface, glow_pos)
    
    bits_rect = bits_text.get_rect(center=(current_width // 2, int(40 * scale_y)))
    screen.blit(bits_text, bits_rect)
    
    rate = state.get_production_rate()
    rate_str = f"+{int(rate)} bits/sec"
    if rate >= 1000:
        rate_str = f"+{rate / 1000:.1f}K bits/sec"
    if rate >= 1000000:
        rate_str = f"+{rate / 1000000:.1f}M bits/sec"
    if rate >= 1000000000:
        rate_str = f"+{rate / 1000000000:.1f}B bits/sec"
        
    rate_text = medium_font.render(rate_str, True, COLORS["electric_cyan"])
    rate_rect = rate_text.get_rect(center=(current_width // 2, int(68 * scale_y)))
    
    for offset, alpha in [((1, 1), 30), ((-1, -1), 50)]:
        glow_surface = rate_text.copy()
        glow_surface.set_alpha(alpha)
        screen.blit(glow_surface, (rate_rect.x + offset[0], rate_rect.y + offset[1]))
    
    screen.blit(rate_text, rate_rect)
    
    click_power = state.get_click_power()
    if click_power > 1:
        click_str = f"Click: +{int(click_power)}"
        if click_power >= 1000:
            click_str = f"Click: +{click_power / 1000:.1f}K"
        click_text = small_font.render(click_str, True, COLORS["signal_orange"])
        click_rect = click_text.get_rect(center=(current_width // 2, int(88 * scale_y)))
        screen.blit(click_text, click_rect)
