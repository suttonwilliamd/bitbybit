"""A four-valve signal instrument with a quiet, scrolling demonstration scope.

Illustrative waveforms/electrons are not a circuit simulator or earnings meter.
Only the inset LOW BYTE register reads currency. No clocks, random draws or saves.
"""
from functools import lru_cache
import math
import pygame
from . import theme as t
from .machines import MachineAnimation, _label, _line, _panel, _screw, output_bits

TAU = math.tau
DARK = (20, 29, 28)
COPPER = (133, 110, 75)
METAL = (139, 153, 143)
STAGES = ('OSCILLATOR', 'AMPLIFIER', 'RECTIFIER', 'DIVIDE / 2')
NOTES = ('SINE SOURCE', 'SATURATED GAIN', 'HALF WAVE', 'HALF RATE')


def tube_geometry(compact=False):
    return tuple(pygame.Rect(x - 28, 81 if compact else 92, 56, 94 if compact else 190)
                 for x in (88, 192, 296, 400))


def socket_rect(glass):
    return pygame.Rect(glass.centerx - 37, glass.bottom - 3, 74, 24)


def scope_geometry(compact=False):
    return pygame.Rect(494, 122 if compact else 126, 174, 48 if compact else 138)


def output_geometry(compact=False):
    return pygame.Rect(40, (280 if compact else 400) - 64, 640, 36)


def stage_values(theta):
    source = math.sin(theta)
    amplifier = math.tanh(2.2 * source) / math.tanh(2.2)
    return .35 * source, amplifier, max(0, amplifier), float(math.sin(theta / 2) >= 0)


def selected_stage(phase):
    return math.floor(max(0, phase) / 5) % 4


def conduction_levels(theta):
    values = stage_values(theta)
    return ((values[0] / .35 + 1) / 2, (values[1] + 1) / 2, values[2], values[3])


def scope_points(phase, compact=False, channel=None):
    """A bounded rolling window of three source periods, newest sample at right."""
    channel = selected_stage(phase) if channel is None else channel
    rect = scope_geometry(compact)
    now = phase * TAU * .65
    return tuple((rect.x + 4 + i, rect.centery - stage_values(now - 3 * TAU *
                  (1 - i / (rect.width - 9)))[channel] * (rect.height - 10) / 2)
                 for i in range(rect.width - 8))


def signal_paths(compact=False):
    """Output socket pin to the next valve's input pin, via the chassis wiring."""
    tubes = tube_geometry(compact)
    y = socket_rect(tubes[0]).bottom
    return tuple(((a.centerx + 24, y), (a.centerx + 42, y), (a.centerx + 42, y - 12),
                  (b.centerx - 42, y - 12), (b.centerx - 42, y), (b.centerx - 24, y))
                 for a, b in zip(tubes, tubes[1:]))


def probe_path(phase, compact=False):
    glass = tube_geometry(compact)[selected_stage(phase)]
    y = (280 if compact else 400) - 67
    return ((glass.centerx + 24, socket_rect(glass).bottom), (glass.centerx + 24, y),
            (470, y), (470, scope_geometry(compact).centery), (480, scope_geometry(compact).centery))


def flow_segment(path, phase):
    lengths = [math.dist(a, b) for a, b in zip(path, path[1:])]
    start = ((phase * .6) % 1) * (sum(lengths) + 18) - 18
    result, traveled = [], 0
    for a, b, length in zip(path, path[1:], lengths):
        lo, hi = max(0, start, traveled), min(sum(lengths), start + 18, traveled + length)
        if hi > lo:
            for distance in (lo, hi):
                fraction = (distance - traveled) / length
                point = (a[0] + (b[0] - a[0]) * fraction, a[1] + (b[1] - a[1]) * fraction)
                if not result or point != result[-1]:
                    result.append(point)
        traveled += length
    return tuple(result)


