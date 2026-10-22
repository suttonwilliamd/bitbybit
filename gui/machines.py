"""Working era dioramas: clockwork arithmetic and a relay sequencing cabinet.

All motion comes from MachineAnimation, never wall-clock reads in draw code.
These are illustrative mechanisms, not additional currency/production simulations.
"""
from dataclasses import dataclass
from functools import lru_cache
import math
import pygame
from . import theme as t

TAU = math.tau
WIDTH = 720
FLAP_SECONDS = .24
BRASS = (207, 168, 103)
BRASS_LIGHT = (246, 218, 160)
BRASS_SHADOW = (111, 79, 45)
COPPER = (184, 117, 76)
STEEL = (144, 162, 155)
DARK = (22, 29, 29)
PAPER = (219, 208, 169)


@dataclass
class MachineAnimation:
    """Per-game, non-persistent presentation state; delta-time driven and bounded."""
    phase: float = 0.0
    impulse: float = 0.0
    amount: int | None = None
    previous_amount: int = 0
    counter_age: float = FLAP_SECONDS
    production_rate: float = 0.0

    def click(self, reduced_motion=False):
        if not reduced_motion:
            self.impulse = min(3.0, self.impulse + 1.5)

    def update(self, dt, amount, production_rate=0, reduced_motion=False):
        dt = min(.25, max(0.0, dt))  # Never fast-forward the artwork after a stall.
        amount = max(0, int(amount))
        self.production_rate = max(0, production_rate)
        if self.amount is None:
            self.amount = self.previous_amount = amount
        elif amount != self.amount:
            if amount < self.amount or amount - self.amount > 9:
                # Purchases, loading and large jumps settle without invented counts.
                self.previous_amount = amount
                self.counter_age = FLAP_SECONDS
            elif self.counter_age >= FLAP_SECONDS:
                self.previous_amount = self.amount
                self.counter_age = 0.0
            self.amount = amount
        if reduced_motion:
            self.impulse = 0.0
            self.previous_amount = self.amount
            self.counter_age = FLAP_SECONDS
            return
        self.counter_age = min(FLAP_SECONDS, self.counter_age + dt)
        decay = math.exp(-5 * dt)
        speed = min(1.7, 1.1 + .16 * math.log10(1 + self.production_rate))
        self.phase += dt * speed + self.impulse * (1 - decay)
        self.impulse *= decay

    @property
    def counter_progress(self):
        value = min(1.0, self.counter_age / FLAP_SECONDS)
        return value * value * (3 - 2 * value)


@lru_cache(maxsize=16)
def _font(size, bold=False):
    return pygame.font.SysFont('Consolas,DejaVu Sans Mono', size, bold=bold)


def _label(surface, value, pos, size=13, color=None, center=False):
    image = _font(size).render(value, True, t.MUTED if color is None else color)
    rect = image.get_rect(center=pos) if center else image.get_rect(topleft=pos)
    surface.blit(image, rect)


def _line(surface, color, start, end, width=2):
    pygame.draw.line(surface, color, start, end, width)


def _screw(surface, center):
    pygame.draw.circle(surface, DARK, center, 6)
    pygame.draw.circle(surface, STEEL, center, 4)
    _line(surface, DARK, (center[0] - 2, center[1] + 1), (center[0] + 2, center[1] - 1), 1)


def _panel(surface, rect, fill, edge, radius=8):
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    pygame.draw.rect(surface, edge, rect, 2, border_radius=radius)


