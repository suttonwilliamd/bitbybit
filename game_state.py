"""
Game state management for Bit by Bit Game
"""

import pygame
import math
import json
from constants import CONFIG, GENERATORS, UPGRADES, HARDWARE_GENERATIONS, COST_MULT_BY_ERA


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

        # Era: entropy, compression
        self.era = "entropy"

        # Visual settings - CRT effects OFF by default
        self.visual_settings = {
            "crt_effects": False,
            "binary_rain": True,
            "particle_effects": True,
        }

        # Data Shards system
        self.data_shards = 0  # New name for compression tokens
        self.total_data_shards = 0
        self.last_collect_bits = 0  # Track last collection threshold
        self.compressed_bits = 0
        self.total_compressed_bits = 0
        self.overhead_rate = 0
        self.efficiency = 1.0

        # Compression generators and upgrades
        self.compression_generators = {}
        self.data_shard_upgrades = {}

        # Meta progression
        self.total_rebirths = 0
        self.total_lifetime_bits = 0
        self.hardware_generation = 0  # 0=Mainframe, 1=Apple II, 2=IBM PC, etc.
        self.unlocked_hardware_categories = ["cpu"]  # Start with CPU only

        # Prestige system
        self.prestige_currency = 0  # New prestige currency
        self.total_prestige_currency = 0
        self.prestige_count = 0

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
            if "data_shard_upgrades" in compression_ups:
                for upgrade in compression_ups["data_shard_upgrades"]:
                    self.data_shard_upgrades[upgrade["id"]] = upgrade
        except (FileNotFoundError, KeyError, ImportError):
            pass

        # Initialize compression structures
        for gen_id in self.compression_generators:
            self.compression_generators[gen_id] = {"count": 0, "total_bought": 0}

        for upgrade_id in self.data_shard_upgrades:
            self.data_shard_upgrades[upgrade_id] = {"level": 0}

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

            # Apply era multiplier (+25% per era as per design doc)
            era_multiplier = CONFIG.get("ERA_MULTIPLIER", 1.25)

            # Apply prestige bonus
            prestige_bonus = self.get_prestige_bonus()

            return base_production * entropy_multiplier * prestige_bonus * era_multiplier

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

            # Apply data shard upgrade bonuses
            mastery_bonus = self.get_data_shard_upgrade_effect("compression_mastery") / 100.0
            parallel_bonus = self.get_data_shard_upgrade_effect("parallel_streams") / 100.0
            
            # Apply compression mastery bonus to production
            compressed_production *= (1 + mastery_bonus)
            
            # Apply parallel streams bonus per generator type
            if parallel_bonus > 0:
                gen_count = sum(gen_data["count"] for gen_data in self.compression_generators.values())
                compressed_production *= (1 + parallel_bonus * gen_count / 10)
            
            # Calculate efficiency floor from upgrades
            efficiency_floor = self.get_data_shard_upgrade_effect("efficiency_shield") / 100.0
            
            # Calculate penalty threshold reduction from entropy barrier
            penalty_threshold_reduction = self.get_data_shard_upgrade_effect("entropy_barrier") / 100.0
            
            # Calculate net production and efficiency
            net_overhead = overhead_production
            efficiency = (
                compressed_production / (compressed_production + net_overhead)
                if (compressed_production + net_overhead) > 0
                else 1.0
            )
            
            # Apply efficiency floor
            efficiency = max(efficiency, efficiency_floor)

            self.efficiency = efficiency
            self.overhead_rate = net_overhead

            # Apply efficiency penalties with threshold reduction
            penalty_50 = 0.5 - penalty_threshold_reduction
            penalty_70 = 0.7 - penalty_threshold_reduction
            penalty_90 = 0.9 - penalty_threshold_reduction
            
            if efficiency < penalty_50:
                penalty = 0.5
            elif efficiency < penalty_70:
                penalty = 0.75
            elif efficiency < penalty_90:
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
        prestige_click_bonus = self.get_click_prestige_bonus()
        return base_click + click_upgrade_bonus + prestige_click_bonus

    def get_generator_cost(self, generator_id, quantity=1):
        # Check both basic and hardware generators
        if generator_id in CONFIG["GENERATORS"]:
            generator = CONFIG["GENERATORS"][generator_id]
        elif generator_id in CONFIG.get("HARDWARE_GENERATORS", {}):
            generator = CONFIG["HARDWARE_GENERATORS"][generator_id]
        else:
            return float('inf')  # Unknown generator
        
        current_count = self.generators[generator_id]["count"]
        
        # Get era-specific cost multiplier (design doc: 1.15 for early eras, 1.10 for late)
        era_cost_mult = COST_MULT_BY_ERA.get(self.hardware_generation, 1.15)
        
        # Use generator's own multiplier if set, otherwise use era multiplier
        cost_multiplier = generator.get("cost_multiplier", era_cost_mult)

        if quantity == 1:
            return int(
                generator["base_cost"]
                * math.pow(cost_multiplier, current_count)
            )

        # Bulk purchase cost calculation
        first_cost = generator["base_cost"] * math.pow(
            cost_multiplier, current_count
        )
        ratio = math.pow(cost_multiplier, quantity) - 1
        denominator = cost_multiplier - 1

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

        category_upgrades = {
            "cpu": "overclock",
            "ram": "memory_optimization",
            "storage": "data_compression",
            "gpu": "ray_tracing",
            "network": "bandwidth_boost",
            "mobile": "battery_efficiency",
            "ai": "neural_network",
            "quantum": "quantum_entanglement",
            "hyper": "hyper_parallelism",
            "singularity": "transcendence",
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
        shard_bonus = self.get_rebirth_shard_bonus()
        return int((base_tokens + era_bonus) * (1 + shard_bonus))

    def can_rebirth(self, bit_grid=None):
        """Check if rebirth is available - requires 100% era completion"""
        # Check basic threshold
        if self.total_bits_earned < self.get_rebirth_threshold():
            return False

        # Check if era is 100% complete (if bit_grid is available)
        if bit_grid:
            threshold = self.get_rebirth_threshold()
            era_completion = bit_grid.get_era_completion_percentage(threshold)
            return era_completion >= 99.9  # Allow for floating point precision

        # Fallback to basic threshold check
        return True

    def get_rebirth_threshold(self):
        """Get the current rebirth threshold based on hardware generation era capacity"""
        era_thresholds = {
            0: 9728,  # Mainframe Era
            1: 150016,  # Apple II Era
            2: 1114112,  # IBM PC Era
            3: 46137344,  # Multimedia Era
            4: 10884218880,  # Internet Era
            5: 1832519377920,  # Mobile Era
            6: 111669149696,  # AI Era
            7: 43980465111040,  # Quantum Era
            8: 175921860444160,  # Hyper Era
            9: 703687441776640,  # Singularity Era
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

        # Initialize data shards if first rebirth
        if not hasattr(self, "data_shards"):
            self.data_shards = 0
            self.total_data_shards = 0
            self.era = "compression"  # Move to compression era
            self.compressed_bits = 0
            self.overhead_rate = 0
            self.efficiency = 1.0

        # Add data shards
        self.data_shards += tokens
        self.total_data_shards += tokens

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

    def get_prestige_bonus(self):
        """Calculate prestige production bonus based on prestige count"""
        if self.prestige_count == 0:
            return 1.0
        # Each prestige adds 10% bonus: 1 prestige = 1.1x, 10 prestige = 2x, etc.
        return 1.0 + (self.prestige_count * 0.1)

    def get_click_prestige_bonus(self):
        """Calculate prestige click bonus"""
        if self.prestige_count == 0:
            return 0
        # Each prestige adds +1 to base click
        return self.prestige_count

    def get_prestige_currency_earned(self):
        """Calculate prestige currency earned on prestige"""
        # Base formula: sqrt(total_bits_earned) / 100
        # Modified by hardware generation
        base_earned = math.sqrt(max(0, self.total_bits_earned)) / 100
        generation_bonus = 1.0 + (self.hardware_generation * 0.5)
        return int(base_earned * generation_bonus)

    def can_prestige(self):
        """Check if prestige is available"""
        # Require reaching at least hardware generation 3 and 1M total bits
        return self.hardware_generation >= 3 and self.total_bits_earned >= 1000000

    def perform_prestige(self):
        """Perform prestige - full restart with bonuses"""
        if not self.can_prestige():
            return False

        # Calculate prestige currency earned
        currency_earned = self.get_prestige_currency_earned()

        # Add prestige currency
        self.prestige_currency += currency_earned
        self.total_prestige_currency += currency_earned
        self.prestige_count += 1

        # Reset everything for full prestige
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

        # Keep prestige currency but reset hardware
        self.hardware_generation = 0
        self.unlocked_hardware_categories = ["cpu"]

        # Reset era
        self.era = "entropy"
        self.data_shards = 0

        return True

    def get_data_shards_earned(self):
        """Calculate data shards earned based on total bits earned since last collection"""
        if self.total_bits_earned < 10000:
            return 0
        
        bits_since_collect = self.total_bits_earned - self.last_collect_bits
        if bits_since_collect < 10000:
            return 0
        
        shards = max(0, int(math.log10(bits_since_collect)) - 3)
        return shards

    def can_collect_data_shards(self):
        """Check if player can collect NEW data shards"""
        threshold = self.get_collect_threshold()
        if self.total_bits_earned < threshold:
            return False
        
        bits_since_collect = self.total_bits_earned - self.last_collect_bits
        return bits_since_collect >= threshold

    def collect_data_shards(self):
        """Collect data shards based on current progress (doesn't reset anything)"""
        if not self.can_collect_data_shards():
            return 0
        
        shards = self.get_data_shards_earned()
        if shards > 0:
            self.data_shards += shards
            self.total_data_shards += shards
            self.last_collect_bits = self.total_bits_earned
        return shards

    def get_data_shard_upgrade_cost(self, upgrade_id):
        """Calculate cost for next level of a data shard upgrade"""
        if upgrade_id not in self.data_shard_upgrades:
            return 0
        
        upgrade = self.data_shard_upgrades[upgrade_id]
        current_level = upgrade.get("level", 0)
        max_level = upgrade.get("max_level", 1)
        
        if current_level >= max_level:
            return None
        
        base_cost = upgrade.get("base_cost", 1)
        cost_scale = upgrade.get("cost_scale", 1)
        
        return base_cost + (current_level * cost_scale)
    
    def get_data_shard_upgrade_effect(self, upgrade_id):
        """Calculate current effect bonus from a data shard upgrade"""
        if upgrade_id not in self.data_shard_upgrades:
            return 0
        
        upgrade = self.data_shard_upgrades[upgrade_id]
        current_level = upgrade.get("level", 0)
        effect_per_level = upgrade.get("effect_per_level", 0)
        
        return current_level * effect_per_level
    
    def can_purchase_data_shard_upgrade(self, upgrade_id):
        """Check if player can afford a data shard upgrade"""
        cost = self.get_data_shard_upgrade_cost(upgrade_id)
        if cost is None:
            return False
        return self.data_shards >= cost
    
    def purchase_data_shard_upgrade(self, upgrade_id):
        """Purchase a data shard upgrade using data shards"""
        if not self.can_purchase_data_shard_upgrade(upgrade_id):
            return False
        
        cost = self.get_data_shard_upgrade_cost(upgrade_id)
        if cost is None:
            return False
        
        self.data_shards -= cost
        self.data_shard_upgrades[upgrade_id]["level"] += 1
        return True
    
    def get_collect_threshold(self):
        """Get the bits threshold for collecting data shards (modified by quick_collect)"""
        base_threshold = 10000
        reduction = self.get_data_shard_upgrade_effect("quick_collect") / 100.0
        return int(base_threshold * (1 - reduction))
    
    def get_rebirth_shard_bonus(self):
        """Get the bonus multiplier for shards earned on rebirth"""
        return self.get_data_shard_upgrade_effect("shard_doubler") / 100.0
