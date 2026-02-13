"""
GUI module for Bit by Bit Game

This module provides a modular GUI system with the following submodules:
- panels: ScrollablePanel class for panel management
- cards: Generator and upgrade card drawing functions
- modals: Settings, rebirth, and tutorial modal dialogs
- top_bar: Top bar drawing functions
- accumulator: Accumulator drawing functions
- effects: Visual effects (CRT, particles, tooltips)
- information_core: Main click target drawing
- rebirth_bar: Rebirth progress bar drawing
"""

import pygame
import sys
import math
import json
import os
import random

from constants import (
    COLORS, CONFIG, GENERATORS, UPGRADES, WINDOW_WIDTH, WINDOW_HEIGHT,
    FPS, get_all_generators, get_all_upgrades
)
from game_state import GameState
from visual_effects import Particle, BinaryRain, SmartBitVisualization
from ui_components import Button, FloatingText, LayoutManager, GameUIState
from bit_grid import MotherboardBitGrid
from compression_ui import CompressionPanel, CompressionMeter, TokenDisplay, CompressionProgressBar

from .panels import ScrollablePanel
from .cards import draw_generator_card, draw_upgrade_card, draw_panel_toggle, draw_panel_with_integrated_title, draw_scrollbar
from .modals import draw_rebirth_confirmation, draw_prestige_confirmation, draw_tutorial, draw_settings_page
from .top_bar import draw_top_bar
from .accumulator import draw_accumulator
from .effects import draw_effects, draw_crt_overlay, draw_circuit_background, draw_tooltips
from .information_core import draw_information_core
from .rebirth_bar import draw_rebirth_bar
from .motherboard_notification import MotherboardUpgradeNotification


UI_ARROW_DOWN = "▼"
UI_ARROW_RIGHT = "▶"

try:
    test_font = pygame.font.SysFont("Segoe UI Symbol", 12)
    if not test_font.render(UI_ARROW_DOWN, True, (255, 255, 255)).get_width() > 0:
        raise Exception("Font doesn't render Unicode")
except:
    UI_ARROW_DOWN = "v"
    UI_ARROW_RIGHT = ">"


