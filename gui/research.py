"""Quiet research journal with the same geometry for paint and input."""
import pygame
from constants import ERAS, format_number
from . import theme as t


def research_button_rect(width, height):
    return pygame.Rect(24, height - 72, width - 48, 64)


def research_layout(width, height):
    margin = max(24, (width - 1040) // 2)
    row_height = min(100, (height - 156) // 6)
    cards = [pygame.Rect(margin, 112 + i * row_height, width - 2 * margin, row_height - 8)
             for i in range(6)]
    buttons = [pygame.Rect(card.right - 140, card.centery - 18, 120, 36) for card in cards]
    close = pygame.Rect(width - margin - 100, 26, 100, 38)
    return cards, buttons, close


def research_finished(state):
    projects = state.get_research_projects()
    return bool(projects) and all(project['complete'] for project in projects) and state.get_next_era_info() is None


def completed_research_layout(width, height):
    margin = max(24, (width - 1040) // 2)
    row_height = min(64, max(48, (height - 400) // 5))
    cards = [pygame.Rect(margin, 112 + i * row_height, width - 2 * margin, row_height - 6)
             for i in range(5)]
    panel = pygame.Rect(margin, cards[-1].bottom + 18, width - 2 * margin,
                        height - 48 - cards[-1].bottom - 18)
    button = pygame.Rect(panel.right - 184, panel.bottom - 56, 168, 40)
    close = pygame.Rect(width - margin - 100, 26, 100, 38)
    return cards, panel, button, close


def research_reset_step(state, bit_grid=None):
    # Rebirth is the first reset tier. After trying it, guide the larger Prestige reset.
    prestige = state.total_rebirths > 0
    name = 'Prestige' if prestige else 'Rebirth'
    target = 1000000 if prestige else state.get_rebirth_threshold()
    earned = state.total_bits_earned
    ready = state.can_prestige() if prestige else state.can_rebirth(bit_grid)
    requirement = f'{format_number(earned)} / {format_number(target)} bits earned this cycle.'
    if prestige and state.hardware_generation < 3:
        requirement += ' Reach hardware generation 3.'
    elif not prestige and earned >= target and not ready:
        requirement += ' Finishing cycle completion...'
    if prestige:
        gain = (f'Gain {format_number(state.get_prestige_currency_earned())} Quantum Fragments' if ready else
                'Prestige grants Quantum Fragments')
        reward = gain + ', +10% production and +1 base click.'
    else:
        shards = state.get_estimated_rebirth_tokens()
        gain = f'Gain {format_number(shards)} Data Shards' if shards else 'Rebirth grants Data Shards'
        reward = gain + '. Historical and shard upgrades stay.'
    return {
        'name': name, 'ready': ready,
        'instruction': ('You have tried Rebirth. Prestige is your next larger reset.' if prestige else
                        'Rebirth comes first: start a new cycle and earn Data Shards.'),
        'requirement': requirement,
        'resets': ('Resets bits, machines, standard upgrades, hardware generation and current shards.' if prestige else
                   'Resets bits, machines and standard upgrades. Your research stays.'),
        'reward': reward,
        'fraction': max(0, min(1, earned / target)),
    }


def _draw_completed_research(screen, state, title_font, font, small_font, bit_grid):
    width, height = screen.get_size()
    cards, panel, button, close = completed_research_layout(width, height)
    step = research_reset_step(state, bit_grid)
    screen.fill(t.BACKGROUND)
    t.text(screen, title_font, 'The research journal', (cards[0].x, 24))
    t.text(screen, small_font, 'Every discovery is permanent. Your next chapter is a new cycle.',
           (cards[0].x, 67), t.MUTED, cards[0].width - 120)
    t.button(screen, close, 'Close [R]', small_font)
    for card, project in zip(cards, state.get_research_projects()):
        t.panel(screen, card)
        t.text(screen, font, project['name'], (card.x + 16, card.centery - font.get_height() // 2), t.SAGE, 300)
        t.text(screen, small_font, project['reward'], (card.x + 330, card.centery - small_font.get_height() // 2),
               t.MUTED, card.width - 470)
        t.text(screen, small_font, 'Completed', (card.right - 112, card.centery - small_font.get_height() // 2), t.SAGE)
    t.panel(screen, panel)
    t.text(screen, font, 'Next step · ' + step['name'], (panel.x + 16, panel.y + 14), t.SAGE)
    for i, (key, color) in enumerate((('instruction', t.TEXT), ('requirement', t.MUTED),
                                     ('resets', t.AMBER), ('reward', t.TEXT))):
        t.text(screen, small_font, step[key], (panel.x + 16, panel.y + 46 + i * 24), color, panel.width - 32)
    t.progress(screen, pygame.Rect(panel.x + 16, panel.bottom - 32, panel.width - 220, 5), step['fraction'])
    t.button(screen, button, ('Review ' if step['ready'] else 'Locked: ') + step['name'],
             small_font, step['ready'], step['ready'])
    t.text(screen, small_font, 'Research stays permanent. Review the reset before confirming; nothing resets from this page.',
           (panel.x, height - 30), t.MUTED, panel.width)


def draw_research(screen, state, title_font, font, small_font, bit_grid=None):
    if research_finished(state):
        _draw_completed_research(screen, state, title_font, font, small_font, bit_grid)
        return
    width, height = screen.get_size()
    screen.fill(t.BACKGROUND)
    cards, buttons, close = research_layout(width, height)
    t.text(screen, title_font, 'The research journal', (cards[0].x, 24))
    t.text(screen, small_font, 'Ideas become inventions. Each discovery brings a permanent reward.',
           (cards[0].x, 67), t.MUTED, cards[0].width - 120)
    t.button(screen, close, 'Close [R]', small_font)
    projects = state.get_research_projects()
    next_era = state.get_next_era_info()
    for i, card in enumerate(cards):
        if i < len(projects):
            project = projects[i]
            title = f"{i + 1:02}   {project['name']}"
            unit = 'pebbles' if i == 0 else 'units'
            detail = (f"{format_number(project['earned'])} / {format_number(project['target'])} {unit} earned"
                      f"   ·   {ERAS[project['era']]['name']}")
            reward, ready, complete = project['reward'], project['ready'], project['complete']
            label = 'Completed' if complete else 'Discover' if ready else 'Not ready'
            fraction = min(1, project['earned'] / project['target'])
        else:
            title = 'Next chapter · ' + next_era['name'] if next_era else 'The journey continues'
            detail = (f"{format_number(state.get_total_currency_earned())} / "
                      f"{format_number(next_era['unlock_bits'])} earned · Define Bit required"
                      if next_era else 'All historical eras explored. Keep building your legacy.')
            reward = 'Add new hardware. Keep your balance, machines and inventions.'
            ready, complete = state.can_advance_era(), next_era is None
            label = 'Advance' if ready else 'Completed' if complete else 'Not ready'
            fraction = state.get_era_progress()
        t.panel(screen, card)
        available_width = card.width - 180
        t.text(screen, font, title, (card.x + 16, card.y + 7), t.SAGE if complete else t.TEXT, available_width)
        t.text(screen, small_font, detail, (card.x + 16, card.y + 31), t.MUTED, available_width)
        t.text(screen, small_font, reward, (card.x + 16, card.y + 49), t.AMBER, available_width)
        t.progress(screen, pygame.Rect(card.x + 16, card.bottom - 5, available_width, 3), fraction)
        t.button(screen, buttons[i], label, small_font, ready, ready)
    t.text(screen, small_font, 'Discover in order. Spent currency still counts. Research survives rebirth and prestige.',
           (cards[0].x, height - 30), t.MUTED, cards[0].width)
