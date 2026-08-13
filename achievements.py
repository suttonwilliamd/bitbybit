"""
Achievements system for Bit by Bit Game
Defines achievements with triggers and rewards
"""

import pygame
import math
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class AchievementCategory(Enum):
    """Categories for organizing achievements"""
    CLICKING = "clicking"
    GENERATORS = "generators"
    UPGRADES = "upgrades"
    PROGRESSION = "progression"
    COMPRESSION = "compression"
    PRESTIGE = "prestige"
    SPECIAL = "special"


@dataclass
class AchievementReward:
    """Defines a reward for unlocking an achievement"""
    reward_type: str  # "bits", "multiplier", "cosmetic", "unlock"
    value: Any
    description: str


@dataclass
class Achievement:
    """Defines a single achievement"""
    id: str
    name: str
    description: str
    category: AchievementCategory
    icon: str = "🏆"
    
    # Trigger conditions
    trigger_type: str = "manual"  # "bits", "generators", "upgrades", "custom"
    trigger_value: Any = None
    
    # Rewards
    rewards: List[AchievementReward] = field(default_factory=list)
    
    # UI
    hidden: bool = False
    secret_description: str = "???"
    
    # State
    unlocked: bool = False
    progress: float = 0.0  # 0.0 to 1.0
    
    def get_display_description(self) -> str:
        """Get description based on unlock state"""
        if self.unlocked or not self.hidden:
            return self.description
        return self.secret_description
    
    def is_complete(self) -> bool:
        """Check if achievement is complete"""
        return self.progress >= 1.0


