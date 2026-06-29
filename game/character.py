from __future__ import annotations

from typing import Tuple

from .entity import Entity, EntityStyle


class Character(Entity):
    def __init__(
        self,
        entity_id: str,
        display_name_key: str,
        style: EntityStyle,
        size: Tuple[int, int] = (82, 82),
        can_control_boat: bool = False,
    ) -> None:
        super().__init__(entity_id=entity_id, display_name_key=display_name_key, style=style, size=size)
        self.can_control_boat = can_control_boat