class BitByBitGame:
    def __init__(self):
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE
        )
        pygame.display.set_caption("Bit by Bit - A Game About Information")
        self.clock = pygame.time.Clock()
        self.running = True

        self.base_width = WINDOW_WIDTH
        self.base_height = WINDOW_HEIGHT
        self.current_width = WINDOW_WIDTH
        self.current_height = WINDOW_HEIGHT

        self._setup_fonts()
        self.state = GameState()
        
        self._setup_visual_systems()
        self._setup_accessibility()
        
        self.layout = LayoutManager(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        self.bit_grid = MotherboardBitGrid(
            WINDOW_WIDTH // 2 - 300, 120, 600, 240
        )

        self.information_core = {
            "x": WINDOW_WIDTH // 2,
            "y": 420,
            "radius": 120,
            "pulse_phase": 0,
            "particles": [],
            "click_effects": [],
        }
        self.click_button = Button(
            WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 180, 200, 50, "+1 bit", (40, 45, 65)
        )

        self._setup_compression_ui()
        self._setup_header_buttons()
        
        self.generator_buttons = {}
        self.generator_buy_buttons = {}
        self.setup_generator_buttons()

        self.upgrade_buttons = {}
        self.upgrade_card_buttons = {}
        self.setup_upgrade_buttons()

        self.component_upgrade_buttons = {}
        self.setup_component_upgrade_buttons()

        self.showing_settings = False
        self.showing_rebirth_confirmation = False
        self.showing_prestige_confirmation = False
        self.hardware_panel_open = True
        self.upgrades_panel_open = True

        self._setup_layout()
        self._setup_panels()
        self._setup_effects()
        
        self.last_auto_save = pygame.time.get_ticks()
        self.last_update = pygame.time.get_ticks()
        self.last_click_time = 0

        self.showing_tutorial = False
        self.tutorial_text = ""
        
        self.crt_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.crt_surface.set_alpha(30)

        self.rebirth_button = Button(
            WINDOW_WIDTH // 2 - 150,
            WINDOW_HEIGHT - 120,
            300,
            40,
            "🌀 COMPRESS DATA",
            COLORS["neon_purple"],
            COLORS["soft_white"],
        )

        self.prestige_button = Button(
            WINDOW_WIDTH // 2 - 75,
            WINDOW_HEIGHT - 170,
            150,
            35,
            "🔧 UPGRADE MOBO",
            COLORS["quantum_violet"],
            COLORS["soft_white"],
        )

        self.collect_shards_button = Button(
            WINDOW_WIDTH // 2 - 75,
            WINDOW_HEIGHT - 220,
            150,
            35,
            "💎 COLLECT SHARDS",
            COLORS["gold"],
            COLORS["soft_white"],
        )

        self._gradient_surface = None
        self._last_gradient_size = (0, 0)

        self.load_game()

    def _setup_fonts(self):
        try:
            self.title_font = pygame.font.SysFont("Consolas", 24, bold=True)
            self.large_font = pygame.font.SysFont("Consolas", 18, bold=True)
            self.medium_font = pygame.font.SysFont("Consolas", 16)
            self.small_font = pygame.font.SysFont("Consolas", 13)
            self.tiny_font = pygame.font.SysFont("Consolas", 11)
            self.monospace_font = pygame.font.SysFont("Consolas", 16)
            self.bit_counter_font = pygame.font.SysFont("Consolas", 28, bold=True)
            self.ui_font = pygame.font.SysFont("Segoe UI Symbol", 16)
            self.ui_font_fallback = pygame.font.SysFont("Arial", 16)
        except (pygame.error, OSError):
            self.title_font = pygame.font.Font(None, 24)
            self.large_font = pygame.font.Font(None, 18)
            self.medium_font = pygame.font.Font(None, 16)
            self.small_font = pygame.font.Font(None, 13)
            self.tiny_font = pygame.font.Font(None, 11)
            self.monospace_font = pygame.font.Font(None, 16)
            self.bit_counter_font = pygame.font.Font(None, 28)
            self.ui_font = pygame.font.Font(None, 16)
            self.ui_font_fallback = pygame.font.Font(None, 16)

    def _setup_visual_systems(self):
        self.binary_rain = BinaryRain(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.bit_visualization = SmartBitVisualization(WINDOW_WIDTH // 2, 200)

    def _setup_accessibility(self):
        self.high_contrast_mode = False
        self.reduced_motion_mode = False
        self.visual_quality = "high"

    def _setup_compression_ui(self):
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

    def _setup_header_buttons(self):
        self.settings_button = Button(
            WINDOW_WIDTH - 150, 20, 120, 40, "⚙️ CONFIG", (50, 50, 70)
        )
        self.stats_button = Button(
            WINDOW_WIDTH - 280, 20, 120, 40, "📊 STATUS", (50, 50, 70)
        )

    def _setup_layout(self):
        top_bar_height = 70
        side_panel_width = int(WINDOW_WIDTH * 0.22)
        center_area_width = WINDOW_WIDTH - (side_panel_width * 2)
        
        panel_y_start = top_bar_height + 20
        panel_height = WINDOW_HEIGHT - panel_y_start - 100
        toggle_button_height = 40
        
        left_panel_x = 15
        right_panel_x = WINDOW_WIDTH - side_panel_width - 15
        
        self.center_area_x = side_panel_width + 20
        self.center_area_width = center_area_width - 40
        
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

        self.hardware_toggle = Button(
            left_panel_x,
            panel_y_start,
            side_panel_width,
            toggle_button_height,
            UI_ARROW_RIGHT + " HARDWARE",
            (25, 30, 45),
            high_contrast=self.high_contrast_mode,
        )
        self.upgrades_toggle = Button(
            right_panel_x,
            panel_y_start,
            side_panel_width,
            toggle_button_height,
            UI_ARROW_RIGHT + " UPGRADES",
            (25, 30, 45),
            high_contrast=self.high_contrast_mode,
        )

    def _setup_panels(self):
        pass

    def _setup_effects(self):
        self.particles = []
        self.floating_texts = []
        self.motherboard_notification = MotherboardUpgradeNotification()
        self.max_particles = 100  # Performance limit for 60fps target
    
    def _add_particle(self, particle):
        """Add a particle while respecting the max limit for performance"""
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)
    
    def _add_particles(self, particles):
        """Add multiple particles while respecting the max limit"""
        available = self.max_particles - len(self.particles)
        if available > 0:
            self.particles.extend(particles[:available])

    def setup_generator_buttons(self):
        pass  # Generator buttons are handled dynamically in _draw_hardware_panel
        
    def setup_upgrade_buttons(self):
        x_start = 750
        y_start = 200
        card_height = 120

        basic_upgrades = UPGRADES if UPGRADES else CONFIG["UPGRADES"]
        hardware_upgrades = CONFIG.get("HARDWARE_UPGRADES", {})
        all_upgrades = {**basic_upgrades, **hardware_upgrades}

        for i, (upgrade_id, upgrade) in enumerate(all_upgrades.items()):
            y = y_start + i * (card_height + 10)

            buy_button = Button(x_start + 250, y + 70, 80, 30, "BUY")
            self.upgrade_buttons[upgrade_id] = buy_button

    def setup_component_upgrade_buttons(self):
        button_width = 50
        button_height = 18

        for comp_name, comp in self.bit_grid.components.items():
            button_x = comp["x"] + comp["width"] - button_width - 6
            button_y = comp["y"] + 4

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

    def handle_window_resize(self, new_width, new_height):
        self.current_width = new_width
        self.current_height = new_height
        
        self.layout.update_size(new_width, new_height)
        
        self.bit_grid.update_dimensions(
            self.layout.get_bit_grid_rect().x,
            self.layout.get_bit_grid_rect().y,
            self.layout.get_bit_grid_rect().width,
            self.layout.get_bit_grid_rect().height
        )
        
        click_btn_rect = self.layout.get_click_button_rect()
        self.click_button.rect.x = click_btn_rect.x
        self.click_button.rect.y = click_btn_rect.y
        self.click_button.rect.width = click_btn_rect.width
        self.click_button.rect.height = click_btn_rect.height
        
        comp_panel_rect = self.layout.get_compression_panel_rect()
        self.compression_panel.rect.x = comp_panel_rect.x
        self.compression_panel.rect.y = comp_panel_rect.y
        self.compression_panel.rect.width = comp_panel_rect.width
        self.compression_panel.rect.height = comp_panel_rect.height
        
        comp_meter_rect = self.layout.get_compression_meter_rect()
        self.compression_meter.rect.x = comp_meter_rect.x
        self.compression_meter.rect.y = comp_meter_rect.y
        self.compression_meter.rect.width = comp_meter_rect.width
        self.compression_meter.rect.height = comp_meter_rect.height
        
        token_pos = self.layout.get_token_display_pos()
        self.token_display.x = token_pos[0]
        self.token_display.y = token_pos[1]
        
        comp_prog_rect = self.layout.get_compression_progress_rect()
        self.compression_progress.rect.x = comp_prog_rect.x
        self.compression_progress.rect.y = comp_prog_rect.y
        self.compression_progress.rect.width = comp_prog_rect.width
        self.compression_progress.rect.height = comp_prog_rect.height
        
        settings_rect = self.layout.get_header_button_rect(is_settings=True)
        stats_rect = self.layout.get_header_button_rect(is_settings=False)
        self.settings_button.rect.x = settings_rect.x
        self.settings_button.rect.y = settings_rect.y
        self.stats_button.rect.x = stats_rect.x
        self.stats_button.rect.y = stats_rect.y
        
        left_panel = self.layout.get_left_panel_rect()
        right_panel = self.layout.get_right_panel_rect()
        self.hardware_scroll_panel.rect.x = left_panel.x
        self.hardware_scroll_panel.rect.y = left_panel.y
        self.hardware_scroll_panel.rect.width = left_panel.width
        self.hardware_scroll_panel.rect.height = left_panel.height
        
        self.upgrades_scroll_panel.rect.x = right_panel.x
        self.upgrades_scroll_panel.rect.y = right_panel.y
        self.upgrades_scroll_panel.rect.width = right_panel.width
        self.upgrades_scroll_panel.rect.height = right_panel.height
        
        left_toggle = self.layout.get_toggle_rect(is_left=True)
        right_toggle = self.layout.get_toggle_rect(is_left=False)
        self.hardware_toggle.rect.x = left_toggle.x
        self.hardware_toggle.rect.y = left_toggle.y
        self.hardware_toggle.rect.width = left_toggle.width
        self.hardware_toggle.rect.height = left_toggle.height
        
        self.upgrades_toggle.rect.x = right_toggle.x
        self.upgrades_toggle.rect.y = right_toggle.y
        self.upgrades_toggle.rect.width = right_toggle.width
        self.upgrades_toggle.rect.height = right_toggle.height
        
        rebirth_rect = self.layout.get_rebirth_button_rect()
        self.rebirth_button.rect.x = rebirth_rect.x
        self.rebirth_button.rect.y = rebirth_rect.y
        self.rebirth_button.rect.width = rebirth_rect.width
        
        prestige_rect = self.layout.get_prestige_button_rect()
        self.prestige_button.rect.x = prestige_rect.x
        self.prestige_button.rect.y = prestige_rect.y
        self.prestige_button.rect.width = prestige_rect.width
        
        shards_rect = self.layout.get_collect_shards_button_rect()
        self.collect_shards_button.rect.x = shards_rect.x
        self.collect_shards_button.rect.y = shards_rect.y
        self.collect_shards_button.rect.width = shards_rect.width
        
        self.bit_visualization.center_x = new_width // 2
        self.binary_rain.width = new_width
        self.binary_rain.height = new_height
        
        info_core_rect = self.layout.get_information_core_rect()
        self.information_core["x"] = info_core_rect.x + info_core_rect.width // 2
        self.information_core["y"] = info_core_rect.y + info_core_rect.height // 2
        self.information_core["radius"] = info_core_rect.width // 2
        
        for comp_name, comp in self.bit_grid.components.items():
            button_width = int(50 * self.layout.scale_x)
            button_height = int(18 * self.layout.scale_y)
            button_x = comp["x"] + comp["width"] - button_width - 6
            button_y = comp["y"] + 4

            if comp_name in self.component_upgrade_buttons:
                self.component_upgrade_buttons[comp_name].rect.x = button_x
                self.component_upgrade_buttons[comp_name].rect.y = button_y
                self.component_upgrade_buttons[comp_name].rect.width = button_width
                self.component_upgrade_buttons[comp_name].rect.height = button_height

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.handle_window_resize(event.w, event.h)

            if event.type == pygame.MOUSEWHEEL:
                self.hardware_scroll_panel.handle_scroll(event)
                self.upgrades_scroll_panel.handle_scroll(event)

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
                        self.showing_rebirth_confirmation = False
                        if result:
                            self.bit_grid.reset_on_rebirth()
                            self.bit_grid.upgrade_to_era(self.state.hardware_generation)
                            self.hardware_scroll_panel.scroll_to(0)
                            self.upgrades_scroll_panel.scroll_to(0)

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
                continue

            if self.showing_prestige_confirmation:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    yes_rect = pygame.Rect(
                        WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 120, 140, 50
                    )
                    no_rect = pygame.Rect(
                        WINDOW_WIDTH // 2 + 10, WINDOW_HEIGHT // 2 + 120, 140, 50
                    )

                    if yes_rect.collidepoint(mouse_pos):
                        result = self.state.perform_prestige()
                        if result:
                            self.showing_prestige_confirmation = False
                            self.bit_grid.reset_on_rebirth()
                            self.bit_grid.upgrade_to_era(0)
                            self.hardware_scroll_panel.scroll_to(0)
                            self.upgrades_scroll_panel.scroll_to(0)
                            self.create_prestige_effect()
                    elif no_rect.collidepoint(mouse_pos):
                        self.showing_prestige_confirmation = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.showing_prestige_confirmation = False
                continue

            if self.showing_settings:
                self.handle_settings_events(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.showing_settings = False
                continue

            if self.showing_tutorial:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    continue_rect = pygame.Rect(
                        WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 60, 200, 40
                    )
                    if continue_rect.collidepoint(mouse_pos):
                        self.showing_tutorial = False
                        self.tutorial_text = ""
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.showing_tutorial = False
                    self.tutorial_text = ""
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hasattr(self, 'information_core') and self.information_core:
                    core = self.information_core
                    dist = math.sqrt((mouse_pos[0] - core["x"]) ** 2 + (mouse_pos[1] - core["y"]) ** 2)
                    if dist < core["radius"]:
                        self.handle_click()
            
            if self.click_button.is_clicked(event):
                self.handle_click()

            if (
                self.hardware_panel_open
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                self.handle_generator_card_clicks(mouse_pos)

            if (
                self.upgrades_panel_open
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                self.handle_upgrade_card_clicks(mouse_pos)

            for comp_name, button in self.component_upgrade_buttons.items():
                if button.is_clicked(event):
                    self.upgrade_component(comp_name)

            if self.settings_button.is_clicked(event):
                self.showing_settings = True
            elif self.stats_button.is_clicked(event):
                self.show_statistics()

            if self.hardware_toggle.is_clicked(event):
                self.hardware_panel_open = not self.hardware_panel_open

            if self.upgrades_toggle.is_clicked(event):
                self.upgrades_panel_open = not self.upgrades_panel_open

            if self.state.can_rebirth(self.bit_grid) and self.rebirth_button.is_clicked(event):
                self.showing_rebirth_confirmation = True

            if self.state.can_prestige() and self.prestige_button.is_clicked(event):
                self.showing_prestige_confirmation = True

            if self.state.can_collect_data_shards() and self.collect_shards_button.is_clicked(event):
                shards_collected = self.state.collect_data_shards()
                if shards_collected > 0:
                    self.create_shards_collected_effect(shards_collected)

        if not self.showing_settings and not self.showing_rebirth_confirmation and not self.showing_prestige_confirmation:
            self.click_button.update(mouse_pos)
            self.settings_button.update(mouse_pos)
            self.stats_button.update(mouse_pos)

            self.hardware_toggle.update(mouse_pos)
            self.upgrades_toggle.update(mouse_pos)

            if self.hardware_panel_open:
                pass  # Generator card hover handled via rect collision

            if self.upgrades_panel_open:
                for btn in self.upgrade_card_buttons.values():
                    btn.update(mouse_pos)

            if self.state.can_rebirth(self.bit_grid):
                self.rebirth_button.update(mouse_pos)

            if self.state.can_prestige():
                self.prestige_button.update(mouse_pos)

            if self.state.can_collect_data_shards():
                self.collect_shards_button.update(mouse_pos)

    def handle_click(self):
        click_power = self.state.get_click_power()
        self.state.bits += click_power
        self.state.total_bits_earned += click_power
        self.state.total_clicks += 1

        self.last_click_time = pygame.time.get_ticks()

        self.bit_grid.add_click_effect()

        if self.state.visual_settings["particle_effects"]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.floating_texts.append(
                FloatingText(mouse_x, mouse_y, f"+{self.format_number(click_power)}")
            )

            self._add_particle(
                Particle(mouse_x, mouse_y, COLORS["matrix_green"], "click")
            )

        self.check_tutorial()

    def buy_generator(self, generator_id, quantity):
        if not self.state.is_generator_unlocked(generator_id):
            return

        cost = self.state.get_generator_cost(generator_id, quantity)

        if self.state.can_afford(cost):
            self.state.bits -= cost
            self.state.generators[generator_id]["count"] += quantity
            self.state.generators[generator_id]["total_bought"] += quantity

            self.bit_grid.add_purchase_effect()

            if self.state.visual_settings["particle_effects"]:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                particles_to_add = []
                for _ in range(4):
                    particles_to_add.append(
                        Particle(
                            mouse_x,
                            mouse_y,
                            COLORS["electric_cyan"],
                            "purchase",
                        )
                    )
                self._add_particles(particles_to_add)

    def buy_upgrade(self, upgrade_id):
        if not self.state.is_upgrade_unlocked(upgrade_id):
            return

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

            self.bit_grid.add_purchase_effect()

            if self.state.visual_settings["particle_effects"]:
                button_rect = self.upgrade_buttons[upgrade_id].rect
                button_center_x = button_rect.centerx
                button_center_y = button_rect.centery

                for _ in range(4):
                    self.particles.append(
                        Particle(
                            button_center_x,
                            button_center_y,
                            COLORS["neon_purple"],
                            "purchase",
                        )
                    )

    def handle_generator_card_clicks(self, mouse_pos):
        panel = self.hardware_scroll_panel

        all_generators = get_all_generators()
        basic_generators = GENERATORS if GENERATORS else CONFIG["GENERATORS"]
        hardware_generators = CONFIG.get("HARDWARE_GENERATORS", {})

        y_offset = -panel.get_scroll_offset()

        for gen_id, generator in all_generators.items():
            is_locked = False
            if gen_id in basic_generators:
                if not self.state.is_generator_unlocked(gen_id):
                    is_locked = True
            elif gen_id in hardware_generators:
                if not self.state.is_hardware_category_unlocked(generator.get("category", "")):
                    is_locked = True

            if is_locked:
                continue

            count = self.state.generators[gen_id]["count"]
            cost = self.state.get_generator_cost(gen_id)
            can_afford = self.state.can_afford(cost)

            card_x = panel.rect.x + 20
            card_y = panel.rect.y + 50 + y_offset + 8
            card_width = panel.rect.width - 40
            card_height = 90

            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            if card_rect.collidepoint(mouse_pos):
                button_y = card_y + card_height - 32
                btn_width = 55
                btn_height = 26
                btn_spacing = 5

                btn1_rect = pygame.Rect(
                    card_x + card_width - btn_width * 2 - btn_spacing * 2 - 10, button_y, btn_width, btn_height
                )
                if btn1_rect.collidepoint(mouse_pos) and can_afford:
                    self.buy_generator(gen_id, 10)
                    return

                btn2_rect = pygame.Rect(
                    card_x + card_width - btn_width - btn_spacing - 10, button_y, btn_width, btn_height
                )
                if btn2_rect.collidepoint(mouse_pos) and can_afford:
                    self.buy_generator(gen_id, 1)
                    return

            y_offset += card_height + 14

    def handle_upgrade_card_clicks(self, mouse_pos):
        panel = self.upgrades_scroll_panel

        all_upgrades = get_all_upgrades()
        basic_upgrades = UPGRADES if UPGRADES else CONFIG["UPGRADES"]
        hardware_upgrades = CONFIG.get("HARDWARE_UPGRADES", {})

        y_offset = -panel.get_scroll_offset()

        for upgrade_id, upgrade in all_upgrades.items():
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

            card_x = panel.rect.x + 20
            card_y = panel.rect.y + 50 + y_offset + 8
            card_width = panel.rect.width - 40
            card_height = 85

            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            if card_rect.collidepoint(mouse_pos):
                if level < upgrade["max_level"]:
                    btn_key = f"{upgrade_id}_btn"
                    if btn_key in self.upgrade_card_buttons:
                        btn = self.upgrade_card_buttons[btn_key]
                        btn.rect.x = card_x + card_width - 80
                        btn.rect.y = card_y + card_height - 25
                        
                        if btn.rect.collidepoint(mouse_pos) and can_afford:
                            self.buy_upgrade(upgrade_id)
                            return

            y_offset += card_height + 14

    def upgrade_component(self, comp_name):
        from constants import COMPONENT_BASE_COSTS
        
        comp = self.bit_grid.components[comp_name]

        cost_multiplier = 2.5 ** comp["level"]
        cost = int(COMPONENT_BASE_COSTS.get(comp_name, 100) * cost_multiplier)

        if self.state.can_afford(cost) and comp["unlocked"] and comp["level"] < 10:
            self.state.bits -= cost
            self.bit_grid.upgrade_component(comp_name)

            self.bit_grid.add_purchase_effect()

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
        if self.state.visual_settings["binary_rain"]:
            self.binary_rain.update(dt)
        
        if self.state.era == "compression":
            self.compression_panel.update(dt)
            self.compression_meter.update(dt)
            self.token_display.update(dt)
            self.compression_progress.update(dt)

        if hasattr(self, 'motherboard_notification'):
            self.motherboard_notification.update(dt)

        production_rate = self.state.get_production_rate()
        production = production_rate * dt

        if not hasattr(self, "production_accumulator"):
            self.production_accumulator = 0.0

        self.production_accumulator += production
        production_int = int(self.production_accumulator)

        if production_int > 0:
            self.state.bits += production_int
            self.state.total_bits_earned += production_int
            self.production_accumulator -= production_int

        for gen_id, generator in CONFIG["GENERATORS"].items():
            if "unlock_threshold" in generator:
                if (
                    gen_id not in self.state.unlocked_generators
                    and self.state.total_bits_earned >= generator["unlock_threshold"]
                ):
                    self.state.unlocked_generators.append(gen_id)

        if self.state.visual_settings["particle_effects"]:
            self.particles = [p for p in self.particles if p.lifetime > 0]
            for particle in self.particles:
                particle.update(dt)

            self.floating_texts = [t for t in self.floating_texts if t.lifetime > 0]
            for text in self.floating_texts:
                text.update(dt)
        else:
            self.particles.clear()
            self.floating_texts.clear()

        current_time = pygame.time.get_ticks()
        if current_time - self.last_auto_save > CONFIG["AUTO_SAVE_INTERVAL"]:
            self.save_game()
            self.last_auto_save = current_time

    def draw(self):
        self._draw_background()

        draw_circuit_background(self.screen, self.current_width, self.current_height)

        if self.state.visual_settings["binary_rain"]:
            self.binary_rain.draw(self.screen)

        if not self.showing_settings and not self.showing_rebirth_confirmation and not self.showing_prestige_confirmation:
            if self.state.visual_settings["particle_effects"]:
                self.bit_visualization.draw(self.screen, self.state.bits)

            draw_top_bar(
                self.screen, self.current_width, self.current_height,
                self.base_width, self.base_height, self.state,
                self.bit_counter_font, self.large_font, self.small_font, self.medium_font, COLORS
            )

            if self.state.prestige_count > 0:
                prestige_text = f"🔧 {self.state.prestige_currency} Quantum Fragments (+{int((self.state.get_prestige_bonus()-1)*100)}% prod)"
                prestige_surface = self.small_font.render(prestige_text, True, COLORS["quantum_violet"])
                prestige_rect = prestige_surface.get_rect(center=(self.current_width // 2, 55))
                self.screen.blit(prestige_surface, prestige_rect)

            if self.state.can_prestige():
                self.prestige_button.draw(self.screen)

            if self.state.can_collect_data_shards():
                self.collect_shards_button.draw(self.screen)

            draw_accumulator(
                self.screen, self.state, self.bit_grid, self.compression_panel,
                self.compression_meter, self.token_display, self.compression_progress,
                self.current_width, self.current_height, self.base_width, self.base_height,
                self.monospace_font, self.medium_font, self.small_font, COLORS
            )

            self._draw_panels()

            draw_rebirth_bar(
                self.screen, self.state, self.bit_grid, self.rebirth_button,
                self.current_width, self.current_height, self.base_width, self.base_height,
                self.monospace_font, COLORS
            )

            if hasattr(self, 'motherboard_notification'):
                self.motherboard_notification.draw(self.screen, self.current_width, self.current_height)

            self.click_button.draw(self.screen)

            draw_effects(self.screen, self.particles, self.floating_texts)
            draw_tutorial(
                self.screen, self.showing_tutorial, self.tutorial_text,
                self.current_width, self.current_height, self.medium_font, self.small_font, COLORS
            )

            self.settings_button.draw(self.screen)
            self.stats_button.draw(self.screen)

            draw_tooltips(
                self.screen, pygame.mouse.get_pos(), self.hardware_panel_open,
                self.upgrades_panel_open, self.hardware_scroll_panel,
                self.upgrades_scroll_panel, self.state, CONFIG,
                self.small_font, self.tiny_font, self.current_width, self.current_height, COLORS
            )

            if self.state.visual_settings["crt_effects"]:
                draw_crt_overlay(self.screen, self.current_width, self.current_height)
        elif self.showing_rebirth_confirmation:
            draw_rebirth_confirmation(
                self.screen, self.showing_rebirth_confirmation, self.state,
                self.bit_grid, WINDOW_WIDTH, WINDOW_HEIGHT,
                self.large_font, self.medium_font, self.small_font, COLORS
            )
        elif self.showing_prestige_confirmation:
            draw_prestige_confirmation(
                self.screen, self.showing_prestige_confirmation, self.state,
                WINDOW_WIDTH, WINDOW_HEIGHT,
                self.large_font, self.medium_font, self.small_font, COLORS
            )
        else:
            draw_settings_page(
                self.screen, self.current_width, self.current_height,
                self.base_width, self.base_height, self.state.visual_settings,
                self.high_contrast_mode, self.reduced_motion_mode, self.visual_quality,
                self.large_font, self.medium_font, self.small_font, self.tiny_font, COLORS
            )

    def _draw_background(self):
        if (self._gradient_surface is None or 
            self._last_gradient_size != (self.current_width, self.current_height)):
            self._gradient_surface = pygame.Surface((self.current_width, self.current_height))
            for i in range(self.current_height):
                color_ratio = i / self.current_height
                color = (
                    int(COLORS["deep_space_blue"][0] + (COLORS["deep_space_gradient_end"][0] - COLORS["deep_space_blue"][0]) * color_ratio),
                    int(COLORS["deep_space_blue"][1] + (COLORS["deep_space_gradient_end"][1] - COLORS["deep_space_blue"][1]) * color_ratio),
                    int(COLORS["deep_space_blue"][2] + (COLORS["deep_space_gradient_end"][2] - COLORS["deep_space_blue"][2]) * color_ratio),
                )
                pygame.draw.line(self._gradient_surface, color, (0, i), (self.current_width, i))
            self._last_gradient_size = (self.current_width, self.current_height)
        self.screen.blit(self._gradient_surface, (0, 0))

    def _draw_panels(self):
        self._draw_hardware_panel()
        self._draw_upgrades_panel()

    def _draw_hardware_panel(self):
        if self.hardware_panel_open:
            self.hardware_toggle.text = UI_ARROW_DOWN + " HARDWARE"
        else:
            self.hardware_toggle.text = UI_ARROW_RIGHT + " HARDWARE"

        draw_panel_toggle(self.screen, self.hardware_toggle, self.hardware_panel_open, self.small_font)

        if not self.hardware_panel_open:
            return

        panel = self.hardware_scroll_panel
        draw_panel_with_integrated_title(self.screen, panel, COLORS["electric_cyan"], self.medium_font, self.tiny_font)

        scroll_surface = pygame.Surface((panel.rect.width - 20, panel.rect.height - 60))
        scroll_surface.fill((18, 20, 28))

        y_offset = -panel.get_scroll_offset()

        all_generators = get_all_generators()
        basic_generators = GENERATORS if GENERATORS else CONFIG["GENERATORS"]
        hardware_generators = CONFIG.get("HARDWARE_GENERATORS", {})

        for gen_id, generator in all_generators.items():
            if gen_id in basic_generators:
                if not self.state.is_generator_unlocked(gen_id):
                    continue
            elif gen_id in hardware_generators:
                if not self.state.is_hardware_category_unlocked(generator["category"]):
                    continue

            count = self.state.generators[gen_id]["count"]
            cost = self.state.get_generator_cost(gen_id)
            if gen_id in CONFIG["GENERATORS"]:
                gen_cfg = CONFIG["GENERATORS"][gen_id]
                production = count * gen_cfg["base_production"]
            elif gen_id in CONFIG.get("HARDWARE_GENERATORS", {}):
                gen_cfg = CONFIG["HARDWARE_GENERATORS"][gen_id]
                category = gen_cfg["category"]
                if self.state.is_hardware_category_unlocked(category):
                    category_multiplier = self.state.get_category_multiplier(category)
                    production = count * gen_cfg["base_production"] * category_multiplier
                else:
                    production = 0
            else:
                production = 0

            card_height = 90
            card_y = y_offset + 8

            cost_x10 = self.state.get_generator_cost(gen_id, 10)

            if card_y + card_height > -20 and card_y < scroll_surface.get_height():
                draw_generator_card(
                    scroll_surface, 10, card_y, panel.rect.width - 40, card_height,
                    generator, gen_id, count, cost, production, 
                    self.state.can_afford(cost), self.state.can_afford(cost_x10),
                    self.state, CONFIG, self.medium_font, self.small_font, self.tiny_font
                )

            y_offset += card_height + 14

        panel.set_content_height(y_offset + panel.get_scroll_offset() + 20)
        self.screen.blit(scroll_surface, (panel.rect.x + 10, panel.rect.y + 50))

        if panel.content_height > panel.rect.height - 60:
            draw_scrollbar(self.screen, panel)

    def _draw_upgrades_panel(self):
        if self.upgrades_panel_open:
            self.upgrades_toggle.text = UI_ARROW_DOWN + " UPGRADES"
        else:
            self.upgrades_toggle.text = UI_ARROW_RIGHT + " UPGRADES"

        draw_panel_toggle(self.screen, self.upgrades_toggle, self.upgrades_panel_open, self.small_font)

        if not self.upgrades_panel_open:
            return

        panel = self.upgrades_scroll_panel
        draw_panel_with_integrated_title(self.screen, panel, COLORS["neon_purple"], self.medium_font, self.tiny_font)

        scroll_surface = pygame.Surface((panel.rect.width - 20, panel.rect.height - 60))
        scroll_surface.fill((18, 20, 28))

        y_offset = -panel.get_scroll_offset()

        all_upgrades = get_all_upgrades()
        basic_upgrades = UPGRADES if UPGRADES else CONFIG["UPGRADES"]
        hardware_upgrades = CONFIG.get("HARDWARE_UPGRADES", {})

        for upgrade_id, upgrade in all_upgrades.items():
            if upgrade_id in basic_upgrades:
                if not self.state.is_upgrade_unlocked(upgrade_id):
                    continue
            elif upgrade_id in hardware_upgrades:
                if not self.state.is_hardware_category_unlocked(upgrade["category"]):
                    continue

            level = self.state.upgrades[upgrade_id]["level"]
            cost = self.state.get_upgrade_cost(upgrade_id)
            can_afford = self.state.can_afford(cost) and level < upgrade["max_level"]

            card_height = 85
            card_y = y_offset + 8

            if card_y + card_height > -20 and card_y < scroll_surface.get_height():
                draw_upgrade_card(
                    scroll_surface, 10, card_y, panel.rect.width - 40, card_height,
                    upgrade, upgrade_id, level, cost, can_afford,
                    self.upgrade_card_buttons, self.medium_font, self.small_font, self.tiny_font, COLORS,
                    panel.rect
                )

            y_offset += card_height + 14

        panel.set_content_height(y_offset + panel.get_scroll_offset() + 20)
        self.screen.blit(scroll_surface, (panel.rect.x + 10, panel.rect.y + 50))

        if panel.content_height > panel.rect.height - 60:
            draw_scrollbar(self.screen, panel)

        for comp_name, button in self.component_upgrade_buttons.items():
            comp = self.bit_grid.components[comp_name]

            button.rect.x = comp["x"] + comp["width"] - button.rect.width - 6
            button.rect.y = comp["y"] + 4

            if comp["unlocked"]:
                from constants import COMPONENT_BASE_COSTS
                cost_multiplier = 2.5 ** comp["level"]
                cost = int(COMPONENT_BASE_COSTS.get(comp_name, 100) * cost_multiplier)
                can_afford = self.state.can_afford(cost) and comp["level"] < 10

                button.is_enabled = can_afford
                button.draw(self.screen)

                cost_text = self.tiny_font.render(
                    self.format_number(cost), True, (200, 200, 210)
                )
                cost_rect = cost_text.get_rect(
                    midtop=(button.rect.centerx, button.rect.bottom + 2)
                )
                self.screen.blit(cost_text, cost_rect)
            else:
                button.is_enabled = False

    def handle_settings_events(self, event):
        mouse_pos = pygame.mouse.get_pos()

        crt_toggle_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 250, 400, 40)
        rain_toggle_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 300, 400, 40)
        particle_toggle_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 350, 400, 40)
        high_contrast_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 400, 400, 40)
        reduced_motion_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 450, 400, 40)
        quality_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 500, 400, 40)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if crt_toggle_rect.collidepoint(mouse_pos):
                self.state.visual_settings["crt_effects"] = not self.state.visual_settings["crt_effects"]
            elif rain_toggle_rect.collidepoint(mouse_pos):
                self.state.visual_settings["binary_rain"] = not self.state.visual_settings["binary_rain"]
            elif particle_toggle_rect.collidepoint(mouse_pos):
                self.state.visual_settings["particle_effects"] = not self.state.visual_settings["particle_effects"]
            elif high_contrast_rect.collidepoint(mouse_pos):
                self.high_contrast_mode = not self.high_contrast_mode
                self._update_button_accessibility()
            elif reduced_motion_rect.collidepoint(mouse_pos):
                self.reduced_motion_mode = not self.reduced_motion_mode
                quality = "low" if self.reduced_motion_mode else self.visual_quality
                self.bit_visualization.set_quality_level(quality)
            elif quality_rect.collidepoint(mouse_pos):
                quality_levels = ["high", "medium", "low"]
                current_index = quality_levels.index(self.visual_quality)
                self.visual_quality = quality_levels[(current_index + 1) % len(quality_levels)]
                self.bit_visualization.set_quality_level(self.visual_quality)

    def _update_button_accessibility(self):
        self.hardware_toggle.high_contrast = self.high_contrast_mode
        self.upgrades_toggle.high_contrast = self.high_contrast_mode
        self.click_button.high_contrast = self.high_contrast_mode
        self.settings_button.high_contrast = self.high_contrast_mode
        self.stats_button.high_contrast = self.high_contrast_mode

        for button_list in [
            self.upgrade_buttons,
            self.component_upgrade_buttons,
        ]:
            if isinstance(button_list, dict):
                for button in button_list.values():
                    if isinstance(button, Button):
                        button.high_contrast = self.high_contrast_mode
                    elif isinstance(button, dict):
                        for sub_button in button.values():
                            if isinstance(sub_button, Button):
                                sub_button.high_contrast = self.high_contrast_mode

    def show_statistics(self):
        print(f"""
=== STATISTICS ===
Time Played: {(pygame.time.get_ticks() - self.state.start_time) // 1000}s
Total Bits Earned: {self.format_number(self.state.total_bits_earned)}
Current Production: {self.format_number(self.state.get_production_rate())} b/s
Total Clicks: {self.state.total_clicks}
================
        """)

    def create_rebirth_effect(self):
        center_x = WINDOW_WIDTH // 2
        center_y = 200

        particles_to_add = []
        for _ in range(50):
            color = random.choice(
                [COLORS["electric_cyan"], COLORS["neon_purple"], COLORS["gold"]]
            )
            particles_to_add.append(Particle(center_x, center_y, color, "burst"))
        self._add_particles(particles_to_add)

        if (
            hasattr(self.state, "data_shards")
            and self.state.data_shards > 0
        ):
            current_tokens = self.state.data_shards
            self.floating_texts.append(
                FloatingText(
                    center_x,
                    center_y - 50,
                    f"+{current_tokens} 💎 SHARDS!",
                    COLORS["gold"],
                )
            )
            particles_to_add = []
            for _ in range(10):
                particle_color = random.choice(
                    [COLORS["electric_cyan"], COLORS["neon_purple"], COLORS["gold"]]
                )
                particles_to_add.append(
                    Particle(center_x, center_y, particle_color, "burst")
                )
            self._add_particles(particles_to_add)

    def create_prestige_effect(self):
        center_x = WINDOW_WIDTH // 2
        center_y = 200

        particles_to_add = []
        for _ in range(150):
            color = random.choice(
                [COLORS["quantum_violet"], COLORS["gold"], COLORS["electric_cyan"], COLORS["neon_purple"]]
            )
            particles_to_add.append(Particle(center_x, center_y, color, "burst"))
        self._add_particles(particles_to_add)

        currency_earned = self.state.get_prestige_currency_earned()
        self.floating_texts.append(
            FloatingText(
                center_x,
                center_y - 50,
                f"+{currency_earned} 💎 QUANTUM FRAGMENTS!",
                COLORS["quantum_violet"],
            )
        )

        bonus_pct = int((self.state.get_prestige_bonus() - 1) * 100)
        self.floating_texts.append(
            FloatingText(
                center_x,
                center_y - 20,
                f"MOTHERBOARD UPGRADED: +{bonus_pct}% production!",
                COLORS["gold"],
            )
        )

        if hasattr(self, 'motherboard_notification'):
            self.motherboard_notification.show(0)

    def create_shards_collected_effect(self, shards):
        center_x = WINDOW_WIDTH // 2
        center_y = 200

        for _ in range(30):
            color = COLORS["gold"]
            self.particles.append(Particle(center_x, center_y, color, "burst"))

        self.floating_texts.append(
            FloatingText(
                center_x,
                center_y - 50,
                f"+{shards} 💎 DATA SHARDS!",
                COLORS["gold"],
            )
        )

    def create_hardware_advancement_effect(self):
        center_x = self.current_width // 2
        center_y = int(250 * (self.current_height / self.base_height))

        particles_to_add = []
        for _ in range(100):
            color = random.choice(
                [
                    COLORS["electric_cyan"],
                    COLORS["neon_purple"],
                    COLORS["gold"],
                    COLORS["signal_orange"],
                ]
            )
            particles_to_add.append(Particle(center_x, center_y, color, "burst"))
        self._add_particles(particles_to_add)

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

        if hasattr(self, 'motherboard_notification'):
            self.motherboard_notification.show(self.state.hardware_generation)

    def check_tutorial(self):
        if self.state.has_seen_tutorial or self.state.total_rebirths > 0:
            return

        step = self.state.tutorial_step

        if step == 0 and self.state.total_bits_earned >= 10:
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
            center_x = WINDOW_WIDTH // 2
            center_y = 250
            color = COLORS["matrix_green"]
            self.particles.append(Particle(center_x, center_y, color, "burst"))

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
                "total_rebirths": self.state.total_rebirths,
                "total_lifetime_bits": self.state.total_lifetime_bits,
                "hardware_generation": self.state.hardware_generation,
                "unlocked_hardware_categories": self.state.unlocked_hardware_categories,
                "era": self.state.era,
                "data_shards": self.state.data_shards,
                "total_data_shards": self.state.total_data_shards,
                "last_collect_bits": self.state.last_collect_bits,
                "compressed_bits": self.state.compressed_bits,
                "total_compressed_bits": self.state.total_compressed_bits,
                "overhead_rate": self.state.overhead_rate,
                "efficiency": self.state.efficiency,
                "prestige_currency": self.state.prestige_currency,
                "total_prestige_currency": self.state.total_prestige_currency,
                "prestige_count": self.state.prestige_count,
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
            self.showing_tutorial = True
            self.tutorial_text = "Welcome to BIT BY BIT!\n\nYou are about to discover\nfundamental nature of information.\n\nClick accumulator to generate\nyour first bits."
            return

        try:
            with open(CONFIG["SAVE_FILE"], "r") as f:
                save_data = json.load(f)

            state_data = save_data["state"]
            self.state.bits = state_data.get("bits", 0)
            self.state.total_bits_earned = state_data.get("total_bits_earned", 0)
            self.state.total_clicks = state_data.get("total_clicks", 0)
            self.state.start_time = state_data.get("start_time", pygame.time.get_ticks())
            self.state.total_play_time = state_data.get("total_play_time", 0)
            
            self.state.total_rebirths = state_data.get("total_rebirths", 0)
            self.state.total_lifetime_bits = state_data.get("total_lifetime_bits", 0)
            self.state.hardware_generation = state_data.get("hardware_generation", 0)
            self.state.unlocked_hardware_categories = state_data.get("unlocked_hardware_categories", ["cpu"])
            
            self.state.era = state_data.get("era", "entropy")
            self.state.data_shards = state_data.get("data_shards", 0)
            self.state.total_data_shards = state_data.get("total_data_shards", 0)
            self.state.last_collect_bits = state_data.get("last_collect_bits", 0)
            self.state.compressed_bits = state_data.get("compressed_bits", 0)
            self.state.total_compressed_bits = state_data.get("total_compressed_bits", 0)
            self.state.overhead_rate = state_data.get("overhead_rate", 0)
            self.state.efficiency = state_data.get("efficiency", 1.0)
            self.state.prestige_currency = state_data.get("prestige_currency", 0)
            self.state.total_prestige_currency = state_data.get("total_prestige_currency", 0)
            self.state.prestige_count = state_data.get("prestige_count", 0)
            
            if "compression_tokens" in state_data:
                self.state.data_shards = state_data.get("compression_tokens", 0)
                self.state.total_data_shards = state_data.get("total_compression_tokens", 0)
            
            self.state.generators = state_data.get("generators", self.state.generators)
            self.state.unlocked_generators = state_data.get("unlocked_generators", ["rng"])
            self.state.upgrades = state_data.get("upgrades", self.state.upgrades)
            self.state.tutorial_step = state_data.get("tutorial_step", 0)
            self.state.has_seen_tutorial = state_data.get("has_seen_tutorial", False)
            self.state.visual_settings = state_data.get("visual_settings", self.state.visual_settings)

            for gen_id in CONFIG["GENERATORS"]:
                if gen_id not in self.state.generators:
                    self.state.generators[gen_id] = {"count": 0, "total_bought": 0}
            
            if "HARDWARE_GENERATORS" in CONFIG:
                for gen_id in CONFIG["HARDWARE_GENERATORS"]:
                    if gen_id not in self.state.generators:
                        self.state.generators[gen_id] = {"count": 0, "total_bought": 0}
            
            for upgrade_id in CONFIG["UPGRADES"]:
                if upgrade_id not in self.state.upgrades:
                    self.state.upgrades[upgrade_id] = {"level": 0}
            
            if "HARDWARE_UPGRADES" in CONFIG:
                for upgrade_id in CONFIG["HARDWARE_UPGRADES"]:
                    if upgrade_id not in self.state.upgrades:
                        self.state.upgrades[upgrade_id] = {"level": 0}

            if save_data.get("timestamp"):
                offline_time = min(
                    (pygame.time.get_ticks() - save_data["timestamp"]) / 1000, 86400
                )
                offline_production = (
                    self.state.get_production_rate() * offline_time * 0.75
                )

                if offline_production > 0:
                    self.state.bits += offline_production
                    self.state.total_bits_earned += offline_production
                    print(f"Offline progress: {self.format_number(offline_production)} bits")

        except Exception as e:
            print(f"Failed to load game: {e}")

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.update(dt)
            self.draw()

            pygame.display.flip()

        self.save_game()
        pygame.quit()
        sys.exit()
