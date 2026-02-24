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

# Setup icon font for emoji rendering (works on Windows)
ICON_FONT = None
ICON_FONT_FALLBACK = None

def get_icon_font(size=36):
    """Get a font that can render emoji/icons"""
    global ICON_FONT
    
    if ICON_FONT is None:
        # Try emoji-capable fonts in order of preference
        font_names = [
            "Segoe UI Emoji",      # Windows 10+
            "Segoe UI Symbol",     # Windows 7+
            "Apple Color Emoji",    # macOS
            "Noto Color Emoji",    # Linux
            "Symbola",             # Fallback
            "Arial Unicode MS",    # Fallback
        ]
        
        for font_name in font_names:
            try:
                test_font = pygame.font.SysFont(font_name, size)
                # Test if it can render a common emoji
                test_surface = test_font.render("🔲", True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    ICON_FONT = font_name
                    break
            except:
                continue
    
    # Return font at requested size
    return pygame.font.SysFont(ICON_FONT, size) if ICON_FONT else pygame.font.Font(None, size)


try:
    GAME_CONFIG = load_toon_file("config/game.toon")
    GENERATORS_CONFIG = load_toon_file("config/generators.toon")
    UPGRADES_CONFIG = load_toon_file("config/upgrades.toon")
except Exception:
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
    "white": (255, 255, 255),  # Pure white
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

GENERATORS = {}
if "generators" in GENERATORS_CONFIG and GENERATORS_CONFIG["generators"]:
    for gen in GENERATORS_CONFIG["generators"]:
        GENERATORS[gen["id"]] = gen

# Game Configuration
CONFIG = {
    "SAVE_FILE": "bitbybit_save.json",
    "AUTO_SAVE_INTERVAL": 30000,  # 30 seconds
    "REBIRTH_THRESHOLD": 128 * 1024 * 1024,  # 128 MB in bits - for rebirth
    "VISUAL_FILL_THRESHOLD": 10000,            # 10K bits - fills at 1MB total
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
    "HARDWARE_GENERATORS": {
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
        "ethernet_card": {
            "id": "ethernet_card",
            "name": "Ethernet Card",
            "category": "network",
            "base_cost": 3000,
            "base_production": 300,
            "cost_multiplier": 1.15,
            "icon": "🌐",
            "flavor": "Connect to world.",
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
        "quantum_processor": {
            "id": "quantum_processor",
            "name": "Quantum Processor",
            "category": "quantum",
            "base_cost": 500000,
            "base_production": 50000,
            "cost_multiplier": 1.15,
            "icon": "⚛️",
            "flavor": "Superposition and entanglement.",
        },
        "qubit_register": {
            "id": "qubit_register",
            "name": "Qubit Register",
            "category": "quantum",
            "base_cost": 1000000,
            "base_production": 100000,
            "cost_multiplier": 1.15,
            "icon": "🔮",
            "flavor": "Quantum state storage.",
        },
        "hyper_cluster": {
            "id": "hyper_cluster",
            "name": "Hyper Cluster",
            "category": "hyper",
            "base_cost": 5000000,
            "base_production": 500000,
            "cost_multiplier": 1.15,
            "icon": "🌌",
            "flavor": "Massive distributed computing.",
        },
        "dimension_gate": {
            "id": "dimension_gate",
            "name": "Dimension Gate",
            "category": "hyper",
            "base_cost": 10000000,
            "base_production": 1000000,
            "cost_multiplier": 1.15,
            "icon": "🌀",
            "flavor": "Interdimensional data processing.",
        },
        "singularity_core": {
            "id": "singularity_core",
            "name": "Singularity Core",
            "category": "singularity",
            "base_cost": 50000000,
            "base_production": 5000000,
            "cost_multiplier": 1.15,
            "icon": "✨",
            "flavor": "Transcendent computation.",
        },
    },
    "HARDWARE_UPGRADES": {
        "overclock": {
            "id": "overclock",
            "category": "cpu",
            "name": "CPU Overclock",
            "icon": "🚀",
            "base_cost": 5000,
            "cost_multiplier": 5,
            "effect": 2,
            "max_level": 5,
            "description": "Double all CPU production",
        },
        "memory_optimization": {
            "id": "memory_optimization",
            "category": "ram",
            "name": "Memory Optimization",
            "icon": "🔧",
            "base_cost": 8000,
            "cost_multiplier": 5,
            "effect": 2,
            "max_level": 5,
            "description": "Double all RAM production",
        },
        "data_compression": {
            "id": "data_compression",
            "category": "storage",
            "name": "Data Compression",
            "icon": "📦",
            "base_cost": 12000,
            "cost_multiplier": 5,
            "effect": 2,
            "max_level": 5,
            "description": "Double all Storage production",
        },
        "ray_tracing": {
            "id": "ray_tracing",
            "category": "gpu",
            "name": "Ray Tracing",
            "icon": "✨",
            "base_cost": 20000,
            "cost_multiplier": 5,
            "effect": 2,
            "max_level": 5,
            "description": "Double all GPU production",
        },
        "bandwidth_boost": {
            "id": "bandwidth_boost",
            "category": "network",
            "name": "Bandwidth Boost",
            "icon": "📡",
            "base_cost": 25000,
            "cost_multiplier": 5,
            "effect": 2,
            "max_level": 5,
            "description": "Double all Network production",
        },
        "battery_efficiency": {
            "id": "battery_efficiency",
            "category": "mobile",
            "name": "Battery Efficiency",
            "icon": "🔋",
            "base_cost": 30000,
            "cost_multiplier": 5,
            "effect": 2,
            "max_level": 5,
            "description": "Double all Mobile production",
        },
        "neural_network": {
            "id": "neural_network",
            "category": "ai",
            "name": "Neural Network",
            "icon": "🧠",
            "base_cost": 50000,
            "cost_multiplier": 5,
            "effect": 2,
            "max_level": 5,
            "description": "Double all AI production",
        },
        "quantum_entanglement": {
            "id": "quantum_entanglement",
            "category": "quantum",
            "name": "Quantum Entanglement",
            "icon": "🔗",
            "base_cost": 100000,
            "cost_multiplier": 5,
            "effect": 2,
            "max_level": 5,
            "description": "Double all Quantum production",
        },
        "hyper_parallelism": {
            "id": "hyper_parallelism",
            "category": "hyper",
            "name": "Hyper Parallelism",
            "icon": "⚡",
            "base_cost": 200000,
            "cost_multiplier": 5,
            "effect": 2,
            "max_level": 5,
            "description": "Double all Hyper production",
        },
        "transcendence": {
            "id": "transcendence",
            "category": "singularity",
            "name": "Transcendence",
            "icon": "🌟",
            "base_cost": 500000,
            "cost_multiplier": 5,
            "effect": 2,
            "max_level": 5,
            "description": "Double all Singularity production",
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
    7: {
        "name": "Quantum Era",
        "description": "Quantum computing revolution",
        "storage_capacity": 2 * 1024 * 1024 * 1024 * 1024,  # 2 TB threshold
        "unlock_categories": [
            "cpu", "ram", "storage", "gpu", "network", "mobile", "ai", "quantum",
        ],
        "primary_category": "quantum",
        "visual_theme": "quantum",
        "icon": "⚛️",
    },
    8: {
        "name": "Hyper Era",
        "description": "Hyperscale computing",
        "storage_capacity": 8 * 1024 * 1024 * 1024 * 1024,  # 8 TB threshold
        "unlock_categories": [
            "cpu", "ram", "storage", "gpu", "network", "mobile", "ai", "quantum", "hyper",
        ],
        "primary_category": "hyper",
        "visual_theme": "hyper",
        "icon": "🌌",
    },
    9: {
        "name": "Singularity Era",
        "description": "Technological singularity",
        "storage_capacity": 32 * 1024 * 1024 * 1024 * 1024,  # 32 TB threshold
        "unlock_categories": [
            "cpu", "ram", "storage", "gpu", "network", "mobile", "ai", "quantum", "hyper", "singularity",
        ],
        "primary_category": "singularity",
        "visual_theme": "singularity",
        "icon": "✨",
    },
}

# ============================================================================
# ERA PROGRESSION SYSTEM
# Starting from Abacus (Era 0) through Transistors (Era 4), then Quantum/Cosmic
# ============================================================================

ERAS = {
    0: {
        "id": "abacus",
        "name": "Abacus Era",
        "description": "Counting with pebbles and marks",
        "currency_name": "Pebbles",
        "currency_icon": "🪨",
        "primary_color": (139, 90, 43),  # Brown/sandy
        "secondary_color": (210, 180, 140),  # Tan
        "unlock_bits": 0,
        "generator_categories": ["abacus"],
        "visual_theme": "ancient",
        "icon": "🔢",
        "prestige_unlock": "define_bit",
        "prestige_name": "Define Bit",
        "prestige_description": "Invent Boolean Algebra to unlock binary efficiency",
    },
    1: {
        "id": "mechanical",
        "name": "Mechanical Era",
        "description": "Gears, levers, and early calculating machines",
        "currency_name": "Ticks",
        "currency_icon": "⚙️",
        "primary_color": (184, 134, 11),  # Dark goldenrod
        "secondary_color": (218, 165, 32),  # Goldenrod
        "unlock_bits": 1000,
        "generator_categories": ["mechanical"],
        "visual_theme": "steampunk",
        "icon": "🦯",
        "prestige_unlock": "boolean_algebra",
        "prestige_name": "Boolean Algebra",
        "prestige_description": "Formalize logic to double all production",
    },
    2: {
        "id": "electromechanical",
        "name": "Electromechanical Era",
        "description": "Relays and punch cards",
        "currency_name": "Pulses",
        "currency_icon": "🔌",
        "primary_color": (70, 70, 70),  # Dark gray
        "secondary_color": (169, 169, 169),  # Dark gray
        "unlock_bits": 50000,
        "generator_categories": ["electromechanical"],
        "visual_theme": "industrial",
        "icon": "📠",
    },
    3: {
        "id": "vacuum_tubes",
        "name": "Vacuum Tubes Era",
        "description": "ENIAC and early computers",
        "currency_name": "Volts",
        "currency_icon": "💡",
        "primary_color": (180, 60, 60),  # Dark red (heat)
        "secondary_color": (255, 140, 0),  # Dark orange (glow)
        "unlock_bits": 500000,
        "generator_categories": ["vacuum_tubes"],
        "visual_theme": "retro_computer",
        "icon": "🕰️",
    },
    4: {
        "id": "transistors",
        "name": "Transistors Era",
        "description": "Modern computing - CPUs, RAM, GPUs",
        "currency_name": "Bits",
        "currency_icon": "💻",
        "primary_color": (0, 170, 220),  # Electric cyan
        "secondary_color": (160, 90, 230),  # Neon purple
        "unlock_bits": 10000000,
        "generator_categories": ["cpu", "ram", "storage", "gpu", "network", "mobile", "ai", "quantum", "hyper", "singularity"],
        "visual_theme": "modern",
        "icon": "🧠",
    },
    5: {
        "id": "quantum",
        "name": "Quantum Era",
        "description": "Qubits and quantum computing",
        "currency_name": "Qubits",
        "currency_icon": "⚛️",
        "primary_color": (138, 43, 226),  # Purple
        "secondary_color": (0, 255, 255),  # Cyan
        "unlock_bits": 1000000000,
        "generator_categories": ["quantum"],
        "visual_theme": "quantum",
        "icon": "🔮",
    },
    6: {
        "id": "cosmic",
        "name": "Cosmic Era",
        "description": "Interdimensional computation",
        "currency_name": "Cosmic Units",
        "currency_icon": "🌌",
        "primary_color": (75, 0, 130),  # Indigo
        "secondary_color": (255, 215, 0),  # Gold
        "unlock_bits": 100000000000,
        "generator_categories": ["cosmic"],
        "visual_theme": "cosmic",
        "icon": "🌀",
    },
}

# Era-specific generator definitions
ABACUS_GENERATORS = {
    "pebble": {
        "id": "pebble",
        "name": "Pebble Counter",
        "category": "abacus",
        "era": 0,
        "base_cost": 10,
        "base_production": 1,
        "cost_multiplier": 1.15,
        "icon": "🪨",
        "flavor": "One pebble, one count.",
    },
    "tally_stick": {
        "id": "tally_stick",
        "name": "Tally Stick",
        "category": "abacus",
        "era": 0,
        "base_cost": 100,
        "base_production": 8,
        "cost_multiplier": 1.15,
        "icon": "📏",
        "flavor": "Notches in wood mark the way.",
        "unlock_threshold": 50,
    },
    "abacus": {
        "id": "abacus",
        "name": "Abacus",
        "category": "abacus",
        "era": 0,
        "base_cost": 500,
        "base_production": 50,
        "cost_multiplier": 1.15,
        "icon": "🔢",
        "flavor": "The ancient calculating marvel.",
        "unlock_threshold": 200,
    },
    "clay_tablet": {
        "id": "clay_tablet",
        "name": "Clay Tablet",
        "category": "abacus",
        "era": 0,
        "base_cost": 2000,
        "base_production": 250,
        "cost_multiplier": 1.15,
        "icon": "📜",
        "flavor": "Cuneiform records of numbers.",
        "unlock_threshold": 1000,
    },
}

MECHANICAL_GENERATORS = {
    "lever": {
        "id": "lever",
        "name": "Calculating Lever",
        "category": "mechanical",
        "era": 1,
        "base_cost": 2000,
        "base_production": 100,
        "cost_multiplier": 1.15,
        "icon": "�杠杆",
        "flavor": "Leverage in motion.",
        "unlock_threshold": 1000,
    },
    "gear_train": {
        "id": "gear_train",
        "name": "Gear Train",
        "category": "mechanical",
        "era": 1,
        "base_cost": 10000,
        "base_production": 500,
        "cost_multiplier": 1.15,
        "icon": "⚙️",
        "flavor": "Turning gears, computing numbers.",
        "unlock_threshold": 5000,
    },
    "antikythera": {
        "id": "antikythera",
        "name": "Antikythera Mechanism",
        "category": "mechanical",
        "era": 1,
        "base_cost": 50000,
        "base_production": 2500,
        "cost_multiplier": 1.15,
        "icon": "🔮",
        "flavor": "Ancient analog computer from the deep.",
        "unlock_threshold": 15000,
    },
    "pascaline": {
        "id": "pascaline",
        "name": "Pascaline",
        "category": "mechanical",
        "era": 1,
        "base_cost": 150000,
        "base_production": 10000,
        "cost_multiplier": 1.15,
        "icon": "➕",
        "flavor": "Blaise Pascal's arithmetic machine.",
        "unlock_threshold": 40000,
    },
    "difference_engine": {
        "id": "difference_engine",
        "name": "Difference Engine",
        "category": "mechanical",
        "era": 1,
        "base_cost": 500000,
        "base_production": 40000,
        "cost_multiplier": 1.15,
        "icon": "🔧",
        "flavor": "Babbage's dream of mechanical computation.",
        "unlock_threshold": 100000,
    },
}

ELECTROMECHANICAL_GENERATORS = {
    "relay": {
        "id": "relay",
        "name": "Electromagnetic Relay",
        "category": "electromechanical",
        "era": 2,
        "base_cost": 100000,
        "base_production": 5000,
        "cost_multiplier": 1.15,
        "icon": "🔗",
        "flavor": "Click-clack computing.",
        "unlock_threshold": 50000,
    },
    "stepping_switch": {
        "id": "stepping_switch",
        "name": "Stepping Switch",
        "category": "electromechanical",
        "era": 2,
        "base_cost": 500000,
        "base_production": 25000,
        "cost_multiplier": 1.15,
        "icon": "🔀",
        "flavor": "Rotary telephone switches compute.",
        "unlock_threshold": 150000,
    },
    "punch_card": {
        "id": "punch_card",
        "name": "Punch Card Reader",
        "category": "electromechanical",
        "era": 2,
        "base_cost": 2000000,
        "base_production": 100000,
        "cost_multiplier": 1.15,
        "icon": "🗃️",
        "flavor": "Holes in cards store data.",
        "unlock_threshold": 500000,
    },
    "teletype": {
        "id": "teletype",
        "name": "Teletype Machine",
        "category": "electromechanical",
        "era": 2,
        "base_cost": 8000000,
        "base_production": 400000,
        "cost_multiplier": 1.15,
        "icon": "📟",
        "flavor": "Typewriter meets telegraph.",
        "unlock_threshold": 2000000,
    },
}

VACUUM_TUBE_GENERATORS = {
    "triode": {
        "id": "triode",
        "name": "Triode Tube",
        "category": "vacuum_tubes",
        "era": 3,
        "base_cost": 10000000,
        "base_production": 500000,
        "cost_multiplier": 1.15,
        "icon": "💡",
        "flavor": "Vacuum amplifies signals.",
        "unlock_threshold": 5000000,
    },
    "eniac": {
        "id": "eniac",
        "name": "ENIAC Unit",
        "category": "vacuum_tubes",
        "era": 3,
        "base_cost": 50000000,
        "base_production": 2500000,
        "cost_multiplier": 1.15,
        "icon": "🖥️",
        "flavor": "18,000 vacuum tubes compute.",
        "unlock_threshold": 20000000,
    },
    "cooling_system": {
        "id": "cooling_system",
        "name": "Cooling System",
        "category": "vacuum_tubes",
        "era": 3,
        "base_cost": 200000000,
        "base_production": 10000000,
        "cost_multiplier": 1.15,
        "icon": "❄️",
        "flavor": "Keep those tubes from melting.",
        "unlock_threshold": 80000000,
    },
    "transputer": {
        "id": "transputer",
        "name": "Transputer Array",
        "category": "vacuum_tubes",
        "era": 3,
        "base_cost": 800000000,
        "base_production": 40000000,
        "cost_multiplier": 1.15,
        "icon": "🌡️",
        "flavor": "Early parallel computing.",
        "unlock_threshold": 300000000,
    },
}

# Era-specific upgrades
ERA_UPGRADES = {
    # Abacus Era Upgrades
    "abacus_mastery": {
        "id": "abacus_mastery",
        "name": "Abacus Mastery",
        "icon": "🔢",
        "era": 0,
        "category": "abacus",
        "base_cost": 1000,
        "cost_multiplier": 5,
        "effect": 2,  # 2x multiplier
        "max_level": 5,
        "description": "Double all Abacus-era production",
    },
    "clay_inscriptions": {
        "id": "clay_inscriptions",
        "name": "Clay Inscriptions",
        "icon": "📜",
        "era": 0,
        "category": "abacus",
        "base_cost": 500,
        "cost_multiplier": 3,
        "effect": 1,  # +1 per click
        "max_level": 10,
        "description": "Increase click power by +1",
    },
    # Mechanical Era Upgrades
    "gear_lubrication": {
        "id": "gear_lubrication",
        "name": "Gear Lubrication",
        "icon": "🛢️",
        "era": 1,
        "category": "mechanical",
        "base_cost": 50000,
        "cost_multiplier": 5,
        "effect": 2,
        "max_level": 5,
        "description": "Double all Mechanical-era production",
    },
    "precision_crafting": {
        "id": "precision_crafting",
        "name": "Precision Crafting",
        "icon": "🎯",
        "era": 1,
        "category": "mechanical",
        "base_cost": 25000,
        "cost_multiplier": 3,
        "effect": 1,
        "max_level": 10,
        "description": "Increase click power by +5",
    },
    # Electromechanical Era Upgrades
    "relay_optimization": {
        "id": "relay_optimization",
        "name": "Relay Optimization",
        "icon": "⚡",
        "era": 2,
        "category": "electromechanical",
        "base_cost": 2000000,
        "cost_multiplier": 5,
        "effect": 2,
        "max_level": 5,
        "description": "Double all Electromechanical-era production",
    },
    "card_punching": {
        "id": "card_punching",
        "name": "Efficient Card Punching",
        "icon": "🗂️",
        "era": 2,
        "category": "electromechanical",
        "base_cost": 1000000,
        "cost_multiplier": 3,
        "effect": 5,
        "max_level": 10,
        "description": "Increase click power by +25",
    },
    # Vacuum Tubes Era Upgrades
    "heat_management": {
        "id": "heat_management",
        "name": "Heat Management",
        "icon": "🔥",
        "era": 3,
        "category": "vacuum_tubes",
        "base_cost": 50000000,
        "cost_multiplier": 5,
        "effect": 2,
        "max_level": 5,
        "description": "Double all Vacuum Tube-era production",
    },
    "tube_replacement": {
        "id": "tube_replacement",
        "name": "Quick Tube Replacement",
        "icon": "🔌",
        "era": 3,
        "category": "vacuum_tubes",
        "base_cost": 25000000,
        "cost_multiplier": 3,
        "effect": 50,
        "max_level": 10,
        "description": "Increase click power by +250",
    },
}

# Binary/Invention Prestige System
PRESTIGE_UPGRADES = {
    "define_bit": {
        "id": "define_bit",
        "name": "Define Bit",
        "icon": "🔲",
        "era": 0,
        "description": "Invent the concept of a binary digit",
        "base_cost": 0,  # Free - first prestige
        "effect": 2,  # 2x production multiplier
        "max_level": 1,
        "unlock_threshold": 500,  # pebbles
    },
    "boolean_algebra": {
        "id": "boolean_algebra",
        "name": "Boolean Algebra",
        "icon": "🔣",
        "era": 1,
        "description": "Formalize logical operations",
        "base_cost": 1000,  # Costs pebbles after define_bit
        "effect": 2,  # Additional 2x multiplier
        "max_level": 1,
        "unlock_threshold": 50000,  # ticks
        "prerequisite": "define_bit",
    },
    "logic_gates": {
        "id": "logic_gates",
        "name": "Logic Gates",
        "icon": "🔀",
        "era": 2,
        "description": "Build AND, OR, NOT gates",
        "base_cost": 100000,
        "effect": 2,
        "max_level": 1,
        "unlock_threshold": 5000000,  # pulses
        "prerequisite": "boolean_algebra",
    },
}

# Cost multipliers by era (for later eras)
COST_MULT_BY_ERA = {
    0: 1.20,  # Abacus - slower scaling
    1: 1.18,  # Mechanical
    2: 1.15,  # Electromechanical
    3: 1.12,  # Vacuum Tubes
    4: 1.10,  # Transistors
    5: 1.08,  # Quantum
    6: 1.05,  # Cosmic
}

# Era-specific visual themes
ERA_VISUAL_THEMES = {
    "ancient": {
        "background": (60, 40, 20),
        "primary": (139, 90, 43),
        "accent": (210, 180, 140),
        "glow": (255, 200, 100),
    },
    "steampunk": {
        "background": (40, 30, 20),
        "primary": (184, 134, 11),
        "accent": (218, 165, 32),
        "glow": (255, 180, 50),
    },
    "industrial": {
        "background": (30, 30, 35),
        "primary": (100, 100, 100),
        "accent": (169, 169, 169),
        "glow": (200, 200, 200),
    },
    "retro_computer": {
        "background": (20, 15, 25),
        "primary": (180, 60, 60),
        "accent": (255, 140, 0),
        "glow": (255, 200, 100),
    },
    "modern": {
        "background": (15, 18, 28),
        "primary": (0, 170, 220),
        "accent": (160, 90, 230),
        "glow": (0, 255, 255),
    },
    "quantum": {
        "background": (10, 5, 20),
        "primary": (138, 43, 226),
        "accent": (0, 255, 255),
        "glow": (200, 100, 255),
    },
    "cosmic": {
        "background": (5, 0, 15),
        "primary": (75, 0, 130),
        "accent": (255, 215, 0),
        "glow": (255, 255, 200),
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
    "quantum": {
        "name": "Quantum",
        "description": "Quantum Processor - Qubit-based computing",
        "icon": "⚛️",
        "color": (138, 43, 226),  # Purple
    },
    "hyper": {
        "name": "Hyper",
        "description": "Hyperscale Cluster - Distributed computing",
        "icon": "🌌",
        "color": (75, 0, 130),  # Indigo
    },
    "singularity": {
        "name": "Singularity",
        "description": "Transcendent Computing - Beyond limits",
        "icon": "✨",
        "color": (255, 215, 0),  # Gold
    },
}

COMPONENT_BASE_COSTS = {
    "CPU": 100,
    "BUS": 50,
    "RAM": 200,
    "STORAGE": 300,
    "GPU": 400,
}


def get_all_generators():
    """Get merged dictionary of all generators, sorted by base_cost"""
    # Include era-specific generators
    era_gens = {}
    era_gens.update(ABACUS_GENERATORS)
    era_gens.update(MECHANICAL_GENERATORS)
    era_gens.update(ELECTROMECHANICAL_GENERATORS)
    era_gens.update(VACUUM_TUBE_GENERATORS)
    
    basic = GENERATORS if GENERATORS else CONFIG["GENERATORS"]
    hardware = CONFIG.get("HARDWARE_GENERATORS", {})
    all_gen = {**era_gens, **basic, **hardware}
    
    sorted_items = sorted(all_gen.items(), key=lambda x: x[1].get('base_cost', float('inf')))
    return dict(sorted_items)


def get_all_upgrades():
    """Get merged dictionary of all upgrades, sorted by base_cost"""
    # Include era-specific upgrades
    era_upgrades = ERA_UPGRADES.copy()
    
    basic = UPGRADES if UPGRADES else CONFIG["UPGRADES"]
    hardware = CONFIG.get("HARDWARE_UPGRADES", {})
    all_upg = {**era_upgrades, **basic, **hardware}
    
    sorted_items = sorted(all_upg.items(), key=lambda x: x[1].get('base_cost', float('inf')))
    return dict(sorted_items)

# Initialize UPGRADES from CONFIG since TOON parsing has issues
UPGRADES = {}
if "UPGRADES" in CONFIG:
    for upgrade_id, upgrade in CONFIG["UPGRADES"].items():
        UPGRADES[upgrade_id] = upgrade


# Ensure we have generators and upgrades from CONFIG if TOON loading failed
def ensure_config_loaded():
    global GENERATORS, UPGRADES
    if not GENERATORS:
        GENERATORS = CONFIG["GENERATORS"]
    if not UPGRADES:
        UPGRADES = CONFIG["UPGRADES"]


ensure_config_loaded()


def format_number(num):
    """Format a number with K/M/B/T suffixes"""
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


def get_exact_bits(category, generation):
    """
    Get exact bit capacity for a component based on category and generation.
    Used by the LED grid visualization system.
    """
    # Base capacities by category (in bits)
    base_capacities = {
        "cpu": 1024,           # 1 KB
        "ram": 2048,           # 2 KB  
        "storage": 4096,       # 4 KB
        "gpu": 1024,           # 1 KB
        "network": 512,        # 512 B
        "mobile": 1024,        # 1 KB
        "ai": 4096,            # 4 KB
        "quantum": 8192,       # 8 KB
        "hyper": 16384,        # 16 KB
        "singularity": 32768,   # 32 KB
    }
    
    base = base_capacities.get(category, 1024)
    
    # Multiply by generation (each gen doubles)
    return base * (2 ** generation)


def get_generators_for_era(era):
    """Get all generators available in a specific era"""
    era_gens = {}
    
    if era == 0:
        era_gens = ABACUS_GENERATORS.copy()
    elif era == 1:
        era_gens = {**ABACUS_GENERATORS, **MECHANICAL_GENERATORS}
    elif era == 2:
        era_gens = {**MECHANICAL_GENERATORS, **ELECTROMECHANICAL_GENERATORS}
    elif era == 3:
        era_gens = {**ELECTROMECHANICAL_GENERATORS, **VACUUM_TUBE_GENERATORS}
    elif era >= 4:
        # Transistor era includes all hardware generators
        era_gens = {**VACUUM_TUBE_GENERATORS, **CONFIG.get("HARDWARE_GENERATORS", {})}
    
    return era_gens