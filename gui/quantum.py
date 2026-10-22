"""A driven single-qubit interferometer, not a source of currency or real samples.

Normalized complex amplitudes drive the Bloch vector and ideal Z probabilities.
The cryostat/control pulses are schematic; all motion uses the existing GUI clock.
"""
from dataclasses import dataclass
from functools import lru_cache
import cmath
import math
import pygame
from . import theme as t
from .machines import MachineAnimation, _label, _line, _panel, _screw
from .vacuum import flow_segment

DARK = (19, 29, 31)
GOLD = (174, 150, 105)
WIRE = (104, 129, 136)
CYCLE = 16.0
ENDS = (1.0, 4.0, 9.0, 13.0, CYCLE)
STAGES = ('RESET', 'RY +90', 'PHASE', 'RY -90', 'READ P')
ROOT_HALF = math.sqrt(.5)


def target_phase(index):
    return math.tau * ((1 / 3 + index * .3819660112501051) % 1)


def rotate_y(state, angle):
    a, b = state
    c, s = math.cos(angle / 2), math.sin(angle / 2)
    return c * a - s * b, s * a + c * b


def _final_state(index):
    phase = cmath.exp(1j * target_phase(index))
    return (1 + phase) / 2, (phase - 1) / 2


@dataclass(frozen=True)
class QuantumFrame:
    index: int
    stage: int
    progress: float
    amplitudes: tuple[complex, complex]
    target: float

    @property
    def probabilities(self):
        return tuple(abs(value) ** 2 for value in self.amplitudes)

    @property
    def bloch(self):
        a, b = self.amplitudes
        product = a.conjugate() * b
        return 2 * product.real, 2 * product.imag, abs(a) ** 2 - abs(b) ** 2


def quantum_frame(phase):
    phase = max(0.0, phase)
    index = math.floor(phase / CYCLE)
    local = phase % CYCLE
    stage = next(i for i, end in enumerate(ENDS) if local < end)
    start = 0 if stage == 0 else ENDS[stage - 1]
    progress = (local - start) / (ENDS[stage] - start)
    eased = progress * progress * (3 - 2 * progress)
    target = target_phase(index)
    if stage == 0:
        # An illustrative preparation path, not a modeled physical reset channel.
        a, b = _final_state(index - 1) if index else (1 + 0j, 0j)
        a, b = a * (1 - eased) + eased, b * (1 - eased)
        norm = math.sqrt(abs(a) ** 2 + abs(b) ** 2)
        state = a / norm, b / norm
    elif stage == 1:
        state = rotate_y((1 + 0j, 0j), math.pi / 2 * eased)
    elif stage == 2:
        state = ROOT_HALF + 0j, ROOT_HALF * cmath.exp(1j * target * eased)
    elif stage == 3:
        state = rotate_y((ROOT_HALF + 0j, ROOT_HALF * cmath.exp(1j * target)), -math.pi / 2 * eased)
    else:
        state = _final_state(index)
    return QuantumFrame(index, stage, progress, state, target)


def sphere_geometry(compact=False):
    return (386, 146 if compact else 192), 53 if compact else 90


def project(vector, compact=False):
    (cx, cy), radius = sphere_geometry(compact)
    x, y, z = vector
    return cx + radius * (math.sqrt(3) / 2 * x + .5 * y), cy + radius * (.25 * x - math.sqrt(3) / 4 * y - math.sqrt(3) / 2 * z)


def _depth(vector):
    x, y, z = vector
    return math.sqrt(3) / 4 * x - .75 * y + .5 * z


def probability_geometry(compact=False):
    return tuple(pygame.Rect(534, y, 136, 12 if compact else 16)
                 for y in ((114, 164) if compact else (130, 200)))


def timeline_geometry(compact=False):
    return tuple(pygame.Rect(42 + i * 130, (280 if compact else 400) - 61, 122, 30) for i in range(5))


