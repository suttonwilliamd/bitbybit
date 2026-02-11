"""
Constants and configuration for Bit by Bit Game
"""

import pygame
import math
import sys
import os
from toon_parser import load_toon_file

# Initialize Pygame
pygame.init()

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


# Enhanced color palette with better visual hierarchy and accessibility
COLORS = {
    # Primary colors - optimized for eye comfort and accessibility
    "deep_space_blue": (15, 18, 28),  # Darkest background
    "electric_cyan": (0, 170, 220),  # Reduced saturation for better eye comfort
    "neon_purple": (160, 90, 230),  # Lighter for better contrast and readability
    "matrix_green": (57, 255, 20),  # Success/positive states
    "signal_orange": (255, 140, 90),  # Warning/caution
    "quantum_violet": (148, 63, 236),  # Premium accent
    "gold": (255, 215, 0),  # Premium tokens
    "red_error": (255, 89, 89),  # Error states
    # UI layers - clear hierarchy with better contrast
    "panel_background": (22, 25, 35),  # Panel backgrounds
    "panel_title_bg": (28, 32, 45),  # Title bars
    "card_background": (28, 32, 42),  # Card backgrounds
    "card_affordable": (32, 36, 48),  # Affordable cards
    "card_disabled": (25, 25, 30),  # Disabled cards
    # Text colors - improved readability with high contrast
    "soft_white": (240, 245, 255),  # Primary text
    "muted_blue": (120, 140, 180),  # Secondary text
    "muted_gray": (100, 110, 130),  # Tertiary text
    "text_disabled": (80, 85, 95),  # Disabled text
    # High contrast mode colors (for accessibility)
    "high_contrast_primary": (255, 255, 255),  # White
    "high_contrast_secondary": (0, 0, 0),  # Black
    "high_contrast_border": (128, 128, 128),  # Gray
    "high_contrast_background": (255, 255, 255),  # White
    # Legacy colors for compatibility
    "dim_gray": (42, 45, 58),
    "deep_space_gradient_end": (26, 30, 55),
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
            "effect": 1,  # +1 bit per click
            "max_level": 15,
            "description": "Increases click value by +1 bit",
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
