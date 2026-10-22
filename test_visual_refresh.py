"""Dashboard render/input regressions. All saves live in temporary directories."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pygame
from constants import CONFIG
from gui import BitByBitGame, dashboard, theme
from gui.modals import reset_layout, tutorial_layout
from gui.research import research_button_rect


class VisualRefreshTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'save.json'
        self.config = patch.dict(CONFIG, SAVE_FILE=str(self.path))
        self.config.start()
        self.game = BitByBitGame()
        self.game.showing_tutorial = False
        pygame.event.clear()

    def tearDown(self):
        self.config.stop()
        self.directory.cleanup()
        theme.configure(False)

    def click(self, rect):
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center))
        self.game.handle_events()

    def test_all_eras_and_pages_at_supported_sizes(self):
        game = self.game
        for size in ((960, 640), (1024, 768), (1200, 800), (1600, 900)):
            game.handle_window_resize(*size)
            left, right, hero = dashboard.layout(*size)
            self.assertFalse(left.colliderect(hero))
            self.assertFalse(right.colliderect(hero))
            self.assertTrue(hero.contains(game.click_button.rect))
            self.assertFalse(research_button_rect(*size).colliderect(left))
            for era in range(7):
                game.state.current_era = era
                game.draw()
            for attribute in ('showing_settings', 'showing_statistics', 'showing_research',
                              'showing_rebirth_confirmation', 'showing_prestige_confirmation', 'showing_tutorial'):
                setattr(game, attribute, True)
                game.tutorial_text = 'A small beginning.\nBuild hardware, then open Research [R].'
                game.draw()
                setattr(game, attribute, False)
            game.high_contrast_mode = True
            game.draw()
            game.high_contrast_mode = False
        game.handle_window_resize(800, 600)
        self.assertEqual(game.screen.get_size(), (960, 640))

    def test_shop_clicks_follow_painted_buttons_after_resize_and_scroll(self):
        game = self.game
        game.handle_window_resize(960, 640)
        game.state.pebbles = game.state.total_pebbles_earned = 10**9
        game.draw()
        panel = game.hardware_scroll_panel
        items = dashboard.shop_items(game.state)
        _, one, ten = dashboard.card_geometry(panel, 0)
        self.click(one)
        self.assertEqual(game.state.generators[items[0][0]]['count'], 1)
        self.click(ten)
        self.assertEqual(game.state.generators[items[0][0]]['count'], 11)
        panel.scroll_to_bottom()
        game.draw()
        _, one, _ = dashboard.card_geometry(panel, len(items) - 1)
        self.assertTrue(dashboard.viewport(panel).contains(one))
        self.click(one)
        self.assertEqual(game.state.generators[items[-1][0]]['count'], 1)
        upgrades = dashboard.shop_items(game.state, True)
        _, one, _ = dashboard.card_geometry(game.upgrades_scroll_panel, 0)
        self.click(one)
        self.assertEqual(game.state.era_upgrades[upgrades[0][0]]['level'], 1)

    def test_clipped_cards_hidden_panels_and_modal_are_not_purchasable(self):
        game = self.game
        game.handle_window_resize(960, 640)
        game.state.pebbles = game.state.total_pebbles_earned = 10**9
        game.draw()
        panel = game.hardware_scroll_panel
        _, last, _ = dashboard.card_geometry(panel, len(dashboard.shop_items(game.state)) - 1)
        self.assertFalse(dashboard.handle_shop_click(game, last.center))
        _, first, _ = dashboard.card_geometry(panel, 0)
        self.click(game.hardware_toggle.rect)
        self.assertFalse(game.hardware_panel_open)
        self.click(first)
        self.assertEqual(game.state.generators['pebble']['count'], 0)
        game.hardware_panel_open = True
        game.showing_statistics = True
        self.click(first)
        self.assertEqual(game.state.generators['pebble']['count'], 0)

    def test_shard_restorations_have_dedicated_visible_workshop_geometry(self):
        from gui.workshop import history_button_rect, workshop_layout
        game = self.game
        game.state.data_shards = game.state.total_data_shards = 10**9
        game.draw()
        self.assertFalse(any(kind == 'shard' for _, _, kind in dashboard.shop_items(game.state, True)))
        self.click(history_button_rect(game.current_width, game.current_height))
        self.assertTrue(game.showing_workshop)
        game.draw()
        geometry = workshop_layout(game.current_width, game.current_height)
        self.assertTrue(geometry['panel'].contains(geometry['buy']))
        self.click(geometry['buy'])
        self.assertEqual(game.state.get_machine_level(0), 1)
        self.assertEqual(game.state.data_shards, 10**9 - 1)

    def test_dialog_and_settings_clicks_at_resized_coordinates(self):
        game = self.game
        game.handle_window_resize(960, 640)
        for attribute in ('showing_rebirth_confirmation', 'showing_prestige_confirmation'):
            setattr(game, attribute, True)
            game.draw()
            _, _, no = reset_layout(game.current_width, game.current_height)
            self.click(no)
            self.assertFalse(getattr(game, attribute))
        game.showing_tutorial = True
        game.tutorial_text = 'Continue your journey.'
        game.draw()
        _, button = tutorial_layout(game.current_width, game.current_height)
        self.click(button)
        self.assertFalse(game.showing_tutorial)
        self.click(game.settings_button.rect)
        game.draw()
        self.click(game._settings_rects['contrast'])
        self.assertTrue(game.high_contrast_mode)
        self.click(game._settings_rects['close'])
        self.assertFalse(game.showing_settings)

    def test_visual_migration_preserves_progress_and_remembers_new_preferences(self):
        game = self.game
        game.state.pebbles = 1234
        game.state.generators['pebble']['count'] = 7
        game.save_game()
        data = json.loads(self.path.read_text())
        data['state']['visual_settings'] = dict(binary_rain=True, particle_effects=True, crt_effects=True)
        self.path.write_text(json.dumps(data))
        loaded = BitByBitGame()
        self.assertGreaterEqual(loaded.state.pebbles, 1234)
        self.assertEqual(loaded.state.generators['pebble']['count'], 7)
        self.assertFalse(loaded.state.visual_settings['binary_rain'])
        self.assertFalse(loaded.state.visual_settings['particle_effects'])
        loaded.state.visual_settings['particle_effects'] = True
        loaded.high_contrast_mode = True
        loaded.reduced_motion_mode = True
        loaded.save_game()
        restored = BitByBitGame()
        self.assertTrue(restored.state.visual_settings['particle_effects'])
        self.assertTrue(restored.high_contrast_mode)
        self.assertTrue(restored.reduced_motion_mode)

    def test_body_text_contrast(self):
        def luminance(rgb):
            values = [v / 255 for v in rgb]
            linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055)**2.4 for v in values]
            return sum(v * w for v, w in zip(linear, (.2126, .7152, .0722)))
        for high_contrast in (False, True):
            theme.configure(high_contrast)
            for foreground, background in ((theme.TEXT, theme.CARD), (theme.MUTED, theme.CARD),
                                            (theme.INK, theme.SAGE), (theme.AMBER, theme.SURFACE)):
                a, b = sorted((luminance(foreground), luminance(background)))
                self.assertGreaterEqual((b + .05) / (a + .05), 4.5)


if __name__ == '__main__':
    unittest.main()
