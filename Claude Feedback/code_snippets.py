"""
CODE SNIPPETS FOR IMPROVED UI
Copy these into your gui.py file, replacing the existing methods
"""

# ============================================================================
# 1. ADD THIS NEW CLASS (before BitByBitGame class)
# ============================================================================

class ScrollablePanel:
    """A scrollable panel container for overflow content"""
    
    def __init__(self, x, y, width, height, title=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.scroll_offset = 0
        self.content_height = 0
        
    def handle_scroll(self, event):
        """Handle mouse wheel scrolling"""
        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.scroll_offset = max(0, min(
                self.scroll_offset - event.y * 30,
                max(0, self.content_height - self.rect.height + 60)  # 60 for title area
            ))
            
    def get_scroll_offset(self):
        """Get current scroll position"""
        return self.scroll_offset
        
    def set_content_height(self, height):
        """Set the total height of scrollable content"""
        self.content_height = height


# ============================================================================
# 2. ADD THESE TO __init__ METHOD (in BitByBitGame class)
# ============================================================================

# Add after existing panel state variables:
self.generators_scroll_panel = ScrollablePanel(50, 520, 600, 300, "INFORMATION SOURCES")
self.upgrades_scroll_panel = ScrollablePanel(700, 520, 450, 300, "UPGRADES")

# UPDATE toggle button initialization (replace existing):
self.generators_toggle = Button(
    50, 510, 600, 40, "▶ INFORMATION SOURCES", (35, 40, 55)
)
self.upgrades_toggle = Button(
    700, 510, 450, 40, "▶ UPGRADES", (35, 40, 55)
)


# ============================================================================
# 3. ADD TO handle_events METHOD
# ============================================================================

# Add this inside your event loop (in handle_events method):
if event.type == pygame.MOUSEWHEEL:
    self.generators_scroll_panel.handle_scroll(event)
    self.upgrades_scroll_panel.handle_scroll(event)


# ============================================================================
# 4. UPDATE handle_window_resize METHOD
# ============================================================================

# Add after updating toggle button positions:
self.generators_scroll_panel.rect.x = int(50 * scale_x)
self.generators_scroll_panel.rect.y = panel_y + 45
self.generators_scroll_panel.rect.width = int(600 * scale_x)
self.generators_scroll_panel.rect.height = min(int(300 * scale_y), new_height - panel_y - 150)

self.upgrades_scroll_panel.rect.x = int(700 * scale_x)
self.upgrades_scroll_panel.rect.y = panel_y + 45
self.upgrades_scroll_panel.rect.width = int(450 * scale_x)
self.upgrades_scroll_panel.rect.height = min(int(300 * scale_y), new_height - panel_y - 150)


# ============================================================================
# 5. NEW HELPER METHODS - ADD THESE TO BitByBitGame CLASS
# ============================================================================

def draw_panel_toggle(self, button, is_open):
    """Draw panel toggle button with better affordances"""
    # Better visual state for toggle
    if is_open:
        bg_color = (45, 50, 65)
        border_color = COLORS["electric_cyan"]
        text_color = COLORS["electric_cyan"]
    else:
        bg_color = (32, 36, 48)
        border_color = COLORS["muted_blue"]
        text_color = COLORS["muted_blue"]
    
    # Background
    pygame.draw.rect(self.screen, bg_color, button.rect, border_radius=6)
    
    # Border with glow effect if open
    if is_open:
        # Glow
        glow_rect = button.rect.inflate(4, 4)
        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*COLORS["electric_cyan"], 40), 
                        (0, 0, glow_rect.width, glow_rect.height), border_radius=8)
        self.screen.blit(glow_surf, glow_rect)
    
    pygame.draw.rect(self.screen, border_color, button.rect, 2, border_radius=6)
    
    # Text
    text_surface = self.small_font.render(button.text, True, text_color)
    text_rect = text_surface.get_rect(center=button.rect.center)
    self.screen.blit(text_surface, text_rect)