@lru_cache(maxsize=8)
def _housing(era, compact, palette):
    """Only static machining, lettering and wiring are cached, never animation frames."""
    height = 280 if compact else 400
    surface = pygame.Surface((WIDTH, height), pygame.SRCALPHA)
    if era == 1:
        # Walnut plinth, beveled bronze case, engraved index strips.
        _panel(surface, (8, 9, 704, height - 18), (57, 43, 33), (112, 88, 59), 16)
        _panel(surface, (18, 16, 684, height - 36), (68, 63, 49), BRASS_SHADOW, 12)
        _panel(surface, (27, 24, 666, height - 54), (39, 43, 39), BRASS, 8)
        _label(surface, 'STEPPED RECKONER', (48, 34), 17, BRASS_LIGHT)
        _label(surface, 'CLOCKWORK / No. 01', (480, 35), 14, BRASS)
        window_y = 60
        window_h = 58 if compact else 86
        _panel(surface, (46, window_y, 430, window_h), DARK, BRASS_SHADOW)
        if not compact:
            _label(surface, 'LOW 8 DIGITS', (48, window_y + window_h + 5), 12, BRASS)
        gear_top = 124 if compact else window_y + window_h + 27
        _panel(surface, (42, gear_top, 440, height - 55 - gear_top),
               (27, 34, 32), (90, 100, 84), 6)
        for x, y, radius, teeth, angle in (mechanical_gears(compact)[0], mechanical_gears(compact)[-1]):
            base_y = height - (55 if compact else 65)
            pygame.draw.polygon(surface, (90, 102, 85),
                                [(x - 17, base_y), (x - 9, y - 15), (x + 9, y - 15), (x + 17, base_y)])
            _line(surface, BRASS_SHADOW, (x - 21, base_y), (x + 21, base_y), 5)
        # Guide rails sit clear of the continuously rotating train.
        rack_y = height - (40 if compact else 49)
        for y in (rack_y - 10, rack_y + 10):
            _line(surface, BRASS_SHADOW, (54, y), (480, y), 5)
            _line(surface, STEEL, (54, y - 1), (480, y - 1), 1)
        if not compact:
            _label(surface, 'CARRY TRAIN', (62, height - 32), 12, BRASS)
            _label(surface, 'HAND CRANK', (596, height - 32), 12, BRASS, center=True)
        else:
            _label(surface, 'LOW 8 DIGITS', (52, height - 20), 12, BRASS)
        # Flywheel mount and engraved radial index.
        cy = height - (110 if compact else 151)
        r = 46 if compact else 67
        for i in range(40):
            angle = i * TAU / 40
            inner = r + (10 if i % 5 else 6)
            outer = r + 15
            _line(surface, BRASS_SHADOW,
                  (596 + math.cos(angle) * inner, cy + math.sin(angle) * inner),
                  (596 + math.cos(angle) * outer, cy + math.sin(angle) * outer), 2)
        if not compact:
            _label(surface, 'ROTARY INPUT', (596, 100), 13, BRASS, center=True)
            _label(surface, 'PIN  >  GEAR  >  CARRY', (596, 123), 10, t.MUTED, center=True)
    else:
        # Enamel instrument cabinet; dark phenolic relay sockets and copper buses.
        _panel(surface, (8, 9, 704, height - 18), (46, 56, 55), (115, 135, 122), 16)
        _panel(surface, (20, 20, 680, height - 40), (29, 39, 38), (72, 91, 81), 9)
        _label(surface, 'RELAY SEQUENCER', (42, 32), 17, t.SAGE)
        if not compact:
            _label(surface, '8 CONTACTS / No. 02', (476, 35), 14, t.MUTED)
        bank = relay_geometry(compact)
        _panel(surface, (34, 62, 482, height - 116), (21, 29, 29), (70, 91, 82), 7)
        for index, rect in enumerate(bank):
            x, y = rect.centerx, rect.centery
            bus_y = rect.y - 9
            # Wires bend around the sockets rather than floating behind them.
            pygame.draw.lines(surface, (81, 100, 82), False,
                              [(x - 43, bus_y), (x + 43, bus_y), (x + 43, y), (rect.right, y)], 2)
            _panel(surface, rect, (44, 45, 39), (95, 102, 82), 5)
            for sx in (rect.x + 7, rect.right - 7):
                _screw(surface, (sx, rect.bottom - 8))
            if not compact:
                _label(surface, f'K{index + 1:02}', (rect.x + 7, rect.y + 5), 11, t.MUTED)
        _panel(surface, (34, height - 49, 482, 33), DARK, (70, 91, 82), 4)
        _label(surface, 'LOW BYTE', (45, height - 32), 12, t.MUTED)
        for i in range(8):
            _label(surface, str(7 - i), (246 + i * 27, height - 42), 10, t.MUTED, center=True)
        _panel(surface, (540, 62, 136, height - 116), (53, 61, 53), (117, 129, 107), 5)
        _label(surface, 'DEMO TAPE', (608, 77), 12, t.MUTED, center=True)
        if not compact:
            _label(surface, 'READ / PUNCH', (608, height - 74), 11, t.MUTED, center=True)
    for x in (29, 691):
        for y in (28, height - 34):
            _screw(surface, (x, y))
    return surface


