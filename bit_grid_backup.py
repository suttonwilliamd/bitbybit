"""
Bit grid visualization for Bit by Bit Game
"""

import pygame
import math
import random
from constants import COLORS


class BitDot:
    def __init__(self, center_x, center_y, bits_value):
        self.center_x = center_x
        self.center_y = center_y
        self.angle = random.uniform(0, 2 * math.pi)
        self.radius = 0
        self.target_radius = random.uniform(20, 80)
        self.lifetime = 1.0
        self.size = 4
        self.bits_value = bits_value
        self.spiral_speed = random.uniform(1, 3)

    def update(self, dt):
        # Spiral outward animation
        self.radius += (self.target_radius - self.radius) * 2 * dt
        self.angle += self.spiral_speed * dt
        self.lifetime -= dt
        # Calculate actual position
        self.x = self.center_x + math.cos(self.angle) * self.radius
        self.y = self.center_y + math.sin(self.angle) * self.radius

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * self.lifetime)

            color = COLORS["electric_cyan"]
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)


class MotherboardBitGrid:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Motherboard component definitions - based on real-world hardware specifications
        # Using mainframe era (1960s) as starting point
        self.components = {
            "CPU": {
                "x_ratio": 0.15,  # Moved left
                "y_ratio": 0.35,
                "width_ratio": 0.25,  # Slightly smaller
                "height_ratio": 0.3,
                "bits": 64,  # 64-bit registers (realistic for early mainframes)
                "unlocked": True,
                "level": 1,
                "color": (200, 50, 50),
                "name": "CPU",
                "description": "64-bit Registers",
            },
            "BUS": {
                "x_ratio": 0.42,  # Centered, spans between CPU and GPU
                "y_ratio": 0.15,
                "width_ratio": 0.35,  # Still spans width but proportionally smaller
                "height_ratio": 0.15,
                "bits": 16,  # 16-bit address bus (typical for mainframe era)
                "unlocked": True,
                "level": 1,
                "color": (100, 100, 150),
                "name": "BUS",
                "description": "16-bit Address Bus",
            },
            "RAM": {
                "x_ratio": 0.02,  # Far left
                "y_ratio": 0.6,  # Lower
                "width_ratio": 0.22,  # Slightly smaller
                "height_ratio": 0.35,
                "bits": 1024,  # 1KB RAM (realistic for 1960s mainframes)
                "unlocked": False,
                "level": 0,
                "color": (50, 200, 50),
                "name": "RAM",
                "description": "1KB Core Memory",
            },
            "STORAGE": {
                "x_ratio": 0.76,  # Far right
                "y_ratio": 0.6,  # Lower
                "width_ratio": 0.22,  # Slightly smaller
                "height_ratio": 0.35,
                "bits": 8192,  # 8KB storage (typical for early disk drives)
                "unlocked": False,
                "level": 0,
                "color": (50, 100, 200),
                "name": "STORAGE",
                "description": "8KB Disk Drive",
            },
            "GPU": {
                "x_ratio": 0.53,  # Moved right, more space from CPU
                "y_ratio": 0.05,
                "width_ratio": 0.25,  # Slightly smaller
                "height_ratio": 0.25,
                "bits": 512,  # 512B video memory (realistic for early graphics terminals)
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

        # Global state
        self.total_bits_earned = 0
        self.last_bits_count = 0
        self.last_rebirth_progress = 0

        # Enhanced colors with better contrast and visual hierarchy
        self.colors = {
            0: (30, 30, 35),  # 0 bit (darker, less saturated)
            1: (57, 255, 20),  # 1 bit (matrix green for consistency)
            "transitioning": (100, 150, 100),  # Transitioning state
            "component_border": (120, 140, 180),  # Component borders (muted blue)
            "locked": (25, 25, 30),  # Locked component color (slightly darker)
            "connection": (80, 100, 120),  # Connection lines (more visible)
            "active_glow": (0, 170, 220),  # Active component glow (electric cyan)
            "capacity_full": (255, 140, 90),  # Near capacity warning (signal orange)
            "upgrade_available": (255, 215, 0),  # Upgrade available (gold)
        }

        # Animation and visual enhancement states
        self.component_states = {}
        for comp_name in self.components:
            self.component_states[comp_name] = {
                "glow_intensity": 0,
                "pulse_timer": 0,
                "data_flow_active": False,
                "upgrade_glow": 0,
            }

    def update(self, bits, total_bits_earned, rebirth_threshold, hardware_generation=0):
        # Store current state
        self.total_bits_earned = total_bits_earned
        self.last_rebirth_progress = min(1.0, total_bits_earned / rebirth_threshold)
        self.hardware_generation = hardware_generation

        # Unlock components based on hardware generation and progress
        self._update_component_unlocks()

        # Update bits based on current progress
        self._update_bits_to_progress()

        # Animate based on production
        production_rate = max(0, bits - self.last_bits_count)
        if production_rate > 0:
            self._animate_production(production_rate)

        # Update animations
        self._update_animations()

        # Update component states (for enhanced effects)
        dt = 1 / 60  # Assuming 60 FPS, should pass dt from game loop
        self.update_component_states(dt)

        # Store current state
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

    def _get_component_fill_ratio(self, comp):
        """Get the fill ratio of a component"""
        if comp["bits"] == 0:
            return 0
        filled_bits = sum(comp["bit_states"])
        return filled_bits / comp["bits"]

    def _get_unlock_requirement(self, comp_name):
        """Get unlock requirement percentage for a component"""
        requirements = {
            "RAM": 10,  # 10% progress
            "STORAGE": 5,  # 5% progress in later eras
            "GPU": 3,  # 3% progress in later eras
        }
        return requirements.get(comp_name, 50)  # Default 50%

    def _draw_data_flow(self, screen, comp):
        """Draw animated data flow lines from component"""
        # Create flowing data effect
        flow_color = self.colors["active_glow"]
        center_x = comp["x"] + comp["width"] // 2
        center_y = comp["y"] + comp["height"] // 2

        # Draw radiating lines from component
        num_lines = 4
        for i in range(num_lines):
            angle = (2 * math.pi * i) / num_lines + pygame.time.get_ticks() * 0.001
            end_x = center_x + math.cos(angle) * 30
            end_y = center_y + math.sin(angle) * 30

            # Animated alpha
            alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.003 + i)) * 100)
            flow_surf = pygame.Surface((2, 30), pygame.SRCALPHA)
            flow_color_alpha = (*flow_color, alpha)
            pygame.draw.line(flow_surf, flow_color_alpha, (1, 0), (1, 30))

            # Rotate and position flow line
            screen.blit(flow_surf, (center_x - 1, center_y - 15))

    def _update_bits_to_progress(self):
        """Update bits to match current progress - only accumulates, never removes"""
        # Don't accumulate if all unlocked components are full
        if self._are_all_unlocked_components_full():
            return

        # Calculate actual fill progress based on available capacity
        total_capacity = self._get_total_capacity()
        current_filled = self._get_current_filled_bits()

        if total_capacity == 0:
            return

        # Use rebirth progress to determine target fill level
        # This ensures bits correspond to game state progression
        effective_progress = self.last_rebirth_progress

        for comp_name, comp in self.components.items():
            if not comp["unlocked"]:
                continue

            # Skip if this component is already full
            if all(comp["bit_states"]):
                continue

            total_bits = comp["bits"]
            target_ones = int(
                total_bits * effective_progress * comp["level"] / 5.0
            )  # Scale by level

            # Cap target at the maximum capacity of this component
            target_ones = min(target_ones, total_bits)

            current_ones = sum(comp["bit_states"])

            if current_ones < target_ones:
                # ONLY turn 0s into 1s - NEVER turn 1s into 0s
                zeros = [i for i, bit in enumerate(comp["bit_states"]) if bit == 0]
                # Fill bits systematically, not randomly, to ensure accumulation
                bits_to_add = min(target_ones - current_ones, len(zeros))
                for i in range(bits_to_add):
                    if zeros:
                        # Take bits in order for predictable accumulation
                        bit_idx = zeros[i % len(zeros)]
                        comp["bit_states"][bit_idx] = 1

    def _animate_production(self, production_rate):
        """Animate bits based on production rate - disabled to prevent flickering"""
        # Removed random animations to prevent visual flickering
        pass

    def _start_bit_animation(self, comp_name, bit_idx, from_value, to_value):
        """Start an animation for a specific bit"""
        comp = self.components[comp_name]
        key = (comp_name, bit_idx)
        comp["bit_animations"][key] = {
            "from_value": from_value,
            "to_value": to_value,
            "progress": 0.0,
            "duration": 0.3,
        }

    def _update_animations(self):
        """Update all bit animations"""
        for comp_name, comp in self.components.items():
            completed = []
            for key, anim in comp["bit_animations"].items():
                anim["progress"] += 1 / 60  # Assuming 60 FPS
                if anim["progress"] >= anim["duration"]:
                    completed.append(key)

            for key in completed:
                del comp["bit_animations"][key]

    def add_click_effect(self):
        """Add a bit accumulation effect when user clicks - only turns 0s to 1s"""
        unlocked_comps = [
            name for name, comp in self.components.items() if comp["unlocked"]
        ]
        for _ in range(3):
            if unlocked_comps:
                comp_name = random.choice(unlocked_comps)
                comp = self.components[comp_name]

                # Find only 0 bits to flip to 1 - never flip 1s to 0s
                zero_bits = [i for i, bit in enumerate(comp["bit_states"]) if bit == 0]
                if zero_bits:
                    bit_idx = random.choice(zero_bits)
                    self._start_bit_animation(comp_name, bit_idx, 0, 1)
                    comp["bit_states"][bit_idx] = 1

    def add_purchase_effect(self):
        """Add cascading accumulation effect for purchases - only turns 0s to 1s"""
        unlocked_comps = [
            name for name, comp in self.components.items() if comp["unlocked"]
        ]
        for _ in range(8):
            if unlocked_comps:
                comp_name = random.choice(unlocked_comps)
                comp = self.components[comp_name]

                # Find only 0 bits to flip to 1 - never flip 1s to 0s
                zero_bits = [i for i, bit in enumerate(comp["bit_states"]) if bit == 0]
                if zero_bits:
                    bit_idx = random.choice(zero_bits)
                    self._start_bit_animation(comp_name, bit_idx, 0, 1)
                    comp["bit_states"][bit_idx] = 1

    def upgrade_component(self, comp_name):
        """Upgrade a component level"""
        if comp_name in self.components:
            comp = self.components[comp_name]
            comp["level"] += 1
            # Add upgrade effect
            for _ in range(10):
                bit_idx = random.randint(0, comp["bits"] - 1)
                self._start_bit_animation(comp_name, bit_idx, 0, 1)
                comp["bit_states"][bit_idx] = 1

    def draw(self, screen):
        """Draw the motherboard layout"""
        # Draw background
        pygame.draw.rect(
            screen, (20, 20, 20), (self.x, self.y, self.width, self.height)
        )

        # Draw connection lines between components
        self._draw_connections(screen)

        # Draw components
        for comp_name, comp in self.components.items():
            self._draw_component(screen, comp_name, comp)

    def _draw_connections(self, screen):
        """Draw connection lines between components"""
        # CPU to BUS
        cpu = self.components["CPU"]
        bus = self.components["BUS"]
        cpu_center = (cpu["x"] + cpu["width"] // 2, cpu["y"] + cpu["height"] // 2)
        bus_left = (bus["x"], bus["y"] + bus["height"] // 2)
        bus_right = (bus["x"] + bus["width"], bus["y"] + bus["height"] // 2)

        pygame.draw.line(screen, self.colors["connection"], cpu_center, bus_left, 2)
        pygame.draw.line(screen, self.colors["connection"], cpu_center, bus_right, 2)

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
        """Draw a single component with enhanced visual effects"""
        state = self.component_states[comp_name]

        # Component background with enhanced effects
        if comp["unlocked"]:
            bg_color = tuple(c // 4 for c in comp["color"])  # Darker version

            # Add glow effect for active components
            if state["glow_intensity"] > 0:
                glow_surf = pygame.Surface(
                    (comp["width"], comp["height"]), pygame.SRCALPHA
                )
                glow_color = (
                    *self.colors["active_glow"],
                    int(state["glow_intensity"] * 50),
                )
                pygame.draw.rect(
                    glow_surf, glow_color, (0, 0, comp["width"], comp["height"])
                )
                screen.blit(glow_surf, (comp["x"], comp["y"]))

            # Add upgrade glow if available
            if state["upgrade_glow"] > 0:
                upgrade_glow_surf = pygame.Surface(
                    (comp["width"], comp["height"]), pygame.SRCALPHA
                )
                upgrade_color = (
                    *self.colors["upgrade_available"],
                    int(state["upgrade_glow"] * 30),
                )
                pygame.draw.rect(
                    upgrade_glow_surf,
                    upgrade_color,
                    (0, 0, comp["width"], comp["height"]),
                    3,
                )
                screen.blit(upgrade_glow_surf, (comp["x"], comp["y"]))
        else:
            bg_color = self.colors["locked"]

        pygame.draw.rect(
            screen, bg_color, (comp["x"], comp["y"], comp["width"], comp["height"])
        )

        # Enhanced component border with dynamic coloring
        if comp["unlocked"]:
            # Check capacity and set border color accordingly
            filled_ratio = self._get_component_fill_ratio(comp)
            if filled_ratio > 0.9:
                border_color = self.colors["capacity_full"]
            elif state["data_flow_active"]:
                border_color = self.colors["active_glow"]
            else:
                border_color = comp["color"]
        else:
            border_color = (60, 60, 60)

        pygame.draw.rect(
            screen,
            border_color,
            (comp["x"], comp["y"], comp["width"], comp["height"]),
            3,
        )

        if comp["unlocked"]:
            # Enhanced component label with better typography
            font = pygame.font.Font(None, 16)
            label = font.render(
                f"{comp['name']} Lvl.{comp['level']}", True, (240, 245, 255)
            )
            screen.blit(label, (comp["x"] + 5, comp["y"] + 5))

            # Draw description with better contrast
            desc_font = pygame.font.Font(None, 12)
            desc_label = desc_font.render(comp["description"], True, (180, 185, 195))
            screen.blit(desc_label, (comp["x"] + 5, comp["y"] + 20))

            # Draw capacity indicator
            filled_ratio = self._get_component_fill_ratio(comp)
            capacity_text = f"{filled_ratio * 100:.0f}%"
            capacity_color = (
                self.colors["capacity_full"] if filled_ratio > 0.9 else (120, 140, 180)
            )
            capacity_label = desc_font.render(capacity_text, True, capacity_color)
            screen.blit(capacity_label, (comp["x"] + 5, comp["y"] + 35))

            # Draw bits in a grid layout with enhanced visualization
            if comp["width"] > 30 and comp["height"] > 50:  # Ensure minimum size
                self._draw_component_bits(screen, comp)

            # Draw data flow lines between components
            if state["data_flow_active"]:
                self._draw_data_flow(screen, comp)
        else:
            # Enhanced locked indicator
            font = pygame.font.Font(None, 20)
            label = font.render("LOCKED", True, (80, 85, 95))
            text_rect = label.get_rect(
                center=(comp["x"] + comp["width"] // 2, comp["y"] + comp["height"] // 2)
            )
            screen.blit(label, text_rect)

            # Draw unlock progress hint
            progress_hint = f"Unlock at {self._get_unlock_requirement(comp_name)}%"
            hint_font = pygame.font.Font(None, 10)
            hint_label = hint_font.render(progress_hint, True, (60, 65, 75))
            hint_rect = hint_label.get_rect(
                center=(
                    comp["x"] + comp["width"] // 2,
                    comp["y"] + comp["height"] // 2 + 15,
                )
            )
            screen.blit(hint_label, hint_rect)

    def _draw_component_bits(self, screen, comp):
        """Draw the bits within a component"""
        total_bits = comp["bits"]

        # Calculate grid dimensions for bits
        total_bits = comp["bits"]

        # Ensure minimum component size
        if comp["width"] <= 30 or comp["height"] <= 50:
            return

        # Calculate grid dimensions for bits
        grid_cols = max(1, int(math.sqrt(total_bits * comp["width"] / comp["height"])))
        grid_rows = (total_bits + grid_cols - 1) // grid_cols

        bit_width = max(1, (comp["width"] - 20) // grid_cols)
        bit_height = max(1, (comp["height"] - 40) // grid_rows)

        start_x = comp["x"] + 10
        start_y = comp["y"] + 30

        for bit_idx in range(total_bits):
            row = bit_idx // grid_cols
            col = bit_idx % grid_cols

            if row >= grid_rows:
                continue

            bit_x = start_x + col * bit_width
            bit_y = start_y + row * bit_height

            # Check if bit is animating
            anim_key = (comp["name"], bit_idx)
            bit_value = comp["bit_states"][bit_idx]

            if anim_key in comp["bit_animations"]:
                anim = comp["bit_animations"][anim_key]
                progress = anim["progress"] / anim["duration"]

                # Interpolate color during animation
                from_color = self.colors[anim["from_value"]]
                to_color = self.colors[anim["to_value"]]

                color = tuple(
                    int(from_color[i] + (to_color[i] - from_color[i]) * progress)
                    for i in range(3)
                )

                # Add glow effect during animation
                if progress < 0.5:
                    glow_surface = pygame.Surface((bit_width, bit_height))
                    glow_surface.set_alpha(100)
                    glow_color = tuple(min(255, c + 50) for c in color)
                    glow_surface.fill(glow_color)
                    screen.blit(glow_surface, (bit_x, bit_y))
            else:
                color = self.colors[bit_value]

            # Draw bit with component color tint
            tinted_color = tuple(
                min(255, int(color[i] * 0.7 + comp["color"][i] * 0.3)) for i in range(3)
            )

            pygame.draw.rect(
                screen, tinted_color, (bit_x, bit_y, bit_width - 1, bit_height - 1)
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
            
            # Reset component states
            if comp_name in self.component_states:
                self.component_states[comp_name] = {
                    "glow_intensity": 0,
                    "pulse_timer": 0,
                    "data_flow_active": False,
                    "upgrade_glow": 0,
                }

    def upgrade_to_era(self, era_level):
        """Upgrade hardware components to match a specific computing era"""
        era_configs = {
            0: {  # Mainframe Era (1960s) - Current
                "CPU": {"bits": 64, "description": "64-bit Registers"},
                "BUS": {"bits": 16, "description": "16-bit Address Bus"},
                "RAM": {"bits": 1024, "description": "1KB Core Memory"},
                "STORAGE": {"bits": 8192, "description": "8KB Disk Drive"},
                "GPU": {"bits": 512, "description": "512B Video Memory"},
            },
            1: {  # Apple II Era (1977)
                "CPU": {"bits": 256, "description": "8-bit Registers"},
                "BUS": {"bits": 16, "description": "16-bit Address Bus"},
                "RAM": {"bits": 4096, "description": "4KB DRAM"},
                "STORAGE": {"bits": 143360, "description": "140KB Floppy Disk"},
                "GPU": {"bits": 2048, "description": "2KB Video Memory"},
            },
            2: {  # IBM PC Era (1981)
                "CPU": {"bits": 1024, "description": "16-bit Registers"},
                "BUS": {"bits": 20, "description": "20-bit Address Bus"},
                "RAM": {"bits": 65536, "description": "64KB RAM"},
                "STORAGE": {"bits": 1048576, "description": "1MB Hard Drive"},
                "GPU": {"bits": 16384, "description": "16KB CGA Graphics"},
            },
            3: {  # Multimedia Era (1990s)
                "CPU": {"bits": 4096, "description": "32-bit Registers"},
                "BUS": {"bits": 32, "description": "32-bit PCI Bus"},
                "RAM": {"bits": 4194304, "description": "4MB RAM"},
                "STORAGE": {"bits": 104857600, "description": "100MB Hard Drive"},
                "GPU": {"bits": 262144, "description": "256KB VGA Graphics"},
            },
            4: {  # Internet Era (2000s)
                "CPU": {"bits": 8192, "description": "64-bit Registers"},
                "BUS": {"bits": 64, "description": "64-bit Front Side Bus"},
                "RAM": {"bits": 134217728, "description": "128MB DDR RAM"},
                "STORAGE": {"bits": 10737418240, "description": "10GB IDE Drive"},
                "GPU": {"bits": 16777216, "description": "16MB VRAM"},
            },
            5: {  # Mobile Era (2010s)
                "CPU": {"bits": 16384, "description": "ARM 64-bit"},
                "BUS": {"bits": 64, "description": "64-bit Memory Bus"},
                "RAM": {"bits": 1073741824, "description": "1GB Mobile RAM"},
                "STORAGE": {"bits": 17179869184, "description": "16GB Flash Storage"},
                "GPU": {"bits": 134217728, "description": "128MB Mobile GPU"},
            },
            6: {  # AI Era (2020s)
                "CPU": {"bits": 32768, "description": "64-bit Multi-core"},
                "BUS": {"bits": 128, "description": "128-bit PCIe"},
                "RAM": {"bits": 17179869184, "description": "16GB DDR5"},
                "STORAGE": {"bits": 1099511627776, "description": "1TB NVMe SSD"},
                "GPU": {"bits": 17179869184, "description": "16GB VRAM"},
            },
        }

        if era_level in era_configs:
            era_config = era_configs[era_level]
            for comp_name, comp in self.components.items():
                if comp_name in era_config:
                    # Preserve current bit states proportionally
                    old_bits = comp["bits"]
                    new_bits = era_config[comp_name]["bits"]

                    # Scale bit states to new size
                    if old_bits > 0:
                        old_fill_ratio = sum(comp["bit_states"]) / old_bits
                        comp["bits"] = new_bits
                        comp["bit_states"] = [0] * new_bits

                        # Fill same proportion of bits in new component
                        target_ones = int(new_bits * old_fill_ratio)
                        for i in range(min(target_ones, new_bits)):
                            comp["bit_states"][i] = 1

                    # Update description
                    comp["description"] = era_config[comp_name]["description"]

                    # Update animations for new size
                    comp["bit_animations"] = {}

    def get_era_total_capacity(self):
        """Get total bit capacity for the current hardware era"""
        hw_gen = getattr(self, "hardware_generation", 0)

        # Era capacity definitions (total bits needed to complete each era)
        era_capacities = {
            0: 9728,  # Mainframe Era: CPU(64) + BUS(16) + RAM(1024) + STORAGE(8192) + GPU(512)
            1: 150016,  # Apple II Era: CPU(256) + BUS(16) + RAM(4096) + STORAGE(143360) + GPU(2048)
            2: 1114112,  # IBM PC Era: CPU(1024) + BUS(20) + RAM(65536) + STORAGE(1048576) + GPU(16384)
            3: 46137344,  # Multimedia Era: CPU(4096) + BUS(32) + RAM(4194304) + STORAGE(104857600) + GPU(262144)
            4: 10884218880,  # Internet Era: CPU(8192) + BUS(64) + RAM(134217728) + STORAGE(10737418240) + GPU(16777216)
            5: 1832519377920,  # Mobile Era: CPU(16384) + BUS(64) + RAM(1073741824) + STORAGE(17179869184) + GPU(134217728)
            6: 111669149696,  # AI Era: CPU(32768) + BUS(128) + RAM(17179869184) + STORAGE(1099511627776) + GPU(17179869184)
        }

        return era_capacities.get(hw_gen, 9728)  # Default to mainframe era

    def get_era_completion_percentage(self):
        """Calculate the percentage completion of the current hardware era"""
        total_capacity = self.get_era_total_capacity()
        current_filled = self._get_current_filled_bits()

        if total_capacity == 0:
            return 0
        return (current_filled / total_capacity) * 100

    def get_debug_info(self):
        """Get debug information about current state"""
        info = []
        info.append(f"Hardware Generation: {getattr(self, 'hardware_generation', 0)}")
        info.append(f"Era Capacity: {self.get_era_total_capacity()} bits")
        info.append(f"Current Filled: {self._get_current_filled_bits()} bits")
        info.append(f"Era Completion: {self.get_era_completion_percentage():.2f}%")
        info.append("Components:")
        for comp_name, comp in self.components.items():
            if comp["unlocked"]:
                filled = sum(comp["bit_states"])
                total = comp["bits"]
                info.append(
                    f"  {comp_name}: {filled}/{total} ({filled / total * 100:.1f}%)"
                )
        return "\n".join(info)

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