@lru_cache(maxsize=8)
def _layers(compact, palette):
    height = 280 if compact else 400
    back = pygame.Surface((720, height), pygame.SRCALPHA)
    front = pygame.Surface((720, height), pygame.SRCALPHA)
    _panel(back, (8, 9, 704, height - 18), (49, 58, 53), (120, 135, 118), 14)
    _panel(back, (20, 20, 680, height - 40), (29, 39, 36), (73, 91, 79), 8)
    _label(back, 'THERMIONIC LAB', (42, 32), 18, t.SAGE)
    if not compact:
        _label(back, '4 VALVES / DEMO SIGNAL', (432, 36), 13, t.MUTED)
    _panel(back, (30, 66, 430, height - 136), DARK, (78, 98, 85), 7)
    _panel(back, (480, 66, 202, height - 136), (48, 58, 49), (113, 129, 107), 7)
    _label(back, 'DEMO SCOPE', (581, 81), 12, t.MUTED, center=True)
    plot = scope_geometry(compact)
    _panel(back, plot.inflate(8, 8), (14, 27, 23), (93, 113, 91), 7)
    for i in range(1, 6):
        x = plot.x + i * plot.width / 6
        _line(back, (33, 49, 40), (x, plot.y + 3), (x, plot.bottom - 3), 1)
    for i in range(1, 4):
        y = plot.y + i * plot.height / 4
        _line(back, (39, 55, 44), (plot.x + 3, y), (plot.right - 3, y), 1)
    for path in signal_paths(compact):
        pygame.draw.lines(back, COPPER, False, path, 2)
    for index, glass in enumerate(tube_geometry(compact)):
        cx = glass.centerx
        # Clear shouldered glass envelope, silver getter patch, steel support rods.
        pygame.draw.rect(back, (37, 49, 46), glass, border_radius=27)
        for x in (cx - 20, cx + 20):
            _line(back, (89, 107, 96), (x, glass.y + 28), (x, glass.bottom - 8), 2)
        pygame.draw.ellipse(front, (92, 109, 100), (cx - 17, glass.y + 9, 34, 10))
        # Two vented plate assemblies leave the central cathode/grid visible.
        top, bottom = glass.y + (23 if compact else 37), glass.bottom - 31
        for x in (cx - 18, cx + 6):
            pygame.draw.rect(front, (101, 115, 105), (x, top, 12, bottom - top), border_radius=2)
            for y in range(top + 5, bottom - 3, 9 if compact else 15):
                pygame.draw.rect(front, (39, 52, 46), (x + 3, y, 6, 3), border_radius=1)
        for y in range(top + 4, bottom, 11 if compact else 20):
            _line(front, (126, 130, 104), (cx - 6, y), (cx + 6, y), 1)
        # Heater stays steadily warm. No pulsing bloom or large-area flashing.
        pygame.draw.ellipse(front, (74, 56, 36), (cx - 13, glass.bottom - 26, 26, 16))
        pygame.draw.lines(front, (234, 177, 109), False,
                          [(cx - 8, glass.bottom - 16), (cx - 4, glass.bottom - 22),
                           (cx, glass.bottom - 16), (cx + 4, glass.bottom - 22),
                           (cx + 8, glass.bottom - 16)], 2)
        pygame.draw.rect(front, (113, 138, 128), glass, 2, border_radius=27)
        _line(front, (158, 176, 164), (glass.x + 8, glass.y + 29), (glass.x + 8, glass.bottom - 25), 2)
        _line(front, (76, 98, 87), (glass.right - 7, glass.y + 35), (glass.right - 7, glass.bottom - 30), 1)
        if not compact:
            _label(front, '6SN7', (cx, glass.bottom - 39), 10, t.MUTED, center=True)
        socket = socket_rect(glass)
        _panel(front, (cx - 31, glass.bottom - 4, 62, 9), (60, 49, 38), (123, 105, 75), 3)
        _panel(front, (socket.x, glass.bottom + 4, socket.width, 13), (150, 147, 120), (77, 89, 73), 4)
        for x in (cx - 24, cx - 8, cx + 8, cx + 24):
            _line(front, COPPER, (x, glass.bottom + 14), (x, socket.bottom), 2)
        tag = f'V{index + 1} ' + ('OSC', 'AMP', 'RECT', '/2')[index]
        _label(front, tag, (cx, glass.bottom + (28 if compact else 33)), 11 if compact else 13,
               t.MUTED, center=True)
    output = output_geometry(compact)
    _panel(front, output, DARK, (78, 98, 85), 4)
    _label(front, 'LOW BYTE', (52, output.centery - 7), 12, t.MUTED)
    for i in range(8):
        _label(front, str(7 - i), (250 + i * 27, output.y + 8), 10, t.MUTED, center=True)
    for x in (29, 691):
        for y in (28, height - 34):
            _screw(front, (x, y))
    return back, front