def mechanical_gears(compact=False, phase=0.0):
    """A common tooth pitch and exact external-gear ratios (including gap phase)."""
    scale = .80 if compact else 1.0
    teeth = (20, 30, 13, 18, 18)
    y = 178 if compact else 274
    x = 94.0
    angle = phase * .9
    result = []
    for index, count in enumerate(teeth):
        radius = count * 2 * scale
        if index:
            previous = result[-1]
            x += previous[2] + radius
            angle = (math.pi * (count - 1) - previous[3] * previous[4]) / count
        result.append((x, y, radius, count, angle))
    # Centre the complete train in its inspection window.
    offset = (524 - result[-1][0] - result[0][0]) / 2
    return [(x + offset, y, r, count, angle) for x, y, r, count, angle in result]


def _gear(surface, x, y, radius, teeth, angle, index):
    depth = radius / teeth * 1.35
    points = []
    for tooth in range(teeth):
        for fraction, r in ((-.49, radius - depth), (-.23, radius + depth),
                            (.23, radius + depth), (.49, radius - depth)):
            a = angle + (tooth + fraction) * TAU / teeth
            points.append((x + math.cos(a) * r, y + math.sin(a) * r))
    shadow = [(px + 2, py + 4) for px, py in points]
    pygame.draw.polygon(surface, (10, 17, 17), shadow)
    pygame.draw.polygon(surface, BRASS if index % 2 == 0 else COPPER, points)
    pygame.draw.polygon(surface, BRASS_LIGHT if index % 2 == 0 else BRASS, points, 1)
    center = (round(x), round(y))
    rim = max(3, round(radius - depth - 5))
    pygame.draw.circle(surface, BRASS_SHADOW, center, rim)
    pygame.draw.circle(surface, DARK, center, max(2, rim - 3))
    for spoke in range(6):
        a = angle + spoke * TAU / 6
        start = (x + math.cos(a) * radius * .18, y + math.sin(a) * radius * .18)
        end = (x + math.cos(a) * (rim - 2), y + math.sin(a) * (rim - 2))
        _line(surface, BRASS if index % 2 == 0 else COPPER, start, end, max(3, round(radius * .13)))
    pygame.draw.circle(surface, BRASS_LIGHT, center, max(5, round(radius * .19)))
    pygame.draw.circle(surface, STEEL, center, max(3, round(radius * .11)))
    a = angle + .4
    _line(surface, DARK, (x - math.cos(a) * 3, y - math.sin(a) * 3),
          (x + math.cos(a) * 3, y + math.sin(a) * 3), 2)


def flap_projection(progress, height):
    """Projected leaf height about a fixed middle hinge, never digit translation.

    First the outgoing upper leaf folds to edge-on; then the incoming lower
    leaf opens downward. Odd-height faces keep their exact upper/lower sizes.
    """
    progress = max(0.0, min(1.0, progress))
    upper = height // 2
    if progress < .5:
        return 'upper', round(upper * math.cos(math.pi * progress))
    return 'lower', round((height - upper) * -math.cos(math.pi * progress))


