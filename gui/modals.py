"""
Modal dialog drawing functions for settings, rebirth, and tutorial
"""

import pygame
from constants import COLORS, HARDWARE_GENERATIONS, format_number


def draw_rebirth_confirmation(screen, showing_rebirth_confirmation, state, bit_grid, WINDOW_WIDTH, WINDOW_HEIGHT, large_font, medium_font, small_font, COLORS):
    """Draw rebirth confirmation modal"""
    if not showing_rebirth_confirmation:
        return

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(COLORS["deep_space_blue"])
    screen.blit(overlay, (0, 0))

    box_rect = pygame.Rect(
        WINDOW_WIDTH // 2 - 300, WINDOW_HEIGHT // 2 - 200, 600, 400
    )
    pygame.draw.rect(
        screen, COLORS["dim_gray"], box_rect, border_radius=16
    )
    pygame.draw.rect(screen, COLORS["gold"], box_rect, 3, border_radius=16)

    title_text = large_font.render(
        "⚠️ COMPRESSION CYCLE ⚠️", True, COLORS["gold"]
    )
    title_rect = title_text.get_rect(
        center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 150)
    )
    screen.blit(title_text, title_rect)

    tokens = state.get_estimated_rebirth_tokens()
    current_mb = format_number(
        state.total_bits_earned / (1024 * 1024)
    )

    current_gen, next_gen = state.get_hardware_generation_info()

    info_lines = [
        f"You will lose:",
        f"• All {current_mb} MB of data",
        f"• All generators",
        f"• All upgrades",
        "",
        f"You will gain:",
        f"• {tokens} Data Shards 💎",
        f"• Access to Compression Era",
        f"• Permanent meta-progression",
    ]

    if next_gen:
        info_lines.extend(
            [
                "",
                f"🚀 HARDWARE UPGRADE AVAILABLE:",
                f"• Advance to {next_gen['name']}",
                f"• Unlock {next_gen['primary_category'].upper()} category",
            ]
        )

    y_offset = -50
    for line in info_lines:
        if line.startswith("•"):
            text_color = COLORS["soft_white"]
        elif line == "":
            y_offset -= 10
            continue
        elif line.startswith("You will lose:"):
            text_color = COLORS["signal_orange"]
        elif line.startswith("You will gain:"):
            text_color = COLORS["matrix_green"]
        else:
            text_color = COLORS["gold"]

        text_surface = small_font.render(line, True, text_color)
        text_rect = text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + y_offset)
        )
        screen.blit(text_surface, text_rect)
        y_offset += 25

    mouse_pos = pygame.mouse.get_pos()

    yes_rect = pygame.Rect(
        WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2 + 50, 100, 40
    )
    yes_color = (
        COLORS["matrix_green"]
        if yes_rect.collidepoint(mouse_pos)
        else COLORS["gold"]
    )
    pygame.draw.rect(screen, yes_color, yes_rect, border_radius=8)
    yes_text = medium_font.render(
        "COMPRESS! 🌀", True, COLORS["soft_white"]
    )
    yes_text_rect = yes_text.get_rect(center=yes_rect.center)
    screen.blit(yes_text, yes_text_rect)

    no_rect = pygame.Rect(
        WINDOW_WIDTH // 2 + 20, WINDOW_HEIGHT // 2 + 50, 100, 40
    )
    no_color = (
        COLORS["signal_orange"]
        if no_rect.collidepoint(mouse_pos)
        else COLORS["dim_gray"]
    )
    pygame.draw.rect(screen, no_color, no_rect, border_radius=8)
    no_text = medium_font.render("CANCEL", True, COLORS["soft_white"])
    no_text_rect = no_text.get_rect(center=no_rect.center)
    screen.blit(no_text, no_text_rect)


