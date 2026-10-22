"""Headless regression tests; never touch the player's save."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import pygame
from game_state import GameState
from constants import CONFIG, ERA_UPGRADES
from gui import BitByBitGame


class GameplayTests(unittest.TestCase):
    def test_currency_and_costs(self):
        s = GameState()
        s.add_idle_currency(100)
        self.assertEqual(s.pebbles, 100)
        self.assertEqual(s.bits, 0)
        self.assertEqual(s.get_generator_cost('pebble'), s.get_era_generator_cost('pebble'))
        self.assertTrue(s.purchase_generator('pebble'))
        self.assertFalse(s.purchase_generator('pebble', 1.5))
        self.assertFalse(s.purchase_generator('lever'))

    def test_upgrade_caps_and_click_upgrade_not_production(self):
        s = GameState()
        s.pebbles = 10**15
        s.generators['pebble']['count'] = 1
        rate = s.get_production_rate()
        for _ in range(ERA_UPGRADES['clay_inscriptions']['max_level']):
            self.assertTrue(s.purchase_upgrade('clay_inscriptions'))
        self.assertFalse(s.purchase_upgrade('clay_inscriptions'))
        self.assertEqual(s.get_production_rate(), rate)
        self.assertFalse(s.purchase_upgrade('gear_lubrication'))

    def test_shard_resets_and_reduced_threshold(self):
        s = GameState()
        s.binary_invented = True
        s.total_bits_earned = 10000
        self.assertEqual(s.collect_data_shards(), 1)
        self.assertEqual(s.collect_data_shards(), 0)
        self.assertTrue(s.perform_rebirth())
        self.assertEqual(s.last_collect_bits, 0)
        s.data_shard_upgrades['quick_collect'] = {'level': 1, 'effect_per_level': 10}
        s.total_bits_earned = 9000
        self.assertEqual(s.collect_data_shards(), 1)
        self.assertFalse(s.purchase_data_shard_upgrade('missing'))

    def test_research_roadmap(self):
        s = GameState()
        self.assertFalse(s.complete_research('missing'))
        self.assertFalse(s.complete_research('define_bit'))
        s.pebbles = s.total_pebbles_earned = 500
        self.assertFalse(s.can_advance_era())
        self.assertTrue(s.complete_research('define_bit'))
        self.assertEqual(s.bits, 5)
        self.assertFalse(s.complete_research('define_bit'))
        s.total_bits_earned = s.bits = 50000
        self.assertFalse(s.complete_research('boolean_algebra'))
        self.assertTrue(s.advance_era())
        self.assertTrue(s.complete_research('boolean_algebra'))
        self.assertTrue(s.advance_era())
        s.total_bits_earned = s.bits = 5000000
        self.assertTrue(s.complete_research('logic_gates'))
        self.assertTrue(s.advance_era())
        s.total_bits_earned = s.bits = 8000000
        self.assertTrue(s.complete_research('stored_program'))
        s.total_bits_earned = s.bits = 50000000
        self.assertTrue(s.advance_era())
        self.assertTrue(s.complete_research('integrated_circuits'))
        self.assertEqual(s.binary_efficiency, 24)
        self.assertTrue(all(p['complete'] for p in s.get_research_projects()))
        s.perform_prestige()
        self.assertTrue(all(p['complete'] for p in s.get_research_projects()))
        self.assertEqual(s.binary_efficiency, 24)
        s.current_era = 4
        s.total_bits_earned = 10**12
        s.unlocked_hardware_categories = ['cpu', 'ram']
        self.assertTrue(s.advance_era())
        self.assertTrue(s.is_hardware_category_unlocked('cpu'))
        self.assertTrue(s.advance_era())
        self.assertTrue(s.is_hardware_category_unlocked('ram'))

    def test_research_gui_events(self):
        from gui.research import research_layout
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(CONFIG, SAVE_FILE=str(Path(directory) / 'save.json')):
                game = BitByBitGame()
                game.showing_tutorial = False
                game.state.pebbles = game.state.total_pebbles_earned = 500
                pygame.event.clear()
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
                game.handle_events()
                self.assertTrue(game.showing_research)
                game.draw()
                _, buttons, _ = research_layout(game.current_width, game.current_height)
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                     button=1, pos=buttons[0].center))
                game.handle_events()
                self.assertTrue(game.state.binary_invented)
                restored = BitByBitGame()
                self.assertTrue(restored.state.binary_invented)
                game.state.current_era = 4
                game.state.bits = game.state.total_bits_earned = 50000000
                game.state.boolean_algebra_invented = True
                for project in ('boolean_algebra', 'logic_gates', 'stored_program'):
                    game.state.prestige_upgrades[project] = {'purchased': True}
                self.assertTrue(game.state.complete_research('integrated_circuits'))
                game.save_game()
                restored = BitByBitGame()
                self.assertTrue(restored.state.prestige_upgrades['integrated_circuits']['purchased'])
                self.assertEqual(restored.state.binary_efficiency, game.state.binary_efficiency)
                for size in ((1200, 800), (1024, 768), (800, 600)):
                    game.handle_window_resize(*size)
                    game.draw()
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
                game.handle_events()
                self.assertFalse(game.showing_research)
                for era in range(7):
                    game.state.current_era = era
                    game.draw()

    def test_gui_save_offline_and_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'save.json')
            with patch.dict(CONFIG, SAVE_FILE=path):
                game = BitByBitGame()
                game.showing_tutorial = False
                game.state.pebbles = 1000
                game.state.total_pebbles_earned = 2000
                game.state.generators['pebble']['count'] = 1
                game.update(1)
                self.assertEqual(game.state.bits, 0)
                game.state.perform_define_bit()
                game.state.purchase_upgrade('clay_inscriptions')
                with patch('gui.time.time', return_value=1000):
                    game.save_game()
                self.assertIsNone(game.last_save_error)
                with patch('gui.time.time', return_value=1060):
                    loaded = BitByBitGame()
                self.assertTrue(loaded.state.binary_invented)
                self.assertEqual(loaded.state.total_pebbles_earned, game.state.total_pebbles_earned)
                self.assertGreater(loaded.state.bits, game.state.bits)
                loaded.draw()
                # Back up the full state, then corrupt main save.
                loaded.save_game()
                Path(path).write_text('{broken')
                recovered = BitByBitGame()
                self.assertTrue(recovered.state.binary_invented)
                self.assertEqual(recovered.last_load_error, 'Restored from backup')
                recovered.draw()
                # Legacy tick clocks must never produce offline currency.
                data = json.loads(Path(path + '.backup').read_text())
                data.pop('clock')
                Path(path).write_text(json.dumps(data))
                legacy = BitByBitGame()
                self.assertEqual(legacy.state.bits, data['state']['bits'])


if __name__ == '__main__':
    unittest.main()
