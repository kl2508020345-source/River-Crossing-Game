from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .boat import Boat
from .entity import Entity, Side


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    reason_key: Optional[str] = None


class PuzzleLogic:
    def __init__(self, wizard_id: str) -> None:
        self.wizard_id = wizard_id

    def _wizard_present_on_bank(self, bank: Side, entities: Sequence[Entity], boat: Boat) -> bool:
        for e in entities:
            if e.entity_id != self.wizard_id:
                continue
            if e.side == bank:
                return True
            if e.side == Side.BOAT and boat.is_docked() and boat.side == bank:
                return True
            return False
        return False

    def _bank_entities(self, bank: Side, entities: Sequence[Entity]) -> List[str]:
        return [e.entity_id for e in entities if e.side == bank]

    def validate(self, entities: Sequence[Entity], boat: Boat) -> ValidationResult:
        left = set(self._bank_entities(Side.LEFT, entities))
        right = set(self._bank_entities(Side.RIGHT, entities))

        wizard_left = self._wizard_present_on_bank(Side.LEFT, entities, boat)
        wizard_right = self._wizard_present_on_bank(Side.RIGHT, entities, boat)

        def violates(bank_set: set[str], wizard_present: bool) -> Optional[str]:
            if wizard_present:
                return None

            if bank_set == {"dragon", "phoenix"}:
                return "rule_dragon_phoenix"
            if bank_set == {"crystal", "chest"}:
                return "rule_crystal_chest"
            return None

        reason = violates(left, wizard_left)
        if reason:
            return ValidationResult(ok=False, reason_key=reason)
        reason = violates(right, wizard_right)
        if reason:
            return ValidationResult(ok=False, reason_key=reason)

        return ValidationResult(ok=True)

    def is_win(self, entities: Sequence[Entity]) -> bool:
        return all(e.side == Side.RIGHT for e in entities)
