"""Fictional folded-space router: cosmic scenery, real byte-XOR demonstrations.

Stars do not flash. Packets, accretion streams and orbit markers use the existing
presentation clock. The separate LOW BYTE header alone reads player currency.
"""
from dataclasses import dataclass
from functools import lru_cache
import math
import pygame
from . import theme as t
from .machines import MachineAnimation, _label, _line, _panel, _screw

DARK = (14, 21, 29)
GOLD = (188, 155, 103)
CYCLE = 10.0
ENDS = (3.0, 5.0, 8.0, CYCLE)
STAGES = ('UPLINK', 'FOLD', 'RETURN', 'HOLD')


@lru_cache(maxsize=128)
def cosmic_job(index):
    if index < 0:
        raise ValueError('Demo job index must be nonnegative')
    a = (73 * index + 0x35) & 255
    raw = (151 * index + 0xA6) & 255
    shift = (index // 64) % 8
    b = ((raw << shift) | (raw >> ((8 - shift) % 8))) & 255
    return a, b, a ^ b


@dataclass(frozen=True)
class CosmicFrame:
    index: int
    stage: int
    progress: float
    inputs: tuple[int, int]
    answer: int

    @property
    def result(self):
        return self.answer if self.stage >= 2 else None

    @property
    def input_position(self):
        eased = self.progress ** 2 * (3 - 2 * self.progress)
        return .55 * eased if self.stage == 0 else .55 + .45 * eased if self.stage == 1 else 1.0

    @property
    def output_position(self):
        return 0.0 if self.stage < 2 else self.progress ** 2 * (3 - 2 * self.progress) if self.stage == 2 else 1.0


def cosmic_frame(phase):
    phase = max(0.0, phase)
    index = math.floor(phase / CYCLE)
    local = phase % CYCLE
    stage = next(i for i, end in enumerate(ENDS) if local < end)
    start = 0 if stage == 0 else ENDS[stage - 1]
    a, b, answer = cosmic_job(index)
    return CosmicFrame(index, stage, (local - start) / (ENDS[stage] - start), (a, b), answer)


def engine_geometry(compact=False):
    return (278, 143 if compact else 195), 130 if compact else 198, 24 if compact else 40


def orbit_point(angle, phase, compact=False, scale=1.0, aspect=.44):
    (cx, cy), radius, _ = engine_geometry(compact)
    tilt = .065 * math.sin(phase * .13)
    x, y = radius * scale * math.cos(angle), radius * scale * aspect * math.sin(angle)
    return cx + x * math.cos(tilt) - y * math.sin(tilt), cy + x * math.sin(tilt) + y * math.cos(tilt)


def route_point(position, branch, phase, compact=False):
    """Two inward spirals and one outward spiral; points stay on their drawn route."""
    _, radius, _ = engine_geometry(compact)
    if branch == 2:
        r, angle = 6 + (radius - 6) * position, -.65 - 1.8 * (1 - position)
    else:
        r, angle = radius - (radius - 6) * position, (3.8, .65)[branch] + 1.8 * position
    return orbit_point(angle, phase, compact, r / radius)


def route_path(branch, phase, compact=False):
    return tuple(route_point(i / 64, branch, phase, compact) for i in range(65))


def timeline_geometry(compact=False):
    return tuple(pygame.Rect(42 + i * 162, (280 if compact else 400) - 61, 154, 30) for i in range(4))


def balance_text(amount):
    return f'LOW BYTE 0x{int(amount) & 255:02X}'


@lru_cache(maxsize=8)
def _housing(compact, palette):
    height = 280 if compact else 400
    surface = pygame.Surface((720, height), pygame.SRCALPHA)
    _panel(surface, (8, 9, 704, height - 18), (35, 37, 47), (116, 117, 132), 18)
    _panel(surface, (20, 20, 680, height - 40), (23, 27, 38), (69, 77, 96), 10)
    _label(surface, 'COSMIC FOLD ENGINE', (42, 33), 18, t.SAGE)
    _panel(surface, (34, 66, 486, height - 136), DARK, (64, 78, 95), 8)
    _panel(surface, (532, 66, 152, height - 136), DARK, (64, 78, 95), 8)
    # Fixed integer placement, not randomness or blinking background effects.
    for i in range(36):
        x = 46 + ((i * 137) ^ (i * i * 43) ^ (i << 7)) % 460
        y = 78 + ((i * 73) ^ (i * i * 19) ^ (i << 3)) % (height - 160)
        color = ((62, 74, 86), (82, 96, 101), (111, 118, 115))[i % 3]
        pygame.draw.circle(surface, color, (x, y), 1)
        if i % 9 == 0:
            _line(surface, color, (x - 2, y), (x + 2, y), 1)
    _label(surface, 'FICTIONAL ROUTING DEMO', (48, 77), 11, t.MUTED)
    _label(surface, 'A XOR B', (608, 80), 14, t.MUTED, center=True)
    _line(surface, (71, 84, 102), (548, 146 if compact else 173), (668, 146 if compact else 173), 1)
    _label(surface, 'DEMO ONLY', (608, 196 if compact else 243), 10 if compact else 12, t.MUTED, center=True)
    if not compact:
        _label(surface, 'RECENT', (608, 281), 11, t.MUTED, center=True)
        _label(surface, 'ILLUSTRATIVE FOLDED-SPACE ROUTING', (278, 312), 11, t.MUTED, center=True)
    for x in (29, 691):
        for y in (28, height - 34):
            _screw(surface, (x, y))
    return surface


@lru_cache(maxsize=2)
def _disc_bands(compact):
    """Steady dust body: two immutable sets of half-annuli for correct occlusion."""
    (cx, cy), _, _ = engine_geometry(compact)
    inner, outer = (36, 80) if compact else (60, 132)
    bands = []
    for band in range(10):
        r0 = inner + (outer - inner) * band / 10
        r1 = inner + (outer - inner) * (band + 1) / 10
        color = tuple(round(value * (.72 - .34 * band / 9)) for value in GOLD)
        for front in (False, True):
            angles = [math.pi * i / 36 + (0 if front else math.pi) for i in range(37)]
            points = tuple((cx + r * math.cos(angle), cy + r * .34 * math.sin(angle))
                           for r, arc in ((r1, angles), (r0, reversed(angles))) for angle in arc)
            bands.append((points, color, front))
    return tuple(bands)


def _disc(phase, compact):
    (cx, cy), _, _ = engine_geometry(compact)
    inner, outer = (36, 80) if compact else (60, 132)
    segments = []
    for arm in range(3):
        points = []
        for i in range(49):
            u = i / 48
            radius = inner + (outer - inner) * u
            angle = phase * .65 + arm * math.tau / 3 + u * math.tau * 1.2
            points.append((cx + radius * math.cos(angle), cy + radius * .34 * math.sin(angle)))
        for i, (a, b) in enumerate(zip(points, points[1:])):
            fraction = .9 - .4 * i / 48
            color = tuple(round(62 + (value - 62) * fraction) for value in (228, 196, 139))
            segments.append((a, b, color, (a[1] + b[1]) / 2 >= cy))
    return segments


def _packet(canvas, position, branch, phase, compact, color):
    center, _, horizon = engine_geometry(compact)
    points = [route_point(max(0, position - (7 - i) * .009), branch, phase, compact) for i in range(8)]
    for i, (a, b) in enumerate(zip(points, points[1:])):
        if min(math.dist(center, a), math.dist(center, b)) > horizon + 5:
            shade = tuple(round(DARK[k] + (color[k] - DARK[k]) * (i + 1) / 7) for k in range(3))
            pygame.draw.aaline(canvas, shade, a, b)
    point = points[-1]
    if math.dist(center, point) > horizon + 5:
        pygame.draw.circle(canvas, color, tuple(round(v) for v in point), 4)
        pygame.draw.circle(canvas, t.TEXT, tuple(round(v) for v in point), 2)


def draw_cosmic_engine(screen, rect, amount, animation=None):
    if rect.width <= 0 or rect.height <= 0:
        return
    animation = animation if animation is not None else MachineAnimation()
    phase = animation.phase
    compact = rect.height < 180
    frame = cosmic_frame(phase)
    canvas = _housing(compact, (t.TEXT, t.MUTED, t.SAGE, t.AMBER, t.BORDER)).copy()
    center, _, horizon = engine_geometry(compact)
    for scale, aspect in ((1, .44), (.9, .52)):
        orbit = [orbit_point(i * math.tau / 96, phase, compact, scale, aspect) for i in range(97)]
        pygame.draw.aalines(canvas, (64, 78, 96), False, orbit)
    for branch in range(3):
        pygame.draw.aalines(canvas, (58, 76, 82), False, route_path(branch, phase, compact))
    for i in range(8):
        point = orbit_point(i * math.tau / 8 + phase * .14, phase, compact)
        pygame.draw.circle(canvas, (112, 132, 137), tuple(round(v) for v in point), 2)
    disc = _disc(phase, compact)
    for points, color, front in _disc_bands(compact):
        if not front:
            pygame.draw.polygon(canvas, color, points)
    for a, b, color, front in disc:
        if not front:
            pygame.draw.aaline(canvas, color, a, b)
    pygame.draw.circle(canvas, (7, 11, 18), center, horizon)
    pygame.draw.circle(canvas, GOLD, center, horizon + 3, 2)
    pygame.draw.circle(canvas, (107, 97, 80), center, horizon + 6, 1)
    for points, color, front in _disc_bands(compact):
        if front:
            pygame.draw.polygon(canvas, color, points)
    for a, b, color, front in disc:
        if front:
            pygame.draw.aaline(canvas, color, a, b)
    for branch, text in enumerate(('A', 'B', 'OUT')):
        point = route_point(1 if branch == 2 else 0, branch, phase, compact)
        pygame.draw.circle(canvas, DARK, tuple(round(v) for v in point), 7)
        pygame.draw.circle(canvas, t.SAGE if branch == 2 and frame.stage == 3 else GOLD, tuple(round(v) for v in point), 5, 1)
        _label(canvas, text, (point[0] + (-15 if branch == 0 else 18), point[1] - 12), 11, t.MUTED, center=True)
    if frame.stage < 2:
        for branch, color in enumerate((t.SAGE, t.AMBER)):
            _packet(canvas, frame.input_position, branch, phase, compact, color)
    elif frame.stage == 2:
        _packet(canvas, frame.output_position, 2, phase, compact, t.SAGE)
    for i, value in enumerate(frame.inputs):
        _label(canvas, f'{"AB"[i]} 0x{value:02X}', (550, (96 + i * 25) if compact else (103 + i * 38)),
               16 if compact else 18, t.SAGE if i == 0 else t.AMBER)
    answer = '= ----' if frame.result is None else f'= 0x{frame.result:02X}'
    _label(canvas, answer, (608, 170 if compact else 204), 20 if compact else 26,
           t.MUTED if frame.result is None else t.TEXT, center=True)
    if not compact:
        for i in range(4):
            previous = frame.index - 4 + i
            text = '--' if previous < 0 else f'{cosmic_job(previous)[2]:02X}'
            _label(canvas, text, (557 + i * 34, 305), 13, t.MUTED, center=True)
    _label(canvas, balance_text(amount), (535, 36), 13, t.SAGE)
    for i, box in enumerate(timeline_geometry(compact)):
        _panel(canvas, box, (47, 54, 65) if i == frame.stage else DARK,
               t.SAGE if i == frame.stage else (64, 78, 95), 4)
        _label(canvas, STAGES[i], (box.centerx, box.centery - 3), 13,
               t.TEXT if i == frame.stage else t.MUTED, center=True)
        if i == frame.stage:
            pygame.draw.rect(canvas, t.AMBER, (box.x + 5, box.bottom - 6, round((box.width - 10) * frame.progress), 2))
    screen.blit(pygame.transform.smoothscale(canvas, rect.size), rect)
