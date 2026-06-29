import pygame

from game.boat import Boat
from game.entity import Entity, EntityStyle, Side
from game.puzzle_logic import PuzzleLogic


def _entity(entity_id: str) -> Entity:
    return Entity(entity_id, entity_id, EntityStyle((0, 0, 0)))


def test_valid_initial_state() -> None:
    boat = Boat(pygame.Vector2(0, 0), pygame.Vector2(10, 0))
    logic = PuzzleLogic(wizard_id="wizard")

    wizard = _entity("wizard")
    dragon = _entity("dragon")
    phoenix = _entity("phoenix")
    crystal = _entity("crystal")
    chest = _entity("chest")
    entities = [wizard, dragon, phoenix, crystal, chest]

    for e in entities:
        e.side = Side.LEFT

    result = logic.validate(entities, boat)
    assert result.ok


def test_dragon_phoenix_violation_when_wizard_absent() -> None:
    boat = Boat(pygame.Vector2(0, 0), pygame.Vector2(10, 0))
    logic = PuzzleLogic(wizard_id="wizard")

    wizard = _entity("wizard")
    dragon = _entity("dragon")
    phoenix = _entity("phoenix")
    crystal = _entity("crystal")
    chest = _entity("chest")
    entities = [wizard, dragon, phoenix, crystal, chest]

    dragon.side = Side.LEFT
    phoenix.side = Side.LEFT
    crystal.side = Side.RIGHT
    chest.side = Side.RIGHT
    wizard.side = Side.RIGHT

    result = logic.validate(entities, boat)
    assert not result.ok
    assert result.reason_key == "rule_dragon_phoenix"


def test_crystal_chest_violation_when_wizard_absent() -> None:
    boat = Boat(pygame.Vector2(0, 0), pygame.Vector2(10, 0))
    logic = PuzzleLogic(wizard_id="wizard")

    wizard = _entity("wizard")
    crystal = _entity("crystal")
    chest = _entity("chest")
    dragon = _entity("dragon")
    phoenix = _entity("phoenix")
    entities = [wizard, crystal, chest, dragon, phoenix]

    crystal.side = Side.LEFT
    chest.side = Side.LEFT
    wizard.side = Side.RIGHT
    dragon.side = Side.RIGHT
    phoenix.side = Side.RIGHT

    result = logic.validate(entities, boat)
    assert not result.ok
    assert result.reason_key == "rule_crystal_chest"


def test_wizard_on_docked_boat_counts_as_present() -> None:
    boat = Boat(pygame.Vector2(0, 0), pygame.Vector2(10, 0))
    boat.side = Side.LEFT
    logic = PuzzleLogic(wizard_id="wizard")

    wizard = _entity("wizard")
    dragon = _entity("dragon")
    phoenix = _entity("phoenix")
    entities = [wizard, dragon, phoenix]

    dragon.side = Side.LEFT
    phoenix.side = Side.LEFT
    wizard.side = Side.BOAT
    boat.add_passenger(wizard)

    result = logic.validate(entities, boat)
    assert result.ok


def test_forbidden_pair_not_alone_is_allowed() -> None:
    boat = Boat(pygame.Vector2(0, 0), pygame.Vector2(10, 0))
    logic = PuzzleLogic(wizard_id="wizard")

    wizard = _entity("wizard")
    crystal = _entity("crystal")
    chest = _entity("chest")
    phoenix = _entity("phoenix")
    entities = [wizard, crystal, chest, phoenix]

    crystal.side = Side.LEFT
    chest.side = Side.LEFT
    phoenix.side = Side.LEFT
    wizard.side = Side.RIGHT

    result = logic.validate(entities, boat)
    assert result.ok


def test_win_condition() -> None:
    logic = PuzzleLogic(wizard_id="wizard")
    wizard = _entity("wizard")
    dragon = _entity("dragon")
    phoenix = _entity("phoenix")
    crystal = _entity("crystal")
    chest = _entity("chest")
    entities = [wizard, dragon, phoenix, crystal, chest]
    for e in entities:
        e.side = Side.RIGHT
    assert logic.is_win(entities)
