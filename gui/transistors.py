"""A discrete-transistor logic card, not a generic modern microchip.

The quiet traveling trace is a labeled demonstration. The output register alone
reads actual currency. Rendering has no clock, gameplay mutations or save state.
"""
from functools import lru_cache
import math
import pygame
from . import theme as t
from .machines import MachineAnimation, _label, _line, _panel, _screw, output_bits

WIDTH = 720
BOARD = (35, 55, 45)
TRACE = (123, 111, 76)
METAL = (166, 178, 167)
DARK = (21, 31, 28)


def transistor_positions(compact=False):
    ys = (100, 160) if compact else (132, 243)
    return tuple((x, y) for y in ys for x in (140, 340, 540))


def signal_paths(compact=False):
    """Trace endpoints meet the collector and the next transistor's base lead."""
    radius = 18 if compact else 23
    return tuple(((x + 18, y + radius + 16), (x + 18, y + radius + 26),
                  (x + 108, y + radius + 26), (x + 108, y + radius + 16),
                  (x + 200, y + radius + 16))
                 for x, y in transistor_positions(compact) if x != 540)


def signal_segment(phase, compact=False):
    """One short, constant-speed segment along existing right-angle copper traces."""
    cycle = (phase * .65) % 4
    path = signal_paths(compact)[int(cycle)]
    lengths = [math.dist(a, b) for a, b in zip(path, path[1:])]
    distance = (cycle % 1) * (sum(lengths) + 24) - 24
    start, end = max(0, distance), min(sum(lengths), distance + 24)
    if end <= start:
        return ()
    points = []
    traveled = 0.0
    for a, b, length in zip(path, path[1:], lengths):
        lo, hi = max(start, traveled), min(end, traveled + length)
        if hi > lo:
            for value in (lo, hi):
                fraction = (value - traveled) / length
                point = (a[0] + (b[0] - a[0]) * fraction,
                         a[1] + (b[1] - a[1]) * fraction)
                if not points or point != points[-1]:
                    points.append(point)
        traveled += length
    return tuple(points)


def _via(surface, point):
    pygame.draw.circle(surface, TRACE, point, 5)
    pygame.draw.circle(surface, DARK, point, 2)


def _resistor(surface, center):
    x, y = center
    _line(surface, METAL, (x - 34, y), (x + 34, y), 3)
    _panel(surface, (x - 22, y - 7, 44, 14), (190, 173, 130), (114, 103, 75), 5)
    for offset, color in ((-13, (94, 65, 43)), (-5, (47, 51, 42)), (3, (148, 95, 52)), (14, (180, 150, 82))):
        _line(surface, color, (x + offset, y - 6), (x + offset, y + 6), 3)


def _transistor(surface, center, index, compact, detail=3):
    x, y = center
    radius = 18 if compact else 23
    for offset in (-18, 0, 18):
        top = (x + offset * .65, y + radius - 6)
        bottom = (x + offset, y + radius + 16)
        _line(surface, (9, 18, 16), (top[0] + 2, top[1] + 2), (bottom[0] + 2, bottom[1] + 2), 5)
        _line(surface, METAL, top, bottom, 3)
        _via(surface, bottom)
    pygame.draw.circle(surface, (17, 30, 23), (x + 4, y + 5), radius + 3)
    pygame.draw.circle(surface, (86, 105, 94), (x, y), radius + 2)
    pygame.draw.circle(surface, (191, 199, 180), (x - 1, y - 1), radius)
    if detail >= 3:
        pygame.draw.circle(surface, (120, 139, 126), (x + 1, y + 1), radius - 3)
        pygame.draw.circle(surface, METAL, (x - 1, y - 2), radius - 4)
        # The metal-can package's locating tab and a restrained machined highlight.
        pygame.draw.polygon(surface, (185, 194, 177),
                            [(x - radius, y - 6), (x - radius - 7, y - 10), (x - radius - 5, y - 16), (x - radius + 3, y - 13)])
        pygame.draw.arc(surface, (216, 221, 201), (x - radius + 3, y - radius + 3, radius * 2 - 6, radius * 2 - 6),
                        .7, 2.7, 2)
    _label(surface, 'NPN', (x, y), 12 if compact else 14, DARK, center=True)
    _label(surface, f'Q{index + 1}', (x + radius + 9, y - 14), 12, t.MUTED)


