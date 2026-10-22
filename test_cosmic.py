"""Cosmic routing is fictional scenery with deterministic, verifiable byte demos."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from dataclasses import asdict, FrozenInstanceError
import math
import unittest
from unittest.mock import patch
import pygame
from gui import theme
from gui.machines import MachineAnimation, _font
from gui.cosmic import (CYCLE, ENDS, STAGES, _disc, _disc_bands, _housing, balance_text,
                        cosmic_frame, cosmic_job, draw_cosmic_engine, engine_geometry,
                        orbit_point, route_path, route_point, timeline_geometry)


class CosmicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    def tearDown(self):
        theme.configure(False)

    def image(self, phase=7.2, amount=129, size=(720, 400)):
        surface = pygame.Surface(size); surface.fill(theme.SURFACE)
        draw_cosmic_engine(surface, surface.get_rect(), amount, MachineAnimation(phase=phase))
        return surface

    def pixels(self, surface, rect=None):
        return pygame.image.tostring(surface.subsurface(rect) if rect else surface, 'RGB')

    def test_demo_bytes_and_xor_are_correct_varied_bounded_and_immutable(self):
        answers = set()
        for index in range(1024):
            a, b, answer = cosmic_job(index)
            self.assertTrue(all(0 <= v < 256 for v in (a, b, answer)))
            self.assertEqual(answer, a ^ b)
            raw = (151 * index + 0xA6) & 255
            bits = f'{raw:08b}'; shift = (index // 64) % 8
            self.assertEqual(b, int(bits[shift:] + bits[:shift], 2))
            answers.add(answer)
        self.assertGreater(len(answers), 200)
        self.assertLessEqual(cosmic_job.cache_info().currsize, 128)
        with self.assertRaises(ValueError):
            cosmic_job(-1)
        frame = cosmic_frame(6)
        with self.assertRaises(FrozenInstanceError):
            frame.answer = 0
        self.assertEqual(cosmic_frame(-100), cosmic_frame(0))

    def test_packets_converge_before_result_and_return_before_hold(self):
        for index in range(8):
            for stage, end in enumerate(ENDS):
                before, after = cosmic_frame(index * CYCLE + end - 1e-6), cosmic_frame(index * CYCLE + end)
                self.assertEqual(before.stage, stage)
                self.assertEqual(after.stage, (stage + 1) % 4)
                self.assertTrue(0 <= before.progress < 1)
                self.assertEqual(after.progress, 0)
                if stage < 3:
                    self.assertAlmostEqual(before.input_position, after.input_position)
                    self.assertAlmostEqual(before.output_position, after.output_position)
            for step in range(100):
                frame = cosmic_frame(index * CYCLE + step / 10)
                self.assertTrue(0 <= frame.input_position <= 1)
                self.assertTrue(0 <= frame.output_position <= 1)
                if frame.stage < 2:
                    self.assertIsNone(frame.result)
                    self.assertEqual(frame.output_position, 0)
                else:
                    self.assertEqual(frame.input_position, 1)
                    self.assertEqual(frame.result, frame.inputs[0] ^ frame.inputs[1])
        self.assertEqual(cosmic_frame(8).output_position, 1)

    def test_orbits_disc_routes_and_ports_fit_both_observatories(self):
        for compact in (False, True):
            well = pygame.Rect(34, 66, 486, (280 if compact else 400) - 136)
            center, _, horizon = engine_geometry(compact)
            self.assertTrue(well.contains(pygame.Rect(center[0] - horizon - 6, center[1] - horizon - 6, 2 * horizon + 13, 2 * horizon + 13)))
            bands = _disc_bands(compact)
            self.assertIsInstance(bands, tuple)
            self.assertEqual(len(bands), 20)
            for points, color, front in bands:
                self.assertIsInstance(points, tuple)
                self.assertTrue(all(well.collidepoint(p) for p in points))
                self.assertTrue(all(0 <= v <= 255 for v in color))
            for step in range(80):
                phase = step * .53
                for scale, aspect in ((1, .44), (.9, .52)):
                    for i in range(97):
                        self.assertTrue(well.collidepoint(orbit_point(i * math.tau / 96, phase, compact, scale, aspect)))
                for branch in range(3):
                    path = route_path(branch, phase, compact)
                    self.assertEqual(path[0], route_point(0, branch, phase, compact))
                    self.assertEqual(path[-1], route_point(1, branch, phase, compact))
                    self.assertTrue(all(well.collidepoint(p) for p in path))
                    self.assertLessEqual(max(math.dist(a, b) for a, b in zip(path, path[1:])), 9)
                for a, b, color, front in _disc(phase, compact):
                    self.assertTrue(well.collidepoint(a) and well.collidepoint(b))
                    self.assertEqual(front, (a[1] + b[1]) / 2 >= center[1])
                    self.assertTrue(all(0 <= v <= 255 for v in color))
            incoming = [route_point(1, branch, 0, compact) for branch in (0, 1)]
            outgoing = route_point(0, 2, 0, compact)
            self.assertTrue(all(math.dist(center, p) < horizon for p in (*incoming, outgoing)))

    def test_all_readings_and_stage_labels_are_inside_the_cabinet(self):
        for compact in (False, True):
            height = 280 if compact else 400
            cabinet = pygame.Rect(20, 20, 680, height - 40)
            panel = pygame.Rect(532, 66, 152, height - 136)
            for i in range(2):
                pos = (550, (96 + i * 25) if compact else (103 + i * 38))
                self.assertTrue(panel.contains(_font(16 if compact else 18).render('A 0xFF', True, theme.TEXT).get_rect(topleft=pos)))
            for text in ('= ----', '= 0xFF'):
                self.assertTrue(panel.contains(_font(20 if compact else 26).render(text, True, theme.TEXT).get_rect(center=(608, 170 if compact else 204))))
            self.assertTrue(cabinet.contains(_font(13).render('LOW BYTE 0xFF', True, theme.TEXT).get_rect(topleft=(535, 36))))
            for stage, box in zip(STAGES, timeline_geometry(compact)):
                self.assertTrue(cabinet.contains(box))
                self.assertGreater(box.top, panel.bottom)
                self.assertTrue(box.contains(_font(13).render(stage, True, theme.TEXT).get_rect(center=(box.centerx, box.centery - 3))))

    def test_true_balance_is_independent_of_demo_after_spending_jumps_and_wrap(self):
        for value, expected in ((128, '80'), (129, '81'), (5, '05'), (2**64 + 5, '05'), (255, 'FF'), (256, '00'), (257.9, '01')):
            self.assertEqual(balance_text(value), 'LOW BYTE 0x' + expected)
        for size in ((464, 244), (344, 140)):
            a, b = self.image(amount=128, size=size), self.image(amount=129, size=size)
            self.assertNotEqual(self.pixels(a), self.pixels(b))
            body = pygame.Rect(0, round(size[1] * .24), size[0], int(size[1] * .7))
            self.assertEqual(self.pixels(a, body), self.pixels(b, body))

    def test_motion_continues_during_hold_but_stars_and_horizon_do_not_flash(self):
        a, b = self.image(8.2), self.image(9.2)
        self.assertNotEqual(self.pixels(a), self.pixels(b))
        # Unoccluded fixed star near the upper left; core's central disk stays dark.
        for point in ((46, 78), (278, 195)):
            self.assertEqual(a.get_at(point), b.get_at(point))
        self.assertEqual(a.get_at((278, 195))[:3], (7, 11, 18))

    def test_draw_is_pure_deterministic_clipped_and_needs_no_wall_clock_or_randomness(self):
        for contrast in (False, True):
            theme.configure(contrast)
            for size in ((464, 244), (344, 140)):
                surface = pygame.Surface((size[0] + 40, size[1] + 40)); surface.fill((255, 0, 255))
                rect = pygame.Rect((20, 20), size); clip = rect.inflate(-8, -8); surface.set_clip(clip)
                animation = MachineAnimation(phase=7.2); before = asdict(animation)
                with patch('time.time', side_effect=AssertionError('wall clock')), patch('random.getrandbits', side_effect=AssertionError('random')):
                    draw_cosmic_engine(surface, rect, 129, animation)
                    first = self.pixels(surface)
                    surface.fill((255, 0, 255)); draw_cosmic_engine(surface, rect, 129, animation)
                self.assertEqual(first, self.pixels(surface))
                self.assertEqual(before, asdict(animation))
                self.assertEqual(surface.get_clip(), clip)
                self.assertEqual(surface.get_at(rect.topleft)[:3], (255, 0, 255))

    def test_cache_is_bounded_immutable_theme_safe_and_empty_targets_are_noops(self):
        original = self.pixels(self.image())
        palette = (theme.TEXT, theme.MUTED, theme.SAGE, theme.AMBER, theme.BORDER)
        cached = _housing(False, palette); before = self.pixels(cached)
        self.image(phase=17.2, amount=255)
        self.assertEqual(before, self.pixels(cached))
        for i in range(12):
            with patch.object(theme, 'TEXT', (150 + i, 180, 170)):
                self.image()
        self.assertLessEqual(_housing.cache_info().currsize, 8)
        self.assertEqual(_disc_bands.cache_info().maxsize, 2)
        self.assertLessEqual(_disc_bands.cache_info().currsize, 2)
        theme.configure(True); self.assertNotEqual(original, self.pixels(self.image()))
        theme.configure(False); self.assertEqual(original, self.pixels(self.image()))
        surface = self.image(); before = self.pixels(surface)
        for size in ((0, 10), (10, 0)):
            draw_cosmic_engine(surface, pygame.Rect((10, 10), size), 255)
        self.assertEqual(before, self.pixels(surface))


if __name__ == '__main__':
    unittest.main()
