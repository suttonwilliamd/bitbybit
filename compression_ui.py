"""
Enhanced compression UI components for Bit by Bit Game
"""

import pygame
import math
from constants import COLORS


class CompressionPanel:
    """Dedicated compression era panel with enhanced visual design"""
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.particles = []
        self.compression_animation = 0
        self.token_glow = 0
        
    def update(self, dt):
        """Update animations and particles"""
        self.compression_animation += dt * 2
        self.token_glow = (math.sin(self.compression_animation) + 1) * 0.5
        
        # Update particles
        for particle in self.particles[:]:
            particle['life'] -= dt
            particle['y'] -= particle['speed'] * dt
            particle['x'] += math.sin(particle['life'] * 10) * 0.5
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def add_compression_particle(self, x, y):
        """Add a compression effect particle"""
        self.particles.append({
            'x': x,
            'y': y,
            'speed': 50 + pygame.time.get_ticks() % 50,
            'life': 1.0,
            'size': 2 + pygame.time.get_ticks() % 4,
            'color': COLORS["neon_purple"]
        })
    
    def draw(self, screen, compressed_bits, data_shards, efficiency, rate):
        """Draw the enhanced compression panel"""
        # Draw panel background with gradient effect
        panel_surface = pygame.Surface((self.rect.width, self.rect.height))
        panel_surface.set_alpha(200)
        
        # Gradient background
        for i in range(self.rect.height):
            color_factor = i / self.rect.height
            color = (
                int(COLORS["deep_space_blue"][0] * (1 - color_factor) + COLORS["neon_purple"][0] * color_factor * 0.3),
                int(COLORS["deep_space_blue"][1] * (1 - color_factor) + COLORS["neon_purple"][1] * color_factor * 0.3),
                int(COLORS["deep_space_blue"][2] * (1 - color_factor) + COLORS["neon_purple"][2] * color_factor * 0.3)
            )
            pygame.draw.line(panel_surface, color, (0, i), (self.rect.width, i))
        
        screen.blit(panel_surface, self.rect)
        
        # Draw border with glow effect
        border_color = COLORS["neon_purple"]
        for i in range(3):
            alpha = 100 - i * 30
            glow_surface = pygame.Surface((self.rect.width - i * 4, self.rect.height - i * 4))
            glow_surface.set_alpha(alpha)
            pygame.draw.rect(glow_surface, border_color, glow_surface.get_rect(), 2)
            screen.blit(glow_surface, (self.rect.x + i * 2, self.rect.y + i * 2))
        
        # Draw compression particles
        for particle in self.particles:
            alpha = int(particle['life'] * 255)
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
            particle_surface.set_alpha(alpha)
            particle_surface.fill(particle['color'])
            screen.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))
        
        # Title with animated glow
        title_font = pygame.font.Font(None, 48)
        title_text = "COMPRESSION ERA"
        title_surface = title_font.render(title_text, True, COLORS["neon_purple"])
        title_rect = title_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y + 20)
        
        # Title glow effect
        glow_offset = int(math.sin(self.compression_animation) * 2)
        for i in range(3):
            glow_alpha = 50 - i * 15
            glow_surface = title_surface.copy()
            glow_surface.set_alpha(glow_alpha)
            screen.blit(glow_surface, (title_rect.x + glow_offset + i, title_rect.y + i))
        
        screen.blit(title_surface, title_rect)


