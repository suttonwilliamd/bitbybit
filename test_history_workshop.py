"""Historical views are not progression, and previews never purchase upgrades."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pygame
from constants import CONFIG, ERAS, get_all_generators
from game_state import GameState
from machine_progression import technology_era
from gui import BitByBitGame, dashboard, theme
from gui.machines import MachineAnimation
from gui.workshop import history_button_rect, present_button_rect, workshop_layout


class HistoryWorkshopTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.config = patch.dict(CONFIG, SAVE_FILE=str(Path(self.directory.name) / 'save.json'))
        self.config.start()
        self.addCleanup(self.directory.cleanup)
        self.addCleanup(self.config.stop)
        self.addCleanup(theme.configure)
        self.game = BitByBitGame()
        self.game.showing_tutorial = False
        self.state = self.game.state
        self.state.current_era = 6
        self.state.binary_invented = True
        self.state.bits = self.state.total_bits_earned = 10**15
        self.state.data_shards = 10**6
        self.state.unlocked_hardware_categories = list({d.get('category') for d in get_all_generators().values()})
        for owned in self.state.generators.values():
            owned['count'] = 2
        pygame.event.clear()

    def click(self, rect):
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center))
        self.game.handle_events()

    def key(self, key):
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
        self.game.handle_events()

    def test_only_matching_era_stock_including_quantum_and_cosmic_categories(self):
        for era in ERAS:
            for upgrades in (False, True):
                items = dashboard.shop_items(self.state, upgrades, era)
                self.assertTrue(items)
                self.assertTrue(all(technology_era(d) == era and kind != 'shard' for _, d, kind in items))
        self.assertIn('quantum_processor', [k for k, _, _ in dashboard.shop_items(self.state, era=5)])
        self.assertIn('singularity_core', [k for k, _, _ in dashboard.shop_items(self.state)])
        self.assertNotIn('pebble', [k for k, _, _ in dashboard.shop_items(self.state)])
        self.assertNotIn('quantum_processor', [k for k, _, _ in dashboard.shop_items(self.state, era=4)])
        # Catalogue grouping must not reprice technology or change model eligibility.
        self.assertEqual(self.state.get_generator_era('quantum_processor'), 4)

    def test_browsing_and_all_preview_modes_do_not_mutate_or_save_progress(self):
        before = copy.deepcopy(self.state.__dict__)
        with patch.object(self.game, 'save_game') as save:
            self.key(pygame.K_h)
            self.assertTrue(self.game.showing_workshop)
            for era in ERAS:
                geometry = workshop_layout(self.game.current_width, self.game.current_height)
                self.click(geometry['rows'][era])
                for mode in range(3):
                    self.click(geometry['modes'][mode])
                    self.game.draw()
            self.key(pygame.K_ESCAPE)
            self.assertFalse(self.game.showing_workshop)
            save.assert_not_called()
        self.assertEqual(self.state.__dict__, before)

    def test_selecting_history_switches_machine_both_shops_and_resets_scrolling(self):
        before = copy.deepcopy(self.state.__dict__)
        rate = self.state.get_production_rate()
        for size in ((960, 640), (1200, 800), (1600, 900)):
            self.game.handle_window_resize(*size)
            self.game.draw()
            self.click(history_button_rect(*size))
            geometry = workshop_layout(*size)
            self.click(geometry['rows'][0])
            self.click(geometry['view'])
            self.assertFalse(self.game.showing_workshop)
            self.assertEqual(dashboard.viewed_era(self.game), 0)
            for panel in (self.game.hardware_scroll_panel, self.game.upgrades_scroll_panel):
                self.assertEqual(panel.scroll_offset, 0)
                self.assertFalse(panel.dragging)
            with patch.object(dashboard, 'draw_machine', wraps=dashboard.draw_machine) as draw:
                self.game.draw()
                self.assertEqual(draw.call_args.args[2], 0)
                self.assertEqual(draw.call_args.args[3], self.state.bits)
            for upgrades in (False, True):
                self.assertTrue(all(technology_era(d) == 0 for _, d, _ in
                                    dashboard.shop_items(self.state, upgrades, dashboard.viewed_era(self.game))))
            self.assertEqual(self.state.get_production_rate(), rate)
            self.assertEqual(self.state.__dict__, before)
            self.click(present_button_rect(*size))
            self.assertIsNone(self.game.viewed_era)
            self.assertEqual(dashboard.viewed_era(self.game), 6)

    def test_historical_purchases_use_live_currency_with_matching_painted_geometry(self):
        self.state.pebbles = 123
        for size in ((960, 640), (1200, 800)):
            self.game.handle_window_resize(*size)
            for era in ERAS:
                self.game._select_era_view(era)
                for upgrades in (False, True):
                    self.game.draw()
                    items = dashboard.shop_items(self.state, upgrades, era)
                    index = len(items) - 1
                    key, _, _ = items[index]
                    panel = self.game.upgrades_scroll_panel if upgrades else self.game.hardware_scroll_panel
                    panel.scroll_to(index * (dashboard.CARD_HEIGHT + dashboard.CARD_GAP))
                    self.game.draw()
                    _, button, _ = dashboard.card_geometry(panel, index)
                    self.assertTrue(dashboard.viewport(panel).contains(button))
                    levels = self.state.era_upgrades if key in self.state.era_upgrades else self.state.upgrades
                    before = levels[key]['level'] if upgrades else self.state.generators[key]['count']
                    bits = self.state.bits
                    self.click(button)
                    after = levels[key]['level'] if upgrades else self.state.generators[key]['count']
                    self.assertEqual(after, before + 1)
                    self.assertLess(self.state.bits, bits)
                    self.assertEqual(self.state.pebbles, 123)
                    self.assertEqual(self.state.current_era, 6)

    def test_future_history_and_restoration_are_locked_without_unlocking_anything(self):
        self.game.state = self.state = GameState()
        self.state.data_shards = 10**6
        before = copy.deepcopy(self.state.__dict__)
        self.key(pygame.K_h)
        self.click(workshop_layout(self.game.current_width, self.game.current_height)['rows'][6])
        self.assertEqual(self.game.workshop_era, 0)
        self.assertFalse(self.game._select_era_view(6))
        self.assertFalse(self.state.purchase_machine_restoration(6))
        self.assertEqual(dashboard.shop_items(self.state, era=6), [])
        self.assertEqual(self.state.__dict__, before)

    def test_era_appropriate_layout_and_animation_follow_view_not_progression(self):
        self.game.handle_window_resize(960, 640)
        self.game._select_era_view(0)
        self.assertFalse(dashboard.compact_machine_header(self.game))
        self.game._select_era_view(1)
        self.assertTrue(dashboard.compact_machine_header(self.game))
        phase = self.game.machine_animation.phase
        self.game.update(.1)
        self.assertGreater(self.game.machine_animation.phase, phase)
        self.game.reduced_motion_mode = True
        phase = self.game.machine_animation.phase
        self.game.update(.1)
        self.assertEqual(self.game.machine_animation.phase, phase)
        # Hardware generations after historical chapters retain an animated Cosmic view.
        self.state.current_era = 9
        self.game._select_era_view(None)
        self.assertEqual(dashboard.viewed_era(self.game), 6)
        self.game.reduced_motion_mode = False
        self.game.update(.1)
        self.assertGreater(self.game.machine_animation.phase, phase)

    def test_one_permanent_additive_bonus_per_rank_with_bounded_costs(self):
        production, click = self.state.get_production_rate(), self.state.get_click_power()
        shards = self.state.data_shards
        spent = 0
        for era in ERAS:
            for level in range(3):
                expected = (era + 1) * 8 ** level
                self.assertEqual(self.state.get_machine_restoration_cost(era), expected)
                self.assertTrue(self.state.purchase_machine_restoration(era))
                spent += expected
                self.assertEqual(self.state.get_machine_level(era), level + 1)
                multiplier = 1 + (era * 3 + level + 1) * .1
                self.assertAlmostEqual(self.state.get_production_rate(), production * multiplier, delta=production * 1e-12)
                self.assertAlmostEqual(self.state.get_click_power(), click * multiplier)
            self.assertIsNone(self.state.get_machine_restoration_cost(era))
            self.assertFalse(self.state.purchase_machine_restoration(era))
        self.assertEqual(spent, 2044)
        self.assertEqual(self.state.data_shards, shards - spent)
        self.assertAlmostEqual(self.state.get_workshop_multiplier(), 3.1)

    def test_bonus_applies_once_in_every_era_alongside_research_and_prestige(self):
        self.state.binary_efficiency = 24
        self.state.prestige_count = 3
        for era in ERAS:
            self.state.current_era = era
            self.state.machine_restorations['0'] = 0
            rate, click = self.state.get_production_rate(), self.state.get_click_power()
            sources = {key: self.state.get_generator_production(key) for key in self.state.generators}
            self.assertTrue(self.state.purchase_machine_restoration(0))
            self.assertAlmostEqual(self.state.get_production_rate(), rate * 1.1, delta=rate * 1e-12)
            self.assertAlmostEqual(self.state.get_click_power(), click * 1.1)
            for key, output in sources.items():
                self.assertAlmostEqual(self.state.get_generator_production(key), output * 1.1, delta=max(1, output) * 1e-12)

    def test_locked_or_maxed_purchase_does_not_spend_and_preview_never_grants_bonus(self):
        self.state.data_shards = 0
        self.key(pygame.K_w)
        geometry = workshop_layout(self.game.current_width, self.game.current_height)
        self.click(geometry['modes'][2])
        before = copy.deepcopy(self.state.__dict__)
        self.click(geometry['buy'])
        self.assertEqual(self.state.__dict__, before)
        for invalid in (-1, 7, '0', None, True, 1.0):
            self.assertFalse(self.state.purchase_machine_restoration(invalid))
        self.assertEqual(self.state.get_workshop_multiplier(), 1)

    def test_purchase_saves_immediately_and_shows_newly_owned_art(self):
        self.key(pygame.K_h)
        geometry = workshop_layout(self.game.current_width, self.game.current_height)
        self.click(geometry['modes'][2])
        with patch.object(self.game, 'save_game', wraps=self.game.save_game) as save:
            self.click(geometry['buy'])
            save.assert_called_once_with()
        self.assertEqual(self.game.workshop_preview, 0)
        self.assertEqual(self.state.get_machine_level(6), 1)
        self.assertIsNone(self.game.last_save_error)
        with patch('gui.time.time', return_value=0):
            loaded = BitByBitGame()
        self.assertEqual(loaded.state.machine_restorations, self.state.machine_restorations)

    def test_history_and_restorations_survive_both_reset_tiers(self):
        self.assertTrue(self.state.purchase_machine_restoration(6))
        ranks = copy.deepcopy(self.state.machine_restorations)
        self.assertTrue(self.state.perform_rebirth())
        self.assertEqual(self.state.get_history_limit(), 6)
        self.assertEqual(self.state.machine_restorations, ranks)
        self.state.total_bits_earned = 10**6
        self.assertTrue(self.state.perform_prestige())
        self.assertEqual(self.state.current_era, 0)
        self.assertEqual(self.state.get_history_limit(), 6)
        self.assertEqual(self.state.machine_restorations, ranks)
        self.assertEqual(self.state.data_shards, 0)
        self.assertAlmostEqual(self.state.get_workshop_multiplier(), 1.1)
        self.assertEqual(dashboard.shop_items(self.state, era=6), [])
        self.assertTrue(self.game._select_era_view(6))
        # Historic access is not economic access to future-cycle hardware.
        self.assertFalse(self.state.purchase_generator('quantum_processor'))

    def test_old_saves_infer_history_without_inventing_free_restorations(self):
        self.state.load_machine_progression({})
        self.assertEqual(self.state.get_history_limit(), 6)
        self.assertEqual(self.state.get_workshop_multiplier(), 1)
        self.state.load_machine_progression(dict(highest_era='bad', machine_restorations={'0': -9, '1': 99, '2': '3', '3': True, 'future': 1000}))
        self.assertEqual(self.state.get_machine_level(0), 0)
        self.assertEqual(self.state.get_machine_level(1), 3)
        self.assertEqual(self.state.get_machine_level(2), 0)
        self.assertEqual(self.state.get_machine_level(3), 0)
        self.assertNotIn('future', self.state.machine_restorations)
        self.state.load_machine_progression(dict(machine_restorations=None))
        self.assertEqual(self.state.get_workshop_multiplier(), 1)

    def test_offline_income_and_backup_restore_include_real_restoration_bonus(self):
        self.assertTrue(self.state.purchase_machine_restoration(0))
        rate, bits = self.state.get_production_rate(), self.state.bits
        with patch('gui.time.time', return_value=1000):
            self.game.save_game()
            self.game.save_game()
        with patch('gui.time.time', return_value=1060):
            loaded = BitByBitGame()
        self.assertAlmostEqual(loaded.state.bits, bits + rate * 60 * .75)
        Path(CONFIG['SAVE_FILE']).write_text('{broken', encoding='utf-8')
        with patch('gui.time.time', return_value=1000):
            backup = BitByBitGame()
        self.assertEqual(backup.last_load_error, 'Restored from backup')
        self.assertEqual(backup.state.get_machine_level(0), 1)
        self.assertEqual(backup.state.get_history_limit(), 6)
        self.assertEqual(backup.state.get_production_rate(), rate)

    def test_gallery_geometry_and_journal_return_route_at_all_supported_sizes(self):
        for size in ((960, 640), (1024, 768), (1200, 800), (1600, 900)):
            self.game.handle_window_resize(*size)
            geometry = workshop_layout(*size)
            full = pygame.Rect((0, 0), size)
            for key in ('panel', 'preview', 'buy', 'view', 'close'):
                self.assertTrue(full.contains(geometry[key]))
            for key in ('buy', 'view', 'preview'):
                self.assertTrue(geometry['panel'].contains(geometry[key]))
            for mode in geometry['modes']:
                self.assertTrue(geometry['panel'].contains(mode))
                self.assertFalse(mode.colliderect(geometry['preview']))
            self.assertFalse(geometry['buy'].colliderect(geometry['view']))
            self.game.showing_research = True
            self.click(history_button_rect(*size, journal=True))
            self.assertTrue(self.game.showing_workshop)
            self.assertFalse(self.game.showing_research)
            for contrast in (False, True):
                self.game.high_contrast_mode = contrast
                self.game.draw()
            self.key(pygame.K_ESCAPE)
            self.assertTrue(self.game.showing_research)
            self.assertFalse(self.game.showing_workshop)
            self.game.showing_research = False

    def test_other_modals_block_history_and_escape_returns_to_present(self):
        for attribute in ('showing_settings', 'showing_statistics', 'showing_rebirth_confirmation',
                          'showing_prestige_confirmation', 'showing_tutorial'):
            setattr(self.game, attribute, True)
            self.key(pygame.K_h)
            self.assertFalse(self.game.showing_workshop)
            setattr(self.game, attribute, False)
        self.game._select_era_view(0)
        self.key(pygame.K_ESCAPE)
        self.assertIsNone(self.game.viewed_era)

    def test_each_art_rank_is_distinct_pure_theme_safe_and_full_art_unchanged(self):
        animation = MachineAnimation(phase=7.4)
        before = copy.deepcopy(animation)
        for size in ((464, 244), (344, 140)):
            for contrast in (False, True):
                theme.configure(contrast)
                for era in ERAS:
                    images = []
                    for level in range(4):
                        screen = pygame.Surface(size)
                        screen.fill(theme.BACKGROUND)
                        dashboard.draw_machine(screen, screen.get_rect(), era, 173, animation, level)
                        images.append(pygame.image.tostring(screen, 'RGB'))
                    self.assertEqual(len(set(images)), 4, (size, contrast, era))
                    screen.fill(theme.BACKGROUND)
                    dashboard.draw_machine(screen, screen.get_rect(), era, 173, animation)
                    self.assertEqual(pygame.image.tostring(screen, 'RGB'), images[3])
                    screen.fill(theme.BACKGROUND)
                    dashboard.draw_machine(screen, screen.get_rect(), era, 174, animation, 0)
                    self.assertNotEqual(pygame.image.tostring(screen, 'RGB'), images[0])
        self.assertEqual(animation, before)


if __name__ == '__main__':
    unittest.main()
