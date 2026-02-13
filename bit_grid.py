"""
Bit grid visualization for Bit by Bit Game
Motherboard-style tech tree with horizontal flow: CPU → BUS → RAM/GPU/STORAGE
Exact bit-level LED representation v2.2
"""

import pygame
import math
import random
from constants import COLORS, get_exact_bits

# Try to import numpy for high-performance LED rendering
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None


class LEDGrid:
    """Exact bit-level LED grid with density scaling for large capacities"""
    
    _font_cache = None
    _label_cache = {}
    
    def __init__(self, rect, exact_bits: int):
        self.rect = rect
        self.exact_bits = max(1, exact_bits)  # Ensure at least 1
        self.max_cells = 1048576
        self.cells = min(self.exact_bits, self.max_cells)
        self.density = self.exact_bits / self.cells if self.exact_bits > self.max_cells else 1.0
        
        self.grid_w = int(math.sqrt(self.cells))
        self.grid_h = self.cells // self.grid_w
        
        self.grid = np.zeros((self.grid_h, self.grid_w, 3), dtype=np.uint8) if HAS_NUMPY else None
        self.surf = pygame.Surface((rect.width, rect.height)) if rect.width > 0 and rect.height > 0 else None
        self.glow = np.zeros((self.grid_h, self.grid_w), dtype=np.float32) if HAS_NUMPY else None
        
        self._setup_label()
        
        self.current_lit = 0
        self.passive_glow_timer = 0
        self.click_bursts = []
        
        self._cached_text_surf = None
        self._cached_label = None
        
    def _setup_label(self):
        if self.density > 1:
            self.label = f"{self.exact_bits:,} bits\n1 LED = {int(self.density):,} bits"
        else:
            self.label = f"{self.exact_bits:,} bits\n1 LED = 1 bit"
    
    def update_fill(self, frac: float):
        """Update fill based on progress fraction (0.0 - 1.0)"""
        lit = int(frac * self.cells)
        self.current_lit = lit
        
        if not HAS_NUMPY or self.grid is None:
            return
            
        rows = lit // self.grid_w
        cols = lit % self.grid_w
        
        self.grid[:] = [16, 16, 32]
        if rows > 0:
            self.grid[:rows, :] = [0, 255, 20]
        if cols > 0 and rows < self.grid_h:
            self.grid[rows, :cols] = [0, 255, 20]
    
    def animate_passive(self, bits_per_sec: float, dt: float):
        """Animate passive fill based on bits per second"""
        if bits_per_sec <= 0 or not HAS_NUMPY or self.glow is None:
            return
            
        new_lights = int(bits_per_sec * dt / self.density)
        if new_lights > 0:
            max_row = max(0, self.grid_h - 20)
            num_bursts = min(new_lights, 100)
            recent_rows = np.random.randint(max_row, self.grid_h, num_bursts)
            self.grid[recent_rows, :] = [0, 173, 255]
            self.glow[recent_rows] = 1.0
    
    def animate_click(self, click_bits: float):
        """Animate click burst effect"""
        if click_bits <= 0 or not HAS_NUMPY or self.glow is None:
            return
            
        cells_to_light = int(click_bits / self.density)
        if cells_to_light > 0:
            actual_cells = self.grid_h * self.grid_w
            indices = np.random.randint(0, actual_cells, min(cells_to_light, 50))
            rows, cols = np.unravel_index(indices, (self.grid_h, self.grid_w))
            self.grid[rows, cols] = [255, 215, 0]
            self.glow[rows, cols] = 1.5
    
    def render(self, screen):
        """Render the LED grid to screen"""
        if LEDGrid._font_cache is None:
            LEDGrid._font_cache = pygame.font.SysFont("Consolas", 18)
        
        if not HAS_NUMPY or self.grid is None or self.surf is None:
            self._render_fallback(screen)
            return
        
        if self._cached_label != self.label:
            self._cached_label = self.label
            self._cached_text_surf = LEDGrid._font_cache.render(self.label, True, (200, 255, 255))
        
        if self._cached_text_surf:
            screen.blit(self._cached_text_surf, (self.rect.x, self.rect.bottom - 40))
            
        self.glow *= 0.85
        glow_int = (self.glow * 128).astype(np.uint8)
        
        combined = self.grid.astype(np.float32)
        glow_broadcast = np.stack([glow_int] * 3, axis=-1)
        combined = combined + glow_broadcast
        combined = np.clip(combined, 0, 255).astype(np.uint8)
        
        try:
            pygame.surfarray.blit_array(self.surf, combined)
        except:
            pass
        
        px_per_led = min(self.rect.width / self.grid_w, self.rect.height / self.grid_h)
        
        if px_per_led < 1 and self.grid_w > 0 and self.grid_h > 0:
            try:
                scaled = pygame.transform.smoothscale(
                    self.surf, 
                    (int(self.grid_w * px_per_led), int(self.grid_h * px_per_led))
                )
                screen.blit(scaled, (self.rect.x, self.rect.y))
            except:
                screen.blit(self.surf, (self.rect.x, self.rect.y))
        else:
            screen.blit(self.surf, (self.rect.x, self.rect.y))
        
        if self._cached_label != self.label:
            self._cached_label = self.label
            self._cached_text_surf = LEDGrid._font_cache.render(self.label, True, (200, 255, 255))
        
        if self._cached_text_surf:
            screen.blit(self._cached_text_surf, (self.rect.x, self.rect.bottom - 40))
    
    def _render_fallback(self, screen):
        """Fallback rendering when numpy is not available"""
        if self.rect.width <= 0 or self.rect.height <= 0:
            return
            
        if self.current_lit == 0:
            pygame.draw.rect(screen, (16, 16, 32), self.rect)
            return
        
        grid_w = int(math.sqrt(self.cells))
        grid_h = self.cells // grid_w
        
        px_w = self.rect.width / grid_w
        px_h = self.rect.height / grid_h
        
        fill_color = (0, 255, 20)
        empty_color = (16, 16, 32)
        
        lit = self.current_lit
        for row in range(grid_h):
            for col in range(grid_w):
                idx = row * grid_w + col
                if idx >= self.cells:
                    break
                    
                x = self.rect.x + int(col * px_w)
                y = self.rect.y + int(row * px_h)
                w = max(1, int(px_w) - 1)
                h = max(1, int(px_h) - 1)
                
                color = fill_color if idx < lit else empty_color
                pygame.draw.rect(screen, color, (x, y, w, h))
        
        if LEDGrid._font_cache is None:
            LEDGrid._font_cache = pygame.font.SysFont("Consolas", 18)
        
        if self._cached_label != self.label:
            self._cached_label = self.label
            self._cached_text_surf = LEDGrid._font_cache.render(self.label, True, (200, 255, 255))
        
        if self._cached_text_surf:
            screen.blit(self._cached_text_surf, (self.rect.x, self.rect.bottom - 40))
    
    def reset(self):
        """Reset on rebirth"""
        if HAS_NUMPY:
            if self.grid is not None:
                self.grid[:] = [16, 16, 32]
            if self.glow is not None:
                self.glow[:] = 0
        self.current_lit = 0


