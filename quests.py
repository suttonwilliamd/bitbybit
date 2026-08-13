"""
Quest system for Bit by Bit Game
Tutorial and progression quests with rewards
"""

import pygame
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class QuestCategory(Enum):
    """Categories for quests"""
    TUTORIAL = "tutorial"
    MAIN = "main"
    SIDE = "side"
    DAILY = "daily"
    WEEKLY = "weekly"


class QuestState(Enum):
    """Quest completion states"""
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLAIMED = "claimed"


@dataclass
class QuestObjective:
    """A single objective within a quest"""
    id: str
    description: str
    target_type: str  # "bits", "clicks", "generators", "upgrades", "custom"
    target_value: Any
    current_value: Any = 0
    
    def is_complete(self) -> bool:
        """Check if objective is complete"""
        if isinstance(self.target_value, (int, float)):
            return self.current_value >= self.target_value
        return self.current_value == self.target_value
        
    def get_progress(self) -> float:
        """Get progress as 0.0 to 1.0"""
        if isinstance(self.target_value, (int, float)) and self.target_value > 0:
            return min(1.0, self.current_value / self.target_value)
        return 1.0 if self.is_complete() else 0.0


@dataclass
class QuestReward:
    """Reward for completing a quest"""
    reward_type: str  # "bits", "generator", "upgrade", "unlock", "achievement"
    value: Any
    description: str


@dataclass
class Quest:
    """Defines a single quest"""
    id: str
    name: str
    description: str
    category: QuestCategory
    
    objectives: List[QuestObjective] = field(default_factory=list)
    rewards: List[QuestReward] = field(default_factory=list)
    
    # Progression
    prerequisites: List[str] = field(default_factory=list)  # Quest IDs required
    unlocks_quest: Optional[str] = None  # Quest ID this unlocks
    
    # Display
    icon: str = "📋"
    suggested_level: int = 1
    
    # State
    state: QuestState = QuestState.LOCKED
    
    def is_complete(self) -> bool:
        """Check if all objectives are complete"""
        return all(obj.is_complete() for obj in self.objectives)
        
    def get_progress(self) -> float:
        """Get overall quest progress"""
        if not self.objectives:
            return 0.0
        return sum(obj.get_progress() for obj in self.objectives) / len(self.objectives)


