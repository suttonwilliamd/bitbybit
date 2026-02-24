"""
Top bar drawing functions for Bit by Bit Game
"""

import pygame
from constants import COLORS


def draw_top_bar(screen, current_width, current_height, base_width, base_height, game_state, bit_counter_font, large_font, small_font, medium_font, COLORS):
    """Draw the top bar with game title and basic stats"""
    bar_height = 70
    bar_rect = pygame.Rect(0, 0, current_width, bar_height)
    
    # Background
    pygame.draw.rect(screen, COLORS["panel_title_bg"], bar_rect)
    
    # Title
    if large_font:
        title_text = large_font.render("Bit by Bit", True, COLORS["electric_cyan"])
        screen.blit(title_text, (20, 20))
    
    # Current era display
    if medium_font:
        era_text = medium_font.render(f"Era: {game_state.current_era}", True, COLORS["muted_blue"])
        screen.blit(era_text, (20, 45))
    
    # Currency display
    if medium_font:
        if game_state.binary_invented:
            bits_text = medium_font.render(f"Bits: {game_state.bits:,.0f}", True, COLORS["matrix_green"])
        else:
            bits_text = medium_font.render(f"Pebbles: {game_state.pebbles:,.0f}", True, COLORS["soft_white"])
        screen.blit(bits_text, (current_width - 200, 25))
    
    return bar_height
