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
        self.bits = 0
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

        # Initialize structures
        self.initialize_structures()

    def initialize_structures(self):
        # Initialize generators
        for gen_id in CONFIG["GENERATORS"]:
            self.generators[gen_id] = {"count": 0, "total_bought": 0}

        # Initialize upgrades
        for upgrade_id in CONFIG["UPGRADES"]:
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

            # Calculate from generators
            for gen_id, gen_data in self.generators.items():
                if gen_data["count"] > 0:
                    generator = CONFIG["GENERATORS"][gen_id]
                    base_production += gen_data["count"] * generator["base_production"]

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
        base_click = 10
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
        upgrade = CONFIG["UPGRADES"][upgrade_id]
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
        return self.total_bits_earned >= 1000

    def get_rebirth_progress(self):
        return min(self.total_bits_earned / CONFIG["REBIRTH_THRESHOLD"], 1)

    def get_estimated_rebirth_tokens(self):
        if self.total_bits_earned < CONFIG["REBIRTH_THRESHOLD"]:
            return 0
        return int(math.log2(self.total_bits_earned) - 20)

    def can_rebirth(self):
        return self.total_bits_earned >= CONFIG["REBIRTH_THRESHOLD"]

    def perform_rebirth(self):
        if not self.can_rebirth():
            return False

        # Calculate tokens earned
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

        return True


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
        # Determine base color based on state with defrag styling
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

        # Draw defrag-style button background (flat, no rounded corners)
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
                center=(text_rect.x + 1, text_rect.y + 1)
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
                    "flicker_chance": 0.001,  # Very rare flicker
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

            # Rare flicker effect
            if random.random() < column["flicker_chance"]:
                column["chars"] = ["1" if c == "0" else "0" for c in column["chars"]]

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


