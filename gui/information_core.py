"""
Information Core - the main click target for Bit by Bit Game
"""

import pygame
from constants import COLORS


def draw_information_core(screen, game_state, fonts, x, y, size):
    """Draw the main click target (information core / bit generator)"""
    # Placeholder - the actual implementation was likely in the main __init__.py before
    # This is a basic version to get the game running
    center_x = x + size // 2
    center_y = y + size // 2
    
    # Draw a simple circle as the click target
    pygame.draw.circle(screen, COLORS["electric_cyan"], (center_x, center_y), size // 3)
    
    # Draw label
    small_font = fonts.get("small_font")
    if small_font:
        label = "Click" if not game_state.binary_invented else "Generate"
        text = small_font.render(label, True, COLORS["soft_white"])
        text_rect = text.get_rect(center=(center_x, center_y))
        screen.blit(text, text_rect)
