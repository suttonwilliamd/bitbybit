"""Pure transistor-board rendering tests. No player files or save access."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from dataclasses import asdict
import math
import unittest
import pygame
from gui import theme
from gui.machines import MachineAnimation
from gui.transistors import (_layers, draw_transistor_board, signal_paths,
                             signal_segment, transistor_positions)


class TransistorBoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    def tearDown(self):
        theme.configure(False)

    def render(self, amount, phase=.6, size=(464, 244)):
        screen = pygame.Surface(size)
        screen.fill(theme.SURFACE)
        draw_transistor_board(screen, screen.get_rect(), amount, MachineAnimation(phase=phase))
        return pygame.image.tostring(screen, 'RGB')

    def test_traces_meet_transistor_terminals_and_leave_register_clear(self):
        for compact in (False, True):
            positions = transistor_positions(compact)
            self.assertEqual(len(set(positions)), 6)
            radius = 18 if compact else 23
            register_top = 212 if compact else 323
            for path, (x, y) in zip(signal_paths(compact), (p for p in positions if p[0] != 540)):
                self.assertEqual(path[0], (x + 18, y + radius + 16))
                self.assertEqual(path[-1], (x + 200, y + radius + 16))
                self.assertTrue(all(20 < px < 700 and 59 < py < register_top for px, py in path))
                self.assertTrue(all(a[0] == b[0] or a[1] == b[1] for a, b in zip(path, path[1:])))

    def test_demo_segment_is_bounded_and_always_follows_existing_copper(self):
        for compact in (False, True):
            for frame in range(1200):
                phase = frame / 60
                segment = signal_segment(phase, compact)
                path = signal_paths(compact)[int((phase * .65) % 4)]
                self.assertLessEqual(sum(math.dist(a, b) for a, b in zip(segment, segment[1:])), 24.000001)
                for x, y in segment:
                    self.assertTrue(any(
                        min(a[0], b[0]) - 1e-8 <= x <= max(a[0], b[0]) + 1e-8 and
                        min(a[1], b[1]) - 1e-8 <= y <= max(a[1], b[1]) + 1e-8
                        for a, b in zip(path, path[1:])))
                repeated = signal_segment(phase + 4 / .65, compact)
                self.assertEqual(len(segment), len(repeated))
                for a, b in zip(segment, repeated):
                    self.assertAlmostEqual(a[0], b[0])
                    self.assertAlmostEqual(a[1], b[1])

    def test_render_is_pure_deterministic_and_keeps_parent_clip(self):
        for contrast in (False, True):
            theme.configure(contrast)
            for size in ((464, 244), (344, 140)):
                screen = pygame.Surface((size[0] + 40, size[1] + 40))
                screen.fill((255, 0, 255))
                rect = pygame.Rect((20, 20), size)
                clip = pygame.Rect(10, 10, size[0] // 2, size[1] + 20)
                screen.set_clip(clip)
                animation = MachineAnimation(phase=.8, amount=88)
                before = asdict(animation)
                draw_transistor_board(screen, rect, 15, animation)
                image = pygame.image.tostring(screen, 'RGB')
                screen.fill((255, 0, 255))  # Repaint the alpha border against the same background.
                draw_transistor_board(screen, rect, 15, animation)
                self.assertEqual(image, pygame.image.tostring(screen, 'RGB'))
                self.assertEqual(before, asdict(animation))
                self.assertEqual(screen.get_clip(), clip)
                for point in ((19, 25), (rect.right, 25), (clip.right, rect.centery), (25, rect.bottom)):
                    self.assertEqual(screen.get_at(point)[:3], (255, 0, 255))

    def test_motion_is_separate_from_truthful_low_byte_and_spending(self):
        for size in ((464, 244), (344, 140)):
            self.assertNotEqual(self.render(1, .6, size), self.render(1, 1.2, size))
            for amount in (0, 1, 2, 128, 255, 10**40 + 7):
                image = self.render(amount, size=size)
                self.assertEqual(image, self.render(amount + 256, size=size))
                self.assertNotEqual(image, self.render((amount + 1) % 256, size=size))
            self.assertEqual(self.render(257.9, size=size), self.render(1, size=size))

    def test_palette_cache_is_bounded_and_returns_original_palette(self):
        theme.configure(False)
        standard = self.render(175)
        theme.configure(True)
        self.assertNotEqual(standard, self.render(175))
        theme.configure(False)
        self.assertEqual(standard, self.render(175))
        self.assertEqual(_layers.cache_info().maxsize, 8)
        self.assertLessEqual(_layers.cache_info().currsize, 8)

    def test_empty_targets_are_noop(self):
        screen = pygame.Surface((100, 100))
        screen.fill((255, 0, 255))
        before = pygame.image.tostring(screen, 'RGB')
        for size in ((0, 100), (100, 0), (-1, 10)):
            draw_transistor_board(screen, pygame.Rect((0, 0), size), 1)
        self.assertEqual(before, pygame.image.tostring(screen, 'RGB'))


if __name__ == '__main__':
    unittest.main()
