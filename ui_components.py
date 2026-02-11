"""
UI components for Bit by Bit Game
"""

import pygame
from constants import COLORS


class Button:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        color=COLORS["dim_gray"],
        text_color=COLORS["soft_white"],
        hover_color=None,
        active_color=None,
        high_contrast=False,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover_color = hover_color or COLORS["electric_cyan"]
        self.active_color = active_color or COLORS["neon_purple"]
        self.is_hovered = False
        self.is_active = False
        self.font = pygame.font.Font(None, 24)
        self.is_enabled = True
        self.animation_time = 0
        self.high_contrast = high_contrast

    def update(self, mouse_pos):
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos) and self.is_enabled
        if self.is_hovered and not was_hovered:
            self.animation_time = pygame.time.get_ticks()

    def draw(self, screen):
        # Enhanced color system with better contrast and high-contrast support
        if not self.is_enabled:
            if getattr(self, "high_contrast", False):
                color = COLORS["high_contrast_background"]
                border_color = COLORS["high_contrast_border"]
                text_color = COLORS["high_contrast_secondary"]
            else:
                color = COLORS["card_disabled"]
                border_color = COLORS["text_disabled"]
                text_color = COLORS["text_disabled"]
            glow_alpha = 0
        elif self.is_active:
            if getattr(self, "high_contrast", False):
                color = COLORS["high_contrast_primary"]
                border_color = COLORS["high_contrast_secondary"]
                text_color = COLORS["high_contrast_secondary"]
            else:
                color = COLORS["card_affordable"]
                border_color = COLORS["matrix_green"]
                text_color = COLORS["soft_white"]
            glow_alpha = 100
        elif self.is_hovered:
            if getattr(self, "high_contrast", False):
                color = COLORS["high_contrast_primary"]
                border_color = COLORS["high_contrast_secondary"]
                text_color = COLORS["high_contrast_secondary"]
            else:
                color = COLORS["card_affordable"]
                border_color = COLORS["electric_cyan"]
                text_color = COLORS["soft_white"]
            glow_alpha = 60
        else:
            color = self.color
            border_color = COLORS["muted_blue"]
            text_color = self.text_color
            glow_alpha = 0

        # Draw glow effect for hover/active states
        if glow_alpha > 0:
            glow_rect = self.rect.inflate(4, 4)
            glow_surf = pygame.Surface(
                (glow_rect.width, glow_rect.height), pygame.SRCALPHA
            )
            pygame.draw.rect(
                glow_surf,
                (*border_color, glow_alpha),
                (0, 0, glow_rect.width, glow_rect.height),
                border_radius=6,
            )
            screen.blit(glow_surf, glow_rect)

        # Draw button background with rounded corners
        pygame.draw.rect(screen, color, self.rect, border_radius=4)

        # Draw border with enhanced styling
        if self.is_enabled:
            # Multi-layer border for depth
            pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=4)
            # Inner highlight
            if self.is_hovered or self.is_active:
                highlight_rect = pygame.Rect(
                    self.rect.x + 2,
                    self.rect.y + 2,
                    self.rect.width - 4,
                    self.rect.height - 4,
                )
                pygame.draw.rect(
                    screen,
                    tuple(min(255, c + 30) for c in border_color),
                    highlight_rect,
                    1,
                    border_radius=3,
                )
        else:
            # Disabled border
            pygame.draw.rect(
                screen, COLORS["text_disabled"], self.rect, 1, border_radius=4
            )

        # Add subtle inner shadow for depth
        if self.is_enabled:
            shadow_rect = pygame.Rect(
                self.rect.x + 3,
                self.rect.y + 3,
                self.rect.width - 6,
                self.rect.height - 6,
            )
            shadow_surf = pygame.Surface(
                (shadow_rect.width, shadow_rect.height), pygame.SRCALPHA
            )
            pygame.draw.rect(
                shadow_surf,
                (0, 0, 0, 20),
                (0, 0, shadow_rect.width, shadow_rect.height),
                border_radius=2,
            )
            screen.blit(shadow_surf, shadow_rect)

        # Enhanced text rendering
        font_size = self.font.get_height()

        # Text shadow for better readability
        shadow_surface = self.font.render(self.text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(
            center=(self.rect.centerx + 1, self.rect.centery + 1)
        )
        shadow_alpha = 150 if self.is_enabled else 50
        shadow_surface.set_alpha(shadow_alpha)
        screen.blit(shadow_surface, shadow_rect)

        # Main text
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)

        # Add subtle text glow for hover states
        if (self.is_hovered or self.is_active) and self.is_enabled:
            glow_text_surface = self.font.render(self.text, True, border_color)
            glow_text_surface.set_alpha(50)
            glow_text_rect = glow_text_surface.get_rect(
                center=(text_rect.centerx - 1, text_rect.centery - 1)
            )
            screen.blit(glow_text_surface, glow_text_rect)

        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1  # Only left mouse button (1), not scroll wheel (4,5)
            and self.rect.collidepoint(event.pos)
            and self.is_enabled
        )


class FloatingText:
    def __init__(self, x, y, text, color=COLORS["matrix_green"]):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = 1.0
        self.vy = -50
        self.font = pygame.font.Font(None, 32)

    def update(self, dt):
        self.y += self.vy * dt
        self.lifetime -= dt

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * self.lifetime)
            text_surface = self.font.render(self.text, True, self.color)
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, (self.x, self.y))
