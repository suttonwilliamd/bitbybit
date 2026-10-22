"""Presentation-only thermionic instrument regressions; no player files."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from dataclasses import asdict
import math
import unittest
from unittest.mock import patch
import pygame
from gui import theme
from gui.machines import MachineAnimation, _font
from gui.vacuum import (STAGES, _layers, conduction_levels, draw_vacuum_instrument,
                        flow_segment, output_geometry, probe_path, scope_geometry,
                        scope_points, selected_stage, signal_paths, socket_rect,
                        stage_values, tube_geometry)


class VacuumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    def tearDown(self):
        theme.configure(False)

    def image(self, amount=129, phase=.4, size=(720, 400)):
        screen = pygame.Surface(size)
        screen.fill(theme.SURFACE)
        draw_vacuum_instrument(screen, screen.get_rect(), amount, MachineAnimation(phase=phase))
        return screen

    def pixels(self, surface, rect=None):
        return pygame.image.tostring(surface.subsurface(rect) if rect else surface, 'RGB')

    def test_distinct_waveforms_are_bounded_and_divider_has_half_the_frequency(self):
        for i in range(1024):
            theta = .013 + i * math.tau / 128
            source, amplifier, rectified, divided = stage_values(theta)
            self.assertAlmostEqual(source, .35 * math.sin(theta))
            self.assertTrue(-1 <= amplifier <= 1)
            self.assertEqual(rectified, max(0, amplifier))
            self.assertIn(divided, (0, 1))
            self.assertEqual(divided, float(math.sin(theta / 2) >= 0))
            self.assertTrue(all(0 <= value <= 1 for value in conduction_levels(theta)))
            for a, b in zip(stage_values(theta), stage_values(theta + 2 * math.tau)):
                self.assertAlmostEqual(a, b)
        self.assertGreater(stage_values(math.pi / 6)[1], .8)
        self.assertEqual(stage_values(3 * math.pi / 2)[2], 0)
        self.assertNotEqual(stage_values(.1)[3], stage_values(.1 + math.tau)[3])

    def test_scope_cycles_four_views_and_keeps_every_sample_in_its_screen(self):
        self.assertEqual(tuple(selected_stage(i * 5) for i in range(8)), (0, 1, 2, 3) * 2)
        self.assertEqual(selected_stage(-1), 0)
        for compact in (False, True):
            rect = scope_geometry(compact)
            for phase in (.4, 5.4, 10.4, 15.4, 1e6):
                points = scope_points(phase, compact)
                self.assertEqual(len(points), rect.width - 8)
                self.assertTrue(all(rect.collidepoint(point) for point in points))
                self.assertEqual(sorted(x for x, _ in points), [x for x, _ in points])
                self.assertEqual(points[-1][0], rect.right - 5)
            self.assertEqual(len(set(scope_points(1, compact, i) for i in range(4))), 4)

    def test_wiring_meets_socket_pins_and_flow_stays_on_copper(self):
        for compact in (False, True):
            tubes = tube_geometry(compact)
            for i, path in enumerate(signal_paths(compact)):
                self.assertEqual(path[0], (tubes[i].centerx + 24, socket_rect(tubes[i]).bottom))
                self.assertEqual(path[-1], (tubes[i + 1].centerx - 24, socket_rect(tubes[i + 1]).bottom))
            for phase in (.4, 5.4, 10.4, 15.4):
                probe = probe_path(phase, compact)
                glass = tubes[selected_stage(phase)]
                self.assertEqual(probe[0], (glass.centerx + 24, socket_rect(glass).bottom))
                self.assertEqual(probe[-1], (480, scope_geometry(compact).centery))
                for path in (*signal_paths(compact), probe):
                    for step in range(60):
                        segment = flow_segment(path, step / 30)
                        self.assertLessEqual(sum(math.dist(a, b) for a, b in zip(segment, segment[1:])), 18.000001)
                        for point in segment:
                            self.assertTrue(any(abs(math.dist(a, point) + math.dist(point, b) - math.dist(a, b)) < 1e-6
                                                for a, b in zip(path, path[1:])))

    def test_glass_sockets_scope_and_low_byte_are_all_inside_the_cabinet(self):
        for compact in (False, True):
            height = 280 if compact else 400
            cabinet = pygame.Rect(20, 20, 680, height - 40)
            bank = pygame.Rect(30, 66, 430, height - 136)
            scope = pygame.Rect(480, 66, 202, height - 136)
            output = output_geometry(compact)
            self.assertTrue(cabinet.contains(output.inflate(16, 16)))
            self.assertFalse(output.colliderect(bank))
            self.assertTrue(scope.contains(scope_geometry(compact).inflate(8, 8)))
            for i, glass in enumerate(tube_geometry(compact)):
                self.assertTrue(bank.contains(glass))
                self.assertTrue(bank.contains(socket_rect(glass)))
                tag = f'V{i + 1} ' + ('OSC', 'AMP', 'RECT', '/2')[i]
                label = _font(11 if compact else 13).render(tag, True, theme.TEXT)
                self.assertTrue(bank.contains(label.get_rect(center=(glass.centerx, glass.bottom + (28 if compact else 33)))))
            for i in range(8):
                x, y = 250 + i * 27, output.bottom - 10
                self.assertTrue(output.contains(pygame.Rect(x - 7, y - 7, 15, 15)))
                label = _font(10).render(str(7 - i), True, theme.TEXT)
                self.assertTrue(output.contains(label.get_rect(center=(x, output.y + 8))))
            for name in STAGES:
                self.assertLessEqual(_font(18).size(name)[0], 174)

    def test_truthful_low_byte_is_separate_from_demo_and_handles_spending_and_jumps(self):
        for size in ((720, 400), (720, 140)):
            compact = size[1] < 180
            height, scale = (280, .5) if compact else (400, 1)
            original = None
            for amount in (128, 129, 5, 2**64 + 5, 255, 256, 257.9):
                surface = self.image(amount, size=size)
                decoded = 0
                for bit in range(8):
                    color = surface.get_at((250 + bit * 27, round((height - 38) * scale)))[:3]
                    if color == theme.TEXT:
                        decoded |= 1 << (7 - bit)
                self.assertEqual(decoded, int(amount) & 255)
                demo = pygame.Rect(30, 66 * scale, 652, (height - 136) * scale)
                current = self.pixels(surface, demo)
                if original is None:
                    original = current
                self.assertEqual(original, current)

    def test_render_is_pure_clipped_and_filaments_do_not_flash(self):
        for size in ((464, 244), (344, 140)):
            screen = pygame.Surface((size[0] + 20, size[1] + 20)); screen.fill((255, 0, 255))
            rect = pygame.Rect((10, 10), size)
            clip = rect.inflate(-10, -10); screen.set_clip(clip)
            animation = MachineAnimation(phase=.4)
            before = asdict(animation)
            draw_vacuum_instrument(screen, rect, 129, animation)
            first = self.pixels(screen)
            screen.fill((255, 0, 255))
            draw_vacuum_instrument(screen, rect, 129, animation)
            self.assertEqual(first, self.pixels(screen))
            self.assertEqual(before, asdict(animation))
            self.assertEqual(screen.get_clip(), clip)
            self.assertEqual(screen.get_at(rect.topleft)[:3], (255, 0, 255))
        first, second = self.image(phase=.4), self.image(phase=6.8)
        self.assertNotEqual(self.pixels(first), self.pixels(second))
        for glass in tube_geometry():
            heater = pygame.Rect(glass.centerx - 13, glass.bottom - 26, 26, 16)
            self.assertEqual(self.pixels(first, heater), self.pixels(second, heater))

    def test_cache_is_bounded_theme_safe_and_empty_targets_are_noops(self):
        original = self.pixels(self.image())
        for index in range(12):
            with patch.object(theme, 'TEXT', (150 + index, 180, 170)):
                self.image()
        self.assertLessEqual(_layers.cache_info().currsize, 8)
        self.assertEqual(_layers.cache_info().maxsize, 8)
        theme.configure(True)
        self.assertNotEqual(original, self.pixels(self.image()))
        theme.configure(False)
        self.assertEqual(original, self.pixels(self.image()))
        surface = self.image(); before = self.pixels(surface)
        draw_vacuum_instrument(surface, pygame.Rect(10, 10, 0, 20), 10)
        draw_vacuum_instrument(surface, pygame.Rect(10, 10, 20, 0), 10)
        self.assertEqual(before, self.pixels(surface))


if __name__ == '__main__':
    unittest.main()
