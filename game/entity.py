from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Tuple

import pygame


class Side(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    BOAT = "boat"


@dataclass(frozen=True)
class EntityStyle:
    color: Tuple[int, int, int]
    text_color: Tuple[int, int, int] = (20, 20, 25)


class Entity:
    def __init__(
        self,
        entity_id: str,
        display_name_key: str,
        style: EntityStyle,
        size: Tuple[int, int] = (78, 78),
    ) -> None:
        self.entity_id = entity_id
        self.display_name_key = display_name_key
        self.style = style
        self.size = pygame.Vector2(size)
        self.side: Side = Side.LEFT
        self.pos = pygame.Vector2(0, 0)
        self.target_pos = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(0, 0)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.pos.x), int(self.pos.y), int(self.size.x), int(self.size.y))

    def set_position(self, pos: pygame.Vector2) -> None:
        self.pos.update(pos)
        self.target_pos.update(pos)
        self.velocity.update(0, 0)

    def set_target(self, pos: pygame.Vector2) -> None:
        self.target_pos.update(pos)

    def update(self, dt: float) -> None:
        smoothing = 14.0
        to_target = self.target_pos - self.pos
        self.velocity = to_target * smoothing
        self.pos += self.velocity * dt
        if to_target.length_squared() < 0.25:
            self.pos.update(self.target_pos)
            self.velocity.update(0, 0)

    def _draw_token(self, surface: pygame.Surface, rect: pygame.Rect, selected: bool) -> None:
        base_shadow = pygame.Rect(rect.x + 10, rect.bottom - 4, rect.w - 20, 12)
        pygame.draw.ellipse(surface, (0, 0, 0, 55), base_shadow)

        shadow = pygame.Rect(rect.x + 4, rect.y + 6, rect.w, rect.h)
        pygame.draw.ellipse(surface, (0, 0, 0, 60), shadow)
        pygame.draw.ellipse(surface, (244, 246, 248), rect.inflate(6, 6))
        pygame.draw.ellipse(surface, self.style.color, rect)
        pygame.draw.ellipse(surface, (248, 248, 252), rect, width=3)

        gloss = pygame.Rect(rect.x + 10, rect.y + 8, rect.w - 20, rect.h // 2 - 4)
        gloss_surf = pygame.Surface((gloss.w, gloss.h), pygame.SRCALPHA)
        pygame.draw.ellipse(gloss_surf, (255, 255, 255, 46), gloss_surf.get_rect())
        surface.blit(gloss_surf, gloss.topleft)

        if selected:
            ring = rect.inflate(12, 12)
            pygame.draw.ellipse(surface, (255, 225, 120), ring, width=4)
            pygame.draw.ellipse(surface, (255, 255, 255), rect.inflate(18, 18), width=2)

    def _draw_wizard(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        cx, cy = rect.centerx, rect.centery

        # Hat body
        hat = [(cx - 18, cy + 6), (cx, cy - 26), (cx + 18, cy + 6)]
        pygame.draw.polygon(surface, (32, 28, 90), hat)
        pygame.draw.polygon(surface, (80, 68, 180), hat, width=2)

        # Hat brim
        pygame.draw.rect(surface, (22, 18, 68), pygame.Rect(cx - 24, cy + 4, 48, 9), border_radius=3)
        pygame.draw.rect(surface, (70, 55, 160), pygame.Rect(cx - 24, cy + 4, 48, 9), width=2, border_radius=3)

        # Star on hat
        star_pts = []
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            r = 6 if i % 2 == 0 else 3
            star_pts.append((cx + r * math.cos(angle), cy - 18 + r * math.sin(angle)))
        pygame.draw.polygon(surface, (245, 208, 30), star_pts)

        # Face
        pygame.draw.ellipse(surface, (245, 228, 190), pygame.Rect(cx - 13, cy + 10, 26, 22))

        # Eyes
        pygame.draw.circle(surface, (255, 255, 255), (cx - 5, cy + 18), 4)
        pygame.draw.circle(surface, (255, 255, 255), (cx + 5, cy + 18), 4)
        pygame.draw.circle(surface, (40, 30, 130), (cx - 4, cy + 18), 2)
        pygame.draw.circle(surface, (40, 30, 130), (cx + 6, cy + 18), 2)
        pygame.draw.circle(surface, (255, 255, 255), (cx - 3, cy + 17), 1)
        pygame.draw.circle(surface, (255, 255, 255), (cx + 7, cy + 17), 1)

        # Eyebrows
        pygame.draw.line(surface, (120, 85, 40), (cx - 9, cy + 14), (cx - 2, cy + 12), 2)
        pygame.draw.line(surface, (120, 85, 40), (cx + 2, cy + 12), (cx + 9, cy + 14), 2)

        # Beard
        beard_pts = [(cx - 10, cy + 26), (cx - 14, cy + 34), (cx, cy + 38), (cx + 14, cy + 34), (cx + 10, cy + 26)]
        pygame.draw.polygon(surface, (220, 205, 140), beard_pts)

        # Smile
        pygame.draw.arc(surface, (140, 100, 50), pygame.Rect(cx - 6, cy + 22, 12, 7), math.radians(200), math.radians(340), 2)

        # Wand
        pygame.draw.line(surface, (90, 58, 22), (cx + 20, cy + 12), (cx + 28, cy - 10), 3)
        pygame.draw.circle(surface, (240, 220, 40), (cx + 28, cy - 12), 5)
        pygame.draw.circle(surface, (255, 248, 180), (cx + 28, cy - 12), 3)

        # Sparkles
        pygame.draw.circle(surface, (255, 240, 80), (cx + 33, cy - 18), 2)
        pygame.draw.circle(surface, (220, 200, 40), (cx + 22, cy - 20), 2)

    def _draw_dragon(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        cx, cy = rect.centerx, rect.centery

        # Ears / horns
        pygame.draw.polygon(surface, (130, 48, 78), [(cx - 18, cy - 2), (cx - 26, cy - 22), (cx - 8, cy - 8)])
        pygame.draw.polygon(surface, (130, 48, 78), [(cx + 18, cy - 2), (cx + 26, cy - 22), (cx + 8, cy - 8)])
        pygame.draw.polygon(surface, (235, 130, 170), [(cx - 18, cy - 4), (cx - 23, cy - 18), (cx - 10, cy - 8)])
        pygame.draw.polygon(surface, (235, 130, 170), [(cx + 18, cy - 4), (cx + 23, cy - 18), (cx + 10, cy - 8)])

        # Head / body
        pygame.draw.ellipse(surface, (185, 60, 100), pygame.Rect(cx - 22, cy - 10, 44, 38))

        # Belly
        pygame.draw.ellipse(surface, (230, 130, 165), pygame.Rect(cx - 13, cy + 8, 26, 20))

        # Eyes (large and expressive)
        pygame.draw.circle(surface, (255, 255, 255), (cx - 9, cy + 2), 7)
        pygame.draw.circle(surface, (255, 255, 255), (cx + 9, cy + 2), 7)
        pygame.draw.circle(surface, (80, 20, 120), (cx - 8, cy + 2), 5)
        pygame.draw.circle(surface, (80, 20, 120), (cx + 10, cy + 2), 5)
        pygame.draw.circle(surface, (40, 0, 60), (cx - 8, cy + 2), 3)
        pygame.draw.circle(surface, (40, 0, 60), (cx + 10, cy + 2), 3)
        pygame.draw.circle(surface, (255, 255, 255), (cx - 6, cy + 1), 1)
        pygame.draw.circle(surface, (255, 255, 255), (cx + 12, cy + 1), 1)

        # Snout
        pygame.draw.ellipse(surface, (210, 85, 125), pygame.Rect(cx - 12, cy + 16, 24, 14))
        pygame.draw.ellipse(surface, (140, 40, 70), pygame.Rect(cx - 8, cy + 17, 16, 9))

        # Nostrils
        pygame.draw.ellipse(surface, (100, 20, 50), pygame.Rect(cx - 7, cy + 19, 5, 3))
        pygame.draw.ellipse(surface, (100, 20, 50), pygame.Rect(cx + 2, cy + 19, 5, 3))

        # Fangs
        pygame.draw.polygon(surface, (255, 252, 245), [(cx - 6, cy + 27), (cx - 9, cy + 34), (cx - 2, cy + 29)])
        pygame.draw.polygon(surface, (255, 252, 245), [(cx + 6, cy + 27), (cx + 9, cy + 34), (cx + 2, cy + 29)])

    def _draw_crystal(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        cx, cy = rect.centerx, rect.centery

        # Crystal body — multi-facet diamond shape
        diamond = [
            (cx, cy - 28),
            (cx + 20, cy - 2),
            (cx + 16, cy + 20),
            (cx, cy + 28),
            (cx - 16, cy + 20),
            (cx - 20, cy - 2),
        ]
        pygame.draw.polygon(surface, (80, 180, 230), diamond)

        # Facets — lighter top-right, darker bottom-left
        top_right = [(cx, cy - 28), (cx + 20, cy - 2), (cx, cy + 2)]
        pygame.draw.polygon(surface, (160, 225, 255), top_right)

        top_left = [(cx, cy - 28), (cx - 20, cy - 2), (cx, cy + 2)]
        pygame.draw.polygon(surface, (50, 140, 200), top_left)

        bot_right = [(cx, cy + 2), (cx + 16, cy + 20), (cx, cy + 28)]
        pygame.draw.polygon(surface, (60, 160, 218), bot_right)

        bot_left = [(cx, cy + 2), (cx - 16, cy + 20), (cx, cy + 28)]
        pygame.draw.polygon(surface, (30, 110, 175), bot_left)

        # Outline
        pygame.draw.polygon(surface, (180, 235, 255), diamond, width=2)

        # Center line
        pygame.draw.line(surface, (220, 248, 255), (cx, cy - 24), (cx, cy + 24), 2)
        pygame.draw.line(surface, (180, 230, 255), (cx - 16, cy), (cx + 16, cy), 1)

        # Glowing eyes
        pygame.draw.ellipse(surface, (10, 30, 80), pygame.Rect(cx - 14, cy - 4, 10, 9))
        pygame.draw.ellipse(surface, (10, 30, 80), pygame.Rect(cx + 4, cy - 4, 10, 9))
        pygame.draw.ellipse(surface, (30, 130, 220), pygame.Rect(cx - 13, cy - 3, 8, 7))
        pygame.draw.ellipse(surface, (30, 130, 220), pygame.Rect(cx + 5, cy - 3, 8, 7))
        pygame.draw.ellipse(surface, (140, 220, 255), pygame.Rect(cx - 12, cy - 2, 6, 5))
        pygame.draw.ellipse(surface, (140, 220, 255), pygame.Rect(cx + 6, cy - 2, 6, 5))

        # Floating diamonds around
        for angle, size in [(270, 4), (0, 3), (180, 3)]:
            rad = math.radians(angle)
            dx = int(cx + 28 * math.cos(rad))
            dy = int(cy + 28 * math.sin(rad))
            mini = [(dx, dy - size), (dx + size, dy), (dx, dy + size), (dx - size, dy)]
            pygame.draw.polygon(surface, (130, 210, 255), mini)

    def _draw_chest(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        cx, cy = rect.centerx, rect.centery

        # Chest base
        base = pygame.Rect(cx - 24, cy + 2, 48, 26)
        pygame.draw.rect(surface, (90, 50, 14), base, border_radius=5)
        pygame.draw.rect(surface, (180, 110, 35), base, width=2, border_radius=5)

        # Wood grain lines on base
        for i, x in enumerate([cx - 14, cx - 4, cx + 6, cx + 16]):
            pygame.draw.line(surface, (110, 65, 18), (x, cy + 3), (x, cy + 27), 1)

        # Metal band horizontal
        band = pygame.Rect(cx - 25, cy + 12, 50, 7)
        pygame.draw.rect(surface, (180, 130, 30), band, border_radius=2)
        pygame.draw.rect(surface, (220, 170, 50), band, width=1, border_radius=2)

        # Band rivets
        for rx in [cx - 20, cx + 20]:
            pygame.draw.circle(surface, (240, 195, 55), (rx, cy + 15), 3)
            pygame.draw.circle(surface, (255, 225, 90), (rx, cy + 15), 1)

        # Lid
        lid_pts = [(cx - 24, cy + 4), (cx - 22, cy - 14), (cx, cy - 18), (cx + 22, cy - 14), (cx + 24, cy + 4)]
        pygame.draw.polygon(surface, (108, 62, 18), lid_pts)
        pygame.draw.polygon(surface, (190, 125, 42), lid_pts, width=2)

        # Lid band
        pygame.draw.line(surface, (190, 135, 32), (cx - 22, cy - 4), (cx + 22, cy - 4), 5)
        pygame.draw.line(surface, (225, 168, 50), (cx - 22, cy - 4), (cx + 22, cy - 4), 1)

        # Lock body
        lock = pygame.Rect(cx - 7, cy + 6, 14, 11)
        pygame.draw.rect(surface, (155, 105, 18), lock, border_radius=3)
        pygame.draw.rect(surface, (220, 170, 40), lock, width=2, border_radius=3)

        # Lock shackle
        pygame.draw.arc(surface, (220, 170, 40), pygame.Rect(cx - 5, cy - 2, 10, 10), math.radians(0), math.radians(180), 2)

        # Lock keyhole
        pygame.draw.circle(surface, (240, 200, 50), (cx, cy + 11), 2)
        pygame.draw.line(surface, (240, 200, 50), (cx, cy + 13), (cx, cy + 15), 2)

        # Coins peeking from top
        for ox, oy in [(-10, -16), (0, -20), (10, -16)]:
            pygame.draw.circle(surface, (220, 175, 20), (cx + ox, cy + oy), 5)
            pygame.draw.circle(surface, (255, 220, 60), (cx + ox, cy + oy), 3)

        # Sparkle
        pygame.draw.line(surface, (255, 230, 60), (cx - 26, cy - 20), (cx - 22, cy - 20), 2)
        pygame.draw.line(surface, (255, 230, 60), (cx - 24, cy - 22), (cx - 24, cy - 18), 2)
        pygame.draw.line(surface, (255, 230, 60), (cx + 22, cy - 24), (cx + 26, cy - 24), 2)
        pygame.draw.line(surface, (255, 230, 60), (cx + 24, cy - 26), (cx + 24, cy - 22), 2)

    def _draw_phoenix(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        cx, cy = rect.centerx, rect.centery

        # Outer brass ring
        pygame.draw.circle(surface, (160, 105, 18), (cx, cy), 28)
        pygame.draw.circle(surface, (210, 155, 38), (cx, cy), 28, width=3)

        # Inner compass face
        pygame.draw.circle(surface, (245, 238, 210), (cx, cy), 23)
        pygame.draw.circle(surface, (195, 140, 30), (cx, cy), 23, width=2)

        # Cardinal tick marks
        for angle_deg in [0, 90, 180, 270]:
            rad = math.radians(angle_deg - 90)
            x1 = cx + int(18 * math.cos(rad))
            y1 = cy + int(18 * math.sin(rad))
            x2 = cx + int(23 * math.cos(rad))
            y2 = cy + int(23 * math.sin(rad))
            pygame.draw.line(surface, (140, 90, 15), (x1, y1), (x2, y2), 2)

        # Minor ticks
        for angle_deg in [45, 135, 225, 315]:
            rad = math.radians(angle_deg - 90)
            x1 = cx + int(19 * math.cos(rad))
            y1 = cy + int(19 * math.sin(rad))
            x2 = cx + int(23 * math.cos(rad))
            y2 = cy + int(23 * math.sin(rad))
            pygame.draw.line(surface, (180, 130, 30), (x1, y1), (x2, y2), 1)

        # North needle (red)
        north = [(cx, cy - 20), (cx - 4, cy + 2), (cx, cy - 2), (cx + 4, cy + 2)]
        pygame.draw.polygon(surface, (200, 28, 28), north)
        pygame.draw.polygon(surface, (240, 60, 60), north, width=1)

        # South needle (white/grey)
        south = [(cx, cy + 20), (cx - 4, cy - 2), (cx, cy + 2), (cx + 4, cy - 2)]
        pygame.draw.polygon(surface, (220, 218, 205), south)
        pygame.draw.polygon(surface, (160, 155, 140), south, width=1)

        # Center pivot
        pygame.draw.circle(surface, (195, 140, 25), (cx, cy), 5)
        pygame.draw.circle(surface, (245, 205, 60), (cx, cy), 3)
        pygame.draw.circle(surface, (175, 120, 15), (cx, cy), 1)

        # Corner ornament dots
        for ox, oy in [(0, -28), (0, 28), (-28, 0), (28, 0)]:
            pygame.draw.circle(surface, (220, 165, 35), (cx + ox, cy + oy), 4)
            pygame.draw.circle(surface, (250, 215, 70), (cx + ox, cy + oy), 2)

    def _draw_icon(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self.entity_id == "wizard":
            self._draw_wizard(surface, rect)
        elif self.entity_id == "dragon":
            self._draw_dragon(surface, rect)
        elif self.entity_id == "crystal":
            self._draw_crystal(surface, rect)
        elif self.entity_id == "chest":
            self._draw_chest(surface, rect)
        elif self.entity_id == "phoenix":
            self._draw_phoenix(surface, rect)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, label: str, selected: bool) -> None:
        r = self.rect
        self._draw_token(surface, r, selected)
        self._draw_icon(surface, r)