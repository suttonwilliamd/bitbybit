"""
UI Panel classes for Bit by Bit Game
"""

import pygame


class ScrollablePanel:
    """A scrollable panel container for overflow content"""

    def __init__(self, x, y, width, height, title=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.scroll_offset = 0
        self.content_height = 0
        self.dragging = False
        self.drag_offset = 0
        self.hovering_scrollbar = False

    def get_scrollbar_geometry(self):
        """Returns scrollbar geometry: (track_rect, thumb_rect)"""
        if self.content_height <= self.rect.height - 60:
            return None, None

        scrollbar_x = self.rect.right - 16
        scrollbar_y = self.rect.y + 52
        scrollbar_height = self.rect.height - 60
        scrollbar_width = 12

        track_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)

        thumb_height = max(
            30, int((scrollbar_height * scrollbar_height) / self.content_height)
        )
        scroll_range = max(1, self.content_height - scrollbar_height)
        
        # Calculate thumb position based on scroll offset
        max_offset = max(0, self.content_height - scrollbar_height)
        if max_offset > 0:
            thumb_ratio = self.scroll_offset / max_offset
        else:
            thumb_ratio = 0
        
        thumb_y = scrollbar_y + int(thumb_ratio * (scrollbar_height - thumb_height))
        thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)

        return track_rect, thumb_rect

    def update_hover(self, mouse_pos):
        """Update hover state for scrollbar"""
        track_rect, thumb_rect = self.get_scrollbar_geometry()
        if track_rect:
            # Check if mouse is near the scrollbar area (with generous hit area)
            hit_area = track_rect.inflate(20, 0)
            self.hovering_scrollbar = hit_area.collidepoint(mouse_pos)
        else:
            self.hovering_scrollbar = False

    def handle_scrollbar_click(self, pos):
        """Handle clicking on scrollbar. Returns True if clicked on thumb."""
        track_rect, thumb_rect = self.get_scrollbar_geometry()
        if track_rect is None:
            return False

        # Use a larger hit area for easier clicking
        thumb_hit_area = thumb_rect.inflate(8, 10)
        track_hit_area = track_rect.inflate(8, 0)

        if thumb_hit_area.collidepoint(pos):
            self.dragging = True
            mouse_y = pos[1]
            thumb_center = thumb_rect.centery
            self.drag_offset = mouse_y - thumb_center
            return True
        elif track_hit_area.collidepoint(pos):
            if pos[1] < thumb_rect.top:
                self.scroll_by(-self.rect.height + 60)
            elif pos[1] > thumb_rect.bottom:
                self.scroll_by(self.rect.height - 60)
            else:
                # Clicked on track but not on thumb - jump to position
                relative_y = (pos[1] - track_rect.y) / track_rect.height
                max_offset = max(0, self.content_height - (self.rect.height - 60))
                new_offset = int(relative_y * max_offset)
                self.scroll_to(new_offset)
            return True
        return False

    def handle_scrollbar_drag(self, pos):
        """Handle dragging the scrollbar thumb."""
        if not self.dragging:
            return

        track_rect, thumb_rect = self.get_scrollbar_geometry()
        if track_rect is None:
            return

        scrollbar_height = track_rect.height
        thumb_height = thumb_rect.height
        scroll_range = max(1, self.content_height - scrollbar_height)

        # Calculate new position based on mouse Y
        target_y = pos[1] - self.drag_offset
        thumb_range = scrollbar_height - thumb_height
        
        if thumb_range > 0:
            relative_pos = (target_y - track_rect.y) / thumb_range
            relative_pos = max(0, min(1, relative_pos))  # Clamp to 0-1
            max_offset = max(0, self.content_height - scrollbar_height)
            new_scroll_offset = int(relative_pos * max_offset)
            self.scroll_to(new_scroll_offset)

    def stop_drag(self):
        """Stop any ongoing drag."""
        self.dragging = False

    def handle_scroll(self, event):
        """Handle mouse wheel scrolling"""
        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(
            pygame.mouse.get_pos()
        ):
            self.scroll_offset = max(
                0,
                min(
                    self.scroll_offset - event.y * 30,
                    max(
                        0, self.content_height - self.rect.height + 60
                    ),
                ),
            )

    def scroll_by(self, amount):
        """Scroll by a relative amount"""
        self.scroll_offset = max(
            0,
            min(
                self.scroll_offset + amount,
                max(0, self.content_height - self.rect.height + 60),
            ),
        )

    def scroll_to(self, position):
        """Scroll to an absolute position"""
        self.scroll_offset = max(0, min(position, max(0, self.content_height - self.rect.height + 60)))

    def scroll_to_bottom(self):
        """Scroll to the bottom of the content"""
        self.scroll_offset = max(0, self.content_height - self.rect.height + 60)

    def get_scroll_offset(self):
        """Get current scroll position"""
        return self.scroll_offset

    def set_content_height(self, height):
        """Set the total height of scrollable content"""
        self.content_height = height
