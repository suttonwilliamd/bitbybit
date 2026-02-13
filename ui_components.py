"""
UI components for Bit by Bit Game
"""

import pygame
from constants import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT


class LayoutManager:
    """Centralized layout management for responsive positioning"""
    
    def __init__(self, base_width=WINDOW_WIDTH, base_height=WINDOW_HEIGHT):
        self.base_width = base_width
        self.base_height = base_height
        self.current_width = base_width
        self.current_height = base_height
        self._recalculate()
    
    def _recalculate(self):
        """Recalculate all scale factors"""
        self.scale_x = self.current_width / self.base_width
        self.scale_y = self.current_height / self.base_height
        self.min_scale = min(self.scale_x, self.scale_y)
        
        self.side_panel_width = int(self.current_width * 0.22)
        self.center_area_width = self.current_width - (self.side_panel_width * 2)
        
        self.top_bar_height = int(70 * self.scale_y)
        self.top_bar_y = 0
        
        self.toggle_button_height = int(40 * self.scale_y)
        
        self.panel_y_start = self.top_bar_height + int(20 * self.scale_y)
        self.panel_height = self.current_height - self.panel_y_start - int(80 * self.scale_y)
        
        self.left_panel_x = int(15 * self.scale_x)
        self.right_panel_x = self.current_width - self.side_panel_width - int(15 * self.scale_x)
        
        self.center_area_x = self.side_panel_width + int(20 * self.scale_x)
        self.center_area_w = self.center_area_width - int(40 * self.scale_x)
        
        self.bottom_bar_height = int(80 * self.scale_y)
        self.bottom_bar_y = self.current_height - self.bottom_bar_height
    
    def update_size(self, width, height):
        """Update current dimensions and recalculate"""
        self.current_width = width
        self.current_height = height
        self._recalculate()
    
    def scale_value(self, value, use_min=False):
        """Scale a value by scale factors"""
        if use_min:
            return int(value * self.min_scale)
        return int(value * self.scale_x)
    
    def scale_y_value(self, value):
        """Scale a Y value"""
        return int(value * self.scale_y)
    
    def scale_font_size(self, base_size):
        """Scale font size proportionally"""
        return int(base_size * self.min_scale)
    
    def get_center_x(self):
        """Get center X of the window"""
        return self.current_width // 2
    
    def get_center_y(self):
        """Get center Y of the window"""
        return self.current_height // 2
    
    def get_center_area_rect(self):
        """Get the main center area rectangle for UI elements"""
        return pygame.Rect(
            self.center_area_x,
            self.panel_y_start + self.toggle_button_height,
            self.center_area_w,
            self.panel_height
        )
    
    def get_top_bar_rect(self):
        """Get the top bar rectangle"""
        return pygame.Rect(0, 0, self.current_width, self.top_bar_height)
    
    def get_bottom_bar_rect(self):
        """Get the bottom bar rectangle"""
        return pygame.Rect(0, self.bottom_bar_y, self.current_width, self.bottom_bar_height)
    
    def get_left_panel_rect(self):
        """Get left panel rectangle"""
        return pygame.Rect(
            self.left_panel_x,
            self.panel_y_start + self.toggle_button_height,
            self.side_panel_width,
            self.panel_height
        )
    
    def get_right_panel_rect(self):
        """Get right panel rectangle"""
        return pygame.Rect(
            self.right_panel_x,
            self.panel_y_start + self.toggle_button_height,
            self.side_panel_width,
            self.panel_height
        )
    
    def get_toggle_rect(self, is_left=True):
        """Get toggle button rectangle"""
        x = self.left_panel_x if is_left else self.right_panel_x
        return pygame.Rect(
            x,
            self.panel_y_start,
            self.side_panel_width,
            self.toggle_button_height
        )
    
    def get_click_button_rect(self, width_ratio=0.25):
        """Get click button rectangle in center area"""
        button_width = int(min(280, self.center_area_w * width_ratio))
        return pygame.Rect(
            self.center_area_x + (self.center_area_w - button_width) // 2,
            self.current_height - int(260 * self.scale_y),
            button_width,
            int(60 * self.scale_y)
        )
    
    def get_rebirth_button_rect(self):
        """Get rebirth button rectangle"""
        return pygame.Rect(
            self.current_width // 2 - int(150 * self.scale_x),
            self.current_height - int(120 * self.scale_y),
            int(300 * self.scale_x),
            int(40 * self.scale_y)
        )
    
    def get_prestige_button_rect(self):
        """Get prestige button rectangle"""
        return pygame.Rect(
            self.current_width // 2 - int(75 * self.scale_x),
            self.current_height - int(170 * self.scale_y),
            int(150 * self.scale_x),
            int(35 * self.scale_y)
        )
    
    def get_collect_shards_button_rect(self):
        """Get collect shards button rectangle"""
        return pygame.Rect(
            self.current_width // 2 - int(75 * self.scale_x),
            self.current_height - int(220 * self.scale_y),
            int(150 * self.scale_x),
            int(35 * self.scale_y)
        )
    
    def get_header_button_rect(self, is_settings=True):
        """Get header button rectangle"""
        x = self.current_width - int(150 * self.scale_x) if is_settings else self.current_width - int(280 * self.scale_x)
        return pygame.Rect(
            x,
            int(15 * self.scale_y),
            int(120 * self.scale_x),
            int(40 * self.scale_y)
        )
    
    def get_accumulator_rect(self):
        """Get accumulator rectangle in center area"""
        acc_width = int(min(700 * self.scale_x, self.center_area_w - 20))
        acc_height = int(440 * self.scale_y)
        acc_x = self.center_area_x + (self.center_area_w - acc_width) // 2
        acc_y = int(80 * self.scale_y)
        return pygame.Rect(acc_x, acc_y, acc_width, acc_height)
    
    def get_information_core_rect(self):
        """Get information core rectangle"""
        radius = int(120 * self.scale_y)
        return pygame.Rect(
            self.get_center_x() - radius,
            int(420 * self.scale_y),
            radius * 2,
            radius * 2
        )
    
    def get_bit_grid_rect(self):
        """Get bit grid rectangle within accumulator"""
        acc = self.get_accumulator_rect()
        return pygame.Rect(
            acc.x + int(16 * self.scale_x),
            acc.y + int(60 * self.scale_y),
            acc.width - int(32 * self.scale_x),
            acc.height - int(80 * self.scale_y)
        )
    
    def get_progress_bar_rect(self):
        """Get rebirth progress bar rectangle"""
        return pygame.Rect(
            int(200 * self.scale_x),
            self.current_height - int(50 * self.scale_y),
            int(800 * self.scale_x),
            int(20 * self.scale_y)
        )
    
    def get_compression_panel_rect(self):
        """Get compression panel rectangle"""
        panel_width = int(min(800 * self.scale_x, self.center_area_w - 40))
        return pygame.Rect(
            self.center_area_x + (self.center_area_w - panel_width) // 2,
            self.top_bar_height + int(30 * self.scale_y),
            panel_width,
            int(350 * self.scale_y)
        )
    
    def get_compression_meter_rect(self):
        """Get compression meter rectangle"""
        return pygame.Rect(
            self.center_area_x + (self.center_area_w - int(300 * self.scale_x)) // 2,
            self.top_bar_height + int(160 * self.scale_y),
            int(300 * self.scale_x),
            int(25 * self.scale_y)
        )
    
    def get_token_display_pos(self):
        """Get token display position"""
        return (
            self.center_area_x + self.center_area_w // 2 - int(50 * self.scale_x),
            self.top_bar_height + int(200 * self.scale_y)
        )
    
    def get_compression_progress_rect(self):
        """Get compression progress bar rectangle"""
        return pygame.Rect(
            self.center_area_x + (self.center_area_w - int(400 * self.scale_x)) // 2,
            self.top_bar_height + int(240 * self.scale_y),
            int(400 * self.scale_x),
            int(30 * self.scale_y)
        )


