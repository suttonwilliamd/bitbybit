"""
Visual effects drawing functions
"""

import pygame
from constants import COLORS


def draw_effects(screen, particles, floating_texts):
    """Draw particles and floating texts"""
    for particle in particles:
        particle.draw(screen)

    for text in floating_texts:
        text.draw(screen)


def draw_crt_overlay(screen, current_width, current_height):
    """Draw CRT scanline overlay effect with vignette for cyberpunk aesthetic"""
    # Scanlines
    for y in range(0, current_height, 3):
        pygame.draw.line(screen, (0, 0, 0, 25), (0, y), (current_width, y))
    
    # Subtle vignette effect at corners
    vignette_strength = 40
    corners = [
        (0, 0), (current_width, 0), 
        (0, current_height), (current_width, current_height)
    ]
    for cx, cy in corners:
        # Draw gradient vignette corners
        for i in range(50):
            alpha = int(vignette_strength * (1 - i / 50))
            rect = pygame.Rect(cx - i*2 if cx > 0 else 0, cy - i*2 if cy > 0 else 0, i*4, i*4)
            pygame.draw.rect(screen, (0, 0, 0, alpha // 4), rect)


def draw_circuit_background(screen, current_width, current_height):
    """Draw subtle circuit board pattern in background"""
    circuit_color = (30, 40, 60)
    trace_width = 2
    
    for x in [int(current_width * 0.15), int(current_width * 0.85)]:
        pygame.draw.line(screen, circuit_color, (x, 0), (x, current_height), trace_width)
    
    for y in [int(current_height * 0.3), int(current_height * 0.6)]:
        pygame.draw.line(screen, circuit_color, (0, y), (current_width, trace_width))
    
    node_color = (40, 55, 80)
    node_radius = 4
    for x in [int(current_width * 0.15), int(current_width * 0.85)]:
        for y in [int(current_height * 0.3), int(current_height * 0.6)]:
            pygame.draw.circle(screen, node_color, (x, y), node_radius)


def _get_gradient_surface(screen, current_width, current_height, cached_gradient, last_size):
    """Get or create gradient background surface"""
    if (cached_gradient is None or 
        last_size != (current_width, current_height)):
        gradient_surface = pygame.Surface((current_width, current_height))
        for i in range(current_height):
            color_ratio = i / current_height
            color = (
                int(
                    COLORS["deep_space_blue"][0]
                    + (
                        COLORS["deep_space_gradient_end"][0]
                        - COLORS["deep_space_blue"][0]
                    )
                    * color_ratio
                ),
                int(
                    COLORS["deep_space_blue"][1]
                    + (
                        COLORS["deep_space_gradient_end"][1]
                        - COLORS["deep_space_blue"][1]
                    )
                    * color_ratio
                ),
                int(
                    COLORS["deep_space_blue"][2]
                    + (
                        COLORS["deep_space_gradient_end"][2]
                        - COLORS["deep_space_blue"][2]
                    )
                    * color_ratio
                ),
            )
            pygame.draw.line(gradient_surface, color, (0, i), (current_width, i))
        return gradient_surface, (current_width, current_height)
    return cached_gradient, last_size


def draw_tooltips(screen, mouse_pos, hardware_panel_open, upgrades_panel_open,
                  hardware_scroll_panel, upgrades_scroll_panel, state, config,
                  small_font, tiny_font, current_width, current_height, COLORS):
    """Draw tooltips for hovered elements"""
    from constants import GENERATORS, UPGRADES
    from constants import get_all_generators, get_all_upgrades
    
    if hardware_panel_open:
        panel = hardware_scroll_panel
        all_generators = get_all_generators()
        y_offset = -panel.get_scroll_offset()

        for gen_id, generator in all_generators.items():
            basic_generators = GENERATORS if GENERATORS else config["GENERATORS"]
            hardware_generators = config.get("HARDWARE_GENERATORS", {})
            
            if gen_id in basic_generators:
                if not state.is_generator_unlocked(gen_id):
                    continue
            elif gen_id in hardware_generators:
                if not state.is_hardware_category_unlocked(generator.get("category", "")):
                    continue

            card_x = panel.rect.x + 10
            card_y = panel.rect.y + 50 + y_offset + 8
            card_width = panel.rect.width - 40
            card_height = 70

            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            
            if card_rect.collidepoint(mouse_pos):
                flavor = generator.get("flavor", "")
                if flavor:
                    _draw_tooltip_box(screen, mouse_pos, flavor, current_width, current_height)
                return
            
            y_offset += card_height + 14

    if upgrades_panel_open:
        panel = upgrades_scroll_panel
        all_upgrades = get_all_upgrades()
        y_offset = -panel.get_scroll_offset()

        for upgrade_id, upgrade in all_upgrades.items():
            basic_upgrades = UPGRADES if UPGRADES else config["UPGRADES"]
            hardware_upgrades = config.get("HARDWARE_UPGRADES", {})
            
            if upgrade_id in basic_upgrades:
                if not state.is_upgrade_unlocked(upgrade_id):
                    continue
            elif upgrade_id in hardware_upgrades:
                if not state.is_hardware_category_unlocked(upgrade.get("category", "")):
                    continue

            card_x = panel.rect.x + 10
            card_y = panel.rect.y + 50 + y_offset + 8
            card_width = panel.rect.width - 40
            card_height = 65

            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            
            if card_rect.collidepoint(mouse_pos):
                desc = upgrade.get("description", "")
                effect = upgrade.get("effect", 0)
                max_level = upgrade.get("max_level", 0)
                if desc:
                    tooltip_text = desc
                    if effect and max_level:
                        tooltip_text += f"\nEffect: {effect}x per level"
                    _draw_tooltip_box(screen, mouse_pos, tooltip_text, current_width, current_height)
                return
            
            y_offset += card_height + 14


def _draw_tooltip_box(screen, mouse_pos, text, current_width, current_height):
    """Draw a tooltip box at the mouse position"""
    tooltip_font = pygame.font.Font(None, 22)
    lines = text.split("\n")
    
    max_width = 0
    for line in lines:
        width = tooltip_font.size(line)[0]
        max_width = max(max_width, width)
    
    padding = 15
    tooltip_width = max_width + padding * 2
    tooltip_height = len(lines) * 22 + padding * 2
    
    tooltip_x = mouse_pos[0] + 15
    tooltip_y = mouse_pos[1] + 15
    
    if tooltip_x + tooltip_width > current_width - 10:
        tooltip_x = mouse_pos[0] - tooltip_width - 10
    if tooltip_y + tooltip_height > current_height - 10:
        tooltip_y = mouse_pos[1] - tooltip_height - 10
    
    tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
    
    tooltip_bg = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
    tooltip_bg.fill((15, 18, 28, 230))
    screen.blit(tooltip_bg, (tooltip_x, tooltip_y))
    
    pygame.draw.rect(screen, COLORS["electric_cyan"], tooltip_rect, 1, border_radius=4)
    
    for i, line in enumerate(lines):
        text_surface = tooltip_font.render(line, True, COLORS["soft_white"])
        screen.blit(text_surface, (tooltip_x + padding, tooltip_y + padding + i * 22))
