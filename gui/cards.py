"""
Card drawing functions for generators and upgrades
"""

import pygame
from constants import COLORS, format_number

UI_ARROW_DOWN = "▼"
UI_ARROW_RIGHT = "▶"

try:
    test_font = pygame.font.SysFont("Segoe UI Symbol", 12)
    if not test_font.render(UI_ARROW_DOWN, True, (255, 255, 255)).get_width() > 0:
        raise Exception("Font doesn't render Unicode")
except:
    UI_ARROW_DOWN = "v"
    UI_ARROW_RIGHT = ">"


def draw_panel_toggle(screen, button, is_open, small_font):
    """Draw panel toggle button with clear visual affordances"""
    if is_open:
        bg_color = (60, 70, 95)
        border_color = COLORS["electric_cyan"]
        text_color = COLORS["soft_white"]
    else:
        bg_color = (35, 40, 55)
        border_color = (80, 90, 120)
        text_color = (160, 170, 200)

    pygame.draw.rect(screen, bg_color, button.rect, border_radius=10)
    
    # Draw subtle gradient overlay for depth
    gradient_rect = button.rect.inflate(-4, -4)
    overlay_color = (*bg_color, 40)
    pygame.draw.rect(screen, (*bg_color, 30), gradient_rect, 1, border_radius=8)

    glow_intensity = 60 if is_open else 20
    if is_open:
        for i in range(3):
            glow_rect = button.rect.inflate(6 + i * 3, 6 + i * 3)
            glow_alpha = glow_intensity - i * 15
            glow_surf = pygame.Surface(
                (glow_rect.width, glow_rect.height), pygame.SRCALPHA
            )
            pygame.draw.rect(
                glow_surf,
                (*border_color, glow_alpha),
                (0, 0, glow_rect.width, glow_rect.height),
                border_radius=10 + i * 2,
            )
            screen.blit(glow_surf, glow_rect.topleft)

    pygame.draw.rect(screen, border_color, button.rect, 2, border_radius=10)

    # Draw arrow indicator
    arrow_x = button.rect.x + 15
    arrow_y = button.rect.centery
    arrow_size = 5
    
    if is_open:
        # Down arrow
        pygame.draw.polygon(
            screen, text_color,
            [(arrow_x, arrow_y - arrow_size),
             (arrow_x + arrow_size * 1.5, arrow_y + arrow_size),
             (arrow_x - arrow_size * 1.5, arrow_y + arrow_size)]
        )
    else:
        # Right arrow
        pygame.draw.polygon(
            screen, text_color,
            [(arrow_x - arrow_size, arrow_y - arrow_size * 1.5),
             (arrow_x + arrow_size, arrow_y),
             (arrow_x - arrow_size, arrow_y + arrow_size * 1.5)]
        )

    # Draw panel title text
    # Extract the arrow indicator and title
    title_text = button.text
    if title_text.startswith(UI_ARROW_DOWN) or title_text.startswith(UI_ARROW_RIGHT):
        title_text = title_text[1:].strip()
    text_surface = small_font.render(title_text, True, text_color)
    text_rect = text_surface.get_rect(
        center=(button.rect.centerx + 5, button.rect.centery)
    )
    screen.blit(text_surface, text_rect)