class AchievementManager:
    """
    Manages achievements - tracking, unlocking, rewards
    """
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.achievements: Dict[str, Achievement] = {}
        self._triggers: Dict[str, Callable[[], bool]] = {}
        self._progress_calcs: Dict[str, Callable[[], float]] = {}
        self._on_unlock_callbacks: List[Callable[[Achievement], None]] = []
        self._notification_queue: List[Achievement] = []
        
    def register_achievement(self, achievement: Achievement):
        """Register an achievement"""
        self.achievements[achievement.id] = achievement
        
    def register_trigger(self, achievement_id: str, 
                        trigger: Callable[[], bool],
                        progress_calc: Optional[Callable[[], float]] = None):
        """Register a trigger function for an achievement"""
        self._triggers[achievement_id] = trigger
        if progress_calc:
            self._progress_calcs[achievement_id] = progress_calc
            
    def on_unlock(self, callback: Callable[[Achievement], None]):
        """Register callback for achievement unlocks"""
        self._on_unlock_callbacks.append(callback)
        
    def check_achievements(self):
        """Check all achievement triggers"""
        for achievement_id, trigger in self._triggers.items():
            if achievement_id not in self.achievements:
                continue
                
            achievement = self.achievements[achievement_id]
            
            if achievement.unlocked:
                continue
                
            # Check trigger
            if trigger():
                self._unlock_achievement(achievement)
            elif achievement_id in self._progress_calcs:
                # Update progress
                achievement.progress = self._progress_calcs[achievement_id]()
                
    def _unlock_achievement(self, achievement: Achievement):
        """Unlock an achievement and apply rewards"""
        achievement.unlocked = True
        achievement.progress = 1.0
        
        # Apply rewards
        for reward in achievement.rewards:
            self._apply_reward(reward)
            
        # Queue notification
        self._notification_queue.append(achievement)
        
        # Call callbacks
        for callback in self._on_unlock_callbacks:
            callback(achievement)
            
    def _apply_reward(self, reward: AchievementReward):
        """Apply a reward to the game state"""
        if reward.reward_type == "bits":
            self.game_state.bits += reward.value
            self.game_state.total_bits_earned += reward.value
        elif reward.reward_type == "multiplier":
            # Apply as a permanent multiplier
            if not hasattr(self.game_state, 'achievement_multiplier'):
                self.game_state.achievement_multiplier = 1.0
            self.game_state.achievement_multiplier *= reward.value
        elif reward.reward_type == "unlock":
            # Unlock something specific
            if reward.value == "generator" and hasattr(self.game_state, 'unlocked_generators'):
                # Handle generator unlock
                pass
                
    def get_next_notification(self) -> Optional[Achievement]:
        """Get next achievement notification"""
        if self._notification_queue:
            return self._notification_queue.pop(0)
        return None
        
    def get_category_achievements(self, category: AchievementCategory) -> List[Achievement]:
        """Get all achievements in a category"""
        return [a for a in self.achievements.values() if a.category == category]
        
    def get_unlocked_count(self) -> int:
        """Get count of unlocked achievements"""
        return sum(1 for a in self.achievements.values() if a.unlocked)
        
    def get_total_count(self) -> int:
        """Get total achievement count"""
        return len(self.achievements)
        
    def save(self) -> dict:
        """Save achievement state"""
        return {
            "unlocked": [a.id for a in self.achievements.values() if a.unlocked],
            "progress": {a.id: a.progress for a in self.achievements.values()}
        }
        
    def load(self, data: dict):
        """Load achievement state"""
        unlocked = data.get("unlocked", [])
        progress = data.get("progress", {})
        
        for achievement in self.achievements.values():
            if achievement.id in unlocked:
                achievement.unlocked = True
                achievement.progress = 1.0
            elif achievement.id in progress:
                achievement.progress = progress[achievement.id]
    
    def from_toon_config(self, config: dict):
        """Load achievements from TOON config"""
        for ach_data in config.get("achievements", []):
            category = AchievementCategory(ach_data.get("category", "special"))
            
            rewards = []
            for reward_data in ach_data.get("rewards", []):
                rewards.append(AchievementReward(
                    reward_type=reward_data.get("type", "bits"),
                    value=reward_data.get("value", 0),
                    description=reward_data.get("description", "")
                ))
            
            achievement = Achievement(
                id=ach_data["id"],
                name=ach_data["name"],
                description=ach_data["description"],
                category=category,
                icon=ach_data.get("icon", "🏆"),
                trigger_type=ach_data.get("trigger_type", "manual"),
                trigger_value=ach_data.get("trigger_value"),
                rewards=rewards,
                hidden=ach_data.get("hidden", False),
                secret_description=ach_data.get("secret_description", "???")
            )
            
            self.register_achievement(achievement)
            
            # Set up trigger based on type
            self._setup_trigger(achievement)
            
    def _setup_trigger(self, achievement: Achievement):
        """Set up automatic trigger for an achievement"""
        if achievement.trigger_type == "bits":
            threshold = achievement.trigger_value
            self.register_trigger(
                achievement.id,
                lambda t=threshold: self.game_state.total_bits_earned >= t,
                lambda t=threshold: min(1.0, self.game_state.total_bits_earned / t)
            )
        elif achievement.trigger_type == "clicks":
            threshold = achievement.trigger_value
            self.register_trigger(
                achievement.id,
                lambda t=threshold: self.game_state.total_clicks >= t,
                lambda t=threshold: min(1.0, self.game_state.total_clicks / t)
            )
        elif achievement.trigger_type == "generators":
            gen_id = achievement.trigger_value
            self.register_trigger(
                achievement.id,
                lambda g=gen_id: self.game_state.generators.get(g, {}).get("count", 0) > 0,
                lambda g=gen_id: 1.0 if self.game_state.generators.get(g, {}).get("count", 0) > 0 else 0.0
            )
        elif achievement.trigger_type == "rebirths":
            threshold = achievement.trigger_value
            self.register_trigger(
                achievement.id,
                lambda t=threshold: self.game_state.total_rebirths >= t,
                lambda t=threshold: min(1.0, self.game_state.total_rebirths / t)
            )


