"""Settings, statistics and confirmations in the dashboard's visual language."""
import pygame
from constants import format_number
from . import theme as t


def reset_layout(width, height):
    box = pygame.Rect(0, 0, min(600, width - 64), min(460, height - 96))
    box.center = (width // 2, height // 2)
    yes = pygame.Rect(box.centerx - 150, box.bottom - 64, 140, 40)
    no = pygame.Rect(box.centerx + 10, box.bottom - 64, 140, 40)
    return box, yes, no


def tutorial_layout(width, height):
    box = pygame.Rect(0, 0, min(640, width - 64), min(420, height - 96))
    box.center = (width // 2, height // 2)
    return box, pygame.Rect(box.centerx - 100, box.bottom - 64, 200, 40)


def reset_dialog(screen, state, prestige, large_font, font, small_font):
    box, yes, no = reset_layout(*screen.get_size())
    t.panel(screen, box)
    t.text(screen, large_font, 'A new motherboard' if prestige else 'Start a new cycle', (box.x + 28, box.y + 24))
    t.text(screen, small_font, 'A fresh start. Your research stays with you.', (box.x + 28, box.y + 62), t.MUTED)
    if prestige:
        lines = [
            ('This resets:', t.AMBER),
            ('Bits, generators, standard upgrades and hardware generation.', t.TEXT),
            ('Your current shards and compression era.', t.TEXT),
            ('You receive:', t.SAGE),
            (f'{state.get_prestige_currency_earned()} Quantum Fragments', t.TEXT),
            (f'Total production bonus: +{(state.prestige_count + 1) * 10}%', t.TEXT),
            (f'Total click bonus: +{state.prestige_count + 1}', t.TEXT),
        ]
    else:
        lines = [
            ('This resets:', t.AMBER),
            ('Bits, generators and standard upgrades.', t.TEXT),
            ('You receive:', t.SAGE),
            (f'{state.get_estimated_rebirth_tokens()} Data Shards', t.TEXT),
            ('Research, historical upgrades and shard upgrades stay.', t.TEXT),
        ]
    for i, (line, color) in enumerate(lines):
        t.text(screen, small_font, line, (box.x + 28, box.y + 108 + i * 31), color, box.width - 56)
    t.button(screen, yes, 'Prestige' if prestige else 'Rebirth', font, primary=True)
    t.button(screen, no, 'Keep going', font)
    return yes, no


def draw_rebirth_confirmation(screen, showing_rebirth_confirmation, state, bit_grid, WINDOW_WIDTH, WINDOW_HEIGHT, large_font, medium_font, small_font, COLORS):
    if showing_rebirth_confirmation:
        return reset_dialog(screen, state, False, large_font, medium_font, small_font)


def draw_prestige_confirmation(screen, showing_prestige_confirmation, state, WINDOW_WIDTH, WINDOW_HEIGHT, large_font, medium_font, small_font, COLORS):
    if showing_prestige_confirmation:
        return reset_dialog(screen, state, True, large_font, medium_font, small_font)


def draw_tutorial(screen, showing_tutorial, tutorial_text, current_width, current_height, medium_font, small_font, COLORS):
    if not showing_tutorial or not tutorial_text:
        return
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 160))
    screen.blit(shade, (0, 0))
    box, continue_button = tutorial_layout(current_width, current_height)
    t.panel(screen, box)
    t.text(screen, medium_font, 'One small step', (box.x + 28, box.y + 24), t.SAGE)
    y = box.y + 68
    for paragraph in tutorial_text.splitlines():
        line = ''
        for word in paragraph.split():
            if small_font.size(line + ' ' + word)[0] > box.width - 56:
                t.text(screen, small_font, line, (box.x + 28, y))
                y += 24
                line = word
            else:
                line = (line + ' ' + word).strip()
        t.text(screen, small_font, line, (box.x + 28, y))
        y += 26
    t.button(screen, continue_button, 'Continue', medium_font, primary=True)


def draw_settings_page(screen, current_width, current_height, base_width, base_height,
                       visual_settings, high_contrast_mode, reduced_motion_mode,
                       visual_quality, large_font, medium_font, small_font, tiny_font, COLORS):
    box = pygame.Rect(0, 0, min(620, current_width - 64), min(540, current_height - 64))
    box.center = (current_width // 2, current_height // 2)
    t.panel(screen, box)
    t.text(screen, large_font, 'Make yourself comfortable', (box.x + 28, box.y + 24))
    t.text(screen, small_font, 'Quiet by default. Effects are always optional.', (box.x + 28, box.y + 62), t.MUTED)
    close = pygame.Rect(box.right - 62, box.y + 20, 36, 36)
    t.button(screen, close, '×', medium_font)
    result = {'close': close}
    entries = [('crt', 'CRT texture', visual_settings['crt_effects']),
               ('rain', 'Binary rain', visual_settings['binary_rain']),
               ('particle', 'Click particles', visual_settings['particle_effects']),
               ('contrast', 'High contrast', high_contrast_mode),
               ('motion', 'Reduce motion', reduced_motion_mode),
               ('quality', 'Effect quality', visual_quality.title())]
    for i, (key, label, value) in enumerate(entries):
        rect = pygame.Rect(box.x + 28, box.y + 112 + i * 54, box.width - 56, 44)
        result[key] = rect
        t.button(screen, rect, '', small_font)
        t.text(screen, small_font, label, (rect.x + 14, rect.y + 12))
        value = 'On' if value is True else 'Off' if value is False else value
        image = small_font.render(value, True, t.SAGE)
        screen.blit(image, (rect.right - image.get_width() - 14, rect.y + 12))
    t.text(screen, tiny_font, 'Reduced motion pauses animated effects. Escape closes this page.',
           (box.x + 28, box.bottom - 42), t.MUTED, box.width - 56)
    return result


def draw_statistics_page(screen, current_width, current_height, base_width, base_height,
                         state, format_number_func, large_font, medium_font, small_font, tiny_font, COLORS):
    box = pygame.Rect(0, 0, min(620, current_width - 64), min(520, current_height - 64))
    box.center = (current_width // 2, current_height // 2)
    t.panel(screen, box)
    t.text(screen, large_font, 'A little progress adds up', (box.x + 28, box.y + 24))
    close = pygame.Rect(box.right - 62, box.y + 20, 36, 36)
    t.button(screen, close, '×', medium_font)
    seconds = max(0, (pygame.time.get_ticks() - state.start_time) // 1000)
    stats = [('Time this session', f'{seconds // 3600}h {(seconds % 3600) // 60}m {seconds % 60}s'),
             ('Pebbles earned', format_number(state.total_pebbles_earned)),
             ('Bits earned', format_number(state.total_bits_earned)),
             ('Production', f'{format_number(state.get_production_rate())} / second'),
             ('Total clicks', format_number(state.total_clicks)),
             ('Data Shards', format_number(state.data_shards)),
             ('Prestige cycles', str(state.prestige_count)),
             ('Quantum Fragments', format_number(state.prestige_currency))]
    for i, (label, value) in enumerate(stats):
        y = box.y + 98 + i * 42
        t.text(screen, small_font, label, (box.x + 28, y), t.MUTED)
        image = medium_font.render(value, True, t.TEXT)
        screen.blit(image, (box.right - image.get_width() - 28, y))
    t.text(screen, tiny_font, 'Keep going, bit by bit. Escape closes this page.', (box.x + 28, box.bottom - 36), t.MUTED)
    return close
