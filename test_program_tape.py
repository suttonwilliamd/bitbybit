"""Demo-program, rare-message and cabinet-bound regressions; no player saves."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from dataclasses import asdict, FrozenInstanceError
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pygame
from constants import CONFIG
from gui import BitByBitGame, theme
from gui.machines import (DARK, PAPER, MachineAnimation, _font, _tape, draw_era_machine,
                          relay_geometry, relay_output_geometry, relay_states, tape_geometry)
from gui.tape_program import (JOB_PHASE, MESSAGE_ODDS, PROGRAMS, _SECRET_MESSAGE,
                              _message_starts, tape_frame, tape_job)

RARE_TEST_SEED = 45844  # A genuine hash hit at job zero, not altered live odds.


class ProgramTapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    def tearDown(self):
        tape_job.cache_clear()
        theme.configure(False)

    def pixels(self, screen, rect=None):
        return pygame.image.tostring(screen.subsurface(rect) if rect else screen, 'RGB')

    def tape(self, phase, compact=False, seed=0):
        screen = pygame.Surface((720, 280 if compact else 400))
        screen.fill(theme.SURFACE)
        _tape(screen, tape_frame(phase, seed), compact, seed)
        return screen

    def test_all_eight_programs_compute_real_byte_results_and_vary_inputs(self):
        with patch('gui.tape_program._message_starts', return_value=False):
            tape_job.cache_clear()
            self.assertEqual(tuple(tape_job(i).name for i in range(8)), PROGRAMS)
            self.assertEqual(tuple(tape_job(i).result for i in range(8)), (1, 20, 6, 105, 2, 2, 72, 0))
            results = set()
            for index in range(2048):
                job = tape_job(index)
                a, *rest = job.inputs
                b = rest[0] if rest else 0
                expected = {'COUNT': (a + 1) & 255, 'ADD': a + b, 'MULT': a * b,
                            'XOR': a ^ b, 'SHIFT': (a << 1) & 255, 'FIB': a + b,
                            'ASCII': a, 'PARITY': a.bit_count() & 1}[job.name]
                self.assertEqual(job.result, expected)
                self.assertTrue(0 <= job.result <= 255)
                self.assertNotEqual(job.prompt, job.answer)
                results.add(job.result)
            self.assertGreater(len(results), 150)
            self.assertEqual(tape_job.cache_info().maxsize, 128)
            self.assertLessEqual(tape_job.cache_info().currsize, 128)
            with self.assertRaises(FrozenInstanceError):
                tape_job(0).result = 99
            with self.assertRaises(ValueError):
                tape_job(-1)

    def test_read_scan_punch_hold_and_feed_are_ordered_continuous_and_bounded(self):
        self.assertEqual(tape_frame(-10), tape_frame(0))
        self.assertEqual([tape_frame(p).stage for p in (0, .5, 4.5, 5)], ['READ', 'RUN', 'PUNCH', 'HOLD'])
        for index in range(8):
            frame = tape_frame(.5 + (index + .4) / 2)
            states = relay_states(frame.scan_phase)
            self.assertEqual(states[index], 1)
            self.assertEqual(sum(s > 0 for s in states), 1)
        positions = []
        for tick in range(3601):
            phase = tick / 100
            frame = tape_frame(phase)
            positions.append(frame.position)
            self.assertTrue(frame.index <= frame.position <= frame.index + 1)
            self.assertEqual(frame.result_ready, frame.stage in ('PUNCH', 'HOLD'))
            self.assertEqual(frame.last_printable, frame.index if frame.result_ready else frame.index - 1)
            self.assertEqual(frame.scan_phase is not None, frame.stage == 'RUN')
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(tape_frame(4.5).position, 0)
        self.assertEqual(tape_frame(4.75).position, .5)
        self.assertEqual(tape_frame(5).position, 1)
        self.assertEqual(tape_frame(6 - 1e-8).position, tape_frame(6).position)

    def test_paper_punches_only_completed_results_and_preserves_history(self):
        for compact in (False, True):
            paper = tape_geometry(compact)
            for phase, expected in ((0, None), (4.49, None), (5, 1), (6, 1), (11, 20)):
                screen = self.tape(phase, compact)
                byte = 0
                for bit in range(8):
                    color = screen.get_at((paper.x + 24 + bit * 10, paper.y + 7))[:3]
                    if color == DARK:
                        byte |= 1 << (7 - bit)
                    else:
                        self.assertEqual(color, PAPER)
                self.assertEqual(byte, expected or 0)
            before = self.tape(5.999999, compact)
            after = self.tape(6, compact)
            self.assertEqual(self.pixels(before, paper), self.pixels(after, paper))
            # The next result pushes down the previous byte rather than changing it.
            screen = self.tape(11, compact)
            byte = sum((1 << (7 - bit)) for bit in range(8)
                       if screen.get_at((paper.x + 24 + bit * 10, paper.y + 21))[:3] == DARK)
            self.assertEqual(byte, 1)

    def test_low_byte_band_and_every_reading_fit_inside_cabinet_with_padding(self):
        for compact in (False, True):
            height = 280 if compact else 400
            cabinet = pygame.Rect(20, 20, 680, height - 40)
            output, lamps = relay_output_geometry(compact)
            self.assertTrue(cabinet.contains(output.inflate(16, 16)))
            bank = pygame.Rect(34, 62, 482, height - 128)
            self.assertFalse(output.colliderect(bank))
            self.assertTrue(all(bank.contains(cell) for cell in relay_geometry(compact)))
            self.assertTrue(pygame.Rect(540, 62, 136, height - 128).contains(tape_geometry(compact)))
            for i, (x, y) in enumerate(lamps):
                self.assertTrue(output.contains(pygame.Rect(x - 8, y - 8, 17, 17)))
                label = _font(10).render(str(7 - i), True, theme.TEXT)
                self.assertTrue(output.contains(label.get_rect(center=(x, output.y + 8))))
            label = _font(12).render('LOW BYTE', True, theme.TEXT)
            self.assertTrue(output.contains(label.get_rect(topleft=(45, output.centery - 7))))
            value = _font(12).render('255 / 255', True, theme.TEXT)
            self.assertTrue(output.contains(value.get_rect(center=(608, output.centery))))

    def test_program_labels_and_equations_fit_the_tape_module(self):
        with patch('gui.tape_program._message_starts', return_value=False):
            tape_job.cache_clear()
            for index in range(1024):
                job = tape_job(index)
                self.assertLessEqual(_font(20).size(job.name)[0], 108)
                for text in (job.prompt, job.answer):
                    self.assertLessEqual(_font(14).size(text)[0], 108)

    def test_rare_message_uses_genuine_odds_and_deterministic_ascii_bytes(self):
        self.assertEqual(MESSAGE_ODDS, 1 << 16)
        self.assertFalse(_message_starts(0, 0))
        self.assertTrue(_message_starts(0, RARE_TEST_SEED))
        jobs = [tape_job(i, RARE_TEST_SEED) for i in range(len(_SECRET_MESSAGE))]
        self.assertTrue(all(job.tag == '?' and job.name == 'ASCII' for job in jobs))
        self.assertEqual(''.join(chr(job.result) for job in jobs), _SECRET_MESSAGE)
        self.assertEqual(jobs, [tape_job(i, RARE_TEST_SEED) for i in range(len(jobs))])
        self.assertNotEqual(tape_job(len(jobs), RARE_TEST_SEED).tag, '?')
        for index, job in enumerate(jobs):
            self.assertEqual(tape_frame(index * JOB_PHASE + 5, RARE_TEST_SEED).job, job)
        # Resampling the renderer never rolls the lottery again.
        animation = MachineAnimation(phase=5, demo_seed=RARE_TEST_SEED)
        before = asdict(animation)
        screen = pygame.Surface((720, 400))
        with patch('random.getrandbits', side_effect=AssertionError('draw-time randomness')):
            for _ in range(5):
                draw_era_machine(screen, screen.get_rect(), 2, 128, animation)
        self.assertEqual(before, asdict(animation))

    def test_rendering_is_clipped_and_demo_does_not_depend_on_currency(self):
        for compact in (False, True):
            height = 280 if compact else 400
            panel = pygame.Rect(540, 62, 136, height - 128)
            for seed in (0, RARE_TEST_SEED):
                animation = MachineAnimation(phase=5, demo_seed=seed)
                first = pygame.Surface((720, height)); first.fill(theme.SURFACE)
                second = first.copy()
                draw_era_machine(first, first.get_rect(), 2, 128, animation)
                draw_era_machine(second, second.get_rect(), 2, 129, animation)
                self.assertEqual(self.pixels(first, panel), self.pixels(second, panel))
                output, _ = relay_output_geometry(compact)
                self.assertNotEqual(self.pixels(first, output), self.pixels(second, output))
                screen = pygame.Surface((720, height)); screen.fill((255, 0, 255))
                clip = pygame.Rect(570, 150, 10, 15)
                screen.set_clip(clip)
                _tape(screen, tape_frame(5, seed), compact, seed)
                self.assertEqual(screen.get_clip(), clip)
                self.assertEqual(screen.get_at((569, 155))[:3], (255, 0, 255))
                self.assertEqual(screen.get_at((580, 155))[:3], (255, 0, 255))

    def test_rare_demo_is_session_only_and_reduced_motion_keeps_actual_readings_live(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(CONFIG, SAVE_FILE=str(Path(directory) / 'test.json')):
            with patch('gui.random.getrandbits', return_value=RARE_TEST_SEED) as seed:
                game = BitByBitGame()
            seed.assert_called_once_with(64)
            game.showing_tutorial = False
            game.state.current_era = 2
            game.state.bits = 128
            game.machine_animation.phase = 5
            game.reduced_motion_mode = True
            for size in ((1200, 800), (960, 640)):
                game.handle_window_resize(*size)
                game.update(.1); game.draw()
                rect = game.accumulator_click_rect
                before = self.pixels(game.screen, rect)
                for _ in range(60):
                    game.update(.1)
                game.draw()
                self.assertEqual(before, self.pixels(game.screen, rect))
                game.state.bits += 1
                game.update(.1); game.draw()
                self.assertNotEqual(before, self.pixels(game.screen, rect))
                self.assertEqual(game.machine_animation.phase, 5)
                self.assertEqual(game.machine_animation.demo_seed, RARE_TEST_SEED)
            game.save_game()
            self.assertIsNone(game.last_save_error)
            self.assertNotIn('demo_seed', (Path(directory) / 'test.json').read_text())


if __name__ == '__main__':
    unittest.main()