class QuestManager:
    """
    Manages quests - tracking, completion, rewards
    """
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.quests: Dict[str, Quest] = {}
        self._objectives_update_handlers: Dict[str, Callable[[], Any]] = {}
        self._on_complete_callbacks: List[Callable[[Quest], None]] = []
        self._on_claim_callbacks: List[Callable[[Quest], None]] = []
        self._notification_queue: List[Quest] = []
        
    def register_quest(self, quest: Quest):
        """Register a quest"""
        self.quests[quest.id] = quest
        self._update_quest_availability(quest.id)
        
    def on_complete(self, callback: Callable[[Quest], None]):
        """Register callback for quest completion"""
        self._on_complete_callbacks.append(callback)
        
    def on_claim(self, callback: Callable[[Quest], None]):
        """Register callback for quest reward claims"""
        self._on_claim_callbacks.append(callback)
        
    def _update_quest_availability(self, quest_id: str):
        """Update availability of a quest based on prerequisites"""
        quest = self.quests.get(quest_id)
        if not quest:
            return
            
        # Check prerequisites
        prereqs_met = all(
            self.quests.get(pid, Quest("", "", "", QuestCategory.MAIN)).state == QuestState.CLAIMED
            for pid in quest.prerequisites
        )
        
        if prereqs_met and quest.state == QuestState.LOCKED:
            quest.state = QuestState.AVAILABLE
            
    def start_quest(self, quest_id: str) -> bool:
        """Start a quest"""
        quest = self.quests.get(quest_id)
        if not quest or quest.state != QuestState.AVAILABLE:
            return False
            
        quest.state = QuestState.IN_PROGRESS
        return True
        
    def check_quest_completion(self):
        """Check all quests for completion"""
        for quest in self.quests.values():
            if quest.state != QuestState.IN_PROGRESS:
                continue
                
            if quest.is_complete():
                quest.state = QuestState.COMPLETED
                self._notification_queue.append(quest)
                
                for callback in self._on_complete_callbacks:
                    callback(quest)
                    
                # Unlock next quest
                if quest.unlocks_quest:
                    next_quest = self.quests.get(quest.unlocks_quest)
                    if next_quest:
                        next_quest.state = QuestState.AVAILABLE
                        
    def claim_reward(self, quest_id: str) -> bool:
        """Claim rewards for a completed quest"""
        quest = self.quests.get(quest_id)
        if not quest or quest.state != QuestState.COMPLETED:
            return False
            
        # Apply rewards
        for reward in quest.rewards:
            self._apply_reward(reward)
            
        quest.state = QuestState.CLAIMED
        
        for callback in self._on_claim_callbacks:
            callback(quest)
            
        return True
        
    def _apply_reward(self, reward: QuestReward):
        """Apply a reward to the game state"""
        if reward.reward_type == "bits":
            self.game_state.bits += reward.value
            self.game_state.total_bits_earned += reward.value
        elif reward.reward_type == "generator":
            if reward.value in self.game_state.generators:
                self.game_state.generators[reward.value]["count"] += 1
            if reward.value not in self.game_state.unlocked_generators:
                self.game_state.unlocked_generators.append(reward.value)
                
    def update_objectives(self):
        """Update all objective progress"""
        for quest in self.quests.values():
            if quest.state != QuestState.IN_PROGRESS:
                continue
                
            for objective in quest.objectives:
                current = self._get_objective_value(objective.target_type, objective.target_value)
                objective.current_value = current
                
    def _get_objective_value(self, target_type: str, target_value: Any) -> Any:
        """Get current value for an objective type"""
        if target_type == "bits":
            return self.game_state.total_bits_earned
        elif target_type == "clicks":
            return self.game_state.total_clicks
        elif target_type == "current_bits":
            return self.game_state.bits
        elif target_type == "generators":
            gen_id = target_value if isinstance(target_value, str) else "rng"
            return self.game_state.generators.get(gen_id, {}).get("count", 0)
        elif target_type == "upgrades":
            upgrade_id = target_value if isinstance(target_value, str) else "click_power"
            return self.game_state.upgrades.get(upgrade_id, {}).get("level", 0)
        elif target_type == "prestige":
            return self.game_state.prestige_count
        elif target_type == "rebirths":
            return self.game_state.total_rebirths
        elif target_type == "era":
            return self.game_state.era
        return 0
        
    def get_next_notification(self) -> Optional[Quest]:
        """Get next quest notification"""
        if self._notification_queue:
            return self._notification_queue.pop(0)
        return None
        
    def get_active_quests(self) -> List[Quest]:
        """Get all in-progress quests"""
        return [q for q in self.quests.values() if q.state == QuestState.IN_PROGRESS]
        
    def get_available_quests(self) -> List[Quest]:
        """Get all available quests"""
        return [q for q in self.quests.values() if q.state == QuestState.AVAILABLE]
        
    def get_completed_quests(self) -> List[Quest]:
        """Get all completed (unclaimed) quests"""
        return [q for q in self.quests.values() if q.state == QuestState.COMPLETED]
        
    def save(self) -> dict:
        """Save quest state"""
        return {
            "quest_states": {q.id: q.state.value for q in self.quests.values()},
            "objective_progress": {
                q.id: {obj.id: obj.current_value for obj in q.objectives}
                for q in self.quests.values()
            }
        }
        
    def load(self, data: dict):
        """Load quest state"""
        quest_states = data.get("quest_states", {})
        objective_progress = data.get("objective_progress", {})
        
        for quest_id, state_str in quest_states.items():
            if quest_id in self.quests:
                self.quests[quest_id].state = QuestState(state_str)
                
        for quest_id, objectives in objective_progress.items():
            if quest_id in self.quests:
                quest = self.quests[quest_id]
                for obj in quest.objectives:
                    if obj.id in objectives:
                        obj.current_value = objectives[obj.id]
                        
        # Ensure first quest is available
        if self.quests:
            first_quest = min(self.quests.values(), key=lambda q: q.suggested_level)
            if first_quest.state == QuestState.LOCKED:
                first_quest.state = QuestState.AVAILABLE
                
    def from_toon_config(self, config: dict):
        """Load quests from TOON config"""
        for quest_data in config.get("quests", []):
            category = QuestCategory(quest_data.get("category", "main"))
            
            objectives = []
            for obj_data in quest_data.get("objectives", []):
                objectives.append(QuestObjective(
                    id=obj_data["id"],
                    description=obj_data["description"],
                    target_type=obj_data["type"],
                    target_value=obj_data["value"]
                ))
                
            rewards = []
            for reward_data in quest_data.get("rewards", []):
                rewards.append(QuestReward(
                    reward_type=reward_data.get("type", "bits"),
                    value=reward_data.get("value", 0),
                    description=reward_data.get("description", "")
                ))
                
            quest = Quest(
                id=quest_data["id"],
                name=quest_data["name"],
                description=quest_data["description"],
                category=category,
                objectives=objectives,
                rewards=rewards,
                prerequisites=quest_data.get("prerequisites", []),
                unlocks_quest=quest_data.get("unlocks"),
                icon=quest_data.get("icon", "📋"),
                suggested_level=quest_data.get("level", 1)
            )
            
            self.register_quest(quest)