class DefragGrid:
    def __init__(self, x, y, width, height, grid_cols=16, grid_rows=12):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.grid_cols = grid_cols
        self.grid_rows = grid_rows
        self.block_width = width // grid_cols
        self.block_height = height // grid_rows

        # Block states: 0=empty, 1=fragmented, 2=organizing, 3=organized, 4=moving
        self.blocks = [[0 for _ in range(grid_cols)] for _ in range(grid_rows)]
        self.block_animations = {}  # Store animation data for moving blocks
        self.scan_line_position = 0
        self.last_bits = 0
        self.target_organized_blocks = 0

        # Defrag color mapping
        self.colors = {
            0: (40, 40, 40),  # Empty (dark gray)
            1: (200, 50, 50),  # Fragmented (red)
            2: (100, 100, 200),  # Organizing (blue)
            3: (50, 200, 50),  # Organized (green)
            4: (255, 165, 0),  # Moving (orange)
        }

    def update(self, bits, production_rate):
        # Calculate how many blocks should be organized based on bit progress
        # Scale: 0 bits = mostly fragmented, max bits = mostly organized
        max_bits_for_full_organization = 1000000  # Adjust this threshold as needed
        organization_ratio = min(1.0, bits / max_bits_for_full_organization)
        self.target_organized_blocks = int(
            (self.grid_cols * self.grid_rows) * organization_ratio * 0.7
        )  # 70% max organized

        # Initialize grid with some fragmentation if not already done
        if self.last_bits == 0 and bits > 0:
            self._initialize_fragmented_grid()

        # Gradually organize blocks based on bit accumulation
        self._update_block_organization(bits)

        # Animate blocks based on production rate
        if production_rate > 0:
            self._animate_production(production_rate)

        # Update block animations
        self._update_animations()

        # Update scan line
        self.scan_line_position = (self.scan_line_position + 2) % self.height

        self.last_bits = bits

    def _initialize_fragmented_grid(self):
        """Initialize grid with fragmented blocks scattered randomly"""
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                # Random distribution: some empty, some fragmented, few organized
                rand = random.random()
                if rand < 0.3:
                    self.blocks[row][col] = 0  # Empty
                elif rand < 0.85:
                    self.blocks[row][col] = 1  # Fragmented
                elif rand < 0.95:
                    self.blocks[row][col] = 2  # Organizing
                else:
                    self.blocks[row][col] = 3  # Organized

    def _update_block_organization(self, bits):
        """Update blocks to show increasing organization as bits accumulate"""
        organized_count = sum(1 for row in self.blocks for block in row if block == 3)

        while organized_count < self.target_organized_blocks:
            # Find a fragmented or organizing block to convert to organized
            candidates = []
            for row in range(self.grid_rows):
                for col in range(self.grid_cols):
                    if self.blocks[row][col] in [1, 2]:  # Fragmented or organizing
                        candidates.append((row, col))

            if candidates:
                row, col = random.choice(candidates)
                # Animate the transition
                self._start_block_animation(row, col, 2, 3)  # organizing -> organized
                self.blocks[row][col] = 3
                organized_count += 1
            else:
                break

    def _animate_production(self, production_rate):
        """Animate blocks based on current production rate"""
        # Higher production = more animations
        animation_chance = min(0.1, production_rate / 1000)

        if random.random() < animation_chance:
            # Pick a random organized block to animate
            organized_blocks = []
            for row in range(self.grid_rows):
                for col in range(self.grid_cols):
                    if self.blocks[row][col] == 3:
                        organized_blocks.append((row, col))

            if organized_blocks:
                row, col = random.choice(organized_blocks)
                # Brief animation effect
                self._start_block_animation(
                    row, col, 3, 2
                )  # organized -> organizing (briefly)

    def _start_block_animation(self, row, col, from_state, to_state):
        """Start an animation for a specific block"""
        key = (row, col)
        self.block_animations[key] = {
            "from_state": from_state,
            "to_state": to_state,
            "progress": 0.0,
            "duration": 0.5,  # seconds
        }

    def _update_animations(self):
        """Update all block animations"""
        completed = []
        for key, anim in self.block_animations.items():
            anim["progress"] += 1 / 60  # Assuming 60 FPS
            if anim["progress"] >= anim["duration"]:
                completed.append(key)

        for key in completed:
            del self.block_animations[key]

    def add_click_effect(self):
        """Add a defragmentation effect when user clicks"""
        # Trigger multiple block reorganizations
        for _ in range(3):
            # Find scattered fragmented blocks
            fragmented = []
            for row in range(self.grid_rows):
                for col in range(self.grid_cols):
                    if self.blocks[row][col] == 1:
                        fragmented.append((row, col))

            if fragmented:
                row, col = random.choice(fragmented)
                self._start_block_animation(row, col, 1, 3)  # fragmented -> organized
                self.blocks[row][col] = 3

    def add_purchase_effect(self):
        """Add cascading effect for purchases"""
        # Start from edges and move inward
        for _ in range(5):
            edge_blocks = []
            for row in range(self.grid_rows):
                for col in range(self.grid_cols):
                    if (
                        row == 0
                        or row == self.grid_rows - 1
                        or col == 0
                        or col == self.grid_cols - 1
                    ):
                        if self.blocks[row][col] in [1, 2]:
                            edge_blocks.append((row, col))

            if edge_blocks:
                row, col = random.choice(edge_blocks)
                self._start_block_animation(row, col, 1, 3)
                self.blocks[row][col] = 3

    def draw(self, screen):
        """Draw the defrag grid"""
        # Draw background
        pygame.draw.rect(
            screen, (20, 20, 20), (self.x, self.y, self.width, self.height)
        )

        # Draw blocks
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                block_x = self.x + col * self.block_width
                block_y = self.y + row * self.block_height

                # Check if block is animating
                block_state = self.blocks[row][col]
                anim_key = (row, col)

                if anim_key in self.block_animations:
                    anim = self.block_animations[anim_key]
                    # Interpolate between colors during animation
                    progress = anim["progress"] / anim["duration"]
                    from_color = self.colors[anim["from_state"]]
                    to_color = self.colors[anim["to_state"]]

                    # Add glow effect during animation
                    color = tuple(
                        int(from_color[i] + (to_color[i] - from_color[i]) * progress)
                        for i in range(3)
                    )

                    # Draw animated block with glow
                    if progress < 0.5:
                        glow_size = 2
                        glow_color = tuple(min(255, c + 100) for c in color)
                        pygame.draw.rect(
                            screen,
                            glow_color,
                            (
                                block_x - glow_size,
                                block_y - glow_size,
                                self.block_width + glow_size * 2,
                                self.block_height + glow_size * 2,
                            ),
                        )
                else:
                    color = self.colors[block_state]

                # Draw block
                pygame.draw.rect(
                    screen,
                    color,
                    (block_x, block_y, self.block_width - 1, self.block_height - 1),
                )

        # Draw scan line effect
        scan_alpha = int(100 * (0.5 + 0.5 * math.sin(self.scan_line_position * 0.1)))
        scan_surface = pygame.Surface((self.width, 3))
        scan_surface.set_alpha(scan_alpha)
        scan_surface.fill((100, 200, 255))  # Cyan scan line
        screen.blit(
            scan_surface, (self.x, self.y + self.scan_line_position % self.height)
        )

        # Draw grid lines (subtle)
        for i in range(self.grid_rows + 1):
            y = self.y + i * self.block_height
            pygame.draw.line(
                screen, (60, 60, 60), (self.x, y), (self.x + self.width, y), 1
            )

        for i in range(self.grid_cols + 1):
            x = self.x + i * self.block_width
            pygame.draw.line(
                screen, (60, 60, 60), (x, self.y), (x, self.y + self.height), 1
            )

    def get_defragmentation_percentage(self):
        """Calculate the defragmentation percentage based on organized blocks"""
        total_blocks = self.grid_cols * self.grid_rows
        organized_blocks = sum(1 for row in self.blocks for block in row if block == 3)
        return (organized_blocks / total_blocks) * 100


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
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Bit by Bit - A Game About Information")
        self.clock = pygame.time.Clock()
        self.running = True

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

        # Defrag grid for accumulator visualization
        self.defrag_grid = DefragGrid(
            WINDOW_WIDTH // 2 - 200,
            140,
            400,
            200,  # Position within accumulator area
        )

        # UI elements
        self.click_button = Button(
            WINDOW_WIDTH // 2 - 150, 420, 300, 60, "DEFRAGMENT [+10b]", (60, 60, 80)
        )

        # Header buttons with defrag styling
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

    def setup_generator_buttons(self):
        x_start = 50
        y_start = 200
        card_height = 140
        card_width = 500

        for i, (gen_id, generator) in enumerate(CONFIG["GENERATORS"].items()):
            y = y_start + i * (card_height + 10)

            # Buy buttons
            buy_x1 = Button(x_start + card_width - 180, y + 90, 70, 30, "BUY x1")
            buy_x10 = Button(x_start + card_width - 100, y + 90, 70, 30, "BUY x10")

            self.generator_buy_buttons[gen_id] = {"x1": buy_x1, "x10": buy_x10}

    def setup_upgrade_buttons(self):
        x_start = 750
        y_start = 200
        card_height = 120

        for i, (upgrade_id, upgrade) in enumerate(CONFIG["UPGRADES"].items()):
            y = y_start + i * (card_height + 10)

            buy_button = Button(x_start + 250, y + 70, 80, 30, "BUY")
            self.upgrade_buttons[upgrade_id] = buy_button

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
                        if self.state.perform_rebirth():
                            self.showing_rebirth_confirmation = False
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

        # Add defrag click effect
        self.defrag_grid.add_click_effect()

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

            # Add defrag purchase effect
            self.defrag_grid.add_purchase_effect()

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

            # Add defrag purchase effect
            self.defrag_grid.add_purchase_effect()

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

    def update(self, dt):
        # Update binary rain (if enabled)
        if self.state.visual_settings["binary_rain"]:
            self.binary_rain.update(dt)

        # Update game state
        production_rate = self.state.get_production_rate()
        production = production_rate * dt
        self.state.bits += production
        self.state.total_bits_earned += production

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
        # Update defrag grid with current bits and production rate
        production_rate = self.state.get_production_rate()
        self.defrag_grid.update(self.state.bits, production_rate)

        # Draw accumulator background with defrag aesthetic
        acc_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 100, 400, 300)
        center_x = WINDOW_WIDTH // 2
        center_y = 250

        # Dark background for defrag aesthetic
        pygame.draw.rect(self.screen, (10, 10, 20), acc_rect, border_radius=8)

        # Animated glow effect around accumulator (subtler for defrag look)
        time_ms = pygame.time.get_ticks()
        glow_intensity = abs(math.sin(time_ms * 0.001)) * 0.3 + 0.2

        # Draw border with classic defrag styling
        border_glow = abs(math.sin(time_ms * 0.002)) * 0.2 + 0.8
        border_color = tuple(int(c * border_glow) for c in COLORS["electric_cyan"])
        pygame.draw.rect(self.screen, border_color, acc_rect, 2, border_radius=8)

        # Title with defrag aesthetic
        title_text = self.small_font.render(
            "DISK DEFRAGMENTER", True, COLORS["muted_blue"]
        )
        title_rect = title_text.get_rect(center=(center_x, 120))
        self.screen.blit(title_text, title_rect)

        # Draw the defrag grid
        self.defrag_grid.draw(self.screen)

        # Show defragmentation percentage
        defrag_percent = self.defrag_grid.get_defragmentation_percentage()
        progress_text = self.small_font.render(
            f"{defrag_percent:.0f}% Defragmented", True, COLORS["matrix_green"]
        )
        progress_rect = progress_text.get_rect(center=(center_x, 160))
        self.screen.blit(progress_text, progress_rect)

        # Bits display with defrag-style monospace font
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

        # Rate display with defrag styling
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
        # Draw toggle button with defrag styling when collapsed
        if not self.generators_panel_open:
            # Draw collapsed toggle button with defrag style
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

            # Draw text with defrag styling
            text_color = (120, 120, 140)  # Dimmed defrag color
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

        # Panel background with defrag styling
        panel_rect = pygame.Rect(
            50, 520, 600, 200
        )  # Position below expanded toggle button

        # Draw flat dark background like defrag interface
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

        # Title with defrag styling
        title_text = self.medium_font.render(
            "DATA SOURCES",
            True,
            (100, 200, 255),  # Cyan like scan lines
        )
        title_rect = title_text.get_rect(center=(350, 540))
        self.screen.blit(title_text, title_rect)

        # Generator cards
        y_start = 560  # Adjusted for new panel position
        generators_to_use = GENERATORS if GENERATORS else CONFIG["GENERATORS"]

        for gen_id, generator in generators_to_use.items():
            if not self.state.is_generator_unlocked(gen_id):
                continue

            count = self.state.generators[gen_id]["count"]
            cost = self.state.get_generator_cost(gen_id)
            can_afford = self.state.can_afford(cost)

            # Card background with defrag block styling
            card_rect = pygame.Rect(
                60, y_start, 580, 70
            )  # Reduced height for smaller panel

            # Use defrag block colors for card background
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

            # Add small status indicator block (defrag style)
            status_block_rect = pygame.Rect(card_rect.x + 5, card_rect.y + 5, 8, 8)
            if can_afford:
                pygame.draw.rect(
                    self.screen, (100, 255, 100), status_block_rect
                )  # Green
            else:
                pygame.draw.rect(self.screen, (200, 50, 50), status_block_rect)  # Red

            # Draw defrag-style grid lines on card
            for i in range(0, card_rect.width, 20):
                pygame.draw.line(
                    self.screen,
                    (40, 40, 40),
                    (card_rect.x + i, card_rect.y + 15),
                    (card_rect.x + i, card_rect.bottom - 5),
                    1,
                )

            # Icon area with defrag styling
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

            # Generator name and count with defrag styling
            name_text = self.small_font.render(
                f"{generator['name']}",
                True,
                (200, 200, 200),  # Light gray like old UI
            )
            self.screen.blit(name_text, (180, y_start + 8))

            count_text = self.tiny_font.render(
                f"QUANTITY: {count}",
                True,
                (100, 200, 255),  # Cyan like scan lines
            )
            self.screen.blit(count_text, (180, y_start + 28))

            # Production rate with defrag styling
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

            # Cost display with defrag styling
            cost_color = (
                (50, 200, 50) if can_afford else (200, 50, 50)
            )  # Defrag green/red
            cost_text = self.small_font.render(
                f"COST: {self.format_number(cost)} bits", True, cost_color
            )
            self.screen.blit(cost_text, (400, y_start + 35))

            # Progress bar with defrag block styling
            if not can_afford:
                progress = self.state.bits / cost
                progress_bg = pygame.Rect(400, y_start + 55, 150, 10)
                progress_fill = pygame.Rect(400, y_start + 55, int(150 * progress), 10)

                # Draw background with block style
                pygame.draw.rect(self.screen, (40, 40, 40), progress_bg)
                pygame.draw.rect(self.screen, (60, 60, 60), progress_bg, 1)

                # Draw fill with defrag green blocks
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

            # Draw buttons
            self.generator_buy_buttons[gen_id]["x1"].draw(self.screen)
            self.generator_buy_buttons[gen_id]["x10"].draw(self.screen)

            y_start += 80  # Reduced spacing for smaller cards

    def draw_upgrades_panel(self):
        # Draw toggle button with adjusted appearance when collapsed
        if not self.upgrades_panel_open:
            # Draw collapsed toggle button with defrag style
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

            # Draw text with defrag styling
            text_color = (120, 120, 140)  # Dimmed defrag color
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

        # Panel background with defrag styling
        panel_rect = pygame.Rect(
            700, 520, 450, 200
        )  # Position below expanded toggle button

        # Draw flat dark background like defrag interface
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

        # Title with defrag styling
        title_text = self.medium_font.render(
            "SYSTEM OPTIMIZATIONS", True, (150, 100, 200)
        )  # Purple accent
        title_rect = title_text.get_rect(center=(925, 540))
        self.screen.blit(title_text, title_rect)

        # Upgrade cards
        y_start = 540  # Adjusted for new panel position
        upgrades_to_use = UPGRADES if UPGRADES else CONFIG["UPGRADES"]

        for upgrade_id, upgrade in upgrades_to_use.items():
            if not self.state.is_upgrade_unlocked(upgrade_id):
                continue

            level = self.state.upgrades[upgrade_id]["level"]
            cost = self.state.get_upgrade_cost(upgrade_id)
            can_afford = self.state.can_afford(cost) and level < upgrade["max_level"]

            # Card background with defrag block styling
            card_rect = pygame.Rect(
                710, y_start, 430, 60
            )  # Reduced height for smaller panel

            # Use defrag block colors for card background
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

            # Add small status indicator block (defrag style)
            status_block_rect = pygame.Rect(card_rect.x + 5, card_rect.y + 5, 8, 8)
            if can_afford:
                pygame.draw.rect(
                    self.screen, (200, 150, 255), status_block_rect
                )  # Purple
            else:
                pygame.draw.rect(self.screen, (200, 50, 50), status_block_rect)  # Red

            # Draw defrag-style grid lines on card
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
            icon_surface = icon_font.render(icon_text, True, COLORS["neon_purple"])
            self.screen.blit(icon_surface, (720, y_start + 10))

            # Upgrade name
            name_text = self.small_font.render(
                f"{upgrade['name']}", True, COLORS["soft_white"]
            )
            self.screen.blit(name_text, (765, y_start + 10))

            # Description
            desc_text = self.tiny_font.render(
                upgrade["description"], True, COLORS["muted_blue"]
            )
            self.screen.blit(desc_text, (720, y_start + 35))

            # Current effect
            if level > 0:
                if upgrade_id == "entropy_amplification":
                    effect_text = f"Currently: ×{math.pow(2, level):.0f} boost"
                else:
                    effect_text = f"Currently: +{level * upgrade['effect']} bits"

                effect_surface = self.tiny_font.render(
                    effect_text, True, COLORS["neon_purple"]
                )
                self.screen.blit(effect_surface, (720, y_start + 55))

            # Cost and button
            if level < upgrade["max_level"]:
                cost_color = (
                    COLORS["neon_purple"] if can_afford else COLORS["red_error"]
                )
                cost_text = self.tiny_font.render(
                    f"Cost: {self.format_number(cost)} bits", True, cost_color
                )
                self.screen.blit(cost_text, (720, y_start + 75))

                # Update button state and draw
                self.upgrade_buttons[upgrade_id].is_enabled = can_afford
                self.upgrade_buttons[upgrade_id].draw(self.screen)
            else:
                # Golden MAX LEVEL text
                max_text = self.small_font.render("MAX LEVEL", True, COLORS["gold"])
                self.screen.blit(max_text, (720, y_start + 75))

            y_start += 70  # Reduced spacing for smaller cards

    def draw_rebirth_bar(self):
        # Background with elevation shadow
        bar_rect = pygame.Rect(0, WINDOW_HEIGHT - 80, WINDOW_WIDTH, 80)

        # Shadow effect
        shadow_rect = pygame.Rect(2, WINDOW_HEIGHT - 78, WINDOW_WIDTH - 4, 76)
        pygame.draw.rect(self.screen, (0, 0, 0, 50), shadow_rect)

        # Main background
        pygame.draw.rect(self.screen, COLORS["deep_space_blue"], bar_rect)

        # Top border with glow
        pygame.draw.line(
            self.screen,
            COLORS["neon_purple"],
            (0, WINDOW_HEIGHT - 80),
            (WINDOW_WIDTH, WINDOW_HEIGHT - 80),
            2,
        )
        # Add glow effect
        for i in range(1, 4):
            alpha = 50 - i * 15
            glow_color = (*COLORS["neon_purple"][:3], alpha)
            pygame.draw.line(
                self.screen,
                glow_color[:3],
                (0, WINDOW_HEIGHT - 80 + i),
                (WINDOW_WIDTH, WINDOW_HEIGHT - 80 + i),
                1,
            )

        # Rebirth progress
        progress = self.state.get_rebirth_progress()
        tokens = self.state.get_estimated_rebirth_tokens()
        current_mb = self.format_number(self.state.total_bits_earned / (1024 * 1024))

        # Progress bar with shimmer effect
        progress_bg = pygame.Rect(200, WINDOW_HEIGHT - 50, 800, 20)
        progress_fill = pygame.Rect(200, WINDOW_HEIGHT - 50, int(800 * progress), 20)

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
        if tokens > 0:
            # Update and draw rebirth button
            self.rebirth_button.text = f"🌀 COMPRESS FOR {tokens} ⭐"
            self.rebirth_button.draw(self.screen)
        else:
            # Main text for not ready
            rebirth_text = f"🌀 COMPRESSION AVAILABLE AT 128 MB"
            text_color = COLORS["neon_purple"]
            text_surface = self.medium_font.render(rebirth_text, True, text_color)
            text_rect = text_surface.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60)
            )
            self.screen.blit(text_surface, text_rect)

        # Progress text with monospace font
        progress_text = self.monospace_font.render(
            f"({current_mb} MB / 128 MB) {int(progress * 100)}%",
            True,
            COLORS["soft_white"],
        )
        progress_rect = progress_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 25)
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
        for y in range(0, WINDOW_HEIGHT, 4):
            pygame.draw.line(self.screen, (0, 0, 0, 20), (0, y), (WINDOW_WIDTH, y))

        # Add subtle flicker
        if random.random() < 0.02:  # 2% chance of flicker
            flicker_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            flicker_surface.set_alpha(random.randint(5, 15))
            flicker_surface.fill((255, 255, 255))
            self.screen.blit(flicker_surface, (0, 0))

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
            # Overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(COLORS["deep_space_blue"])
            self.screen.blit(overlay, (0, 0))

            # Tutorial box
            box_rect = pygame.Rect(
                WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2 - 150, 500, 300
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
                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50 + y_offset)
                )
                self.screen.blit(text_surface, text_rect)
                y_offset += 30

            # Continue button
            continue_text = self.medium_font.render(
                "CLICK TO CONTINUE", True, COLORS["electric_cyan"]
            )
            continue_rect = continue_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80)
            )
            self.screen.blit(continue_text, continue_rect)

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
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill(COLORS["deep_space_blue"])
        self.screen.blit(overlay, (0, 0))

        # Settings box
        settings_rect = pygame.Rect(WINDOW_WIDTH // 2 - 300, 150, 600, 400)
        pygame.draw.rect(
            self.screen, COLORS["dim_gray"], settings_rect, border_radius=16
        )
        pygame.draw.rect(
            self.screen, COLORS["electric_cyan"], settings_rect, 3, border_radius=16
        )

        # Title
        title_text = self.large_font.render("⚙️ SETTINGS", True, COLORS["electric_cyan"])
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)

        # Visual settings section
        section_text = self.medium_font.render(
            "VISUAL EFFECTS", True, COLORS["neon_purple"]
        )
        section_rect = section_text.get_rect(center=(WINDOW_WIDTH // 2, 240))
        self.screen.blit(section_text, section_rect)

        mouse_pos = pygame.mouse.get_pos()

        # CRT Effects toggle
        crt_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 250, 400, 40)
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
        rain_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 300, 400, 40)
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
        particle_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, 350, 400, 40)
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
        inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, 450))
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
        for i in range(WINDOW_HEIGHT):
            color_ratio = i / WINDOW_HEIGHT
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
            pygame.draw.line(self.screen, color, (0, i), (WINDOW_WIDTH, i))

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
            title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 40))
            self.screen.blit(title_text, title_rect)

            subtitle_text = self.small_font.render(
                "A Game About Information", True, COLORS["muted_blue"]
            )
            subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 70))
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