class GameUIState:
    """Consolidated UI state to replace global state"""
    
    def __init__(self):
        self.display_bits = 0
        self.display_compressed_bits = 0
        self.display_rate = 0
    
    def reset(self):
        self.display_bits = 0
        self.display_compressed_bits = 0
        self.display_rate = 0


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
        try:
            self.font = pygame.font.SysFont("segoe ui symbol", 18)
        except:
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
        self.lifetime = 1.2
        self.vy = -80
        self.scale = 1.5
        self.target_scale = 1.0
        try:
            self.font = pygame.font.SysFont("Consolas", 28, bold=True)
        except:
            self.font = pygame.font.Font(None, 32)
        self._cached_surface = self.font.render(text, True, color)

    def update(self, dt):
        self.y += self.vy * dt
        self.vy += 20 * dt
        self.lifetime -= dt
        self.scale += (self.target_scale - self.scale) * 8 * dt

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = min(255, int(255 * self.lifetime * 2))
            text_surface = self._cached_surface.copy()
            text_surface.set_alpha(alpha)
            
            w, h = text_surface.get_size()
            scaled_w = int(w * self.scale)
            scaled_h = int(h * self.scale)
            if scaled_w > 0 and scaled_h > 0:
                scaled = pygame.transform.scale(text_surface, (scaled_w, scaled_h))
                screen.blit(scaled, (self.x - scaled_w // 2, self.y - scaled_h // 2))
            else:
                screen.blit(text_surface, (self.x, self.y))
