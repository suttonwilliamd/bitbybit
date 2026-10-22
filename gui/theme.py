"""Quiet, shared art direction. No glow, flashing, or animated gradients."""
import pygame

BACKGROUND = (23, 27, 28)
SURFACE = (31, 37, 38)
CARD = (39, 46, 46)
BORDER = (63, 74, 73)
TEXT = (237, 238, 226)
MUTED = (175, 188, 181)
SAGE = (170, 202, 167)
SAGE_DARK = (48, 69, 56)
INK = (25, 38, 29)
AMBER = (218, 183, 128)
DANGER = (226, 153, 139)

_STANDARD = {name: value for name, value in globals().copy().items() if name.isupper()}
_CONTRAST = dict(BACKGROUND=(0, 0, 0), SURFACE=(12, 12, 12), CARD=(24, 24, 24),
                 BORDER=(170, 170, 170), TEXT=(255, 255, 255), MUTED=(220, 220, 220),
                 SAGE=(235, 255, 226), SAGE_DARK=(45, 60, 45), INK=(0, 0, 0),
                 AMBER=(255, 224, 180), DANGER=(255, 190, 180))


def configure(high_contrast=False):
    globals().update(_CONTRAST if high_contrast else _STANDARD)


def text(screen, font, value, pos, color=None, max_width=None):
    color = TEXT if color is None else color
    value = str(value)
    if max_width is not None and font.size(value)[0] > max_width:
        while value and font.size(value + '…')[0] > max_width:
            value = value[:-1]
        value += '…'
    image = font.render(value, True, color)
    screen.blit(image, pos)
    return image.get_rect(topleft=pos)


def panel(screen, rect, color=None):
    color = SURFACE if color is None else color
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, BORDER, rect, 1, border_radius=12)


def button(screen, rect, label, font, enabled=True, primary=False, mouse=None):
    hovered = enabled and rect.collidepoint(mouse if mouse is not None else pygame.mouse.get_pos())
    fill = SAGE if primary and enabled else SAGE_DARK if hovered else CARD
    foreground = INK if primary and enabled else TEXT if enabled else MUTED
    pygame.draw.rect(screen, fill, rect, border_radius=7)
    pygame.draw.rect(screen, SAGE if hovered else BORDER, rect, 1, border_radius=7)
    image = font.render(label, True, foreground)
    screen.blit(image, image.get_rect(center=rect.center))


def progress(screen, rect, value):
    pygame.draw.rect(screen, BORDER, rect, border_radius=3)
    fill = rect.copy()
    fill.width = round(rect.width * max(0, min(1, value)))
    if fill.width:
        pygame.draw.rect(screen, SAGE, fill, border_radius=3)