def create_tutorial_quests(manager: QuestManager):
    """Create the tutorial quest chain"""
    
    quests = [
        Quest(
            id="tutorial_click",
            name="Generate Bits",
            description="Click the accumulator to generate your first bits",
            category=QuestCategory.TUTORIAL,
            icon="👆",
            suggested_level=1,
            objectives=[
                QuestObjective("click_1", "Click the accumulator", "current_bits", 1)
            ],
            rewards=[
                QuestReward("bits", 10, "10 bits"),
                QuestReward("generator", "rng", "Random Number Generator")
            ],
            unlocks_quest="tutorial_buy_generator"
        ),
        Quest(
            id="tutorial_buy_generator",
            name="Automate It",
            description="Buy your first generator to automate bit production",
            category=QuestCategory.TUTORIAL,
            icon="🎲",
            suggested_level=1,
            objectives=[
                QuestObjective("buy_rng", "Buy a Random Number Generator", "generators", "rng")
            ],
            prerequisites=["tutorial_click"],
            rewards=[
                QuestReward("bits", 50, "50 bits")
            ],
            unlocks_quest="tutorial_reach_100"
        ),
        Quest(
            id="tutorial_reach_100",
            name="Growing Pains",
            description="Reach 100 total bits",
            category=QuestCategory.TUTORIAL,
            icon="💯",
            suggested_level=1,
            objectives=[
                QuestObjective("reach_100", "Earn 100 total bits", "bits", 100)
            ],
            prerequisites=["tutorial_buy_generator"],
            rewards=[
                QuestReward("bits", 100, "100 bits")
            ],
            unlocks_quest="tutorial_first_upgrade"
        ),
        Quest(
            id="tutorial_first_upgrade",
            name="Power Up",
            description="Buy your first upgrade to boost production",
            category=QuestCategory.TUTORIAL,
            icon="⚡",
            suggested_level=1,
            objectives=[
                QuestObjective("buy_upgrade", "Buy an upgrade", "upgrades", "click_power")
            ],
            prerequisites=["tutorial_reach_100"],
            rewards=[
                QuestReward("bits", 200, "200 bits")
            ],
            unlocks_quest="tutorial_1k_bits"
        ),
        Quest(
            id="tutorial_1k_bits",
            name="Kilobit Club",
            description="Earn 1,000 total bits",
            category=QuestCategory.TUTORIAL,
            icon="1k",
            suggested_level=2,
            objectives=[
                QuestObjective("reach_1k", "Earn 1,000 bits", "bits", 1000)
            ],
            prerequisites=["tutorial_first_upgrade"],
            rewards=[
                QuestReward("bits", 500, "500 bits"),
                QuestReward("generator", "biased_coin", "Biased Coin")
            ]
        ),
    ]
    
    for quest in quests:
        manager.register_quest(quest)
        
    # Auto-start first quest
    if "tutorial_click" in manager.quests:
        manager.start_quest("tutorial_click")


