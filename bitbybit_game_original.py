import pygame
import sys
import math
import json
import os
from datetime import datetime
import random

# Initialize Pygame
pygame.init()

# Import TOON parser
from toon_parser import load_toon_file

# Load game configuration from TOON files
try:
    GAME_CONFIG = load_toon_file("config/game.toon")
    GENERATORS_CONFIG = load_toon_file("config/generators.toon")
    UPGRADES_CONFIG = load_toon_file("config/upgrades.toon")
    print("Successfully loaded TOON configs")
except Exception as e:
    print(f"Error loading TOON config: {e}")
    # Fallback to hardcoded config
    GAME_CONFIG = {
        "display": {
            "width": 1200,
            "height": 800,
            "fps": 60,
            "auto_save_interval": 30000,
        },
        "game": {"SAVE_FILE": "bitbybit_save.json", "AUTO_SAVE_INTERVAL": 30000},
        "rebirth": {"threshold_bits": 128 * 1024 * 1024},
    }
    GENERATORS_CONFIG = {"generators": []}
    UPGRADES_CONFIG = {"upgrades": []}


# Parse colors from config
def parse_color(color_str):
    """Parse hex color string to RGB tuple"""
    if color_str.startswith("#"):
        hex_str = color_str[1:]
        return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))
    return (255, 255, 255)  # Default white


# Enhanced color palette from VISUAL.MD
COLORS = {
    "deep_space_blue": (10, 14, 39),
    "electric_cyan": (0, 217, 255),
    "neon_purple": (180, 74, 255),
    "matrix_green": (57, 255, 20),
    "signal_orange": (255, 107, 53),
    "quantum_violet": (138, 43, 226),
    "dim_gray": (42, 45, 58),
    "soft_white": (232, 232, 240),
    "muted_blue": (74, 85, 104),
    "gold": (255, 215, 0),
    "red_error": (255, 68, 68),
    # Additional gradient colors
    "deep_space_gradient_end": (26, 30, 55),
    "card_background": (31, 34, 51),
    "panel_background": (42, 35, 51),
}

# Game constants from config
WINDOW_WIDTH = GAME_CONFIG.get("display", {}).get("width", 1200)
WINDOW_HEIGHT = GAME_CONFIG.get("display", {}).get("height", 800)
FPS = GAME_CONFIG.get("display", {}).get("fps", 60)
SAVE_FILE = GAME_CONFIG.get("game", {}).get("SAVE_FILE", "bitbybit_save.json")
AUTO_SAVE_INTERVAL = GAME_CONFIG.get("display", {}).get("auto_save_interval", 30000)
REBIRTH_THRESHOLD = GAME_CONFIG.get("rebirth", {}).get(
    "threshold_bits", 128 * 1024 * 1024
)

# Convert config arrays to dictionaries for easier access
GENERATORS = {}
if "generators" in GENERATORS_CONFIG and GENERATORS_CONFIG["generators"]:
    for gen in GENERATORS_CONFIG["generators"]:
        GENERATORS[gen["id"]] = gen
        print(f"Loaded generator: {gen['id']}")
else:
    print("No generators found in config, will use hardcoded later")

UPGRADES = {}
if "upgrades" in UPGRADES_CONFIG and UPGRADES_CONFIG["upgrades"]:
    for upgrade in UPGRADES_CONFIG["upgrades"]:
        UPGRADES[upgrade["id"]] = upgrade
        print(f"Loaded upgrade: {upgrade['id']}")
else:
    print("No upgrades found in config, will use hardcoded later")

# Game Configuration
CONFIG = {
    "SAVE_FILE": "bitbybit_save.json",
    "AUTO_SAVE_INTERVAL": 30000,  # 30 seconds
    "REBIRTH_THRESHOLD": 128 * 1024 * 1024,  # 128 MB in bits
    "GENERATORS": {
        "rng": {
            "id": "rng",
            "name": "Random Number Generator",
            "base_cost": 10,
            "base_production": 1,
            "cost_multiplier": 1.15,
            "icon": "🎲",
            "flavor": "Pure chaos. Maximum entropy.",
        },
        "biased_coin": {
            "id": "biased_coin",
            "name": "Biased Coin",
            "base_cost": 100,
            "base_production": 8,
            "cost_multiplier": 1.15,
            "icon": "🪙",
            "flavor": "Not all outcomes are equal.",
            "unlock_threshold": 100,
        },
        "dice_roller": {
            "id": "dice_roller",
            "name": "Dice Roller",
            "base_cost": 1200,
            "base_production": 100,
            "cost_multiplier": 1.15,
            "icon": "🎯",
            "flavor": "Six possible states.",
            "unlock_threshold": 1000,
        },
    },
    "UPGRADES": {
        "entropy_amplification": {
            "id": "entropy_amplification",
            "name": "Entropy Amplification",
            "icon": "⚡",
            "base_cost": 1000,
            "cost_multiplier": 10,
            "effect": 2,  # 2x multiplier
            "max_level": 10,
            "description": "Multiplies ALL production by 2×",
        },
        "click_power": {
            "id": "click_power",
            "name": "Click Power",
            "icon": "👆",
            "base_cost": 500,
            "cost_multiplier": 3,
            "effect": 10,  # +10 bits per click
            "max_level": 15,
            "description": "Increases click value by +10 bits",
        },
    },
}

# Hardware Generations Configuration
HARDWARE_GENERATIONS = {
    0: {
        "name": "Mainframe Era (1960s)",
        "description": "Massive room-sized computers",
        "storage_capacity": 128 * 1024 * 1024,  # 128 MB threshold
        "unlock_categories": ["cpu"],
        "primary_category": "cpu",
        "visual_theme": "mainframe",
        "icon": "🖥️",
    },
    1: {
        "name": "Apple II Era (1977)",
        "description": "Personal computer revolution begins",
        "storage_capacity": 512 * 1024 * 1024,  # 512 MB threshold
        "unlock_categories": ["cpu", "ram"],
        "primary_category": "ram",
        "visual_theme": "apple2",
        "icon": "🍎",
    },
    2: {
        "name": "IBM PC Era (1981)",
        "description": "Business computing standardization",
        "storage_capacity": 2 * 1024 * 1024 * 1024,  # 2 GB threshold
        "unlock_categories": ["cpu", "ram", "storage"],
        "primary_category": "storage",
        "visual_theme": "ibmpc",
        "icon": "💼",
    },
    3: {
        "name": "Multimedia Era (1990s)",
        "description": "Sound and graphics cards emerge",
        "storage_capacity": 8 * 1024 * 1024 * 1024,  # 8 GB threshold
        "unlock_categories": ["cpu", "ram", "storage", "gpu"],
        "primary_category": "gpu",
        "visual_theme": "multimedia",
        "icon": "🎮",
    },
    4: {
        "name": "Internet Era (2000s)",
        "description": "Broadband and networking revolution",
        "storage_capacity": 32 * 1024 * 1024 * 1024,  # 32 GB threshold
        "unlock_categories": ["cpu", "ram", "storage", "gpu", "network"],
        "primary_category": "network",
        "visual_theme": "internet",
        "icon": "🌐",
    },
    5: {
        "name": "Mobile Era (2010s)",
        "description": "Smartphones and cloud computing",
        "storage_capacity": 128 * 1024 * 1024 * 1024,  # 128 GB threshold
        "unlock_categories": ["cpu", "ram", "storage", "gpu", "network", "mobile"],
        "primary_category": "mobile",
        "visual_theme": "mobile",
        "icon": "📱",
    },
    6: {
        "name": "AI Era (2020s)",
        "description": "Machine learning and quantum computing",
        "storage_capacity": 512 * 1024 * 1024 * 1024,  # 512 GB threshold
        "unlock_categories": [
            "cpu",
            "ram",
            "storage",
            "gpu",
            "network",
            "mobile",
            "ai",
        ],
        "primary_category": "ai",
        "visual_theme": "ai",
        "icon": "🤖",
    },
}

# Hardware Categories
HARDWARE_CATEGORIES = {
    "cpu": {
        "name": "CPU",
        "description": "Central Processing Unit - The brain of the computer",
        "icon": "🧠",
        "color": (255, 100, 100),  # Red
    },
    "ram": {
        "name": "RAM",
        "description": "Random Access Memory - Temporary workspace",
        "icon": "⚡",
        "color": (100, 255, 100),  # Green
    },
    "storage": {
        "name": "Storage",
        "description": "Hard Drive - Permanent data storage",
        "icon": "💾",
        "color": (100, 100, 255),  # Blue
    },
    "gpu": {
        "name": "GPU",
        "description": "Graphics Processing Unit - Visual computing",
        "icon": "🎮",
        "color": (255, 100, 255),  # Magenta
    },
    "network": {
        "name": "Network",
        "description": "Network Adapter - Internet connectivity",
        "icon": "🌐",
        "color": (100, 255, 255),  # Cyan
    },
    "mobile": {
        "name": "Mobile",
        "description": "Mobile Processor - Portable computing",
        "icon": "📱",
        "color": (255, 255, 100),  # Yellow
    },
    "ai": {
        "name": "AI",
        "description": "AI Accelerator - Machine learning hardware",
        "icon": "🤖",
        "color": (255, 165, 0),  # Orange
    },
}


# Ensure we have generators and upgrades from CONFIG if TOON loading failed
def ensure_config_loaded():
    global GENERATORS, UPGRADES
    if not GENERATORS:
        GENERATORS = CONFIG["GENERATORS"]
        print("Using hardcoded generators from CONFIG")
    if not UPGRADES:
        UPGRADES = CONFIG["UPGRADES"]
        print("Using hardcoded upgrades from CONFIG")


# Call this after CONFIG is defined
ensure_config_loaded()