def cryostat_geometry(compact=False):
    levels = (102, 125, 148, 171) if compact else (112, 163, 214, 265)
    plates = tuple(pygame.Rect(145 - width // 2, y, width, 12)
                   for width, y in zip((156, 134, 108, 86), levels))
    chip = pygame.Rect(123, 190 if compact else 288, 44, 17 if compact else 24)
    paths = []
    for i, x in enumerate((96, 124, 166, 194)):
        path = [(x, 92)]
        path.extend((145 + (x - 145) * (1 - level * .16), plate.centery) for level, plate in enumerate(plates))
        path.append((chip.x + 7 + i * 10, chip.y))
        paths.append(tuple(path))
    return plates, chip, tuple(paths)


def balance_text(amount):
    return f'LOW BYTE 0x{int(amount) & 255:02X}'


@lru_cache(maxsize=8)
def _housing(compact, palette):
    height = 280 if compact else 400
    surface = pygame.Surface((720, height), pygame.SRCALPHA)
    _panel(surface, (8, 9, 704, height - 18), (37, 47, 52), (111, 132, 141), 18)
    _panel(surface, (20, 20, 680, height - 40), (25, 34, 40), (65, 87, 94), 10)
    _label(surface, 'QUANTUM INTERFEROMETER', (42, 33), 18, t.SAGE)
    for x, width in ((34, 218), (266, 240), (520, 166)):
        _panel(surface, (x, 66, width, height - 136), DARK, (67, 89, 96), 7)
    _label(surface, 'CRYOSTAT / Q0', (143, 79), 12, t.MUTED, center=True)
    _label(surface, 'BLOCH / DEMO', (386, 79), 12, t.MUTED, center=True)
    _label(surface, 'IDEAL PROB.', (603, 79), 12, t.MUTED, center=True)
    plates, chip, paths = cryostat_geometry(compact)
    for x in (74, 216):
        _line(surface, (88, 108, 113), (x, 96), (x, plates[-1].bottom + 3), 3)
    for plate in plates:
        pygame.draw.rect(surface, (106, 91, 64), plate.move(0, 4), border_radius=5)
        pygame.draw.ellipse(surface, GOLD, plate)
        pygame.draw.ellipse(surface, (217, 193, 144), plate, 1)
        for x in (plate.x + 15, plate.right - 15):
            pygame.draw.circle(surface, (77, 75, 61), (x, plate.centery), 2)
    for path in paths:
        pygame.draw.lines(surface, WIRE, False, path, 2)
        pygame.draw.circle(surface, GOLD, path[0], 3)
    _panel(surface, chip, (65, 79, 94), GOLD, 3)
    _label(surface, 'Q0', chip.center, 11, t.TEXT, center=True)
    for x in (chip.x - 5, chip.right + 4):
        for y in (chip.y + 4, chip.bottom - 4):
            _line(surface, GOLD, (x - 3, y), (x + 3, y), 2)
    center, radius = sphere_geometry(compact)
    pygame.draw.circle(surface, (79, 103, 112), center, radius, 1)
    for plane in range(3):
        for i in range(96):
            pair = []
            vectors = []
            for step in (i, i + 1):
                angle = math.tau * step / 96
                vector = [math.cos(angle), math.sin(angle)]
                vector.insert(plane, 0)
                vectors.append(vector); pair.append(project(vector, compact))
            color = (72, 100, 106) if _depth(vectors[0]) >= 0 else (42, 61, 69)
            pygame.draw.aaline(surface, color, *pair)
    north, south = project((0, 0, 1), compact), project((0, 0, -1), compact)
    _line(surface, (64, 85, 91), north, south, 1)
    for text, point in (('0', north), ('1', south)):
        _label(surface, text, (point[0] - 13, point[1]), 11, t.MUTED, center=True)
    if not compact:
        _label(surface, 'STATE VECTOR / Q0', (386, 311), 12, t.MUTED, center=True)
        _label(surface, 'NOT EARNINGS', (603, 268), 11, t.MUTED, center=True)
    for i, rect in enumerate(probability_geometry(compact)):
        _panel(surface, rect, (33, 46, 51), (72, 93, 97), 3)
        _label(surface, f'P({i})', (534, rect.y - 23), 14, t.MUTED)
    for x in (29, 691):
        for y in (28, height - 34):
            _screw(surface, (x, y))
    return surface


def draw_quantum_instrument(screen, rect, amount, animation=None):
    if rect.width <= 0 or rect.height <= 0:
        return
    animation = animation if animation is not None else MachineAnimation()
    phase = animation.phase
    frame = quantum_frame(phase)
    compact = rect.height < 180
    canvas = _housing(compact, (t.TEXT, t.MUTED, t.SAGE, t.AMBER, t.BORDER)).copy()
    _, chip, paths = cryostat_geometry(compact)
    # A short control burst travels down a real drawn feed line; never an orbiting electron.
    path = paths[frame.stage % len(paths)]
    segment = flow_segment(path, phase)
    if len(segment) > 1:
        pygame.draw.lines(canvas, t.AMBER, False, segment, 3)
    pygame.draw.rect(canvas, t.SAGE, chip.inflate(6, 6), 1, border_radius=4)
    # Bounded presentation history, reconstructed without saving samples or using a clock.
    history = [project(quantum_frame(max(0, phase - (25 - i) * .055)).bloch, compact) for i in range(26)]
    for i, (a, b) in enumerate(zip(history, history[1:])):
        fraction = .15 + .55 * i / 24
        color = tuple(round(DARK[k] + (t.SAGE[k] - DARK[k]) * fraction) for k in range(3))
        pygame.draw.aaline(canvas, color, a, b)
    center, _ = sphere_geometry(compact)
    point = project(frame.bloch, compact)
    color = t.SAGE if _depth(frame.bloch) >= 0 else t.MUTED
    _line(canvas, color, center, point, 3)
    distance = math.dist(center, point)
    if distance > 8:
        dx, dy = ((point[i] - center[i]) / distance for i in range(2))
        pygame.draw.polygon(canvas, color, (point, (point[0] - dx * 10 - dy * 4, point[1] - dy * 10 + dx * 4),
                                                    (point[0] - dx * 10 + dy * 4, point[1] - dy * 10 - dx * 4)))
    pygame.draw.circle(canvas, color, tuple(round(v) for v in point), 5)
    pygame.draw.circle(canvas, t.TEXT, tuple(round(v) for v in point), 2)
    for probability, bar in zip(frame.probabilities, probability_geometry(compact)):
        fill = bar.inflate(-4, -4)
        fill.width = round(fill.width * max(0, min(1, probability)))
        if fill.width:
            pygame.draw.rect(canvas, t.SAGE, fill, border_radius=2)
        _label(canvas, f'{probability * 100:5.1f}%', (642, bar.y - 15), 14, t.TEXT, center=True)
    _label(canvas, f'phi set {math.degrees(frame.target):.1f} deg', (603, 198 if compact else 240),
           12 if compact else 14, t.AMBER, center=True)
    _label(canvas, balance_text(amount), (535, 36), 13, t.SAGE)
    for i, box in enumerate(timeline_geometry(compact)):
        _panel(canvas, box, (44, 61, 65) if i == frame.stage else DARK,
               t.SAGE if i == frame.stage else (64, 82, 89), 4)
        _label(canvas, STAGES[i], (box.centerx, box.centery - 3), 13, t.TEXT if i == frame.stage else t.MUTED, center=True)
        if i == frame.stage:
            pygame.draw.rect(canvas, t.AMBER, (box.x + 5, box.bottom - 6, round((box.width - 10) * frame.progress), 2))
    screen.blit(pygame.transform.smoothscale(canvas, rect.size), rect)
