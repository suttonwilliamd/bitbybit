"""
Game state management for Bit by Bit Game
"""

import pygame
import math
import json
from constants import CONFIG, GENERATORS, UPGRADES, HARDWARE_GENERATIONS


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

        try:
            from toon_parser import load_toon_file

            compression_gens = load_toon_file("config/compression_generators.toon")
            if "compression_generators" in compression_gens:
                for gen in compression_gens["compression_generators"]:
                    self.compression_generators[gen["id"]] = gen

            compression_ups = load_toon_file("config/compression_upgrades.toon")
            if "compression_token_upgrades" in compression_ups:
                for upgrade in compression_ups["compression_token_upgrades"]:
                    self.compression_upgrades[upgrade["id"]] = upgrade
        except (FileNotFoundError, KeyError, ImportError):
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
                    gen_production = gen_data["count"] * generator["base_production"]
                    base_production += gen_production

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
        # Check both basic and hardware generators
        if generator_id in CONFIG["GENERATORS"]:
            generator = CONFIG["GENERATORS"][generator_id]
        elif generator_id in CONFIG.get("HARDWARE_GENERATORS", {}):
            generator = CONFIG["HARDWARE_GENERATORS"][generator_id]
        else:
            return float('inf')  # Unknown generator
        
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
        # Check both basic and hardware generators
        if generator_id in CONFIG["GENERATORS"]:
            generator = CONFIG["GENERATORS"][generator_id]
            if "unlock_threshold" not in generator:
                return True
            return (
                generator_id in self.unlocked_generators
                or self.total_bits_earned >= generator["unlock_threshold"]
            )
        elif generator_id in CONFIG.get("HARDWARE_GENERATORS", {}):
            generator = CONFIG["HARDWARE_GENERATORS"][generator_id]
            # Hardware generators are unlocked by category
            return self.is_hardware_category_unlocked(generator["category"])
        else:
            # Unknown generator
            return False

    def is_upgrade_unlocked(self, upgrade_id):
        """Check if upgrade is unlocked based on hardware category and bits earned"""
        if upgrade_id in CONFIG["UPGRADES"]:
            # Basic upgrades available from start
            if self.total_bits_earned >= 1000:
                return True
        elif upgrade_id in CONFIG.get("HARDWARE_UPGRADES", {}):
            upgrade = CONFIG["HARDWARE_UPGRADES"][upgrade_id]
            # Hardware upgrades are unlocked by category
            return self.is_hardware_category_unlocked(upgrade["category"])
        else:
            # Unknown upgrade
            return False
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
        """Calculate rebirth progress based on era-specific threshold"""
        threshold = self.get_rebirth_threshold()
        return min(self.total_bits_earned / threshold, 1)

    def get_estimated_rebirth_tokens(self):
        """Calculate compression tokens based on current era completion"""
        threshold = self.get_rebirth_threshold()
        if self.total_bits_earned < threshold:
            return 0
        # Base tokens + bonus for era completion
        base_tokens = int(math.log2(self.total_bits_earned) - 20)
        era_bonus = self.hardware_generation * 5  # Bonus tokens for higher eras
        return base_tokens + era_bonus

    def can_rebirth(self, bit_grid=None):
        """Check if rebirth is available - requires 100% era completion"""
        # Check basic threshold
        if self.total_bits_earned < self.get_rebirth_threshold():
            return False

        # Check if era is 100% complete (if bit_grid is available)
        if bit_grid:
            era_completion = bit_grid.get_era_completion_percentage()
            return era_completion >= 99.9  # Allow for floating point precision

        # Fallback to basic threshold check
        return True

    def get_rebirth_threshold(self):
        """Get the current rebirth threshold based on hardware generation era capacity"""
        # Era-specific bit thresholds (total bits needed to complete each era)
        era_thresholds = {
            0: 9728,  # Mainframe Era: Complete all hardware components
            1: 150016,  # Apple II Era: Complete all hardware components
            2: 1114112,  # IBM PC Era: Complete all hardware components
            3: 46137344,  # Multimedia Era: Complete all hardware components
            4: 10884218880,  # Internet Era: Complete all hardware components
            5: 1832519377920,  # Mobile Era: Complete all hardware components
            6: 111669149696,  # AI Era: Complete all hardware components
        }

        return era_thresholds.get(self.hardware_generation, 9728)

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
