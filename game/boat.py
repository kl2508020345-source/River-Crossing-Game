from __future__ import annotations

from typing import List, Optional

import pygame

from .entity import Entity, Side


class Boat:
    def __init__(self, left_dock: pygame.Vector2, right_dock: pygame.Vector2) -> None:
        self.left_dock = pygame.Vector2(left_dock)
        self.right_dock = pygame.Vector2(right_dock)

        self.side: Side = Side.LEFT
        self.pos = pygame.Vector2(left_dock)
        self.target_pos = pygame.Vector2(left_dock)

        self.size = pygame.Vector2(200, 70)
        self.passengers: List[Entity] = []

        self.is_moving = False
        self.cross_duration_s = 1.4
        self._cross_elapsed = 0.0
        self._from = pygame.Vector2(self.pos)
        self._to = pygame.Vector2(self.pos)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.pos.x), int(self.pos.y), int(self.size.x), int(self.size.y))

    def is_docked(self) -> bool:
        return not self.is_moving

    def capacity_total(self) -> int:
        return 2

    def has_wizard(self, wizard_id: str) -> bool:
        return any(p.entity_id == wizard_id for p in self.passengers)

    def can_board(self) -> bool:
        return self.is_docked() and len(self.passengers) < self.capacity_total()

    def add_passenger(self, entity: Entity) -> bool:
        if not self.can_board():
            return False
        if entity in self.passengers:
            return True
        self.passengers.append(entity)
        entity.side = Side.BOAT
        return True

    def remove_passenger(self, entity: Entity, to_side: Side) -> bool:
        if not self.is_docked():
            return False
        if entity not in self.passengers:
            return False
        self.passengers.remove(entity)
        entity.side = to_side
        return True

    def start_cross(self, wizard_id: str, duration_s: float) -> bool:
        if self.is_moving:
            return False
        if not self.has_wizard(wizard_id):
            return False

        self.cross_duration_s = max(0.6, float(duration_s))
        self._cross_elapsed = 0.0
        self.is_moving = True

        self._from = pygame.Vector2(self.pos)
        if self.side == Side.LEFT:
            self.side = Side.RIGHT
            self._to = pygame.Vector2(self.right_dock)
        else:
            self.side = Side.LEFT
            self._to = pygame.Vector2(self.left_dock)

        self.target_pos.update(self._to)
        return True

    def update(self, dt: float) -> Optional[Side]:
        if not self.is_moving:
            self.pos.update(self.target_pos)
            return None

        self._cross_elapsed += dt
        t = min(1.0, self._cross_elapsed / self.cross_duration_s)
        eased = 1.0 - (1.0 - t) * (1.0 - t)
        self.pos = self._from.lerp(self._to, eased)

        if t >= 1.0:
            self.is_moving = False
            self.pos.update(self._to)
            return self.side
        return None

    def draw(self, surface: pygame.Surface) -> None:
        r = self.rect
        shadow = pygame.Rect(r.x + 6, r.y + 9, r.w, r.h - 4)
        pygame.draw.ellipse(surface, (0, 0, 0, 70), shadow)

        hull = [
            (r.x + 10, r.y + 32),
            (r.x + 26, r.y + 16),
            (r.x + r.w - 26, r.y + 16),
            (r.x + r.w - 10, r.y + 32),
            (r.x + r.w - 32, r.y + 58),
            (r.x + 32, r.y + 58),
        ]
        pygame.draw.polygon(surface, (120, 82, 50), hull)
        pygame.draw.polygon(surface, (232, 216, 192), hull, width=3)

        inner = [
            (r.x + 26, r.y + 30),
            (r.x + 44, r.y + 20),
            (r.x + r.w - 44, r.y + 20),
            (r.x + r.w - 26, r.y + 30),
            (r.x + r.w - 44, r.y + 48),
            (r.x + 44, r.y + 48),
        ]
        pygame.draw.polygon(surface, (92, 61, 34), inner)

        stripe_y = r.y + 24
        pygame.draw.line(surface, (255, 234, 196), (r.x + 36, stripe_y), (r.x + r.w - 36, stripe_y), 3)
        pygame.draw.line(surface, (255, 234, 196), (r.x + 52, stripe_y + 10), (r.x + r.w - 52, stripe_y + 10), 2)