def draw_panel_with_integrated_title(screen, panel, title_color=None, medium_font=None, tiny_font=None):
    """Draw a panel with integrated title bar"""
    if title_color is None:
        title_color = COLORS["electric_cyan"]

    pygame.draw.rect(screen, (18, 22, 32), panel.rect, border_radius=12)

    pygame.draw.rect(
        screen, (*title_color, 80), panel.rect, 2, border_radius=12
    )

    inner_rect = panel.rect.inflate(-3, -3)
    pygame.draw.rect(
        screen, (40, 45, 60), inner_rect, 1, border_radius=10
    )

    title_bar_height = 48
    title_rect = pygame.Rect(
        panel.rect.x, panel.rect.y, panel.rect.width, title_bar_height
    )
    
    pygame.draw.rect(
        screen,
        (30, 35, 50),
        title_rect,
        border_top_left_radius=12,
        border_top_right_radius=12,
    )
    
    pygame.draw.line(
        screen,
        (*title_color, 40),
        (panel.rect.x + 1, panel.rect.y + title_bar_height - 1),
        (panel.rect.x + panel.rect.width - 1, panel.rect.y + title_bar_height - 1),
        1,
    )

    if medium_font:
        title_surface = medium_font.render(panel.title, True, title_color)
        title_text_rect = title_surface.get_rect(
            center=(panel.rect.centerx, panel.rect.y + title_bar_height // 2)
        )
        
        shadow_surface = medium_font.render(panel.title, True, (0, 0, 0))
        shadow_rect = title_text_rect.copy()
        shadow_rect.x += 1
        shadow_rect.y += 1
        screen.blit(shadow_surface, shadow_rect)
        
        screen.blit(title_surface, title_text_rect)

    pygame.draw.line(
        screen,
        title_color,
        (panel.rect.x + 15, panel.rect.y + title_bar_height),
        (panel.rect.x + panel.rect.width - 15, panel.rect.y + title_bar_height),
        3,
    )


def draw_scrollbar(screen, panel, mouse_pos=None):
    """Draw scrollbar for panel with hover feedback"""
    if panel.content_height <= panel.rect.height - 60:
        return

    scrollbar_x = panel.rect.right - 16
    scrollbar_y = panel.rect.y + 52
    scrollbar_height = panel.rect.height - 60
    scrollbar_width = 12

    track_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
    
    # Track background
    pygame.draw.rect(screen, (25, 30, 42), track_rect, border_radius=6)
    pygame.draw.rect(screen, (45, 50, 65), track_rect, 1, border_radius=6)

    # Calculate thumb position
    thumb_height = max(30, int((scrollbar_height * scrollbar_height) / panel.content_height))
    scroll_range = max(1, panel.content_height - scrollbar_height)
    max_offset = max(0, panel.content_height - scrollbar_height)
    if max_offset > 0:
        thumb_ratio = panel.scroll_offset / max_offset
    else:
        thumb_ratio = 0
    thumb_y = scrollbar_y + int(thumb_ratio * (scrollbar_height - thumb_height))
    thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
    
    # Check if hovering over scrollbar
    is_hovering = False
    if mouse_pos:
        hit_area = track_rect.inflate(20, 0)
        is_hovering = hit_area.collidepoint(mouse_pos)
    
    # Draw thumb with hover/drag feedback
    thumb_color = COLORS["electric_cyan"] if (panel.dragging or is_hovering) else (60, 70, 90)
    thumb_glow = 40 if (panel.dragging or is_hovering) else 0
    
    if thumb_glow > 0:
        glow_surf = pygame.Surface((thumb_rect.width + 8, thumb_rect.height + 8), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*thumb_color, thumb_glow), glow_surf.get_rect(), border_radius=8)
        screen.blit(glow_surf, (thumb_rect.x - 4, thumb_rect.y - 4))
    
    pygame.draw.rect(screen, thumb_color, thumb_rect, border_radius=5)
    
    # Draw arrow buttons at top and bottom
    arrow_color = (70, 80, 100) if not is_hovering else (100, 120, 150)
    arrow_size = 4
    
    # Up arrow
    up_arrow_center = (scrollbar_x + scrollbar_width // 2, scrollbar_y - 8)
    pygame.draw.polygon(
        screen, arrow_color,
        [(up_arrow_center[0], up_arrow_center[1] - arrow_size),
         (up_arrow_center[0] - arrow_size, up_arrow_center[1] + arrow_size),
         (up_arrow_center[0] + arrow_size, up_arrow_center[1] + arrow_size)]
    )
    
    # Down arrow
    down_arrow_center = (scrollbar_x + scrollbar_width // 2, scrollbar_y + scrollbar_height + 8)
    pygame.draw.polygon(
        screen, arrow_color,
        [(down_arrow_center[0], down_arrow_center[1] + arrow_size),
         (down_arrow_center[0] - arrow_size, down_arrow_center[1] - arrow_size),
         (down_arrow_center[0] + arrow_size, down_arrow_center[1] - arrow_size)]
    )
    scroll_range = max(1, panel.content_height - scrollbar_height)
    thumb_y = (
        scrollbar_y
        + int((panel.scroll_offset * (scrollbar_height - thumb_height)) / scroll_range)
    )
    thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
    
    pygame.draw.rect(screen, (45, 50, 65), thumb_rect.inflate(4, 4), border_radius=6)
    pygame.draw.rect(screen, COLORS["electric_cyan"], thumb_rect, border_radius=5)

    arrow_color = (80, 90, 110)
    
    pygame.draw.polygon(
        screen, arrow_color,
        [(scrollbar_x + scrollbar_width // 2, scrollbar_y - 5),
         (scrollbar_x + 3, scrollbar_y + 8),
         (scrollbar_x + scrollbar_width - 3, scrollbar_y + 8)]
    )
    
    pygame.draw.polygon(
        screen, arrow_color,
        [(scrollbar_x + scrollbar_width // 2, scrollbar_y + scrollbar_height + 5),
         (scrollbar_x + 3, scrollbar_y + scrollbar_height - 8),
         (scrollbar_x + scrollbar_width - 3, scrollbar_y + scrollbar_height - 8)]
    )


def draw_generator_card(
    screen,
    x,
    y,
    width,
    height,
    generator,
    gen_id,
    count,
    cost,
    production,
    can_afford_x1,
    can_afford_x10,
    state,
    config,
    medium_font,
    small_font,
    tiny_font,
):
    """Draw individual generator card - clean, scannable design with integrated buttons"""
    card_rect = pygame.Rect(x, y, width, height)

    is_locked = False
    if gen_id in config["GENERATORS"]:
        if not state.is_generator_unlocked(gen_id):
            is_locked = True
    elif gen_id in config.get("HARDWARE_GENERATORS", {}):
        generator_cfg = config["HARDWARE_GENERATORS"][gen_id]
        if not state.is_hardware_category_unlocked(generator_cfg.get("category", "")):
            is_locked = True

    if is_locked:
        bg_color = (18, 20, 28)
        border_color = (45, 50, 60)
        name_color = (70, 75, 90)
        info_color = (55, 60, 75)
        cost_color = (60, 65, 80)
        accent_color = (35, 40, 50)
    elif can_afford_x1:
        bg_color = (28, 35, 50)
        border_color = COLORS["matrix_green"]
        name_color = COLORS["soft_white"]
        info_color = (160, 180, 200)
        cost_color = COLORS["matrix_green"]
        accent_color = COLORS["matrix_green"]
    else:
        bg_color = (22, 25, 35)
        border_color = (55, 65, 85)
        name_color = (120, 130, 150)
        info_color = (70, 80, 100)
        cost_color = (90, 100, 120)
        accent_color = (45, 55, 70)

    # Draw card background with rounded corners
    pygame.draw.rect(screen, bg_color, card_rect, border_radius=8)

    # Draw subtle glow for affordable cards
    if can_afford_x1:
        glow_rect = card_rect.inflate(6, 6)
        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*border_color, 25), (0, 0, glow_rect.width, glow_rect.height), border_radius=10)
        screen.blit(glow_surf, glow_rect.topleft)

    # Draw card border
    pygame.draw.rect(screen, border_color, card_rect, 2, border_radius=8)

    # Draw left accent bar (replaces the thin line)
    accent_rect = pygame.Rect(x, y, 5, height)
    pygame.draw.rect(screen, accent_color, accent_rect, border_top_left_radius=8, border_bottom_left_radius=8)

    # Draw icon in dedicated square area
    icon_box_size = 50
    icon_box_x = x + 12
    icon_box_y = y + (height - icon_box_size) // 2
    icon_box = pygame.Rect(icon_box_x, icon_box_y, icon_box_size, icon_box_size)
    
    # Icon background
    icon_bg_color = tuple(max(0, c - 15) for c in bg_color)
    pygame.draw.rect(screen, icon_bg_color, icon_box, border_radius=6)
    pygame.draw.rect(screen, accent_color, icon_box, 1, border_radius=6)
    
    icon_text = generator.get("icon", "🎲")
    if is_locked:
        icon_fg_color = (55, 60, 75)
    elif can_afford_x1:
        icon_fg_color = border_color
    else:
        icon_fg_color = (80, 90, 110)
    
    try:
        icon_font = pygame.font.SysFont("segoe ui emoji", 36)
        icon_surface = icon_font.render(icon_text, True, icon_fg_color)
        icon_rect = icon_surface.get_rect(center=icon_box.center)
        screen.blit(icon_surface, icon_rect)
    except (pygame.error, UnicodeEncodeError):
        # Fallback: draw a simple shape
        pygame.draw.circle(screen, icon_fg_color, icon_box.center, 18)

    # Calculate text positions
    text_x = x + 75
    
    # Generator name
    name_text = medium_font.render(generator["name"], True, name_color)
    screen.blit(name_text, (text_x, y + 8))
    
    # Production info line
    if production > 0:
        qty_prod_text = small_font.render(
            f"{count} owned  →  +{format_number(production)}/s",
            True, info_color
        )
    else:
        qty_prod_text = small_font.render(f"{count} owned", True, info_color)
    screen.blit(qty_prod_text, (text_x, y + 28))

    # Flavor text (if exists)
    flavor = generator.get("flavor", "")
    if flavor:
        flavor_text = tiny_font.render(flavor[:35] + ("..." if len(flavor) > 35 else ""), True, (60, 65, 80))
        screen.blit(flavor_text, (text_x, y + 46))

    # Cost display (in the cost_color area, top right)
    cost_str = format_number(cost)
    cost_label = tiny_font.render("COST:", True, cost_color)
    screen.blit(cost_label, (x + width - 105, y + 8))
    cost_text = small_font.render(cost_str, True, cost_color)
    screen.blit(cost_text, (x + width - 105, y + 22))

    if is_locked:
        unlock_threshold = generator.get("unlock_threshold", 0)
        if unlock_threshold > 0:
            req_text = f"Unlocks at {format_number(unlock_threshold)}"
        else:
            category = generator.get("category", "")
            req_text = f"Requires {category.upper()}" if category else "Locked"
        locked_text = small_font.render(req_text, True, (55, 60, 75))
        screen.blit(locked_text, (text_x, y + 62))

    # Integrated BUY buttons at bottom right of card
    btn_width = 50
    btn_height = 24
    btn_y = y + height - 30
    btn_spacing = 4
    
    if not is_locked:
        # x10 button
        if can_afford_x10:
            x10_btn_color = (35, 45, 35)
            x10_btn_border = COLORS["matrix_green"]
            x10_btn_text = COLORS["soft_white"]
        else:
            x10_btn_color = (22, 25, 32)
            x10_btn_border = (45, 50, 60)
            x10_btn_text = (55, 60, 75)
        
        btn1_rect = pygame.Rect(x + width - btn_width * 2 - btn_spacing * 2 - 8, btn_y, btn_width, btn_height)
        pygame.draw.rect(screen, x10_btn_color, btn1_rect, border_radius=4)
        pygame.draw.rect(screen, x10_btn_border, btn1_rect, 1, border_radius=4)
        btn1_text = tiny_font.render("x10", True, x10_btn_text)
        btn1_text_rect = btn1_text.get_rect(center=btn1_rect.center)
        screen.blit(btn1_text, btn1_text_rect)

        # x1 button (primary, slightly larger)
        if can_afford_x1:
            x1_btn_color = (35, 45, 35)
            x1_btn_border = COLORS["matrix_green"]
            x1_btn_text = COLORS["soft_white"]
        else:
            x1_btn_color = (22, 25, 32)
            x1_btn_border = (45, 50, 60)
            x1_btn_text = (55, 60, 75)

        btn2_rect = pygame.Rect(x + width - btn_width - btn_spacing - 8, btn_y, btn_width, btn_height)
        pygame.draw.rect(screen, x1_btn_color, btn2_rect, border_radius=4)
        pygame.draw.rect(screen, x1_btn_border, btn2_rect, 1, border_radius=4)
        btn2_text = tiny_font.render("x1", True, x1_btn_text)
        btn2_text_rect = btn2_text.get_rect(center=btn2_rect.center)
        screen.blit(btn2_text, btn2_text_rect)


def draw_upgrade_card(
    screen,
    x,
    y,
    width,
    height,
    upgrade,
    upgrade_id,
    level,
    cost,
    can_afford,
    upgrade_card_buttons,
    medium_font,
    small_font,
    tiny_font,
    COLORS,
    panel_rect=None,
):
    """Draw individual upgrade card - clean, scannable design with integrated button"""
    card_rect = pygame.Rect(x, y, width, height)

    max_level = upgrade["max_level"]
    is_maxed = level >= max_level

    if is_maxed:
        bg_color = (30, 28, 45)
        border_color = COLORS["gold"]
        name_color = COLORS["gold"]
        info_color = (200, 180, 100)
        cost_color = COLORS["gold"]
        accent_color = COLORS["gold"]
    elif can_afford:
        bg_color = (30, 28, 48)
        border_color = COLORS["neon_purple"]
        name_color = COLORS["soft_white"]
        info_color = (170, 150, 200)
        cost_color = COLORS["matrix_green"]
        accent_color = COLORS["neon_purple"]
    else:
        bg_color = (20, 22, 35)
        border_color = (60, 50, 90)
        name_color = (110, 100, 140)
        info_color = (70, 60, 90)
        cost_color = (80, 70, 100)
        accent_color = (50, 40, 75)

    # Draw card background with rounded corners
    pygame.draw.rect(screen, bg_color, card_rect, border_radius=8)

    # Draw subtle glow for affordable/maxed cards
    if can_afford or is_maxed:
        glow_rect = card_rect.inflate(6, 6)
        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*border_color, 25), (0, 0, glow_rect.width, glow_rect.height), border_radius=10)
        screen.blit(glow_surf, glow_rect.topleft)

    # Draw card border
    pygame.draw.rect(screen, border_color, card_rect, 2, border_radius=8)

    # Draw left accent bar
    accent_rect = pygame.Rect(x, y, 5, height)
    pygame.draw.rect(screen, accent_color, accent_rect, border_top_left_radius=8, border_bottom_left_radius=8)

    # Draw icon in dedicated square area
    icon_box_size = 46
    icon_box_x = x + 12
    icon_box_y = y + (height - icon_box_size) // 2
    icon_box = pygame.Rect(icon_box_x, icon_box_y, icon_box_size, icon_box_size)
    
    # Icon background
    icon_bg_color = tuple(max(0, c - 15) for c in bg_color)
    pygame.draw.rect(screen, icon_bg_color, icon_box, border_radius=6)
    pygame.draw.rect(screen, accent_color, icon_box, 1, border_radius=6)
    
    icon_text = upgrade.get("icon", "⚡")
    if is_maxed:
        icon_fg_color = COLORS["gold"]
    elif can_afford:
        icon_fg_color = COLORS["neon_purple"]
    else:
        icon_fg_color = (70, 60, 90)
    
    try:
        icon_font = pygame.font.SysFont("segoe ui emoji", 32)
        icon_surface = icon_font.render(icon_text, True, icon_fg_color)
        icon_rect = icon_surface.get_rect(center=icon_box.center)
        screen.blit(icon_surface, icon_rect)
    except (pygame.error, UnicodeEncodeError):
        pygame.draw.circle(screen, icon_fg_color, icon_box.center, 16)

    # Calculate text positions
    text_x = x + 70
    
    # Upgrade name
    name_text = medium_font.render(upgrade["name"], True, name_color)
    screen.blit(name_text, (text_x, y + 6))
    
    # Level indicator
    level_color = COLORS["gold"] if is_maxed else COLORS["neon_purple"]
    level_text = small_font.render(f"Lv {level}/{max_level}", True, level_color)
    screen.blit(level_text, (text_x, y + 24))

    # Effect description
    effect_text = upgrade.get("description", "Increases production")
    desc_text = small_font.render(effect_text[:40] + ("..." if len(effect_text) > 40 else ""), True, info_color)
    screen.blit(desc_text, (text_x, y + 42))

    # Progress bar
    bar_x = x + width - 115
    bar_y = y + 28
    bar_w = 105
    bar_h = 6
    
    pygame.draw.rect(screen, (25, 22, 35), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
    progress = level / max_level if max_level > 0 else 0
    pygame.draw.rect(screen, border_color, (bar_x, bar_y, int(bar_w * progress), bar_h), border_radius=3)

    # Cost and integrated BUY button area
    if is_maxed:
        maxed_text = small_font.render("★ MAXED", True, COLORS["gold"])
        screen.blit(maxed_text, (x + width - 95, y + 50))
    else:
        cost_str = format_number(cost)
        cost_label = tiny_font.render("COST:", True, cost_color)
        screen.blit(cost_label, (x + width - 110, y + 50))
        cost_text = small_font.render(cost_str, True, cost_color)
        screen.blit(cost_text, (x + width - 110, y + 62))

        # Integrated BUY button
        btn_x = x + width - 75
        btn_y = y + height - 30
        btn_w = 65
        btn_h = 24
        
        if is_maxed:
            btn_color = (50, 45, 30)
            btn_border_color = COLORS["gold"]
            btn_text_color = COLORS["soft_white"]
        elif can_afford:
            btn_color = (50, 35, 60)
            btn_border_color = COLORS["neon_purple"]
            btn_text_color = COLORS["soft_white"]
        else:
            btn_color = (22, 25, 35)
            btn_border_color = (50, 45, 65)
            btn_text_color = (60, 65, 80)

        btn_key = f"{upgrade_id}_btn"
        from ui_components import Button
        if btn_key not in upgrade_card_buttons:
            upgrade_card_buttons[btn_key] = Button(
                btn_x, btn_y, btn_w, btn_h, "BUY",
                color=btn_color,
                text_color=btn_text_color
            )
        
        btn = upgrade_card_buttons[btn_key]
        btn.rect.x = btn_x
        btn.rect.y = btn_y
        btn.color = btn_color
        btn.is_enabled = can_afford
        
        if panel_rect:
            mouse_pos = pygame.mouse.get_pos()
            adjusted_mouse = (mouse_pos[0] - panel_rect.x, mouse_pos[1] - panel_rect.y)
            btn.update(adjusted_mouse)
        btn.draw(screen)