def draw_prestige_confirmation(screen, showing_prestige_confirmation, state, WINDOW_WIDTH, WINDOW_HEIGHT, large_font, medium_font, small_font, COLORS):
    """Draw prestige confirmation modal"""
    if not showing_prestige_confirmation:
        return

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(220)
    overlay.fill(COLORS["deep_space_blue"])
    screen.blit(overlay, (0, 0))

    box_rect = pygame.Rect(
        WINDOW_WIDTH // 2 - 350, WINDOW_HEIGHT // 2 - 250, 700, 500
    )
    pygame.draw.rect(
        screen, COLORS["panel_background"], box_rect, border_radius=16
    )
    pygame.draw.rect(screen, COLORS["quantum_violet"], box_rect, 3, border_radius=16)

    title_text = large_font.render(
        "🔧 UPGRADE MOTHERBOARD 🔧", True, COLORS["quantum_violet"]
    )
    title_rect = title_text.get_rect(
        center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 200)
    )
    screen.blit(title_text, title_rect)

    currency_earned = state.get_prestige_currency_earned()
    current_bits = format_number(state.total_bits_earned)

    info_lines = [
        "Warning: This will RESET everything!",
        "",
        "You will lose:",
        f"• All {current_bits} bits",
        "• All generators & upgrades",
        "• All hardware generations",
        "• Compression tokens",
        "",
        "You will gain:",
        f"• {currency_earned} Quantum Fragments 💎",
        f"• +{state.prestige_count + 1}0% production bonus",
        f"• +{state.prestige_count + 1} click power bonus",
        "",
        f"Current motherboard bonus: +{(state.get_prestige_bonus() - 1) * 100:.0f}% production",
    ]

    y_offset = -150
    for line in info_lines:
        if line.startswith("•"):
            text_color = COLORS["soft_white"]
        elif line == "":
            y_offset -= 10
            continue
        elif line.startswith("Warning:"):
            text_color = COLORS["red_error"]
        elif line.startswith("You will lose:"):
            text_color = COLORS["signal_orange"]
        elif line.startswith("You will gain:"):
            text_color = COLORS["matrix_green"]
        else:
            text_color = COLORS["muted_blue"]

        text_surface = small_font.render(line, True, text_color)
        text_rect = text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + y_offset)
        )
        screen.blit(text_surface, text_rect)
        y_offset += 25

    mouse_pos = pygame.mouse.get_pos()

    yes_rect = pygame.Rect(
        WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 120, 140, 50
    )
    yes_color = (
        COLORS["quantum_violet"]
        if yes_rect.collidepoint(mouse_pos)
        else COLORS["gold"]
    )
    pygame.draw.rect(screen, yes_color, yes_rect, border_radius=8)
    yes_text = medium_font.render(
        "UPGRADE! 🔧", True, COLORS["soft_white"]
    )
    yes_text_rect = yes_text.get_rect(center=yes_rect.center)
    screen.blit(yes_text, yes_text_rect)

    no_rect = pygame.Rect(
        WINDOW_WIDTH // 2 + 10, WINDOW_HEIGHT // 2 + 120, 140, 50
    )
    no_color = (
        COLORS["signal_orange"]
        if no_rect.collidepoint(mouse_pos)
        else COLORS["dim_gray"]
    )
    pygame.draw.rect(screen, no_color, no_rect, border_radius=8)
    no_text = medium_font.render("CANCEL", True, COLORS["soft_white"])
    no_text_rect = no_text.get_rect(center=no_rect.center)
    screen.blit(no_text, no_text_rect)

    return yes_rect, no_rect


def draw_tutorial(screen, showing_tutorial, tutorial_text, current_width, current_height, medium_font, small_font, COLORS):
    """Draw tutorial modal"""
    if not showing_tutorial or not tutorial_text:
        return

    overlay = pygame.Surface((current_width, current_height))
    overlay.set_alpha(200)
    overlay.fill(COLORS["deep_space_blue"])
    screen.blit(overlay, (0, 0))

    box_width = min(500, current_width - 100)
    box_height = min(300, current_height - 200)
    box_rect = pygame.Rect(
        current_width // 2 - box_width // 2,
        current_height // 2 - box_height // 2,
        box_width,
        box_height,
    )
    pygame.draw.rect(
        screen, COLORS["dim_gray"], box_rect, border_radius=16
    )
    pygame.draw.rect(
        screen, COLORS["electric_cyan"], box_rect, 3, border_radius=16
    )

    lines = tutorial_text.split("\n")
    y_offset = 0
    for line in lines:
        text_surface = small_font.render(line, True, COLORS["soft_white"])
        text_rect = text_surface.get_rect(
            center=(
                current_width // 2,
                current_height // 2 - 50 + y_offset,
            )
        )
        screen.blit(text_surface, text_rect)
        y_offset += 30

    continue_button_rect = pygame.Rect(
        current_width // 2 - 100, current_height // 2 + 60, 200, 40
    )
    mouse_pos = pygame.mouse.get_pos()
    if continue_button_rect.collidepoint(mouse_pos):
        button_color = COLORS["electric_cyan"]
        text_color = COLORS["soft_white"]
    else:
        button_color = COLORS["muted_blue"]
        text_color = COLORS["soft_white"]

    pygame.draw.rect(
        screen, button_color, continue_button_rect, border_radius=8
    )
    pygame.draw.rect(
        screen,
        COLORS["electric_cyan"],
        continue_button_rect,
        2,
        border_radius=8,
    )

    continue_text = medium_font.render(
        "CLICK TO CONTINUE", True, text_color
    )
    continue_text_rect = continue_text.get_rect(
        center=continue_button_rect.center
    )
    screen.blit(continue_text, continue_text_rect)


