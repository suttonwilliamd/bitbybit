"""
Game state management for Bit by Bit Game
"""

import pygame
import math
import json
from constants import (
    CONFIG, GENERATORS, UPGRADES, HARDWARE_GENERATIONS, COST_MULT_BY_ERA,
    ERAS, ABACUS_GENERATORS, MECHANICAL_GENERATORS, ELECTROMECHANICAL_GENERATORS,
    VACUUM_TUBE_GENERATORS, ERA_UPGRADES, PRESTIGE_UPGRADES
)


class GameState:
    def __init__(self):
        # Start with Era 0 (Abacus) - pebbles as currency
        self.current_era = 0  # 0=Abacus, 1=Mechanical, 2=Electromechanical, etc.
        
        # Currency (pebbles in Era 0, converts to bits when binary is invented)
        self.pebbles = 0  # Era 0 currency
        self.bits = 0  # Modern currency (available after "Define Bit")
        self.total_pebbles_earned = 0
        self.total_bits_earned = 0
        
        self.total_clicks = 0
        self.start_time = pygame.time.get_ticks()
        self.total_play_time = 0
        self.last_save_time = pygame.time.get_ticks()

        # Generators - organized by era
        self.generators = {}
        self.unlocked_generators = ["pebble"]  # Start with pebble counter

        # Upgrades
        self.upgrades = {}
        
        # Era-specific upgrades
        self.era_upgrades = {}
        
        # Prestige upgrades (Binary invention system)
        self.prestige_upgrades = {}
        self.binary_invented = False  # Has "Define Bit" been done?
        self.boolean_algebra_invented = False  # Has Boolean Algebra been done?
        
        # Binary efficiency multiplier (from prestige)
        self.binary_efficiency = 1.0

        # Tutorial state
        self.tutorial_step = 0
        self.has_seen_tutorial = True  # Disabled

        # Era: entropy, compression (for compatibility with existing systems)
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
        # Initialize era-specific generators (Abacus Era - Era 0)
        for gen_id in ABACUS_GENERATORS:
            self.generators[gen_id] = {"count": 0, "total_bought": 0}
        
        for gen_id in MECHANICAL_GENERATORS:
            self.generators[gen_id] = {"count": 0, "total_bought": 0}
            
        for gen_id in ELECTROMECHANICAL_GENERATORS:
            self.generators[gen_id] = {"count": 0, "total_bought": 0}
            
        for gen_id in VACUUM_TUBE_GENERATORS:
            self.generators[gen_id] = {"count": 0, "total_bought": 0}

        # Initialize basic generators (for compatibility)
        for gen_id in CONFIG["GENERATORS"]:
            self.generators[gen_id] = {"count": 0, "total_bought": 0}

        # Initialize hardware-specific generators
        if "HARDWARE_GENERATORS" in CONFIG:
            for gen_id in CONFIG["HARDWARE_GENERATORS"]:
                self.generators[gen_id] = {"count": 0, "total_bought": 0}

        # Initialize basic upgrades
        for upgrade_id in CONFIG["UPGRADES"]:
            self.upgrades[upgrade_id] = {"level": 0}
        
        # Initialize era-specific upgrades
        for upgrade_id in ERA_UPGRADES:
            self.era_upgrades[upgrade_id] = {"level": 0}
            
        # Initialize prestige upgrades
        for upgrade_id in PRESTIGE_UPGRADES:
            self.prestige_upgrades[upgrade_id] = {"purchased": False}

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
        # Use the new era progression system
        return self.get_era_production_rate()

    # =========================================================================
    # ERA PROGRESSION SYSTEM
    # =========================================================================
    
    def get_current_currency(self):
        """Get the name of the current era's currency"""
        if self.current_era == 0:
            return "pebbles" if not self.binary_invented else "bits"
        elif self.current_era >= 4:
            return "bits"
        else:
            era_info = ERAS.get(self.current_era, {})
            return era_info.get("currency_name", "units")
    
    def get_current_currency_value(self):
        """Get the current era's currency amount (pebbles or bits)"""
        if self.current_era == 0 and not self.binary_invented:
            return self.pebbles
        return self.bits
    
    def get_total_currency_earned(self):
        """Get total currency earned in current era"""
        if self.current_era == 0 and not self.binary_invented:
            return self.total_pebbles_earned
        return self.total_bits_earned
    
    def get_era_production_rate(self):
        """Calculate production rate based on current era"""
        base_production = 0
        
        # Era 0: Abacus generators
        if self.current_era == 0:
            for gen_id, gen_data in self.generators.items():
                if gen_data["count"] > 0 and gen_id in ABACUS_GENERATORS:
                    generator = ABACUS_GENERATORS[gen_id]
                    # Check if generator is unlocked
                    if self.is_era_generator_unlocked(gen_id):
                        gen_production = gen_data["count"] * generator["base_production"]
                        base_production += gen_production
            
            # Apply era-specific upgrades
            era_multiplier = self.get_era_upgrade_multiplier("abacus")
            base_production *= era_multiplier
            
        # Era 1: Mechanical generators
        elif self.current_era == 1:
            for gen_id, gen_data in self.generators.items():
                if gen_data["count"] > 0 and gen_id in MECHANICAL_GENERATORS:
                    generator = MECHANICAL_GENERATORS[gen_id]
                    if self.is_era_generator_unlocked(gen_id):
                        gen_production = gen_data["count"] * generator["base_production"]
                        base_production += gen_production
            
            era_multiplier = self.get_era_upgrade_multiplier("mechanical")
            base_production *= era_multiplier
            
        # Era 2: Electromechanical generators
        elif self.current_era == 2:
            for gen_id, gen_data in self.generators.items():
                if gen_data["count"] > 0 and gen_id in ELECTROMECHANICAL_GENERATORS:
                    generator = ELECTROMECHANICAL_GENERATORS[gen_id]
                    if self.is_era_generator_unlocked(gen_id):
                        gen_production = gen_data["count"] * generator["base_production"]
                        base_production += gen_production
            
            era_multiplier = self.get_era_upgrade_multiplier("electromechanical")
            base_production *= era_multiplier
            
        # Era 3: Vacuum Tube generators
        elif self.current_era == 3:
            for gen_id, gen_data in self.generators.items():
                if gen_data["count"] > 0 and gen_id in VACUUM_TUBE_GENERATORS:
                    generator = VACUUM_TUBE_GENERATORS[gen_id]
                    if self.is_era_generator_unlocked(gen_id):
                        gen_production = gen_data["count"] * generator["base_production"]
                        base_production += gen_production
            
            era_multiplier = self.get_era_upgrade_multiplier("vacuum_tubes")
            base_production *= era_multiplier
            
        # Era 4+: Transistors (modern hardware generators)
        elif self.current_era >= 4:
            # Use existing hardware generator logic
            for gen_id, gen_data in self.generators.items():
                if (gen_data["count"] > 0 and gen_id in CONFIG.get("HARDWARE_GENERATORS", {})):
                    generator = CONFIG["HARDWARE_GENERATORS"][gen_id]
                    category = generator["category"]
                    if self.is_hardware_category_unlocked(category):
                        category_multiplier = self.get_category_multiplier(category)
                        production = gen_data["count"] * generator["base_production"] * category_multiplier
                        base_production += production
        
        # Apply binary efficiency multiplier (from prestige upgrades)
        base_production *= self.binary_efficiency
        
        # Apply prestige bonus
        prestige_bonus = self.get_prestige_bonus()
        base_production *= prestige_bonus
        
        return base_production
    
    def is_era_generator_unlocked(self, generator_id):
        """Check if an era-specific generator is unlocked"""
        # Check which generator dictionary it belongs to
        if generator_id in ABACUS_GENERATORS:
            generator = ABACUS_GENERATORS[generator_id]
        elif generator_id in MECHANICAL_GENERATORS:
            generator = MECHANICAL_GENERATORS[generator_id]
        elif generator_id in ELECTROMECHANICAL_GENERATORS:
            generator = ELECTROMECHANICAL_GENERATORS[generator_id]
        elif generator_id in VACUUM_TUBE_GENERATORS:
            generator = VACUUM_TUBE_GENERATORS[generator_id]
        else:
            return False
        
        # Check if there's an unlock threshold
        if "unlock_threshold" not in generator:
            return True
        
        # Check based on current era's total currency
        total_currency = self.get_total_currency_earned()
        return total_currency >= generator["unlock_threshold"]
    
    def get_era_upgrade_multiplier(self, category):
        """Get the upgrade multiplier for an era category"""
        multiplier = 1.0
        
        # Find upgrades for this category
        for upgrade_id, upgrade_data in ERA_UPGRADES.items():
            if upgrade_data.get("category") == category:
                level = self.era_upgrades.get(upgrade_id, {}).get("level", 0)
                effect = upgrade_data.get("effect", 1)
                multiplier *= math.pow(effect, level)
        
        return multiplier
    
    def get_era_click_power(self):
        """Calculate click power based on current era"""
        base_click = 1
        
        # Era-specific click bonuses
        if self.current_era == 0:
            level = self.era_upgrades.get("clay_inscriptions", {}).get("level", 0)
            base_click += level * ERA_UPGRADES["clay_inscriptions"]["effect"]
        elif self.current_era == 1:
            level = self.era_upgrades.get("precision_crafting", {}).get("level", 0)
            base_click += level * ERA_UPGRADES["precision_crafting"]["effect"]
        elif self.current_era == 2:
            level = self.era_upgrades.get("card_punching", {}).get("level", 0)
            base_click += level * ERA_UPGRADES["card_punching"]["effect"]
        elif self.current_era == 3:
            level = self.era_upgrades.get("tube_replacement", {}).get("level", 0)
            base_click += level * ERA_UPGRADES["tube_replacement"]["effect"]
        
        # Add basic click upgrade bonus
        click_upgrade_level = self.upgrades.get("click_power", {}).get("level", 0)
        click_upgrade_bonus = click_upgrade_level * CONFIG["UPGRADES"]["click_power"]["effect"]
        
        # Add prestige click bonus
        prestige_click_bonus = self.get_click_prestige_bonus()
        
        # Apply binary efficiency to click as well
        return (base_click + click_upgrade_bonus + prestige_click_bonus) * self.binary_efficiency
    
    def get_era_generator_cost(self, generator_id, quantity=1):
        """Get the cost for an era-specific generator"""
        # Determine which generator dict to use
        if generator_id in ABACUS_GENERATORS:
            generator = ABACUS_GENERATORS[generator_id]
        elif generator_id in MECHANICAL_GENERATORS:
            generator = MECHANICAL_GENERATORS[generator_id]
        elif generator_id in ELECTROMECHANICAL_GENERATORS:
            generator = ELECTROMECHANICAL_GENERATORS[generator_id]
        elif generator_id in VACUUM_TUBE_GENERATORS:
            generator = VACUUM_TUBE_GENERATORS[generator_id]
        elif generator_id in CONFIG["GENERATORS"]:
            generator = CONFIG["GENERATORS"][generator_id]
        elif generator_id in CONFIG.get("HARDWARE_GENERATORS", {}):
            generator = CONFIG["HARDWARE_GENERATORS"][generator_id]
        else:
            return float('inf')
        
        current_count = self.generators[generator_id]["count"]
        
        # Get era-specific cost multiplier
        era_cost_mult = COST_MULT_BY_ERA.get(self.current_era, 1.15)
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
    
    def get_era_upgrade_cost(self, upgrade_id):
        """Get the cost for an era-specific upgrade"""
        if upgrade_id not in ERA_UPGRADES:
            return float('inf')
        
        upgrade = ERA_UPGRADES[upgrade_id]
        current_level = self.era_upgrades.get(upgrade_id, {}).get("level", 0)
        
        return int(
            upgrade["base_cost"]
            * math.pow(upgrade["cost_multiplier"], current_level)
        )
    
    def can_afford_era_upgrade(self, upgrade_id):
        """Check if player can afford an era upgrade"""
        cost = self.get_era_upgrade_cost(upgrade_id)
        if self.current_era == 0 and not self.binary_invented:
            return self.pebbles >= cost
        return self.bits >= cost
    
    def purchase_era_upgrade(self, upgrade_id):
        """Purchase an era-specific upgrade"""
        if not self.can_afford_era_upgrade(upgrade_id):
            return False
        
        cost = self.get_era_upgrade_cost(upgrade_id)
        
        if self.current_era == 0 and not self.binary_invented:
            self.pebbles -= cost
        else:
            self.bits -= cost
        
        if upgrade_id not in self.era_upgrades:
            self.era_upgrades[upgrade_id] = {"level": 0}
        self.era_upgrades[upgrade_id]["level"] += 1
        return True
    
    def can_advance_era(self):
        """Check if player can advance to the next era"""
        if self.current_era >= len(ERAS) - 1:
            return False
        
        next_era_info = ERAS[self.current_era + 1]
        unlock_bits = next_era_info.get("unlock_bits", 0)
        
        total_currency = self.get_total_currency_earned()
        return total_currency >= unlock_bits
    
    def advance_era(self):
        """Advance to the next era"""
        if not self.can_advance_era():
            return False
        
        self.current_era += 1
        
        # Update unlocked categories for new era
        if self.current_era in ERAS:
            era_info = ERAS[self.current_era]
            # For transistor era and beyond, unlock hardware categories
            if self.current_era >= 4:
                self.unlocked_hardware_categories = era_info.get("generator_categories", ["cpu"])
        
        return True
    
    def get_era_info(self):
        """Get information about the current era"""
        return ERAS.get(self.current_era, {})
    
    def get_next_era_info(self):
        """Get information about the next era"""
        return ERAS.get(self.current_era + 1, None)
    
    def get_era_progress(self):
        """Get progress towards next era (0.0 - 1.0)"""
        next_era = self.get_next_era_info()
        if not next_era:
            return 1.0
        
        unlock_bits = next_era.get("unlock_bits", 0)
        if unlock_bits == 0:
            return 1.0 if self.current_era > 0 else 0.0
        
        total_currency = self.get_total_currency_earned()
        return min(total_currency / unlock_bits, 1.0)
    
    # =========================================================================
    # BINARY INVENTION / PRESTIGE SYSTEM
    # =========================================================================
    
    def can_define_bit(self):
        """Check if Define Bit prestige is available"""
        if self.binary_invented:
            return False
        # Requires 500 pebbles in Abacus era
        return self.total_pebbles_earned >= PRESTIGE_UPGRADES["define_bit"]["unlock_threshold"]
    
    def perform_define_bit(self):
        """Perform Define Bit prestige - converts pebbles to bits"""
        if not self.can_define_bit():
            return False
        
        # Convert pebbles to bits (100:1 ratio)
        conversion_ratio = 100
        converted_bits = self.pebbles // conversion_ratio
        
        # Set up binary mode
        self.binary_invented = True
        self.bits = converted_bits
        self.total_bits_earned = converted_bits
        self.total_pebbles_earned = self.pebbles  # Keep track
        
        # Apply binary efficiency multiplier
        self.binary_efficiency = PRESTIGE_UPGRADES["define_bit"]["effect"]
        
        # Mark prestige upgrade as purchased
        self.prestige_upgrades["define_bit"]["purchased"] = True
        
        # Update currency tracking
        self.pebbles = 0
        
        return True
    
    def can_invent_boolean_algebra(self):
        """Check if Boolean Algebra prestige is available"""
        if self.boolean_algebra_invented or not self.binary_invented:
            return False
        
        # Requires Define Bit first
        if not self.prestige_upgrades.get("define_bit", {}).get("purchased", False):
            return False
        
        # Requires 50,000 pebbles earned in Abacus era
        return self.total_pebbles_earned >= PRESTIGE_UPGRADES["boolean_algebra"]["unlock_threshold"]
    
    def perform_boolean_algebra(self):
        """Perform Boolean Algebra prestige - doubles production"""
        if not self.can_invent_boolean_algebra():
            return False
        
        # Apply additional binary efficiency
        self.boolean_algebra_invented = True
        self.binary_efficiency *= PRESTIGE_UPGRADES["boolean_algebra"]["effect"]
        
        # Mark prestige upgrade as purchased
        self.prestige_upgrades["boolean_algebra"]["purchased"] = True
        
        return True
    
    def can_invent_logic_gates(self):
        """Check if Logic Gates prestige is available"""
        if self.prestige_upgrades.get("logic_gates", {}).get("purchased", False):
            return False
        
        # Requires Boolean Algebra first
        if not self.boolean_algebra_invented:
            return False
        
        # Requires significant progress in Electromechanical era
        return self.current_era >= 2 and self.total_bits_earned >= PRESTIGE_UPGRADES["logic_gates"]["unlock_threshold"]
    
    def perform_logic_gates(self):
        """Perform Logic Gates prestige - another 2x multiplier"""
        if not self.can_invent_logic_gates():
            return False
        
        # Apply additional binary efficiency
        self.binary_efficiency *= PRESTIGE_UPGRADES["logic_gates"]["effect"]
        
        # Mark prestige upgrade as purchased
        self.prestige_upgrades["logic_gates"]["purchased"] = True
        
        return True
    
    def get_binary_invention_progress(self):
        """Get progress towards next binary invention"""
        if self.boolean_algebra_invented and self.prestige_upgrades.get("logic_gates", {}).get("purchased", False):
            return 1.0
        
        if not self.binary_invented:
            threshold = PRESTIGE_UPGRADES["define_bit"]["unlock_threshold"]
            return min(self.total_pebbles_earned / threshold, 1.0)
        
        if not self.boolean_algebra_invented:
            threshold = PRESTIGE_UPGRADES["boolean_algebra"]["unlock_threshold"]
            return min(self.total_pebbles_earned / threshold, 1.0)
        
        # Logic gates
        threshold = PRESTIGE_UPGRADES["logic_gates"]["unlock_threshold"]
        return min(self.total_bits_earned / threshold, 1.0)
    
    # =========================================================================
    # END ERA METHODS
    # =========================================================================

    def get_click_power(self):
        # Use the new era progression system
        return self.get_era_click_power()

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
