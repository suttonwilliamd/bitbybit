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


def draw_research(screen, state, title_font, font, small_font):
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
            reward = 'Unlock hardware. Keep your balance and inventions.'
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