def draw_settings_page(screen, current_width, current_height, base_width, base_height,
                        visual_settings, high_contrast_mode, reduced_motion_mode,
                        visual_quality, large_font, medium_font, small_font, tiny_font, COLORS):
    """Draw settings page modal"""
    overlay = pygame.Surface((current_width, current_height))
    overlay.set_alpha(230)
    overlay.fill(COLORS["deep_space_blue"])
    screen.blit(overlay, (0, 0))

    scale_x = current_width / base_width
    scale_y = current_height / base_height
    settings_rect = pygame.Rect(
        current_width // 2 - int(300 * scale_x),
        int(120 * scale_y),
        int(600 * scale_x),
        int(520 * scale_y),
    )
    pygame.draw.rect(
        screen, COLORS["dim_gray"], settings_rect, border_radius=16
    )
    pygame.draw.rect(
        screen, COLORS["electric_cyan"], settings_rect, 3, border_radius=16
    )

    title_text = large_font.render("⚙️ SETTINGS", True, COLORS["electric_cyan"])
    title_rect = title_text.get_rect(
        center=(current_width // 2, int(170 * scale_y))
    )
    screen.blit(title_text, title_rect)

    mouse_pos = pygame.mouse.get_pos()

    close_button_rect = pygame.Rect(
        settings_rect.right - 35, settings_rect.top + 10, 25, 25
    )
    close_button_color = (
        COLORS["signal_orange"] if close_button_rect.collidepoint(mouse_pos) else COLORS["dim_gray"]
    )
    pygame.draw.rect(screen, close_button_color, close_button_rect, border_radius=4)
    close_x = medium_font.render("×", True, COLORS["soft_white"])
    close_x_rect = close_x.get_rect(center=close_button_rect.center)
    screen.blit(close_x, close_x_rect)

    section_text = medium_font.render(
        "VISUAL EFFECTS", True, COLORS["neon_purple"]
    )
    section_rect = section_text.get_rect(
        center=(current_width // 2, int(220 * scale_y))
    )
    screen.blit(section_text, section_rect)

    crt_rect = pygame.Rect(
        current_width // 2 - int(200 * scale_x),
        int(270 * scale_y),
        int(400 * scale_x),
        int(40 * scale_y),
    )
    crt_color = (
        COLORS["electric_cyan"]
        if visual_settings["crt_effects"]
        else COLORS["muted_blue"]
    )
    pygame.draw.rect(screen, crt_color, crt_rect, 2, border_radius=8)
    crt_text = small_font.render(
        f"📺 CRT Effects: {'ON' if visual_settings['crt_effects'] else 'OFF'}",
        True,
        COLORS["soft_white"],
    )
    crt_text_rect = crt_text.get_rect(center=crt_rect.center)
    screen.blit(crt_text, crt_text_rect)

    rain_rect = pygame.Rect(
        current_width // 2 - int(200 * scale_x),
        int(320 * scale_y),
        int(400 * scale_x),
        int(40 * scale_y),
    )
    rain_color = (
        COLORS["electric_cyan"]
        if visual_settings["binary_rain"]
        else COLORS["muted_blue"]
    )
    pygame.draw.rect(screen, rain_color, rain_rect, 2, border_radius=8)
    rain_text = small_font.render(
        f"🌧️ Binary Rain: {'ON' if visual_settings['binary_rain'] else 'OFF'}",
        True,
        COLORS["soft_white"],
    )
    rain_text_rect = rain_text.get_rect(center=rain_rect.center)
    screen.blit(rain_text, rain_text_rect)

    particle_rect = pygame.Rect(
        current_width // 2 - int(200 * scale_x),
        int(370 * scale_y),
        int(400 * scale_x),
        int(40 * scale_y),
    )
    particle_color = (
        COLORS["electric_cyan"]
        if visual_settings["particle_effects"]
        else COLORS["muted_blue"]
    )
    pygame.draw.rect(screen, particle_color, particle_rect, 2, border_radius=8)
    particle_text = small_font.render(
        f"✨ Particle Effects: {'ON' if visual_settings['particle_effects'] else 'OFF'}",
        True,
        COLORS["soft_white"],
    )
    particle_text_rect = particle_text.get_rect(center=particle_rect.center)
    screen.blit(particle_text, particle_text_rect)

    access_section_text = medium_font.render(
        "ACCESSIBILITY", True, COLORS["neon_purple"]
    )
    access_section_rect = access_section_text.get_rect(
        center=(current_width // 2, int(420 * scale_y))
    )
    screen.blit(access_section_text, access_section_rect)

    contrast_rect = pygame.Rect(
        current_width // 2 - int(200 * scale_x),
        int(450 * scale_y),
        int(400 * scale_x),
        int(40 * scale_y),
    )
    contrast_color = (
        COLORS["electric_cyan"] if high_contrast_mode else COLORS["muted_blue"]
    )
    pygame.draw.rect(screen, contrast_color, contrast_rect, 2, border_radius=8)
    contrast_text = small_font.render(
        f"👁️ High Contrast: {'ON' if high_contrast_mode else 'OFF'}",
        True,
        COLORS["soft_white"],
    )
    contrast_text_rect = contrast_text.get_rect(center=contrast_rect.center)
    screen.blit(contrast_text, contrast_text_rect)

    motion_rect = pygame.Rect(
        current_width // 2 - int(200 * scale_x),
        int(500 * scale_y),
        int(400 * scale_x),
        int(40 * scale_y),
    )
    motion_color = (
        COLORS["electric_cyan"]
        if reduced_motion_mode
        else COLORS["muted_blue"]
    )
    pygame.draw.rect(screen, motion_color, motion_rect, 2, border_radius=8)
    motion_text = small_font.render(
        f"🎯 Reduced Motion: {'ON' if reduced_motion_mode else 'OFF'}",
        True,
        COLORS["soft_white"],
    )
    motion_text_rect = motion_text.get_rect(center=motion_rect.center)
    screen.blit(motion_text, motion_text_rect)

    quality_rect = pygame.Rect(
        current_width // 2 - int(200 * scale_x),
        int(550 * scale_y),
        int(400 * scale_x),
        int(40 * scale_y),
    )
    quality_color = COLORS["electric_cyan"]
    pygame.draw.rect(screen, quality_color, quality_rect, 2, border_radius=8)
    quality_text = small_font.render(
        f"🎨 Visual Quality: {visual_quality.upper()}",
        True,
        COLORS["soft_white"],
    )
    quality_text_rect = quality_text.get_rect(center=quality_rect.center)
    screen.blit(quality_text, quality_text_rect)

    inst_text = tiny_font.render(
        "Click any setting to toggle • Press ESC or click × to close",
        True,
        COLORS["muted_blue"],
    )
    inst_rect = inst_text.get_rect(
        center=(current_width // 2, int(600 * scale_y))
    )
    screen.blit(inst_text, inst_rect)

    if crt_rect.collidepoint(mouse_pos):
        pygame.draw.rect(
            screen, COLORS["electric_cyan"], crt_rect, 3, border_radius=8
        )
    elif rain_rect.collidepoint(mouse_pos):
        pygame.draw.rect(
            screen, COLORS["electric_cyan"], rain_rect, 3, border_radius=8
        )
    elif particle_rect.collidepoint(mouse_pos):
        pygame.draw.rect(
            screen, COLORS["electric_cyan"], particle_rect, 3, border_radius=8
        )
    elif contrast_rect.collidepoint(mouse_pos):
        pygame.draw.rect(
            screen, COLORS["electric_cyan"], contrast_rect, 3, border_radius=8
        )
    elif motion_rect.collidepoint(mouse_pos):
        pygame.draw.rect(
            screen, COLORS["electric_cyan"], motion_rect, 3, border_radius=8
        )
    elif quality_rect.collidepoint(mouse_pos):
        pygame.draw.rect(
            screen, COLORS["electric_cyan"], quality_rect, 3, border_radius=8
        )

    return {
        "close": close_button_rect,
        "crt": crt_rect,
        "rain": rain_rect,
        "particle": particle_rect,
        "contrast": contrast_rect,
        "motion": motion_rect,
        "quality": quality_rect,
    }


def draw_statistics_page(screen, current_width, current_height, base_width, base_height,
                        state, format_number_func, large_font, medium_font, small_font, tiny_font, COLORS):
    """Draw statistics page modal"""
    overlay = pygame.Surface((current_width, current_height))
    overlay.set_alpha(230)
    overlay.fill(COLORS["deep_space_blue"])
    screen.blit(overlay, (0, 0))

    scale_x = current_width / base_width
    scale_y = current_height / base_height
    stats_rect = pygame.Rect(
        current_width // 2 - int(250 * scale_x),
        int(150 * scale_y),
        int(500 * scale_y),
        int(400 * scale_y),
    )
    pygame.draw.rect(
        screen, COLORS["dim_gray"], stats_rect, border_radius=16
    )
    pygame.draw.rect(
        screen, COLORS["neon_purple"], stats_rect, 3, border_radius=16
    )

    title_text = large_font.render("📊 STATISTICS", True, COLORS["neon_purple"])
    title_rect = title_text.get_rect(
        center=(current_width // 2, int(200 * scale_y))
    )
    screen.blit(title_text, title_rect)

    mouse_pos = pygame.mouse.get_pos()

    close_button_rect = pygame.Rect(
        stats_rect.right - 35, stats_rect.top + 10, 25, 25
    )
    close_button_color = (
        COLORS["signal_orange"] if close_button_rect.collidepoint(mouse_pos) else COLORS["dim_gray"]
    )
    pygame.draw.rect(screen, close_button_color, close_button_rect, border_radius=4)
    close_x = medium_font.render("×", True, COLORS["soft_white"])
    close_x_rect = close_x.get_rect(center=close_button_rect.center)
    screen.blit(close_x, close_x_rect)

    time_played_seconds = (pygame.time.get_ticks() - state.start_time) // 1000
    hours = time_played_seconds // 3600
    minutes = (time_played_seconds % 3600) // 60
    seconds = time_played_seconds % 60
    time_str = f"{hours}h {minutes}m {seconds}s"

    stats_lines = [
        ("Time Played:", time_str),
        ("Total Bits Earned:", format_number_func(state.total_bits_earned)),
        ("Current Production:", f"{format_number_func(state.get_production_rate())} b/s"),
        ("Total Clicks:", str(state.total_clicks)),
        ("Prestige Count:", str(state.prestige_count)),
    ]

    if hasattr(state, 'data_shards'):
        stats_lines.append(("Data Shards:", str(state.data_shards)))

    y_offset = 250
    for label, value in stats_lines:
        label_text = small_font.render(label, True, COLORS["muted_blue"])
        label_rect = label_text.get_rect(
            center=(current_width // 2 - 80, int(y_offset * scale_y))
        )
        screen.blit(label_text, label_rect)

        value_text = small_font.render(str(value), True, COLORS["soft_white"])
        value_rect = value_text.get_rect(
            center=(current_width // 2 + 80, int(y_offset * scale_y))
        )
        screen.blit(value_text, value_rect)
        y_offset += 35

    inst_text = tiny_font.render(
        "Click × or press ESC to close",
        True,
        COLORS["muted_blue"],
    )
    inst_rect = inst_text.get_rect(
        center=(current_width // 2, int(510 * scale_y))
    )
    screen.blit(inst_text, inst_rect)

    return close_button_rect
