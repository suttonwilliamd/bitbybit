"""The finished journal must lead safely into the existing reset flow."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from copy import deepcopy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pygame
from constants import CONFIG
from gui import BitByBitGame, theme
from gui.modals import reset_layout
from gui.research import (research_finished, completed_research_layout,
                          research_reset_step)


class ResearchNextStepTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.config = patch.dict(CONFIG, SAVE_FILE=str(Path(self.directory.name) / 'save.json'))
        self.config.start()
        self.game = BitByBitGame()
        self.game.showing_tutorial = False
        state = self.game.state
        state.current_era = 6
        state.binary_invented = state.boolean_algebra_invented = True
        for key in ('logic_gates', 'stored_program', 'integrated_circuits'):
            state.prestige_upgrades.setdefault(key, {})['purchased'] = True
        state.bits = state.total_bits_earned = state.get_rebirth_threshold()
        state.generators['rng']['count'] = 3
        self.game.update(0)
        self.grid = patch.object(self.game.bit_grid, 'get_era_completion_percentage', return_value=100)
        self.grid.start()
        self.game.showing_research = True
        pygame.event.clear()

    def tearDown(self):
        self.grid.stop()
        self.config.stop()
        self.directory.cleanup()
        theme.configure(False)

    def click(self, rect):
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center))
        self.game.handle_events()

    def reset_button(self):
        return completed_research_layout(self.game.current_width, self.game.current_height)[2]

    def test_completion_requires_every_invention_and_every_historical_era(self):
        state = self.game.state
        self.assertTrue(research_finished(state))
        state.current_era = 4
        self.assertFalse(research_finished(state))
        self.game.draw()
        state.current_era = 6
        state.prestige_upgrades['stored_program']['purchased'] = False
        self.assertFalse(research_finished(state))
        before = deepcopy(state.__dict__)
        self.click(self.reset_button())
        self.assertFalse(self.game.showing_rebirth_confirmation)
        self.assertEqual(before, state.__dict__)

    def test_rebirth_is_first_then_prestige_and_both_use_real_unlocks(self):
        state = self.game.state
        self.assertTrue(state.can_prestige())
        self.assertEqual(research_reset_step(state)['name'], 'Rebirth')
        state.total_bits_earned = state.get_rebirth_threshold() - 1
        self.assertFalse(research_reset_step(state)['ready'])
        state.total_rebirths = 1
        self.assertEqual(research_reset_step(state)['name'], 'Prestige')
        state.total_bits_earned = 999999
        self.assertFalse(research_reset_step(state)['ready'])
        state.total_bits_earned = 1000000
        self.assertTrue(research_reset_step(state)['ready'])
        state.hardware_generation = 2
        step = research_reset_step(state)
        self.assertFalse(step['ready'])
        self.assertIn('generation 3', step['requirement'])

    def test_locked_button_cannot_open_confirmation_or_reset_anything(self):
        state = self.game.state
        for rebirths in (0, 1):
            state.total_rebirths = rebirths
            state.total_bits_earned = 0
            before = deepcopy(state.__dict__)
            self.game.draw()
            self.click(self.reset_button())
            self.assertTrue(self.game.showing_research)
            self.assertFalse(self.game.showing_rebirth_confirmation or self.game.showing_prestige_confirmation)
            self.assertEqual(before, state.__dict__)
        state.total_rebirths = 0
        state.total_bits_earned = state.get_rebirth_threshold()
        with patch.object(self.game.bit_grid, 'get_era_completion_percentage', return_value=50):
            self.assertFalse(research_reset_step(state, self.game.bit_grid)['ready'])
            self.click(self.reset_button())
            self.assertFalse(self.game.showing_rebirth_confirmation)

    def test_review_and_cancel_or_escape_return_to_journal_without_mutation(self):
        game = self.game
        for rebirths in (0, 1):
            game.state.total_rebirths = rebirths
            for escape in (False, True):
                before = deepcopy(game.state.__dict__)
                with patch.object(game.state, 'perform_rebirth') as rebirth, patch.object(game.state, 'perform_prestige') as prestige, patch.object(game, 'save_game') as save:
                    self.click(self.reset_button())
                    self.assertFalse(game.showing_research)
                    self.assertEqual(game.showing_rebirth_confirmation, rebirths == 0)
                    self.assertEqual(game.showing_prestige_confirmation, rebirths == 1)
                    game.draw()
                    if escape:
                        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
                        game.handle_events()
                    else:
                        self.click(reset_layout(game.current_width, game.current_height)[2])
                    rebirth.assert_not_called(); prestige.assert_not_called(); save.assert_not_called()
                self.assertTrue(game.showing_research)
                self.assertFalse(game.reset_from_research)
                self.assertEqual(before, game.state.__dict__)

    def test_only_explicit_confirmation_executes_reset_and_preserves_research(self):
        game = self.game
        for rebirths in (0, 1):
            game.state.current_era = 6
            game.state.total_rebirths = rebirths
            game.state.bits = game.state.total_bits_earned = game.state.get_rebirth_threshold()
            game.state.generators['rng']['count'] = 3
            game.showing_research = True
            claims = [p['complete'] for p in game.state.get_research_projects()]
            self.click(self.reset_button())
            self.assertEqual(game.state.generators['rng']['count'], 3)
            self.click(reset_layout(game.current_width, game.current_height)[1])
            self.assertEqual(game.state.bits, 0)
            self.assertEqual(game.state.generators['rng']['count'], 0)
            self.assertEqual(claims, [p['complete'] for p in game.state.get_research_projects()])
            self.assertFalse(game.showing_research or game.showing_rebirth_confirmation or game.showing_prestige_confirmation)
            self.assertFalse(game.reset_from_research)
            if rebirths == 0:
                self.assertEqual(game.state.total_rebirths, 1)
                self.assertGreater(game.state.data_shards, 0)
            else:
                self.assertEqual(game.state.prestige_count, 1)
                self.assertGreater(game.state.prestige_currency, 0)

    def test_normal_dashboard_reset_cancel_still_returns_to_dashboard(self):
        game = self.game
        game.showing_research = False
        for flag in ('showing_rebirth_confirmation', 'showing_prestige_confirmation'):
            setattr(game, flag, True)
            self.click(reset_layout(game.current_width, game.current_height)[2])
            self.assertFalse(game.showing_research)
            self.assertFalse(getattr(game, flag))

    def test_completed_layout_paint_and_click_align_at_all_supported_sizes(self):
        game = self.game
        for size in ((960, 640), (1024, 768), (1200, 800), (1600, 900)):
            game.handle_window_resize(*size)
            cards, panel, button, close = completed_research_layout(*size)
            bounds = pygame.Rect((0, 0), size)
            self.assertTrue(all(bounds.contains(r) for r in (*cards, panel, button, close)))
            self.assertTrue(panel.contains(button))
            self.assertFalse(cards[-1].colliderect(panel))
            step = research_reset_step(game.state)
            for i, key in enumerate(('instruction', 'requirement', 'resets', 'reward')):
                label = game.tiny_font.render(step[key], True, theme.TEXT).get_rect(topleft=(panel.x + 16, panel.y + 46 + i * 24))
                self.assertTrue(panel.contains(label))
                self.assertLess(label.bottom, button.top)
            for contrast in (False, True):
                game.high_contrast_mode = contrast
                game.draw()
            self.click(button)
            self.assertTrue(game.showing_rebirth_confirmation)
            self.click(reset_layout(*size)[2])
            self.assertTrue(game.showing_research)
        self.click(close)
        self.assertFalse(game.showing_research)

    def test_dashboard_footer_points_to_reset_instead_of_a_dead_end(self):
        game = self.game
        game.showing_research = False
        for rebirths, name in ((0, 'Rebirth'), (1, 'Prestige')):
            game.state.total_rebirths = rebirths
            with patch.object(theme, 'text', wraps=theme.text) as text:
                game.draw()
            labels = [call.args[2] for call in text.call_args_list]
            self.assertIn('Next step · ' + name, labels)
            self.assertNotIn('All research complete', labels)


if __name__ == '__main__':
    unittest.main()
