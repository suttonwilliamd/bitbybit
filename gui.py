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

        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.large_font = pygame.font.Font(None, 36)
        self.medium_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        self.tiny_font = pygame.font.Font(None, 16)
        try:
            self.monospace_font = pygame.font.SysFont("Courier New", 24)
        except (pygame.error, OSError):
            self.monospace_font = pygame.font.Font(None, 24)

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

        # Panel states - start with panels collapsed
        self.generators_panel_open = False
        self.upgrades_panel_open = False

        # Calculate responsive panel dimensions
        panel_margin = 50
        panel_spacing = 30
        toggle_button_height = 40
        accumulator_height = 400  # Leave space for accumulator area
        
        # Calculate complete space needed for click button including visual elements
        button_height = 50
        button_spacing = 15
        button_border_and_glow = 4  # 2px border + 2px potential glow
        aesthetic_spacing = 40  # Better visual breathing room
        total_button_space = button_height + button_spacing + button_border_and_glow + aesthetic_spacing

        # Panel positions - ensure complete visual clearance for click button
        panel_y_start = accumulator_height + total_button_space
        available_height = WINDOW_HEIGHT - panel_y_start - 50  # Leave margin at bottom
        panel_height = max(250, min(available_height, 350))  # Between 250-350px

        # Panel widths - ensure both fit side by side with margins
        total_panel_width = WINDOW_WIDTH - (panel_margin * 2) - panel_spacing
        generators_width = int(total_panel_width * 0.55)  # 55% for generators
        upgrades_width = int(total_panel_width * 0.45)  # 45% for upgrades

        # Scrollable panels with responsive sizing
        self.generators_scroll_panel = ScrollablePanel(
            panel_margin,
            panel_y_start + toggle_button_height,
            generators_width,
            panel_height,
            "INFORMATION SOURCES",
        )
        self.upgrades_scroll_panel = ScrollablePanel(
            panel_margin + generators_width + panel_spacing,
            panel_y_start + toggle_button_height,
            upgrades_width,
            panel_height,
            "UPGRADES",
        )

        # Panel toggle buttons with responsive sizing
        self.generators_toggle = Button(
            panel_margin,
            panel_y_start,
            generators_width,
            toggle_button_height,
            "▶ INFORMATION SOURCES",
            (35, 40, 55),
            high_contrast=self.high_contrast_mode,
        )
        self.upgrades_toggle = Button(
            panel_margin + generators_width + panel_spacing,
            panel_y_start,
            upgrades_width,
            toggle_button_height,
            "▶ UPGRADES",
            (35, 40, 55),
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
        """Handle window resizing and update UI element positions"""
        self.current_width = new_width
        self.current_height = new_height

        # Calculate scale factors
        scale_x = new_width / self.base_width
        scale_y = new_height / self.base_height

        # Update accumulator and bit grid - enhanced responsive layout
        self.bit_grid.x = int(new_width // 2 - 300 * scale_x)
        self.bit_grid.width = int(600 * scale_x)
        self.bit_grid.height = int(300 * scale_y)

        # Update click button
        self.click_button.rect.x = int(new_width // 2 - 150 * scale_x)
        self.click_button.rect.y = int(420 * scale_y)
        self.click_button.rect.width = int(300 * scale_x)
        self.click_button.rect.height = int(60 * scale_y)

        # Update header buttons
        self.settings_button.rect.x = int(new_width - 150 * scale_x)
        self.stats_button.rect.x = int(new_width - 280 * scale_x)

        # Update panel positions with responsive sizing
        panel_margin = int(50 * scale_x)
        panel_spacing = int(30 * scale_x)
        toggle_button_height = int(40 * scale_y)
        accumulator_height = int(400 * scale_y)
        
        # Calculate complete space needed for click button including visual elements
        button_height = int(50 * scale_y)
        button_spacing = int(15 * scale_y)
        button_border_and_glow = int(4 * scale_y)  # 2px border + 2px potential glow
        aesthetic_spacing = int(40 * scale_y)  # Better visual breathing room
        total_button_space = button_height + button_spacing + button_border_and_glow + aesthetic_spacing

        # Panel positions - ensure complete visual clearance for click button
        panel_y_start = accumulator_height + total_button_space
        available_height = new_height - panel_y_start - int(80 * scale_y)
        panel_height = max(
            int(250 * scale_y), min(available_height, int(350 * scale_y))
        )

        # Panel widths - ensure both fit side by side
        total_panel_width = new_width - (panel_margin * 2) - panel_spacing
        generators_width = int(total_panel_width * 0.55)
        upgrades_width = int(total_panel_width * 0.45)

        # Generators panel
        generators_x = panel_margin
        generators_y = panel_y_start + toggle_button_height

        self.generators_scroll_panel.rect.x = generators_x
        self.generators_scroll_panel.rect.y = generators_y
        self.generators_scroll_panel.rect.width = generators_width
        self.generators_scroll_panel.rect.height = panel_height

        # Upgrades panel
        upgrades_x = panel_margin + generators_width + panel_spacing
        upgrades_y = panel_y_start + toggle_button_height

        self.upgrades_scroll_panel.rect.x = upgrades_x
        self.upgrades_scroll_panel.rect.y = upgrades_y
        self.upgrades_scroll_panel.rect.width = upgrades_width
        self.upgrades_scroll_panel.rect.height = panel_height

        # Update panel toggle buttons
        self.generators_toggle.rect.x = generators_x
        self.generators_toggle.rect.y = panel_y_start
        self.generators_toggle.rect.width = generators_width
        self.generators_toggle.rect.height = toggle_button_height

        self.upgrades_toggle.rect.x = upgrades_x
        self.upgrades_toggle.rect.y = panel_y_start
        self.upgrades_toggle.rect.width = upgrades_width
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
                self.generators_scroll_panel.handle_scroll(event)
                self.upgrades_scroll_panel.handle_scroll(event)

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
                self.generators_panel_open
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
            if self.generators_toggle.is_clicked(event):
                self.generators_panel_open = not self.generators_panel_open

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
            self.generators_toggle.update(mouse_pos)
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
        panel = self.generators_scroll_panel

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
                if not self.state.is_hardware_category_unlocked(generator["category"]):
                    continue

            count = self.state.generators[gen_id]["count"]
            cost = self.state.get_generator_cost(gen_id)
            can_afford = self.state.can_afford(cost)

            # Card position (optimized dimensions)
            card_x = panel.rect.x + 10
            card_y = panel.rect.y + 50 + y_offset + 8  # Reduced from 10
            card_width = panel.rect.width - 40
            card_height = 70  # Reduced from 90

            # Check if click is within this card
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            if not card_rect.collidepoint(mouse_pos):
                y_offset += card_height + 8  # Reduced spacing
                continue

            # Check button positions (bottom right of card) - updated for compact layout
            button_y = card_y + card_height - 25  # Reduced from 32
            btn_width = 60  # Updated to match card drawing
            btn_height = 22  # Updated to match card drawing

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

            y_offset += card_height + 8  # Reduced spacing

    def handle_upgrade_card_clicks(self, mouse_pos):
        """Handle clicks on upgrade card buttons"""
        panel = self.upgrades_scroll_panel

        all_upgrades = get_all_upgrades()

        y_offset = -panel.get_scroll_offset()

        for upgrade_id, upgrade in all_upgrades.items():
            basic_upgrades = UPGRADES if UPGRADES else CONFIG["UPGRADES"]
            hardware_upgrades = CONFIG.get("HARDWARE_UPGRADES", {})
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

            # Card position (optimized dimensions)
            card_x = panel.rect.x + 10
            card_y = panel.rect.y + 50 + y_offset + 8  # Reduced from 10
            card_width = panel.rect.width - 40
            card_height = 65  # Reduced from 85

            # Check if click is within this card
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            if not card_rect.collidepoint(mouse_pos):
                y_offset += card_height + 8  # Reduced spacing
                continue

            # Check if maxed
            if level >= upgrade["max_level"]:
                y_offset += card_height + 8  # Reduced spacing
                continue

            # BUY button (bottom right) - updated for compact layout
            button_x = card_x + card_width - 80  # Adjusted for compact layout
            button_y = card_y + card_height - 25  # Reduced from 30
            btn_rect = pygame.Rect(button_x, button_y, 70, 20)  # Smaller button

            if btn_rect.collidepoint(mouse_pos) and can_afford:
                self.buy_upgrade(upgrade_id)
                return

            y_offset += card_height + 8  # Reduced spacing

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
        production_rate = self.state.get_production_rate()
        dt = 1 / FPS

        scale_x = self.current_width / self.base_width
        scale_y = self.current_height / self.base_height

        acc_width = int(650 * scale_x)
        acc_height = int(340 * scale_y)
        acc_x = self.current_width // 2 - acc_width // 2
        acc_y = int(85 * scale_y)

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
        center_x = self.current_width // 2

        pygame.draw.rect(self.screen, (10, 10, 20), acc_rect, border_radius=12)

        time_ms = pygame.time.get_ticks()
        border_glow = abs(math.sin(time_ms * 0.002)) * 0.2 + 0.8
        border_color = tuple(int(c * border_glow) for c in COLORS["electric_cyan"])
        pygame.draw.rect(self.screen, border_color, acc_rect, 2, border_radius=12)

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
        if not hasattr(self, "display_compressed_bits"):
            self.display_compressed_bits = getattr(self.state, "compressed_bits", 0)
        if not hasattr(self, "display_rate"):
            self.display_rate = self.state.get_production_rate()

        smoothing_factor = 0.1
        self.display_bits += (self.state.bits - self.display_bits) * smoothing_factor
        if hasattr(self.state, "compressed_bits"):
            self.display_compressed_bits += (
                self.state.compressed_bits - self.display_compressed_bits
            ) * smoothing_factor
        self.display_rate += (
            self.state.get_production_rate() - self.display_rate
        ) * smoothing_factor

        if self.state.era == "compression":
            bits_str = f"{self.format_number(int(self.display_compressed_bits))} cb"
            bits_color = COLORS["neon_purple"]
        else:
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

        if self.state.era == "compression":
            efficiency = self.state.efficiency * 100
            rate_str = f"+{self.format_number(int(self.display_rate))} cb/s"
            rate_color = COLORS["neon_purple"]
        else:
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
        else:
            click_text = self.medium_font.render(
                f"Tokens: {self.state.compression_tokens} ⭐", True, COLORS["gold"]
            )
            click_rect = click_text.get_rect(center=(center_x, button_y + button_height // 2))
            self.screen.blit(click_text, click_rect)

    def _update_button_accessibility(self):
        """Update all buttons to match accessibility settings"""
        # Update panel toggle buttons
        self.generators_toggle.high_contrast = self.high_contrast_mode
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
        """Draw panel toggle button with better affordances"""
        # Better visual state for toggle
        if is_open:
            bg_color = (45, 50, 65)
            border_color = COLORS["electric_cyan"]
            text_color = COLORS["electric_cyan"]
        else:
            bg_color = (32, 36, 48)
            border_color = COLORS["muted_blue"]
            text_color = COLORS["muted_blue"]

        # Background
        pygame.draw.rect(self.screen, bg_color, button.rect, border_radius=6)

        # Border with glow effect if open
        if is_open:
            # Glow
            glow_rect = button.rect.inflate(4, 4)
            glow_surf = pygame.Surface(
                (glow_rect.width, glow_rect.height), pygame.SRCALPHA
            )
            pygame.draw.rect(
                glow_surf,
                (*COLORS["electric_cyan"], 40),
                (0, 0, glow_rect.width, glow_rect.height),
                border_radius=8,
            )
            self.screen.blit(glow_surf, glow_rect)

        pygame.draw.rect(self.screen, border_color, button.rect, 2, border_radius=6)

        # Text
        text_surface = self.small_font.render(button.text, True, text_color)
        text_rect = text_surface.get_rect(center=button.rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_panel_with_integrated_title(self, panel, title_color=None):
        """Draw a panel with integrated title bar (the correct design)"""
        if title_color is None:
            title_color = COLORS["electric_cyan"]

        # Main panel background
        pygame.draw.rect(self.screen, (22, 25, 35), panel.rect, border_radius=10)

        # Outer border
        pygame.draw.rect(
            self.screen, COLORS["muted_blue"], panel.rect, 2, border_radius=10
        )

        # Title bar (integrated at top)
        title_bar_height = 45
        title_rect = pygame.Rect(
            panel.rect.x, panel.rect.y, panel.rect.width, title_bar_height
        )
        pygame.draw.rect(
            self.screen,
            (28, 32, 45),
            title_rect,
            border_top_left_radius=10,
            border_top_right_radius=10,
        )

        # Title text
        title_surface = self.medium_font.render(panel.title, True, title_color)
        title_text_rect = title_surface.get_rect(
            center=(panel.rect.centerx, panel.rect.y + title_bar_height // 2)
        )
        self.screen.blit(title_surface, title_text_rect)

        # Separator line under title
        pygame.draw.line(
            self.screen,
            title_color,
            (panel.rect.x + 10, panel.rect.y + title_bar_height),
            (panel.rect.x + panel.rect.width - 10, panel.rect.y + title_bar_height),
            2,
        )

    def draw_panel_background(self, panel):
        """Legacy method - use draw_panel_with_integrated_title instead"""
        self.draw_panel_with_integrated_title(panel)

    def draw_scrollbar(self, panel):
        """Draw scrollbar for panel"""
        if panel.content_height <= panel.rect.height - 60:
            return

        scrollbar_x = panel.rect.right - 12
        scrollbar_y = panel.rect.y + 50
        scrollbar_height = panel.rect.height - 60

        # Track
        track_rect = pygame.Rect(scrollbar_x, scrollbar_y, 8, scrollbar_height)
        pygame.draw.rect(self.screen, (40, 45, 55), track_rect, border_radius=4)

        # Thumb
        thumb_height = max(
            30, (scrollbar_height * scrollbar_height) // panel.content_height
        )
        scroll_range = max(1, panel.content_height - scrollbar_height)
        thumb_y = (
            scrollbar_y
            + (panel.scroll_offset * (scrollbar_height - thumb_height)) // scroll_range
        )
        thumb_rect = pygame.Rect(scrollbar_x, thumb_y, 8, thumb_height)
        pygame.draw.rect(
            self.screen, COLORS["electric_cyan"], thumb_rect, border_radius=4
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
        """Draw individual generator card with proper layout and spacing"""
        card_rect = pygame.Rect(x, y, width, height)

        # Enhanced color scheme with better contrast
        if can_afford:
            bg_color = (28, 32, 42)
            border_color = COLORS["electric_cyan"]
            border_alpha = 200
            cost_color = COLORS["matrix_green"]
        else:
            bg_color = (25, 25, 30)
            border_color = COLORS["muted_blue"]
            border_alpha = 120
            cost_color = COLORS["muted_blue"]

        # Draw card background with rounded corners
        pygame.draw.rect(surface, bg_color, card_rect, border_radius=8)

        # Draw enhanced border with glow effect if affordable
        if can_afford:
            # Glow effect for affordable cards
            glow_surf = pygame.Surface((width + 4, height + 4), pygame.SRCALPHA)
            pygame.draw.rect(
                glow_surf,
                (*border_color, 30),
                (0, 0, width + 4, height + 4),
                border_radius=10,
            )
            surface.blit(glow_surf, (x - 2, y - 2))

        # Main border
        border_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(
            border_surf,
            (*border_color, border_alpha),
            (0, 0, width, height),
            2,
            border_radius=8,
        )
        surface.blit(border_surf, (x, y))

        # Icon (optimized for smaller cards)
        icon_size = 36  # Reduced from 48
        icon_x = x + 12
        icon_y = y + height // 2 - icon_size // 2

        # Try to render emoji icon with fallback
        icon_text = generator.get("icon", "🎲")
        try:
            icon_font = pygame.font.Font(
                None,
                36,  # Smaller font for compact cards
            )
            icon_surface = icon_font.render(
                icon_text, True, border_color if can_afford else COLORS["muted_blue"]
            )
            surface.blit(icon_surface, (icon_x, icon_y))
        except (pygame.error, UnicodeEncodeError):
            pygame.draw.circle(
                surface,
                border_color if can_afford else COLORS["muted_blue"],
                (icon_x + icon_size // 2, icon_y + icon_size // 2),
                15,
            )

        # Text area with optimized spacing
        text_x = x + 55  # Moved left due to smaller icon
        line_height = 18  # Reduced from 22

        # Name (top line, compact)
        name_text = self.small_font.render(  # Use smaller font
            generator["name"], True, COLORS["soft_white"]
        )
        surface.blit(name_text, (text_x, y + 10))

        # Quantity and production on same line to save space
        if production > 0:
            qty_prod_text = self.tiny_font.render(
                f"Qty: {count} | Rate: +{self.format_number(production)} b/s",
                True,
                COLORS["muted_blue"],
            )
            surface.blit(qty_prod_text, (text_x, y + 28))
        else:
            qty_text = self.tiny_font.render(
                f"Qty: {count}", True, COLORS["muted_blue"]
            )
            surface.blit(qty_text, (text_x, y + 28))

        # Cost and buttons area (bottom right)
        bottom_y = y + height - 25  # Reduced from 35

        # Cost text (left of buttons)
        cost_text = self.tiny_font.render(
            f"{self.format_number(cost)}",
            True,
            cost_color,
        )
        surface.blit(cost_text, (x + width - 150, bottom_y + 6))

        # Buy buttons (optimized for compact layout)
        btn_width = 60  # Reduced from 70
        btn_height = 22  # Reduced from 28
        btn_spacing = 4
        btn_color = (45, 55, 70) if can_afford else (30, 33, 40)

        # BUY x10 button (left)
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
            COLORS["electric_cyan"] if can_afford else COLORS["muted_blue"],
            btn1_rect,
            1,
            border_radius=3,
        )
        btn1_text = self.tiny_font.render(
            "BUY x10",
            True,
            COLORS["soft_white"] if can_afford else COLORS["muted_blue"],
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
            COLORS["electric_cyan"] if can_afford else COLORS["muted_blue"],
            btn2_rect,
            1,
            border_radius=3,
        )
        btn2_text = self.tiny_font.render(
            "BUY x1",
            True,
            COLORS["soft_white"] if can_afford else COLORS["muted_blue"],
        )
        btn2_text_rect = btn2_text.get_rect(center=btn2_rect.center)
        surface.blit(btn2_text, btn2_text_rect)

    def draw_upgrade_card(
        self, surface, x, y, width, height, upgrade, upgrade_id, level, cost, can_afford
    ):
        """Draw individual upgrade card with proper layout and spacing"""
        card_rect = pygame.Rect(x, y, width, height)

        # Enhanced purple theme for upgrades
        max_level = upgrade["max_level"]
        is_maxed = level >= max_level

        if is_maxed:
            bg_color = (35, 30, 45)
            border_color = COLORS["gold"]
            border_alpha = 220
            text_color = COLORS["gold"]
        elif can_afford:
            bg_color = (30, 28, 40)
            border_color = COLORS["neon_purple"]
            border_alpha = 200
            text_color = COLORS["soft_white"]
        else:
            bg_color = (25, 25, 30)
            border_color = COLORS["muted_blue"]
            border_alpha = 120
            text_color = COLORS["muted_blue"]

        # Background
        pygame.draw.rect(surface, bg_color, card_rect, border_radius=8)

        # Enhanced border with glow for affordable upgrades
        if can_afford and not is_maxed:
            # Subtle glow effect
            glow_surf = pygame.Surface((width + 4, height + 4), pygame.SRCALPHA)
            pygame.draw.rect(
                glow_surf,
                (*border_color, 40),
                (0, 0, width + 4, height + 4),
                border_radius=10,
            )
            surface.blit(glow_surf, (x - 2, y - 2))

        # Main border
        border_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(
            border_surf,
            (*border_color, border_alpha),
            (0, 0, width, height),
            2,
            border_radius=8,
        )
        surface.blit(border_surf, (x, y))

        # Icon (optimized for compact cards)
        icon_x = x + 12
        icon_y = y + height // 2 - 18
        icon_text = upgrade.get("icon", "⚡")

        try:
            icon_font = pygame.font.Font(None, 36)  # Smaller for compact cards
            icon_surface = icon_font.render(
                icon_text, True, border_color if can_afford else COLORS["muted_blue"]
            )
            surface.blit(icon_surface, (icon_x, icon_y))
        except (pygame.error, UnicodeEncodeError):
            pygame.draw.circle(
                surface,
                border_color if can_afford else COLORS["muted_blue"],
                (icon_x + 18, icon_y + 18),
                15,
            )

        # Text area with optimized spacing
        text_x = x + 50  # Moved left due to smaller icon
        line_height = 18  # Reduced from 22

        # Name (top line, compact)
        name_text = self.small_font.render(
            upgrade["name"], True, COLORS["soft_white"]
        )  # Smaller font
        surface.blit(name_text, (text_x, y + 8))

        # Level and info on same line to save space
        level_color = COLORS["gold"] if is_maxed else COLORS["neon_purple"]
        level_text = self.small_font.render(
            f"Level {level}/{max_level}",
            True,
            level_color,
        )
        surface.blit(level_text, (text_x, y + 12 + line_height))

        # Effect description (third line)
        effect_text = upgrade.get("description", "Increases production")
        desc_text = self.tiny_font.render(effect_text, True, COLORS["muted_blue"])
        surface.blit(desc_text, (text_x, y + 12 + line_height * 2))

        # Cost and button area (bottom right)
        if is_maxed:
            # Centered MAXED indicator
            maxed_text = self.medium_font.render("MAXED", True, COLORS["gold"])
            maxed_rect = maxed_text.get_rect(center=(x + width - 60, y + height // 2))
            surface.blit(maxed_text, maxed_rect)
        else:
            # Cost (above button)
            cost_y = y + height - 40
            cost_text = self.small_font.render(
                f"{self.format_number(cost)}",
                True,
                text_color,
            )
            cost_rect = cost_text.get_rect(center=(x + width - 60, cost_y))
            surface.blit(cost_text, cost_rect)

            # BUY button
            btn_y = y + height - 30
            btn_rect = pygame.Rect(x + width - 100, btn_y, 80, 24)

            if can_afford:
                btn_color = (55, 45, 75)
                btn_border = COLORS["neon_purple"]
                btn_text_color = COLORS["soft_white"]
            else:
                btn_color = (30, 33, 40)
                btn_border = COLORS["muted_blue"]
                btn_text_color = COLORS["muted_blue"]

            pygame.draw.rect(surface, btn_color, btn_rect, border_radius=4)
            pygame.draw.rect(surface, btn_border, btn_rect, 1, border_radius=4)

            btn_text = self.small_font.render("BUY", True, btn_text_color)
            btn_text_rect = btn_text.get_rect(center=btn_rect.center)
            surface.blit(btn_text, btn_text_rect)

    def draw_generators_panel(self):
        """Draw generators panel with better design and scrolling"""
        # Update toggle button text based on state
        if self.generators_panel_open:
            self.generators_toggle.text = "▼ INFORMATION SOURCES"
        else:
            self.generators_toggle.text = "▶ INFORMATION SOURCES"

        # Draw toggle button with better styling
        self.draw_panel_toggle(self.generators_toggle, self.generators_panel_open)

        if not self.generators_panel_open:
            return

        # Draw scrollable panel background with integrated title
        panel = self.generators_scroll_panel
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

            # Card dimensions - optimized for better space utilization
            card_height = 70  # Reduced from 90
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

            y_offset += card_height + 8  # Reduced spacing from 12

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

            # Card - optimized for better space utilization
            card_height = 65  # Reduced from 85
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

            y_offset += card_height + 8  # Reduced spacing from 12

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
            # Show current generation and progress
            gen_text = f"{current_gen['icon'] if 'icon' in current_gen else '💻'} {current_gen['name']}"
            text_color = COLORS["neon_purple"]
            text_surface = self.medium_font.render(gen_text, True, text_color)
            text_rect = text_surface.get_rect(
                center=(
                    self.current_width // 2,
                    self.current_height - int(60 * scale_y),
                )
            )
            self.screen.blit(text_surface, text_rect)

            # Show next generation info if available
            if next_gen:
                next_text = f"Next: {next_gen['name'].split()[0]} at {target_mb} MB"
                next_color = COLORS["muted_blue"]
                next_surface = self.small_font.render(next_text, True, next_color)
                next_rect = next_surface.get_rect(
                    center=(
                        self.current_width // 2,
                        self.current_height - int(40 * scale_y),
                    )
                )
                self.screen.blit(next_surface, next_rect)

        # Progress text with era completion
        progress_text = self.monospace_font.render(
            f"{era_completion_text} | ({current_mb} MB / {target_mb} MB)",
            True,
            COLORS["soft_white"],
        )
        progress_rect = progress_text.get_rect(
            center=(self.current_width // 2, self.current_height - int(25 * scale_y))
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

    def draw(self):
        self.screen.blit(self._get_gradient_surface(), (0, 0))

        # Draw binary rain (if enabled)
        if self.state.visual_settings["binary_rain"]:
            self.binary_rain.draw(self.screen)

        if not self.showing_settings and not self.showing_rebirth_confirmation:
            # Draw game elements in proper z-order (back to front)

            # 1. Background visual effects (drawn before accumulator)
            if self.state.visual_settings["particle_effects"]:
                # Draw only background particles, not interactive elements
                self.bit_visualization.draw(self.screen, self.state.bits)

            # 2. Main accumulator (central element)
            self.draw_accumulator()

            # 3. Side panels (drawn after accumulator so they appear in front)
            self.draw_generators_panel()
            self.draw_upgrades_panel()

            # 4. Bottom rebirth bar
            self.draw_rebirth_bar()

            # 5. Interactive effects and UI elements
            self.draw_effects()
            self.draw_tutorial()

            # 6. Header UI (top layer)
            title_text = self.large_font.render(
                "BIT BY BIT", True, COLORS["electric_cyan"]
            )
            title_rect = title_text.get_rect(
                center=(
                    self.current_width // 2,
                    int(40 * (self.current_height / self.base_height)),
                )
            )
            self.screen.blit(title_text, title_rect)

            subtitle_text = self.small_font.render(
                "A Game About Information", True, COLORS["muted_blue"]
            )
            subtitle_rect = subtitle_text.get_rect(
                center=(
                    self.current_width // 2,
                    int(70 * (self.current_height / self.base_height)),
                )
            )
            self.screen.blit(subtitle_text, subtitle_rect)

            # Header buttons (always on top)
            self.settings_button.draw(self.screen)
            self.stats_button.draw(self.screen)

            # CRT scanline overlay (final layer)
            if self.state.visual_settings["crt_effects"]:
                self.draw_crt_overlay()
        elif self.showing_rebirth_confirmation:
            # Draw rebirth confirmation modal
            self.draw_rebirth_confirmation()
        else:
            # Draw settings page
            self.draw_settings_page()

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