class GameState:
    def __init__(self):
        self.bits: int = 0
        self.total_bits_earned = 0
        self.total_clicks = 0
        self.start_time = pygame.time.get_ticks()
        self.total_play_time = 0
        self.last_save_time = pygame.time.get_ticks()

        # Generators
        self.generators = {}
        self.unlocked_generators = ["rng"]

        # Upgrades
        self.upgrades = {}

        # Tutorial state
        self.tutorial_step = 0
        self.has_seen_tutorial = False

        # Visual settings
        self.visual_settings = {
            "crt_effects": False,  # Off by default
            "binary_rain": True,
            "particle_effects": True,
        }

        # Compression era state
        self.era = "entropy"  # entropy, compression, channel, quantum
        self.compression_tokens = 0
        self.total_compression_tokens = 0
        self.compressed_bits = 0
        self.total_compressed_bits = 0
        self.overhead_rate = 0
        self.efficiency = 1.0

        # Compression generators and upgrades
        self.compression_generators = {}
        self.compression_upgrades = {}

        # Meta progression
        self.total_rebirths = 0
        self.total_lifetime_bits = 0
        self.hardware_generation = 0  # 0=Mainframe, 1=Apple II, 2=IBM PC, etc.
        self.unlocked_hardware_categories = ["cpu"]  # Start with CPU only

        # Initialize structures
        self.initialize_structures()

    def initialize_structures(self):
        # Initialize basic generators
        for gen_id in CONFIG["GENERATORS"]:
            self.generators[gen_id] = {"count": 0, "total_bought": 0}

        # Initialize hardware-specific generators
        if "HARDWARE_GENERATORS" in CONFIG:
            for gen_id in CONFIG["HARDWARE_GENERATORS"]:
                self.generators[gen_id] = {"count": 0, "total_bought": 0}

        # Initialize basic upgrades
        for upgrade_id in CONFIG["UPGRADES"]:
            self.upgrades[upgrade_id] = {"level": 0}

        # Initialize hardware-specific upgrades
        if "HARDWARE_UPGRADES" in CONFIG:
            for upgrade_id in CONFIG["HARDWARE_UPGRADES"]:
                self.upgrades[upgrade_id] = {"level": 0}

        # Load compression configs if available
        try:
            compression_gens = load_toon_file("config/compression_generators.toon")
            if "compression_generators" in compression_gens:
                for gen in compression_gens["compression_generators"]:
                    self.compression_generators[gen["id"]] = gen

            compression_ups = load_toon_file("config/compression_upgrades.toon")
            if "compression_token_upgrades" in compression_ups:
                for upgrade in compression_ups["compression_token_upgrades"]:
                    self.compression_upgrades[upgrade["id"]] = upgrade
        except:
            # Config files not found, use empty
            pass

        # Initialize compression structures
        for gen_id in self.compression_generators:
            self.compression_generators[gen_id] = {"count": 0, "total_bought": 0}

        for upgrade_id in self.compression_upgrades:
            self.compression_upgrades[upgrade_id] = {"level": 0}

    def get_production_rate(self):
        if self.era == "entropy":
            base_production = 0

            # Calculate from basic generators
            for gen_id, gen_data in self.generators.items():
                if gen_data["count"] > 0 and gen_id in CONFIG["GENERATORS"]:
                    generator = CONFIG["GENERATORS"][gen_id]
                    base_production += gen_data["count"] * generator["base_production"]

            # Calculate from hardware-specific generators
            if "HARDWARE_GENERATORS" in CONFIG:
                for gen_id, gen_data in self.generators.items():
                    if (
                        gen_data["count"] > 0
                        and gen_id in CONFIG["HARDWARE_GENERATORS"]
                    ):
                        generator = CONFIG["HARDWARE_GENERATORS"][gen_id]
                        category = generator["category"]

                        # Only count if this hardware category is unlocked
                        if self.is_hardware_category_unlocked(category):
                            # Apply category-specific multiplier
                            category_multiplier = self.get_category_multiplier(category)
                            production = (
                                gen_data["count"]
                                * generator["base_production"]
                                * category_multiplier
                            )
                            base_production += production

            # Apply entropy amplification multiplier
            entropy_multiplier = math.pow(
                2, self.upgrades["entropy_amplification"]["level"]
            )

            return base_production * entropy_multiplier

        elif self.era == "compression":
            compressed_production = 0
            overhead_production = 0

            # Calculate from compression generators
            for gen_id, gen_data in self.compression_generators.items():
                if gen_data["count"] > 0:
                    generator = self.compression_generators[gen_id]
                    compressed_production += (
                        gen_data["count"] * generator["base_production"]
                    )
                    overhead_production += gen_data["count"] * generator.get(
                        "overhead_production", 0
                    )

            # Apply token bonuses
            compression_ratio_bonus = (
                self.compression_upgrades.get("compression_ratio", {}).get("level", 0)
                * 0.05
            )
            overhead_reduction = overhead_production * compression_ratio_bonus

            # Calculate net production and efficiency
            net_overhead = max(0, overhead_production - overhead_reduction)
            efficiency = (
                compressed_production / (compressed_production + net_overhead)
                if (compressed_production + net_overhead) > 0
                else 1.0
            )

            self.efficiency = efficiency
            self.overhead_rate = net_overhead

            # Apply efficiency penalties
            if efficiency < 0.5:
                penalty = 0.5
            elif efficiency < 0.7:
                penalty = 0.75
            elif efficiency < 0.9:
                penalty = 0.9
            else:
                penalty = 1.0

            return compressed_production * penalty

        return 0

    def get_click_power(self):
        base_click = 1
        click_upgrade_bonus = (
            self.upgrades["click_power"]["level"]
            * CONFIG["UPGRADES"]["click_power"]["effect"]
        )
        return base_click + click_upgrade_bonus

    def get_generator_cost(self, generator_id, quantity=1):
        generator = CONFIG["GENERATORS"][generator_id]
        current_count = self.generators[generator_id]["count"]

        if quantity == 1:
            return int(
                generator["base_cost"]
                * math.pow(generator["cost_multiplier"], current_count)
            )

        # Bulk purchase cost calculation
        first_cost = generator["base_cost"] * math.pow(
            generator["cost_multiplier"], current_count
        )
        ratio = math.pow(generator["cost_multiplier"], quantity) - 1
        denominator = generator["cost_multiplier"] - 1

        return int(first_cost * ratio / denominator)

    def get_upgrade_cost(self, upgrade_id):
        # Check if it's a basic upgrade or hardware upgrade
        if upgrade_id in CONFIG["UPGRADES"]:
            upgrade = CONFIG["UPGRADES"][upgrade_id]
        elif (
            "HARDWARE_UPGRADES" in CONFIG and upgrade_id in CONFIG["HARDWARE_UPGRADES"]
        ):
            upgrade = CONFIG["HARDWARE_UPGRADES"][upgrade_id]
        else:
            return 10**18  # Very large number as "infinite" cost

        return int(
            upgrade["base_cost"]
            * math.pow(upgrade["cost_multiplier"], self.upgrades[upgrade_id]["level"])
        )

    def can_afford(self, cost):
        return self.bits >= cost

    def is_generator_unlocked(self, generator_id):
        generator = CONFIG["GENERATORS"][generator_id]
        if "unlock_threshold" not in generator:
            return True
        return (
            generator_id in self.unlocked_generators
            or self.total_bits_earned >= generator["unlock_threshold"]
        )

    def is_upgrade_unlocked(self, upgrade_id):
        """Check if upgrade is unlocked based on hardware category and bits earned"""
        if upgrade_id in CONFIG["UPGRADES"]:
            # Basic upgrades available from start
            if self.total_bits_earned >= 1000:
                return True
        return False

    def is_hardware_category_unlocked(self, category):
        """Check if a hardware category is unlocked"""
        return category in self.unlocked_hardware_categories

    def get_category_multiplier(self, category):
        """Get the production multiplier for a specific hardware category"""
        if "HARDWARE_UPGRADES" not in CONFIG:
            return 1.0

        # Find the corresponding upgrade for this category
        category_upgrades = {
            "cpu": "overclock",
            "ram": "memory_optimization",
            "storage": "data_compression",
            "gpu": "ray_tracing",
            "network": "bandwidth_boost",
            "mobile": "battery_efficiency",
            "ai": "neural_network",
        }

        upgrade_id = category_upgrades.get(category)
        if upgrade_id and upgrade_id in CONFIG["HARDWARE_UPGRADES"]:
            level = self.upgrades.get(upgrade_id, {}).get("level", 0)
            return math.pow(CONFIG["HARDWARE_UPGRADES"][upgrade_id]["effect"], level)

        return 1.0

    def get_rebirth_progress(self):
        return min(self.total_bits_earned / CONFIG["REBIRTH_THRESHOLD"], 1)

    def get_estimated_rebirth_tokens(self):
        if self.total_bits_earned < CONFIG["REBIRTH_THRESHOLD"]:
            return 0
        return int(math.log2(self.total_bits_earned) - 20)

    def can_rebirth(self):
        return self.total_bits_earned >= self.get_rebirth_threshold()

    def get_rebirth_threshold(self):
        """Get the current rebirth threshold based on hardware generation"""
        if self.hardware_generation >= len(HARDWARE_GENERATIONS) - 1:
            # Final generation - much higher threshold
            return HARDWARE_GENERATIONS[self.hardware_generation]["storage_capacity"]
        return HARDWARE_GENERATIONS[self.hardware_generation]["storage_capacity"]

    def get_hardware_generation_info(self):
        """Get information about current and next hardware generation"""
        current = HARDWARE_GENERATIONS[self.hardware_generation]
        next_gen = None
        if self.hardware_generation < len(HARDWARE_GENERATIONS) - 1:
            next_gen = HARDWARE_GENERATIONS[self.hardware_generation + 1]
        return current, next_gen

    def advance_hardware_generation(self):
        """Advance to the next hardware generation if possible"""
        if self.hardware_generation < len(HARDWARE_GENERATIONS) - 1:
            self.hardware_generation += 1
            new_gen = HARDWARE_GENERATIONS[self.hardware_generation]
            self.unlocked_hardware_categories = new_gen["unlock_categories"]
            return True
        return False

    def perform_rebirth(self):
        if not self.can_rebirth():
            return False

        # Calculate tokens earned based on total bits
        tokens = self.get_estimated_rebirth_tokens()

        # Initialize compression era data if first rebirth
        if not hasattr(self, "compression_tokens"):
            self.compression_tokens = 0
            self.total_compression_tokens = 0
            self.era = "compression"  # Move to compression era
            self.compressed_bits = 0
            self.overhead_rate = 0
            self.efficiency = 1.0

        # Add tokens
        self.compression_tokens += tokens
        self.total_compression_tokens += tokens

        # Check if we should advance hardware generation
        advanced = self.advance_hardware_generation()

        # Reset progress (keep lifetime stats)
        lifetime_bits = self.total_bits_earned
        self.bits = 0
        self.total_bits_earned = 0

        # Reset generators
        for gen_id in self.generators:
            self.generators[gen_id] = {"count": 0, "total_bought": 0}

        # Reset upgrades
        for upgrade_id in self.upgrades:
            self.upgrades[upgrade_id] = {"level": 0}

        # Reset unlocks
        self.unlocked_generators = ["rng"]

        # Update lifetime tracking
        self.total_lifetime_bits = (
            getattr(self, "total_lifetime_bits", 0) + lifetime_bits
        )
        self.total_rebirths = getattr(self, "total_rebirths", 0) + 1

        return True, advanced  # Return whether hardware generation advanced


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
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover_color = hover_color or COLORS["electric_cyan"]
        self.active_color = active_color or COLORS["neon_purple"]
        self.is_hovered = False
        self.is_active = False
        self.font = pygame.font.Font(None, 24)
        self.is_enabled = True
        self.animation_time = 0

    def update(self, mouse_pos):
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos) and self.is_enabled
        if self.is_hovered and not was_hovered:
            self.animation_time = pygame.time.get_ticks()

    def draw(self, screen):
        # Determine base color based on state
        if not self.is_enabled:
            color = (40, 40, 40)  # Dark gray like empty blocks
            border_color = (60, 60, 60)  # Grid line color
            text_color = (80, 80, 80)  # Very dim text
        elif self.is_active:
            color = (50, 200, 50)  # Green like organized blocks
            border_color = (100, 255, 100)
            text_color = self.text_color
        elif self.is_hovered:
            color = (100, 100, 200)  # Blue like organizing blocks
            border_color = (150, 150, 255)
            text_color = self.text_color
        else:
            color = self.color
            border_color = COLORS["muted_blue"]
            text_color = self.text_color

        # Draw flat button background (no rounded corners)
        pygame.draw.rect(screen, color, self.rect)

        # Draw pixel-perfect border (classic Windows style)
        pygame.draw.rect(screen, border_color, self.rect, 2)

        # Add classic inset effect for disabled buttons
        if not self.is_enabled:
            # Inner inset border
            inset_rect = pygame.Rect(
                self.rect.x + 2,
                self.rect.y + 2,
                self.rect.width - 4,
                self.rect.height - 4,
            )
            pygame.draw.rect(screen, (20, 20, 20), inset_rect, 1)

        # Add simple highlight effect for active/hovered states (no glow)
        if (self.is_hovered or self.is_active) and self.is_enabled:
            highlight_rect = pygame.Rect(
                self.rect.x + 2, self.rect.y + 2, self.rect.width - 4, 3
            )
            highlight_color = tuple(min(255, c + 50) for c in border_color)
            pygame.draw.rect(screen, highlight_color, highlight_rect)

        # Draw text with classic monospace appearance
        text_surface = self.font.render(
            self.text,
            True,
            text_color,
        )
        text_rect = text_surface.get_rect(center=self.rect.center)

        # Add text shadow for better readability
        if self.is_enabled:
            shadow_surface = self.font.render(self.text, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(
                center=(text_rect.centerx + 1, text_rect.centery + 1)
            )
            screen.blit(shadow_surface, shadow_rect)

        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and self.rect.collidepoint(event.pos)
            and self.is_enabled
        )


