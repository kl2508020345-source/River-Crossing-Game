from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import pygame

from .ui_theme import Theme


def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def ease_out_cubic(t: float) -> float:
    t = clamp01(t)
    u = 1.0 - t
    return 1.0 - u * u * u


def ease_out_quadratic(t: float) -> float:
    t = clamp01(t)
    return 1.0 - (1.0 - t) * (1.0 - t)


@dataclass
class Transition:
    active: bool = False
    t: float = 0.0
    duration: float = 0.22
    direction: int = 1
    reduced_motion: bool = False

    def start(self) -> None:
        self.active = True
        self.t = 0.0
        self.direction = 1

    def update(self, dt: float) -> None:
        if not self.active:
            return
        if self.reduced_motion:
            self.active = False
            self.t = 1.0
            return
        self.t += dt / max(0.01, self.duration)
        if self.t >= 1.0:
            self.t = 1.0
            self.active = False

    def overlay_alpha(self) -> int:
        v = 1.0 - ease_out_quadratic(self.t)
        return int(255 * v)


@dataclass
class Button:
    key: str
    rect: pygame.Rect
    enabled: bool = True
    hover: bool = False
    pressed: bool = False
    focus: bool = False
    anim: float = 0.0
    press_anim: float = 0.0

    def set_focus(self, focus: bool) -> None:
        self.focus = focus

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if not self.enabled:
            return None

        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return None
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            if was_pressed and self.rect.collidepoint(event.pos):
                return self.key
        return None

    def update(self, dt: float, reduced_motion: bool) -> None:
        target = 1.0 if (self.hover or self.focus) and self.enabled else 0.0
        speed = 18.0
        if reduced_motion:
            self.anim = target
        else:
            self.anim += (target - self.anim) * min(1.0, speed * dt)

        press_target = 1.0 if self.pressed else 0.0
        press_speed = 28.0
        if reduced_motion:
            self.press_anim = press_target
        else:
            self.press_anim += (press_target - self.press_anim) * min(1.0, press_speed * dt)

    def draw(self, surface: pygame.Surface, theme: Theme, font: pygame.font.Font, label: str) -> None:
        r = self.rect

        lift = int(4 * ease_out_cubic(self.anim))
        press = int(3 * ease_out_quadratic(self.press_anim))
        y_offset = -lift + press
        draw_rect = pygame.Rect(r.x, r.y + y_offset, r.w, r.h)

        shadow = pygame.Surface((draw_rect.w + 10, draw_rect.h + 14), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 0))
        pygame.draw.rect(shadow, (0, 0, 0, 90), pygame.Rect(5, 8, draw_rect.w, draw_rect.h), border_radius=theme.radius_m)
        surface.blit(shadow, (draw_rect.x - 5, draw_rect.y - 8))

        base = theme.panel_bg
        accent = theme.accent
        mix = ease_out_cubic(self.anim)
        fill = (
            int(base[0] + (accent[0] - base[0]) * 0.12 * mix),
            int(base[1] + (accent[1] - base[1]) * 0.12 * mix),
            int(base[2] + (accent[2] - base[2]) * 0.12 * mix),
        )

        pygame.draw.rect(surface, fill, draw_rect, border_radius=theme.radius_m)
        border_color = theme.panel_border if self.enabled else theme.text_secondary
        pygame.draw.rect(surface, border_color, draw_rect, width=2, border_radius=theme.radius_m)

        if self.focus:
            pygame.draw.rect(surface, theme.accent_2, draw_rect.inflate(8, 8), width=3, border_radius=theme.radius_m + 4)

        text_color = theme.text_primary if self.enabled else theme.text_secondary
        text = font.render(label, True, text_color)
        surface.blit(text, text.get_rect(center=draw_rect.center))

