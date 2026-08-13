"""
Motherboard upgrade notification UI
"""

import pygame
import math
from constants import COLORS, HARDWARE_GENERATIONS


class MotherboardUpgradeNotification:
    """Notification that appears when player unlocks a new motherboard generation"""
    
    def __init__(self):
        self.active = False
        self.generation = 0
        self.timer = 0
        self.duration = 4.0
        self.progress = 0
        
    def show(self, generation):
        """Show notification for the given generation"""
        self.active = True
        self.generation = generation
        self.timer = 0
        self.progress = 0
        
    def update(self, dt):
        """Update notification state"""
        if not self.active:
            return
            
        self.timer += dt
        self.progress = min(self.timer / self.duration, 1.0)
        
        if self.timer >= self.duration:
            self.active = False
            
    def draw(self, screen, width, height):
        """Draw the notification"""
        if not self.active:
            return
        
        gen_info = HARDWARE_GENERATIONS.get(self.generation, None)
        if not gen_info:
            self.active = False
            return
        
        try:
            fade_in = min(self.timer / 0.5, 1.0)
            fade_out = max(0, 1 - (self.timer - (self.duration - 0.5)) / 0.5)
            alpha = int(255 * fade_in * fade_out)
            
            scale = 0.5 + 0.5 * math.sin(self.timer * 3) * 0.1
            
            center_x = width // 2
            center_y = height // 3
            
            glow_radius = int(200 * scale)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            
            for i in range(5, 0, -1):
                glow_alpha = int(alpha * 0.1 * (6 - i) / 5)
                pygame.draw.circle(
                    glow_surface, 
                    (*COLORS["electric_cyan"], glow_alpha), 
                    (glow_radius, glow_radius), 
                    glow_radius - i * 15
                )
            screen.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius))
            
            panel_width = 500
            panel_height = 200
            panel_rect = pygame.Rect(
                center_x - panel_width // 2,
                center_y - panel_height // 2,
                panel_width,
                panel_height
            )
            
            panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            panel_surface.fill((15, 18, 28, alpha))
            
            pygame.draw.rect(panel_surface, (COLORS["gold"][0], COLORS["gold"][1], COLORS["gold"][2], alpha), (0, 0, panel_width, panel_height), 3)
            
            screen.blit(panel_surface, panel_rect)
            
            icon = gen_info.get("icon", "🖥️")
            try:
                icon_font = pygame.font.SysFont("Segoe UI Symbol", 64)
                icon_surface = icon_font.render(icon, True, COLORS["gold"])
                icon_surface.set_alpha(alpha)
                icon_rect = icon_surface.get_rect(center=(center_x, center_y - 50))
                screen.blit(icon_surface, icon_rect)
            except Exception:
                pygame.draw.circle(screen, (*COLORS["gold"], alpha), (center_x, center_y - 50), 30)
            
            title_font = pygame.font.SysFont("Consolas", 32, bold=True)
            title_text = "MOTHERBOARD UPGRADE!"
            title_surface = title_font.render(title_text, True, COLORS["gold"])
            title_surface.set_alpha(alpha)
            title_rect = title_surface.get_rect(center=(center_x, center_y + 10))
            screen.blit(title_surface, title_rect)
            
            name_font = pygame.font.SysFont("Consolas", 24)
            name_text = gen_info.get("name", "Unknown Era")
            name_surface = name_font.render(name_text, True, COLORS["electric_cyan"])
            name_surface.set_alpha(alpha)
            name_rect = name_surface.get_rect(center=(center_x, center_y + 45))
            screen.blit(name_surface, name_rect)
            
            desc_font = pygame.font.SysFont("Consolas", 16)
            desc_text = gen_info.get("description", "")
            desc_surface = desc_font.render(desc_text, True, COLORS["soft_white"])
            desc_surface.set_alpha(alpha)
            desc_rect = desc_surface.get_rect(center=(center_x, center_y + 75))
            screen.blit(desc_surface, desc_rect)
            
            categories = gen_info.get("unlock_categories", [])
            cat_text = "Unlocked: " + ", ".join(categories)
            cat_font = pygame.font.SysFont("Consolas", 14)
            cat_surface = cat_font.render(cat_text, True, COLORS["muted_blue"])
            cat_surface.set_alpha(alpha)
            cat_rect = cat_surface.get_rect(center=(center_x, center_y + 105))
            screen.blit(cat_surface, cat_rect)
        except Exception:
            self.active = False
