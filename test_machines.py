"""Working machine regressions. Tests never load or write the player's save."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from dataclasses import asdict
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pygame
from constants import CONFIG
from gui import BitByBitGame, dashboard, theme
from gui.machines import (MachineAnimation, ROLL_SECONDS, crank_linkage, draw_era_machine,
                          mechanical_gears, output_bits, relay_states, tape_position)


class MachineAnimationTests(unittest.TestCase):
    def test_delta_time_and_click_response_are_frame_rate_independent(self):
        slow, fast = MachineAnimation(), MachineAnimation()
        for animation, fps in ((slow, 30), (fast, 60)):
            animation.click()
            for _ in range(fps * 3):
                animation.update(1 / fps, 123, 1000)
        self.assertAlmostEqual(slow.phase, fast.phase, places=10)
        self.assertAlmostEqual(slow.impulse, fast.impulse, places=10)
        idle = MachineAnimation()
        for _ in range(30):
            idle.update(.1, 123, 0)
        self.assertLess(idle.phase, slow.phase)
        self.assertEqual(idle.amount, 123)

    def test_stalls_and_rapid_clicks_are_bounded(self):
        animation = MachineAnimation()
        for _ in range(1000):
            animation.click()
        self.assertEqual(animation.impulse, 3)
        animation.update(-1, 0)
        self.assertEqual(animation.phase, 0)
        animation.update(10000, 0, 10**100)
        self.assertLess(animation.phase, 4)

    def test_register_carries_coalesces_and_settles_large_jumps_or_spending(self):
        animation = MachineAnimation()
        animation.update(0, 9999)
        animation.update(0, 10000)
        self.assertEqual(animation.previous_amount, 9999)
        self.assertEqual(animation.counter_progress, 0)
        animation.update(ROLL_SECONDS, 10000)
        self.assertEqual(animation.counter_progress, 1)
        for value in (9000, 10**20):
            animation.update(0, value)
            self.assertEqual(animation.previous_amount, value)
            self.assertEqual(animation.counter_progress, 1)
        for i in range(1, 51):
            animation.update(.02, 10**20 + i)
        self.assertGreater(animation.previous_amount, 10**20)
        self.assertEqual(animation.amount, 10**20 + 50)

    def test_reduced_motion_freezes_every_phase_but_updates_readings(self):
        animation = MachineAnimation()
        animation.update(.1, 123)
        phase = animation.phase
        animation.click()
        animation.update(.1, 124, 100, reduced_motion=True)
        for _ in range(30):
            animation.click(reduced_motion=True)
            animation.update(.1, 124, 100, reduced_motion=True)
        self.assertEqual(animation.phase, phase)
        self.assertEqual(animation.impulse, 0)
        self.assertEqual(animation.previous_amount, 124)
        self.assertEqual(animation.counter_progress, 1)
        animation.update(.1, 124)
        self.assertGreater(animation.phase, phase)

    def test_gears_touch_at_pitch_and_counter_rotate_with_correct_tooth_phase(self):
        for compact in (False, True):
            a, b = mechanical_gears(compact, .3), mechanical_gears(compact, 1.3)
            self.assertEqual(len(a), 5)
            for i in range(1, 5):
                left, right = a[i - 1], a[i]
                self.assertAlmostEqual(math.dist(left[:2], right[:2]), left[2] + right[2])
                da, db = b[i - 1][4] - left[4], b[i][4] - right[4]
                self.assertLess(da * db, 0)
                self.assertAlmostEqual(left[3] * da + right[3] * db, 0)
                self.assertAlmostEqual(left[3] * left[4] + right[3] * right[4], math.pi * (right[3] - 1))

    def test_connecting_rod_has_fixed_length_and_slider_stays_in_guides(self):
        for compact in (False, True):
            for step in range(360):
                pin, slider, length = crank_linkage(math.tau * step / 360, compact)
                self.assertAlmostEqual(math.dist(pin, slider), length)
                self.assertEqual(slider[1], 240 if compact else 351)
                self.assertGreaterEqual(slider[0] - 330, 54)
                self.assertLessEqual(slider[0] + 10, 482)

    def test_scan_selects_one_relay_in_order_and_tape_indexes_then_holds(self):
        for index in range(8):
            states = relay_states((index + .4) / 2)
            self.assertEqual(states[index], 1)
            self.assertEqual(sum(s > 0 for s in states), 1)
        for step in range(100):
            phase = step / 20
            for a, b in zip(relay_states(phase), relay_states(phase + 4)):
                self.assertAlmostEqual(a, b)
            self.assertTrue(all(0 <= value <= 1 for value in relay_states(phase)))
        self.assertEqual(tape_position(0), 0)
        self.assertGreater(tape_position(.24), 0)
        self.assertEqual(tape_position(.6), tape_position(3.9))
        self.assertEqual(tape_position(4), 10)
        self.assertGreater(tape_position(4.24), 10)
        self.assertEqual(tape_position(4.6), 20)

    def test_output_lamps_are_actual_low_byte_most_significant_bit_first(self):
        self.assertEqual(output_bits(128), (True,) + (False,) * 7)
        self.assertEqual(output_bits(1), (False,) * 7 + (True,))
        self.assertEqual(output_bits(255), (True,) * 8)
        self.assertEqual(output_bits(256), (False,) * 8)
        self.assertEqual(output_bits(257.9), output_bits(1))


class MachineRenderTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.config = patch.dict(CONFIG, SAVE_FILE=str(Path(self.directory.name) / 'test.json'))
        self.config.start()
        self.game = BitByBitGame()
        self.game.showing_tutorial = False
        pygame.event.clear()

    def tearDown(self):
        self.config.stop()
        self.directory.cleanup()
        theme.configure(False)

    def image(self, rect):
        return pygame.image.tostring(self.game.screen.subsurface(rect), 'RGB')

    def test_render_is_pure_clipped_and_changes_with_motion_at_both_sizes(self):
        for high_contrast in (False, True):
            theme.configure(high_contrast)
            for size in ((464, 244), (344, 140)):
                for era in (1, 2):
                    animation = MachineAnimation()
                    animation.update(0, 12345)
                    screen = pygame.Surface((size[0] + 40, size[1] + 40))
                    screen.fill((255, 0, 255))
                    rect = pygame.Rect((20, 20), size)
                    before = asdict(animation)
                    draw_era_machine(screen, rect, era, 12345, animation)
                    self.assertEqual(asdict(animation), before)
                    first = pygame.image.tostring(screen, 'RGB')
                    screen.fill((255, 0, 255), rect)
                    draw_era_machine(screen, rect, era, 12345, animation)
                    self.assertEqual(first, pygame.image.tostring(screen, 'RGB'))
                    animation.phase = 1.2
                    screen.fill((255, 0, 255), rect)
                    draw_era_machine(screen, rect, era, 12345, animation)
                    self.assertNotEqual(first, pygame.image.tostring(screen, 'RGB'))
                    for point in ((0, 0), (19, rect.centery), (rect.right, rect.centery), (rect.centerx, rect.bottom)):
                        self.assertEqual(screen.get_at(point)[:3], (255, 0, 255))
                    self.assertEqual(screen.get_clip(), screen.get_rect())

    def test_actual_click_target_follows_compact_and_full_machine(self):
        game = self.game
        for era in (1, 2, 4):
            game.state.current_era = era
            for size in ((960, 640), (1024, 768), (1200, 800), (1600, 900)):
                game.showing_tutorial = False
                game.handle_window_resize(*size)
                game.draw()
                rect = game.accumulator_click_rect
                self.assertTrue(dashboard.layout(*size)[2].contains(rect))
                self.assertFalse(rect.colliderect(game.click_button.rect))
                before, power = game.state.bits, game.state.get_click_power()
                pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center))
                game.handle_events()
                self.assertEqual(game.state.bits, before + power)
                self.assertGreater(game.machine_animation.impulse, 0)
                game.update(.1)
                self.assertGreater(game.machine_animation.phase, 0)

    def test_reduced_motion_pixels_stay_fixed_and_readings_update_immediately(self):
        game = self.game
        for era in (1, 2, 4):
            game.state.current_era = era
            game.state.bits = 124
            game.reduced_motion_mode = True
            game.update(.1)
            game.draw()
            rect = game.accumulator_click_rect
            first = self.image(rect)
            for _ in range(30):
                game.update(.1)
            game.draw()
            self.assertEqual(first, self.image(rect))
            game.state.bits = 125
            game.update(.1)
            game.draw()
            self.assertNotEqual(first, self.image(rect))
            self.assertEqual(game.machine_animation.counter_progress, 1)
            self.assertEqual(game.machine_animation.previous_amount, 125)

    def test_unrelated_eras_remain_static_and_render_never_earns_currency(self):
        game = self.game
        before = (game.state.bits, game.state.pebbles, game.state.total_clicks,
                  game.state.total_bits_earned, game.state.total_pebbles_earned)
        rect = pygame.Rect(0, 0, 464, 244)
        for era in (0, 1, 2, 3, 4, 5, 6):
            game.machine_animation.phase = 0
            dashboard.draw_machine(game.screen, rect, era, 9999, game.machine_animation)
            first = self.image(rect)
            game.machine_animation.phase = 1.2
            dashboard.draw_machine(game.screen, rect, era, 9999, game.machine_animation)
            if era not in (1, 2, 4):
                self.assertEqual(first, self.image(rect))
        self.assertEqual(before, (game.state.bits, game.state.pebbles, game.state.total_clicks,
                                 game.state.total_bits_earned, game.state.total_pebbles_earned))


if __name__ == '__main__':
    unittest.main()