@lru_cache(maxsize=20)
def _flap_face(digit, width, height, font_size):
    """Ten stationary glyph faces at each of two sizes; no animated-frame cache."""
    face = pygame.Surface((width, height))
    face.fill(PAPER)
    face.fill((208, 197, 158), (0, height // 2, width, height - height // 2))
    image = _font(font_size).render(digit, True, DARK)
    face.blit(image, image.get_rect(center=face.get_rect().center))
    _line(face, (239, 228, 189), (0, 0), (width - 1, 0), 1)
    _line(face, (164, 148, 108), (0, height - 1), (width - 1, height - 1), 1)
    return face


def _flap_digit(surface, rect, previous, digit, progress, compact):
    _panel(surface, rect, DARK, BRASS_SHADOW, 3)
    inner = rect.inflate(-4, -4)
    split = inner.height // 2
    hinge = inner.y + split
    font_size = 35 if compact else 49
    current = _flap_face(digit, inner.width, inner.height, font_size)
    if previous == digit or progress >= 1:
        surface.blit(current, inner)
    else:
        outgoing = _flap_face(previous, inner.width, inner.height, font_size)
        if progress <= 0:
            surface.blit(outgoing, inner)
        else:
            upper = pygame.Rect(0, 0, inner.width, split)
            lower = pygame.Rect(0, split, inner.width, inner.height - split)
            # Stationary backing leaves: new upper half, old lower half.
            surface.blit(current, inner.topleft, upper)
            surface.blit(outgoing, (inner.x, hinge), lower)
            half, projected = flap_projection(progress, inner.height)
            if projected:
                source = outgoing.subsurface(upper) if half == 'upper' else current.subsurface(lower)
                leaf = pygame.transform.smoothscale(source, (inner.width, projected))
                # A folding leaf darkens as it turns away, without glow or flashing.
                shade = round(255 * (.45 + .55 * projected / source.get_height()))
                leaf.fill((shade, shade, shade), special_flags=pygame.BLEND_RGB_MULT)
                y = hinge - projected if half == 'upper' else hinge
                surface.blit(leaf, (inner.x, y))
    # A real split and fixed side pivots remain visible even at rest.
    _line(surface, DARK, (inner.x, hinge), (inner.right - 1, hinge), 2)
    for x in (rect.x + 2, rect.right - 3):
        pygame.draw.circle(surface, BRASS_SHADOW, (x, hinge), 2)
        pygame.draw.circle(surface, BRASS_LIGHT, (x, hinge), 1)


def _counter(surface, amount, animation, compact):
    y, height = 66, 45 if compact else 69
    digit_width = 47
    value = f'{int(amount) % 10**8:08}'
    previous = value if animation.amount is None else f'{animation.previous_amount % 10**8:08}'
    progress = animation.counter_progress
    for i, digit in enumerate(value):
        rect = pygame.Rect(70 + i * digit_width, y, digit_width - 4, height)
        _flap_digit(surface, rect, previous[i], digit, progress, compact)


def _mechanical(surface, amount, animation, compact):
    height = surface.get_height()
    gears = mechanical_gears(compact, animation.phase)
    crank = gears[-1][4]
    cy = height - (110 if compact else 151)
    radius = 46 if compact else 67
    pin, slider, rod_length = crank_linkage(crank, compact)
    slider_x, rack_y = slider
    # An equal-pulley belt connects the last gear's axle to the crank axle.
    gx, gy = gears[-1][:2]
    distance = math.hypot(596 - gx, cy - gy)
    nx, ny = -(cy - gy) / distance * 13, (596 - gx) / distance * 13
    for sign in (-1, 1):
        start, end = (gx + sign * nx, gy + sign * ny), (596 + sign * nx, cy + sign * ny)
        _line(surface, (12, 21, 19), start, end, 7)
        _line(surface, (112, 111, 79), start, end, 2)
    # The rack is a separate reciprocating carriage, not a falsely meshed pinion.
    pygame.draw.rect(surface, BRASS_SHADOW, (slider_x - 330, rack_y - 6, 340, 12), border_radius=3)
    for i in range(34):
        x = slider_x - 329 + i * 10
        pygame.draw.polygon(surface, BRASS, [(x, rack_y - 5), (x + 2, rack_y - 11),
                                            (x + 6, rack_y - 11), (x + 8, rack_y - 5)])
    _line(surface, (9, 18, 17), (slider_x, rack_y + 3), (pin[0], pin[1] + 3), 12)
    _line(surface, STEEL, (slider_x, rack_y), pin, 8)
    pygame.draw.circle(surface, BRASS_LIGHT, (round(slider_x), rack_y), 7)
    for index, gear in enumerate(gears):
        _gear(surface, *gear, index)
    # Flywheel: rotating spokes, eccentric crank pin and wooden grip.
    pygame.draw.circle(surface, DARK, (596, cy + 3), radius + 5)
    pygame.draw.circle(surface, BRASS_SHADOW, (596, cy), radius, 9)
    pygame.draw.circle(surface, BRASS_LIGHT, (596, cy), radius, 2)
    for i in range(4):
        a = crank + i * TAU / 4
        _line(surface, BRASS, (596, cy), (596 + math.cos(a) * (radius - 5), cy + math.sin(a) * (radius - 5)), 8)
    _line(surface, STEEL, (596, cy), pin, 10)
    pygame.draw.circle(surface, BRASS, (596, cy), 12)
    pygame.draw.circle(surface, STEEL, (596, cy), 5)
    pygame.draw.circle(surface, (14, 22, 21), (round(pin[0]), round(pin[1]) + 3), 10)
    pygame.draw.circle(surface, (130, 83, 45), (round(pin[0]), round(pin[1])), 9)
    pygame.draw.circle(surface, BRASS_LIGHT, (round(pin[0]) - 2, round(pin[1]) - 2), 3)
    _counter(surface, amount, animation, compact)


def relay_geometry(compact=False):
    cell_height = 58 if compact else 108
    row_gap = 19 if compact else 30
    return [pygame.Rect(50 + (i % 4) * 115, 82 + (i // 4) * (cell_height + row_gap), 105, cell_height)
            for i in range(8)]


def crank_linkage(angle, compact=False):
    """Offset crank-slider with a fixed-length connecting rod and horizontal guide."""
    cy, radius, rack_y, length = (170, 46, 240, 165) if compact else (249, 67, 351, 200)
    pin = (596 + math.cos(angle) * radius * .48, cy + math.sin(angle) * radius * .48)
    slider_x = pin[0] - math.sqrt(length**2 - (rack_y - pin[1])**2)
    return pin, (slider_x, rack_y), length


def _smooth(value):
    value = max(0, min(1, value))
    return value * value * (3 - 2 * value)


def relay_states(phase):
    """One left-to-right scan: close, hold, open, then move to the next socket."""
    step = (phase * 2) % 8
    result = []
    for index in range(8):
        local = (step - index) % 8
        closure = min(_smooth(local / .18), 1 - _smooth((local - .65) / .30)) if local < 1 else 0
        result.append(closure)
    return result


def output_bits(amount):
    return tuple(bool((int(amount) & 255) & (1 << (7 - i))) for i in range(8))


def tape_position(phase):
    """One short indexed feed per complete relay scan, then a stationary hold."""
    cycle = phase / 4
    whole = math.floor(cycle)
    return (whole + _smooth((cycle - whole) / .12)) * 10


def _relay(surface, rect, index, closure, compact):
    cx, cy = rect.centerx, rect.centery
    coil_y = rect.y + (26 if compact else 57)
    coil_h = 16 if compact else 31
    core = pygame.Rect(cx - 28, coil_y - coil_h // 2, 41, coil_h)
    pygame.draw.rect(surface, STEEL, core.inflate(8, -coil_h + 6))
    pygame.draw.rect(surface, (91, 59, 40), core, border_radius=3)
    # Individual copper windings and bobbin flanges.
    energized = tuple(round(a + (b - a) * closure) for a, b in zip(COPPER, BRASS_LIGHT))
    for x in range(core.x + 3, core.right - 2, 6 if compact else 3):
        _line(surface, energized, (x, core.y + 2), (x, core.bottom - 2), 2)
    for x in (core.x - 3, core.right):
        pygame.draw.rect(surface, (109, 119, 98), (x, core.y - 3, 4, coil_h + 6))
    # The armature pivots toward a stationary contact as the coil energizes.
    pivot = (cx + 34, coil_y + 12)
    fixed = (cx + 16, coil_y - 10)
    length = math.dist(pivot, fixed)
    angle = math.atan2(fixed[1] - pivot[1], fixed[0] - pivot[0]) + math.radians(13 if compact else 10) * (1 - closure)
    tip = (pivot[0] + math.cos(angle) * length, pivot[1] + math.sin(angle) * length)
    _line(surface, (11, 18, 18), (pivot[0] + 2, pivot[1] + 2), (tip[0] + 2, tip[1] + 2), 6)
    _line(surface, STEEL, pivot, tip, 4)
    pygame.draw.circle(surface, STEEL, pivot, 4)
    _line(surface, BRASS, (fixed[0] + 9, fixed[1] - 6), (fixed[0] + 9, fixed[1]), 3)
    _line(surface, BRASS, (fixed[0] + 9, fixed[1]), fixed, 3)
    pygame.draw.circle(surface, BRASS_LIGHT, (round(tip[0]), round(tip[1])), 2)
    pygame.draw.circle(surface, BRASS_LIGHT, fixed, 2)
    # Small local pilot lamps, not bloom or full-screen strobes.
    lamp = (rect.right - 12, rect.y + 10)
    pygame.draw.circle(surface, DARK, lamp, 6)
    lamp_color = tuple(round(a + (b - a) * closure) for a, b in zip((64, 78, 65), t.SAGE))
    pygame.draw.circle(surface, lamp_color, lamp, 4)
    if not compact:
        _label(surface, 'CLOSED' if closure > .65 else 'OPEN', (cx, rect.bottom - 17), 10,
               t.SAGE if closure > .65 else t.MUTED, center=True)


def _tape(surface, phase):
    height = surface.get_height()
    tape = pygame.Rect(554, 92, 108, height - 186)
    old_clip = surface.get_clip()
    surface.set_clip(tape)
    pygame.draw.rect(surface, PAPER, tape)
    row_height = 10
    position = tape_position(phase)
    offset = position % row_height
    first_row = int(position // row_height)
    for row in range(-1, tape.height // row_height + 2):
        y = tape.y + row * row_height + offset
        # A fixed timing demonstration, explicitly not a history of player earnings.
        value = (0x81, 0x42, 0x24, 0x18)[(row - first_row) % 4]
        for bit in range(8):
            if value & (1 << (7 - bit)):
                pygame.draw.circle(surface, DARK, (tape.x + 16 + bit * 11, round(y)), 2)
        for x in (tape.x + 5, tape.right - 5):
            pygame.draw.circle(surface, (116, 113, 90), (x, round(y)), 2)
    surface.set_clip(old_clip)
    pygame.draw.rect(surface, (20, 29, 28), tape, 2)
    # Dark roller lips and their turning index ticks.
    for y in (tape.y - 3, tape.bottom):
        _panel(surface, (548, y - 4, 120, 9), (91, 106, 95), DARK, 3)
        for i in range(10):
            x = 556 + i * 11 + position % 11
            _line(surface, (160, 168, 146), (x, y - 2), (x, y + 2), 1)


def _electromechanical(surface, amount, animation, compact):
    height = surface.get_height()
    phase = animation.phase
    cells = relay_geometry(compact)
    for i, (rect, closure) in enumerate(zip(cells, relay_states(phase))):
        _relay(surface, rect, i, closure, compact)
        # Only the selected circuit brightens after its contact has closed.
        local = (phase * 2 - i) % 8
        if .2 < local < .8:
            x = rect.centerx - 40 + (local - .2) / .6 * 60
            _line(surface, t.SAGE, (x, rect.y - 9), (x + 20, rect.y - 9), 2)
    _tape(surface, phase)
    # Output lamps reflect the *actual* resource's low byte, not the scan clock.
    value = int(amount) & 255
    for i, on in enumerate(output_bits(amount)):
        x = 246 + i * 27
        pygame.draw.circle(surface, DARK, (x, height - 24), 8)
        pygame.draw.circle(surface, t.SAGE if on else (58, 76, 65), (x, height - 24), 6)
        if on:
            pygame.draw.circle(surface, t.TEXT, (x, height - 24), 3)
    _label(surface, f'{value:03} / 255', (608, height - 26), 12, t.SAGE, center=True)


def draw_era_machine(screen, rect, era, amount, animation=None):
    """Render only inside rect, with cached plate art and antialiased downsampling."""
    if rect.width <= 0 or rect.height <= 0:
        return
    animation = animation if animation is not None else MachineAnimation()
    compact = rect.height < 180
    palette = (t.BACKGROUND, t.TEXT, t.MUTED, t.SAGE, t.AMBER)
    canvas = _housing(era, compact, palette).copy()
    if era == 1:
        _mechanical(canvas, amount, animation, compact)
    elif era == 2:
        _electromechanical(canvas, amount, animation, compact)
    else:
        raise ValueError('Working machine renderer supports eras 1 and 2')
    image = pygame.transform.smoothscale(canvas, rect.size)
    screen.blit(image, rect)
