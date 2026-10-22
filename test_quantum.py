"""Pure quantum demonstration tests; no player save is read or written."""
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
from gui.quantum import (CYCLE, ENDS, STAGES, _housing, balance_text, cryostat_geometry,
                         draw_quantum_instrument, flow_segment, probability_geometry,
                         project, quantum_frame, rotate_y, sphere_geometry,
                         target_phase, timeline_geometry)


class QuantumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    def tearDown(self):
        theme.configure(False)

    def image(self, phase=6.5, amount=129, size=(720, 400)):
        surface = pygame.Surface(size); surface.fill(theme.SURFACE)
        draw_quantum_instrument(surface, surface.get_rect(), amount, MachineAnimation(phase=phase))
        return surface

    def pixels(self, surface, rect=None):
        return pygame.image.tostring(surface.subsurface(rect) if rect else surface, 'RGB')

    def test_amplitudes_stay_normalized_and_y_rotation_is_reversible(self):
        for step in range(2048):
            frame = quantum_frame(step * .037)
            self.assertAlmostEqual(sum(frame.probabilities), 1)
            self.assertTrue(all(0 <= p <= 1.000000000001 for p in frame.probabilities))
            self.assertAlmostEqual(sum(v * v for v in frame.bloch), 1)
            inverse = rotate_y(rotate_y(frame.amplitudes, .71), -.71)
            for a, b in zip(inverse, frame.amplitudes):
                self.assertAlmostEqual(abs(a - b), 0)
        self.assertEqual(quantum_frame(-10), quantum_frame(0))
        self.assertAlmostEqual(quantum_frame(4).probabilities[0], .5)
        self.assertGreater(abs(quantum_frame(9).amplitudes[1].imag), .6)
        self.assertNotEqual(quantum_frame(9).bloch, quantum_frame(13).bloch)

    def test_stage_order_and_all_boundaries_including_reset_are_continuous(self):
        for cycle in range(8):
            for index, end in enumerate(ENDS):
                boundary = cycle * CYCLE + end
                before, after = quantum_frame(boundary - 1e-6), quantum_frame(boundary)
                self.assertEqual(before.stage, index)
                self.assertEqual(after.stage, (index + 1) % 5)
                for a, b in zip(before.amplitudes, after.amplitudes):
                    self.assertLess(abs(a - b), 1e-5)
                self.assertTrue(0 <= before.progress < 1)
                self.assertEqual(after.progress, 0)
        frame = quantum_frame(6)
        with self.assertRaises(FrozenInstanceError):
            frame.stage = 2

    def test_interference_probabilities_follow_phase_and_each_pass_varies(self):
        values = []
        for index in range(128):
            frame = quantum_frame(index * CYCLE + 14)
            self.assertEqual(frame.index, index)
            self.assertEqual(frame.stage, 4)
            self.assertAlmostEqual(frame.probabilities[1], math.sin(target_phase(index) / 2) ** 2)
            self.assertAlmostEqual(frame.probabilities[0], math.cos(target_phase(index) / 2) ** 2)
            self.assertEqual(frame, quantum_frame(index * CYCLE + 14))
            values.append(round(frame.probabilities[1], 4))
        self.assertGreater(len(set(values)), 120)
        self.assertLess(min(values), .001)
        self.assertGreater(max(values), .999)

    def test_projected_vector_and_all_labels_bars_and_timeline_fit(self):
        for compact in (False, True):
            height = 280 if compact else 400
            cabinet = pygame.Rect(20, 20, 680, height - 40)
            sphere_panel = pygame.Rect(266, 66, 240, height - 136)
            probability_panel = pygame.Rect(520, 66, 166, height - 136)
            center, radius = sphere_geometry(compact)
            self.assertTrue(sphere_panel.contains(pygame.Rect(center[0] - radius, center[1] - radius, radius * 2 + 1, radius * 2 + 1)))
            for step in range(512):
                point = project(quantum_frame(step * .07).bloch, compact)
                self.assertLessEqual(math.dist(center, point), radius + 1e-10)
                self.assertTrue(sphere_panel.collidepoint(point))
            for i, bar in enumerate(probability_geometry(compact)):
                self.assertTrue(probability_panel.contains(bar))
                self.assertTrue(probability_panel.contains(_font(14).render('100.0%', True, theme.TEXT).get_rect(center=(642, bar.y - 15))))
            for tag, box in zip(STAGES, timeline_geometry(compact)):
                self.assertTrue(cabinet.contains(box))
                self.assertTrue(box.contains(_font(13).render(tag, True, theme.TEXT).get_rect(center=(box.centerx, box.centery - 3))))
                self.assertGreater(box.top, sphere_panel.bottom)
            self.assertTrue(probability_panel.contains(_font(12 if compact else 14).render('phi set 359.9 deg', True, theme.TEXT).get_rect(center=(603, 198 if compact else 240))))

    def test_cryostat_control_lines_meet_chip_and_packets_stay_on_the_wire(self):
        for compact in (False, True):
            height = 280 if compact else 400
            well = pygame.Rect(34, 66, 218, height - 136)
            plates, chip, paths = cryostat_geometry(compact)
            self.assertTrue(well.contains(chip.inflate(6, 6)))
            for plate in plates:
                self.assertTrue(well.contains(plate.move(0, 4)))
            for i, path in enumerate(paths):
                self.assertEqual(path[-1], (chip.x + 7 + i * 10, chip.y))
                self.assertTrue(all(well.collidepoint(point) for point in path))
                for step in range(64):
                    segment = flow_segment(path, step / 32)
                    self.assertLessEqual(sum(math.dist(a, b) for a, b in zip(segment, segment[1:])), 18.000001)
                    for point in segment:
                        self.assertTrue(any(abs(math.dist(a, point) + math.dist(point, b) - math.dist(a, b)) < 1e-6 for a, b in zip(path, path[1:])))

    def test_true_balance_is_independent_of_the_demonstration(self):
        for amount, expected in ((128, '80'), (129, '81'), (5, '05'), (2**64 + 5, '05'), (255, 'FF'), (256, '00'), (257.9, '01')):
            self.assertEqual(balance_text(amount), 'LOW BYTE 0x' + expected)
        for size in ((464, 244), (344, 140)):
            first, second = self.image(amount=128, size=size), self.image(amount=129, size=size)
            self.assertNotEqual(self.pixels(first), self.pixels(second))
            body = pygame.Rect(0, round(size[1] * .24), size[0], int(size[1] * .7))
            self.assertEqual(self.pixels(first, body), self.pixels(second, body))

    def test_render_is_pure_deterministic_clipped_and_moves_within_a_single_gate(self):
        for contrast in (False, True):
            theme.configure(contrast)
            for size in ((464, 244), (344, 140)):
                surface = pygame.Surface((size[0] + 40, size[1] + 40));surface.fill((255, 0, 255))
                rect = pygame.Rect((20, 20), size);clip = rect.inflate(-8, -8);surface.set_clip(clip)
                animation = MachineAnimation(phase=6.5);before = asdict(animation)
                with patch('time.time', side_effect=AssertionError('wall clock')), patch('random.getrandbits', side_effect=AssertionError('random')):
                    draw_quantum_instrument(surface, rect, 129, animation)
                    first = self.pixels(surface)
                    surface.fill((255, 0, 255))
                    draw_quantum_instrument(surface, rect, 129, animation)
                self.assertEqual(first, self.pixels(surface))
                self.assertEqual(before, asdict(animation))
                self.assertEqual(surface.get_clip(), clip)
                self.assertEqual(surface.get_at(rect.topleft)[:3], (255, 0, 255))
                animation.phase = 7.5
                surface.fill((255, 0, 255));draw_quantum_instrument(surface, rect, 129, animation)
                self.assertNotEqual(first, self.pixels(surface))

    def test_cache_is_bounded_immutable_theme_safe_and_empty_targets_are_noops(self):
        original = self.pixels(self.image())
        palette = (theme.TEXT, theme.MUTED, theme.SAGE, theme.AMBER, theme.BORDER)
        cached = _housing(False, palette);before = self.pixels(cached)
        self.image(phase=12, amount=255)
        self.assertEqual(before, self.pixels(cached))
        for index in range(12):
            with patch.object(theme, 'TEXT', (150 + index, 180, 170)):
                self.image()
        self.assertLessEqual(_housing.cache_info().currsize, 8)
        self.assertEqual(_housing.cache_info().maxsize, 8)
        theme.configure(True);self.assertNotEqual(original, self.pixels(self.image()))
        theme.configure(False);self.assertEqual(original, self.pixels(self.image()))
        surface = self.image();before = self.pixels(surface)
        for size in ((0, 10), (10, 0)):
            draw_quantum_instrument(surface, pygame.Rect((10, 10), size), 255)
        self.assertEqual(before, self.pixels(surface))


if __name__ == '__main__':
    unittest.main()
