"""Historical browsing and a quiet, shard-funded restoration gallery."""
import pygame
from constants import ERAS, format_number
from machine_progression import STAGES, DETAILS
from . import theme as t


def history_button_rect(width, height, journal=False):
    if journal:
        margin = max(24, (width - 1040) // 2)
        return pygame.Rect(width - margin - 256, 26, 140, 38)
    return pygame.Rect(width - 378, 24, 132, 38)


def present_button_rect(width, height):
    return pygame.Rect(width - 534, 24, 144, 38)


def workshop_layout(width, height):
    margin = max(24, (width - 1160) // 2)
    rows = [pygame.Rect(margin, 142 + era * 60, 224, 52) for era in ERAS]
    panel = pygame.Rect(margin + 248, 142, width - margin * 2 - 248, height - 190)
    box = pygame.Rect(panel.x + 16, panel.y + 46, panel.width - 32, panel.height - 244)
    preview = pygame.Rect(0, 0, 720, 400).fit(box)
    preview.center = box.center
    modes = [pygame.Rect(panel.x + 16 + i * 126, panel.bottom - 188, 116, 32) for i in range(3)]
    buy = pygame.Rect(panel.right - 216, panel.bottom - 56, 200, 40)
    view = pygame.Rect(panel.x + 16, panel.bottom - 56, 156, 40)
    close = pygame.Rect(width - margin - 100, 26, 100, 38)
    return dict(rows=rows, panel=panel, preview=preview, modes=modes, buy=buy, view=view, close=close)


def draw_workshop(game):
    # Deferred import avoids a cycle with the dashboard's shared header controls.
    from .dashboard import draw_machine
    screen, state = game.screen, game.state
    screen.fill(t.BACKGROUND)
    geometry = workshop_layout(game.current_width, game.current_height)
    panel, era = geometry['panel'], game.workshop_era
    margin = geometry['rows'][0].x
    t.text(screen, game.large_font, 'History & Shard Workshop', (margin, 28))
    t.text(screen, game.small_font, 'Choose an era to revisit its centerpiece, hardware and upgrades.', (margin, 70), t.MUTED)
    multiplier = state.get_workshop_multiplier()
    t.text(screen, game.small_font,
           f'{format_number(state.data_shards)} shards available  ·  Permanent workshop bonus {multiplier:.2f}x',
           (margin, 101), t.SAGE)
    t.button(screen, geometry['close'], 'Close', game.small_font)
    history_limit = state.get_history_limit()
    for index, row in enumerate(geometry['rows']):
        unlocked = index <= history_limit
        t.panel(screen, row, t.SAGE_DARK if index == era else t.CARD)
        t.text(screen, game.small_font, ERAS[index]['name'], (row.x + 12, row.y + 7),
               t.TEXT if unlocked else t.MUTED, row.width - 24)
        detail = f'{STAGES[state.get_machine_level(index)]} · {state.get_machine_level(index)}/3' if unlocked else 'Not reached yet'
        t.text(screen, game.tiny_font, detail, (row.x + 12, row.y + 30), t.SAGE if unlocked else t.MUTED)
    t.panel(screen, panel)
    owned = state.get_machine_level(era)
    level = owned if game.workshop_preview == 0 else min(3, owned + 1) if game.workshop_preview == 1 else 3
    t.text(screen, game.medium_font, f'{ERAS[era]["name"]} · {STAGES[level]} ({level}/3)',
           (panel.x + 16, panel.y + 13), t.TEXT, panel.width - 32)
    draw_machine(screen, geometry['preview'], era, state.get_current_currency_value(),
                 game.machine_animation, detail=level)
    for i, label in enumerate(('Owned', 'Next rank', 'Masterwork')):
        t.button(screen, geometry['modes'][i], label, game.small_font,
                 enabled=i != 1 or owned < 3, primary=game.workshop_preview == i)
    t.text(screen, game.tiny_font, 'Preview only · live balance in ' + state.get_current_currency().lower(),
           (panel.x + 16, panel.bottom - 146), t.MUTED, panel.width - 32)
    detail = ('Fully restored. Your Masterwork is permanent.' if owned == 3 else
              f'Next {STAGES[owned + 1]}: {DETAILS[era][owned]}.')
    t.text(screen, game.small_font, detail, (panel.x + 16, panel.bottom - 122), t.TEXT, panel.width - 32)
    effect = f'All-era clicks & production: {multiplier:.2f}x' + (f' → {multiplier + .1:.2f}x' if owned < 3 else '')
    t.text(screen, game.small_font, effect, (panel.x + 16, panel.bottom - 94), t.SAGE, panel.width - 32)
    cost = state.get_machine_restoration_cost(era)
    label = 'Fully restored' if cost is None else f'Buy next · {cost} shards'
    t.button(screen, geometry['buy'], label, game.small_font,
             enabled=cost is not None and state.data_shards >= cost, primary=cost is not None and state.data_shards >= cost)
    t.button(screen, geometry['view'], 'View this era', game.small_font)
    note = ('Could not save progress. Close this window for details.' if game.last_save_error else
            'Collect or Rebirth for shards. Restorations survive Rebirth and Prestige.')
    t.text(screen, game.tiny_font, note, (margin, game.current_height - 30),
           t.DANGER if game.last_save_error else t.MUTED, game.current_width - margin * 2)