class Particle:
    def __init__(self, x, y, color=COLORS["electric_cyan"], particle_type="burst"):
        self.x = x
        self.y = y
        self.color = color
        self.particle_type = particle_type
        self.lifetime = 1.0
        self.size = random.randint(2, 6)

        if particle_type == "burst":
            self.vx = random.uniform(-150, 150)
            self.vy = random.uniform(-250, -100)
        elif particle_type == "click":
            self.vx = random.uniform(-80, 80)
            self.vy = random.uniform(-150, -50)
        elif particle_type == "purchase":
            # Particles that fly toward accumulator
            target_x, target_y = WINDOW_WIDTH // 2, 200
            dx = target_x - x
            dy = target_y - y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                self.vx = (dx / distance) * random.uniform(100, 200)
                self.vy = (dy / distance) * random.uniform(100, 200)
            else:
                self.vx = random.uniform(-100, 100)
                self.vy = random.uniform(-100, 100)

        self.gravity = 200 if particle_type == "burst" else 100
        self.trail = []  # Store previous positions for trail effect

    def update(self, dt):
        # Store current position in trail
        if len(self.trail) < 5:
            self.trail.append((self.x, self.y, self.lifetime))
        else:
            self.trail.pop(0)
            self.trail.append((self.x, self.y, self.lifetime))

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.lifetime -= dt
        self.vx *= 0.98  # friction

    def draw(self, screen):
        if self.lifetime > 0:
            # Draw trail
            for i, (tx, ty, trail_lifetime) in enumerate(self.trail):
                trail_alpha = int(
                    255 * trail_lifetime * (i + 1) / len(self.trail) * 0.3
                )
                trail_size = max(1, self.size - 2)
                trail_color = tuple(int(c * trail_lifetime) for c in self.color)
                pygame.draw.circle(screen, trail_color, (int(tx), int(ty)), trail_size)

            # Draw main particle with glow
            alpha = int(255 * self.lifetime)

            # Outer glow
            glow_size = self.size + 2
            glow_color = tuple(int(c * 0.3 * self.lifetime) for c in self.color)
            pygame.draw.circle(
                screen, glow_color, (int(self.x), int(self.y)), glow_size
            )

            # Main particle
            main_color = tuple(int(c * self.lifetime) for c in self.color)
            pygame.draw.circle(
                screen, main_color, (int(self.x), int(self.y)), self.size
            )


class BinaryRain:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.columns = []
        self.init_columns()

    def init_columns(self):
        # Create columns of binary rain
        num_columns = self.width // 20
        for i in range(num_columns):
            self.columns.append(
                {
                    "x": i * 20 + random.randint(0, 15),
                    "y": random.randint(-self.height, 0),
                    "speed": random.uniform(30, 80),  # Very slow movement
                    "chars": random.choices(["0", "1"], k=random.randint(5, 15)),
                    # flicker_chance removed to prevent visual artifacts
                }
            )

    def update(self, dt):
        for column in self.columns:
            column["y"] += column["speed"] * dt

            # Reset column when it goes off screen
            if column["y"] > self.height + len(column["chars"]) * 20:
                column["y"] = -len(column["chars"]) * 20
                column["chars"] = random.choices(["0", "1"], k=random.randint(5, 15))
                column["speed"] = random.uniform(30, 80)

            # Removed flicker effect to prevent visual artifacts

    def draw(self, screen):
        font = pygame.font.Font(None, 16)
        for column in self.columns:
            for i, char in enumerate(column["chars"]):
                y_pos = column["y"] + i * 20
                if 0 <= y_pos <= self.height:
                    # Very faint green color
                    alpha = max(10, 30 - i * 2)
                    color = (57, 255, 20) if char == "1" else (20, 100, 20)

                    text_surface = font.render(char, True, color)
                    text_surface.set_alpha(alpha)
                    screen.blit(text_surface, (column["x"], y_pos))


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


