"""
Event-driven input handling for Bit by Bit Game
Separates input processing from game logic
"""

import pygame
from typing import Callable, Dict, List, Optional, Any


class InputEvent:
    """Base class for all input events"""
    def __init__(self, event: pygame.event.Event):
        self.event = event
        self.consumed = False

    def consume(self):
        self.consumed = True


class ClickEvent(InputEvent):
    def __init__(self, event: pygame.event.Event, position: tuple):
        super().__init__(event)
        self.position = position
        self.button = event.button if hasattr(event, 'button') else 1


class MouseMotionEvent(InputEvent):
    def __init__(self, event: pygame.event.Event, position: tuple):
        super().__init__(event)
        self.position = position
        self.rel = event.rel if hasattr(event, 'rel') else (0, 0)


class ScrollEvent(InputEvent):
    def __init__(self, event: pygame.event.Event):
        super().__init__(event)
        self.x = getattr(event, 'x', 0)
        self.y = getattr(event, 'y', 0)


class KeyEvent(InputEvent):
    def __init__(self, event: pygame.event.Event):
        super().__init__(event)
        self.key = event.key
        self.mod = event.mod
        self.unicode = event.unicode


class WindowResizeEvent(InputEvent):
    def __init__(self, event: pygame.event.Event):
        super().__init__(event)
        self.width = event.w
        self.height = event.h


class InputHandler:
    """
    Centralized input handling with event dispatching
    Allows components to register handlers for specific events
    """
    
    def __init__(self):
        self._handlers: Dict[type, List[Callable]] = {}
        self._position_handlers: Dict[type, List[tuple]] = {}  # (handler, rect_check)
        self.mouse_position = (0, 0)
        self.mouse_buttons = {1: False, 2: False, 3: False}
        self.keys = set()
        
    def register_handler(self, event_type: type, handler: Callable[[Any], None]):
        """Register a handler for a specific event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        
    def register_click_handler(self, handler: Callable[[ClickEvent], None], rect: pygame.Rect):
        """Register a handler that fires when click is within rect"""
        if ClickEvent not in self._position_handlers:
            self._position_handlers[ClickEvent] = []
        self._position_handlers[ClickEvent].append((handler, rect))
        
    def unregister_handler(self, event_type: type, handler: Callable):
        """Remove a handler"""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    def handle_event(self, event: pygame.event.Event) -> Optional[InputEvent]:
        """Process a single pygame event and dispatch to handlers"""
        input_event = None
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            input_event = ClickEvent(event, event.pos)
            self.mouse_buttons[event.button] = True
            self._dispatch_position_handlers(input_event)
            
        elif event.type == pygame.MOUSEBUTTONUP:
            input_event = ClickEvent(event, event.pos)
            self.mouse_buttons[event.button] = False
            
        elif event.type == pygame.MOUSEMOTION:
            input_event = MouseMotionEvent(event, event.pos)
            self.mouse_position = event.pos
            
        elif event.type == pygame.MOUSEWHEEL:
            input_event = ScrollEvent(event)
            
        elif event.type == pygame.KEYDOWN:
            input_event = KeyEvent(event)
            self.keys.add(event.key)
            
        elif event.type == pygame.KEYUP:
            input_event = KeyEvent(event)
            self.keys.discard(event.key)
            
        elif event.type == pygame.VIDEORESIZE:
            input_event = WindowResizeEvent(event)
            
        elif event.type == pygame.QUIT:
            return None  # Handled specially
            
        # Dispatch to type-specific handlers
        if input_event:
            self._dispatch_handlers(input_event)
            
        return input_event
    
    def _dispatch_handlers(self, input_event: InputEvent):
        """Dispatch event to registered handlers"""
        event_type = type(input_event)
        
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                if input_event.consumed:
                    break
                handler(input_event)
                
    def _dispatch_position_handlers(self, input_event: ClickEvent):
        """Dispatch click events to rect-based handlers"""
        if ClickEvent in self._position_handlers:
            for handler, rect in self._position_handlers[ClickEvent]:
                if input_event.consumed:
                    break
                if rect.collidepoint(input_event.position):
                    handler(input_event)
                    
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed"""
        return key in self.keys
    
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a mouse button is currently pressed"""
        return self.mouse_buttons.get(button, False)
    
    def get_mouse_position(self) -> tuple:
        """Get current mouse position"""
        return self.mouse_position


class UIComponent:
    """Base class for UI components that can handle input"""
    
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.enabled = True
        self.visible = True
        self._handlers = {}
        
    def on(self, event_type: type, handler: Callable):
        """Register an event handler for this component"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        
    def handle_event(self, event: InputEvent) -> bool:
        """Handle an input event. Returns True if handled."""
        if not self.enabled or not self.visible:
            return False
            
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                if handler(event):
                    return True
        return False
    
    def update(self, dt: float):
        """Update component state"""
        pass
    
    def draw(self, screen: pygame.Surface):
        """Draw component"""
        pass
