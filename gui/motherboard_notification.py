"""
Motherboard Upgrade Notification for Bit by Bit Game
"""

import pygame
from constants import COLORS


class MotherboardUpgradeNotification:
    """Notification for motherboard/hardware upgrades"""
    
    def __init__(self, message="", duration=3000):
        self.message = message
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.alpha = 255
        self.active = False
    
    def show(self, message):
        """Show a notification"""
        self.message = message
        self.start_time = pygame.time.get_ticks()
        self.active = True
        self.alpha = 255
    
    def update(self, dt):
        """Update notification state"""
        if self.active and not self.is_active():
            self.active = False
    
    def is_active(self):
        return self.active and pygame.time.get_ticks() - self.start_time < self.duration
    
    def draw(self, screen, width, height):
        """Draw the notification"""
        if not self.is_active():
            return
        
        # Fade out effect
        elapsed = pygame.time.get_ticks() - self.start_time
        self.alpha = max(0, 255 - int(255 * elapsed / self.duration))
        
        font = pygame.font.SysFont("Arial", 24)
        
        # Render text with alpha
        text = font.render(self.message, True, COLORS["matrix_green"])
        text.set_alpha(self.alpha)
        
        # Center at top of screen
        x = (width - text.get_width()) // 2
        y = 100
        
        screen.blit(text, (x, y))
