"""
Information Core (main click target) drawing function
"""

import pygame
import math
from constants import COLORS, format_number


def draw_information_core(screen, x, y, scale_x, scale_y, state, small_font, medium_font, last_click_time):
    """Draw the BIG central clickable Information Core - main interaction point"""
    time_ms = pygame.time.get_ticks()
    
    base_radius = int(140 * scale_x)
    
    pulse = math.sin(time_ms * 0.002) * 0.08 + 1.0
    radius = int(base_radius * pulse)
    
    click_power = state.get_click_power()
    
    mouse_pos = pygame.mouse.get_pos()
    dist = math.sqrt((mouse_pos[0] - x) ** 2 + (mouse_pos[1] - y) ** 2)
    is_hovering = dist < radius
    
    glow_intensity = 1.5 if is_hovering else 1.0
    
    for i in range(6, 0, -1):
        glow_radius = radius + i * 20
        alpha = int(max(5, (50 - i * 8) * glow_intensity))
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COLORS["electric_cyan"], alpha), (glow_radius, glow_radius), glow_radius)
        pygame.draw.circle(glow_surf, (*COLORS["neon_purple"], alpha // 2), (glow_radius, glow_radius), glow_radius - 8)
        screen.blit(glow_surf, (x - glow_radius, y - glow_radius))
    
    for i in range(radius, 0, -3):
        ratio = (radius - i) / radius
        r = int(15 + ratio * 30)
        g = int(20 + ratio * 180)
        b = int(30 + ratio * 220)
        pygame.draw.circle(screen, (r, g, b), (x, y), i)
    
    highlight_x = x - int(radius * 0.3)
    highlight_y = y - int(radius * 0.3)
    highlight_radius = int(radius * 0.5)
    highlight_surf = pygame.Surface((highlight_radius * 2, highlight_radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(highlight_surf, (255, 255, 255, 25), (highlight_radius, highlight_radius), highlight_radius)
    screen.blit(highlight_surf, (highlight_x - highlight_radius, highlight_y - highlight_radius))
    
    ring_color = COLORS["matrix_green"] if is_hovering else COLORS["electric_cyan"]
    ring_width = 4 if is_hovering else 3
    
    pygame.draw.circle(screen, ring_color, (x, y), radius, ring_width)
    
    for ring_idx in range(2):
        ring_offset = (time_ms * 0.0005 + ring_idx * 1.5) % 6.28
        ring_r = radius + 15 + ring_idx * 12
        for arc in range(4):
            start_angle = ring_offset + arc * 1.5
            end_angle = start_angle + 0.8
            if end_angle <= ring_offset + 6.28:
                pygame.draw.arc(screen, (*COLORS["neon_purple"], 100), 
                               (x - ring_r, y - ring_r, ring_r * 2, ring_r * 2),
                               start_angle, end_angle, 2)
    
    num_bits = 12
    for i in range(num_bits):
        angle = (i / num_bits) * math.pi * 2 + time_ms * 0.001
        bit_dist = radius * 0.55
        bx = x + int(math.cos(angle) * bit_dist)
        by = y + int(math.sin(angle) * bit_dist)
        bit_char = "1" if (i + time_ms // 300) % 2 == 0 else "0"
        bit_color = COLORS["matrix_green"] if bit_char == "1" else (30, 100, 30)
        bit_text = small_font.render(bit_char, True, bit_color)
        screen.blit(bit_text, (bx - 6, by - 6))
    
    click_text = f"+{format_number(click_power)}"
    click_font = pygame.font.SysFont("Consolas", int(36 * scale_x), bold=True)
    click_surface = click_font.render(click_text, True, COLORS["soft_white"])
    click_rect = click_surface.get_rect(center=(x, y - 15))
    
    for ox, oy in [(4, 4), (3, 3), (2, 2), (1, 1)]:
        glow_s = click_surface.copy()
        glow_s.set_alpha(80)
        screen.blit(glow_s, (click_rect.x + ox, click_rect.y + oy))
    
    screen.blit(click_surface, click_rect)
    
    click_label = medium_font.render("CLICK TO GENERATE", True, COLORS["muted_blue"])
    label_rect = click_label.get_rect(center=(x, y + 35 * scale_x))
    screen.blit(click_label, label_rect)
    
    if hasattr(last_click_time, '__iter__') and time_ms - last_click_time < 500:
        ripple_age = (time_ms - last_click_time) / 500.0
        ripple_radius = int(radius * (1 + ripple_age * 0.8))
        ripple_alpha = int(200 * (1 - ripple_age))
        ripple_surf = pygame.Surface((ripple_radius * 2, ripple_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(ripple_surf, (*COLORS["matrix_green"], ripple_alpha), 
                        (ripple_radius, ripple_radius), ripple_radius, 6)
        
        ripple_radius2 = int(radius * (1 + ripple_age * 0.4))
        ripple_alpha2 = int(150 * (1 - ripple_age))
        pygame.draw.circle(ripple_surf, (*COLORS["electric_cyan"], ripple_alpha2), 
                        (ripple_radius2, ripple_radius2), ripple_radius2, 3)
        
        screen.blit(ripple_surf, (x - ripple_radius, y - ripple_radius))
    
    return {
        "x": x,
        "y": y,
        "radius": radius,
    }
