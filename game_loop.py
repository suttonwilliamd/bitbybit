"""
Game loop management for Bit by Bit Game
Separates update logic from rendering
"""

import pygame
import time
from typing import Callable, Optional, List
from dataclasses import dataclass


@dataclass
class GameMetrics:
    """Performance metrics for the game"""
    fps: float = 60.0
    frame_time: float = 0.016
    update_time: float = 0.0
    draw_time: float = 0.0
    particles_count: int = 0


class GameLoop:
    """
    Manages the main game loop with update/draw separation
    Handles timing, FPS limiting, and game state transitions
    """
    
    def __init__(self, target_fps: int = 60):
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.running = False
        self.paused = False
        self.dt = 0.0
        
        self._update_callbacks: List[Callable[[float], None]] = []
        self._draw_callbacks: List[Callable[[pygame.Surface], None]] = []
        self._event_callbacks: List[Callable[[pygame.event.Event], None]] = []
        
        self.metrics = GameMetrics()
        self._last_time = time.perf_counter()
        self._accumulator = 0.0
        self._fixed_timestep = 1.0 / 60.0  # Fixed update at 60fps
        
        self._show_fps = False
        
    def register_update(self, callback: Callable[[float], None]):
        """Register a function to be called every update frame"""
        self._update_callbacks.append(callback)
        
    def register_draw(self, callback: Callable[[pygame.Surface], None]):
        """Register a function to be called every draw frame"""
        self._draw_callbacks.append(callback)
        
    def register_event(self, callback: Callable[[pygame.event.Event], None]):
        """Register a function to handle pygame events"""
        self._event_callbacks.append(callback)
        
    def unregister_update(self, callback: Callable[[float], None]):
        """Remove an update callback"""
        try:
            self._update_callbacks.remove(callback)
        except ValueError:
            pass
            
    def unregister_draw(self, callback: Callable[[pygame.Surface], None]):
        """Remove a draw callback"""
        try:
            self._draw_callbacks.remove(callback)
        except ValueError:
            pass
    
    def run(self, screen: pygame.Surface, clock: pygame.time.Clock):
        """Main game loop"""
        self.running = True
        
        while self.running:
            start_time = time.perf_counter()
            
            # Calculate delta time
            current_time = time.perf_counter()
            self.dt = current_time - self._last_time
            self._last_time = current_time
            
            # Cap dt to prevent spiral of death
            self.dt = min(self.dt, 0.25)
            
            # Handle events
            self._handle_events()
            
            if not self.paused:
                # Fixed timestep update for physics/game logic
                self._accumulator += self.dt
                while self._accumulator >= self._fixed_timestep:
                    self._fixed_update(self._fixed_timestep)
                    self._accumulator -= self._fixed_timestep
                    
                # Variable timestep update
                self._update(self.dt)
            
            # Draw
            self._draw(screen)
            
            # Update FPS counter
            self.metrics.frame_time = time.perf_counter() - start_time
            self.metrics.fps = 1.0 / self.metrics.frame_time if self.metrics.frame_time > 0 else 0
            
            # Tick clock
            clock.tick(self.target_fps)
            
        return self.running
    
    def _handle_events(self):
        """Process pygame events"""
        for event in pygame.event.get():
            # Handle quit
            if event.type == pygame.QUIT:
                self.running = False
                
            # Dispatch to registered callbacks
            for callback in self._event_callbacks:
                callback(event)
    
    def _fixed_update(self, dt: float):
        """Fixed timestep updates (physics, game logic)"""
        for callback in self._update_callbacks:
            callback(dt)
    
    def _update(self, dt: float):
        """Variable timestep updates (animation, effects)"""
        # This is called at variable framerate for visual stuff
        pass
    
    def _draw(self, screen: pygame.Surface):
        """Render the game"""
        for callback in self._draw_callbacks:
            callback(screen)
            
        if self._show_fps:
            self._draw_fps(screen)
    
    def _draw_fps(self, screen: pygame.Surface):
        """Draw FPS counter"""
        font = pygame.font.Font(None, 24)
        fps_text = font.render(f"FPS: {self.metrics.fps:.1f}", True, (255, 255, 255))
        screen.blit(fps_text, (10, 10))
    
    def pause(self):
        """Pause the game"""
        self.paused = True
        
    def resume(self):
        """Resume the game"""
        self.paused = False
        self._last_time = time.perf_counter()
        
    def stop(self):
        """Stop the game loop"""
        self.running = False
        
    def toggle_fps(self):
        """Toggle FPS display"""
        self._show_fps = not self._show_fps


class GameState:
    """Enum for game states"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    SETTINGS = "settings"
    REBIRTH = "rebirth"
    PRESTIGE = "prestige"
    TUTORIAL = "tutorial"


class StateManager:
    """
    Manages game state transitions
    Allows for clean state machine behavior
    """
    
    def __init__(self):
        self.current_state = GameState.PLAYING
        self.previous_state = None
        self._state_enter_handlers = {}
        self._state_exit_handlers = {}
        
    def register_state(self, state: str, 
                       on_enter: Optional[Callable] = None,
                       on_exit: Optional[Callable] = None):
        """Register handlers for state transitions"""
        if on_enter:
            self._state_enter_handlers[state] = on_enter
        if on_exit:
            self._state_exit_handlers[state] = on_exit
            
    def change_state(self, new_state: str):
        """Change to a new state"""
        if new_state == self.current_state:
            return
            
        # Call exit handler
        if self.current_state in self._state_exit_handlers:
            self._state_exit_handlers[self.current_state]()
            
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # Call enter handler
        if new_state in self._state_enter_handlers:
            self._state_enter_handlers[new_state]()
            
    def is_state(self, state: str) -> bool:
        """Check if in a specific state"""
        return self.current_state == state
    
    def can_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a state transition is valid"""
        valid_transitions = {
            GameState.PLAYING: [GameState.PAUSED, GameState.SETTINGS, 
                               GameState.REBIRTH, GameState.PRESTIGE, GameState.TUTORIAL],
            GameState.PAUSED: [GameState.PLAYING],
            GameState.SETTINGS: [GameState.PLAYING],
            GameState.REBIRTH: [GameState.PLAYING],
            GameState.PRESTIGE: [GameState.PLAYING],
            GameState.TUTORIAL: [GameState.PLAYING],
        }
        return to_state in valid_transitions.get(from_state, [])
