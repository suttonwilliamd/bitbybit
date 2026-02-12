"""
Main GUI class for Bit by Bit Game
"""

import pygame
import sys
import math
import json
import os
import random
from datetime import datetime

from constants import (
    COLORS, CONFIG, GENERATORS, UPGRADES, WINDOW_WIDTH, WINDOW_HEIGHT,
    FPS, SAVE_FILE, AUTO_SAVE_INTERVAL, REBIRTH_THRESHOLD,
    HARDWARE_GENERATIONS, HARDWARE_CATEGORIES, COMPONENT_BASE_COSTS,
    get_all_generators, get_all_upgrades
)
from game_state import GameState
from visual_effects import Particle, BinaryRain, BitVisualization, SmartBitVisualization
from ui_components import Button, FloatingText
from bit_grid import MotherboardBitGrid
from compression_ui import CompressionPanel, CompressionMeter, TokenDisplay, CompressionProgressBar


class ScrollablePanel:
    """A scrollable panel container for overflow content"""

    def __init__(self, x, y, width, height, title=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.scroll_offset = 0
        self.content_height = 0

    def handle_scroll(self, event):
        """Handle mouse wheel scrolling"""
        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(
            pygame.mouse.get_pos()
        ):
            self.scroll_offset = max(
                0,
                min(
                    self.scroll_offset - event.y * 30,
                    max(
                        0, self.content_height - self.rect.height + 60
                    ),  # 60 for title area
                ),
            )

    def scroll_by(self, amount):
        """Scroll by a relative amount"""
        self.scroll_offset = max(
            0,
            min(
                self.scroll_offset + amount,
                max(0, self.content_height - self.rect.height + 60),
            ),
        )

    def scroll_to(self, position):
        """Scroll to an absolute position"""
        self.scroll_offset = max(0, min(position, max(0, self.content_height - self.rect.height + 60)))

    def scroll_to_bottom(self):
        """Scroll to the bottom of the content"""
        self.scroll_offset = max(0, self.content_height - self.rect.height + 60)

    def get_scroll_offset(self):
        """Get current scroll position"""
        return self.scroll_offset

    def set_content_height(self, height):
        """Set the total height of scrollable content"""
        self.content_height = height


class BitByBitGame:
    def __init__(self):
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE
        )
        pygame.display.set_caption("Bit by Bit - A Game About Information")
        self.clock = pygame.time.Clock()
        self.running = True

        # Store original dimensions for responsive calculations
        self.base_width = WINDOW_WIDTH
        self.base_height = WINDOW_HEIGHT
        self.current_width = WINDOW_WIDTH
        self.current_height = WINDOW_HEIGHT

        # Fonts - consistent monospace for tech theme
        try:
            self.title_font = pygame.font.SysFont("Consolas", 24, bold=True)
            self.large_font = pygame.font.SysFont("Consolas", 18, bold=True)
            self.medium_font = pygame.font.SysFont("Consolas", 16)
            self.small_font = pygame.font.SysFont("Consolas", 13)
            self.tiny_font = pygame.font.SysFont("Consolas", 11)
            self.monospace_font = pygame.font.SysFont("Consolas", 16)
            self.bit_counter_font = pygame.font.SysFont("Consolas", 28, bold=True)
        except (pygame.error, OSError):
            self.title_font = pygame.font.Font(None, 24)
            self.large_font = pygame.font.Font(None, 18)
            self.medium_font = pygame.font.Font(None, 16)
            self.small_font = pygame.font.Font(None, 13)
            self.tiny_font = pygame.font.Font(None, 11)
            self.monospace_font = pygame.font.Font(None, 16)
            self.bit_counter_font = pygame.font.Font(None, 28)

        # Game state
        self.state = GameState()

        # Visual systems with enhanced visualization
        self.binary_rain = BinaryRain(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.bit_visualization = SmartBitVisualization(WINDOW_WIDTH // 2, 200)

        # Accessibility and performance settings
        self.high_contrast_mode = False
        self.reduced_motion_mode = False
        self.visual_quality = "high"  # high, medium, low

        # Bit grid for accumulator visualization
        self.bit_grid = MotherboardBitGrid(
            WINDOW_WIDTH // 2 - 300,
            120,
            600,
            240,
        )

        self.click_button = Button(
            WINDOW_WIDTH // 2 - 100, 500, 200, 50, "+1 bit", (60, 60, 80)
        )

        # Initialize compression UI components
        self.compression_panel = CompressionPanel(
            WINDOW_WIDTH // 2 - 300, 50, 600, 120
        )
        self.compression_meter = CompressionMeter(
            WINDOW_WIDTH // 2 - 150, 190, 300, 25
        )
        self.token_display = TokenDisplay(
            WINDOW_WIDTH // 2 - 50, 230
        )
        self.compression_progress = CompressionProgressBar(
            WINDOW_WIDTH // 2 - 200, 270, 400, 30
        )

        self._gradient_surface = None
        self._last_gradient_size = (0, 0)

        # Header buttons
        self.settings_button = Button(
            WINDOW_WIDTH - 150, 20, 120, 40, "⚙️ CONFIG", (50, 50, 70)
        )
        self.stats_button = Button(
            WINDOW_WIDTH - 280, 20, 120, 40, "📊 STATUS", (50, 50, 70)
        )

        # Generator buttons
        self.generator_buttons = {}
        self.generator_buy_buttons = {}
        self.setup_generator_buttons()

        # Upgrade buttons
        self.upgrade_buttons = {}
        self.setup_upgrade_buttons()

        # Component upgrade buttons
        self.component_upgrade_buttons = {}
        self.setup_component_upgrade_buttons()

        # Settings state
        self.showing_settings = False

        # Rebirth state
        self.showing_rebirth_confirmation = False

        # Panel states - hardware panel starts expanded, upgrades collapsed for cleaner look
        self.hardware_panel_open = True
        self.upgrades_panel_open = False

        # New layout structure: Left sidebar (hardware), Right sidebar (upgrades), Center (click area)
        # Top bar takes 60px, side panels take 22% width each
        
        # Calculate responsive layout zones
        top_bar_height = 70
        side_panel_width = int(WINDOW_WIDTH * 0.22)
        center_area_width = WINDOW_WIDTH - (side_panel_width * 2)
        
        # Panel vertical positioning - below top bar
        panel_y_start = top_bar_height + 20
        panel_height = WINDOW_HEIGHT - panel_y_start - 100
        toggle_button_height = 40
        
        # Left panel (Hardware/Information Sources)
        left_panel_x = 15
        
        # Right panel (Upgrades)
        right_panel_x = WINDOW_WIDTH - side_panel_width - 15
        
        # Center area for click button and accumulator
        self.center_area_x = side_panel_width + 20
        self.center_area_width = center_area_width - 40

        # Scrollable panels with new layout - Hardware on left, Upgrades on right
        self.hardware_scroll_panel = ScrollablePanel(
            left_panel_x,
            panel_y_start + toggle_button_height,
            side_panel_width,
            panel_height,
            "HARDWARE",
        )
        self.upgrades_scroll_panel = ScrollablePanel(
            right_panel_x,
            panel_y_start + toggle_button_height,
            side_panel_width,
            panel_height,
            "UPGRADES",
        )

        # Panel toggle buttons - always visible on each side
        self.hardware_toggle = Button(
            left_panel_x,
            panel_y_start,
            side_panel_width,
            toggle_button_height,
            "▸ HARDWARE",
            (25, 30, 45),
            high_contrast=self.high_contrast_mode,
        )
        self.upgrades_toggle = Button(
            right_panel_x,
            panel_y_start,
            side_panel_width,
            toggle_button_height,
            "▸ UPGRADES",
            (25, 30, 45),
            high_contrast=self.high_contrast_mode,
        )

        # Effects
        self.particles = []
        self.floating_texts = []

        # Timing
        self.last_auto_save = pygame.time.get_ticks()
        self.last_update = pygame.time.get_ticks()

        # Tutorial
        self.showing_tutorial = False
        self.tutorial_text = ""

        # CRT overlay surface
        self.crt_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.crt_surface.set_alpha(30)

        # Rebirth button (shows when available)
        self.rebirth_button = Button(
            WINDOW_WIDTH // 2 - 150,
            WINDOW_HEIGHT - 120,
            300,
            40,
            "🌀 COMPRESS DATA",
            COLORS["neon_purple"],
            COLORS["soft_white"],
        )

        # Load save
        self.load_game()

    def handle_window_resize(self, new_width, new_height):
        """Handle window resizing and update UI element positions for new layout"""
        self.current_width = new_width
        self.current_height = new_height

        # Calculate scale factors
        scale_x = new_width / self.base_width
        scale_y = new_height / self.base_height

        # New layout: side panels fixed at 22% width, center area between them
        side_panel_width = int(new_width * 0.22)
        center_x = side_panel_width + 20
        center_width = new_width - (side_panel_width * 2) - 40
        
        # Top bar height
        top_bar_height = int(70 * scale_y)
        
        # Update accumulator and bit grid - center area
        self.bit_grid.x = int(center_x + 25 * scale_x)
        self.bit_grid.width = int(center_width - 50 * scale_x)
        self.bit_grid.height = int(200 * scale_y)

        # Update click button - center area
        click_button_width = int(min(280, center_width * 0.7))
        self.click_button.rect.x = int(center_x + (center_width - click_button_width) // 2)
        self.click_button.rect.y = int(top_bar_height + 280 * scale_y)
        self.click_button.rect.width = click_button_width
        self.click_button.rect.height = int(60 * scale_y)
        
        # Update compression UI components - center area
        self.compression_panel.rect.x = int(center_x + (center_width - int(600 * scale_x)) // 2)
        self.compression_panel.rect.y = int(top_bar_height + 30 * scale_y)
        self.compression_panel.rect.width = int(min(600 * scale_x, center_width - 40))
        self.compression_panel.rect.height = int(120 * scale_y)
        
        self.compression_meter.rect.x = int(center_x + (center_width - int(300 * scale_x)) // 2)
        self.compression_meter.rect.y = int(top_bar_height + 160 * scale_y)
        self.compression_meter.rect.width = int(300 * scale_x)
        self.compression_meter.rect.height = int(25 * scale_y)
        
        self.token_display.x = int(center_x + center_width // 2 - 50)
        self.token_display.y = int(top_bar_height + 200 * scale_y)
        
        self.compression_progress.rect.x = int(center_x + (center_width - int(400 * scale_x)) // 2)
        self.compression_progress.rect.y = int(top_bar_height + 240 * scale_y)
        self.compression_progress.rect.width = int(400 * scale_x)
        self.compression_progress.rect.height = int(30 * scale_y)

        # Update header buttons - top right
        self.settings_button.rect.x = int(new_width - 150 * scale_x)
        self.settings_button.rect.y = int(15 * scale_y)
        self.stats_button.rect.x = int(new_width - 280 * scale_x)
        self.stats_button.rect.y = int(15 * scale_y)

        # Side panel dimensions
        toggle_button_height = int(40 * scale_y)
        panel_y_start = top_bar_height + int(20 * scale_y)
        panel_height = new_height - panel_y_start - int(80 * scale_y)
        
        # Hardware panel (left side)
        self.hardware_scroll_panel.rect.x = int(15 * scale_x)
        self.hardware_scroll_panel.rect.y = panel_y_start + toggle_button_height
        self.hardware_scroll_panel.rect.width = side_panel_width
        self.hardware_scroll_panel.rect.height = panel_height

        # Upgrades panel (right side)
        self.upgrades_scroll_panel.rect.x = new_width - side_panel_width - int(15 * scale_x)
        self.upgrades_scroll_panel.rect.y = panel_y_start + toggle_button_height
        self.upgrades_scroll_panel.rect.width = side_panel_width
        self.upgrades_scroll_panel.rect.height = panel_height

        # Panel toggle buttons
        self.hardware_toggle.rect.x = int(15 * scale_x)
        self.hardware_toggle.rect.y = panel_y_start
        self.hardware_toggle.rect.width = side_panel_width
        self.hardware_toggle.rect.height = toggle_button_height

        self.upgrades_toggle.rect.x = new_width - side_panel_width - int(15 * scale_x)
        self.upgrades_toggle.rect.y = panel_y_start
        self.upgrades_toggle.rect.width = side_panel_width
        self.upgrades_toggle.rect.height = toggle_button_height

        # Update rebirth button
        self.rebirth_button.rect.x = int(new_width // 2 - 150 * scale_x)
        self.rebirth_button.rect.y = int(new_height - 120 * scale_y)
        self.rebirth_button.rect.width = int(300 * scale_x)

        # Update visual systems that need resize info
        self.bit_visualization.center_x = new_width // 2
        self.binary_rain.width = new_width
        self.binary_rain.height = new_height

        # Update component positions in bit grid after scaling
        for comp_name, comp in self.bit_grid.components.items():
            comp["x"] = int(self.bit_grid.x + self.bit_grid.width * comp["x_ratio"])
            comp["y"] = int(self.bit_grid.y + self.bit_grid.height * comp["y_ratio"])
            comp["width"] = int(self.bit_grid.width * comp["width_ratio"])
            comp["height"] = int(self.bit_grid.height * comp["height_ratio"])

            # Update component upgrade button position
            button_width = int(60 * scale_x)
            button_height = int(20 * scale_y)
            button_x = comp["x"] + comp["width"] - button_width - 5
            button_y = comp["y"] + comp["height"] - button_height - 5

            self.component_upgrade_buttons[comp_name].rect.x = button_x
            self.component_upgrade_buttons[comp_name].rect.y = button_y
            self.component_upgrade_buttons[comp_name].rect.width = button_width
            self.component_upgrade_buttons[comp_name].rect.height = button_height

    def setup_generator_buttons(self):
        x_start = 50
        y_start = 200
        card_height = 140
        card_width = 500

        # Setup buttons for basic generators
        for i, (gen_id, generator) in enumerate(CONFIG["GENERATORS"].items()):
            y = y_start + i * (card_height + 10)

            # Buy buttons
            card_height = 95 if "category" in generator else 80
            button_y = y + card_height - 35
            buy_x1 = Button(x_start + card_width - 180, button_y, 70, 30, "BUY x1")
            buy_x10 = Button(x_start + card_width - 100, button_y, 70, 30, "BUY x10")

            self.generator_buy_buttons[gen_id] = {"x1": buy_x1, "x10": buy_x10}
        
        # Setup buttons for hardware generators
        if "HARDWARE_GENERATORS" in CONFIG:
            for gen_id, generator in CONFIG["HARDWARE_GENERATORS"].items():
                # Hardware generators use similar button positioning
                buy_x1 = Button(x_start + card_width - 180, 50, 70, 30, "BUY x1")
                buy_x10 = Button(x_start + card_width - 100, 50, 70, 30, "BUY x10")
                
                self.generator_buy_buttons[gen_id] = {"x1": buy_x1, "x10": buy_x10}

    def setup_upgrade_buttons(self):
        x_start = 750
        y_start = 200
        card_height = 120

        # Get upgrade from both basic and hardware upgrades
        basic_upgrades = UPGRADES if UPGRADES else CONFIG["UPGRADES"]
        hardware_upgrades = CONFIG.get("HARDWARE_UPGRADES", {})
        all_upgrades = {**basic_upgrades, **hardware_upgrades}

        for i, (upgrade_id, upgrade) in enumerate(all_upgrades.items()):
            y = y_start + i * (card_height + 10)

            buy_button = Button(x_start + 250, y + 70, 80, 30, "BUY")
            self.upgrade_buttons[upgrade_id] = buy_button

    def setup_component_upgrade_buttons(self):
        """Setup upgrade buttons for motherboard components"""
        # Position upgrade buttons near each component
        button_width = 60
        button_height = 20

        for comp_name, comp in self.bit_grid.components.items():
            # Position button at bottom of each component
            button_x = comp["x"] + comp["width"] - button_width - 5
            button_y = comp["y"] + comp["height"] - button_height - 5

            upgrade_button = Button(
                button_x, button_y, button_width, button_height, "UP"
            )
            self.component_upgrade_buttons[comp_name] = upgrade_button

    def format_number(self, num):
        if num < 1000:
            return str(int(num))
        elif num < 1000000:
            return f"{num / 1000:.1f}K"
        elif num < 1000000000:
            return f"{num / 1000000:.1f}M"
        elif num < 1000000000000:
            return f"{num / 1000000000:.1f}B"
        else:
            return f"{num / 1000000000000:.1f}T"

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.handle_window_resize(event.w, event.h)

            # Handle scroll events
            if event.type == pygame.MOUSEWHEEL:
                self.hardware_scroll_panel.handle_scroll(event)
                self.upgrades_scroll_panel.handle_scroll(event)

            # Handle keyboard scroll (arrow keys)
            if event.type == pygame.KEYDOWN:
                scroll_amount = 50
                if event.key == pygame.K_UP:
                    self.hardware_scroll_panel.scroll_by(-scroll_amount)
                    self.upgrades_scroll_panel.scroll_by(-scroll_amount)
                elif event.key == pygame.K_DOWN:
                    self.hardware_scroll_panel.scroll_by(scroll_amount)
                    self.upgrades_scroll_panel.scroll_by(scroll_amount)
                elif event.key == pygame.K_PAGEUP:
                    self.hardware_scroll_panel.scroll_by(-scroll_amount * 5)
                    self.upgrades_scroll_panel.scroll_by(-scroll_amount * 5)
                elif event.key == pygame.K_PAGEDOWN:
                    self.hardware_scroll_panel.scroll_by(scroll_amount * 5)
                    self.upgrades_scroll_panel.scroll_by(scroll_amount * 5)
                elif event.key == pygame.K_HOME:
                    self.hardware_scroll_panel.scroll_to(0)
                    self.upgrades_scroll_panel.scroll_to(0)
                elif event.key == pygame.K_END:
                    self.hardware_scroll_panel.scroll_to_bottom()
                    self.upgrades_scroll_panel.scroll_to_bottom()

            # Handle rebirth confirmation modal - this blocks all other interactions
            if self.showing_rebirth_confirmation:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    yes_rect = pygame.Rect(
                        WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 + 50, 100, 40
                    )
                    no_rect = pygame.Rect(
                        WINDOW_WIDTH // 2 + 20, WINDOW_HEIGHT // 2 + 50, 100, 40
                    )

                    if yes_rect.collidepoint(mouse_pos):
                        result = self.state.perform_rebirth()
                        if result:
                            self.showing_rebirth_confirmation = False
                            # Reset bit grid and upgrade to new era
                            self.bit_grid.reset_on_rebirth()
                            self.bit_grid.upgrade_to_era(self.state.hardware_generation)

                            if (
                                isinstance(result, tuple)
                                and len(result) == 2
                                and result[1]
                            ):
                                self.create_hardware_advancement_effect()
                            else:
                                self.create_rebirth_effect()
                    elif no_rect.collidepoint(mouse_pos):
                        self.showing_rebirth_confirmation = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.showing_rebirth_confirmation = False
                continue  # Skip all other event processing when modal is open

            # Handle settings modal - this blocks all other interactions
            if self.showing_settings:
                self.handle_settings_events(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.showing_settings = False
                continue  # Skip all other event processing when settings is open

            # Handle tutorial modal - this blocks all other interactions
            if self.showing_tutorial:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if click is on continue button area
                    continue_rect = pygame.Rect(
                        WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 60, 200, 40
                    )
                    if continue_rect.collidepoint(mouse_pos):
                        self.showing_tutorial = False
                        self.tutorial_text = ""
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.showing_tutorial = False
                    self.tutorial_text = ""
                continue  # Skip all other event processing when tutorial is open

            # Handle normal game interactions
            # Handle click button
            if self.click_button.is_clicked(event):
                self.handle_click()

            # Handle generator purchases (only when panel is open and left mouse button)
            if (
                self.hardware_panel_open
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                self.handle_generator_card_clicks(mouse_pos)

            # Handle upgrade purchases (only when panel is open and left mouse button)
            if (
                self.upgrades_panel_open
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                self.handle_upgrade_card_clicks(mouse_pos)

            # Handle component upgrade purchases (always active)
            for comp_name, button in self.component_upgrade_buttons.items():
                if button.is_clicked(event):
                    self.upgrade_component(comp_name)

            # Handle header buttons
            if self.settings_button.is_clicked(event):
                self.showing_settings = True
            elif self.stats_button.is_clicked(event):
                self.show_statistics()

            # Handle panel toggle buttons
            if self.hardware_toggle.is_clicked(event):
                self.hardware_panel_open = not self.hardware_panel_open

            if self.upgrades_toggle.is_clicked(event):
                self.upgrades_panel_open = not self.upgrades_panel_open

            # Handle rebirth button
            if self.state.can_rebirth(self.bit_grid) and self.rebirth_button.is_clicked(
                event
            ):
                self.showing_rebirth_confirmation = True

        # Update button hover states - only update visible elements
        if not self.showing_settings and not self.showing_rebirth_confirmation:
            self.click_button.update(mouse_pos)
            self.settings_button.update(mouse_pos)
            self.stats_button.update(mouse_pos)

            # Only update toggle buttons when modals are closed
            self.hardware_toggle.update(mouse_pos)
            self.upgrades_toggle.update(mouse_pos)

            # Panel buttons are now integrated into cards, no separate updates needed

            # Update rebirth button if available
            if self.state.can_rebirth(self.bit_grid):
                self.rebirth_button.update(mouse_pos)

    def handle_click(self):
        click_power = self.state.get_click_power()
        self.state.bits += click_power
        self.state.total_bits_earned += click_power
        self.state.total_clicks += 1

        # Add bit grid click effect
        self.bit_grid.add_click_effect()

        # Create visual effects (if enabled)
        if self.state.visual_settings["particle_effects"]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.floating_texts.append(
                FloatingText(mouse_x, mouse_y, f"+{self.format_number(click_power)}")
            )

            # Create click particles (reduced from 3 to 1)
            self.particles.append(
                Particle(mouse_x, mouse_y, COLORS["matrix_green"], "click")
            )

        # Check tutorial progress
        self.check_tutorial()

    def buy_generator(self, generator_id, quantity):
        if not self.state.is_generator_unlocked(generator_id):
            return

        cost = self.state.get_generator_cost(generator_id, quantity)

        if self.state.can_afford(cost):
            self.state.bits -= cost
            self.state.generators[generator_id]["count"] += quantity
            self.state.generators[generator_id]["total_bought"] += quantity

            # Add bit grid purchase effect
            self.bit_grid.add_purchase_effect()

            # Create purchase effect - particles from button to accumulator (if enabled)
            if self.state.visual_settings["particle_effects"]:
                button_rect = self.generator_buy_buttons[generator_id]["x1"].rect
                button_center_x = button_rect.centerx
                button_center_y = button_rect.centery

                for _ in range(4):  # Reduced from 8 to 4
                    self.particles.append(
                        Particle(
                            button_center_x,
                            button_center_y,
                            COLORS["electric_cyan"],
                            "purchase",
                        )
                    )

    def buy_upgrade(self, upgrade_id):
        if not self.state.is_upgrade_unlocked(upgrade_id):
            return

        # Get upgrade from both basic and hardware upgrades
        basic_upgrades = UPGRADES if UPGRADES else CONFIG["UPGRADES"]
        hardware_upgrades = CONFIG.get("HARDWARE_UPGRADES", {})
        all_upgrades = {**basic_upgrades, **hardware_upgrades}

        upgrade = all_upgrades[upgrade_id]
        cost = self.state.get_upgrade_cost(upgrade_id)

        if (
            self.state.can_afford(cost)
            and self.state.upgrades[upgrade_id]["level"] < upgrade["max_level"]
        ):
            self.state.bits -= cost
            self.state.upgrades[upgrade_id]["level"] += 1

            # Add bit grid purchase effect
            self.bit_grid.add_purchase_effect()

            # Create purchase effect - particles from button to accumulator (if enabled)
            if self.state.visual_settings["particle_effects"]:
                button_rect = self.upgrade_buttons[upgrade_id].rect
                button_center_x = button_rect.centerx
                button_center_y = button_rect.centery

                for _ in range(4):  # Reduced from 8 to 4
                    self.particles.append(
                        Particle(
                            button_center_x,
                            button_center_y,
                            COLORS["neon_purple"],
                            "purchase",
                        )
                    )

    def handle_generator_card_clicks(self, mouse_pos):
        """Handle clicks on generator card buttons"""
        panel = self.hardware_scroll_panel

        all_generators = get_all_generators()
        basic_generators = GENERATORS if GENERATORS else CONFIG["GENERATORS"]
        hardware_generators = CONFIG.get("HARDWARE_GENERATORS", {})

        y_offset = -panel.get_scroll_offset()

        for gen_id, generator in all_generators.items():
            # Check if unlocked - but always advance y_offset to match drawing
            is_locked = False
            if gen_id in basic_generators:
                if not self.state.is_generator_unlocked(gen_id):
                    is_locked = True
            elif gen_id in hardware_generators:
                if not self.state.is_hardware_category_unlocked(generator.get("category", "")):
                    is_locked = True

            count = self.state.generators[gen_id]["count"]
            cost = self.state.get_generator_cost(gen_id)
            can_afford = self.state.can_afford(cost)

            # Card position (must match drawing code)
            card_x = panel.rect.x + 20
            card_y = panel.rect.y + 50 + y_offset + 8
            card_width = panel.rect.width - 40
            card_height = 90

            # Check if click is within this card
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            if card_rect.collidepoint(mouse_pos):
                # Check button positions (bottom right of card) - updated for compact layout
                button_y = card_y + card_height - 25
                btn_width = 60
                btn_height = 22

                # BUY x10 button (left)
                btn1_rect = pygame.Rect(
                    card_x + card_width - btn_width * 2 - 8, button_y, btn_width, btn_height
                )
                if btn1_rect.collidepoint(mouse_pos) and can_afford:
                    self.buy_generator(gen_id, 10)
                    return

                # BUY x1 button (right)
                btn2_rect = pygame.Rect(
                    card_x + card_width - btn_width - 4, button_y, btn_width, btn_height
                )
                if btn2_rect.collidepoint(mouse_pos) and can_afford:
                    self.buy_generator(gen_id, 1)
                    return

            # Always advance y_offset to match drawing loop
            y_offset += card_height + 14

    def handle_upgrade_card_clicks(self, mouse_pos):
        """Handle clicks on upgrade card buttons"""
        panel = self.upgrades_scroll_panel

        all_upgrades = get_all_upgrades()
        basic_upgrades = UPGRADES if UPGRADES else CONFIG["UPGRADES"]
        hardware_upgrades = CONFIG.get("HARDWARE_UPGRADES", {})

        y_offset = -panel.get_scroll_offset()

        for upgrade_id, upgrade in all_upgrades.items():
            # Check if unlocked - but always advance y_offset to match drawing
            is_locked = False
            if upgrade_id in basic_upgrades:
                if not self.state.is_upgrade_unlocked(upgrade_id):
                    is_locked = True
            elif upgrade_id in hardware_upgrades:
                if not self.state.is_hardware_category_unlocked(upgrade.get("category", "")):
                    is_locked = True

            level = self.state.upgrades[upgrade_id]["level"]
            cost = self.state.get_upgrade_cost(upgrade_id)
            can_afford = self.state.can_afford(cost) and level < upgrade["max_level"]

            # Card position (must match drawing code)
            card_x = panel.rect.x + 20
            card_y = panel.rect.y + 50 + y_offset + 8
            card_width = panel.rect.width - 40
            card_height = 85

            # Check if click is within this card
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            if card_rect.collidepoint(mouse_pos):
                # Check if maxed
                if level < upgrade["max_level"]:
                    # BUY button (bottom right) - updated for compact layout
                    button_x = card_x + card_width - 80
                    button_y = card_y + card_height - 25
                    btn_rect = pygame.Rect(button_x, button_y, 70, 20)

                    if btn_rect.collidepoint(mouse_pos) and can_afford:
                        self.buy_upgrade(upgrade_id)
                        return

            # Always advance y_offset to match drawing loop
            y_offset += card_height + 14

    def upgrade_component(self, comp_name):
        """Upgrade a motherboard component"""
        comp = self.bit_grid.components[comp_name]

        cost_multiplier = 2.5 ** comp["level"]
        cost = int(COMPONENT_BASE_COSTS.get(comp_name, 100) * cost_multiplier)

        if self.state.can_afford(cost) and comp["unlocked"] and comp["level"] < 10:
            self.state.bits -= cost
            self.bit_grid.upgrade_component(comp_name)

            # Add purchase effect
            self.bit_grid.add_purchase_effect()

            # Create purchase effect - particles from button to accumulator
            if self.state.visual_settings["particle_effects"]:
                button_rect = self.component_upgrade_buttons[comp_name].rect
                button_center_x = button_rect.centerx
                button_center_y = button_rect.centery

                for _ in range(6):
                    self.particles.append(
                        Particle(
                            button_center_x,
                            button_center_y,
                            comp["color"],
                            "purchase",
                        )
                    )

    def update(self, dt):
        # Update binary rain (if enabled)
        if self.state.visual_settings["binary_rain"]:
            self.binary_rain.update(dt)
        
        # Update compression UI components
        if self.state.era == "compression":
            self.compression_panel.update(dt)
            self.compression_meter.update(dt)
            self.token_display.update(dt)
            self.compression_progress.update(dt)

        # Update game state
        production_rate = self.state.get_production_rate()
        production = production_rate * dt

        # Use floating-point accumulator for production
        if not hasattr(self, "production_accumulator"):
            self.production_accumulator = 0.0

        self.production_accumulator += production
        production_int = int(self.production_accumulator)

        # Only add the integer part and keep the fractional remainder
        if production_int > 0:
            self.state.bits += production_int
            self.state.total_bits_earned += production_int
            self.production_accumulator -= (
                production_int  # Remove the integer part we just added
            )

        # Check for unlocks
        for gen_id, generator in CONFIG["GENERATORS"].items():
            if "unlock_threshold" in generator:
                if (
                    gen_id not in self.state.unlocked_generators
                    and self.state.total_bits_earned >= generator["unlock_threshold"]
                ):
                    self.state.unlocked_generators.append(gen_id)

        # Update particles (if enabled)
        if self.state.visual_settings["particle_effects"]:
            self.particles = [p for p in self.particles if p.lifetime > 0]
            for particle in self.particles:
                particle.update(dt)

        # Update floating texts (if enabled)
        if self.state.visual_settings["particle_effects"]:
            self.floating_texts = [t for t in self.floating_texts if t.lifetime > 0]
            for text in self.floating_texts:
                text.update(dt)
        else:
            # Clear particles and floating texts if disabled
            self.particles.clear()
            self.floating_texts.clear()

        # Auto-save
        current_time = pygame.time.get_ticks()
        if current_time - self.last_auto_save > CONFIG["AUTO_SAVE_INTERVAL"]:
            self.save_game()
            self.last_auto_save = current_time

    def draw_accumulator(self):
        # Draw compression UI if in compression era
        if self.state.era == "compression":
            self.draw_compression_accumulator()
        else:
            self.draw_standard_accumulator()
    
    def draw_compression_accumulator(self):
        """Draw enhanced accumulator for compression era"""
        production_rate = self.state.get_production_rate()
        dt = 1 / FPS
        
        # Draw compression panel
        self.compression_panel.draw(
            self.screen,
            getattr(self.state, 'compressed_bits', 0),
            getattr(self.state, 'compression_tokens', 0),
            getattr(self.state, 'efficiency', 1.0) * 100,
            production_rate
        )
        
        # Draw compression meter
        self.compression_meter.draw(self.screen, getattr(self.state, 'efficiency', 1.0) * 100)
        
        # Draw token display
        self.token_display.draw(self.screen, getattr(self.state, 'compression_tokens', 0), self.medium_font)
        
        # Draw compression progress bar
        compression_ratio = getattr(self.state, 'efficiency', 1.0)
        self.compression_progress.set_progress(min(compression_ratio / 10, 1.0))  # Normalize to 0-1
        self.compression_progress.draw(self.screen)
        
        # Draw compressed bits with enhanced display
        if not hasattr(self, "display_compressed_bits"):
            self.display_compressed_bits = getattr(self.state, "compressed_bits", 0)
        if not hasattr(self, "display_rate"):
            self.display_rate = self.state.get_production_rate()

        smoothing_factor = 0.1
        self.display_compressed_bits += (
            getattr(self.state, 'compressed_bits', 0) - self.display_compressed_bits
        ) * smoothing_factor
        self.display_rate += (
            self.state.get_production_rate() - self.display_rate
        ) * smoothing_factor

        scale_x = self.current_width / self.base_width
        scale_y = self.current_height / self.base_height
        center_x = self.current_width // 2
        
        # Enhanced compressed bits display
        bits_y = int(320 * scale_y)
        bits_str = f"{self.format_number(int(self.display_compressed_bits))} COMPRESSED BITS"
        bits_text = self.monospace_font.render(bits_str, True, COLORS["neon_purple"])
        bits_rect = bits_text.get_rect(center=(center_x, bits_y))

        # Enhanced glow effect for compression
        for offset, alpha in [((3, 3), 20), ((2, 2), 40), ((1, 1), 60), ((-1, -1), 50), ((-2, -2), 30)]:
            glow_pos = (bits_rect.x + offset[0], bits_rect.y + offset[1])
            glow_surface = bits_text.copy()
            glow_surface.set_alpha(alpha)
            self.screen.blit(glow_surface, glow_pos)

        self.screen.blit(bits_text, bits_rect)

        # Enhanced rate display with compression efficiency
        rate_y = int(350 * scale_y)
        efficiency = getattr(self.state, 'efficiency', 1.0) * 100
        rate_str = f"+{self.format_number(int(self.display_rate))} cb/s @ {efficiency:.1f}% efficiency"
        rate_text = self.medium_font.render(rate_str, True, COLORS["electric_cyan"])
        rate_rect = rate_text.get_rect(center=(center_x, rate_y))

        for offset, alpha in [((2, 2), 30), ((-1, -1), 60)]:
            glow_pos = (rate_rect.x + offset[0], rate_rect.y + offset[1])
            glow_surface = rate_text.copy()
            glow_surface.set_alpha(alpha)
            self.screen.blit(glow_surface, glow_pos)

        self.screen.blit(rate_text, rate_rect)
    
    def draw_standard_accumulator(self):
        """Draw standard accumulator for non-compression eras"""
        production_rate = self.state.get_production_rate()
        dt = 1 / FPS

        scale_x = self.current_width / self.base_width
        scale_y = self.current_height / self.base_height
        
        # New layout: center in the middle area between side panels
        side_panel_width = int(self.current_width * 0.22)
        center_x = side_panel_width + 20
        center_width = self.current_width - (side_panel_width * 2) - 40
        
        # Calculate accumulator dimensions to fit in center area
        acc_width = int(min(600 * scale_x, center_width - 40))
        acc_height = int(300 * scale_y)
        acc_x = center_x + (center_width - acc_width) // 2
        acc_y = int(90 * scale_y)

        self.bit_grid.x = acc_x + int(25 * scale_x)
        self.bit_grid.y = acc_y + int(50 * scale_y)
        self.bit_grid.width = acc_width - int(50 * scale_x)
        self.bit_grid.height = int(180 * scale_y)
        self.bit_grid.update_dimensions(
            self.bit_grid.x, self.bit_grid.y, 
            self.bit_grid.width, self.bit_grid.height
        )

        self.bit_grid.update(
            self.state.bits,
            self.state.total_bits_earned,
            CONFIG["REBIRTH_THRESHOLD"],
            self.state.hardware_generation,
            dt,
        )

        acc_rect = pygame.Rect(acc_x, acc_y, acc_width, acc_height)
        center_x = center_x + center_width // 2  # Center of the center area

        # Background with subtle grid pattern
        pygame.draw.rect(self.screen, (10, 10, 20), acc_rect, border_radius=12)
        
        # Draw subtle grid lines for tech feel
        grid_color = (20, 25, 40)
        grid_spacing = int(20 * scale_x)
        for gx in range(acc_x + grid_spacing, acc_x + acc_width - 10, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (gx, acc_y + 10), (gx, acc_y + acc_height - 10), 1)
        for gy in range(acc_y + grid_spacing, acc_y + acc_height - 10, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (acc_x + 10, gy), (acc_x + acc_width - 10, gy), 1)

        # Animated border glow
        time_ms = pygame.time.get_ticks()
        border_glow = abs(math.sin(time_ms * 0.002)) * 0.2 + 0.8
        border_color = tuple(int(c * border_glow) for c in COLORS["electric_cyan"])
        pygame.draw.rect(self.screen, border_color, acc_rect, 2, border_radius=12)

        # Decorative binary stream on left side
        self._draw_binary_stream(acc_x - int(30 * scale_x), acc_y + int(50 * scale_y), int(25 * scale_y))

        title_text = self.small_font.render(
            "DATA ACCUMULATOR", True, COLORS["muted_blue"]
        )
        title_rect = title_text.get_rect(center=(center_x, acc_y + int(18 * scale_y)))
        self.screen.blit(title_text, title_rect)

        self.bit_grid.draw(self.screen)

        bit_percent = self.bit_grid.get_bit_completeness_percentage()
        progress_text = self.small_font.render(
            f"{bit_percent:.0f}% Complete", True, COLORS["matrix_green"]
        )
        progress_rect = progress_text.get_rect(center=(center_x, acc_y + int(38 * scale_y)))
        self.screen.blit(progress_text, progress_rect)

        if not hasattr(self, "display_bits"):
            self.display_bits = self.state.bits
        if not hasattr(self, "display_rate"):
            self.display_rate = self.state.get_production_rate()

        smoothing_factor = 0.1
        self.display_bits += (self.state.bits - self.display_bits) * smoothing_factor
        self.display_rate += (
            self.state.get_production_rate() - self.display_rate
        ) * smoothing_factor

        bits_str = f"{self.format_number(int(self.display_bits))} bits"
        bits_color = COLORS["electric_cyan"]

        bits_text = self.monospace_font.render(bits_str, True, bits_color)
        bits_y = acc_y + int(255 * scale_y)
        bits_rect = bits_text.get_rect(center=(center_x, bits_y))

        for offset, alpha in [((2, 2), 30), ((1, 1), 60), ((-1, -1), 40)]:
            glow_pos = (bits_rect.x + offset[0], bits_rect.y + offset[1])
            glow_surface = bits_text.copy()
            glow_surface.set_alpha(alpha)
            self.screen.blit(glow_surface, glow_pos)

        self.screen.blit(bits_text, bits_rect)

        current_rate = self.state.get_production_rate()
        self.last_display_rate = current_rate

        rate_y = acc_y + int(285 * scale_y)
        rate_str = f"+{self.format_number(int(self.display_rate))} b/s"
        rate_color = COLORS["matrix_green"]

        rate_text = self.monospace_font.render(rate_str, True, rate_color)
        rate_rect = rate_text.get_rect(center=(center_x, rate_y))

        for offset, alpha in [((1, 1), 25), ((-1, -1), 50)]:
            glow_pos = (rate_rect.x + offset[0], rate_rect.y + offset[1])
            glow_surface = rate_text.copy()
            glow_surface.set_alpha(alpha)
            self.screen.blit(glow_surface, glow_pos)

        self.screen.blit(rate_text, rate_rect)

        button_y = acc_y + acc_height + int(15 * scale_y)
        button_width = int(200 * scale_x)
        button_height = int(50 * scale_y)
        button_x = center_x - button_width // 2

        if self.state.era == "entropy":
            click_power = self.state.get_click_power()
            self.click_button.rect = pygame.Rect(button_x, button_y, button_width, button_height)
            self.click_button.text = f"+{self.format_number(click_power)} bit{'s' if click_power != 1 else ''}"
            self.click_button.draw(self.screen)

    def _update_button_accessibility(self):
        """Update all buttons to match accessibility settings"""
        # Update panel toggle buttons
        self.hardware_toggle.high_contrast = self.high_contrast_mode
        self.upgrades_toggle.high_contrast = self.high_contrast_mode
        self.click_button.high_contrast = self.high_contrast_mode
        self.settings_button.high_contrast = self.high_contrast_mode
        self.stats_button.high_contrast = self.high_contrast_mode

        # Update other buttons as needed
        for button_list in [
            self.generator_buy_buttons,
            self.upgrade_buttons,
            self.component_upgrade_buttons,
        ]:
            if isinstance(button_list, dict):
                for button in button_list.values():
                    if isinstance(button, Button):
                        button.high_contrast = self.high_contrast_mode
                    elif isinstance(button, dict):  # Generator buy buttons have x1/x10
                        for sub_button in button.values():
                            if isinstance(sub_button, Button):
                                sub_button.high_contrast = self.high_contrast_mode

    def handle_settings_events(self, event):
        mouse_pos = pygame.mouse.get_pos()

        # Settings toggle buttons positions - expanded for accessibility
        crt_toggle_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 250, 400, 40)
        rain_toggle_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 300, 400, 40)
        particle_toggle_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 350, 400, 40)
        high_contrast_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 400, 400, 40)
        reduced_motion_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 450, 400, 40)
        quality_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 500, 400, 40)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if crt_toggle_rect.collidepoint(mouse_pos):
                self.state.visual_settings[
                    "crt_effects"
                ] = not self.state.visual_settings["crt_effects"]
            elif rain_toggle_rect.collidepoint(mouse_pos):
                self.state.visual_settings[
                    "binary_rain"
                ] = not self.state.visual_settings["binary_rain"]
            elif particle_toggle_rect.collidepoint(mouse_pos):
                self.state.visual_settings[
                    "particle_effects"
                ] = not self.state.visual_settings["particle_effects"]
            elif high_contrast_rect.collidepoint(mouse_pos):
                self.high_contrast_mode = not self.high_contrast_mode
                # Update all buttons to use high contrast mode
                self._update_button_accessibility()
            elif reduced_motion_rect.collidepoint(mouse_pos):
                self.reduced_motion_mode = not self.reduced_motion_mode
                # Update visualization quality
                quality = "low" if self.reduced_motion_mode else self.visual_quality
                self.bit_visualization.set_quality_level(quality)
            elif quality_rect.collidepoint(mouse_pos):
                # Cycle through quality levels
                quality_levels = ["high", "medium", "low"]
                current_index = quality_levels.index(self.visual_quality)
                self.visual_quality = quality_levels[
                    (current_index + 1) % len(quality_levels)
                ]
                self.bit_visualization.set_quality_level(self.visual_quality)

    def show_statistics(self):
        # This would show a statistics modal, for now just print to console
        print(f"""
=== STATISTICS ===
Time Played: {(pygame.time.get_ticks() - self.state.start_time) // 1000}s
Total Bits Earned: {self.format_number(self.state.total_bits_earned)}
Current Production: {self.format_number(self.state.get_production_rate())} b/s
Total Clicks: {self.state.total_clicks}
=================
        """)

    def create_rebirth_effect(self):
        """Create spectacular rebirth animation"""
        # Create burst of particles from accumulator
        center_x = WINDOW_WIDTH // 2
        center_y = 200

        for _ in range(50):
            color = random.choice(
                [COLORS["electric_cyan"], COLORS["neon_purple"], COLORS["gold"]]
            )
            self.particles.append(Particle(center_x, center_y, color, "burst"))

        # Create floating text for tokens earned (only if user actually has tokens)
        if (
            hasattr(self.state, "compression_tokens")
            and self.state.compression_tokens > 0
        ):
            current_tokens = self.state.compression_tokens
            self.floating_texts.append(
                FloatingText(
                    center_x,
                    center_y - 50,
                    f"+{current_tokens} ⭐ TOKENS!",
                    COLORS["gold"],
                )
            )
            # Add more particles for rebirth effect
            for _ in range(10):
                particle_color = random.choice(
                    [COLORS["electric_cyan"], COLORS["neon_purple"], COLORS["gold"]]
                )
                self.particles.append(
                    Particle(center_x, center_y, particle_color, "burst")
                )

        # Create floating text for tokens earned (only if user actually has tokens)
        if (
            hasattr(self.state, "compression_tokens")
            and self.state.compression_tokens > 0
        ):
            current_tokens = self.state.compression_tokens
            self.floating_texts.append(
                FloatingText(
                    center_x,
                    center_y - 50,
                    f"+{current_tokens} ⭐ TOKENS!",
                    COLORS["gold"],
                )
            )

    def create_hardware_advancement_effect(self):
        """Create spectacular hardware advancement animation"""
        # Create massive burst of particles for advancement
        center_x = self.current_width // 2
        center_y = int(250 * (self.current_height / self.base_height))

        for _ in range(100):  # Double normal rebirth effect
            color = random.choice(
                [
                    COLORS["electric_cyan"],
                    COLORS["neon_purple"],
                    COLORS["gold"],
                    COLORS["signal_orange"],
                ]
            )
            self.particles.append(Particle(center_x, center_y, color, "burst"))

        # Create floating text for hardware advancement
        from constants import HARDWARE_GENERATIONS

        current_gen = HARDWARE_GENERATIONS[self.state.hardware_generation]
        self.floating_texts.append(
            FloatingText(
                center_x,
                center_y - 100,
                f"HARDWARE UPGRADE!",
                COLORS["gold"],
            )
        )
        self.floating_texts.append(
            FloatingText(
                center_x,
                center_y - 70,
                f"{current_gen['name']}",
                COLORS["neon_purple"],
            )
        )

    def check_tutorial(self):
        # Don't show tutorial if player has already seen it OR has compressed/rebirthed
        if self.state.has_seen_tutorial or self.state.total_rebirths > 0:
            return

        step = self.state.tutorial_step

        if step == 0 and self.state.total_bits_earned >= 10:
            # Check if user already has any generators
            has_generators = any(
                gen["count"] > 0 for gen in self.state.generators.values()
            )
            if not has_generators:
                self.showing_tutorial = True
                self.tutorial_text = "Great! You've generated your first bits.\nBut clicking gets tedious quickly.\nTry buying your first generator!"
        elif step == 1 and self.state.generators["rng"]["count"] >= 1:
            self.showing_tutorial = True
            self.tutorial_text = "Excellent! Your Random Number Generator\nnow produces 1 bit per second automatically.\nKeep generating to unlock new content!"
            self.state.has_seen_tutorial = True
            # Create celebration effect at accumulator center
            center_x = WINDOW_WIDTH // 2
            center_y = 250
            color = COLORS["matrix_green"]
            self.particles.append(Particle(center_x, center_y, color, "burst"))

        # Create floating text for tokens earned (only if user actually has tokens)
        if (
            hasattr(self.state, "compression_tokens")
            and self.state.compression_tokens > 0
        ):
            current_tokens = self.state.compression_tokens
            center_x = WINDOW_WIDTH // 2
            center_y = 250
            self.floating_texts.append(
                FloatingText(
                    center_x,
                    center_y - 50,
                    f"+{current_tokens} ⭐ TOKENS!",
                    COLORS["gold"],
                )
            )

    def save_game(self):
        save_data = {
            "version": "1.0.0",
            "timestamp": pygame.time.get_ticks(),
            "state": {
                "bits": self.state.bits,
                "total_bits_earned": self.state.total_bits_earned,
                "total_clicks": self.state.total_clicks,
                "start_time": self.state.start_time,
                "total_play_time": self.state.total_play_time,
                "generators": self.state.generators,
                "unlocked_generators": self.state.unlocked_generators,
                "upgrades": self.state.upgrades,
                "tutorial_step": self.state.tutorial_step,
                "has_seen_tutorial": self.state.has_seen_tutorial,
                "visual_settings": self.state.visual_settings,
                
                # Compression/rebirth state
                "total_rebirths": self.state.total_rebirths,
                "total_lifetime_bits": self.state.total_lifetime_bits,
                "hardware_generation": self.state.hardware_generation,
                "unlocked_hardware_categories": self.state.unlocked_hardware_categories,
                "era": self.state.era,
                "compression_tokens": self.state.compression_tokens,
                "total_compression_tokens": self.state.total_compression_tokens,
                "compressed_bits": self.state.compressed_bits,
                "total_compressed_bits": self.state.total_compressed_bits,
                "overhead_rate": self.state.overhead_rate,
                "efficiency": self.state.efficiency,
            },
        }

        try:
            with open(CONFIG["SAVE_FILE"], "w") as f:
                json.dump(save_data, f, indent=2)
            self.state.last_save_time = pygame.time.get_ticks()
        except Exception as e:
            print(f"Failed to save game: {e}")

    def load_game(self):
        if not os.path.exists(CONFIG["SAVE_FILE"]):
            # Show initial tutorial
            self.showing_tutorial = True
            self.tutorial_text = "Welcome to BIT BY BIT!\n\nYou are about to discover\nfundamental nature of information.\n\nClick accumulator to generate\nyour first bits."
            return

        try:
            with open(CONFIG["SAVE_FILE"], "r") as f:
                save_data = json.load(f)

            # Restore state
            state_data = save_data["state"]
            self.state.bits = state_data.get("bits", 0)
            self.state.total_bits_earned = state_data.get("total_bits_earned", 0)
            self.state.total_clicks = state_data.get("total_clicks", 0)
            self.state.start_time = state_data.get(
                "start_time", pygame.time.get_ticks()
            )
            self.state.total_play_time = state_data.get("total_play_time", 0)
            
            # Load compression/rebirth state
            self.state.total_rebirths = state_data.get("total_rebirths", 0)
            self.state.total_lifetime_bits = state_data.get("total_lifetime_bits", 0)
            self.state.hardware_generation = state_data.get("hardware_generation", 0)
            self.state.unlocked_hardware_categories = state_data.get("unlocked_hardware_categories", ["cpu"])
            
            # Load compression era state
            self.state.era = state_data.get("era", "entropy")
            self.state.compression_tokens = state_data.get("compression_tokens", 0)
            self.state.total_compression_tokens = state_data.get("total_compression_tokens", 0)
            self.state.compressed_bits = state_data.get("compressed_bits", 0)
            self.state.total_compressed_bits = state_data.get("total_compressed_bits", 0)
            self.state.overhead_rate = state_data.get("overhead_rate", 0)
            self.state.efficiency = state_data.get("efficiency", 1.0)
            self.state.generators = state_data.get("generators", self.state.generators)
            self.state.unlocked_generators = state_data.get(
                "unlocked_generators", ["rng"]
            )
            self.state.upgrades = state_data.get("upgrades", self.state.upgrades)
            self.state.tutorial_step = state_data.get("tutorial_step", 0)
            self.state.has_seen_tutorial = state_data.get("has_seen_tutorial", False)
            self.state.visual_settings = state_data.get(
                "visual_settings", self.state.visual_settings
            )

            # Merge missing generators/upgrades that were added since the save was made
            # Initialize basic generators that might be missing
            for gen_id in CONFIG["GENERATORS"]:
                if gen_id not in self.state.generators:
                    self.state.generators[gen_id] = {"count": 0, "total_bought": 0}
            
            # Initialize hardware generators that might be missing
            if "HARDWARE_GENERATORS" in CONFIG:
                for gen_id in CONFIG["HARDWARE_GENERATORS"]:
                    if gen_id not in self.state.generators:
                        self.state.generators[gen_id] = {"count": 0, "total_bought": 0}
            
            # Initialize missing upgrades
            for upgrade_id in CONFIG["UPGRADES"]:
                if upgrade_id not in self.state.upgrades:
                    self.state.upgrades[upgrade_id] = {"level": 0}
            
            if "HARDWARE_UPGRADES" in CONFIG:
                for upgrade_id in CONFIG["HARDWARE_UPGRADES"]:
                    if upgrade_id not in self.state.upgrades:
                        self.state.upgrades[upgrade_id] = {"level": 0}

            # Calculate offline progress
            if save_data.get("timestamp"):
                offline_time = min(
                    (pygame.time.get_ticks() - save_data["timestamp"]) / 1000, 86400
                )  # Cap at 24 hours
                offline_production = (
                    self.state.get_production_rate() * offline_time * 0.75
                )  # 75% efficiency

                if offline_production > 0:
                    self.state.bits += offline_production
                    self.state.total_bits_earned += offline_production
                    print(
                        f"Offline progress: {self.format_number(offline_production)} bits"
                    )

        except Exception as e:
            print(f"Failed to load game: {e}")

    def draw_panel_toggle(self, button, is_open):
        """Draw panel toggle button with clear visual affordances"""
        # Much more prominent visual states
        if is_open:
            bg_color = (60, 70, 95)
            border_color = COLORS["electric_cyan"]
            text_color = COLORS["soft_white"]
            glow_intensity = 60
        else:
            bg_color = (35, 40, 55)
            border_color = (80, 90, 120)
            text_color = (160, 170, 200)

        # Background with subtle gradient effect via layered rects
        pygame.draw.rect(self.screen, bg_color, button.rect, border_radius=8)
        
        # Inner highlight for depth
        highlight_rect = button.rect.inflate(-4, -4)
        pygame.draw.rect(self.screen, (*bg_color, 30), highlight_rect, 1, border_radius=6)

        # Strong glow effect for open state, subtle for closed
        glow_intensity = 60 if is_open else 20
        if is_open:
            for i in range(3):
                glow_rect = button.rect.inflate(6 + i * 3, 6 + i * 3)
                glow_alpha = glow_intensity - i * 15
                glow_surf = pygame.Surface(
                    (glow_rect.width, glow_rect.height), pygame.SRCALPHA
                )
                pygame.draw.rect(
                    glow_surf,
                    (*border_color, glow_alpha),
                    (0, 0, glow_rect.width, glow_rect.height),
                    border_radius=10 + i * 2,
                )
                self.screen.blit(glow_surf, glow_rect.topleft)

        # Main border - thicker for better visibility
        pygame.draw.rect(self.screen, border_color, button.rect, 3, border_radius=8)

        # Add chevron/arrow indicator
        arrow_x = button.rect.x + 15
        arrow_y = button.rect.centery
        arrow_color = text_color
        arrow_size = 6
        
        if is_open:
            # Down arrow (▼)
            pygame.draw.polygon(
                self.screen, arrow_color,
                [(arrow_x, arrow_y - arrow_size),
                 (arrow_x + arrow_size * 1.5, arrow_y + arrow_size),
                 (arrow_x - arrow_size * 1.5, arrow_y + arrow_size)]
            )
        else:
            # Right arrow (▶)
            pygame.draw.polygon(
                self.screen, arrow_color,
                [(arrow_x - arrow_size, arrow_y - arrow_size * 1.5),
                 (arrow_x + arrow_size, arrow_y),
                 (arrow_x - arrow_size, arrow_y + arrow_size * 1.5)]
            )

        # Text - offset to account for arrow
        text_surface = self.small_font.render(button.text, True, text_color)
        text_rect = text_surface.get_rect(
            center=(button.rect.centerx + 10, button.rect.centery)
        )
        self.screen.blit(text_surface, text_rect)

    def draw_panel_with_integrated_title(self, panel, title_color=None):
        """Draw a panel with integrated title bar - enhanced visibility"""
        if title_color is None:
            title_color = COLORS["electric_cyan"]

        # Main panel background - darker for better contrast with content
        pygame.draw.rect(self.screen, (18, 22, 32), panel.rect, border_radius=12)

        # Outer border - more visible
        pygame.draw.rect(
            self.screen, (*title_color, 80), panel.rect, 2, border_radius=12
        )

        # Inner subtle border for depth
        inner_rect = panel.rect.inflate(-3, -3)
        pygame.draw.rect(
            self.screen, (40, 45, 60), inner_rect, 1, border_radius=10
        )

        # Title bar with gradient-like effect (layered rects)
        title_bar_height = 48
        title_rect = pygame.Rect(
            panel.rect.x, panel.rect.y, panel.rect.width, title_bar_height
        )
        
        # Title bar background
        pygame.draw.rect(
            self.screen,
            (30, 35, 50),
            title_rect,
            border_top_left_radius=12,
            border_top_right_radius=12,
        )
        
        # Title bar highlight line
        pygame.draw.line(
            self.screen,
            (*title_color, 40),
            (panel.rect.x + 1, panel.rect.y + title_bar_height - 1),
            (panel.rect.x + panel.rect.width - 1, panel.rect.y + title_bar_height - 1),
            1,
        )

        # Title text - larger and more prominent
        title_surface = self.medium_font.render(panel.title, True, title_color)
        title_text_rect = title_surface.get_rect(
            center=(panel.rect.centerx, panel.rect.y + title_bar_height // 2)
        )
        
        # Subtle text shadow for better readability
        shadow_surface = self.medium_font.render(panel.title, True, (0, 0, 0))
        shadow_rect = title_text_rect.copy()
        shadow_rect.x += 1
        shadow_rect.y += 1
        self.screen.blit(shadow_surface, shadow_rect)
        
        self.screen.blit(title_surface, title_text_rect)

        # Icon count indicator in title bar
        content_height = panel.content_height if hasattr(panel, 'content_height') else 0
        view_height = panel.rect.height - title_bar_height
        if content_height > view_height:
            scroll_pct = view_height / content_height
            scroll_text = f"{int(scroll_pct * 100)}% visible"
        else:
            scroll_text = "All visible"
        
        scroll_surface = self.tiny_font.render(scroll_text, True, (*title_color, 120))
        scroll_rect = scroll_surface.get_rect(
            right=panel.rect.right - 15, centery=panel.rect.y + title_bar_height // 2
        )
        self.screen.blit(scroll_surface, scroll_rect)

        # Separator line under title - more prominent
        pygame.draw.line(
            self.screen,
            title_color,
            (panel.rect.x + 15, panel.rect.y + title_bar_height),
            (panel.rect.x + panel.rect.width - 15, panel.rect.y + title_bar_height),
            3,
        )

    def draw_panel_background(self, panel):
        """Legacy method - use draw_panel_with_integrated_title instead"""
        self.draw_panel_with_integrated_title(panel)

    def draw_scrollbar(self, panel):
        """Draw scrollbar for panel - enhanced visibility"""
        if panel.content_height <= panel.rect.height - 60:
            return

        scrollbar_x = panel.rect.right - 14
        scrollbar_y = panel.rect.y + 50
        scrollbar_height = panel.rect.height - 60
        scrollbar_width = 10

        # Track with gradient effect
        track_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(self.screen, (30, 35, 48), track_rect, border_radius=5)
        
        # Track inner border
        pygame.draw.rect(self.screen, (50, 55, 70), track_rect, 1, border_radius=5)

        # Thumb
        thumb_height = max(
            40, int((scrollbar_height * scrollbar_height) / panel.content_height)
        )
        scroll_range = max(1, panel.content_height - scrollbar_height)
        thumb_y = (
            scrollbar_y
            + int((panel.scroll_offset * (scrollbar_height - thumb_height)) / scroll_range)
        )
        thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
        
        # Thumb with glow effect
        pygame.draw.rect(self.screen, (45, 50, 65), thumb_rect.inflate(4, 4), border_radius=6)
        pygame.draw.rect(self.screen, COLORS["electric_cyan"], thumb_rect, border_radius=5)

        # Navigation arrows
        arrow_color = (80, 90, 110)
        
        # Up arrow
        pygame.draw.polygon(
            self.screen, arrow_color,
            [(scrollbar_x + scrollbar_width // 2, scrollbar_y - 5),
             (scrollbar_x + 3, scrollbar_y + 8),
             (scrollbar_x + scrollbar_width - 3, scrollbar_y + 8)]
        )
        
        # Down arrow
        pygame.draw.polygon(
            self.screen, arrow_color,
            [(scrollbar_x + scrollbar_width // 2, scrollbar_y + scrollbar_height + 5),
             (scrollbar_x + 3, scrollbar_y + scrollbar_height - 8),
             (scrollbar_x + scrollbar_width - 3, scrollbar_y + scrollbar_height - 8)]
        )

    def draw_generator_card(
        self,
        surface,
        x,
        y,
        width,
        height,
        generator,
        gen_id,
        count,
        cost,
        production,
        can_afford,
    ):
        """Draw individual generator card with enhanced visibility and clarity"""
        card_rect = pygame.Rect(x, y, width, height)

        # Check if this is a locked generator (not unlocked yet)
        is_locked = False
        if gen_id in CONFIG["GENERATORS"]:
            if not self.state.is_generator_unlocked(gen_id):
                is_locked = True
        elif gen_id in CONFIG.get("HARDWARE_GENERATORS", {}):
            generator_cfg = CONFIG["HARDWARE_GENERATORS"][gen_id]
            if not self.state.is_hardware_category_unlocked(generator_cfg.get("category", "")):
                is_locked = True

        # Much clearer visual states - gray out locked items
        if is_locked:
            bg_color = (20, 22, 28)
            border_color = (45, 50, 65)
            border_width = 1
            cost_color = (60, 65, 80)
            name_color = (80, 85, 100)
            info_color = (55, 60, 75)
            is_gray = True
        elif can_afford:
            bg_color = (35, 42, 58)
            border_color = COLORS["electric_cyan"]
            border_width = 3
            cost_color = COLORS["matrix_green"]
            name_color = COLORS["soft_white"]
            info_color = (180, 190, 220)
            is_gray = False
        else:
            bg_color = (25, 27, 35)
            border_color = (60, 70, 90)
            border_width = 1
            cost_color = (90, 100, 120)
            name_color = (140, 150, 170)
            info_color = (80, 90, 110)
            is_gray = False

        # Draw card background
        pygame.draw.rect(surface, bg_color, card_rect, border_radius=10)

        # Strong glow for affordable cards
        if can_afford:
            for i in range(3):
                glow_rect = card_rect.inflate(i * 4, i * 4)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(
                    glow_surf,
                    (*border_color, 25 - i * 5),
                    (0, 0, glow_rect.width, glow_rect.height),
                    border_radius=12 + i * 2,
                )
                surface.blit(glow_surf, glow_rect.topleft)

        # Main border - thicker for affordables
        pygame.draw.rect(surface, border_color, card_rect, border_width, border_radius=10)

        # Left accent bar - more prominent
        accent_rect = pygame.Rect(x, y, 5, height)
        pygame.draw.rect(surface, border_color, accent_rect)

        # Icon with circle background
        icon_size = 42
        icon_x = x + 20
        icon_y = y + height // 2 - icon_size // 2
        
        # Icon background circle - grayed out for locked
        if is_locked:
            icon_bg_color = (35, 38, 48)
            icon_fg_color = (70, 75, 90)
        elif can_afford:
            icon_bg_color = (*border_color, 40)
            icon_fg_color = border_color
        else:
            icon_bg_color = (40, 45, 55)
            icon_fg_color = (90, 100, 120)
        pygame.draw.circle(surface, icon_bg_color, (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2 + 2)
        
        icon_text = generator.get("icon", "🎲")
        try:
            icon_font = pygame.font.Font(None, 52)
            icon_surface = icon_font.render(icon_text, True, icon_fg_color)
            surface.blit(icon_surface, (icon_x + 2, icon_y))
        except (pygame.error, UnicodeEncodeError):
            pygame.draw.circle(
                surface,
                icon_fg_color,
                (icon_x + icon_size // 2, icon_y + icon_size // 2),
                18,
            )

        # Text area - clearer layout
        text_x = x + 75
        
        # Name - larger, clearer font
        name_text = self.medium_font.render(generator["name"], True, name_color)
        surface.blit(name_text, (text_x, y + 8))

        # Quantity and production - larger text
        if production > 0:
            qty_prod_text = self.small_font.render(
                f"Owned: {count}  •  Production: {self.format_number(production)} b/s",
                True, info_color
            )
        else:
            qty_prod_text = self.small_font.render(
                f"Owned: {count}", True, info_color
            )
        surface.blit(qty_prod_text, (text_x, y + 32))

        # Cost - right side, very prominent
        cost_label = self.tiny_font.render("COST:", True, cost_color)
        surface.blit(cost_label, (x + width - 155, y + 12))
        
        cost_value = self.small_font.render(self.format_number(cost), True, cost_color)
        surface.blit(cost_value, (x + width - 155, y + 26))

        # Buy indicator - subtle for locked, prominent for affordable
        if is_locked:
            # Show unlock requirement instead of LOCKED
            unlock_threshold = generator.get("unlock_threshold", 0)
            if unlock_threshold > 0:
                req_text = f"Unlock: {self.format_number(unlock_threshold)} bits"
                buy_text = self.small_font.render(req_text, True, (60, 65, 80))
                surface.blit(buy_text, (x + width - 130, y + height // 2 - 10))
            else:
                # For hardware generators, show category requirement
                category = generator.get("category", "")
                if category:
                    buy_text = self.small_font.render(f"Requires: {category.upper()}", True, (60, 65, 80))
                    surface.blit(buy_text, (x + width - 130, y + height // 2 - 10))
        elif can_afford:
            buy_text = self.small_font.render("[BUY]", True, COLORS["matrix_green"])
            surface.blit(buy_text, (x + width - 75, y + height // 2 - 10))
        else:
            buy_text = self.small_font.render("[LOCKED]", True, (80, 85, 95))
            surface.blit(buy_text, (x + width - 85, y + height // 2 - 10))

        # Bottom Y for button alignment
        bottom_y = y + height - 25

        # Buy buttons (optimized for compact layout) - hide for locked generators
        btn_width = 60  # Reduced from 70
        btn_height = 22  # Reduced from 28
        btn_spacing = 4
        if is_locked:
            btn_color = (25, 28, 35)
            btn_border = (45, 50, 60)
            btn_text_color = (60, 65, 80)
        elif can_afford:
            btn_color = (45, 55, 70)
            btn_border = COLORS["electric_cyan"]
            btn_text_color = COLORS["soft_white"]
        else:
            btn_color = (30, 33, 40)
            btn_border = COLORS["muted_blue"]
            btn_text_color = COLORS["muted_blue"]

        # BUY x10 button (left) - hide buttons for locked generators
        if not is_locked:
            btn1_rect = pygame.Rect(
                x + width - btn_width * 2 - btn_spacing * 2, bottom_y, btn_width, btn_height
            )
            pygame.draw.rect(
                surface,
                btn_color,
                btn1_rect,
                border_radius=3,
            )
            pygame.draw.rect(
                surface,
                btn_border,
                btn1_rect,
                1,
                border_radius=3,
            )
            btn1_text = self.tiny_font.render(
                "BUY x10",
                True,
                btn_text_color,
            )
            btn1_text_rect = btn1_text.get_rect(center=btn1_rect.center)
            surface.blit(btn1_text, btn1_text_rect)

            # BUY x1 button (right)
            btn2_rect = pygame.Rect(
                x + width - btn_width - btn_spacing, bottom_y, btn_width, btn_height
            )
            pygame.draw.rect(
                surface,
                btn_color,
                btn2_rect,
                border_radius=3,
            )
            pygame.draw.rect(
                surface,
                btn_border,
                btn2_rect,
                1,
                border_radius=3,
            )
            btn2_text = self.tiny_font.render(
                "BUY x1",
                True,
                btn_text_color,
            )
            btn2_text_rect = btn2_text.get_rect(center=btn2_rect.center)
            surface.blit(btn2_text, btn2_text_rect)

    def draw_upgrade_card(
        self, surface, x, y, width, height, upgrade, upgrade_id, level, cost, can_afford
    ):
        """Draw individual upgrade card with enhanced visibility"""
        card_rect = pygame.Rect(x, y, width, height)

        # Enhanced purple theme for upgrades - clearer states
        max_level = upgrade["max_level"]
        is_maxed = level >= max_level

        if is_maxed:
            bg_color = (40, 35, 55)
            border_color = COLORS["gold"]
            border_width = 3
            name_color = COLORS["gold"]
            info_color = (255, 215, 100)
            cost_color = COLORS["gold"]
        elif can_afford:
            bg_color = (38, 35, 55)
            border_color = COLORS["neon_purple"]
            border_width = 3
            name_color = COLORS["soft_white"]
            info_color = (180, 160, 220)
            cost_color = COLORS["matrix_green"]
        else:
            bg_color = (25, 27, 38)
            border_color = (70, 60, 100)
            border_width = 1
            name_color = (130, 120, 160)
            info_color = (80, 70, 100)
            cost_color = (90, 80, 110)

        # Background
        pygame.draw.rect(surface, bg_color, card_rect, border_radius=10)

        # Strong glow for affordable or maxed cards
        if can_afford or is_maxed:
            for i in range(3):
                glow_rect = card_rect.inflate(i * 4, i * 4)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(
                    glow_surf,
                    (*border_color, 25 - i * 5),
                    (0, 0, glow_rect.width, glow_rect.height),
                    border_radius=12 + i * 2,
                )
                surface.blit(glow_surf, glow_rect.topleft)

        # Main border
        pygame.draw.rect(surface, border_color, card_rect, border_width, border_radius=10)

        # Left accent bar
        pygame.draw.rect(surface, border_color, (x, y, 5, height))

        # Icon with background
        icon_size = 42
        icon_x = x + 20
        icon_y = y + height // 2 - icon_size // 2
        
        icon_bg = (*border_color, 40) if (can_afford or is_maxed) else (40, 45, 60)
        pygame.draw.circle(surface, icon_bg, (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2 + 2)
        
        icon_text = upgrade.get("icon", "⚡")
        try:
            icon_font = pygame.font.Font(None, 52)
            icon_surface = icon_font.render(icon_text, True, border_color if (can_afford or is_maxed) else (90, 80, 110))
            surface.blit(icon_surface, (icon_x + 2, icon_y))
        except (pygame.error, UnicodeEncodeError):
            pygame.draw.circle(surface, border_color, (icon_x + icon_size // 2, icon_y + icon_size // 2), 18)

        # Text area
        text_x = x + 75
        
        # Name - clearer
        name_text = self.medium_font.render(upgrade["name"], True, name_color)
        surface.blit(name_text, (text_x, y + 8))

        # Level indicator - more prominent
        level_color = COLORS["gold"] if is_maxed else COLORS["neon_purple"]
        level_text = self.small_font.render(
            f"Level {level} / {max_level}", True, level_color
        )
        surface.blit(level_text, (text_x, y + 32))

        # Effect description
        effect_text = upgrade.get("description", "Increases production")
        desc_text = self.small_font.render(effect_text, True, info_color)
        surface.blit(desc_text, (text_x, y + 50))

        # Right side - level progress bar
        bar_x = x + width - 130
        bar_y = y + 15
        bar_w = 110
        bar_h = 8
        
        # Progress bar background
        pygame.draw.rect(surface, (30, 25, 45), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        # Progress fill
        progress = level / max_level if max_level > 0 else 0
        pygame.draw.rect(surface, border_color, (bar_x, bar_y, bar_w * progress, bar_h), border_radius=4)
        # Border
        pygame.draw.rect(surface, (*border_color, 80), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

        # Cost or MAXED indicator
        if is_maxed:
            maxed_text = self.medium_font.render("★ MAXED", True, COLORS["gold"])
            surface.blit(maxed_text, (x + width - 120, y + height // 2 - 10))
        else:
            # Cost
            cost_label = self.tiny_font.render("COST:", True, cost_color)
            surface.blit(cost_label, (x + width - 125, y + 35))
            
            cost_value = self.small_font.render(self.format_number(cost), True, cost_color)
            surface.blit(cost_value, (x + width - 125, y + 48))

            # UPGRADE button - draw as actual button
            btn_x = x + width - 80
            btn_y = y + height - 25
            btn_w = 70
            btn_h = 20
            
            if can_afford:
                btn_color = (45, 55, 70)
                btn_border = COLORS["matrix_green"]
                btn_text_col = COLORS["matrix_green"]
            else:
                btn_color = (30, 33, 40)
                btn_border = (60, 65, 80)
                btn_text_col = (60, 65, 80)
            
            pygame.draw.rect(surface, btn_color, (btn_x, btn_y, btn_w, btn_h), border_radius=3)
            pygame.draw.rect(surface, btn_border, (btn_x, btn_y, btn_w, btn_h), 1, border_radius=3)
            
            btn_text = self.small_font.render("UPGRADE", True, btn_text_col)
            btn_text_rect = btn_text.get_rect(center=(btn_x + btn_w // 2, btn_y + btn_h // 2))
            surface.blit(btn_text, btn_text_rect)

    def draw_hardware_panel(self):
        """Draw hardware/information sources panel - alias for draw_generators_panel"""
        self.draw_generators_panel()
        
    def draw_generators_panel(self):
        """Draw generators panel with better design and scrolling"""
        # Update toggle button text based on state
        if self.hardware_panel_open:
            self.hardware_toggle.text = "▼ HARDWARE"
        else:
            self.hardware_toggle.text = "▸ HARDWARE"

        # Draw toggle button with better styling
        self.draw_panel_toggle(self.hardware_toggle, self.hardware_panel_open)

        if not self.hardware_panel_open:
            return

        # Draw scrollable panel background with integrated title
        panel = self.hardware_scroll_panel
        self.draw_panel_with_integrated_title(panel, COLORS["electric_cyan"])

        # Create a subsurface for scrollable content
        scroll_surface = pygame.Surface((panel.rect.width - 20, panel.rect.height - 60))
        scroll_surface.fill((18, 20, 28))

        # Draw generators on scroll surface
        y_offset = -panel.get_scroll_offset()

        all_generators = get_all_generators()
        basic_generators = GENERATORS if GENERATORS else CONFIG["GENERATORS"]
        hardware_generators = CONFIG.get("HARDWARE_GENERATORS", {})

        for gen_id, generator in all_generators.items():
            # Check if unlocked
            if gen_id in basic_generators:
                if not self.state.is_generator_unlocked(gen_id):
                    continue
            elif gen_id in hardware_generators:
                if not self.state.is_hardware_category_unlocked(generator["category"]):
                    continue

            count = self.state.generators[gen_id]["count"]
            cost = self.state.get_generator_cost(gen_id)
            # Calculate production for individual generator
            if gen_id in CONFIG["GENERATORS"]:
                generator = CONFIG["GENERATORS"][gen_id]
                production = count * generator["base_production"]
            elif gen_id in CONFIG.get("HARDWARE_GENERATORS", {}):
                generator = CONFIG["HARDWARE_GENERATORS"][gen_id]
                category = generator["category"]
                if self.state.is_hardware_category_unlocked(category):
                    category_multiplier = self.state.get_category_multiplier(category)
                    production = (
                        count * generator["base_production"] * category_multiplier
                    )
                else:
                    production = 0
            else:
                production = 0
            can_afford = self.state.can_afford(cost)

            # Card dimensions - larger for enhanced design
            card_height = 90  # Increased for better visibility
            card_y = y_offset + 8  # Reduced from 10

            # Only draw if visible (optimization)
            if card_y + card_height > -20 and card_y < scroll_surface.get_height():
                self.draw_generator_card(
                    scroll_surface,
                    10,
                    card_y,
                    panel.rect.width - 40,
                    card_height,
                    generator,
                    gen_id,
                    count,
                    cost,
                    production,
                    can_afford,
                )

            y_offset += card_height + 14  # Generous spacing from 12

        # Update content height for scrolling
        panel.set_content_height(y_offset + panel.get_scroll_offset() + 20)

        # Blit scroll surface to screen
        self.screen.blit(scroll_surface, (panel.rect.x + 10, panel.rect.y + 50))

        # Draw scrollbar if needed
        if panel.content_height > panel.rect.height - 60:
            self.draw_scrollbar(panel)

    def draw_upgrades_panel(self):
        """Draw upgrades panel with better design and scrolling"""
        # Update toggle button text
        if self.upgrades_panel_open:
            self.upgrades_toggle.text = "▼ UPGRADES"
        else:
            self.upgrades_toggle.text = "▶ UPGRADES"

        # Draw toggle button
        self.draw_panel_toggle(self.upgrades_toggle, self.upgrades_panel_open)

        if not self.upgrades_panel_open:
            return

        # Draw scrollable panel with integrated title
        panel = self.upgrades_scroll_panel
        self.draw_panel_with_integrated_title(panel, COLORS["neon_purple"])

        # Create scroll surface
        scroll_surface = pygame.Surface((panel.rect.width - 20, panel.rect.height - 60))
        scroll_surface.fill((18, 20, 28))

        y_offset = -panel.get_scroll_offset()

        all_upgrades = get_all_upgrades()
        basic_upgrades = UPGRADES if UPGRADES else CONFIG["UPGRADES"]
        hardware_upgrades = CONFIG.get("HARDWARE_UPGRADES", {})

        for upgrade_id, upgrade in all_upgrades.items():
            # Check if unlocked
            if upgrade_id in basic_upgrades:
                if not self.state.is_upgrade_unlocked(upgrade_id):
                    continue
            elif upgrade_id in hardware_upgrades:
                if not self.state.is_hardware_category_unlocked(upgrade["category"]):
                    continue

            level = self.state.upgrades[upgrade_id]["level"]
            cost = self.state.get_upgrade_cost(upgrade_id)
            can_afford = self.state.can_afford(cost) and level < upgrade["max_level"]

            # Card - larger for enhanced design
            card_height = 85  # Increased for better visibility
            card_y = y_offset + 8  # Reduced from 10

            if card_y + card_height > -20 and card_y < scroll_surface.get_height():
                self.draw_upgrade_card(
                    scroll_surface,
                    10,
                    card_y,
                    panel.rect.width - 40,
                    card_height,
                    upgrade,
                    upgrade_id,
                    level,
                    cost,
                    can_afford,
                )

            y_offset += card_height + 14  # Generous spacing from 12

        panel.set_content_height(y_offset + panel.get_scroll_offset() + 20)

        # Blit to screen
        self.screen.blit(scroll_surface, (panel.rect.x + 10, panel.rect.y + 50))

        # Scrollbar if needed
        if panel.content_height > panel.rect.height - 60:
            self.draw_scrollbar(panel)

        # Draw component upgrade buttons
        for comp_name, button in self.component_upgrade_buttons.items():
            comp = self.bit_grid.components[comp_name]

            if comp["unlocked"]:
                cost_multiplier = 2.5 ** comp["level"]
                cost = int(COMPONENT_BASE_COSTS.get(comp_name, 100) * cost_multiplier)
                can_afford = self.state.can_afford(cost) and comp["level"] < 10

                # Update button state
                button.is_enabled = can_afford

                # Draw button
                button.draw(self.screen)

                # Draw cost text on button
                cost_text = self.tiny_font.render(
                    self.format_number(cost), True, (255, 255, 255)
                )
                text_rect = cost_text.get_rect(center=button.rect.center)
                self.screen.blit(cost_text, text_rect)
            else:
                # Draw locked button
                button.is_enabled = False
                button.draw(self.screen)

    def draw_rebirth_bar(self):
        # Background with elevation shadow
        bar_rect = pygame.Rect(
            0,
            self.current_height - int(80 * (self.current_height / self.base_height)),
            self.current_width,
            int(80 * (self.current_height / self.base_height)),
        )

        # Shadow effect
        shadow_rect = pygame.Rect(
            2,
            self.current_height - int(78 * (self.current_height / self.base_height)),
            self.current_width - 4,
            int(76 * (self.current_height / self.base_height)),
        )
        pygame.draw.rect(self.screen, (0, 0, 0, 50), shadow_rect)

        # Main background
        pygame.draw.rect(self.screen, COLORS["deep_space_blue"], bar_rect)

        # Top border with glow
        pygame.draw.line(
            self.screen,
            COLORS["neon_purple"],
            (
                0,
                self.current_height
                - int(80 * (self.current_height / self.base_height)),
            ),
            (
                self.current_width,
                self.current_height
                - int(80 * (self.current_height / self.base_height)),
            ),
            2,
        )
        # Add glow effect
        for i in range(1, 4):
            alpha = 50 - i * 15
            glow_color = (*COLORS["neon_purple"][:3], alpha)
            pygame.draw.line(
                self.screen,
                glow_color[:3],
                (
                    0,
                    self.current_height
                    - int(80 * (self.current_height / self.base_height))
                    + i,
                ),
                (
                    self.current_width,
                    self.current_height
                    - int(80 * (self.current_height / self.base_height))
                    + i,
                ),
                1,
            )

        # Hardware generation info
        from constants import HARDWARE_GENERATIONS

        current_gen, next_gen = self.state.get_hardware_generation_info()
        rebirth_threshold = self.state.get_rebirth_threshold()

        # Rebirth progress based on era completion percentage
        era_completion = self.bit_grid.get_era_completion_percentage() / 100
        progress = min(era_completion, 1.0)  # Cap at 100%
        tokens = self.state.get_estimated_rebirth_tokens()
        current_mb = self.format_number(self.state.total_bits_earned / (1024 * 1024))
        target_mb = self.format_number(rebirth_threshold / (1024 * 1024))
        era_completion_text = (
            f"Era Completion: {self.bit_grid.get_era_completion_percentage():.1f}%"
        )

        # Progress bar with shimmer effect
        scale_x = self.current_width / self.base_width
        scale_y = self.current_height / self.base_height
        progress_bg = pygame.Rect(
            int(200 * scale_x),
            self.current_height - int(50 * scale_y),
            int(800 * scale_x),
            int(20 * scale_y),
        )
        progress_fill = pygame.Rect(
            int(200 * scale_x),
            self.current_height - int(50 * scale_y),
            int(800 * scale_x * progress),
            int(20 * scale_y),
        )

        pygame.draw.rect(
            self.screen,
            COLORS["deep_space_gradient_end"],
            progress_bg,
            border_radius=10,
        )

        # Animated gradient fill
        if progress > 0:
            for i in range(progress_fill.width):
                gradient_ratio = i / progress_fill.width
                fill_color = (
                    int(
                        COLORS["electric_cyan"][0]
                        + (COLORS["neon_purple"][0] - COLORS["electric_cyan"][0])
                        * gradient_ratio
                    ),
                    int(
                        COLORS["electric_cyan"][1]
                        + (COLORS["neon_purple"][1] - COLORS["electric_cyan"][1])
                        * gradient_ratio
                    ),
                    int(
                        COLORS["electric_cyan"][2]
                        + (COLORS["neon_purple"][2] - COLORS["electric_cyan"][2])
                        * gradient_ratio
                    ),
                )
                pygame.draw.line(
                    self.screen,
                    fill_color,
                    (progress_fill.left + i, progress_fill.top),
                    (progress_fill.left + i, progress_fill.bottom),
                )

        # Shimmer effect (traveling highlight)
        if progress_fill.width > 0:
            shimmer_offset = (pygame.time.get_ticks() // 20) % (
                progress_fill.width + 40
            )
            shimmer_rect = pygame.Rect(
                progress_fill.left + shimmer_offset - 20,
                progress_fill.top,
                40,
                progress_fill.height,
            )
            if (
                shimmer_rect.left >= progress_fill.left
                and shimmer_rect.right <= progress_fill.right
            ):
                shimmer_surface = pygame.Surface(
                    (shimmer_rect.width, shimmer_rect.height)
                )
                shimmer_surface.set_alpha(100)
                shimmer_surface.fill((255, 255, 255))
                self.screen.blit(shimmer_surface, shimmer_rect)

        # Show rebirth button if available (100% era completion)
        if progress >= 1.0 and self.state.can_rebirth(self.bit_grid):
            # Update and draw rebirth button
            if next_gen:
                self.rebirth_button.text = (
                    f"🚀 UPGRADE TO {next_gen['name'].split()[0]}!"
                )
            else:
                self.rebirth_button.text = f"🌀 COMPRESS FOR {tokens} ⭐"
            self.rebirth_button.draw(self.screen)
        else:
            pass  # Generation info shown in progress text below

        progress_text = self.monospace_font.render(
            f"{era_completion_text} | ({current_mb} MB / {target_mb} MB)",
            True,
            COLORS["soft_white"],
        )
        progress_rect = progress_text.get_rect(
            center=(self.current_width // 2, self.current_height - int(38 * scale_y))
        )
        self.screen.blit(progress_text, progress_rect)

    def draw_effects(self):
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)

        # Draw floating texts
        for text in self.floating_texts:
            text.draw(self.screen)

    def draw_crt_overlay(self):
        # Draw scanlines
        for y in range(0, self.current_height, 4):
            pygame.draw.line(
                self.screen, (0, 0, 0, 20), (0, y), (self.current_width, y)
            )

    def draw_rebirth_confirmation(self):
        if self.showing_rebirth_confirmation:
            # Overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(COLORS["deep_space_blue"])
            self.screen.blit(overlay, (0, 0))

            # Confirmation box
            box_rect = pygame.Rect(
                WINDOW_WIDTH // 2 - 300, WINDOW_HEIGHT // 2 - 200, 600, 400
            )
            pygame.draw.rect(
                self.screen, COLORS["dim_gray"], box_rect, border_radius=16
            )
            pygame.draw.rect(self.screen, COLORS["gold"], box_rect, 3, border_radius=16)

            # Title
            title_text = self.large_font.render(
                "⚠️ COMPRESSION CYCLE ⚠️", True, COLORS["gold"]
            )
            title_rect = title_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 150)
            )
            self.screen.blit(title_text, title_rect)

            # Calculate what player will lose/gain
            tokens = self.state.get_estimated_rebirth_tokens()
            current_mb = self.format_number(
                self.state.total_bits_earned / (1024 * 1024)
            )
            from constants import HARDWARE_GENERATIONS

            current_gen, next_gen = self.state.get_hardware_generation_info()

            # Information text
            info_lines = [
                f"You will lose:",
                f"• All {current_mb} MB of data",
                f"• All generators",
                f"• All upgrades",
                "",
                f"You will gain:",
                f"• {tokens} Compression Tokens ⭐",
                f"• Access to Compression Era",
                f"• Permanent meta-progression",
            ]

            if next_gen:
                info_lines.extend(
                    [
                        "",
                        f"🚀 HARDWARE UPGRADE AVAILABLE:",
                        f"• Advance to {next_gen['name']}",
                        f"• Unlock {next_gen['primary_category'].upper()} category",
                    ]
                )

            y_offset = -50
            for line in info_lines:
                if line.startswith("•"):
                    text_color = COLORS["soft_white"]
                elif line == "":
                    y_offset -= 10
                    continue
                elif line.startswith("You will lose:"):
                    text_color = COLORS["signal_orange"]
                elif line.startswith("You will gain:"):
                    text_color = COLORS["matrix_green"]
                else:
                    text_color = COLORS["gold"]

                text_surface = self.small_font.render(line, True, text_color)
                text_rect = text_surface.get_rect(
                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + y_offset)
                )
                self.screen.blit(text_surface, text_rect)
                y_offset += 25

            # Buttons
            mouse_pos = pygame.mouse.get_pos()

            # Yes button
            yes_rect = pygame.Rect(
                WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 + 50, 100, 40
            )
            yes_color = (
                COLORS["matrix_green"]
                if yes_rect.collidepoint(mouse_pos)
                else COLORS["gold"]
            )
            pygame.draw.rect(self.screen, yes_color, yes_rect, border_radius=8)
            yes_text = self.medium_font.render(
                "COMPRESS! 🌀", True, COLORS["soft_white"]
            )
            yes_text_rect = yes_text.get_rect(center=yes_rect.center)
            self.screen.blit(yes_text, yes_text_rect)

            # No button
            no_rect = pygame.Rect(
                WINDOW_WIDTH // 2 + 20, WINDOW_HEIGHT // 2 + 50, 100, 40
            )
            no_color = (
                COLORS["signal_orange"]
                if no_rect.collidepoint(mouse_pos)
                else COLORS["dim_gray"]
            )
            pygame.draw.rect(self.screen, no_color, no_rect, border_radius=8)
            no_text = self.medium_font.render("CANCEL", True, COLORS["soft_white"])
            no_text_rect = no_text.get_rect(center=no_rect.center)
            self.screen.blit(no_text, no_text_rect)

    def draw_tutorial(self):
        if self.showing_tutorial and self.tutorial_text:
            # Overlay (responsive)
            overlay = pygame.Surface((self.current_width, self.current_height))
            overlay.set_alpha(200)
            overlay.fill(COLORS["deep_space_blue"])
            self.screen.blit(overlay, (0, 0))

            # Tutorial box (responsive)
            box_width = min(500, self.current_width - 100)
            box_height = min(300, self.current_height - 200)
            box_rect = pygame.Rect(
                self.current_width // 2 - box_width // 2,
                self.current_height // 2 - box_height // 2,
                box_width,
                box_height,
            )
            pygame.draw.rect(
                self.screen, COLORS["dim_gray"], box_rect, border_radius=16
            )
            pygame.draw.rect(
                self.screen, COLORS["electric_cyan"], box_rect, 3, border_radius=16
            )

            # Tutorial text
            lines = self.tutorial_text.split("\n")
            y_offset = 0
            for line in lines:
                text_surface = self.small_font.render(line, True, COLORS["soft_white"])
                text_rect = text_surface.get_rect(
                    center=(
                        self.current_width // 2,
                        self.current_height // 2 - 50 + y_offset,
                    )
                )
                self.screen.blit(text_surface, text_rect)
                y_offset += 30

            # Continue button (responsive - make it clickable)
            continue_button_rect = pygame.Rect(
                self.current_width // 2 - 100, self.current_height // 2 + 60, 200, 40
            )
            # Add hover effect for continue button
            mouse_pos = pygame.mouse.get_pos()
            if continue_button_rect.collidepoint(mouse_pos):
                button_color = COLORS["electric_cyan"]
                text_color = COLORS["soft_white"]
            else:
                button_color = COLORS["muted_blue"]
                text_color = COLORS["soft_white"]

            pygame.draw.rect(
                self.screen, button_color, continue_button_rect, border_radius=8
            )
            pygame.draw.rect(
                self.screen,
                COLORS["electric_cyan"],
                continue_button_rect,
                2,
                border_radius=8,
            )

            continue_text = self.medium_font.render(
                "CLICK TO CONTINUE", True, text_color
            )
            continue_text_rect = continue_text.get_rect(
                center=continue_button_rect.center
            )
            self.screen.blit(continue_text, continue_text_rect)

    def draw_settings_page(self):
        # Dark overlay
        overlay = pygame.Surface((self.current_width, self.current_height))
        overlay.set_alpha(230)
        overlay.fill(COLORS["deep_space_blue"])
        self.screen.blit(overlay, (0, 0))

        # Settings box
        scale_x = self.current_width / self.base_width
        scale_y = self.current_height / self.base_height
        settings_rect = pygame.Rect(
            self.current_width // 2 - int(300 * scale_x),
            int(150 * scale_y),
            int(600 * scale_x),
            int(400 * scale_y),
        )
        pygame.draw.rect(
            self.screen, COLORS["dim_gray"], settings_rect, border_radius=16
        )
        pygame.draw.rect(
            self.screen, COLORS["electric_cyan"], settings_rect, 3, border_radius=16
        )

        # Title
        title_text = self.large_font.render("⚙️ SETTINGS", True, COLORS["electric_cyan"])
        title_rect = title_text.get_rect(
            center=(self.current_width // 2, int(200 * scale_y))
        )
        self.screen.blit(title_text, title_rect)

        # Visual settings section
        section_text = self.medium_font.render(
            "VISUAL EFFECTS", True, COLORS["neon_purple"]
        )
        section_rect = section_text.get_rect(
            center=(self.current_width // 2, int(240 * scale_y))
        )
        self.screen.blit(section_text, section_rect)

        mouse_pos = pygame.mouse.get_pos()

        # CRT Effects toggle
        crt_rect = pygame.Rect(
            self.current_width // 2 - int(200 * scale_x),
            int(250 * scale_y),
            int(400 * scale_x),
            int(40 * scale_y),
        )
        crt_color = (
            COLORS["electric_cyan"]
            if self.state.visual_settings["crt_effects"]
            else COLORS["muted_blue"]
        )
        pygame.draw.rect(self.screen, crt_color, crt_rect, 2, border_radius=8)
        crt_text = self.small_font.render(
            f"📺 CRT Effects: {'ON' if self.state.visual_settings['crt_effects'] else 'OFF'}",
            True,
            COLORS["soft_white"],
        )
        crt_text_rect = crt_text.get_rect(center=crt_rect.center)
        self.screen.blit(crt_text, crt_text_rect)

        # Binary Rain toggle
        rain_rect = pygame.Rect(
            self.current_width // 2 - int(200 * scale_x),
            int(300 * scale_y),
            int(400 * scale_x),
            int(40 * scale_y),
        )
        rain_color = (
            COLORS["electric_cyan"]
            if self.state.visual_settings["binary_rain"]
            else COLORS["muted_blue"]
        )
        pygame.draw.rect(self.screen, rain_color, rain_rect, 2, border_radius=8)
        rain_text = self.small_font.render(
            f"🌧️ Binary Rain: {'ON' if self.state.visual_settings['binary_rain'] else 'OFF'}",
            True,
            COLORS["soft_white"],
        )
        rain_text_rect = rain_text.get_rect(center=rain_rect.center)
        self.screen.blit(rain_text, rain_text_rect)

        # Particle Effects toggle
        particle_rect = pygame.Rect(
            self.current_width // 2 - int(200 * scale_x),
            int(350 * scale_y),
            int(400 * scale_x),
            int(40 * scale_y),
        )
        particle_color = (
            COLORS["electric_cyan"]
            if self.state.visual_settings["particle_effects"]
            else COLORS["muted_blue"]
        )
        pygame.draw.rect(self.screen, particle_color, particle_rect, 2, border_radius=8)
        particle_text = self.small_font.render(
            f"✨ Particle Effects: {'ON' if self.state.visual_settings['particle_effects'] else 'OFF'}",
            True,
            COLORS["soft_white"],
        )
        particle_text_rect = particle_text.get_rect(center=particle_rect.center)
        self.screen.blit(particle_text, particle_text_rect)

        # Accessibility section
        access_section_text = self.medium_font.render(
            "ACCESSIBILITY", True, COLORS["neon_purple"]
        )
        access_section_rect = access_section_text.get_rect(
            center=(self.current_width // 2, int(400 * scale_y))
        )
        self.screen.blit(access_section_text, access_section_rect)

        # High Contrast toggle
        contrast_rect = pygame.Rect(
            self.current_width // 2 - int(200 * scale_x),
            int(430 * scale_y),
            int(400 * scale_x),
            int(40 * scale_y),
        )
        contrast_color = (
            COLORS["electric_cyan"] if self.high_contrast_mode else COLORS["muted_blue"]
        )
        pygame.draw.rect(self.screen, contrast_color, contrast_rect, 2, border_radius=8)
        contrast_text = self.small_font.render(
            f"👁️ High Contrast: {'ON' if self.high_contrast_mode else 'OFF'}",
            True,
            COLORS["soft_white"],
        )
        contrast_text_rect = contrast_text.get_rect(center=contrast_rect.center)
        self.screen.blit(contrast_text, contrast_text_rect)

        # Reduced Motion toggle
        motion_rect = pygame.Rect(
            self.current_width // 2 - int(200 * scale_x),
            int(480 * scale_y),
            int(400 * scale_x),
            int(40 * scale_y),
        )
        motion_color = (
            COLORS["electric_cyan"]
            if self.reduced_motion_mode
            else COLORS["muted_blue"]
        )
        pygame.draw.rect(self.screen, motion_color, motion_rect, 2, border_radius=8)
        motion_text = self.small_font.render(
            f"🎯 Reduced Motion: {'ON' if self.reduced_motion_mode else 'OFF'}",
            True,
            COLORS["soft_white"],
        )
        motion_text_rect = motion_text.get_rect(center=motion_rect.center)
        self.screen.blit(motion_text, motion_text_rect)

        # Quality Level toggle
        quality_rect = pygame.Rect(
            self.current_width // 2 - int(200 * scale_x),
            int(530 * scale_y),
            int(400 * scale_x),
            int(40 * scale_y),
        )
        quality_color = COLORS["electric_cyan"]
        pygame.draw.rect(self.screen, quality_color, quality_rect, 2, border_radius=8)
        quality_text = self.small_font.render(
            f"🎨 Visual Quality: {self.visual_quality.upper()}",
            True,
            COLORS["soft_white"],
        )
        quality_text_rect = quality_text.get_rect(center=quality_rect.center)
        self.screen.blit(quality_text, quality_text_rect)

        # Instructions
        inst_text = self.tiny_font.render(
            "Click any setting to toggle • Press ESC to close",
            True,
            COLORS["muted_blue"],
        )
        inst_rect = inst_text.get_rect(
            center=(self.current_width // 2, int(580 * scale_y))
        )
        self.screen.blit(inst_text, inst_rect)

        # Hover effects
        if crt_rect.collidepoint(mouse_pos):
            pygame.draw.rect(
                self.screen, COLORS["electric_cyan"], crt_rect, 3, border_radius=8
            )
        elif rain_rect.collidepoint(mouse_pos):
            pygame.draw.rect(
                self.screen, COLORS["electric_cyan"], rain_rect, 3, border_radius=8
            )
        elif particle_rect.collidepoint(mouse_pos):
            pygame.draw.rect(
                self.screen, COLORS["electric_cyan"], particle_rect, 3, border_radius=8
            )
        elif contrast_rect.collidepoint(mouse_pos):
            pygame.draw.rect(
                self.screen, COLORS["electric_cyan"], contrast_rect, 3, border_radius=8
            )
        elif motion_rect.collidepoint(mouse_pos):
            pygame.draw.rect(
                self.screen, COLORS["electric_cyan"], motion_rect, 3, border_radius=8
            )
        elif quality_rect.collidepoint(mouse_pos):
            pygame.draw.rect(
                self.screen, COLORS["electric_cyan"], quality_rect, 3, border_radius=8
            )

    def _get_gradient_surface(self):
        if (self._gradient_surface is None or 
            self._last_gradient_size != (self.current_width, self.current_height)):
            self._gradient_surface = pygame.Surface((self.current_width, self.current_height))
            for i in range(self.current_height):
                color_ratio = i / self.current_height
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
                pygame.draw.line(self._gradient_surface, color, (0, i), (self.current_width, i))
            self._last_gradient_size = (self.current_width, self.current_height)
        return self._gradient_surface

    def draw_tooltips(self):
        """Draw tooltips for hovered elements"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if hovering over generators in the hardware panel
        if self.hardware_panel_open:
            panel = self.hardware_scroll_panel
            all_generators = get_all_generators()
            y_offset = -panel.get_scroll_offset()

            for gen_id, generator in all_generators.items():
                basic_generators = GENERATORS if GENERATORS else CONFIG["GENERATORS"]
                hardware_generators = CONFIG.get("HARDWARE_GENERATORS", {})
                
                # Check if unlocked
                if gen_id in basic_generators:
                    if not self.state.is_generator_unlocked(gen_id):
                        continue
                elif gen_id in hardware_generators:
                    if not self.state.is_hardware_category_unlocked(generator.get("category", "")):
                        continue

                card_x = panel.rect.x + 10
                card_y = panel.rect.y + 50 + y_offset + 8
                card_width = panel.rect.width - 40
                card_height = 70

                card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                
                if card_rect.collidepoint(mouse_pos):
                    # Show tooltip with flavor text
                    flavor = generator.get("flavor", "")
                    if flavor:
                        self._draw_tooltip_box(mouse_pos, flavor)
                    return
                
                y_offset += card_height + 14

        # Check if hovering over upgrades in the upgrades panel
        if self.upgrades_panel_open:
            panel = self.upgrades_scroll_panel
            all_upgrades = get_all_upgrades()
            y_offset = -panel.get_scroll_offset()

            for upgrade_id, upgrade in all_upgrades.items():
                basic_upgrades = UPGRADES if UPGRADES else CONFIG["UPGRADES"]
                hardware_upgrades = CONFIG.get("HARDWARE_UPGRADES", {})
                
                if upgrade_id in basic_upgrades:
                    if not self.state.is_upgrade_unlocked(upgrade_id):
                        continue
                elif upgrade_id in hardware_upgrades:
                    if not self.state.is_hardware_category_unlocked(upgrade.get("category", "")):
                        continue

                card_x = panel.rect.x + 10
                card_y = panel.rect.y + 50 + y_offset + 8
                card_width = panel.rect.width - 40
                card_height = 65

                card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                
                if card_rect.collidepoint(mouse_pos):
                    # Show tooltip with description
                    desc = upgrade.get("description", "")
                    effect = upgrade.get("effect", 0)
                    max_level = upgrade.get("max_level", 0)
                    if desc:
                        tooltip_text = desc
                        if effect and max_level:
                            tooltip_text += f"\nEffect: {effect}x per level"
                        self._draw_tooltip_box(mouse_pos, tooltip_text)
                    return
                
                y_offset += card_height + 14

    def _draw_tooltip_box(self, mouse_pos, text):
        """Draw a tooltip box at the mouse position"""
        # Create tooltip surface
        tooltip_font = pygame.font.Font(None, 22)
        lines = text.split("\n")
        
        max_width = 0
        for line in lines:
            width = tooltip_font.size(line)[0]
            max_width = max(max_width, width)
        
        padding = 15
        tooltip_width = max_width + padding * 2
        tooltip_height = len(lines) * 22 + padding * 2
        
        # Position tooltip to not go off screen
        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] + 15
        
        if tooltip_x + tooltip_width > self.current_width - 10:
            tooltip_x = mouse_pos[0] - tooltip_width - 10
        if tooltip_y + tooltip_height > self.current_height - 10:
            tooltip_y = mouse_pos[1] - tooltip_height - 10
        
        # Draw tooltip background
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        
        # Semi-transparent dark background
        tooltip_bg = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        tooltip_bg.fill((15, 18, 28, 230))
        self.screen.blit(tooltip_bg, (tooltip_x, tooltip_y))
        
        # Border
        pygame.draw.rect(self.screen, COLORS["electric_cyan"], tooltip_rect, 1, border_radius=4)
        
        # Draw text
        for i, line in enumerate(lines):
            text_surface = tooltip_font.render(line, True, COLORS["soft_white"])
            self.screen.blit(text_surface, (tooltip_x + padding, tooltip_y + padding + i * 22))

    def draw(self):
        self.screen.blit(self._get_gradient_surface(), (0, 0))

        # Draw circuit board background effect
        self.draw_circuit_background()

        # Draw binary rain (if enabled)
        if self.state.visual_settings["binary_rain"]:
            self.binary_rain.draw(self.screen)

        if not self.showing_settings and not self.showing_rebirth_confirmation:
            # Draw game elements in proper z-order (back to front)

            # 1. Background visual effects (drawn before accumulator)
            if self.state.visual_settings["particle_effects"]:
                # Draw only background particles, not interactive elements
                self.bit_visualization.draw(self.screen, self.state.bits)

            # 2. Draw top bar with title and bit counter
            self.draw_top_bar()

            # 3. Main accumulator and click area (central element)
            self.draw_accumulator()

            # 4. Side panels (drawn after accumulator so they appear in front)
            self.draw_hardware_panel()
            self.draw_upgrades_panel()

            # 5. Bottom rebirth bar
            self.draw_rebirth_bar()

            # 6. Interactive effects and UI elements
            self.draw_effects()
            self.draw_tutorial()

            # Header buttons (always on top)
            self.settings_button.draw(self.screen)
            self.stats_button.draw(self.screen)

            # Draw tooltips (after everything else)
            self.draw_tooltips()

            # CRT scanline overlay (final layer)
            if self.state.visual_settings["crt_effects"]:
                self.draw_crt_overlay()
        elif self.showing_rebirth_confirmation:
            # Draw rebirth confirmation modal
            self.draw_rebirth_confirmation()
        else:
            # Draw settings page
            self.draw_settings_page()

    def draw_circuit_background(self):
        """Draw subtle circuit board pattern in background"""
        # Draw faint circuit traces
        circuit_color = (30, 40, 60)
        trace_width = 2
        
        # Vertical traces on left and right thirds
        for x in [int(self.current_width * 0.15), int(self.current_width * 0.85)]:
            pygame.draw.line(self.screen, circuit_color, (x, 0), (x, self.current_height), trace_width)
        
        # Horizontal traces
        for y in [int(self.current_height * 0.3), int(self.current_height * 0.6)]:
            pygame.draw.line(self.screen, circuit_color, (0, y), (self.current_width, trace_width))
        
        # Draw circuit nodes (small circles at intersections)
        node_color = (40, 55, 80)
        node_radius = 4
        for x in [int(self.current_width * 0.15), int(self.current_width * 0.85)]:
            for y in [int(self.current_height * 0.3), int(self.current_height * 0.6)]:
                pygame.draw.circle(self.screen, node_color, (x, y), node_radius)

    def _draw_binary_stream(self, x, y_start, char_height):
        """Draw animated binary digits streaming down the side of accumulator"""
        import random
        time_ms = pygame.time.get_ticks()
        
        # Create binary stream effect
        num_digits = 8
        binary_font = pygame.font.Font(None, 18)
        
        for i in range(num_digits):
            # Stagger the animation
            offset = (time_ms // 300 + i * 50) % 300
            y_pos = y_start + i * char_height - (offset / 10)
            
            # Random binary digit that changes slowly
            seed = (time_ms // 1000 + i) % 2
            digit = "1" if seed else "0"
            
            # Color based on digit - 1s are brighter
            color = COLORS["matrix_green"] if digit == "1" else (30, 80, 30)
            alpha = 180 if digit == "1" else 80
            
            # Create surface for alpha blending
            text_surface = binary_font.render(digit, True, color)
            text_surface.set_alpha(alpha)
            self.screen.blit(text_surface, (x, y_pos))

    def draw_top_bar(self):
        """Draw the top bar with title and bit counter - improved hierarchy"""
        scale_x = self.current_width / self.base_width
        scale_y = self.current_height / self.base_height
        
        # Top bar background with gradient effect
        top_bar_rect = pygame.Rect(0, 0, self.current_width, int(80 * scale_y))
        
        # Subtle gradient background
        for i in range(int(80 * scale_y)):
            color_ratio = i / (80 * scale_y)
            color = (
                int(15 + color_ratio * 10),
                int(20 + color_ratio * 12),
                int(35 + color_ratio * 20)
            )
            pygame.draw.line(self.screen, color, (0, i), (self.current_width, i))
        
        # Bottom border glow - more prominent
        border_color = COLORS["electric_cyan"]
        pygame.draw.line(self.screen, border_color, 
                        (0, int(80 * scale_y)), 
                        (self.current_width, int(80 * scale_y)), 2)
        # Add glow
        for i in range(1, 4):
            alpha = 40 - i * 10
            glow_color = (*border_color[:3], alpha) if len(border_color) > 3 else border_color
            pygame.draw.line(self.screen, border_color, 
                            (0, int(80 * scale_y) + i), 
                            (self.current_width, int(80 * scale_y) + i), 1)
        
        # Title on left side - more prominent
        title_text = self.large_font.render(
            "BIT BY BIT", True, COLORS["electric_cyan"]
        )
        # Title glow
        for offset, alpha in [((2, 2), 30), ((1, 1), 50)]:
            glow_surface = title_text.copy()
            glow_surface.set_alpha(alpha)
            self.screen.blit(glow_surface, (int(20 * scale_x) + offset[0], int(12 * scale_y) + offset[1]))
        self.screen.blit(title_text, (int(20 * scale_x), int(12 * scale_y)))
        
        subtitle_text = self.small_font.render(
            "Information Accumulator", True, COLORS["muted_blue"]
        )
        self.screen.blit(subtitle_text, (int(20 * scale_x), int(50 * scale_y)))
        
        # Bit counter - HUGE and prominent in center-top (main focal point)
        if not hasattr(self, "display_bits"):
            self.display_bits = self.state.bits
        
        smoothing_factor = 0.15
        self.display_bits += (self.state.bits - self.display_bits) * smoothing_factor
        
        # Main bit counter - massive and glowing
        bits_str = f"{self.format_number(int(self.display_bits))}"
        bits_text = self.bit_counter_font.render(bits_str, True, COLORS["matrix_green"])
        
        # Multi-layer glow effect for bit counter
        for offset, alpha in [((4, 4), 15), ((3, 3), 25), ((2, 2), 40), ((1, 1), 60)]:
            glow_surface = bits_text.copy()
            glow_surface.set_alpha(alpha)
            glow_pos = (self.current_width // 2 - bits_text.get_width() // 2 + offset[0],
                       int(25 * scale_y) + offset[1])
            self.screen.blit(glow_surface, glow_pos)
        
        bits_rect = bits_text.get_rect(center=(self.current_width // 2, int(40 * scale_y)))
        self.screen.blit(bits_text, bits_rect)
        
        # Production rate display - directly below bit counter, clear hierarchy
        rate = self.state.get_production_rate()
        rate_str = f"+{self.format_number(int(rate))} bits/sec"
        rate_text = self.medium_font.render(rate_str, True, COLORS["electric_cyan"])
        rate_rect = rate_text.get_rect(center=(self.current_width // 2, int(68 * scale_y)))
        
        # Rate glow
        for offset, alpha in [((1, 1), 30), ((-1, -1), 50)]:
            glow_surface = rate_text.copy()
            glow_surface.set_alpha(alpha)
            self.screen.blit(glow_surface, (rate_rect.x + offset[0], rate_rect.y + offset[1]))
        
        self.screen.blit(rate_text, rate_rect)
        
        # Click power display (if different from base)
        click_power = self.state.get_click_power()
        if click_power > 1:
            click_str = f"Click: +{self.format_number(click_power)}"
            click_text = self.small_font.render(click_str, True, COLORS["signal_orange"])
            click_rect = click_text.get_rect(center=(self.current_width // 2, int(88 * scale_y)))
            self.screen.blit(click_text, click_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.update(dt)
            self.draw()

            pygame.display.flip()

        # Save before quitting
        self.save_game()
        pygame.quit()
        sys.exit()