def draw_panel_background(self, panel):
    """Draw panel background with better design"""
    # Main background
    pygame.draw.rect(self.screen, (22, 25, 35), panel.rect, border_radius=10)
    
    # Border
    pygame.draw.rect(self.screen, COLORS["muted_blue"], panel.rect, 2, border_radius=10)
    
    # Title bar
    title_rect = pygame.Rect(panel.rect.x, panel.rect.y, panel.rect.width, 45)
    pygame.draw.rect(self.screen, (28, 32, 45), title_rect, 
                    border_top_left_radius=10, border_top_right_radius=10)
    
    # Title text
    title_text = self.medium_font.render(panel.title, True, COLORS["electric_cyan"])
    title_text_rect = title_text.get_rect(center=(panel.rect.centerx, panel.rect.y + 22))
    self.screen.blit(title_text, title_text_rect)


def draw_scrollbar(self, panel):
    """Draw scrollbar for panel"""
    if panel.content_height <= panel.rect.height - 60:
        return
        
    scrollbar_x = panel.rect.right - 12
    scrollbar_y = panel.rect.y + 50
    scrollbar_height = panel.rect.height - 60
    
    # Track
    track_rect = pygame.Rect(scrollbar_x, scrollbar_y, 8, scrollbar_height)
    pygame.draw.rect(self.screen, (40, 45, 55), track_rect, border_radius=4)
    
    # Thumb
    thumb_height = max(30, (scrollbar_height * scrollbar_height) // panel.content_height)
    scroll_range = max(1, panel.content_height - scrollbar_height)
    thumb_y = scrollbar_y + (panel.scroll_offset * (scrollbar_height - thumb_height)) // scroll_range
    thumb_rect = pygame.Rect(scrollbar_x, thumb_y, 8, thumb_height)
    pygame.draw.rect(self.screen, COLORS["electric_cyan"], thumb_rect, border_radius=4)


# ============================================================================
# 6. REPLACE draw_generators_panel METHOD
# ============================================================================

def draw_generators_panel(self):
    """Draw generators panel with better design and scrolling"""
    # Update toggle button text based on state
    if self.generators_panel_open:
        self.generators_toggle.text = "▼ INFORMATION SOURCES"
    else:
        self.generators_toggle.text = "▶ INFORMATION SOURCES"
    
    # Draw toggle button with better styling
    self.draw_panel_toggle(self.generators_toggle, self.generators_panel_open)

    if not self.generators_panel_open:
        return

    # Draw scrollable panel background
    panel = self.generators_scroll_panel
    self.draw_panel_background(panel)

    # Create a subsurface for scrollable content
    scroll_surface = pygame.Surface((panel.rect.width - 20, panel.rect.height - 60))
    scroll_surface.fill((18, 20, 28))
    
    # Draw generators on scroll surface
    y_offset = -panel.get_scroll_offset()
    
    basic_generators = GENERATORS if GENERATORS else CONFIG["GENERATORS"]
    hardware_generators = CONFIG.get("HARDWARE_GENERATORS", {})
    all_generators = {**basic_generators, **hardware_generators}

    for gen_id, generator in all_generators.items():
        # Check if unlocked
        if gen_id in basic_generators:
            if not self.state.is_generator_unlocked(gen_id):
                continue
        elif gen_id in hardware_generators:
            if not self.state.is_hardware_category_unlocked(generator["category"]):
                continue

        count = self.state.generators[gen_id]["count"]
        cost = self.state.get_generator_cost(gen_id)
        production = self.state.get_generator_production(gen_id)
        can_afford = self.state.can_afford(cost)

        # Card dimensions
        card_height = 90
        card_y = y_offset + 10
        
        # Only draw if visible (optimization)
        if card_y + card_height > -20 and card_y < scroll_surface.get_height():
            self.draw_generator_card(
                scroll_surface, 10, card_y, 
                panel.rect.width - 40, card_height,
                generator, gen_id, count, cost, production, can_afford
            )
        
        y_offset += card_height + 12

    # Update content height for scrolling
    panel.set_content_height(y_offset + panel.get_scroll_offset() + 20)

    # Blit scroll surface to screen
    self.screen.blit(scroll_surface, (panel.rect.x + 10, panel.rect.y + 50))
    
    # Draw scrollbar if needed
    if panel.content_height > panel.rect.height - 60:
        self.draw_scrollbar(panel)


# ============================================================================
# 7. ADD draw_generator_card METHOD
# ============================================================================

def draw_generator_card(self, surface, x, y, width, height, 
                       generator, gen_id, count, cost, production, can_afford):
    """Draw individual generator card with better design"""
    card_rect = pygame.Rect(x, y, width, height)
    
    # Subtle color scheme - NO green/red backgrounds
    if can_afford:
        bg_color = (28, 32, 42)
        border_color = COLORS["electric_cyan"]
        border_alpha = 180
    else:
        bg_color = (25, 25, 30)
        border_color = COLORS["muted_blue"]
        border_alpha = 100
        
    # Draw card background with rounded corners
    pygame.draw.rect(surface, bg_color, card_rect, border_radius=8)
    
    # Draw border with transparency effect
    border_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(border_surf, (*border_color, border_alpha), 
                    (0, 0, width, height), 2, border_radius=8)
    surface.blit(border_surf, (x, y))
    
    # Icon (larger, better positioned)
    icon_size = 48
    icon_x = x + 15
    icon_y = y + height // 2 - icon_size // 2
    icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
    
    icon_text = generator.get("icon", "🎲")
    icon_font = pygame.font.Font(None, 42)
    icon_surface = icon_font.render(icon_text, True, COLORS["electric_cyan"])
    icon_text_rect = icon_surface.get_rect(center=icon_rect.center)
    surface.blit(icon_surface, icon_text_rect)
    
    # Name and count (better typography)
    name_x = x + 75
    name_y = y + 15
    name_text = self.medium_font.render(generator["name"], True, COLORS["soft_white"])
    surface.blit(name_text, (name_x, name_y))
    
    # Count
    info_y = y + 42
    count_text = self.small_font.render(
        f"Qty: {count}",
        True, COLORS["muted_blue"]
    )
    surface.blit(count_text, (name_x, info_y))
    
    # Production rate (if any)
    if production > 0:
        prod_text = self.small_font.render(
            f"Rate: +{self.format_number(production)} b/s",
            True, COLORS["matrix_green"]
        )
        surface.blit(prod_text, (name_x + 90, info_y))
    
    # Buy buttons (better positioned)
    button_x = x + width - 160
    button_y = y + height // 2 - 14
    
    self.generator_buy_buttons[gen_id]["x1"].rect.x = button_x
    self.generator_buy_buttons[gen_id]["x1"].rect.y = button_y
    self.generator_buy_buttons[gen_id]["x10"].rect.x = button_x + 80
    self.generator_buy_buttons[gen_id]["x10"].rect.y = button_y
    
    self.generator_buy_buttons[gen_id]["x1"].is_enabled = can_afford
    self.generator_buy_buttons[gen_id]["x10"].is_enabled = can_afford
    
    # Draw buttons on the main surface (not scroll surface)
    # Note: You'll need to offset these properly when drawing
    
    # Cost text
    cost_text = self.tiny_font.render(
        f"{self.format_number(cost)} bits",
        True, COLORS["gold"] if can_afford else COLORS["muted_blue"]
    )
    cost_rect = cost_text.get_rect(center=(button_x - 50, button_y + 14))
    surface.blit(cost_text, cost_rect)


# ============================================================================
# 8. REPLACE draw_upgrades_panel METHOD (similar to generators)
# ============================================================================

def draw_upgrades_panel(self):
    """Draw upgrades panel with better design and scrolling"""
    # Update toggle button text
    if self.upgrades_panel_open:
        self.upgrades_toggle.text = "▼ UPGRADES"
    else:
        self.upgrades_toggle.text = "▶ UPGRADES"
    
    # Draw toggle button
    self.draw_panel_toggle(self.upgrades_toggle, self.upgrades_panel_open)

    if not self.upgrades_panel_open:
        return

    # Draw scrollable panel
    panel = self.upgrades_scroll_panel
    self.draw_panel_background(panel)

    # Create scroll surface
    scroll_surface = pygame.Surface((panel.rect.width - 20, panel.rect.height - 60))
    scroll_surface.fill((18, 20, 28))
    
    y_offset = -panel.get_scroll_offset()
    
    basic_upgrades = UPGRADES if UPGRADES else CONFIG["UPGRADES"]
    hardware_upgrades = CONFIG.get("HARDWARE_UPGRADES", {})
    all_upgrades = {**basic_upgrades, **hardware_upgrades}

    for upgrade_id, upgrade in all_upgrades.items():
        # Check if unlocked
        if upgrade_id in basic_upgrades:
            if not self.state.is_upgrade_unlocked(upgrade_id):
                continue
        elif upgrade_id in hardware_upgrades:
            if not self.state.is_hardware_category_unlocked(upgrade["category"]):
                continue

        level = self.state.upgrades[upgrade_id]["level"]
        cost = self.state.get_upgrade_cost(upgrade_id)
        can_afford = self.state.can_afford(cost) and level < upgrade["max_level"]

        # Card
        card_height = 85
        card_y = y_offset + 10
        
        if card_y + card_height > -20 and card_y < scroll_surface.get_height():
            self.draw_upgrade_card(
                scroll_surface, 10, card_y,
                panel.rect.width - 40, card_height,
                upgrade, upgrade_id, level, cost, can_afford
            )
        
        y_offset += card_height + 12

    panel.set_content_height(y_offset + panel.get_scroll_offset() + 20)
    
    # Blit to screen
    self.screen.blit(scroll_surface, (panel.rect.x + 10, panel.rect.y + 50))
    
    # Scrollbar if needed
    if panel.content_height > panel.rect.height - 60:
        self.draw_scrollbar(panel)


# ============================================================================
# 9. ADD draw_upgrade_card METHOD
# ============================================================================

def draw_upgrade_card(self, surface, x, y, width, height, 
                     upgrade, upgrade_id, level, cost, can_afford):
    """Draw individual upgrade card"""
    card_rect = pygame.Rect(x, y, width, height)
    
    # Purple theme for upgrades
    max_level = upgrade["max_level"]
    is_maxed = level >= max_level
    
    if is_maxed:
        bg_color = (35, 30, 45)
        border_color = COLORS["gold"]
        border_alpha = 200
    elif can_afford:
        bg_color = (30, 28, 40)
        border_color = COLORS["neon_purple"]
        border_alpha = 180
    else:
        bg_color = (25, 25, 30)
        border_color = COLORS["muted_blue"]
        border_alpha = 100
        
    # Background
    pygame.draw.rect(surface, bg_color, card_rect, border_radius=8)
    
    # Border
    border_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(border_surf, (*border_color, border_alpha), 
                    (0, 0, width, height), 2, border_radius=8)
    surface.blit(border_surf, (x, y))
    
    # Icon
    icon_x = x + 15
    icon_y = y + height // 2 - 20
    icon_text = upgrade.get("icon", "⚡")
    icon_font = pygame.font.Font(None, 38)
    icon_surface = icon_font.render(icon_text, True, COLORS["neon_purple"])
    surface.blit(icon_surface, (icon_x, icon_y))
    
    # Name
    name_x = x + 55
    name_y = y + 12
    name_text = self.medium_font.render(upgrade["name"], True, COLORS["soft_white"])
    surface.blit(name_text, (name_x, name_y))
    
    # Level progress
    level_y = y + 38
    level_text = self.small_font.render(
        f"Level {level}/{max_level}",
        True, COLORS["gold"] if is_maxed else COLORS["muted_blue"]
    )
    surface.blit(level_text, (name_x, level_y))
    
    # Description
    desc_y = y + 58
    desc = upgrade.get("description", "")
    desc_text = self.tiny_font.render(desc[:40], True, COLORS["muted_blue"])
    surface.blit(desc_text, (name_x, desc_y))
    
    # Buy button or MAX indicator
    button_x = x + width - 90
    button_y = y + height // 2 - 14
    
    if is_maxed:
        max_text = self.small_font.render("MAXED", True, COLORS["gold"])
        max_rect = max_text.get_rect(center=(button_x + 40, button_y + 14))
        surface.blit(max_text, max_rect)
    else:
        self.upgrade_buttons[upgrade_id].rect.x = button_x
        self.upgrade_buttons[upgrade_id].rect.y = button_y
        self.upgrade_buttons[upgrade_id].is_enabled = can_afford
        
        # Cost
        cost_text = self.tiny_font.render(
            f"{self.format_number(cost)}",
            True, COLORS["gold"] if can_afford else COLORS["muted_blue"]
        )
        cost_rect = cost_text.get_rect(center=(button_x - 40, button_y + 14))
        surface.blit(cost_text, cost_rect)


# ============================================================================
# NOTES:
# ============================================================================
# 
# 1. Make sure you have the COLORS defined in your constants.py
# 2. The buttons are drawn on scroll surfaces, so you'll need to handle
#    click events properly (accounting for scroll offset)
# 3. Test thoroughly at different window sizes
# 4. You may need to adjust button drawing - consider drawing them after
#    the scroll surface is blitted, with proper position offsetting
#
# ============================================================================
