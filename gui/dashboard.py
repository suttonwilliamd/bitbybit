"""Calm dashboard and shared shop geometry for drawing and hit-testing."""
import pygame
from constants import ERAS, get_all_generators, get_all_upgrades, format_number
from . import theme as t
from .research import research_button_rect
from .machines import draw_era_machine
from .transistors import draw_transistor_board

CARD_HEIGHT = 132
CARD_GAP = 10


def layout(width, height):
    side = min(320, max(248, width // 4))
    left = pygame.Rect(24, 148, side, height - 244)
    right = pygame.Rect(width - 24 - side, 148, side, height - 244)
    hero = pygame.Rect(left.right + 20, 108, right.x - left.right - 40, height - 264)
    return left, right, hero


def apply_layout(game):
    left, right, hero = layout(game.current_width, game.current_height)
    game.hardware_scroll_panel.rect = left
    game.upgrades_scroll_panel.rect = right
    game.hardware_toggle.rect = pygame.Rect(left.x, 108, left.width, 32)
    game.upgrades_toggle.rect = pygame.Rect(right.x, 108, right.width, 32)
    game.click_button.rect = pygame.Rect(hero.centerx - min(240, hero.width - 40) // 2,
                                         hero.bottom - 92, min(240, hero.width - 40), 46)
    game.settings_button.rect = pygame.Rect(game.current_width - 124, 24, 100, 38)
    game.stats_button.rect = pygame.Rect(game.current_width - 234, 24, 100, 38)
    game.delete_save_button.rect = pygame.Rect(game.current_width - 354, 24, 110, 38)
    reset_width = (hero.width - 16) // 3
    for i, button in enumerate((game.collect_shards_button, game.prestige_button, game.rebirth_button)):
        button.rect = pygame.Rect(hero.x + i * (reset_width + 8), hero.bottom + 12, reset_width, 36)
    if compact_machine_header(game):
        game.accumulator_click_rect = pygame.Rect(hero.x + 16, hero.y + 136, hero.width - 32,
                                                  hero.height - 236)
    else:
        game.accumulator_click_rect = pygame.Rect(hero.x + 24, hero.y + 180, hero.width - 48,
                                                  max(30, hero.height - 292))


def compact_machine_header(game):
    return game.state.current_era in (1, 2, 4) and game.current_height < 720


def shop_items(state, upgrades=False):
    if upgrades:
        result = [(key, definition, 'upgrade') for key, definition in get_all_upgrades().items()
                  if state.is_upgrade_unlocked(key)]
        result.sort(key=lambda item: (item[1].get('era') != state.current_era,
                                      -item[1].get('era', 4)))
        if state.total_data_shards or state.data_shards:
            result += [(key, definition, 'shard') for key, definition in state.data_shard_upgrades.items()]
        return result
    result = [(key, definition, 'generator') for key, definition in get_all_generators().items()
              if state.is_era_generator_unlocked(key)]
    # New technology first, then productive earlier machines, then other old stock.
    result.sort(key=lambda item: (
        0 if state.get_generator_era(item[0]) == state.current_era else
        1 if state.generators[item[0]]['count'] else 2,
        -state.get_generator_era(item[0])))
    return result


def viewport(panel):
    return pygame.Rect(panel.rect.x + 10, panel.rect.y + 52, panel.rect.width - 32, panel.rect.height - 60)


def card_geometry(panel, index):
    view = viewport(panel)
    card = pygame.Rect(view.x, view.y + index * (CARD_HEIGHT + CARD_GAP) - panel.scroll_offset,
                       view.width, CARD_HEIGHT)
    buy_one = pygame.Rect(card.right - 62, card.bottom - 42, 52, 30)
    buy_ten = pygame.Rect(card.right - 120, card.bottom - 42, 52, 30)
    return card, buy_one, buy_ten


def handle_shop_click(game, pos, upgrades=False):
    panel = game.upgrades_scroll_panel if upgrades else game.hardware_scroll_panel
    if panel.dragging or not viewport(panel).collidepoint(pos):
        return False
    for index, (key, definition, kind) in enumerate(shop_items(game.state, upgrades)):
        card, one, ten = card_geometry(panel, index)
        if one.collidepoint(pos):
            if kind == 'generator':
                game.buy_generator(key, 1)
            elif kind == 'shard':
                game.state.purchase_data_shard_upgrade(key)
            else:
                game.buy_upgrade(key)
            return True
        if kind == 'generator' and ten.collidepoint(pos):
            game.buy_generator(key, 10)
            return True
    return False


def draw_shop(game, upgrades=False):
    screen, state = game.screen, game.state
    panel = game.upgrades_scroll_panel if upgrades else game.hardware_scroll_panel
    toggle = game.upgrades_toggle if upgrades else game.hardware_toggle
    opened = game.upgrades_panel_open if upgrades else game.hardware_panel_open
    title = 'Upgrades' if upgrades else 'Hardware'
    t.text(screen, game.large_font, title, (toggle.rect.x, toggle.rect.y + 3))
    t.text(screen, game.small_font, '−' if opened else '+', (toggle.rect.right - 22, toggle.rect.y + 5), t.MUTED)
    if not opened:
        return
    items = shop_items(state, upgrades)
    panel.set_content_height(max(0, len(items) * (CARD_HEIGHT + CARD_GAP) - CARD_GAP))
    panel.scroll_to(panel.scroll_offset)
    t.panel(screen, panel.rect)
    caption = ('Improve your craft' if upgrades else
               'Earlier machines still work' if state.current_era > 0 else 'Build a little momentum')
    t.text(screen, game.small_font, caption,
           (panel.rect.x + 14, panel.rect.y + 16), t.MUTED, panel.rect.width - 28)
    view = viewport(panel)
    old_clip = screen.get_clip()
    screen.set_clip(view)
    for index, (key, definition, kind) in enumerate(items):
        card, one, ten = card_geometry(panel, index)
        if not card.colliderect(view):
            continue
        t.panel(screen, card, t.CARD)
        name = definition.get('name', key.replace('_', ' ').title())
        t.text(screen, game.medium_font, name, (card.x + 12, card.y + 10), t.TEXT, card.width - 24)
        if kind == 'generator':
            count = state.generators[key]['count']
            cost = state.get_generator_cost(key)
            production = state.get_generator_production(key)
            detail = f"{count} owned  ·  +{format_number(production)}/s"
            t.text(screen, game.small_font, detail, (card.x + 12, card.y + 39),
                   t.SAGE if count else t.MUTED, card.width - 24)
            source_era = state.get_generator_era(key)
            description = (ERAS[source_era]['name'] + ' · Still available'
                           if source_era < state.current_era else
                           definition.get('flavor', 'Steady progress, one step at a time.'))
            t.text(screen, game.small_font, description,
                   (card.x + 12, card.y + 61), t.MUTED, card.width - 24)
            t.button(screen, ten, '×10', game.small_font, game.can_afford(state.get_generator_cost(key, 10)))
            affordable = game.can_afford(cost)
        else:
            levels = state.data_shard_upgrades if kind == 'shard' else state.era_upgrades if key in state.era_upgrades else state.upgrades
            level = levels.get(key, {}).get('level', 0)
            maximum = definition.get('max_level', 1)
            cost = state.get_data_shard_upgrade_cost(key) if kind == 'shard' else state.get_upgrade_cost(key)
            t.text(screen, game.small_font, f'Level {level} / {maximum}', (card.x + 12, card.y + 39), t.AMBER)
            t.text(screen, game.small_font, definition.get('description', ''), (card.x + 12, card.y + 61), t.MUTED, card.width - 24)
            affordable = cost is not None and level < maximum and (state.data_shards >= cost if kind == 'shard' else game.can_afford(cost))
        t.text(screen, game.small_font, 'Maxed' if cost is None else format_number(cost),
               (card.x + 12, card.bottom - 40), t.TEXT, card.width - (138 if kind == 'generator' else 82))
        t.text(screen, game.tiny_font, 'shards' if kind == 'shard' else state.get_current_currency().lower(),
               (card.x + 12, card.bottom - 22), t.MUTED)
        t.button(screen, one, '×1' if kind == 'generator' else 'Buy', game.small_font, affordable, affordable)
    if not items:
        t.text(screen, game.small_font, 'New discoveries appear as you grow.', (view.x + 4, view.y + 12), t.MUTED, view.width - 8)
    screen.set_clip(old_clip)
    track, thumb = panel.get_scrollbar_geometry()
    if track:
        pygame.draw.rect(screen, t.BORDER, track, border_radius=5)
        pygame.draw.rect(screen, t.MUTED, thumb, border_radius=5)


def draw_machine(screen, rect, era, amount, animation=None):
    """Presentation-only era illustrations; motion never changes earnings."""
    if era in (1, 2):
        draw_era_machine(screen, rect, era, amount, animation)
    elif era == 4:
        draw_transistor_board(screen, rect, amount, animation)
    elif era == 0:
        t.panel(screen, rect, (44, 46, 39))
        inner = rect.inflate(-24, -16)
        active = int(amount) % 40
        radius = max(4, min(10, inner.height // 12))
        for row in range(4):
            y = inner.y + (row + 1) * inner.height // 5
            pygame.draw.line(screen, (116, 117, 94), (inner.x, y), (inner.right, y), 2)
            for col in range(10):
                x = inner.x + 12 + col * (inner.width - 24) // 9
                color = t.SAGE if row * 10 + col < active else t.AMBER
                pygame.draw.ellipse(screen, color, (x - radius, y - radius, radius * 2, radius * 2))
    elif era == 3:
        for i in range(5):
            x = rect.x + (i + 1) * rect.width // 6
            body = pygame.Rect(x - 16, rect.y + 10, 32, max(30, rect.height - 24))
            t.panel(screen, body, t.CARD)
            pygame.draw.line(screen, t.AMBER, (x, body.y + 8), (x, body.bottom - 8), 3)
    else:
        chip = pygame.Rect(rect.centerx - 45, rect.centery - 30, 90, 60)
        for i in range(5):
            y = chip.y + 8 + i * 11
            pygame.draw.line(screen, t.BORDER, (rect.x + 12, y), (rect.right - 12, y), 2)
            pygame.draw.circle(screen, t.SAGE, (rect.x + 12, y), 3)
            pygame.draw.circle(screen, t.SAGE, (rect.right - 12, y), 3)
        t.panel(screen, chip, t.SAGE_DARK)
        pygame.draw.rect(screen, t.SAGE, chip.inflate(-30, -24), 1, border_radius=4)


def draw(game):
    screen, state = game.screen, game.state
    apply_layout(game)
    screen.fill(t.BACKGROUND)
    if state.visual_settings.get('binary_rain') and not game.reduced_motion_mode:
        rain = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        game.binary_rain.draw(rain)
        rain.set_alpha(20)
        screen.blit(rain, (0, 0))
    left, right, hero = layout(game.current_width, game.current_height)
    t.text(screen, game.title_font, 'bit by bit', (24, 20))
    t.text(screen, game.small_font, 'A quiet journey through computing', (25, 56), t.MUTED)
    t.button(screen, game.stats_button.rect, 'Statistics', game.small_font)
    t.button(screen, game.settings_button.rect, 'Settings', game.small_font)
    if game.cheat_mode:
        t.button(screen, game.delete_save_button.rect, 'Delete save', game.small_font)
    pygame.draw.line(screen, t.BORDER, (24, 88), (game.current_width - 24, 88))
    t.panel(screen, hero)
    era_name = state.get_era_info().get('name', state.get_hardware_generation_info()[0]['name'])
    label = game.small_font.render(era_name.upper(), True, t.SAGE)
    screen.blit(label, label.get_rect(center=(hero.centerx, hero.y + 28)))
    compact = compact_machine_header(game)
    counter_font = game.compact_counter_font if compact else game.bit_counter_font
    amount = counter_font.render(format_number(state.get_current_currency_value()), True, t.TEXT)
    screen.blit(amount, amount.get_rect(center=(hero.centerx, hero.y + (68 if compact else 90))))
    label = game.medium_font.render(state.get_current_currency().lower(), True, t.MUTED)
    screen.blit(label, label.get_rect(center=(hero.centerx, hero.y + (97 if compact else 126))))
    rate = game.small_font.render(f'+{format_number(state.get_production_rate())} per second', True, t.SAGE)
    screen.blit(rate, rate.get_rect(center=(hero.centerx, hero.y + (119 if compact else 157))))
    draw_machine(screen, game.accumulator_click_rect, state.current_era, state.get_current_currency_value(),
                 game.machine_animation)
    t.button(screen, game.click_button.rect, f'Count +{format_number(state.get_click_power())}', game.medium_font, primary=True)
    hint = game.small_font.render('Small steps. Steady progress.', True, t.MUTED)
    screen.blit(hint, hint.get_rect(center=(hero.centerx, hero.bottom - 27)))
    for button, title, ready in (
        (game.collect_shards_button, f'Collect +{state.get_data_shards_earned()}' if state.can_collect_data_shards()
         else f'Shards · {format_number(state.data_shards)}', state.can_collect_data_shards()),
        (game.prestige_button, 'Prestige', state.can_prestige()),
        (game.rebirth_button, 'Rebirth', state.can_rebirth(game.bit_grid)),
    ):
        t.button(screen, button.rect, title, game.small_font, ready)
    draw_shop(game)
    draw_shop(game, True)
    footer = research_button_rect(game.current_width, game.current_height)
    t.panel(screen, footer)
    project = next((p for p in state.get_research_projects() if not p['complete']), None)
    ready = any(p['ready'] for p in state.get_research_projects()) or state.can_advance_era()
    if project:
        goal = f"Next discovery · {project['name']}"
        detail = f"{format_number(project['earned'])} / {format_number(project['target'])} earned"
        fraction = project['earned'] / project['target']
    else:
        goal, detail, fraction = 'All research complete', 'Keep growing your computing legacy.', 1
    t.text(screen, game.medium_font, goal, (footer.x + 16, footer.y + 10), t.TEXT, footer.width - 360)
    t.text(screen, game.small_font, detail, (footer.x + 16, footer.y + 34), t.MUTED, footer.width - 360)
    t.progress(screen, pygame.Rect(footer.x + 16, footer.bottom - 9, footer.width - 200, 3), fraction)
    t.button(screen, pygame.Rect(footer.right - 168, footer.y + 12, 152, 38),
             'Research ready [R]' if ready else 'Research [R]', game.small_font, primary=ready)
    if game.last_save_error or game.last_load_error:
        t.text(screen, game.small_font, game.last_save_error or game.last_load_error,
               (left.x, 92), t.DANGER, game.current_width - 48)
    if game.save_success_message and not (game.last_save_error or game.last_load_error):
        if pygame.time.get_ticks() - state.last_save_time < 3000:
            t.text(screen, game.small_font, 'Progress saved', (game.current_width // 2 - 56, 40), t.MUTED)
    if state.visual_settings.get('particle_effects') and not game.reduced_motion_mode:
        from .effects import draw_effects
        draw_effects(screen, game.particles, game.floating_texts)
    if state.visual_settings.get('crt_effects'):
        from .effects import draw_crt_overlay
        draw_crt_overlay(screen, game.current_width, game.current_height)
    draw_tooltip(game)


def draw_tooltip(game):
    """Full descriptions stay accessible when narrow cards truncate them."""
    mouse = pygame.mouse.get_pos()
    for upgrades, opened, panel in ((False, game.hardware_panel_open, game.hardware_scroll_panel),
                                     (True, game.upgrades_panel_open, game.upgrades_scroll_panel)):
        if not opened or not viewport(panel).collidepoint(mouse):
            continue
        for index, (key, definition, kind) in enumerate(shop_items(game.state, upgrades)):
            card, _, _ = card_geometry(panel, index)
            if not card.collidepoint(mouse) or mouse[1] >= card.bottom - 46:
                continue
            _, _, hero = layout(game.current_width, game.current_height)
            width = hero.width - 32
            lines = []
            for paragraph in (definition.get('name', key.replace('_', ' ').title()),
                              definition.get('description') or definition.get('flavor') or 'Steady progress, one step at a time.'):
                line = ''
                for word in paragraph.split():
                    if game.small_font.size(line + ' ' + word)[0] > width - 32:
                        lines.append(line)
                        line = word
                    else:
                        line = (line + ' ' + word).strip()
                lines.append(line)
            tip = pygame.Rect(hero.x + 16, hero.y + 180, width, 24 + 23 * len(lines))
            t.panel(game.screen, tip, t.CARD)
            for i, line in enumerate(lines):
                t.text(game.screen, game.small_font, line, (tip.x + 16, tip.y + 12 + i * 23), t.TEXT if i == 0 else t.MUTED)
            return