class MotherboardBitGrid:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.hardware_generation = 0
        self.dt = 1/60
        
        self.category_map = {
            "CPU": "cpu",
            "BUS": "cpu",
            "RAM": "ram",
            "GPU": "gpu",
            "STORAGE": "storage",
        }

        self.components = {
            "CPU": {
                "col": 0,
                "row": 0,
                "row_span": 2,
                "bits": 64,
                "exact_bits": 512,
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
                "exact_bits": 512,
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
                "exact_bits": 393216,
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
                "exact_bits": 512,
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
                "exact_bits": 8192,
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

        self.led_grids = {}
        
        for comp in self.components.values():
            total_bits = comp["bits"]
            comp["bit_states"] = [0] * total_bits
            comp["x"] = 0
            comp["y"] = 0
            comp["width"] = 0
            comp["height"] = 0

        self._layout_components()
        
        self._init_led_grids()

        self.total_bits_earned = 0
        self.last_bits_count = 0
        self.last_rebirth_progress = 0
        
        self.bits_per_sec = 0

        self.colors = {
            0: (0, 0, 0),  # Black - empty bit
            1: (57, 255, 20),  # Classic phosphor green - filled bit
            "transitioning": (100, 255, 100),
            "component_border": (120, 120, 140),
            "locked": (20, 20, 28),
            "connection": (55, 60, 80),
        }

        self._label_font = None
        self._desc_font = None
        self._lock_font = None

        self._text_cache = {}
        self._cache_version = 0

        self._click_bursts = []
        self._passive_glow_timers = {}
    
    def _init_led_grids(self):
        """Initialize LED grids for each component"""
        self.led_grids = {}
        
        for comp_name, comp in self.components.items():
            x = comp["x"]
            y = comp["y"]
            w = comp["width"]
            h = comp["height"]
            
            border_thickness = 6
            padding = 10
            led_w = w - border_thickness * 2 - padding * 2
            led_h = h - border_thickness * 2 - padding * 2
            
            if led_w > 0 and led_h > 0:
                rect = pygame.Rect(x + border_thickness + padding, 
                                   y + border_thickness + padding,
                                   led_w, led_h)
                exact_bits = max(1, comp.get("exact_bits", comp["bits"]))
                self.led_grids[comp_name] = LEDGrid(rect, exact_bits)
    
    def _update_led_grids(self):
        """Update LED grid positions on dimension change"""
        for comp_name, comp in self.components.items():
            if comp_name not in self.led_grids:
                continue
                
            x = comp["x"]
            y = comp["y"]
            w = comp["width"]
            h = comp["height"]
            
            border_thickness = 6
            padding = 10
            led_w = w - border_thickness * 2 - padding * 2
            led_h = h - border_thickness * 2 - padding * 2
            
            if led_w > 10 and led_h > 10:
                rect = pygame.Rect(x + border_thickness + padding, 
                                   y + border_thickness + padding,
                                   led_w, led_h)
                old_grid = self.led_grids[comp_name]
                old_bits = old_grid.exact_bits
                self.led_grids[comp_name] = LEDGrid(rect, old_bits)
    
    def _get_exact_bits(self, comp_name):
        """Get exact bits for a component based on category and generation"""
        category = self.category_map.get(comp_name, "cpu")
        gen = self.hardware_generation
        return get_exact_bits(category, gen)

    def _render_led_grid(self, screen, comp):
        """Render component using LEDGrid"""
        comp_name = comp["name"]
        
        if comp_name not in self.led_grids:
            return
            
        led_grid = self.led_grids[comp_name]
        
        if comp["unlocked"]:
            exact_bits = max(1, self._get_exact_bits(comp_name))
            if led_grid.exact_bits != exact_bits:
                x = comp["x"]
                y = comp["y"]
                w = comp["width"]
                h = comp["height"]
                border_thickness = 6
                padding = 10
                led_w = w - border_thickness * 2 - padding * 2
                led_h = h - border_thickness * 2 - padding * 2
                if led_w > 10 and led_h > 10:
                    rect = pygame.Rect(x + border_thickness + padding, 
                                      y + border_thickness + padding,
                                      led_w, led_h)
                    self.led_grids[comp_name] = LEDGrid(rect, exact_bits)
                    led_grid = self.led_grids[comp_name]
            
            fill_frac = 0.0
            if comp["bits"] > 0:
                filled = sum(comp["bit_states"])
                fill_frac = filled / comp["bits"]
            led_grid.update_fill(fill_frac)
            led_grid.animate_passive(self.bits_per_sec, self.dt)
            led_grid.render(screen)

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
        self._update_led_grids()

    def update(self, bits, total_bits_earned, rebirth_threshold, hardware_generation=0, dt=1/60, bits_per_sec=0):
        self.total_bits_earned = total_bits_earned
        visual_threshold = rebirth_threshold if rebirth_threshold > 0 else 1024 * 1024
        self.last_rebirth_progress = min(1.0, total_bits_earned / visual_threshold)
        self.hardware_generation = hardware_generation
        self.dt = dt
        self.bits_per_sec = bits_per_sec
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
        if hasattr(self, '_cached_filled_bits') and self._cached_filled_bits >= 0:
            return self._cached_filled_bits
        filled_bits = 0
        for comp in self.components.values():
            if comp["unlocked"]:
                filled_bits += sum(comp["bit_states"])
        self._cached_filled_bits = filled_bits
        return filled_bits

    def _invalidate_filled_bits_cache(self):
        self._cached_filled_bits = -1

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

        target_filled_bits = min(self.total_bits_earned, total_capacity)
        
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
        
        if bits_added > 0:
            self._invalidate_filled_bits_cache()

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

            # Draw individual bits inside the component
            self._draw_component_bits(screen, comp)

            # Draw text on top of bits
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
        """Draw component bits using LEDGrid"""
        self._render_led_grid(screen, comp)

    def reset_on_rebirth(self):
        for comp_name, comp in self.components.items():
            comp["bit_states"] = [0] * comp["bits"]
            if comp_name not in ["CPU", "BUS"]:
                comp["unlocked"] = False
            comp["level"] = 1 if comp_name in ["CPU", "BUS"] else 0
        for led_grid in self.led_grids.values():
            led_grid.reset()
        self._invalidate_filled_bits_cache()
        self._smoothed_era_progress = 0

    def upgrade_to_era(self, era_level):
        if era_level <= 0:
            return
        if era_level >= 1:
            self.components["RAM"]["unlocked"] = True
        if era_level >= 2:
            self.components["STORAGE"]["unlocked"] = True
        if era_level >= 3:
            self.components["GPU"]["unlocked"] = True

    def get_era_completion_percentage(self, threshold=9728):
        if not hasattr(self, 'total_bits_earned') or self.total_bits_earned == 0:
            return 0
        raw_progress = min(100, (self.total_bits_earned / threshold) * 100)
        if not hasattr(self, '_smoothed_era_progress'):
            self._smoothed_era_progress = raw_progress
        self._smoothed_era_progress += (raw_progress - self._smoothed_era_progress) * 0.3
        return self._smoothed_era_progress

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
        """Add click burst effect to random unlocked components"""
        # Find unlocked components
        unlocked = [name for name, comp in self.components.items() if comp["unlocked"]]
        if not unlocked:
            return
        
        # Add burst to random component
        comp_name = random.choice(unlocked)
        
        # Use LEDGrid animate_click
        if comp_name in self.led_grids:
            self.led_grids[comp_name].animate_click(1)

    def add_purchase_effect(self):
        """Add purchase effect - triggers glow on multiple components"""
        time_ms = pygame.time.get_ticks()
        
        # Trigger glow on all unlocked components
        for comp_name in self.components:
            if self.components[comp_name]["unlocked"]:
                self._passive_glow_timers[comp_name] = time_ms

    def upgrade_component(self, comp_name):
        if comp_name in self.components:
            comp = self.components[comp_name]
            comp["level"] += 1
            old_bits = comp["bits"]
            comp["bits"] *= 2
            comp["bit_states"].extend([0] * old_bits)
