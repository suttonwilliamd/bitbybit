"""
Bit grid visualization for Bit by Bit Game - Working version
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

        # Motherboard component definitions - re-arranged for no overlapping
        # Layout designed like a real motherboard with proper spacing
        self.components = {
            "CPU": {
                "x_ratio": 0.05,  # Left side, top
                "y_ratio": 0.1,
                "width_ratio": 0.18,  # Compact square
                "height_ratio": 0.25,
                "bits": 64,  # 64-bit registers
                "unlocked": True,
                "level": 1,
                "color": (200, 50, 50),
                "name": "CPU",
                "description": "64-bit Registers",
            },
            "BUS": {
                "x_ratio": 0.28,  # Top center, between CPU and RAM
                "y_ratio": 0.05,  # Top row
                "width_ratio": 0.44,  # Wide but not full width
                "height_ratio": 0.12,  # Thin horizontal bar
                "bits": 16,  # 16-bit address bus
                "unlocked": True,
                "level": 1,
                "color": (100, 100, 150),
                "name": "BUS",
                "description": "16-bit Address Bus",
            },
            "RAM": {
                "x_ratio": 0.05,  # Left side, middle
                "y_ratio": 0.4,  # Middle-left, below CPU
                "width_ratio": 0.22,  # Moderate width
                "height_ratio": 0.3,  # Moderate height
                "bits": 1024,  # 1KB RAM
                "unlocked": False,
                "level": 0,
                "color": (50, 200, 50),
                "name": "RAM",
                "description": "1KB Core Memory",
            },
            "STORAGE": {
                "x_ratio": 0.75,  # Right side, bottom
                "y_ratio": 0.6,  # Bottom-right
                "width_ratio": 0.2,  # Compact
                "height_ratio": 0.3,  # Same height as RAM
                "bits": 8192,  # 8KB storage
                "unlocked": False,
                "level": 0,
                "color": (50, 100, 200),
                "name": "STORAGE",
                "description": "8KB Disk Drive",
            },
            "GPU": {
                "x_ratio": 0.38,  # Center-right, top-middle
                "y_ratio": 0.25,  # Middle area, right of CPU
                "width_ratio": 0.18,  # Same size as CPU
                "height_ratio": 0.22,  # Slightly shorter than CPU
                "bits": 512,  # 512B video memory
                "unlocked": False,
                "level": 0,
                "color": (200, 50, 200),
                "name": "GPU",
                "description": "512B Video Memory",
            },
        }

        # Calculate actual component dimensions
        for comp_name, comp in self.components.items():
            comp["x"] = self.x + int(self.width * comp["x_ratio"])
            comp["y"] = self.y + int(self.height * comp["y_ratio"])
            comp["width"] = int(self.width * comp["width_ratio"])
            comp["height"] = int(self.height * comp["height_ratio"])

            # Initialize bit arrays for each component
            total_bits = comp["bits"]
            comp["bit_states"] = [0] * total_bits
            comp["bit_animations"] = {}

        self.total_bits_earned = 0
        self.last_bits_count = 0
        self.last_rebirth_progress = 0

        self.colors = {
            0: (40, 40, 40),
            1: (50, 200, 50),
            "transitioning": (100, 150, 100),
            "component_border": (120, 120, 140),
            "locked": (30, 30, 30),
            "connection": (80, 80, 100),
        }

    def update_dimensions(self, x, y, width, height):
        """Update the grid dimensions and recalculate component positions"""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        for comp_name, comp in self.components.items():
            comp["x"] = self.x + int(self.width * comp["x_ratio"])
            comp["y"] = self.y + int(self.height * comp["y_ratio"])
            comp["width"] = int(self.width * comp["width_ratio"])
            comp["height"] = int(self.height * comp["height_ratio"])

    def update(self, bits, total_bits_earned, rebirth_threshold, hardware_generation=0, dt=1/60):
        self.total_bits_earned = total_bits_earned
        self.last_rebirth_progress = min(1.0, total_bits_earned / rebirth_threshold)
        self.hardware_generation = hardware_generation
        self.dt = dt

        self._update_component_unlocks()

        self._update_bits_to_progress()

        production_rate = max(0, bits - self.last_bits_count)
        if production_rate > 0:
            self._animate_production(production_rate)

        self._update_animations()

        self.last_bits_count = bits

    def _update_component_unlocks(self):
        """Unlock components based on hardware generation and progress"""
        progress = self.last_rebirth_progress
        hw_gen = getattr(self, "hardware_generation", 0)

        # CPU and BUS are always unlocked
        self.components["CPU"]["unlocked"] = True
        self.components["BUS"]["unlocked"] = True

        # Unlock components based on hardware generation
        if hw_gen >= 0:  # Mainframe Era (1960s)
            if progress >= 0.1:
                self.components["RAM"]["unlocked"] = True
        if hw_gen >= 1:  # Apple II Era (1977)
            if progress >= 0.05:
                self.components["RAM"]["unlocked"] = True
                self.components["STORAGE"]["unlocked"] = True
        if hw_gen >= 2:  # IBM PC Era (1981)
            if progress >= 0.03:
                self.components["RAM"]["unlocked"] = True
                self.components["STORAGE"]["unlocked"] = True
                self.components["GPU"]["unlocked"] = True
        if hw_gen >= 3:  # Later eras unlock everything early
            self.components["RAM"]["unlocked"] = True
            self.components["STORAGE"]["unlocked"] = True
            self.components["GPU"]["unlocked"] = True

    def _get_total_capacity(self):
        """Get total bit capacity of all unlocked components"""
        total_capacity = 0
        for comp_name, comp in self.components.items():
            if comp["unlocked"]:
                total_capacity += comp["bits"]
        return total_capacity

    def _get_current_filled_bits(self):
        """Get total number of filled bits across all unlocked components"""
        filled_bits = 0
        for comp_name, comp in self.components.items():
            if comp["unlocked"]:
                filled_bits += sum(comp["bit_states"])
        return filled_bits

    def _are_all_unlocked_components_full(self):
        """Check if all unlocked components are completely filled with 1s"""
        for comp_name, comp in self.components.items():
            if comp["unlocked"]:
                if not all(comp["bit_states"]):  # If any bit is 0, not full
                    return False
        return True

    def _update_bits_to_progress(self):
        """Update bits to match current progress - only accumulates, never removes"""
        # Don't accumulate if all unlocked components are full
        if self._are_all_unlocked_components_full():
            return

        # Calculate fill percentage based on current progress
        total_capacity = self._get_total_capacity()
        if total_capacity == 0:
            return

        fill_percentage = min(1.0, self.last_rebirth_progress)

        # Fill bits proportionally across all unlocked components
        target_filled_bits = int(total_capacity * fill_percentage)
        current_filled_bits = self._get_current_filled_bits()

        # Only add bits, never remove them
        if target_filled_bits > current_filled_bits:
            bits_to_add = target_filled_bits - current_filled_bits
            self._distribute_bits(bits_to_add)

    def _distribute_bits(self, bits_to_add):
        """Distribute bits across unlocked components"""
        if bits_to_add <= 0:
            return

        unlocked_components = [
            (comp_name, comp)
            for comp_name, comp in self.components.items()
            if comp["unlocked"]
        ]

        if not unlocked_components:
            return

        # Distribute bits round-robin style with preference for less full components
        bits_added = 0
        while bits_added < bits_to_add:
            # Find least full component
            best_comp = None
            best_ratio = 1.0

            for comp_name, comp in unlocked_components:
                filled_bits = sum(comp["bit_states"])
                total_bits = comp["bits"]
                fill_ratio = filled_bits / total_bits if total_bits > 0 else 0

                if fill_ratio < best_ratio:
                    best_ratio = fill_ratio
                    best_comp = (comp_name, comp)

            if best_comp:
                comp_name, comp = best_comp
                # Find first 0 bit and set to 1
                for i, bit_value in enumerate(comp["bit_states"]):
                    if bit_value == 0:
                        comp["bit_states"][i] = 1
                        # Start animation for this bit
                        anim_key = (comp["name"], i)
                        comp["bit_animations"][anim_key] = {
                            "from_value": 0,
                            "to_value": 1,
                            "progress": 0,
                            "duration": 0.5,
                        }
                        bits_added += 1
                        break

    def _animate_production(self, production_rate):
        """Animate bit changes based on production rate"""
        if production_rate <= 0:
            return

        # Animate multiple bits changing from 0 to 1 to show production
        unlocked_components = [
            comp for comp in self.components.values() if comp["unlocked"]
        ]

        if not unlocked_components:
            return

        bits_to_animate = min(production_rate, 3)  # Animate up to 3 bits per frame

        for _ in range(bits_to_animate):
            # Find a component with available 0 bits
            for comp in unlocked_components:
                for i, bit_value in enumerate(comp["bit_states"]):
                    if bit_value == 0:
                        # Start animation
                        anim_key = (comp["name"], i)
                        if anim_key not in comp["bit_animations"]:
                            comp["bit_animations"][anim_key] = {
                                "from_value": 0,
                                "to_value": 1,
                                "progress": 0,
                                "duration": 1.0,  # 1 second animation
                            }
                        return  # Animate one bit at a time

    def _update_animations(self):
        """Update all ongoing bit animations"""
        dt = getattr(self, "dt", 1/60)
        for comp_name, comp in self.components.items():
            if not comp["unlocked"]:
                continue

            completed_animations = []
            for anim_key, anim in comp["bit_animations"].items():
                anim["progress"] += dt

                if anim["progress"] >= anim["duration"]:
                    comp_name, bit_idx = anim_key
                    comp["bit_states"][bit_idx] = anim["to_value"]
                    completed_animations.append(anim_key)

            for anim_key in completed_animations:
                del comp["bit_animations"][anim_key]

    def draw(self, screen):
        """Draw the motherboard with all components and connections"""
        # Draw component connections first (background layer)
        self._draw_connections(screen)

        # Draw each component
        for comp_name, comp in self.components.items():
            self._draw_component(screen, comp_name, comp)

    def _draw_connections(self, screen):
        """Draw connection lines between components"""
        # Get component centers
        cpu = self.components["CPU"]
        cpu_center = (
            cpu["x"] + cpu["width"] // 2,
            cpu["y"] + cpu["height"] // 2,
        )

        bus = self.components["BUS"]
        bus_left = (
            bus["x"],
            bus["y"] + bus["height"] // 2,
        )
        bus_right = (
            bus["x"] + bus["width"],
            bus["y"] + bus["height"] // 2,
        )

        # Draw CPU to BUS connection
        pygame.draw.line(screen, self.colors["connection"], cpu_center, bus_left, 2)

        # BUS to RAM (if unlocked)
        if self.components["RAM"]["unlocked"]:
            ram = self.components["RAM"]
            ram_center = (ram["x"] + ram["width"] // 2, ram["y"] + ram["height"] // 2)
            pygame.draw.line(screen, self.colors["connection"], bus_left, ram_center, 2)

        # BUS to STORAGE (if unlocked)
        if self.components["STORAGE"]["unlocked"]:
            storage = self.components["STORAGE"]
            storage_center = (
                storage["x"] + storage["width"] // 2,
                storage["y"] + storage["height"] // 2,
            )
            pygame.draw.line(
                screen, self.colors["connection"], bus_right, storage_center, 2
            )

    def _draw_component(self, screen, comp_name, comp):
        """Draw a single component with its bits"""
        # Draw component background
        if comp["unlocked"]:
            bg_color = tuple(c // 4 for c in comp["color"])  # Darker version
            border_color = comp["color"]
        else:
            bg_color = self.colors["locked"]
            border_color = (60, 60, 60)

        pygame.draw.rect(
            screen, bg_color, (comp["x"], comp["y"], comp["width"], comp["height"])
        )
        pygame.draw.rect(
            screen,
            border_color,
            (comp["x"], comp["y"], comp["width"], comp["height"]),
            3,
        )

        if comp["unlocked"]:
            # Draw component label
            font = pygame.font.Font(None, 16)
            label = font.render(
                f"{comp['name']} Lvl.{comp['level']}", True, (255, 255, 255)
            )
            screen.blit(label, (comp["x"] + 5, comp["y"] + 5))

            # Draw description below name
            desc_font = pygame.font.Font(None, 12)
            desc_label = desc_font.render(comp["description"], True, (200, 200, 200))
            screen.blit(desc_label, (comp["x"] + 5, comp["y"] + 20))

            # Draw bits in a grid layout
            if comp["width"] > 30 and comp["height"] > 50:  # Ensure minimum size
                self._draw_component_bits(screen, comp)
        else:
            # Draw locked indicator
            font = pygame.font.Font(None, 20)
            label = font.render("LOCKED", True, (100, 100, 100))
            text_rect = label.get_rect(
                center=(comp["x"] + comp["width"] // 2, comp["y"] + comp["height"] // 2)
            )
            screen.blit(label, text_rect)

    def _draw_component_bits(self, screen, comp):
        """Draw the bits within a component as individual squares"""
        total_bits = comp["bits"]

        if comp["width"] <= 30 or comp["height"] <= 50:
            return

        # Account for 3px border on each side plus internal padding
        border_thickness = 6  # 3px border on left + 3px border on right
        padding = 10  # Internal padding
        available_width = comp["width"] - border_thickness - padding * 2
        available_height = comp["height"] - border_thickness - padding * 2

        min_bit_size = 3
        max_bit_size = 12

        # Use actual filled bits count for sizing, not theoretical capacity
        filled_bits = sum(comp["bit_states"])
        if filled_bits == 0:
            filled_bits = 1  # Avoid division by zero
        ideal_bit_size = min(
            max_bit_size,
            int(math.sqrt((available_width * available_height) / filled_bits))
        )
        bit_size = max(min_bit_size, ideal_bit_size)

        gap = 1
        total_bit_cell = bit_size + gap

        grid_cols = max(1, available_width // total_bit_cell)
        # Calculate rows based on actual filled bits, not theoretical capacity
        grid_rows = max(1, (filled_bits + grid_cols - 1) // grid_cols)

        if grid_rows * total_bit_cell > available_height:
            bit_size = max(min_bit_size, (available_height // grid_rows) - gap)
            total_bit_cell = bit_size + gap

        # Position bits within border and padding
        border_thickness = 3
        padding = 10
        start_x = comp["x"] + border_thickness + padding
        start_y = comp["y"] + border_thickness + padding

        # Use actual bit states count for grid calculation, not theoretical capacity
        actual_bits = len(comp["bit_states"])
        total_bits_to_draw = min(actual_bits, grid_cols * grid_rows)

        for bit_idx in range(total_bits_to_draw):
            row = bit_idx // grid_cols
            col = bit_idx % grid_cols

            bit_x = start_x + col * total_bit_cell
            bit_y = start_y + row * total_bit_cell
            
            # Ensure bit stays within component height boundaries
            max_y = comp["y"] + comp["height"] - border_thickness - padding
            if bit_y + bit_size > max_y:
                continue  # Skip this bit as it would overflow vertically
            
            anim_key = (comp["name"], bit_idx)
            # Safety check - don't access bit_states beyond array bounds
            if bit_idx < len(comp["bit_states"]):
                bit_value = comp["bit_states"][bit_idx]
            else:
                bit_value = 0

            if anim_key in comp["bit_animations"]:
                anim = comp["bit_animations"][anim_key]
                progress = anim["progress"] / anim["duration"]

                from_color = self.colors[anim["from_value"]]
                to_color = self.colors[anim["to_value"]]

                color = tuple(
                    int(from_color[i] + (to_color[i] - from_color[i]) * progress)
                    for i in range(3)
                )
            else:
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
        """Reset all bits to 0 when rebirth occurs"""
        for comp_name, comp in self.components.items():
            comp["bit_states"] = [0] * comp["bits"]
            comp["bit_animations"] = {}
            # Reset unlocked state to initial
            if comp_name not in ["CPU", "BUS"]:  # Keep these always unlocked
                comp["unlocked"] = False
            comp["level"] = 1 if comp_name in ["CPU", "BUS"] else 0

    def upgrade_to_era(self, era_level):
        """Upgrade hardware components to match a specific computing era"""
        # Simple implementation for basic functionality
        if era_level <= 0:
            return  # Already in mainframe era

        # Unlock more components in later eras
        if era_level >= 1:
            self.components["RAM"]["unlocked"] = True
        if era_level >= 2:
            self.components["STORAGE"]["unlocked"] = True
        if era_level >= 3:
            self.components["GPU"]["unlocked"] = True

    def get_era_completion_percentage(self):
        """Calculate percentage completion of current hardware era"""
        total_capacity = self._get_total_capacity()
        current_filled = self._get_current_filled_bits()

        if total_capacity == 0:
            return 0
        return (current_filled / total_capacity) * 100

    def get_bit_completeness_percentage(self):
        """Calculate the percentage of bits that are 1 across unlocked components"""
        total_bits = 0
        total_ones = 0

        for comp_name, comp in self.components.items():
            if comp["unlocked"]:
                total_bits += comp["bits"]
                total_ones += sum(comp["bit_states"])

        if total_bits == 0:
            return 0
        return (total_ones / total_bits) * 100

    def add_click_effect(self):
        """Add visual effect when accumulator is clicked"""
        # Simple implementation - could be enhanced later
        pass

    def add_purchase_effect(self):
        """Add visual effect when something is purchased"""
        # Simple implementation - could be enhanced later
        pass

    def upgrade_component(self, comp_name):
        """Handle component upgrade with visual effects"""
        if comp_name in self.components:
            comp = self.components[comp_name]
            comp["level"] += 1

            # Double the bit capacity
            old_bits = comp["bits"]
            comp["bits"] *= 2
            comp["bit_states"].extend([0] * old_bits)