class CompressionMeter:
    """Visual compression efficiency meter"""
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.animation = 0
        
    def update(self, dt):
        self.animation += dt * 3
        
    def draw(self, screen, efficiency):
        """Draw compression efficiency meter"""
        # Background
        pygame.draw.rect(screen, COLORS["deep_space_blue"], self.rect)
        pygame.draw.rect(screen, COLORS["neon_purple"], self.rect, 2)
        
        # Efficiency fill
        fill_width = int(self.rect.width * min(efficiency / 100, 1.0))
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        
        # Gradient fill based on efficiency
        if efficiency > 80:
            fill_color = COLORS["matrix_green"]
        elif efficiency > 50:
            fill_color = COLORS["electric_cyan"]
        else:
            fill_color = COLORS["signal_orange"]
        
        pygame.draw.rect(screen, fill_color, fill_rect)
        
        # Animated glow effect
        glow_x = self.rect.x + fill_width
        glow_alpha = (math.sin(self.animation) + 1) * 0.5
        glow_surface = pygame.Surface((10, self.rect.height))
        glow_surface.set_alpha(int(glow_alpha * 100))
        glow_surface.fill(fill_color)
        screen.blit(glow_surface, (glow_x - 5, self.rect.y))
        
        # Efficiency text
        font = pygame.font.Font(None, 28)
        eff_text = f"{efficiency:.1f}%"
        text_surface = font.render(eff_text, True, COLORS["soft_white"])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class TokenDisplay:
    """Animated compression tokens display"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pulse_animation = 0
        self.token_particles = []
        
    def update(self, dt):
        self.pulse_animation += dt * 2
        
        # Update token particles
        for particle in self.token_particles[:]:
            particle['life'] -= dt
            particle['scale'] += dt * 2
            particle['alpha'] -= dt * 200
            
            if particle['alpha'] <= 0:
                self.token_particles.remove(particle)
    
    def add_token_effect(self):
        """Add a token collection effect"""
        self.token_particles.append({
            'life': 1.0,
            'scale': 1.0,
            'alpha': 255,
            'offset_x': 0,
            'offset_y': 0
        })
    
    def draw(self, screen, tokens, font):
        """Draw animated token display"""
        # Token star with pulsing effect
        pulse_scale = 1 + math.sin(self.pulse_animation) * 0.1
        
        # Draw star background glow
        glow_size = int(30 * pulse_scale)
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        glow_color = (*COLORS["gold"], 50)
        pygame.draw.circle(glow_surface, glow_color, (glow_size, glow_size), glow_size)
        screen.blit(glow_surface, (self.x - glow_size, self.y - glow_size))
        
        # Draw star
        star_points = []
        for i in range(10):
            angle = math.pi * i / 5
            if i % 2 == 0:
                radius = 15 * pulse_scale
            else:
                radius = 7 * pulse_scale
            
            x = self.x + math.cos(angle - math.pi / 2) * radius
            y = self.y + math.sin(angle - math.pi / 2) * radius
            star_points.append((x, y))
        
        pygame.draw.polygon(screen, COLORS["gold"], star_points)
        
        # Draw token count
        token_text = f"{tokens}"
        text_surface = font.render(token_text, True, COLORS["gold"])
        text_rect = text_surface.get_rect(midleft=(self.x + 25, self.y))
        screen.blit(text_surface, text_rect)
        
        # Draw token particles
        for particle in self.token_particles:
            alpha = int(particle['alpha'])
            if alpha > 0:
                particle_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
                particle_color = (*COLORS["gold"], alpha)
                pygame.draw.circle(particle_surface, particle_color, (10, 10), int(5 * particle['scale']))
                screen.blit(particle_surface, (self.x + particle['offset_x'] - 10, self.y + particle['offset_y'] - 10))


class CompressionProgressBar:
    """Animated progress bar for compression visualization"""
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.progress = 0
        self.target_progress = 0
        self.animation_speed = 2
        
    def set_progress(self, progress):
        """Set target progress (0-1)"""
        self.target_progress = max(0, min(1, progress))
    
    def update(self, dt):
        """Smoothly animate progress bar"""
        if abs(self.progress - self.target_progress) > 0.01:
            direction = 1 if self.target_progress > self.progress else -1
            self.progress += direction * self.animation_speed * dt
            self.progress = max(0, min(1, self.progress))
    
    def draw(self, screen):
        """Draw animated progress bar"""
        # Background
        pygame.draw.rect(screen, COLORS["deep_space_blue"], self.rect)
        pygame.draw.rect(screen, COLORS["neon_purple"], self.rect, 1)
        
        # Progress fill with compression visualization
        fill_width = int(self.rect.width * self.progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            
            # Create compression pattern
            for i in range(0, fill_width, 4):
                color_intensity = int(128 + 127 * math.sin(i * 0.1 + pygame.time.get_ticks() * 0.001))
                color = (color_intensity // 2, color_intensity // 3, color_intensity)
                segment_rect = pygame.Rect(self.rect.x + i, self.rect.y, 2, self.rect.height)
                pygame.draw.rect(screen, color, segment_rect)
            
            # Draw compression wave effect
            wave_points = []
            for x in range(0, fill_width, 5):
                y = self.rect.centery + math.sin((x + pygame.time.get_ticks() * 0.002) * 0.05) * 3
                wave_points.append((self.rect.x + x, y))
            
            if len(wave_points) > 1:
                pygame.draw.lines(screen, COLORS["electric_cyan"], False, wave_points, 2)