class QuestDisplay:
    """UI for displaying quests"""
    
    def __init__(self, manager: QuestManager):
        self.manager = manager
        self.font_title = None
        self.font_body = None
        self.font_small = None
        self._init_fonts()
        
    def _init_fonts(self):
        try:
            self.font_title = pygame.font.SysFont("Consolas", 16, bold=True)
            self.font_body = pygame.font.SysFont("Consolas", 13)
            self.font_small = pygame.font.SysFont("Consolas", 11)
        except:
            self.font_title = pygame.font.Font(None, 20)
            self.font_body = pygame.font.Font(None, 16)
            self.font_small = pygame.font.Font(None, 14)
            
    def draw_notification(self, screen: pygame.Surface, quest: Quest):
        """Draw quest completion notification"""
        width, height = screen.get_size()
        
        notif_width = 400
        notif_height = 100
        notif_x = width // 2 - notif_width // 2
        notif_y = height // 4
        
        # Background
        bg_color = (30, 40, 30)
        border_color = (100, 200, 100)
        
        pygame.draw.rect(screen, bg_color, (notif_x, notif_y, notif_width, notif_height))
        pygame.draw.rect(screen, border_color, (notif_x, notif_y, notif_width, notif_height), 2)
        
        # Icon
        icon_text = self.font_title.render(quest.icon, True, (150, 255, 150))
        screen.blit(icon_text, (notif_x + 15, notif_y + 15))
        
        # Title
        title_text = self.font_title.render(quest.name, True, (200, 255, 200))
        screen.blit(title_text, (notif_x + 50, notif_y + 15))
        
        # Description
        desc_text = self.font_body.render("Quest Complete!", True, (150, 200, 150))
        screen.blit(desc_text, (notif_x + 50, notif_y + 35))
        
        # Rewards
        reward_text = self.font_small.render(
            f"Claim: {', '.join(r.description for r in quest.rewards)}",
            True, (180, 180, 100)
        )
        screen.blit(reward_text, (notif_x + 50, notif_y + 60))
        
    def draw_quest_panel(self, screen: pygame.Surface, x: int, y: int,
                        width: int, height: int):
        """Draw quests panel"""
        # Background
        pygame.draw.rect(screen, (20, 25, 35), (x, y, width, height))
        pygame.draw.rect(screen, (60, 80, 60), (x, y, width, height), 2)
        
        # Header
        header_height = 35
        pygame.draw.rect(screen, (25, 35, 45), (x, y, width, header_height))
        
        title = self.font_title.render("Quests", True, (150, 255, 150))
        screen.blit(title, (x + 10, y + 8))
        
        # Draw quests
        y_offset = y + header_height + 10
        
        # Active quests
        for quest in self.manager.get_active_quests()[:5]:
            self._draw_quest_row(screen, x + 10, y_offset, width - 20, quest)
            y_offset += 50
            
        # Available quests
        for quest in self.manager.get_available_quests()[:3]:
            self._draw_quest_row(screen, x + 10, y_offset, width - 20, quest)
            y_offset += 50
            
        # Completed (claimable)
        for quest in self.manager.get_completed_quests()[:2]:
            self._draw_quest_claim_row(screen, x + 10, y_offset, width - 20, quest)
            y_offset += 50
            
    def _draw_quest_row(self, screen: pygame.Surface, x: int, y: int,
                       width: int, quest: Quest):
        """Draw a quest row"""
        # Background
        bg_color = (30, 35, 45) if quest.state == QuestState.IN_PROGRESS else (25, 28, 35)
        pygame.draw.rect(screen, bg_color, (x, y, width, 45))
        
        # Icon
        icon_color = (150, 255, 150) if quest.state == QuestState.IN_PROGRESS else (100, 100, 100)
        icon_text = self.font_title.render(quest.icon, True, icon_color)
        screen.blit(icon_text, (x + 5, y + 10))
        
        # Name
        name_text = self.font_body.render(quest.name, True, (220, 220, 220))
        screen.blit(name_text, (x + 35, y + 5))
        
        # Progress
        progress = quest.get_progress()
        progress_text = self.font_small.render(f"{int(progress * 100)}%", True, (150, 200, 150))
        screen.blit(progress_text, (x + 35, y + 25))
        
        # Progress bar
        bar_width = int((width - 100) * progress)
        pygame.draw.rect(screen, (40, 45, 55), (x + 65, y + 28, width - 110, 10))
        pygame.draw.rect(screen, (100, 180, 100), (x + 65, y + 28, bar_width, 10))
        
    def _draw_quest_claim_row(self, screen: pygame.Surface, x: int, y: int,
                             width: int, quest: Quest):
        """Draw a claimable quest row"""
        # Background
        bg_color = (40, 35, 30)
        pygame.draw.rect(screen, bg_color, (x, y, width, 45))
        
        # Icon
        icon_text = self.font_title.render(quest.icon, True, (255, 200, 100))
        screen.blit(icon_text, (x + 5, y + 10))
        
        # Name
        name_text = self.font_body.render(quest.name, True, (255, 220, 150))
        screen.blit(name_text, (x + 35, y + 5))
        
        # Claim button text
        claim_text = self.font_small.render("[CLAIM]", True, (255, 215, 0))
        screen.blit(claim_text, (x + 35, y + 25))