def create_default_achievements(manager: AchievementManager):
    """Create the default achievement set"""
    
    achievements = [
        # Clicking achievements
        Achievement(
            id="first_click",
            name="Hello World",
            description="Click for the first time",
            category=AchievementCategory.CLICKING,
            icon="👆",
            trigger_type="clicks",
            trigger_value=1,
            rewards=[AchievementReward("bits", 10, "10 bits")]
        ),
        Achievement(
            id="click_100",
            name="Button Masher",
            description="Click 100 times",
            category=AchievementCategory.CLICKING,
            icon="🖱️",
            trigger_type="clicks",
            trigger_value=100,
            rewards=[AchievementReward("multiplier", 1.05, "+5% production")]
        ),
        Achievement(
            id="click_1000",
            name="Repetitive Strain",
            description="Click 1,000 times",
            category=AchievementCategory.CLICKING,
            icon="💪",
            trigger_type="clicks",
            trigger_value=1000,
            rewards=[AchievementReward("multiplier", 1.1, "+10% production")]
        ),
        
        # Generator achievements
        Achievement(
            id="first_generator",
            name="RNG Enthusiast",
            description="Buy your first generator",
            category=AchievementCategory.GENERATORS,
            icon="🎲",
            trigger_type="generators",
            trigger_value="rng",
            rewards=[AchievementReward("bits", 100, "100 bits")]
        ),
        Achievement(
            id="all_basic_generators",
            name="Complete Collection",
            description="Own at least one of each basic generator",
            category=AchievementCategory.GENERATORS,
            icon="📦",
            trigger_type="manual"
        ),
        
        # Progression achievements
        Achievement(
            id="1k_bits",
            name="Kilobit",
            description="Earn 1,000 total bits",
            category=AchievementCategory.PROGRESSION,
            icon="1k",
            trigger_type="bits",
            trigger_value=1000
        ),
        Achievement(
            id="1m_bits",
            name="Megabit",
            description="Earn 1,000,000 total bits",
            category=AchievementCategory.PROGRESSION,
            icon="1M",
            trigger_type="bits",
            trigger_value=1000000,
            rewards=[AchievementReward("multiplier", 1.1, "+10% production")]
        ),
        Achievement(
            id="1b_bits",
            name="Gigabit",
            description="Earn 1,000,000,000 total bits",
            category=AchievementCategory.PROGRESSION,
            icon="1G",
            trigger_type="bits",
            trigger_value=1000000000,
            rewards=[AchievementReward("multiplier", 1.25, "+25% production")]
        ),
        
        # Compression achievements
        Achievement(
            id="first_compression",
            name="Data Compression",
            description="Complete your first rebirth",
            category=AchievementCategory.COMPRESSION,
            icon="🌀",
            trigger_type="rebirths",
            trigger_value=1,
            rewards=[AchievementReward("bits", 10000, "10K bits")]
        ),
        Achievement(
            id="compression_master",
            name="Lossless",
            description="Complete 10 rebirths",
            category=AchievementCategory.COMPRESSION,
            icon="📦",
            trigger_type="rebirths",
            trigger_value=10,
            rewards=[AchievementReward("multiplier", 1.5, "+50% production")]
        ),
        
        # Prestige achievements
        Achievement(
            id="first_prestige",
            name="Quantum Leap",
            description="Perform your first prestige",
            category=AchievementCategory.PRESTIGE,
            icon="🔧",
            trigger_type="manual"
        ),
        
        # Special achievements
        Achievement(
            id="speedrunner",
            name="Speedrun",
            description="Reach 1M bits in under 10 minutes",
            category=AchievementCategory.SPECIAL,
            icon="⚡",
            hidden=True
        ),
    ]
    
    for ach in achievements:
        manager.register_achievement(ach)
        manager._setup_trigger(ach)


