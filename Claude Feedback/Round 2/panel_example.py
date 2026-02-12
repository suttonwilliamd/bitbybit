"""
MINIMAL WORKING EXAMPLE: Correct Panel Design
Run this to see how the panels should look, then copy to your game
"""

import pygame
import sys

pygame.init()

# Window
WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bit by Bit - Panel Design Example")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(None, 52)
medium_font = pygame.font.Font(None, 26)
small_font = pygame.font.Font(None, 22)
tiny_font = pygame.font.Font(None, 18)

# Colors
COLORS = {
    "deep_space_blue": (15, 18, 28),
    "panel_dark": (22, 25, 35),
    "panel_title_bg": (28, 32, 45),
    "card_bg": (28, 32, 42),
    "electric_cyan": (0, 200, 255),
    "neon_purple": (180, 100, 255),
    "matrix_green": (0, 255, 128),
    "soft_white": (240, 245, 255),
    "muted_blue": (120, 140, 180),
    "gold": (255, 215, 0),
}


def draw_panel_with_title(screen, x, y, width, height, title, title_color):
    """Draw a panel with integrated title bar"""
    panel_rect = pygame.Rect(x, y, width, height)
    
    # Main panel background
    pygame.draw.rect(screen, COLORS["panel_dark"], panel_rect, border_radius=10)
    
    # Outer border
    pygame.draw.rect(screen, COLORS["muted_blue"], panel_rect, 2, border_radius=10)
    
    # Title bar (integrated at top)
    title_bar_height = 45
    title_rect = pygame.Rect(x, y, width, title_bar_height)
    pygame.draw.rect(screen, COLORS["panel_title_bg"], title_rect, 
                    border_top_left_radius=10, border_top_right_radius=10)
    
    # Title text
    title_surface = medium_font.render(title, True, title_color)
    title_text_rect = title_surface.get_rect(center=(x + width//2, y + title_bar_height//2))
    screen.blit(title_surface, title_text_rect)
    
    # Separator line under title
    pygame.draw.line(screen, title_color, 
                    (x + 10, y + title_bar_height), 
                    (x + width - 10, y + title_bar_height), 2)


def draw_generator_card(screen, x, y, width, height, name, icon, qty, rate, cost, affordable):
    """Draw a single generator card with proper layout"""
    card_rect = pygame.Rect(x, y, width, height)
    
    # Background
    pygame.draw.rect(screen, COLORS["card_bg"], card_rect, border_radius=8)
    
    # Border (glowing if affordable)
    if affordable:
        border_color = COLORS["electric_cyan"]
        border_alpha = 180
    else:
        border_color = COLORS["muted_blue"]
        border_alpha = 100
    
    border_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(border_surf, (*border_color, border_alpha), 
                    (0, 0, width, height), 2, border_radius=8)
    screen.blit(border_surf, (x, y))
    
    # Icon (left side, larger)
    icon_size = 48
    icon_x = x + 15
    icon_y = y + height // 2 - icon_size // 2
    icon_font = pygame.font.Font(None, 42)
    icon_surface = icon_font.render(icon, True, COLORS["electric_cyan"])
    screen.blit(icon_surface, (icon_x, icon_y))
    
    # Text area (starts after icon)
    text_x = x + 75
    
    # Name (top)
    name_surface = medium_font.render(name, True, COLORS["soft_white"])
    screen.blit(name_surface, (text_x, y + 12))
    
    # Qty (middle left)
    qty_surface = small_font.render(f"Qty: {qty}", True, COLORS["muted_blue"])
    screen.blit(qty_surface, (text_x, y + 40))
    
    # Rate (middle right of qty)
    rate_surface = small_font.render(f"Rate: +{rate}", True, COLORS["matrix_green"])
    screen.blit(rate_surface, (text_x + 100, y + 40))
    
    # Cost (bottom right, before buttons)
    cost_surface = tiny_font.render(f"{cost} bits", True, COLORS["gold"] if affordable else COLORS["muted_blue"])
    screen.blit(cost_surface, (x + width - 180, y + height - 22))
    
    # Buttons (bottom right)
    button_y = y + height - 32
    
    # BUY x1 button
    btn1_rect = pygame.Rect(x + width - 155, button_y, 70, 28)
    btn1_color = (45, 55, 70) if affordable else (30, 33, 40)
    pygame.draw.rect(screen, btn1_color, btn1_rect, border_radius=4)
    pygame.draw.rect(screen, COLORS["electric_cyan"] if affordable else COLORS["muted_blue"], 
                    btn1_rect, 1, border_radius=4)
    btn1_text = tiny_font.render("BUY x1", True, COLORS["soft_white"] if affordable else COLORS["muted_blue"])
    btn1_text_rect = btn1_text.get_rect(center=btn1_rect.center)
    screen.blit(btn1_text, btn1_text_rect)
    
    # BUY x10 button
    btn2_rect = pygame.Rect(x + width - 75, button_y, 70, 28)
    pygame.draw.rect(screen, btn1_color, btn2_rect, border_radius=4)
    pygame.draw.rect(screen, COLORS["electric_cyan"] if affordable else COLORS["muted_blue"], 
                    btn2_rect, 1, border_radius=4)
    btn2_text = tiny_font.render("BUY x10", True, COLORS["soft_white"] if affordable else COLORS["muted_blue"])
    btn2_text_rect = btn2_text.get_rect(center=btn2_rect.center)
    screen.blit(btn2_text, btn2_text_rect)


def draw_upgrade_card(screen, x, y, width, height, name, icon, level, max_level, cost, affordable, maxed):
    """Draw a single upgrade card with proper layout"""
    card_rect = pygame.Rect(x, y, width, height)
    
    # Background
    pygame.draw.rect(screen, COLORS["card_bg"], card_rect, border_radius=8)
    
    # Border (gold if maxed, purple if affordable, muted otherwise)
    if maxed:
        border_color = COLORS["gold"]
        border_alpha = 200
    elif affordable:
        border_color = COLORS["neon_purple"]
        border_alpha = 180
    else:
        border_color = COLORS["muted_blue"]
        border_alpha = 100
    
    border_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(border_surf, (*border_color, border_alpha), 
                    (0, 0, width, height), 2, border_radius=8)
    screen.blit(border_surf, (x, y))
    
    # Icon (left side)
    icon_x = x + 15
    icon_y = y + height // 2 - 20
    icon_font = pygame.font.Font(None, 38)
    icon_surface = icon_font.render(icon, True, COLORS["neon_purple"])
    screen.blit(icon_surface, (icon_x, icon_y))
    
    # Text area
    text_x = x + 55
    
    # Name
    name_surface = medium_font.render(name, True, COLORS["soft_white"])
    screen.blit(name_surface, (text_x, y + 10))
    
    # Level
    level_text = f"Level {level}/{max_level}"
    level_color = COLORS["gold"] if maxed else COLORS["muted_blue"]
    level_surface = small_font.render(level_text, True, level_color)
    screen.blit(level_surface, (text_x, y + 36))
    
    # Description
    desc_surface = tiny_font.render("Multiplies all production by 2x", True, COLORS["muted_blue"])
    screen.blit(desc_surface, (text_x, y + 58))
    
    # Button or MAXED indicator
    button_x = x + width - 90
    button_y = y + height // 2 - 14
    
    if maxed:
        maxed_text = small_font.render("MAXED", True, COLORS["gold"])
        maxed_rect = maxed_text.get_rect(center=(button_x + 40, button_y + 14))
        screen.blit(maxed_text, maxed_rect)
    else:
        # Cost
        cost_surface = tiny_font.render(f"{cost}", True, COLORS["gold"] if affordable else COLORS["muted_blue"])
        screen.blit(cost_surface, (button_x - 40, button_y + 10))
        
        # BUY button
        btn_rect = pygame.Rect(button_x, button_y, 80, 28)
        btn_color = (55, 45, 75) if affordable else (30, 33, 40)
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=4)
        pygame.draw.rect(screen, COLORS["neon_purple"] if affordable else COLORS["muted_blue"], 
                        btn_rect, 1, border_radius=4)
        btn_text = tiny_font.render("BUY", True, COLORS["soft_white"] if affordable else COLORS["muted_blue"])
        btn_text_rect = btn_text.get_rect(center=btn_rect.center)
        screen.blit(btn_text, btn_text_rect)


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Background gradient
    for i in range(HEIGHT):
        ratio = i / HEIGHT
        color = (
            int(COLORS["deep_space_blue"][0] * (1 - ratio * 0.3)),
            int(COLORS["deep_space_blue"][1] * (1 - ratio * 0.3)),
            int(COLORS["deep_space_blue"][2] + (40 - COLORS["deep_space_blue"][2]) * ratio)
        )
        pygame.draw.line(screen, color, (0, i), (WIDTH, i))
    
    # Title
    title = title_font.render("BIT BY BIT - CORRECT PANEL DESIGN", True, COLORS["electric_cyan"])
    title_rect = title.get_rect(center=(WIDTH // 2, 40))
    screen.blit(title, title_rect)
    
    subtitle = small_font.render("This is how your panels should look", True, COLORS["muted_blue"])
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 75))
    screen.blit(subtitle, subtitle_rect)
    
    # ===== LEFT PANEL: INFORMATION SOURCES =====
    panel_x = 50
    panel_y = 120
    panel_width = 650
    panel_height = 400
    
    draw_panel_with_title(screen, panel_x, panel_y, panel_width, panel_height, 
                         "INFORMATION SOURCES", COLORS["electric_cyan"])
    
    # Generator cards inside panel
    card_y = panel_y + 60  # Start below title bar
    
    # Card 1: Random Number Generator (affordable)
    draw_generator_card(screen, panel_x + 15, card_y, panel_width - 30, 90,
                       "Random Number Generator", "🎲", 78, "78 b/s", "547K", True)
    
    # Card 2: Biased Coin (affordable)
    draw_generator_card(screen, panel_x + 15, card_y + 102, panel_width - 30, 90,
                       "Biased Coin", "🪙", 52, "416 b/s", "143K", True)
    
    # Card 3: Quantum Observer (not affordable)
    draw_generator_card(screen, panel_x + 15, card_y + 204, panel_width - 30, 90,
                       "Quantum Observer", "👁️", 0, "0 b/s", "5.2M", False)
    
    # ===== RIGHT PANEL: UPGRADES =====
    panel2_x = 720
    panel2_width = 450
    
    draw_panel_with_title(screen, panel2_x, panel_y, panel2_width, panel_height,
                         "UPGRADES", COLORS["neon_purple"])
    
    # Upgrade cards inside panel
    card_y = panel_y + 60
    
    # Upgrade 1: Entropy Amplification (affordable)
    draw_upgrade_card(screen, panel2_x + 15, card_y, panel2_width - 30, 85,
                     "Entropy Amplification", "⚡", 2, 5, "10.0M", True, False)
    
    # Upgrade 2: Click Power (maxed)
    draw_upgrade_card(screen, panel2_x + 15, card_y + 97, panel2_width - 30, 85,
                     "Click Power", "🔋", 5, 5, "—", False, True)
    
    # Upgrade 3: Data Compression (not affordable)
    draw_upgrade_card(screen, panel2_x + 15, card_y + 194, panel2_width - 30, 85,
                     "Data Compression", "📦", 0, 5, "500K", False, False)
    
    # Instructions
    instructions = [
        "NOTICE:",
        "• Title is INSIDE the panel (integrated title bar)",
        "• Cards have glowing borders when affordable (not backgrounds)",
        "• Icons are INSIDE the cards (not vertical bars)",
        "• Buy buttons are INSIDE each card (not floating)",
        "• Generous spacing (12px between cards)",
        "• Rounded corners everywhere",
        "• Clear hierarchy: Title > Name > Details > Actions"
    ]
    
    inst_y = panel_y + panel_height + 30
    for i, line in enumerate(instructions):
        color = COLORS["gold"] if i == 0 else COLORS["soft_white"]
        font = small_font if i == 0 else tiny_font
        inst_surface = font.render(line, True, color)
        screen.blit(inst_surface, (50, inst_y + i * 22))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
