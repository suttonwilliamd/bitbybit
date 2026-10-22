"""Historical machines are accumulated, not retired. All saves are temporary."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pygame
from constants import CONFIG, ERAS, ERA_UPGRADES
from game_state import GameState
from gui import BitByBitGame
from gui.dashboard import shop_items, card_geometry, CARD_HEIGHT, CARD_GAP


class EraProgressionTests(unittest.TestCase):
    def test_every_advance_preserves_all_owned_income_balance_and_clicks(self):
        state = GameState()
        state.binary_invented = True
        state.binary_efficiency = 2
        for era in range(6):
            state.current_era = era
            starter = ('pebble', 'lever', 'relay', 'triode', 'cpu_core', 'rng')[era]
            state.generators[starter] = {'count': 3, 'total_bought': 3}
            if era < 4:
                key = ('clay_inscriptions', 'precision_crafting', 'card_punching', 'tube_replacement')[era]
                state.era_upgrades[key]['level'] = 2
            state.bits = state.total_bits_earned = ERAS[era + 1]['unlock_bits']
            before = (state.get_production_rate(), state.get_click_power(), state.bits,
                      copy.deepcopy(state.generators))
            self.assertGreater(before[0], 0)
            self.assertTrue(state.advance_era())
            self.assertEqual(state.get_production_rate(), before[0])
            self.assertEqual(state.get_click_power(), before[1])
            self.assertEqual(state.bits, before[2])
            self.assertEqual(state.generators, before[3])
            state.add_idle_currency(state.get_production_rate())
            self.assertGreater(state.bits, before[2])

    def test_mixed_families_keep_own_bonuses_and_global_bonus_applies_once(self):
        state = GameState()
        state.current_era = 4
        state.binary_efficiency = 4
        state.prestige_count = 2
        for key in ('pebble', 'lever', 'relay', 'triode', 'cpu_core', 'rng'):
            state.generators[key]['count'] = 2
        state.era_upgrades['abacus_mastery']['level'] = 1
        state.era_upgrades['gear_lubrication']['level'] = 2
        state.upgrades['overclock']['level'] = 1
        state.upgrades['entropy_amplification']['level'] = 2
        global_bonus = 4 * 1.2 * CONFIG['UPGRADES']['entropy_amplification']['effect'] ** 2
        expected = {
            'pebble': 2 * ERA_UPGRADES['abacus_mastery']['effect'],
            'lever': 200 * ERA_UPGRADES['gear_lubrication']['effect'] ** 2,
            'relay': 10000, 'triode': 1000000,
            'cpu_core': 10 * CONFIG['HARDWARE_UPGRADES']['overclock']['effect'], 'rng': 2,
        }
        for key, base in expected.items():
            self.assertAlmostEqual(state.get_generator_production(key), base * global_bonus)
        self.assertAlmostEqual(state.get_production_rate(), sum(expected.values()) * global_bonus)

    def test_define_bit_keeps_old_unlocks_and_owned_income(self):
        state = GameState()
        state.generators['tally_stick']['count'] = 1
        state.total_pebbles_earned = 1000
        state.pebbles = 1
        before = state.get_production_rate()
        self.assertTrue(state.perform_define_bit())
        self.assertEqual(state.bits, 0)
        self.assertEqual(state.get_production_rate(), before * 2)
        self.assertTrue(state.is_era_generator_unlocked('clay_tablet'))
        state.current_era = 3
        state.total_pebbles_earned = state.total_bits_earned = 0
        self.assertTrue(state.is_era_generator_unlocked('tally_stick'))
        self.assertGreater(state.get_generator_production('tally_stick'), 0)

    def test_past_machines_and_bulk_purchases_use_only_current_currency(self):
        state = GameState()
        state.current_era = 3
        state.bits = state.total_bits_earned = 10**9
        state.pebbles = 123
        for key in ('pebble', 'lever', 'relay'):
            cost = state.get_generator_cost(key, 10)
            before = state.bits
            self.assertTrue(state.purchase_generator(key, 10))
            self.assertEqual(state.bits, before - cost)
            self.assertEqual(state.generators[key]['count'], 10)
            self.assertEqual(state.pebbles, 123)
        self.assertFalse(state.purchase_generator('cpu_core'))

    def test_prior_upgrades_remain_buyable_and_benefit_their_machines(self):
        state = GameState()
        state.current_era = 2
        state.bits = state.total_bits_earned = 10**8
        state.generators['lever']['count'] = 1
        before = state.get_production_rate()
        self.assertTrue(state.is_upgrade_unlocked('gear_lubrication'))
        self.assertTrue(state.purchase_upgrade('gear_lubrication'))
        self.assertGreater(state.get_production_rate(), before)
        click = state.get_click_power()
        self.assertTrue(state.purchase_upgrade('clay_inscriptions'))
        self.assertGreater(state.get_click_power(), click)
        self.assertFalse(state.purchase_upgrade('tube_replacement'))
        self.assertFalse(state.purchase_upgrade('overclock'))

    def test_future_and_unknown_machines_cannot_generate_or_be_bought(self):
        state = GameState()
        state.pebbles = state.total_pebbles_earned = 10**15
        for key in ('lever', 'relay', 'triode', 'cpu_core', 'rng'):
            state.generators[key]['count'] = 1
            self.assertEqual(state.get_generator_production(key), 0)
            self.assertFalse(state.is_era_generator_unlocked(key))
            self.assertFalse(state.purchase_generator(key))
        self.assertEqual(state.get_generator_production('missing'), 0)
        self.assertEqual(state.get_production_rate(), 0)

    def test_shop_shows_current_tech_and_keeps_old_stock_in_history(self):
        state = GameState()
        state.current_era = 2
        state.total_bits_earned = 50000
        state.generators['pebble']['count'] = 2
        keys = [key for key, _, _ in shop_items(state)]
        self.assertEqual(keys[0], 'relay')
        self.assertNotIn('pebble', keys)
        self.assertNotIn('lever', keys)
        self.assertNotIn('triode', keys)
        self.assertIn('pebble', [key for key, _, _ in shop_items(state, era=0)])
        self.assertIn('lever', [key for key, _, _ in shop_items(state, era=1)])
        upgrades = [key for key, _, _ in shop_items(state, True)]
        self.assertTrue(all(ERA_UPGRADES[key]['era'] == 2 for key in upgrades))
        self.assertNotIn('clay_inscriptions', upgrades)
        self.assertIn('clay_inscriptions', [key for key, _, _ in shop_items(state, True, era=0)])

    def test_vacuum_entry_machine_bridges_gap_without_nerfing_existing_triodes(self):
        state = GameState()
        state.current_era = 3
        state.bits = 1000000
        state.total_bits_earned = ERAS[3]['unlock_bits']
        self.assertTrue(state.is_era_generator_unlocked('vacuum_diode'))
        self.assertTrue(state.purchase_generator('vacuum_diode'))
        self.assertEqual(state.get_production_rate(), 50000)
        self.assertEqual(state.get_generator_cost('triode'), 10000000)
        state.generators['triode']['count'] = 1
        self.assertEqual(state.get_generator_production('triode'), 500000)
        self.assertEqual(state.get_production_rate(), 550000)

    def test_entry_saving_pacing_has_no_escalating_multi_minute_stall(self):
        from playtest_era_progression import simulate
        for research in (False, True):
            entries = simulate(research)
            self.assertEqual([entry['era'] for entry in entries], [1, 2, 3, 4])
            self.assertTrue(all(entry['carried_production'] > 0 for entry in entries))
            self.assertTrue(all(entry['first_new_machine_after'] <= 60 for entry in entries))

    def test_explicit_resets_still_clear_all_machine_counts(self):
        for reset in ('perform_rebirth', 'perform_prestige'):
            state = GameState()
            state.current_era = 4
            state.bits = state.total_bits_earned = 10**12
            for key in state.generators:
                state.generators[key]['count'] = 2
            self.assertTrue(getattr(state, reset)())
            self.assertTrue(all(owned['count'] == 0 for owned in state.generators.values()))
            self.assertEqual(state.get_production_rate(), 0)

    def test_save_load_and_offline_income_include_earlier_machines(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(CONFIG, SAVE_FILE=str(Path(directory) / 'save.json')):
            game = BitByBitGame()
            game.state.current_era = 2
            game.state.binary_invented = True
            game.state.binary_efficiency = 4
            game.state.bits = 1234
            for key in ('pebble', 'lever'):
                game.state.generators[key]['count'] = 3
            game.state.era_upgrades['gear_lubrication']['level'] = 2
            # A pre-fix save lacks the newly introduced entry tube.
            game.state.generators.pop('vacuum_diode')
            rate = game.state.get_production_rate()
            with patch('gui.time.time', return_value=1000):
                game.save_game()
            with patch('gui.time.time', return_value=1060):
                loaded = BitByBitGame()
            self.assertEqual(loaded.state.get_production_rate(), rate)
            self.assertEqual(loaded.state.generators['vacuum_diode']['count'], 0)
            self.assertAlmostEqual(loaded.state.bits, 1234 + 60 * 0.75 * rate)
            self.assertIn('lever', [key for key, _, _ in shop_items(loaded.state, era=1)])

    def test_old_machine_and_upgrade_clicks_after_resize_and_scroll(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(CONFIG, SAVE_FILE=str(Path(directory) / 'save.json')):
            game = BitByBitGame()
            game.showing_tutorial = False
            game.state.current_era = 2
            game.state.bits = game.state.total_bits_earned = 10**8
            for size in ((1200, 800), (960, 640)):
                game.handle_window_resize(*size)
                game._select_era_view(0)
                for upgrades, key in ((False, 'pebble'), (True, 'clay_inscriptions')):
                    game.draw()
                    items = shop_items(game.state, upgrades, era=0)
                    index = next(i for i, item in enumerate(items) if item[0] == key)
                    panel = game.upgrades_scroll_panel if upgrades else game.hardware_scroll_panel
                    panel.scroll_to(index * (CARD_HEIGHT + CARD_GAP))
                    game.draw()
                    _, one, _ = card_geometry(panel, index)
                    before = (game.state.era_upgrades[key]['level'] if upgrades else
                              game.state.generators[key]['count'])
                    pygame.event.clear()
                    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=one.center))
                    game.handle_events()
                    after = (game.state.era_upgrades[key]['level'] if upgrades else
                             game.state.generators[key]['count'])
                    self.assertEqual(after, before + 1)


if __name__ == '__main__':
    unittest.main()
