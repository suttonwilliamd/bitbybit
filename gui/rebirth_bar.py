"""
Rebirth bar drawing function
"""

import pygame
from constants import COLORS, HARDWARE_GENERATIONS, format_number


def draw_rebirth_bar(screen, state, bit_grid, rebirth_button, current_width, current_height,
                    base_width, base_height, monospace_font, COLORS):
    """Draw the rebirth progress bar at the bottom of the screen"""
    bar_rect = pygame.Rect(
        0,
        current_height - int(80 * (current_height / base_height)),
        current_width,
        int(80 * (current_height / base_height)),
    )

    shadow_rect = pygame.Rect(
        2,
        current_height - int(78 * (current_height / base_height)),
        current_width - 4,
        int(76 * (current_height / base_height)),
    )
    pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect)

    pygame.draw.rect(screen, COLORS["deep_space_blue"], bar_rect)

    pygame.draw.line(
        screen,
        COLORS["neon_purple"],
        (
            0,
            current_height
            - int(80 * (current_height / base_height)),
        ),
        (
            current_width,
            current_height
            - int(80 * (current_height / base_height)),
        ),
        2,
    )
    for i in range(1, 4):
        alpha = 50 - i * 15
        glow_color = (*COLORS["neon_purple"][:3], alpha)
        pygame.draw.line(
            screen,
            glow_color[:3],
            (
                0,
                current_height
                - int(80 * (current_height / base_height))
                + i,
            ),
            (
                current_width,
                current_height
                - int(80 * (current_height / base_height))
                + i,
            ),
            1,
        )

    current_gen, next_gen = state.get_hardware_generation_info()
    rebirth_threshold = state.get_rebirth_threshold()

    era_completion = bit_grid.get_era_completion_percentage(rebirth_threshold) / 100
    progress = min(era_completion, 1.0)
    tokens = state.get_estimated_rebirth_tokens()
    current_bits = format_number(state.total_bits_earned)
    target_bits = format_number(rebirth_threshold)
    era_completion_text = (
        f"Era Completion: {bit_grid.get_era_completion_percentage(rebirth_threshold):.1f}%"
    )

    scale_x = current_width / base_width
    scale_y = current_height / base_height
    progress_bg = pygame.Rect(
        int(200 * scale_x),
        current_height - int(50 * scale_y),
        int(800 * scale_x),
        int(20 * scale_y),
    )
    progress_fill = pygame.Rect(
        int(200 * scale_x),
        current_height - int(50 * scale_y),
        int(800 * scale_x * progress),
        int(20 * scale_y),
    )

    pygame.draw.rect(
        screen,
        COLORS["deep_space_gradient_end"],
        progress_bg,
        border_radius=10,
    )

    if progress > 0:
        for i in range(progress_fill.width):
            gradient_ratio = i / progress_fill.width
            fill_color = (
                int(
                    COLORS["electric_cyan"][0]
                    + (COLORS["neon_purple"][0] - COLORS["electric_cyan"][0])
                    * gradient_ratio
                ),
                int(
                    COLORS["electric_cyan"][1]
                    + (COLORS["neon_purple"][1] - COLORS["electric_cyan"][1])
                    * gradient_ratio
                ),
                int(
                    COLORS["electric_cyan"][2]
                    + (COLORS["neon_purple"][2] - COLORS["electric_cyan"][2])
                    * gradient_ratio
                ),
            )
            pygame.draw.line(
                screen,
                fill_color,
                (progress_fill.left + i, progress_fill.top),
                (progress_fill.left + i, progress_fill.bottom),
            )

    if progress_fill.width > 0:
        shimmer_offset = (pygame.time.get_ticks() // 20) % (
            progress_fill.width + 40
        )
        shimmer_rect = pygame.Rect(
            progress_fill.left + shimmer_offset - 20,
            progress_fill.top,
            40,
            progress_fill.height,
        )
        if (
            shimmer_rect.left >= progress_fill.left
            and shimmer_rect.right <= progress_fill.right
        ):
            shimmer_surface = pygame.Surface(
                (shimmer_rect.width, shimmer_rect.height)
            )
            shimmer_surface.set_alpha(100)
            shimmer_surface.fill((255, 255, 255))
            screen.blit(shimmer_surface, shimmer_rect)

    if progress >= 1.0 and state.can_rebirth(bit_grid):
        if next_gen:
            rebirth_button.text = (
                f"🚀 UPGRADE TO {next_gen['name'].split()[0]}!"
            )
        else:
            rebirth_button.text = f"🌀 COMPRESS FOR {tokens} ⭐"
        rebirth_button.draw(screen)

    progress_text = monospace_font.render(
        f"{era_completion_text} | ({current_bits} / {target_bits})",
        True,
        COLORS["soft_white"],
    )
    progress_rect = progress_text.get_rect(
        center=(current_width // 2, current_height - int(38 * scale_y))
    )
    screen.blit(progress_text, progress_rect)