class AchievementDisplay:
    """UI for displaying achievements"""
    
    def __init__(self, manager: AchievementManager):
        self.manager = manager
        self.font_title = None
        self.font_body = None
        self.font_icon = None
        self._init_fonts()
        
    def _init_fonts(self):
        try:
            self.font_title = pygame.font.SysFont("Consolas", 18, bold=True)
            self.font_body = pygame.font.SysFont("Consolas", 14)
            self.font_icon = pygame.font.SysFont("Segoe UI Symbol", 24)
        except:
            self.font_title = pygame.font.Font(None, 24)
            self.font_body = pygame.font.Font(None, 18)
            self.font_icon = pygame.font.Font(None, 30)
            
    def draw_notification(self, screen: pygame.Surface, achievement: Achievement,
                         progress: float = 1.0):
        """Draw achievement unlock notification"""
        width, height = screen.get_size()
        
        # Notification box
        notif_width = 400
        notif_height = 80
        notif_x = width // 2 - notif_width // 2
        notif_y = height // 4
        
        # Background
        bg_color = (30, 30, 50)
        border_color = (255, 215, 0) if achievement.unlocked else (100, 100, 120)
        
        pygame.draw.rect(screen, bg_color, (notif_x, notif_y, notif_width, notif_height))
        pygame.draw.rect(screen, border_color, (notif_x, notif_y, notif_width, notif_height), 2)
        
        # Icon
        icon_text = self.font_icon.render(achievement.icon, True, (255, 215, 0))
        screen.blit(icon_text, (notif_x + 15, notif_y + 20))
        
        # Title
        title_text = self.font_title.render(achievement.name, True, (255, 255, 255))
        screen.blit(title_text, (notif_x + 60, notif_y + 15))
        
        # Description
        desc_text = self.font_body.render(achievement.get_display_description(), True, (180, 180, 180))
        screen.blit(desc_text, (notif_x + 60, notif_y + 40))
        
    def draw_panel(self, screen: pygame.Surface, x: int, y: int, 
                   width: int, height: int, category: Optional[AchievementCategory] = None):
        """Draw achievements panel"""
        if category:
            achievements = self.manager.get_category_achievements(category)
        else:
            achievements = list(self.manager.achievements.values())
            
        # Background
        pygame.draw.rect(screen, (20, 20, 30), (x, y, width, height))
        pygame.draw.rect(screen, (60, 60, 80), (x, y, width, height), 2)
        
        # Header
        header_height = 40
        pygame.draw.rect(screen, (30, 30, 45), (x, y, width, header_height))
        
        title = self.font_title.render(
            f"Achievements ({self.manager.get_unlocked_count()}/{self.manager.get_total_count()})",
            True, (255, 215, 0)
        )
        screen.blit(title, (x + 10, y + 10))
        
        # List achievements
        y_offset = y + header_height + 10
        for achievement in achievements[:20]:  # Show max 20
            self._draw_achievement_row(screen, x + 10, y_offset, width - 20, achievement)
            y_offset += 35
            
    def _draw_achievement_row(self, screen: pygame.Surface, x: int, y: int,
                              width: int, achievement: Achievement):
        """Draw a single achievement row"""
        # Background
        bg_color = (35, 35, 45) if achievement.unlocked else (25, 25, 35)
        pygame.draw.rect(screen, bg_color, (x, y, width, 30))
        
        # Icon
        icon_color = (255, 215, 0) if achievement.unlocked else (80, 80, 80)
        icon_text = self.font_icon.render(achievement.icon, True, icon_color)
        screen.blit(icon_text, (x + 5, y + 3))
        
        # Name
        name_color = (255, 255, 255) if achievement.unlocked else (120, 120, 120)
        name_text = self.font_body.render(achievement.name, True, name_color)
        screen.blit(name_text, (x + 35, y + 3))
        
        # Progress bar
        if not achievement.unlocked and achievement.progress > 0:
            bar_width = int((width - 120) * achievement.progress)
            pygame.draw.rect(screen, (50, 50, 60), (x + 35, y + 18, width - 120, 8))
            pygame.draw.rect(screen, (100, 150, 200), (x + 35, y + 18, bar_width, 8))