class BitVisualization:
    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y
        self.dots = []
        self.spawn_timer = 0
        self.bits_threshold = 100  # Spawn dots based on bits
        self.data_streams = []  # Flowing data streams
        self.pulse_timer = 0
        self.background_particles = []  # Ambient particles

    def update(self, bits, dt):
        # Update pulse effect
        self.pulse_timer += dt * 2

        # Spawn new dots based on bit count
        self.spawn_timer += dt
        spawn_rate = max(0.2, 1.0 - (bits / 10000))  # Slower spawn (reduced from 0.05)

        if self.spawn_timer >= spawn_rate:
            self.spawn_timer = 0
            num_dots = min(
                2, max(1, int(bits / (self.bits_threshold * 2)))
            )  # Fewer dots
            for _ in range(num_dots):
                # Spawn dots in a ring around accumulator, not directly in center
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(100, 150)  # Keep them away from center
                spawn_x = self.center_x + math.cos(angle) * radius
                spawn_y = self.center_y + math.sin(angle) * radius
                self.dots.append(BitDot(spawn_x, spawn_y, bits))

        # Spawn ambient background particles
        if random.random() < 0.03:  # Reduced from 0.1 to 0.03 (3% chance per frame)
            # Avoid spawning particles over accumulator area
            while True:
                x = random.randint(0, WINDOW_WIDTH)
                y = random.randint(0, WINDOW_HEIGHT)
                # Check if particle is not over accumulator center area (200x300 rectangle centered)
                acc_left = WINDOW_WIDTH // 2 - 100
                acc_right = WINDOW_WIDTH // 2 + 100
                acc_top = 150
                acc_bottom = 350
                if not (acc_left <= x <= acc_right and acc_top <= y <= acc_bottom):
                    break  # Found a good position

            self.background_particles.append(
                {
                    "x": x,
                    "y": y,
                    "vx": random.uniform(-20, 20),
                    "vy": random.uniform(-30, -10),
                    "size": random.randint(1, 2),  # Smaller particles (reduced from 3)
                    "lifetime": random.uniform(3, 8),
                    "color": random.choice(
                        [
                            COLORS["electric_cyan"],
                            COLORS["neon_purple"],
                            COLORS["matrix_green"],
                        ]
                    ),
                }
            )

        # Spawn data streams for higher production
        if bits > 1000 and random.random() < 0.02:  # 2% chance when production is high
            self.data_streams.append(
                {
                    "start_x": random.randint(100, WINDOW_WIDTH - 100),
                    "start_y": 0,
                    "end_x": self.center_x + random.randint(-100, 100),
                    "end_y": self.center_y,
                    "progress": 0,
                    "speed": random.uniform(0.5, 2.0),
                    "width": random.randint(2, 5),
                    "color": random.choice(
                        [COLORS["electric_cyan"], COLORS["neon_purple"]]
                    ),
                }
            )

        # Update existing dots
        self.dots = [dot for dot in self.dots if dot.lifetime > 0]
        for dot in self.dots:
            dot.update(dt)

        # Update background particles
        self.background_particles = [
            p for p in self.background_particles if p["lifetime"] > 0
        ]
        for particle in self.background_particles:
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["lifetime"] -= dt

        # Update data streams
        self.data_streams = [s for s in self.data_streams if s["progress"] < 1.0]
        for stream in self.data_streams:
            stream["progress"] += stream["speed"] * dt

    def draw(self, screen):
        # Draw background particles
        for particle in self.background_particles:
            alpha = particle["lifetime"] / 8.0  # Normalize to 0-1
            color = tuple(int(c * alpha) for c in particle["color"])
            # Ensure color values are valid (0-255)
            color = tuple(max(0, min(255, c)) for c in color)
            pygame.draw.circle(
                screen,
                color,
                (int(particle["x"]), int(particle["y"])),
                particle["size"],
            )

        # Draw data streams
        for stream in self.data_streams:
            if stream["progress"] > 0:
                current_x = (
                    stream["start_x"]
                    + (stream["end_x"] - stream["start_x"]) * stream["progress"]
                )
                current_y = (
                    stream["start_y"]
                    + (stream["end_y"] - stream["start_y"]) * stream["progress"]
                )

                # Draw stream as connected dots
                trail_length = 5
                for i in range(trail_length):
                    trail_progress = max(0, stream["progress"] - (i * 0.02))
                    if trail_progress > 0:
                        trail_x = (
                            stream["start_x"]
                            + (stream["end_x"] - stream["start_x"]) * trail_progress
                        )
                        trail_y = (
                            stream["start_y"]
                            + (stream["end_y"] - stream["start_y"]) * trail_progress
                        )
                        alpha = (1.0 - i / trail_length) * (1.0 - stream["progress"])
                        color = tuple(int(c * alpha) for c in stream["color"])
                        # Ensure color values are valid (0-255)
                        color = tuple(max(0, min(255, c)) for c in color)
                        pygame.draw.circle(
                            screen,
                            color,
                            (int(trail_x), int(trail_y)),
                            stream["width"] - i,
                        )

        # Draw main bit dots with enhanced glow
        for dot in self.dots:
            # Add extra glow effect
            if dot.lifetime > 0.5:
                glow_size = dot.size + 4
                glow_alpha = (dot.lifetime - 0.5) * 0.3
                glow_color = tuple(int(c * glow_alpha) for c in COLORS["electric_cyan"])
                pygame.draw.circle(
                    screen, glow_color, (int(dot.x), int(dot.y)), glow_size
                )

            dot.draw(screen)

        # Draw central pulse effect
        if self.pulse_timer > 0:
            pulse_radius = int(abs(math.sin(self.pulse_timer)) * 30)
            pulse_alpha = abs(math.sin(self.pulse_timer)) * 0.3
            pulse_color = tuple(int(c * pulse_alpha) for c in COLORS["electric_cyan"])
            pygame.draw.circle(
                screen, pulse_color, (self.center_x, self.center_y), pulse_radius, 2
            )