def draw_vacuum_instrument(screen, rect, amount, animation=None):
    if rect.width <= 0 or rect.height <= 0:
        return
    animation = animation if animation is not None else MachineAnimation()
    phase = animation.phase
    compact = rect.height < 180
    palette = (t.TEXT, t.MUTED, t.SAGE, t.AMBER, t.BORDER)
    back, front = _layers(compact, palette)
    canvas = back.copy()
    selected = selected_stage(phase)
    levels = conduction_levels(phase * TAU * .65)
    for index, glass in enumerate(tube_geometry(compact)):
        level = levels[index]
        if level > .12:
            for packet in range(3):
                fraction = (phase * .8 + packet / 3) % 1
                x = glass.centerx + (-1 if packet % 2 else 1) * (1 + fraction * 3)
                y = glass.bottom - 29 - fraction * (glass.height - (54 if compact else 70))
                pygame.draw.circle(canvas, (193, 168, 114), (round(x), round(y)), 2)
    paths = signal_paths(compact)
    for index, path in enumerate(paths):
        segment = flow_segment(path, phase + index * .3)
        if levels[index] > .15 and len(segment) > 1:
            pygame.draw.lines(canvas, t.SAGE, False, segment, 2)
    probe = probe_path(phase, compact)
    pygame.draw.lines(canvas, COPPER, False, probe, 2)
    segment = flow_segment(probe, phase)
    if levels[selected] > .15 and len(segment) > 1:
        pygame.draw.lines(canvas, t.SAGE, False, segment, 2)
    canvas.blit(front, (0, 0))
    plot = scope_geometry(compact)
    points = scope_points(phase, compact)
    pygame.draw.lines(canvas, t.SAGE, False, points, 2)
    pygame.draw.circle(canvas, t.TEXT, (round(points[-1][0]), round(points[-1][1])), 2)
    pygame.draw.circle(canvas, COPPER, (480, plot.centery), 3)
    _label(canvas, STAGES[selected], (581, 103), 18, t.SAGE, center=True)
    _label(canvas, NOTES[selected], (581, 183 if compact else 284), 11 if compact else 13,
           t.MUTED, center=True)
    for index in range(4):
        x, y = 514 + index * 44, 201 if compact else 312
        pygame.draw.circle(canvas, DARK, (x, y), 7)
        pygame.draw.circle(canvas, t.SAGE if index == selected else (75, 92, 77), (x, y), 4)
        _label(canvas, str(index + 1), (x - 12, y), 10, t.MUTED, center=True)
    glass = tube_geometry(compact)[selected]
    _line(canvas, t.SAGE, (glass.centerx - 31, glass.y - 5), (glass.centerx + 31, glass.y - 5), 2)
    output = output_geometry(compact)
    for i, on in enumerate(output_bits(amount)):
        center = (250 + i * 27, output.bottom - 10)
        pygame.draw.circle(canvas, DARK, center, 7)
        pygame.draw.circle(canvas, t.SAGE if on else (57, 75, 63), center, 5)
        if on:
            pygame.draw.circle(canvas, t.TEXT, center, 2)
    _label(canvas, f'0x{int(amount) & 255:02X}', (615, output.centery), 18, t.SAGE, center=True)
    screen.blit(pygame.transform.smoothscale(canvas, rect.size), rect)
