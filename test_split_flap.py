"""Hinged split-flap regressions; no clock reads, game saves or player state."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from dataclasses import asdict
import unittest
import pygame
from gui.machines import (FLAP_SECONDS, MachineAnimation, _counter, _flap_digit,
                          _flap_face, flap_projection)


class SplitFlapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    def pixels(self, surface, rect=None):
        return pygame.image.tostring(surface.subsurface(rect) if rect else surface, 'RGB')

    def digit(self, progress, previous='9', digit='0', compact=False):
        height = 45 if compact else 69
        screen = pygame.Surface((63, height + 20))
        screen.fill((255, 0, 255))
        rect = pygame.Rect(10, 10, 43, height)
        _flap_digit(screen, rect, previous, digit, progress, compact)
        return screen, rect

    def register(self, amount, animation, compact=False):
        screen = pygame.Surface((720, 150))
        screen.fill((255, 0, 255))
        _counter(screen, amount, animation, compact)
        return screen

    def test_leaf_projection_shrinks_then_opens_about_the_same_hinge(self):
        for height in (41, 65):
            upper = [flap_projection(i / 200, height) for i in range(100)]
            lower = [flap_projection(i / 200, height) for i in range(100, 201)]
            self.assertTrue(all(half == 'upper' for half, _ in upper))
            self.assertTrue(all(half == 'lower' for half, _ in lower))
            self.assertEqual([h for _, h in upper], sorted((h for _, h in upper), reverse=True))
            self.assertEqual([h for _, h in lower], sorted(h for _, h in lower))
            self.assertEqual(flap_projection(-1, height), ('upper', height // 2))
            self.assertEqual(flap_projection(.5, height), ('lower', 0))
            self.assertEqual(flap_projection(2, height), ('lower', height - height // 2))

    def test_stationary_backing_halves_never_scroll_and_meet_at_midpoint(self):
        for compact in (False, True):
            old, rect = self.digit(1, digit='9', compact=compact)
            new, _ = self.digit(1, compact=compact)
            inner = rect.inflate(-4, -4)
            hinge = inner.y + inner.height // 2
            upper = pygame.Rect(inner.x, inner.y, inner.width, hinge - inner.y)
            lower = pygame.Rect(inner.x, hinge + 2, inner.width, inner.bottom - hinge - 2)
            for progress in (.05, .2, .4, .5):
                frame, _ = self.digit(progress, compact=compact)
                self.assertEqual(self.pixels(frame, lower), self.pixels(old, lower))
            for progress in (.5, .6, .8, .95):
                frame, _ = self.digit(progress, compact=compact)
                self.assertEqual(self.pixels(frame, upper), self.pixels(new, upper))
            # At edge-on, the two stationary backing halves remain fully readable.
            middle, _ = self.digit(.5, compact=compact)
            self.assertEqual(self.pixels(middle, upper), self.pixels(new, upper))
            self.assertEqual(self.pixels(middle, lower), self.pixels(old, lower))

    def test_endpoints_and_unchanged_digits_are_exact_stationary_faces(self):
        for compact in (False, True):
            first, _ = self.digit(0, compact=compact)
            old, _ = self.digit(1, digit='9', compact=compact)
            last, _ = self.digit(1, compact=compact)
            new, _ = self.digit(1, previous='0', compact=compact)
            self.assertEqual(self.pixels(first), self.pixels(old))
            self.assertEqual(self.pixels(last), self.pixels(new))
            for digit in '0123456789':
                settled, _ = self.digit(1, digit, digit, compact)
                for progress in (0, .2, .5, .8):
                    frame, _ = self.digit(progress, digit, digit, compact)
                    self.assertEqual(self.pixels(frame), self.pixels(settled))
            self.assertNotEqual(self.pixels(self.digit(.25, compact=compact)[0]), self.pixels(first))
            self.assertNotEqual(self.pixels(self.digit(.75, compact=compact)[0]), self.pixels(last))

    def test_carries_and_eight_digit_wrap_flip_only_changed_cells_without_mutation(self):
        for compact in (False, True):
            for previous, amount in ((9999, 10000), (99999999, 100000000)):
                animation = MachineAnimation(amount=amount, previous_amount=previous, counter_age=FLAP_SECONDS / 2)
                before = asdict(animation)
                image = self.register(amount, animation, compact)
                self.assertEqual(before, asdict(animation))
                for index, (a, b) in enumerate(zip(f'{previous % 10**8:08}', f'{amount % 10**8:08}')):
                    expected, rect = self.digit(.5, a, b, compact)
                    cell = pygame.Rect(70 + index * 47, 66, 43, rect.height)
                    self.assertEqual(self.pixels(image, cell), self.pixels(expected, rect))

    def test_spending_large_jumps_initial_load_and_reduced_motion_settle_immediately(self):
        for compact in (False, True):
            animation = MachineAnimation()
            animation.update(0, 9999)
            animation.update(FLAP_SECONDS / 4, 10000)
            self.assertLess(animation.counter_progress, 1)
            for value in (9000, 10**20, 10**20 + 1):
                animation.update(0, value, reduced_motion=True)
                expected = self.register(value, MachineAnimation(), compact)
                self.assertEqual(self.pixels(self.register(value, animation, compact)), self.pixels(expected))
                self.assertEqual(animation.counter_progress, 1)
            for value in (5, 50000000):
                animation.update(0, value)
                self.assertEqual(animation.counter_progress, 1)
                expected = self.register(value, MachineAnimation(), compact)
                self.assertEqual(self.pixels(self.register(value, animation, compact)), self.pixels(expected))

    def test_drawing_respects_existing_clip_and_does_not_leave_cell(self):
        for compact in (False, True):
            for progress in (0, .25, .5, .75, 1):
                height = 45 if compact else 69
                screen = pygame.Surface((63, height + 20))
                screen.fill((255, 0, 255))
                rect = pygame.Rect(10, 10, 43, height)
                clip = pygame.Rect(14, 12, 20, height - 5)
                screen.set_clip(clip)
                _flap_digit(screen, rect, '9', '0', progress, compact)
                self.assertEqual(screen.get_clip(), clip)
                for point in ((9, 20), (13, 20), (34, 20), (20, 11), (20, clip.bottom), (53, 20)):
                    self.assertEqual(screen.get_at(point)[:3], (255, 0, 255))

    def test_cached_faces_are_not_modified_by_folding_or_shading(self):
        for compact in (False, True):
            height, size = (41, 35) if compact else (65, 49)
            faces = [_flap_face(digit, 39, height, size) for digit in '90']
            before = [self.pixels(face) for face in faces]
            for progress in (.1, .3, .5, .7, .9):
                self.digit(progress, compact=compact)
            self.assertEqual(before, [self.pixels(face) for face in faces])
        self.assertEqual(_flap_face.cache_info().maxsize, 20)
        self.assertLessEqual(_flap_face.cache_info().currsize, 20)


if __name__ == '__main__':
    unittest.main()
