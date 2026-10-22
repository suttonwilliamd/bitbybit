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
