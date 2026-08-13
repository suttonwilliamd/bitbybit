"""
Data-driven balance manager for Bit by Bit Game
Loads all balancing values from TOON config files
"""

import math
from typing import Dict, Any, Optional
from toon_parser import load_toon_file


class BalanceManager:
    """
    Centralized balance management
    Loads all magic numbers from TOON config
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._load_config()
        
    def _load_config(self):
        """Load balance configuration"""
        try:
            config = load_toon_file("config/balance.toon")
        except Exception:
            config = {}
            
        # Production
        self.production = config.get("production", {})
        self.base_click_power = self.production.get("base_click_power", 1)
        self.generator_cost_multiplier = self.production.get("generator_cost_multiplier", 1.15)
        self.upgrade_cost_multiplier = self.production.get("upgrade_cost_multiplier", 3.0)
        self.max_cost = self.production.get("max_cost", 10**15)
        
        # Rebirth
        rebirth = config.get("rebirth", {})
        self.rebirth_base_threshold = rebirth.get("base_threshold", 1048576)
        self.rebirth_gen_multiplier = rebirth.get("generation_threshold_multiplier", 15.5)
        self.base_shards = rebirth.get("base_shards", 1)
        self.shards_per_log10 = rebirth.get("shards_per_log10", 1)
        self.generation_bonus = rebirth.get("generation_bonus", 5)
        
        # Prestige
        prestige = config.get("prestige", {})
        self.prestige_min_generation = prestige.get("min_generation", 3)
        self.prestige_min_bits = prestige.get("min_bits", 1000000)
        self.prestige_production_bonus = prestige.get("production_bonus_per_prestige", 0.1)
        self.prestige_click_bonus = prestige.get("click_bonus_per_prestige", 1)
        
        # Hardware generations
        self.hardware_generations = config.get("hardware_generations", [])
        
        # Components
        self.components = config.get("components", {})
        
        # Visuals
        visuals = config.get("visuals", {})
        self.crt_effects_default = visuals.get("crt_effects", True)
        self.binary_rain_default = visuals.get("binary_rain", True)
        self.particle_effects_default = visuals.get("particle_effects", True)
        self.target_fps = visuals.get("target_fps", 60)
        self.max_particles = visuals.get("max_particles", 100)
        
        # Saving
        saving = config.get("saving", {})
        self.auto_save_interval = saving.get("auto_save_interval", 30000)
        self.max_offline_time = saving.get("max_offline_time", 86400000)
        self.offline_efficiency = saving.get("offline_efficiency", 0.75)
        self.backup_count = saving.get("backup_count", 3)
        
        # Formatting
        formatting = config.get("formatting", {})
        self.small_threshold = formatting.get("small_threshold", 1000)
        self.medium_threshold = formatting.get("medium_threshold", 1000000)
        self.large_threshold = formatting.get("large_threshold", 1000000000)
        self.huge_threshold = formatting.get("huge_threshold", 1000000000000)
        
        # Unlocks
        unlocks = config.get("unlocks", {})
        self.unlock_upgrades = unlocks.get("upgrades", 1000)
        self.unlock_second_gen = unlocks.get("second_generator", 100)
        self.unlock_third_gen = unlocks.get("third_generator", 1000)
        self.unlock_compression = unlocks.get("compression_generators", 10000)
        self.unlock_prestige = unlocks.get("prestige", 1000000)
        
    def get_generator_cost(self, base_cost: float, count: int) -> int:
        """Calculate generator cost with configured multiplier"""
        return int(min(
            base_cost * math.pow(self.generator_cost_multiplier, count),
            self.max_cost
        ))
        
    def get_upgrade_cost(self, base_cost: float, level: int) -> int:
        """Calculate upgrade cost with configured multiplier"""
        return int(min(
            base_cost * math.pow(self.upgrade_cost_multiplier, level),
            self.max_cost
        ))
        
    def get_rebirth_threshold(self, generation: int) -> int:
        """Calculate rebirth threshold for a generation"""
        if generation == 0:
            return self.rebirth_base_threshold
        return int(self.rebirth_base_threshold * math.pow(self.rebirth_gen_multiplier, generation))
        
    def get_prestige_bonus(self, prestige_count: int) -> float:
        """Calculate prestige production bonus"""
        return 1.0 + (prestige_count * self.prestige_production_bonus)
        
    def get_prestige_click_bonus(self, prestige_count: int) -> float:
        """Calculate prestige click bonus"""
        return prestige_count * self.prestige_click_bonus
        
    def format_number(self, num: float) -> str:
        """Format number with configured thresholds"""
        if num < self.small_threshold:
            return str(int(num))
        elif num < self.medium_threshold:
            return f"{num / 1000:.1f}K"
        elif num < self.large_threshold:
            return f"{num / 1000000:.1f}M"
        elif num < self.huge_threshold:
            return f"{num / 1000000000:.1f}B"
        else:
            return f"{num / 1000000000000:.1f}T"
            
    def get_component_cost(self, component_name: str, level: int) -> int:
        """Get component upgrade cost"""
        comp = self.components.get(component_name.lower(), {})
        base_cost = comp.get("base_cost", 100)
        multiplier = comp.get("cost_multiplier", 2.0)
        return int(base_cost * math.pow(multiplier, level))
        
    def get_component_bits(self, component_name: str, level: int) -> int:
        """Get component bit capacity"""
        comp = self.components.get(component_name.lower(), {})
        base_bits = comp.get("base_bits", 64)
        return base_bits * (2 ** level)


# Global instance
BALANCE = BalanceManager()


def get_balance() -> BalanceManager:
    """Get the global balance manager instance"""
    return BALANCE