class MotherboardBitGrid:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Motherboard component definitions
        self.components = {
            "CPU": {
                "x_ratio": 0.35,
                "y_ratio": 0.35,
                "width_ratio": 0.3,
                "height_ratio": 0.3,
                "bits": 16,
                "unlocked": True,
                "level": 1,
                "color": (200, 50, 50),
                "name": "CPU",
            },
            "BUS": {
                "x_ratio": 0.25,
                "y_ratio": 0.15,
                "width_ratio": 0.5,
                "height_ratio": 0.15,
                "bits": 8,
                "unlocked": True,
                "level": 1,
                "color": (100, 100, 150),
                "name": "BUS",
            },
            "RAM": {
                "x_ratio": 0.05,
                "y_ratio": 0.4,
                "width_ratio": 0.25,
                "height_ratio": 0.4,
                "bits": 32,
                "unlocked": False,
                "level": 0,
                "color": (50, 200, 50),
                "name": "RAM",
            },
            "STORAGE": {
                "x_ratio": 0.7,
                "y_ratio": 0.4,
                "width_ratio": 0.25,
                "height_ratio": 0.4,
                "bits": 64,
                "unlocked": False,
                "level": 0,
                "color": (50, 100, 200),
                "name": "STORAGE",
            },
            "GPU": {
                "x_ratio": 0.65,
                "y_ratio": 0.05,
                "width_ratio": 0.3,
                "height_ratio": 0.25,
                "bits": 32,
                "unlocked": False,
                "level": 0,
                "color": (200, 50, 200),
                "name": "GPU",
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

        # Colors
        self.colors = {
            0: (40, 40, 40),  # 0 bit (dark gray)
            1: (50, 200, 50),  # 1 bit (green)
            "transitioning": (100, 150, 100),  # Transitioning state
            "component_border": (120, 120, 140),  # Component borders
            "locked": (30, 30, 30),  # Locked component color
            "connection": (80, 80, 100),  # Connection lines
        }

    def update(self, bits, total_bits_earned, rebirth_threshold):
        # Store current state
        self.total_bits_earned = total_bits_earned
        self.last_rebirth_progress = min(1.0, total_bits_earned / rebirth_threshold)

        # Unlock components based on progress
        self._update_component_unlocks()

        # Update bits based on current progress
        self._update_bits_to_progress()

        # Animate based on production
        production_rate = max(0, bits - self.last_bits_count)
        if production_rate > 0:
            self._animate_production(production_rate)

        # Update animations
        self._update_animations()

        # Store current state
        self.last_bits_count = bits

    def _update_component_unlocks(self):
        """Unlock components based on progress"""
        progress = self.last_rebirth_progress

        if progress >= 0.1:
            self.components["RAM"]["unlocked"] = True
        if progress >= 0.3:
            self.components["STORAGE"]["unlocked"] = True
        if progress >= 0.5:
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
        """Update bits to match current progress - only if there's available space"""
        # Don't accumulate if all unlocked components are full
        if self._are_all_unlocked_components_full():
            return

        # Calculate actual fill progress based on available capacity
        total_capacity = self._get_total_capacity()
        current_filled = self._get_current_filled_bits()

        if total_capacity == 0:
            return

        # Use a combination of rebirth progress and actual fill state
        # This ensures bits correspond to game state progression
        fill_progress = current_filled / total_capacity
        rebirth_progress = self.last_rebirth_progress

        # Use the higher of the two to ensure progression doesn't stall
        effective_progress = max(fill_progress, rebirth_progress)

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
                # Turn some 0s into 1s
                zeros = [i for i, bit in enumerate(comp["bit_states"]) if bit == 0]
                for _ in range(min(target_ones - current_ones, len(zeros))):
                    if zeros:
                        bit_idx = random.choice(zeros)
                        comp["bit_states"][bit_idx] = 1
                        zeros.remove(bit_idx)

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
        """Add a bit flip effect when user clicks"""
        unlocked_comps = [
            name for name, comp in self.components.items() if comp["unlocked"]
        ]
        for _ in range(3):
            if unlocked_comps:
                comp_name = random.choice(unlocked_comps)
                comp = self.components[comp_name]
                bit_idx = random.randint(0, comp["bits"] - 1)
                current_value = comp["bit_states"][bit_idx]
                new_value = 1 - current_value
                self._start_bit_animation(comp_name, bit_idx, current_value, new_value)
                comp["bit_states"][bit_idx] = new_value

    def add_purchase_effect(self):
        """Add cascading effect for purchases"""
        unlocked_comps = [
            name for name, comp in self.components.items() if comp["unlocked"]
        ]
        for _ in range(8):
            if unlocked_comps:
                comp_name = random.choice(unlocked_comps)
                comp = self.components[comp_name]
                bit_idx = random.randint(0, comp["bits"] - 1)
                current_value = comp["bit_states"][bit_idx]
                new_value = 1 if current_value == 0 else 0
                self._start_bit_animation(comp_name, bit_idx, current_value, new_value)
                comp["bit_states"][bit_idx] = new_value

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


class FloatingText:
    def __init__(self, x, y, text, color=COLORS["matrix_green"]):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = 1.0
        self.vy = -50
        self.font = pygame.font.Font(None, 32)

    def update(self, dt):
        self.y += self.vy * dt
        self.lifetime -= dt

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * self.lifetime)
            text_surface = self.font.render(self.text, True, self.color)
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, (self.x, self.y))


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
        # Try to load monospace font
        try:
            self.monospace_font = pygame.font.SysFont("Courier New", 24)
        except:
            self.monospace_font = pygame.font.Font(None, 24)

        # Game state
        self.state = GameState()

        # Visual systems
        self.binary_rain = BinaryRain(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.bit_visualization = BitVisualization(WINDOW_WIDTH // 2, 200)

        # Bit grid for accumulator visualization
        self.bit_grid = MotherboardBitGrid(
            WINDOW_WIDTH // 2 - 200,
            140,
            400,
            200,  # Position within accumulator area
        )

        # UI elements
        self.click_button = Button(
            WINDOW_WIDTH // 2 - 150, 420, 300, 60, "+1 bit", (60, 60, 80)
        )

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

        # Panel toggle buttons (start in collapsed state)
        # Position them safely below click button to avoid overlap
        self.generators_toggle = Button(
            50, 480, 600, 30, "▶ DATA SOURCES", (50, 50, 70)
        )
        self.upgrades_toggle = Button(
            700, 480, 450, 30, "▶ OPTIMIZATIONS", (50, 50, 70)
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

        # Update accumulator and bit grid
        self.bit_grid.x = int(new_width // 2 - 200 * scale_x)
        self.bit_grid.width = int(400 * scale_x)
        self.bit_grid.height = int(200 * scale_y)

        # Update click button
        self.click_button.rect.x = int(new_width // 2 - 150 * scale_x)
        self.click_button.rect.y = int(420 * scale_y)
        self.click_button.rect.width = int(300 * scale_x)
        self.click_button.rect.height = int(60 * scale_y)

        # Update header buttons
        self.settings_button.rect.x = int(new_width - 150 * scale_x)
        self.stats_button.rect.x = int(new_width - 280 * scale_x)

        # Update panel positions
        self.generators_toggle.rect.x = int(50 * scale_x)
        self.generators_toggle.rect.y = int(480 * scale_y)
        self.generators_toggle.rect.width = int(600 * scale_x)

        self.upgrades_toggle.rect.x = int(700 * scale_x)
        self.upgrades_toggle.rect.y = int(480 * scale_y)
        self.upgrades_toggle.rect.width = int(450 * scale_x)

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

        for i, (gen_id, generator) in enumerate(CONFIG["GENERATORS"].items()):
            y = y_start + i * (card_height + 10)

            # Buy buttons
            card_height = 95 if "category" in generator else 80
            button_y = y + card_height - 35
            buy_x1 = Button(x_start + card_width - 180, button_y, 70, 30, "BUY x1")
            buy_x10 = Button(x_start + card_width - 100, button_y, 70, 30, "BUY x10")

            self.generator_buy_buttons[gen_id] = {"x1": buy_x1, "x10": buy_x10}

    def setup_upgrade_buttons(self):
        x_start = 750
        y_start = 200
        card_height = 120

        for i, (upgrade_id, upgrade) in enumerate(CONFIG["UPGRADES"].items()):
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

            # Handle generator purchases (only when panel is open)
            if self.generators_panel_open:
                for gen_id, buttons in self.generator_buy_buttons.items():
                    if buttons["x1"].is_clicked(event):
                        self.buy_generator(gen_id, 1)
                    elif buttons["x10"].is_clicked(event):
                        self.buy_generator(gen_id, 10)

            # Handle upgrade purchases (only when panel is open)
            if self.upgrades_panel_open:
                for upgrade_id, button in self.upgrade_buttons.items():
                    if button.is_clicked(event):
                        self.buy_upgrade(upgrade_id)

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
                # Handle click button
                if self.click_button.is_clicked(event):
                    self.handle_click()

                # Handle generator purchases (only when panel is open)
                if self.generators_panel_open:
                    for gen_id, buttons in self.generator_buy_buttons.items():
                        if buttons["x1"].is_clicked(event):
                            self.buy_generator(gen_id, 1)
                        elif buttons["x10"].is_clicked(event):
                            self.buy_generator(gen_id, 10)

                # Handle upgrade purchases (only when panel is open)
                if self.upgrades_panel_open:
                    for upgrade_id, button in self.upgrade_buttons.items():
                        if button.is_clicked(event):
                            self.buy_upgrade(upgrade_id)

                # Handle header buttons
                if self.settings_button.is_clicked(event):
                    self.showing_settings = True
                elif self.stats_button.is_clicked(event):
                    self.show_statistics()

            # Handle panel toggle buttons
            if self.generators_toggle.is_clicked(event):
                self.generators_panel_open = not self.generators_panel_open
                self.generators_toggle.text = (
                    "▼ INFORMATION SOURCES"
                    if self.generators_panel_open
                    else "▶ INFORMATION SOURCES"
                )
                # Reposition and resize toggle button based on panel state
                if self.generators_panel_open:
                    self.generators_toggle.rect.y = (
                        470  # Position below click button (y=400+60=460) + margin
                    )
                    self.generators_toggle.rect.height = 40
                else:
                    self.generators_toggle.rect.y = (
                        480  # Move down when collapsed to avoid covering click button
                    )
                    self.generators_toggle.rect.height = (
                        30  # Make smaller when collapsed
                    )

            if self.upgrades_toggle.is_clicked(event):
                self.upgrades_panel_open = not self.upgrades_panel_open
                self.upgrades_toggle.text = (
                    "▼ UPGRADES" if self.upgrades_panel_open else "▶ UPGRADES"
                )
                # Reposition and resize toggle button based on panel state
                if self.upgrades_panel_open:
                    self.upgrades_toggle.rect.y = (
                        470  # Position below click button (y=400+60=460) + margin
                    )
                    self.upgrades_toggle.rect.height = 40
                else:
                    self.upgrades_toggle.rect.y = (
                        480  # Move down when collapsed to avoid covering click button
                    )
                    self.upgrades_toggle.rect.height = 30  # Make smaller when collapsed
                    self.upgrades_toggle.rect.height = 30  # Make smaller when collapsed
                    self.upgrades_toggle.rect.height = 30  # Make smaller when collapsed

            # Handle rebirth button
            if self.state.can_rebirth() and self.rebirth_button.is_clicked(event):
                self.showing_rebirth_confirmation = True

        # Update button hover states - only update visible elements
        if not self.showing_settings and not self.showing_rebirth_confirmation:
            self.click_button.update(mouse_pos)
            self.settings_button.update(mouse_pos)
            self.stats_button.update(mouse_pos)

            # Only update toggle buttons when modals are closed
            self.generators_toggle.update(mouse_pos)
            self.upgrades_toggle.update(mouse_pos)

            # Only update panel buttons when panels are open
            if self.generators_panel_open:
                for buttons in self.generator_buy_buttons.values():
                    buttons["x1"].update(mouse_pos)
                    buttons["x10"].update(mouse_pos)

            if self.upgrades_panel_open:
                for button in self.upgrade_buttons.values():
                    button.update(mouse_pos)

            # Update rebirth button if available
            if self.state.can_rebirth():
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

        upgrade = CONFIG["UPGRADES"][upgrade_id]
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

    def upgrade_component(self, comp_name):
        """Upgrade a motherboard component"""
        comp = self.bit_grid.components[comp_name]

        # Calculate upgrade cost based on component and current level
        base_cost = {"CPU": 100, "BUS": 50, "RAM": 200, "STORAGE": 300, "GPU": 400}
        cost_multiplier = 2.5 ** comp["level"]
        cost = int(base_cost.get(comp_name, 100) * cost_multiplier)

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
        production_int = int(production)

        # Only add production if there's space in unlocked components
        if not self.bit_grid._are_all_unlocked_components_full():
            self.state.bits += production_int
            self.state.total_bits_earned += production_int

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
        # Update bit grid with current bits and rebirth progress
        production_rate = self.state.get_production_rate()
        self.bit_grid.update(
            self.state.bits, self.state.total_bits_earned, CONFIG["REBIRTH_THRESHOLD"]
        )

        # Draw accumulator background
        acc_rect = pygame.Rect(
            self.current_width // 2 - int(200 * (self.current_width / self.base_width)),
            int(100 * (self.current_height / self.base_height)),
            int(400 * (self.current_width / self.base_width)),
            int(300 * (self.current_height / self.base_height)),
        )
        center_x = self.current_width // 2
        center_y = int(250 * (self.current_height / self.base_height))

        # Dark background for accumulator
        pygame.draw.rect(self.screen, (10, 10, 20), acc_rect, border_radius=8)

        # Animated glow effect around accumulator
        time_ms = pygame.time.get_ticks()
        glow_intensity = abs(math.sin(time_ms * 0.001)) * 0.3 + 0.2

        # Draw border with classic styling
        border_glow = abs(math.sin(time_ms * 0.002)) * 0.2 + 0.8
        border_color = tuple(int(c * border_glow) for c in COLORS["electric_cyan"])
        pygame.draw.rect(self.screen, border_color, acc_rect, 2, border_radius=8)

        # Title with data accumulator aesthetic
        title_text = self.small_font.render(
            "DATA ACCUMULATOR", True, COLORS["muted_blue"]
        )
        title_rect = title_text.get_rect(center=(center_x, 120))
        self.screen.blit(title_text, title_rect)

        # Draw the bit grid
        self.bit_grid.draw(self.screen)

        # Show bit completeness percentage
        bit_percent = self.bit_grid.get_bit_completeness_percentage()
        progress_text = self.small_font.render(
            f"{bit_percent:.0f}% Complete", True, COLORS["matrix_green"]
        )
        progress_rect = progress_text.get_rect(center=(center_x, 160))
        self.screen.blit(progress_text, progress_rect)

        # Bits display with monospace font
        bits_value = self.state.bits
        if self.state.era == "compression":
            bits_text = self.monospace_font.render(
                f"{self.format_number(self.state.compressed_bits)} cb",
                True,
                COLORS["neon_purple"],
            )
        else:
            bits_text = self.monospace_font.render(
                f"{self.format_number(bits_value)} bits", True, COLORS["electric_cyan"]
            )
        bits_rect = bits_text.get_rect(center=(center_x, 360))

        # Subtle glow effect for text
        for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
            glow_pos = (bits_rect.x + offset[0], bits_rect.y + offset[1])
            glow_surface = bits_text.copy()
            glow_surface.set_alpha(50)
            self.screen.blit(glow_surface, glow_pos)

        self.screen.blit(bits_text, bits_rect)

        # Rate display
        rate = self.state.get_production_rate()
        if self.state.era == "compression":
            efficiency = self.state.efficiency * 100
            rate_text = self.monospace_font.render(
                f"+{self.format_number(rate)} cb/s", True, COLORS["neon_purple"]
            )
            eff_text = self.small_font.render(
                f"Efficiency: {efficiency:.1f}%",
                True,
                COLORS["matrix_green"] if efficiency > 90 else COLORS["signal_orange"],
            )
            eff_rect = eff_text.get_rect(center=(center_x, 385))
            self.screen.blit(eff_text, eff_rect)
        else:
            rate_text = self.monospace_font.render(
                f"+{self.format_number(rate)} b/s", True, COLORS["matrix_green"]
            )

        rate_rect = rate_text.get_rect(center=(center_x, 385))
        self.screen.blit(rate_text, rate_rect)

        # Click button with enhanced appearance
        if self.state.era == "entropy":
            self.click_button.rect.y = 420  # Reposition button lower
            self.click_button.draw(self.screen)
        else:
            # Show different button for compression era
            click_text = self.small_font.render(
                f"Tokens: {self.state.compression_tokens} ⭐", True, COLORS["gold"]
            )
            click_rect = click_text.get_rect(center=(center_x, 420))
            self.screen.blit(click_text, click_rect)

    def draw_generators_panel(self):
        # Draw toggle button when collapsed
        if not self.generators_panel_open:
            # Draw collapsed toggle button
            pygame.draw.rect(self.screen, (40, 40, 50), self.generators_toggle.rect)
            pygame.draw.rect(self.screen, (60, 60, 80), self.generators_toggle.rect, 2)

            # Add inset effect
            inset_rect = pygame.Rect(
                self.generators_toggle.rect.x + 2,
                self.generators_toggle.rect.y + 2,
                self.generators_toggle.rect.width - 4,
                self.generators_toggle.rect.height - 4,
            )
            pygame.draw.rect(self.screen, (20, 20, 30), inset_rect, 1)

            # Draw text with classic styling
            text_color = (120, 120, 140)  # Dimmed classic color
            text_surface = self.small_font.render(
                self.generators_toggle.text, True, text_color
            )
            text_rect = text_surface.get_rect(center=self.generators_toggle.rect.center)
            self.screen.blit(text_surface, text_rect)
        else:
            # Draw normal toggle button
            self.generators_toggle.draw(self.screen)

        if not self.generators_panel_open:
            return

        # Panel background with classic styling
        panel_rect = pygame.Rect(
            50, 520, 600, 200
        )  # Position below expanded toggle button

        # Draw flat dark background like classic interface
        pygame.draw.rect(self.screen, (20, 20, 30), panel_rect)

        # Draw pixel-perfect border (classic Windows style)
        pygame.draw.rect(self.screen, (80, 80, 100), panel_rect, 2)

        # Draw inner border for inset effect
        inner_rect = pygame.Rect(
            panel_rect.x + 2,
            panel_rect.y + 2,
            panel_rect.width - 4,
            panel_rect.height - 4,
        )
        pygame.draw.rect(self.screen, (40, 40, 50), inner_rect, 1)

        # Title with classic styling
        title_text = self.medium_font.render(
            "DATA SOURCES",
            True,
            (100, 200, 255),  # Cyan like scan lines
        )
        title_rect = title_text.get_rect(center=(350, 540))
        self.screen.blit(title_text, title_rect)

        # Generator cards
        y_start = 560  # Adjusted for new panel position

        # Show basic generators first
        basic_generators = GENERATORS if GENERATORS else CONFIG["GENERATORS"]

        # Then show hardware-specific generators that are unlocked
        hardware_generators = {}
        if "HARDWARE_GENERATORS" in CONFIG:
            hardware_generators = CONFIG["HARDWARE_GENERATORS"]

        all_generators = {**basic_generators, **hardware_generators}

        for gen_id, generator in all_generators.items():
            # Check if basic generator is unlocked
            if gen_id in basic_generators:
                if not self.state.is_generator_unlocked(gen_id):
                    continue
            # Check if hardware generator is unlocked by hardware category
            elif gen_id in hardware_generators:
                category = generator["category"]
                if not self.state.is_hardware_category_unlocked(category):
                    continue

            count = self.state.generators[gen_id]["count"]
            cost = self.state.get_generator_cost(gen_id)
            can_afford = self.state.can_afford(cost)

            # Card background with classic block styling
            # Adjust height based on whether this is a hardware generator
            card_height = 85 if "category" in generator else 70
            card_rect = pygame.Rect(60, y_start, 580, card_height)

            # Use classic block colors for card background
            if can_afford:
                card_color = (50, 100, 50)  # Dark green (affordable)
                border_color = (100, 200, 100)  # Light green border
            else:
                card_color = (60, 40, 40)  # Dark red (not affordable)
                border_color = (120, 60, 60)  # Light red border

            # Draw flat card background
            pygame.draw.rect(self.screen, card_color, card_rect)

            # Draw pixel-perfect border
            pygame.draw.rect(self.screen, border_color, card_rect, 2)

            # Add subtle inset effect
            inner_card = pygame.Rect(
                card_rect.x + 2,
                card_rect.y + 2,
                card_rect.width - 4,
                card_rect.height - 4,
            )
            pygame.draw.rect(
                self.screen, tuple(c // 2 for c in card_color), inner_card, 1
            )

            # Add small status indicator block (classic style)
            status_block_rect = pygame.Rect(card_rect.x + 5, card_rect.y + 5, 8, 8)
            if can_afford:
                pygame.draw.rect(
                    self.screen, (100, 255, 100), status_block_rect
                )  # Green
            else:
                pygame.draw.rect(self.screen, (200, 50, 50), status_block_rect)  # Red

            # Draw classic-style grid lines on card
            for i in range(0, card_rect.width, 20):
                pygame.draw.line(
                    self.screen,
                    (40, 40, 40),
                    (card_rect.x + i, card_rect.y + 15),
                    (card_rect.x + i, card_rect.bottom - 5),
                    1,
                )

            # Icon area with classic styling
            icon_rect = pygame.Rect(80, y_start + 10, 80, 50)
            pygame.draw.rect(self.screen, (30, 30, 40), icon_rect)
            pygame.draw.rect(self.screen, border_color, icon_rect, 1)

            # Animated icon (simple animation based on generator type)
            icon_text = generator.get("icon", "🎲")
            icon_font = pygame.font.Font(None, 40)
            icon_surface = icon_font.render(icon_text, True, COLORS["electric_cyan"])
            icon_text_rect = icon_surface.get_rect(center=icon_rect.center)

            # Add subtle pulse effect
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.001)) * 0.1 + 0.9
            icon_surface.set_alpha(int(255 * pulse))
            self.screen.blit(icon_surface, icon_text_rect)

            # Generator name and count with classic styling
            name_text = self.small_font.render(
                f"{generator['name']}",
                True,
                (200, 200, 200),  # Light gray like old UI
            )
            self.screen.blit(name_text, (180, y_start + 8))

            # Show hardware category if this is a hardware generator
            if "category" in generator:
                category_info = HARDWARE_CATEGORIES[generator["category"]]
                category_text = self.tiny_font.render(
                    f"{category_info['icon']} {category_info['name']}",
                    True,
                    category_info["color"],
                )
                self.screen.blit(category_text, (180, y_start + 28))

                count_text = self.tiny_font.render(
                    f"QUANTITY: {count}",
                    True,
                    (100, 200, 255),  # Cyan like scan lines
                )
                self.screen.blit(count_text, (180, y_start + 44))

                # Production rate with classic styling
                category_multiplier = self.state.get_category_multiplier(
                    generator["category"]
                )
                production = count * generator["base_production"] * category_multiplier
                prod_text = self.small_font.render(
                    f"RATE: +{self.format_number(production)} b/s",
                    True,
                    (50, 200, 50),  # Defrag green
                )
                self.screen.blit(prod_text, (180, y_start + 60))
            else:
                count_text = self.tiny_font.render(
                    f"QUANTITY: {count}",
                    True,
                    (100, 200, 255),  # Cyan like scan lines
                )
                self.screen.blit(count_text, (180, y_start + 28))

                # Production rate with classic styling
                production = count * generator["base_production"]
                prod_text = self.small_font.render(
                    f"RATE: +{self.format_number(production)} b/s",
                    True,
                    (50, 200, 50),  # Defrag green
                )
                self.screen.blit(prod_text, (180, y_start + 48))

            # Flavor text
            flavor_text = self.tiny_font.render(
                generator["flavor"], True, COLORS["muted_blue"]
            )
            flavor_rect = flavor_text.get_rect()
            flavor_rect.topleft = (180, y_start + 85)
            # Word wrap for long flavor text
            words = generator["flavor"].split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                test_text = " ".join(current_line)
                test_surface = self.tiny_font.render(
                    test_text, True, COLORS["muted_blue"]
                )
                if test_surface.get_width() > 300:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [word]
            lines.append(" ".join(current_line))

            for i, line in enumerate(lines[:2]):  # Max 2 lines
                line_text = self.tiny_font.render(line, True, COLORS["muted_blue"])
                self.screen.blit(line_text, (180, y_start + 85 + i * 15))

            # Cost display with classic styling
            cost_color = (
                (50, 200, 50) if can_afford else (200, 50, 50)
            )  # Defrag green/red
            cost_text = self.small_font.render(
                f"COST: {self.format_number(cost)} bits", True, cost_color
            )
            self.screen.blit(cost_text, (400, y_start + 35))

            # Progress bar with classic block styling
            if not can_afford:
                progress = self.state.bits / cost
                progress_bg = pygame.Rect(400, y_start + 55, 150, 10)
                progress_fill = pygame.Rect(400, y_start + 55, int(150 * progress), 10)

                # Draw background with block style
                pygame.draw.rect(self.screen, (40, 40, 40), progress_bg)
                pygame.draw.rect(self.screen, (60, 60, 60), progress_bg, 1)

                # Draw fill with classic green blocks
                if progress > 0:
                    pygame.draw.rect(self.screen, (50, 150, 50), progress_fill)
                    # Add small block indicators
                    for i in range(0, int(150 * progress), 15):
                        block_rect = pygame.Rect(400 + i, y_start + 55, 13, 10)
                        pygame.draw.rect(self.screen, (70, 200, 70), block_rect)
                        pygame.draw.rect(self.screen, (90, 220, 90), block_rect, 1)

            # Update button states
            self.generator_buy_buttons[gen_id]["x1"].is_enabled = can_afford
            self.generator_buy_buttons[gen_id]["x10"].is_enabled = can_afford

            # Update button positions for expanded panel
            card_height = 85 if "category" in generator else 70
            button_y = y_start + card_height - 35
            self.generator_buy_buttons[gen_id]["x1"].rect.y = button_y
            self.generator_buy_buttons[gen_id]["x10"].rect.y = button_y
            self.generator_buy_buttons[gen_id]["x1"].rect.x = 60 + 400
            self.generator_buy_buttons[gen_id]["x10"].rect.x = 60 + 480

            # Draw buttons
            self.generator_buy_buttons[gen_id]["x1"].draw(self.screen)
            self.generator_buy_buttons[gen_id]["x10"].draw(self.screen)

            # Adjust spacing based on card type
            spacing = 95 if "category" in generator else 80
            y_start += spacing

    def draw_upgrades_panel(self):
        # Draw toggle button with adjusted appearance when collapsed
        if not self.upgrades_panel_open:
            # Draw collapsed toggle button with classic style
            pygame.draw.rect(self.screen, (40, 40, 50), self.upgrades_toggle.rect)
            pygame.draw.rect(self.screen, (60, 60, 80), self.upgrades_toggle.rect, 2)

            # Add inset effect
            inset_rect = pygame.Rect(
                self.upgrades_toggle.rect.x + 2,
                self.upgrades_toggle.rect.y + 2,
                self.upgrades_toggle.rect.width - 4,
                self.upgrades_toggle.rect.height - 4,
            )
            pygame.draw.rect(self.screen, (20, 20, 30), inset_rect, 1)

            # Draw text with classic styling
            text_color = (120, 120, 140)  # Dimmed classic color
            text_surface = self.small_font.render(
                self.upgrades_toggle.text, True, text_color
            )
            text_rect = text_surface.get_rect(center=self.upgrades_toggle.rect.center)
            self.screen.blit(text_surface, text_rect)
        else:
            # Draw normal toggle button
            self.upgrades_toggle.draw(self.screen)

        if not self.upgrades_panel_open:
            return

        # Panel background with classic styling
        panel_rect = pygame.Rect(
            700, 520, 450, 200
        )  # Position below expanded toggle button

        # Draw flat dark background like classic interface
        pygame.draw.rect(self.screen, (20, 20, 30), panel_rect)

        # Draw pixel-perfect border (classic Windows style)
        pygame.draw.rect(self.screen, (80, 80, 100), panel_rect, 2)

        # Draw inner border for inset effect
        inner_rect = pygame.Rect(
            panel_rect.x + 2,
            panel_rect.y + 2,
            panel_rect.width - 4,
            panel_rect.height - 4,
        )
        pygame.draw.rect(self.screen, (40, 40, 50), inner_rect, 1)

        # Title with classic styling
        title_text = self.medium_font.render(
            "SYSTEM OPTIMIZATIONS", True, (150, 100, 200)
        )  # Purple accent
        title_rect = title_text.get_rect(center=(925, 540))
        self.screen.blit(title_text, title_rect)

        # Upgrade cards
        y_start = 540  # Adjusted for new panel position

        # Show basic upgrades first
        basic_upgrades = UPGRADES if UPGRADES else CONFIG["UPGRADES"]

        # Then show hardware-specific upgrades that are unlocked
        hardware_upgrades = {}
        if "HARDWARE_UPGRADES" in CONFIG:
            hardware_upgrades = CONFIG["HARDWARE_UPGRADES"]

        all_upgrades = {**basic_upgrades, **hardware_upgrades}

        for upgrade_id, upgrade in all_upgrades.items():
            # Check if basic upgrade is unlocked
            if upgrade_id in basic_upgrades:
                if not self.state.is_upgrade_unlocked(upgrade_id):
                    continue
            # Check if hardware upgrade is unlocked by hardware category
            elif upgrade_id in hardware_upgrades:
                category = upgrade["category"]
                if not self.state.is_hardware_category_unlocked(category):
                    continue

            level = self.state.upgrades[upgrade_id]["level"]
            cost = self.state.get_upgrade_cost(upgrade_id)
            can_afford = self.state.can_afford(cost) and level < upgrade["max_level"]

            # Card background with classic block styling
            # Adjust height based on whether this is a hardware upgrade
            card_height = 75 if "category" in upgrade else 60
            card_rect = pygame.Rect(710, y_start, 430, card_height)

            # Use classic block colors for card background
            if can_afford:
                card_color = (50, 40, 80)  # Dark purple (affordable)
                border_color = (150, 100, 200)  # Light purple border
            else:
                card_color = (60, 40, 40)  # Dark red (not affordable)
                border_color = (120, 60, 60)  # Light red border

            # Draw flat card background
            pygame.draw.rect(self.screen, card_color, card_rect)

            # Draw pixel-perfect border
            pygame.draw.rect(self.screen, border_color, card_rect, 2)

            # Add subtle inset effect
            inner_card = pygame.Rect(
                card_rect.x + 2,
                card_rect.y + 2,
                card_rect.width - 4,
                card_rect.height - 4,
            )
            pygame.draw.rect(
                self.screen, tuple(c // 2 for c in card_color), inner_card, 1
            )

            # Add small status indicator block (classic style)
            status_block_rect = pygame.Rect(card_rect.x + 5, card_rect.y + 5, 8, 8)
            if can_afford:
                pygame.draw.rect(
                    self.screen, (200, 150, 255), status_block_rect
                )  # Purple
            else:
                pygame.draw.rect(self.screen, (200, 50, 50), status_block_rect)  # Red

            # Draw classic-style grid lines on card
            for i in range(0, card_rect.width, 20):
                pygame.draw.line(
                    self.screen,
                    (40, 40, 40),
                    (card_rect.x + i, card_rect.y + 15),
                    (card_rect.x + i, card_rect.bottom - 5),
                    1,
                )

            # Icon area (32x32)
            icon_text = upgrade.get("icon", "⚡")
            icon_font = pygame.font.Font(None, 32)

            # Use hardware category color if applicable
            icon_color = COLORS["neon_purple"]
            if "category" in upgrade:
                icon_color = HARDWARE_CATEGORIES[upgrade["category"]]["color"]

            icon_surface = icon_font.render(icon_text, True, icon_color)
            self.screen.blit(icon_surface, (720, y_start + 10))

            # Upgrade name
            name_text = self.small_font.render(
                f"{upgrade['name']}", True, COLORS["soft_white"]
            )
            self.screen.blit(name_text, (765, y_start + 10))

            # Show hardware category if this is a hardware upgrade
            if "category" in upgrade:
                category_info = HARDWARE_CATEGORIES[upgrade["category"]]
                category_text = self.tiny_font.render(
                    f"{category_info['icon']} {category_info['name']}",
                    True,
                    category_info["color"],
                )
                self.screen.blit(category_text, (765, y_start + 30))

            # Description
            desc_text = self.tiny_font.render(
                upgrade["description"], True, COLORS["muted_blue"]
            )
            self.screen.blit(desc_text, (720, y_start + 35))

            # Current effect
            if level > 0:
                if upgrade_id == "entropy_amplification":
                    effect_text = f"Currently: ×{math.pow(2, level):.0f} boost"
                elif "category" in upgrade:
                    category = upgrade["category"]
                    effect_text = f"Currently: ×{math.pow(upgrade['effect'], level):.1f} {category.upper()}"
                else:
                    effect_text = f"Currently: +{level * upgrade['effect']} bits"

                effect_surface = self.tiny_font.render(
                    effect_text, True, COLORS["neon_purple"]
                )

                # Adjust position based on whether this is a hardware upgrade
                effect_y = y_start + (70 if "category" in upgrade else 55)
                self.screen.blit(effect_surface, (720, effect_y))

            # Cost and button
            if level < upgrade["max_level"]:
                cost_color = (
                    COLORS["neon_purple"] if can_afford else COLORS["red_error"]
                )
                cost_text = self.tiny_font.render(
                    f"Cost: {self.format_number(cost)} bits", True, cost_color
                )

                # Adjust position based on whether this is a hardware upgrade
                cost_y = y_start + (90 if "category" in upgrade else 75)
                button_y = y_start + (90 if "category" in upgrade else 75)

                self.screen.blit(cost_text, (720, cost_y))

                # Update button position and draw
                self.upgrade_buttons[upgrade_id].rect.y = button_y
                self.upgrade_buttons[upgrade_id].is_enabled = can_afford
                self.upgrade_buttons[upgrade_id].draw(self.screen)
            else:
                # Golden MAX LEVEL text
                max_text = self.small_font.render("MAX LEVEL", True, COLORS["gold"])
                max_y = y_start + (90 if "category" in upgrade else 75)
                self.screen.blit(max_text, (720, max_y))

            # Adjust spacing based on card type
            spacing = 85 if "category" in upgrade else 70
            y_start += spacing

        # Draw component upgrade buttons
        for comp_name, button in self.component_upgrade_buttons.items():
            comp = self.bit_grid.components[comp_name]

            if comp["unlocked"]:
                # Calculate upgrade cost
                base_cost = {
                    "CPU": 100,
                    "BUS": 50,
                    "RAM": 200,
                    "STORAGE": 300,
                    "GPU": 400,
                }
                cost_multiplier = 2.5 ** comp["level"]
                cost = int(base_cost.get(comp_name, 100) * cost_multiplier)
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
        current_gen, next_gen = self.state.get_hardware_generation_info()
        rebirth_threshold = self.state.get_rebirth_threshold()

        # Rebirth progress
        progress = self.state.total_bits_earned / rebirth_threshold
        tokens = self.state.get_estimated_rebirth_tokens()
        current_mb = self.format_number(self.state.total_bits_earned / (1024 * 1024))
        target_mb = self.format_number(rebirth_threshold / (1024 * 1024))

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

        # Show rebirth button if available
        if progress >= 1.0:
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

        # Progress text with monospace font
        progress_text = self.monospace_font.render(
            f"({current_mb} MB / {target_mb} MB) {int(progress * 100)}%",
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

        # Removed flicker effect to prevent visual artifacts

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

            # Continue button (responsive with hover)
            continue_button_rect = pygame.Rect(
                self.current_width // 2 - 100, self.current_height // 2 + 60, 200, 40
            )
            # Add hover effect
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

    def handle_settings_events(self, event):
        mouse_pos = pygame.mouse.get_pos()

        # Settings toggle buttons positions
        crt_toggle_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 250, 400, 40)
        rain_toggle_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 300, 400, 40)
        particle_toggle_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 350, 400, 40)

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

    def show_statistics(self):
        # This would show a statistics modal, for now just print to console
        print(f"""
=== STATISTICS ===
Time Played: {(pygame.time.get_ticks() - self.state.start_time) // 1000}s
Total Bits Earned: {self.format_number(self.state.total_bits_earned)}
Current Production: {self.format_number(self.state.get_production_rate())} b/s
Total Clicks: {self.state.total_clicks}
==================
        """)

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

        scale_x = self.current_width / self.base_width
        scale_y = self.current_height / self.base_height

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

        # Instructions
        inst_text = self.tiny_font.render(
            "Click any setting to toggle • Press ESC to close",
            True,
            COLORS["muted_blue"],
        )
        inst_rect = inst_text.get_rect(
            center=(self.current_width // 2, int(450 * scale_y))
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

        # Create floating text for tokens earned
        if hasattr(self.state, "compression_tokens"):
            current_tokens = self.state.compression_tokens
            self.floating_texts.append(
                FloatingText(
                    center_x,
                    center_y - 50,
                    f"+{current_tokens} ⭐ TOKENS!",
                    COLORS["gold"],
                )
            )
            # Add more particles for the rebirth effect
            for _ in range(10):
                particle_color = random.choice(
                    [COLORS["electric_cyan"], COLORS["neon_purple"], COLORS["gold"]]
                )
                self.particles.append(
                    Particle(center_x, center_y, particle_color, "burst")
                )

        # Create floating text for tokens earned
        if hasattr(self.state, "compression_tokens"):
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

        for _ in range(100):  # Double the normal rebirth effect
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
        if self.state.has_seen_tutorial:
            return

        step = self.state.tutorial_step

        if step == 0 and self.state.total_bits_earned >= 5:
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

        # Create floating text for tokens earned
        tokens = self.state.total_compression_tokens - getattr(
            self.state, "total_compression_tokens", 0
        )
        if hasattr(self.state, "compression_tokens"):
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
            },
            # Hardware-specific generators and upgrades
            "HARDWARE_GENERATORS": {
                # CPU generators
                "cpu_core": {
                    "id": "cpu_core",
                    "name": "CPU Core",
                    "category": "cpu",
                    "base_cost": 50,
                    "base_production": 5,
                    "cost_multiplier": 1.15,
                    "icon": "🧠",
                    "flavor": "The heart of computation.",
                },
                "cpu_cache": {
                    "id": "cpu_cache",
                    "name": "CPU Cache",
                    "category": "cpu",
                    "base_cost": 500,
                    "base_production": 50,
                    "cost_multiplier": 1.15,
                    "icon": "⚡",
                    "flavor": "Lightning-fast memory access.",
                },
                # RAM generators
                "memory_stick": {
                    "id": "memory_stick",
                    "name": "Memory Stick",
                    "category": "ram",
                    "base_cost": 200,
                    "base_production": 20,
                    "cost_multiplier": 1.15,
                    "icon": "📦",
                    "flavor": "Volatile but speedy storage.",
                },
                "memory_bank": {
                    "id": "memory_bank",
                    "name": "Memory Bank",
                    "category": "ram",
                    "base_cost": 2000,
                    "base_production": 200,
                    "cost_multiplier": 1.15,
                    "icon": "🏦",
                    "flavor": "Organized memory architecture.",
                },
                # Storage generators
                "hard_drive": {
                    "id": "hard_drive",
                    "name": "Hard Drive",
                    "category": "storage",
                    "base_cost": 1000,
                    "base_production": 100,
                    "cost_multiplier": 1.15,
                    "icon": "💾",
                    "flavor": "Spinning platters of data.",
                },
                "solid_state": {
                    "id": "solid_state",
                    "name": "SSD",
                    "category": "storage",
                    "base_cost": 10000,
                    "base_production": 1000,
                    "cost_multiplier": 1.15,
                    "icon": "⚡",
                    "flavor": "Flash-based storage revolution.",
                },
                # GPU generators
                "graphics_card": {
                    "id": "graphics_card",
                    "name": "Graphics Card",
                    "category": "gpu",
                    "base_cost": 5000,
                    "base_production": 500,
                    "cost_multiplier": 1.15,
                    "icon": "🎮",
                    "flavor": "Parallel processing powerhouse.",
                },
                "tensor_core": {
                    "id": "tensor_core",
                    "name": "Tensor Core",
                    "category": "gpu",
                    "base_cost": 50000,
                    "base_production": 5000,
                    "cost_multiplier": 1.15,
                    "icon": "🤖",
                    "flavor": "AI acceleration unit.",
                },
                # Network generators
                "ethernet_card": {
                    "id": "ethernet_card",
                    "name": "Ethernet Card",
                    "category": "network",
                    "base_cost": 3000,
                    "base_production": 300,
                    "cost_multiplier": 1.15,
                    "icon": "🌐",
                    "flavor": "Connect to the world.",
                },
                "fiber_optic": {
                    "id": "fiber_optic",
                    "name": "Fiber Optic",
                    "category": "network",
                    "base_cost": 30000,
                    "base_production": 3000,
                    "cost_multiplier": 1.15,
                    "icon": "💫",
                    "flavor": "Light-speed data transfer.",
                },
                # Mobile generators
                "mobile_chip": {
                    "id": "mobile_chip",
                    "name": "Mobile Chip",
                    "category": "mobile",
                    "base_cost": 15000,
                    "base_production": 1500,
                    "cost_multiplier": 1.15,
                    "icon": "📱",
                    "flavor": "Computing in your pocket.",
                },
                # AI generators
                "ai_accelerator": {
                    "id": "ai_accelerator",
                    "name": "AI Accelerator",
                    "category": "ai",
                    "base_cost": 100000,
                    "base_production": 10000,
                    "cost_multiplier": 1.15,
                    "icon": "🧬",
                    "flavor": "Neural network processor.",
                },
            },
            "HARDWARE_UPGRADES": {
                # CPU upgrades
                "overclock": {
                    "id": "overclock",
                    "category": "cpu",
                    "name": "CPU Overclock",
                    "icon": "🚀",
                    "base_cost": 5000,
                    "cost_multiplier": 5,
                    "effect": 2,  # 2x CPU multiplier
                    "max_level": 5,
                    "description": "Double all CPU production",
                },
                # RAM upgrades
                "memory_optimization": {
                    "id": "memory_optimization",
                    "category": "ram",
                    "name": "Memory Optimization",
                    "icon": "🔧",
                    "base_cost": 8000,
                    "cost_multiplier": 5,
                    "effect": 2,  # 2x RAM multiplier
                    "max_level": 5,
                    "description": "Double all RAM production",
                },
                # Storage upgrades
                "data_compression": {
                    "id": "data_compression",
                    "category": "storage",
                    "name": "Data Compression",
                    "icon": "📦",
                    "base_cost": 12000,
                    "cost_multiplier": 5,
                    "effect": 2,  # 2x Storage multiplier
                    "max_level": 5,
                    "description": "Double all Storage production",
                },
                # GPU upgrades
                "ray_tracing": {
                    "id": "ray_tracing",
                    "category": "gpu",
                    "name": "Ray Tracing",
                    "icon": "✨",
                    "base_cost": 20000,
                    "cost_multiplier": 5,
                    "effect": 2,  # 2x GPU multiplier
                    "max_level": 5,
                    "description": "Double all GPU production",
                },
                # Network upgrades
                "bandwidth_boost": {
                    "id": "bandwidth_boost",
                    "category": "network",
                    "name": "Bandwidth Boost",
                    "icon": "📡",
                    "base_cost": 25000,
                    "cost_multiplier": 5,
                    "effect": 2,  # 2x Network multiplier
                    "max_level": 5,
                    "description": "Double all Network production",
                },
                # Mobile upgrades
                "battery_efficiency": {
                    "id": "battery_efficiency",
                    "category": "mobile",
                    "name": "Battery Efficiency",
                    "icon": "🔋",
                    "base_cost": 30000,
                    "cost_multiplier": 5,
                    "effect": 2,  # 2x Mobile multiplier
                    "max_level": 5,
                    "description": "Double all Mobile production",
                },
                # AI upgrades
                "neural_network": {
                    "id": "neural_network",
                    "category": "ai",
                    "name": "Neural Network",
                    "icon": "🧠",
                    "base_cost": 50000,
                    "cost_multiplier": 5,
                    "effect": 2,  # 2x AI multiplier
                    "max_level": 5,
                    "description": "Double all AI production",
                },
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
            self.tutorial_text = "Welcome to BIT BY BIT!\n\nYou are about to discover the\nfundamental nature of information.\n\nClick the accumulator to generate\nyour first bits."
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

    def draw(self):
        # Background with gradient
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
            pygame.draw.line(self.screen, color, (0, i), (self.current_width, i))

        # Draw binary rain (if enabled)
        if self.state.visual_settings["binary_rain"]:
            self.binary_rain.draw(self.screen)

        if not self.showing_settings and not self.showing_rebirth_confirmation:
            # Draw game elements in proper z-order (back to front)

            # 1. Background visual effects (drawn before accumulator)
            if self.state.visual_settings["particle_effects"]:
                # Draw only background particles, not interactive elements
                self.bit_visualization.draw(self.screen)

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


# Main execution
if __name__ == "__main__":
    game = BitByBitGame()
    game.run()
