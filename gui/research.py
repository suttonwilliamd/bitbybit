"""Research roadmap with shared draw/input geometry, scaled to the window."""
import pygame
from constants import ERAS, format_number


def research_button_rect(width, height):
    return pygame.Rect(int(20 * width / 1200), int(48 * height / 800), 245, 26)


def research_layout(width, height):
    margin = max(16, (width - 900) // 2)
    row_height = min(90, (height - 140) // 6)
    cards = [pygame.Rect(margin, 90 + i * row_height, width - 2 * margin, row_height - 6)
             for i in range(6)]
    buttons = [pygame.Rect(card.right - 120, card.y + 12, 108, card.height - 24)
               for card in cards]
    close = pygame.Rect(width - margin - 100, 18, 100, 34)
    return cards, buttons, close


def draw_research(screen, state, title_font, font, small_font):
    width, height = screen.get_size()
    screen.fill((15, 20, 32))
    cards, buttons, close = research_layout(width, height)
    screen.blit(title_font.render('RESEARCH ROADMAP', True, (0, 220, 240)), (cards[0].x, 16))
    screen.blit(small_font.render('Permanent rewards. Earned totals count even after spending. No reset on era advance.',
                                 True, (160, 175, 190)), (cards[0].x, 60))
    pygame.draw.rect(screen, (50, 60, 80), close, border_radius=5)
    screen.blit(font.render('Close [R]', True, (230, 235, 245)), (close.x + 8, close.y + 8))

    projects = state.get_research_projects()
    next_era = state.get_next_era_info()
    for i, card in enumerate(cards):
        if i < len(projects):
            project = projects[i]
            title = project['name']
            unit = 'pebbles' if i == 0 else 'post-binary units'
            detail = (f"{format_number(project['earned'])}/{format_number(project['target'])} {unit} | "
                      f"{ERAS[project['era']]['name']} | in order")
            reward = project['reward']
            ready = project['ready']
            complete = project['complete']
            label = 'DONE' if complete else 'RESEARCH' if ready else 'LOCKED'
            progress = min(1, project['earned'] / project['target'])
        else:
            title = 'Next Era: ' + next_era['name'] if next_era else 'Historical roadmap complete!'
            detail = (f"{format_number(state.get_total_currency_earned())}/"
                      f"{format_number(next_era['unlock_bits'])} earned | Define Bit required"
                      if next_era else 'Continue with hardware rebirths and prestige.')
            reward = 'Unlock new hardware; keep balance, inventions and upgrades.'
            ready = state.can_advance_era()
            complete = next_era is None
            label = 'ADVANCE' if ready else 'DONE' if complete else 'LOCKED'
            progress = state.get_era_progress()
        color = (75, 210, 150) if ready or complete else (150, 170, 195)
        pygame.draw.rect(screen, (25, 33, 48), card, border_radius=6)
        screen.blit(font.render(title, True, color), (card.x + 12, card.y + 7))
        screen.blit(small_font.render(detail, True, (175, 190, 205)), (card.x + 12, card.y + 28))
        if card.height >= 65:
            screen.blit(small_font.render(reward, True, (145, 165, 185)), (card.x + 12, card.y + 46))
        pygame.draw.rect(screen, (40, 50, 70), (card.x + 12, card.bottom - 5, card.width - 150, 3))
        pygame.draw.rect(screen, color, (card.x + 12, card.bottom - 5, int((card.width - 150) * progress), 3))
        button = buttons[i]
        pygame.draw.rect(screen, (30, 75, 65) if ready else (35, 43, 58), button, border_radius=4)
        text = small_font.render(label, True, color)
        screen.blit(text, text.get_rect(center=button.center))
