"""
Bit grid visualization for Bit by Bit Game
Motherboard-style tech tree with horizontal flow: CPU → BUS → RAM/GPU/STORAGE
"""

import pygame
import math
import random
from constants import COLORS
from visual_effects import BitDot


class MotherboardBitGrid:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.components = {
            "CPU": {
                "col": 0,
                "row": 0,
                "row_span": 2,
                "bits": 64,
                "unlocked": True,
                "level": 1,
                "color": (200, 50, 50),
                "name": "CPU",
                "description": "64-bit Registers",
            },
            "BUS": {
                "col": 1,
                "row": 0,
                "row_span": 2,
                "bits": 16,
                "unlocked": True,
                "level": 1,
                "color": (100, 120, 180),
                "name": "BUS",
                "description": "16-bit Address Bus",
            },
            "RAM": {
                "col": 2,
                "row": 0,
                "row_span": 1,
                "bits": 1024,
                "unlocked": False,
                "level": 0,
                "color": (50, 200, 50),
                "name": "RAM",
                "description": "1KB Core Memory",
            },
            "GPU": {
                "col": 2,
                "row": 1,
                "row_span": 1,
                "bits": 512,
                "unlocked": False,
                "level": 0,
                "color": (200, 50, 200),
                "name": "GPU",
                "description": "512B Video Memory",
            },
            "STORAGE": {
                "col": 3,
                "row": 0,
                "row_span": 2,
                "bits": 8192,
                "unlocked": False,
                "level": 0,
                "color": (50, 120, 220),
                "name": "STORAGE",
                "description": "8KB Disk Drive",
            },
        }

        self._connections = [
            ("CPU", "BUS"),
            ("BUS", "RAM"),
            ("BUS", "GPU"),
            ("RAM", "STORAGE"),
            ("GPU", "STORAGE"),
        ]

        self._num_cols = 4
        self._num_rows = 2

        for comp in self.components.values():
            total_bits = comp["bits"]
            comp["bit_states"] = [0] * total_bits
            comp["x"] = 0
            comp["y"] = 0
            comp["width"] = 0
            comp["height"] = 0

        self._layout_components()

        self.total_bits_earned = 0
        self.last_bits_count = 0
        self.last_rebirth_progress = 0

        self.colors = {
            0: (40, 40, 40),
            1: (50, 200, 50),
            "transitioning": (100, 150, 100),
            "component_border": (120, 120, 140),
            "locked": (20, 20, 28),
            "connection": (55, 60, 80),
        }

        self._label_font = None
        self._desc_font = None
        self._lock_font = None

        self._text_cache = {}
        self._cache_version = 0

    def _get_fonts(self):
        if self._label_font is None:
            scale = max(0.6, min(1.5, self.height / 300))
            label_size = max(12, int(15 * scale))
            desc_size = max(10, int(12 * scale))
            lock_size = max(10, int(12 * scale))
            try:
                self._label_font = pygame.font.SysFont("Consolas", label_size, bold=True)
                self._desc_font = pygame.font.SysFont("Consolas", desc_size)
                self._lock_font = pygame.font.SysFont("Consolas", lock_size)
            except pygame.error:
                self._label_font = pygame.font.Font(None, label_size + 4)
                self._desc_font = pygame.font.Font(None, desc_size + 4)
                self._lock_font = pygame.font.Font(None, lock_size + 4)
        return self._label_font, self._desc_font, self._lock_font

    def _layout_components(self):
        scale = max(0.6, min(1.5, self.height / 300))
        pad_x = int(10 * scale)
        pad_y = int(8 * scale)
        gap_x = int(12 * scale)
        gap_y = int(8 * scale)

        usable_w = self.width - pad_x * 2 - gap_x * (self._num_cols - 1)
        usable_h = self.height - pad_y * 2 - gap_y * (self._num_rows - 1)
        cell_w = usable_w // self._num_cols
        cell_h = usable_h // self._num_rows

        for comp in self.components.values():
            col = comp["col"]
            row = comp["row"]
            row_span = comp["row_span"]

            comp["x"] = self.x + pad_x + col * (cell_w + gap_x)
            comp["y"] = self.y + pad_y + row * (cell_h + gap_y)
            comp["width"] = cell_w
            comp["height"] = cell_h * row_span + gap_y * (row_span - 1)

    def update_dimensions(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self._label_font = None
        self._layout_components()

    def update(self, bits, total_bits_earned, rebirth_threshold, hardware_generation=0, dt=1/60):
        self.total_bits_earned = total_bits_earned
        self.last_rebirth_progress = min(1.0, total_bits_earned / rebirth_threshold)
        self.hardware_generation = hardware_generation
        self.dt = dt
        self._update_component_unlocks()
        self._update_bits_to_progress()
        self.last_bits_count = bits

    def _update_component_unlocks(self):
        progress = self.last_rebirth_progress
        hw_gen = getattr(self, "hardware_generation", 0)

        self.components["CPU"]["unlocked"] = True
        self.components["BUS"]["unlocked"] = True

        unlock_thresholds = {
            "RAM": {0: 0.1, 1: 0.05, 2: 0.03, 3: 0.0},
            "STORAGE": {1: 0.05, 2: 0.03, 3: 0.0},
            "GPU": {2: 0.03, 3: 0.0},
        }

        for comp_name, thresholds in unlock_thresholds.items():
            threshold = thresholds.get(hw_gen, 1.0)
            if progress >= threshold:
                self.components[comp_name]["unlocked"] = True
            elif hw_gen < min(thresholds.keys()):
                self.components[comp_name]["unlocked"] = False

    def _get_total_capacity(self):
        total_capacity = 0
        for comp in self.components.values():
            if comp["unlocked"]:
                total_capacity += comp["bits"]
        return total_capacity

    def _get_current_filled_bits(self):
        filled_bits = 0
        for comp in self.components.values():
            if comp["unlocked"]:
                filled_bits += sum(comp["bit_states"])
        return filled_bits

    def _are_all_unlocked_components_full(self):
        for comp in self.components.values():
            if comp["unlocked"]:
                if not all(comp["bit_states"]):
                    return False
        return True

    def _update_bits_to_progress(self):
        if self._are_all_unlocked_components_full():
            return

        total_capacity = self._get_total_capacity()
        if total_capacity == 0:
            return

        fill_percentage = min(1.0, self.last_rebirth_progress)
        target_filled_bits = int(total_capacity * fill_percentage)
        current_filled_bits = self._get_current_filled_bits()

        if target_filled_bits > current_filled_bits:
            bits_to_add = target_filled_bits - current_filled_bits
            self._distribute_bits(bits_to_add)

    def _distribute_bits(self, bits_to_add):
        if bits_to_add <= 0:
            return

        unlocked_components = [
            (name, comp) for name, comp in self.components.items() if comp["unlocked"]
        ]
        if not unlocked_components:
            return

        bits_added = 0
        while bits_added < bits_to_add:
            best_comp = None
            best_ratio = 1.0

            for comp_name, comp in unlocked_components:
                filled = sum(comp["bit_states"])
                total = comp["bits"]
                ratio = filled / total if total > 0 else 0
                if ratio < best_ratio:
                    best_ratio = ratio
                    best_comp = (comp_name, comp)

            if best_comp:
                _, comp = best_comp
                found_zero = False
                for i, val in enumerate(comp["bit_states"]):
                    if val == 0:
                        comp["bit_states"][i] = 1
                        bits_added += 1
                        found_zero = True
                        break
                if not found_zero:
                    break

    def draw(self, screen):
        self._draw_connections(screen)
        for comp_name, comp in self.components.items():
            self._draw_component(screen, comp_name, comp)

    def _draw_connections(self, screen):
        time_ms = pygame.time.get_ticks()

        for src_name, dst_name in self._connections:
            src = self.components[src_name]
            dst = self.components[dst_name]

            both_unlocked = src["unlocked"] and dst["unlocked"]
            either_unlocked = src["unlocked"] or dst["unlocked"]

            if not either_unlocked:
                continue

            src_cx = src["x"] + src["width"]
            src_cy = src["y"] + src["height"] // 2
            dst_cx = dst["x"]
            dst_cy = dst["y"] + dst["height"] // 2

            if both_unlocked:
                base_color = (70, 80, 110)
                pulse = abs(math.sin(time_ms * 0.003)) * 0.3 + 0.7
                color = tuple(int(c * pulse) for c in base_color)
                width = 2
            else:
                color = (35, 35, 50)
                width = 1

            mid_x = (src_cx + dst_cx) // 2
            pygame.draw.line(screen, color, (src_cx, src_cy), (mid_x, src_cy), width)
            pygame.draw.line(screen, color, (mid_x, src_cy), (mid_x, dst_cy), width)
            pygame.draw.line(screen, color, (mid_x, dst_cy), (dst_cx, dst_cy), width)

            if both_unlocked:
                dot_offset = (time_ms // 8) % 40
                total_dist = abs(mid_x - src_cx) + abs(dst_cy - src_cy) + abs(dst_cx - mid_x)
                if total_dist > 0:
                    t = (dot_offset / 40.0)
                    seg1 = abs(mid_x - src_cx)
                    seg2 = abs(dst_cy - src_cy)
                    pos_along = t * total_dist
                    if pos_along < seg1:
                        dx = src_cx + (mid_x - src_cx) * (pos_along / seg1)
                        dy = src_cy
                    elif pos_along < seg1 + seg2:
                        dx = mid_x
                        dy = src_cy + (dst_cy - src_cy) * ((pos_along - seg1) / seg2) if seg2 > 0 else src_cy
                    else:
                        frac = (pos_along - seg1 - seg2) / (total_dist - seg1 - seg2) if (total_dist - seg1 - seg2) > 0 else 0
                        dx = mid_x + (dst_cx - mid_x) * frac
                        dy = dst_cy
                    pygame.draw.circle(screen, COLORS.get("electric_cyan", (0, 200, 255)), (int(dx), int(dy)), 2)

    def _draw_component(self, screen, comp_name, comp):
        label_font, desc_font, lock_font = self._get_fonts()
        x, y, w, h = comp["x"], comp["y"], comp["width"], comp["height"]
        time_ms = pygame.time.get_ticks()

        cache_key = (comp_name, comp.get("level"), comp.get("unlocked"), comp.get("bits", 0))

        if comp["unlocked"]:
            bg_color = tuple(max(0, c // 6) for c in comp["color"])
            border_color = comp["color"]

            pulse = abs(math.sin(time_ms * 0.002)) * 0.15 + 0.85
            border_draw = tuple(int(c * pulse) for c in border_color)

            pygame.draw.rect(screen, bg_color, (x, y, w, h), border_radius=6)
            pygame.draw.rect(screen, border_draw, (x, y, w, h), 2, border_radius=6)

            label_cache_key = ("label", cache_key)
            if label_cache_key not in self._text_cache:
                self._text_cache[label_cache_key] = label_font.render(
                    f"{comp['name']} Lv.{comp['level']}", True, (230, 230, 240)
                )
            screen.blit(self._text_cache[label_cache_key], (x + 8, y + 6))

            desc_cache_key = ("desc", comp_name, comp["description"])
            if desc_cache_key not in self._text_cache:
                self._text_cache[desc_cache_key] = desc_font.render(comp["description"], True, (140, 140, 160))
            screen.blit(self._text_cache[desc_cache_key], (x + 8, y + 24))

            self._draw_component_progress(screen, comp)
        else:
            pygame.draw.rect(screen, (16, 16, 24), (x, y, w, h), border_radius=6)
            pygame.draw.rect(screen, (40, 40, 55), (x, y, w, h), 1, border_radius=6)

            lock_icon_cache = ("lock_icon", comp_name)
            if lock_icon_cache not in self._text_cache:
                self._text_cache[lock_icon_cache] = lock_font.render("🔒", True, (50, 50, 65))
            lock_icon = self._text_cache[lock_icon_cache]
            icon_rect = lock_icon.get_rect(center=(x + w // 2, y + h // 2 - 8))
            screen.blit(lock_icon, icon_rect)

            name_cache = ("lock_name", comp_name)
            if name_cache not in self._text_cache:
                self._text_cache[name_cache] = lock_font.render(comp["name"], True, (50, 50, 65))
            name_text = self._text_cache[name_cache]
            name_rect = name_text.get_rect(center=(x + w // 2, y + h // 2 + 10))
            screen.blit(name_text, name_rect)

    def _draw_component_progress(self, screen, comp):
        progress = min(comp["level"] / 10.0, 1.0)

        bar_x = comp["x"] + 8
        bar_y = comp["y"] + comp["height"] - 14
        bar_width = comp["width"] - 16
        bar_height = 6

        pygame.draw.rect(screen, (25, 25, 35), (bar_x, bar_y, bar_width, bar_height), border_radius=3)

        if progress > 0:
            fill_width = int(bar_width * progress)
            pygame.draw.rect(screen, comp["color"], (bar_x, bar_y, fill_width, bar_height), border_radius=3)

    def _draw_component_bits(self, screen, comp):
        total_bits = comp["bits"]

        if comp["width"] <= 30 or comp["height"] <= 50:
            return

        border_thickness = 6
        padding = 10
        available_width = comp["width"] - border_thickness - padding * 2
        available_height = comp["height"] - border_thickness - padding * 2

        min_bit_size = 3
        max_bit_size = 12

        if total_bits == 0:
            total_bits = 1
        ideal_bit_size = min(
            max_bit_size,
            int(math.sqrt((available_width * available_height) / total_bits))
        )
        bit_size = max(min_bit_size, ideal_bit_size)

        gap = 1
        total_bit_cell = bit_size + gap

        grid_cols = max(1, available_width // total_bit_cell)
        grid_rows = max(1, (total_bits + grid_cols - 1) // grid_cols)

        if grid_rows * total_bit_cell > available_height:
            bit_size = max(min_bit_size, (available_height // grid_rows) - gap)
            total_bit_cell = bit_size + gap

        border_thickness = 3
        padding = 10
        start_x = comp["x"] + border_thickness + padding
        start_y = comp["y"] + border_thickness + padding

        total_bits_to_draw = min(total_bits, grid_cols * grid_rows)

        for bit_idx in range(total_bits_to_draw):
            row = bit_idx // grid_cols
            col = bit_idx % grid_cols

            bit_x = start_x + col * total_bit_cell
            bit_y = start_y + row * total_bit_cell

            max_y = comp["y"] + comp["height"] - border_thickness - padding
            if bit_y + bit_size > max_y:
                continue

            if bit_idx < len(comp["bit_states"]):
                bit_value = comp["bit_states"][bit_idx]
            else:
                bit_value = 0

            color = self.colors[bit_value]

            tinted_color = tuple(
                min(255, int(color[i] * 0.7 + comp["color"][i] * 0.3)) for i in range(3)
            )

            pygame.draw.rect(
                screen, tinted_color, (bit_x, bit_y, bit_size, bit_size)
            )

            if bit_value == 1 and bit_size >= 4:
                highlight_color = tuple(min(255, c + 30) for c in tinted_color)
                pygame.draw.rect(
                    screen, highlight_color, (bit_x, bit_y, bit_size, bit_size), 1
                )

    def reset_on_rebirth(self):
        for comp_name, comp in self.components.items():
            comp["bit_states"] = [0] * comp["bits"]
            if comp_name not in ["CPU", "BUS"]:
                comp["unlocked"] = False
            comp["level"] = 1 if comp_name in ["CPU", "BUS"] else 0

    def upgrade_to_era(self, era_level):
        if era_level <= 0:
            return
        if era_level >= 1:
            self.components["RAM"]["unlocked"] = True
        if era_level >= 2:
            self.components["STORAGE"]["unlocked"] = True
        if era_level >= 3:
            self.components["GPU"]["unlocked"] = True

    def get_era_completion_percentage(self):
        total_capacity = self._get_total_capacity()
        current_filled = self._get_current_filled_bits()
        if total_capacity == 0:
            return 0
        return (current_filled / total_capacity) * 100

    def get_bit_completeness_percentage(self):
        total_bits = 0
        total_ones = 0
        for comp in self.components.values():
            if comp["unlocked"]:
                total_bits += comp["bits"]
                total_ones += sum(comp["bit_states"])
        if total_bits == 0:
            return 0
        return (total_ones / total_bits) * 100

    def add_click_effect(self):
        pass

    def add_purchase_effect(self):
        pass

    def upgrade_component(self, comp_name):
        if comp_name in self.components:
            comp = self.components[comp_name]
            comp["level"] += 1
            old_bits = comp["bits"]
            comp["bits"] *= 2
            comp["bit_states"].extend([0] * old_bits)