@lru_cache(maxsize=8)
def _layers(compact, palette, detail=3):
    """Cache only fixed board and parts; palette changes receive distinct entries."""
    height = 280 if compact else 400
    base = pygame.Surface((WIDTH, height), pygame.SRCALPHA)
    parts = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    _panel(base, (8, 8, 704, height - 16), (49, 61, 55), (115, 131, 116), 14)
    _panel(base, (20, 19, 680, height - 43), BOARD, (77, 104, 79), 8)
    _panel(base, (32, 29, 656, 30), (30, 45, 37), (66, 87, 66), 4)
    _label(base, 'SOLID-STATE LOGIC', (46, 34), 18, t.SAGE)
    _label(base, 'DISCRETE / No. 04', (476, 37), 13, t.MUTED)
    for x, title in ((140, 'INPUT'), (340, 'SWITCH'), (540, 'REGISTER')):
        _label(base, title, (x, 72), 12, t.MUTED, center=True)
    # Etched supply rails, through-hole pads and a gold card-edge connector.
    ys = sorted({y for _, y in transistor_positions(compact)})
    for x in (52, 668):
        _line(base, (79, 105, 77), (x, 82), (x, height - 74), 3)
        for y in (87, height - 79):
            _via(base, (x, y))
    for path in signal_paths(compact):
        pygame.draw.lines(base, TRACE, False, path, 3)
    radius = 18 if compact else 23
    for row, y in enumerate(ys):
        _line(base, TRACE, (52, y + radius + 16), (140, y + radius + 16), 3)
        pygame.draw.lines(base, TRACE, False,
                          [(558, y + radius + 16), (644, y + radius + 16), (644, height - 79)], 3)
        for col, x in enumerate((140, 340, 540)):
            _transistor(parts, (x, y), row * 3 + col, compact, detail)
            # The emitter has a separate return rail, not a disconnected decoration.
            pygame.draw.lines(base, (83, 106, 77), False,
                              [(x - 18, y + radius + 16), (x - 18, y + radius + 23),
                               (x - 56, y + radius + 23), (x - 56, 84), (52, 84)], 2)
            if col < 2:
                _resistor(parts, (x + 65, y + radius + 26))
        # Two dipped ceramic capacitors on the input side of the card.
        cy = y + 5
        if detail >= 2:
            _line(parts, METAL, (66, cy), (66, cy + 30), 2)
            _line(parts, METAL, (78, cy), (78, cy + 30), 2)
            _panel(parts, (60, cy - 11, 24, 30), (156, 117, 65), (198, 162, 100), 9)
    register_y = height - (56 if compact else 65)
    _panel(base, (34, register_y - 12, 652, 36 if compact else 42), DARK, (80, 104, 80), 5)
    _label(base, 'LOW BYTE', (46, register_y + 1), 14, t.MUTED)
    if not compact:
        _label(base, 'DEMO SIGNAL  >  SWITCHING STAGES', (48, 96), 11, t.MUTED)
    else:
        _label(base, 'DEMO FLOW', (590, height - 25), 11, t.MUTED)
    for index in range(16 if detail >= 1 else 0):
        x = 145 + index * 27
        pygame.draw.rect(base, (156, 134, 83), (x, height - 28, 17, 20), border_radius=2)
        _line(base, (205, 181, 115), (x + 3, height - 26), (x + 3, height - 11), 2)
    for x in (31, 689):
        for y in (30, height - 38):
            _screw(base, (x, y))
    return base, parts


def draw_transistor_board(screen, rect, amount, animation=None, detail=3):
    """Bounded, pure render; decorative flow never stands in for earned currency."""
    if rect.width <= 0 or rect.height <= 0:
        return
    animation = animation if animation is not None else MachineAnimation()
    compact = rect.height < 180
    palette = (t.TEXT, t.MUTED, t.SAGE, t.BORDER)
    plate, parts = _layers(compact, palette, detail)
    canvas = plate.copy()
    segment = signal_segment(animation.phase, compact)
    if len(segment) > 1:
        pygame.draw.lines(canvas, t.SAGE, False, segment, 3)
    canvas.blit(parts, (0, 0))
    y = canvas.get_height() - (56 if compact else 65)
    for index, on in enumerate(output_bits(amount)):
        box = pygame.Rect(216 + index * 40, y - 6, 30, 28)
        _panel(canvas, box, t.SAGE_DARK if on else BOARD, t.SAGE if on else (75, 97, 76), 3)
        _label(canvas, '1' if on else '0', box.center, 21, t.TEXT if on else t.MUTED, center=True)
    _label(canvas, f'0x{int(amount) & 255:02X}', (624, y + 8), 22, t.SAGE, center=True)
    screen.blit(pygame.transform.smoothscale(canvas, rect.size), rect)
