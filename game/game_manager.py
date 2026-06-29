from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame

from .boat import Boat
from .character import Character
from .entity import Entity, EntityStyle, Side
from .level import Level
from .puzzle_logic import PuzzleLogic
from .river_system import RiverSystem
from .timer import Timer
from .ui_manager import GameVisuals, UIManager


class GameState(str, Enum):
    MENU = "menu"
    INSTRUCTIONS = "instructions"
    PLAYING = "playing"
    PAUSED = "paused"
    WIN = "win"
    LOSE = "lose"


@dataclass
class Layout:
    left_slots: List[pygame.Vector2]
    right_slots: List[pygame.Vector2]
    boat_slots: List[pygame.Vector2]
    boat_left_dock: pygame.Vector2
    boat_right_dock: pygame.Vector2


class GameManager:
    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=1)

        self.virtual_size: Tuple[int, int] = (1000, 600)
        self.screen_size: Tuple[int, int] = (1000, 600)
        self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
        pygame.display.set_caption("River Crossing Puzzle Adventure")
        self.clock = pygame.time.Clock()

        self.canvas = pygame.Surface(self.virtual_size)
        self.ui = UIManager(GameVisuals(screen_size=self.virtual_size))

        self._present_scale = 1.0
        self._present_offset = pygame.Vector2(0, 0)

        self.state: GameState = GameState.MENU
        self.menu_options = ["start", "instructions", "quit"]
        self.menu_selected = 0

        self.levels: List[Level] = [
            Level(level_id=1, name_key="level_1", timer_seconds=120, boat_cross_seconds=1.35, time_score_multiplier=10, move_penalty=5),
            Level(level_id=2, name_key="level_2", timer_seconds=90, boat_cross_seconds=1.15, time_score_multiplier=12, move_penalty=6),
            Level(level_id=3, name_key="level_3", timer_seconds=75, boat_cross_seconds=0.95, time_score_multiplier=14, move_penalty=7),
        ]
        self.level_index = 0

        self.layout = self._build_layout()
        self.boat = Boat(self.layout.boat_left_dock, self.layout.boat_right_dock)

        self.wizard_id = "wizard"
        self.logic = PuzzleLogic(wizard_id=self.wizard_id)
        self.timer = Timer.create(self.current_level.timer_seconds)
        self.river = RiverSystem(self._save_root() / "river_preferences.json")

        self.entities: List[Entity] = []
        self.selected_entity_id: Optional[str] = None
        self.moves = 0
        self.score = 0
        self.best_score = self._load_best_score()
        self.lose_reason_key: Optional[str] = None
        self.message: Optional[str] = None

        self.sfx = {
            "select": self._tone(660, 0.06, 0.22),
            "load": self._tone(520, 0.07, 0.26),
            "unload": self._tone(420, 0.07, 0.26),
            "cross": self._tone(220, 0.16, 0.28),
            "win": self._tone(880, 0.22, 0.25),
            "lose": self._tone(160, 0.22, 0.25),
        }

    @property
    def current_level(self) -> Level:
        return self.levels[self.level_index]

    def _build_layout(self) -> Layout:
        w, h = self.virtual_size
        top_y = 120
        slot_gap = 86
        left_x = 90
        right_x = w - 168

        left_slots = [pygame.Vector2(left_x, top_y + i * slot_gap) for i in range(5)]
        right_slots = [pygame.Vector2(right_x, top_y + i * slot_gap) for i in range(5)]

        boat_y = h - 160
        boat_left_dock = pygame.Vector2(w // 2 - 250, boat_y)
        boat_right_dock = pygame.Vector2(w // 2 + 50, boat_y)

        boat_slots = [
            pygame.Vector2(0, 0),
            pygame.Vector2(0, 0),
        ]

        return Layout(
            left_slots=left_slots,
            right_slots=right_slots,
            boat_slots=boat_slots,
            boat_left_dock=boat_left_dock,
            boat_right_dock=boat_right_dock,
        )

    def _tone(self, frequency_hz: float, duration_s: float, volume: float) -> pygame.mixer.Sound:
        import math
        from array import array

        sample_rate = 44100
        n_samples = max(1, int(sample_rate * duration_s))
        amplitude = int(32767 * max(0.0, min(1.0, volume)))
        buf = array("h")
        for i in range(n_samples):
            t = i / sample_rate
            s = math.sin(2.0 * math.pi * frequency_hz * t)
            env = 1.0 - (i / n_samples)
            buf.append(int(amplitude * s * env))
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _play(self, key: str) -> None:
        sound = self.sfx.get(key)
        if sound:
            sound.play()

    def _save_path(self) -> Path:
        return self._save_root() / "best_score.json"

    def _save_root(self) -> Path:
        base = Path(__file__).resolve().parent.parent
        save_dir = base / "save"
        save_dir.mkdir(parents=True, exist_ok=True)
        return save_dir

    def _load_best_score(self) -> int:
        path = self._save_path()
        if not path.exists():
            return 0
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return int(data.get("best_score", 0))
        except Exception:
            return 0

    def _store_best_score(self, best_score: int) -> None:
        path = self._save_path()
        payload = json.dumps({"best_score": int(best_score)}, indent=2)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, path)

    def _entity_labels(self) -> Dict[str, str]:
        return {
            "wizard": self.ui.t("wizard"),
            "dragon": self.ui.t("dragon"),
            "crystal": self.ui.t("crystal"),
            "chest": self.ui.t("chest"),
            "phoenix": self.ui.t("phoenix"),
        }

    def _new_game(self, reset_level_index: bool) -> None:
        if reset_level_index:
            self.level_index = 0
        self._start_level(self.level_index)

    def _start_level(self, index: int) -> None:
        self.level_index = max(0, min(index, len(self.levels) - 1))
        self.timer.reset(self.current_level.timer_seconds)
        self.timer.start()
        self.moves = 0
        self.score = 0
        self.lose_reason_key = None
        self.message = None

        self.boat.side = Side.LEFT
        self.boat.pos.update(self.layout.boat_left_dock)
        self.boat.target_pos.update(self.layout.boat_left_dock)
        self.boat.is_moving = False
        self.boat.passengers.clear()

        wizard = Character("wizard", "wizard", EntityStyle((235, 210, 120)), can_control_boat=True)
        dragon = Entity("dragon", "dragon", EntityStyle((200, 120, 140)))
        crystal = Entity("crystal", "crystal", EntityStyle((120, 220, 240)))
        chest = Entity("chest", "chest", EntityStyle((210, 160, 90)))
        phoenix = Entity("phoenix", "phoenix", EntityStyle((255, 170, 80)))

        self.entities = [wizard, dragon, crystal, chest, phoenix]
        for i, e in enumerate(self.entities):
            e.side = Side.LEFT
            e.set_position(self.layout.left_slots[i])

        self.selected_entity_id = "wizard"
        self.state = GameState.PLAYING

        self._reflow_positions()

    def _reflow_positions(self) -> None:
        left = [e for e in self.entities if e.side == Side.LEFT]
        right = [e for e in self.entities if e.side == Side.RIGHT]

        for i, e in enumerate(left):
            e.set_target(self.layout.left_slots[i])
        for i, e in enumerate(right):
            e.set_target(self.layout.right_slots[i])

        boat_r = self.boat.rect
        boat_slots = [
            pygame.Vector2(boat_r.x + 36, boat_r.y - 68),
            pygame.Vector2(boat_r.x + 110, boat_r.y - 68),
        ]
        for i, p in enumerate(self.boat.passengers[:2]):
            if self.boat.is_moving:
                p.set_position(boat_slots[i])
            else:
                p.set_target(boat_slots[i])

    def _eligible_entity_ids(self) -> List[str]:
        if not self.boat.is_docked():
            return []
        eligible: List[str] = []
        dock_side = self.boat.side
        for e in self.entities:
            if e.side == dock_side or e.side == Side.BOAT:
                eligible.append(e.entity_id)
        return eligible

    def _cycle_selection(self) -> None:
        eligible = self._eligible_entity_ids()
        if not eligible:
            return
        if self.selected_entity_id not in eligible:
            self.selected_entity_id = eligible[0]
            self._play("select")
            return
        idx = eligible.index(self.selected_entity_id)
        self.selected_entity_id = eligible[(idx + 1) % len(eligible)]
        self._play("select")

    def _get(self, entity_id: str) -> Optional[Entity]:
        for e in self.entities:
            if e.entity_id == entity_id:
                return e
        return None

    def _wizard(self) -> Character:
        w = self._get(self.wizard_id)
        if not isinstance(w, Character):
            raise RuntimeError("Wizard not found")
        return w

    def _wizard_can_act(self) -> bool:
        wizard = self._wizard()
        if wizard.side == Side.BOAT:
            return True
        return wizard.side == self.boat.side and self.boat.is_docked()

    def _toggle_wizard_board(self) -> None:
        if not self.boat.is_docked():
            return
        wizard = self._wizard()
        dock_side = self.boat.side
        if wizard.side == Side.BOAT:
            if self.boat.remove_passenger(wizard, to_side=dock_side):
                self.moves += 1
                self._play("unload")
        else:
            if wizard.side != dock_side:
                return
            if self.boat.add_passenger(wizard):
                self.moves += 1
                self._play("load")
        self._after_action()

    def _toggle_entity_board(self) -> None:
        if not self.boat.is_docked():
            return
        if not self._wizard_can_act():
            return
        if not self.selected_entity_id or self.selected_entity_id == self.wizard_id:
            return

        entity = self._get(self.selected_entity_id)
        if not entity:
            return

        dock_side = self.boat.side
        if entity.side == Side.BOAT:
            if self.boat.remove_passenger(entity, to_side=dock_side):
                self.moves += 1
                self._play("unload")
        else:
            if entity.side != dock_side:
                return
            if self.boat.add_passenger(entity):
                self.moves += 1
                self._play("load")
        self._after_action()

    def _cross(self) -> None:
        if self.boat.is_moving:
            return
        if self.boat.start_cross(self.wizard_id, duration_s=self.current_level.boat_cross_seconds):
            self.moves += 1
            self._play("cross")
            self.message = None
            self._after_action()
        else:
            self.message = "Wizard must be on boat to cross." if self.ui.language == "en" else "Ahli Sihir mesti berada di bot untuk menyeberang."

    def _after_action(self) -> None:
        self._reflow_positions()
        result = self.logic.validate(self.entities, self.boat)
        if not result.ok:
            self.lose_reason_key = result.reason_key
            self.state = GameState.LOSE
            self._play("lose")
            self.ui.transition.start()
            self._update_score(final=True)
            return
        if self.logic.is_win(self.entities):
            self.state = GameState.WIN
            self._play("win")
            self.ui.transition.start()
            self._update_score(final=True)
            return
        self._update_score(final=False)

    def _update_score(self, final: bool) -> None:
        time_score = int(self.timer.remaining_seconds) * self.current_level.time_score_multiplier
        move_score = self.moves * self.current_level.move_penalty
        self.score = max(0, time_score - move_score)
        if final and self.score > self.best_score:
            self.best_score = self.score
            self._store_best_score(self.best_score)

    def _handle_menu_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_l:
            self.ui.toggle_language()
            self.ui.transition.start()
        if event.key == pygame.K_h:
            self.ui.toggle_high_contrast()
            self.ui.transition.start()
        if event.key == pygame.K_m:
            self.ui.toggle_reduced_motion()
        if event.key == pygame.K_t:
            self.ui.toggle_large_text()
            self.ui.transition.start()
        if event.key == pygame.K_UP:
            self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
            self._play("select")
        if event.key == pygame.K_DOWN:
            self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
            self._play("select")
        if event.key == pygame.K_RETURN:
            choice = self.menu_options[self.menu_selected]
            if choice == "start":
                self._new_game(reset_level_index=True)
            elif choice == "instructions":
                self.state = GameState.INSTRUCTIONS
                self.ui.transition.start()
            elif choice == "quit":
                raise SystemExit

    def _handle_instructions_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_l:
            self.ui.toggle_language()
            self.ui.transition.start()
        if event.key == pygame.K_h:
            self.ui.toggle_high_contrast()
            self.ui.transition.start()
        if event.key == pygame.K_m:
            self.ui.toggle_reduced_motion()
        if event.key == pygame.K_t:
            self.ui.toggle_large_text()
            self.ui.transition.start()
        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.state = GameState.MENU
            self.ui.transition.start()

    def _handle_playing_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_l:
            self.ui.toggle_language()
            self.ui.transition.start()
        if event.key == pygame.K_h:
            self.ui.toggle_high_contrast()
            self.ui.transition.start()
        if event.key == pygame.K_m:
            self.ui.toggle_reduced_motion()
        if event.key == pygame.K_t:
            self.ui.toggle_large_text()
            self.ui.transition.start()
        if event.key == pygame.K_p:
            self.state = GameState.PAUSED
            self.timer.set_paused(True)
            self.ui.transition.start()
        if event.key == pygame.K_r:
            self._start_level(self.level_index)
            self.ui.transition.start()
        if event.key == pygame.K_TAB:
            self._cycle_selection()
        if event.key == pygame.K_b:
            self._toggle_wizard_board()
        if event.key == pygame.K_e:
            self._toggle_entity_board()
        if event.key == pygame.K_RETURN:
            self._cross()

    def _handle_paused_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_l:
            self.ui.toggle_language()
            self.ui.transition.start()
        if event.key == pygame.K_h:
            self.ui.toggle_high_contrast()
            self.ui.transition.start()
        if event.key == pygame.K_m:
            self.ui.toggle_reduced_motion()
        if event.key == pygame.K_t:
            self.ui.toggle_large_text()
            self.ui.transition.start()
        if event.key == pygame.K_p:
            self.state = GameState.PLAYING
            self.timer.set_paused(False)
            self.ui.transition.start()
        if event.key == pygame.K_r:
            self.timer.set_paused(False)
            self._start_level(self.level_index)
            self.ui.transition.start()
        if event.key == pygame.K_ESCAPE:
            self.timer.set_paused(False)
            self.state = GameState.MENU
            self.ui.transition.start()

    def _handle_end_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_l:
            self.ui.toggle_language()
            self.ui.transition.start()
        if event.key == pygame.K_h:
            self.ui.toggle_high_contrast()
            self.ui.transition.start()
        if event.key == pygame.K_m:
            self.ui.toggle_reduced_motion()
        if event.key == pygame.K_t:
            self.ui.toggle_large_text()
            self.ui.transition.start()
        if event.key == pygame.K_r:
            self._start_level(self.level_index)
            self.ui.transition.start()
        if event.key == pygame.K_ESCAPE:
            self.state = GameState.MENU
            self.ui.transition.start()
        if event.key == pygame.K_RETURN:
            if self.state == GameState.WIN and self.level_index < len(self.levels) - 1:
                self._start_level(self.level_index + 1)
                self.ui.transition.start()
            else:
                self.state = GameState.MENU
                self.ui.transition.start()

    def _dispatch_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            mapped = self._map_mouse_event_to_virtual(event)
            if mapped is None:
                return
            action = self.ui.handle_mouse_event(mapped, self.state.value)
            if action:
                self._handle_ui_action(action)

        if self.state == GameState.MENU:
            self._handle_menu_event(event)
        elif self.state == GameState.INSTRUCTIONS:
            self._handle_instructions_event(event)
        elif self.state == GameState.PLAYING:
            self._handle_playing_event(event)
        elif self.state == GameState.PAUSED:
            self._handle_paused_event(event)
        elif self.state in (GameState.WIN, GameState.LOSE):
            self._handle_end_event(event)

    def _handle_ui_action(self, action: str) -> None:
        if action == "start" and self.state == GameState.MENU:
            self._new_game(reset_level_index=True)
            self.ui.transition.start()
        elif action == "instructions" and self.state == GameState.MENU:
            self.state = GameState.INSTRUCTIONS
            self.ui.transition.start()
        elif action == "quit" and self.state == GameState.MENU:
            raise SystemExit
        elif action == "back" and self.state == GameState.INSTRUCTIONS:
            self.state = GameState.MENU
            self.ui.transition.start()
        elif action == "resume" and self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
            self.timer.set_paused(False)
            self.ui.transition.start()
        elif action == "restart" and self.state == GameState.PAUSED:
            self.timer.set_paused(False)
            self._start_level(self.level_index)
            self.ui.transition.start()
        elif action == "menu" and self.state == GameState.PAUSED:
            self.timer.set_paused(False)
            self.state = GameState.MENU
            self.ui.transition.start()
        elif action == "ok" and self.state in (GameState.WIN, GameState.LOSE):
            if self.state == GameState.WIN and self.level_index < len(self.levels) - 1:
                self._start_level(self.level_index + 1)
            else:
                self.state = GameState.MENU
            self.ui.transition.start()

    def _update(self, dt: float) -> None:
        self.ui.update(dt)
        self.river.update(dt)
        if self.state == GameState.PLAYING:
            self.timer.update(dt)
            arrived = self.boat.update(dt)
            if arrived is not None:
                self._after_action()
            self._reflow_positions()
            for e in self.entities:
                e.update(dt)

            if self.timer.is_expired():
                self.lose_reason_key = "timeout"
                self.state = GameState.LOSE
                self._play("lose")
                self.ui.transition.start()
                self._update_score(final=True)
        else:
            self.boat.update(dt)
            self._reflow_positions()
            for e in self.entities:
                e.update(dt)

    def _draw(self) -> None:
        if self.state == GameState.MENU:
            self.ui.draw_menu(self.canvas, self.menu_options, self.menu_selected)
            self.ui.draw_transition_overlay(self.canvas)
            self._present()
            return
        if self.state == GameState.INSTRUCTIONS:
            self.ui.draw_instructions(self.canvas)
            self.ui.draw_transition_overlay(self.canvas)
            self._present()
            return

        entity_labels = self._entity_labels()
        level_name = self.ui.t(self.current_level.name_key)
        timer_text = self.timer.format_mm_ss()

        self.ui.draw_game(
            self.canvas,
            river=self.river,
            entities=self.entities,
            entity_labels=entity_labels,
            selected_entity_id=self.selected_entity_id,
            timer_text=timer_text,
            level_name=level_name,
            moves=self.moves,
            score=self.score,
            best=self.best_score,
            message=self.message,
        )
        self.boat.draw(self.canvas)

        if self.state == GameState.PAUSED:
            self.ui.draw_pause(self.canvas)
        if self.state == GameState.WIN:
            lines = [
                f"{self.ui.t('score')}: {self.score}",
                f"{self.ui.t('best')}: {self.best_score}",
                (self.ui.t("next_level") if self.level_index < len(self.levels) - 1 else self.ui.t("main_menu")),
            ]
            self.ui.draw_end_screen(self.canvas, "win", lines)
        if self.state == GameState.LOSE:
            reason = self.ui.t(self.lose_reason_key or "lose")
            lines = [reason, f"{self.ui.t('score')}: {self.score}", f"{self.ui.t('best')}: {self.best_score}"]
            self.ui.draw_end_screen(self.canvas, "lose", lines)

        self.ui.draw_transition_overlay(self.canvas)
        self._present()

    def _present(self) -> None:
        if self.screen_size == self.virtual_size:
            self._present_scale = 1.0
            self._present_offset.update(0, 0)
            self.screen.blit(self.canvas, (0, 0))
            pygame.display.flip()
            return

        w, h = self.screen_size
        vw, vh = self.virtual_size
        scale = min(w / vw, h / vh)
        self._present_scale = float(scale)
        out_w = max(1, int(vw * scale))
        out_h = max(1, int(vh * scale))
        scaled = pygame.transform.smoothscale(self.canvas, (out_w, out_h))
        x = (w - out_w) // 2
        y = (h - out_h) // 2
        self._present_offset.update(x, y)
        # Use a scene-matching matte instead of black so resized windows
        # do not show harsh black corners around the scaled canvas.
        self.screen.fill(self.ui.theme.land)
        self.screen.blit(scaled, (x, y))
        pygame.display.flip()

    def _map_mouse_event_to_virtual(self, event: pygame.event.Event) -> Optional[pygame.event.Event]:
        if not hasattr(event, "pos"):
            return event

        x, y = event.pos
        vx, vy = self._present_offset.x, self._present_offset.y
        s = self._present_scale
        if s <= 0.0:
            return None

        local_x = (x - vx) / s
        local_y = (y - vy) / s

        if local_x < 0 or local_y < 0 or local_x >= self.virtual_size[0] or local_y >= self.virtual_size[1]:
            return None

        mapped_pos = (int(local_x), int(local_y))
        if event.type == pygame.MOUSEMOTION:
            return pygame.event.Event(pygame.MOUSEMOTION, {"pos": mapped_pos, "rel": (0, 0), "buttons": event.buttons})
        if event.type == pygame.MOUSEBUTTONDOWN:
            return pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": mapped_pos, "button": event.button})
        if event.type == pygame.MOUSEBUTTONUP:
            return pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": mapped_pos, "button": event.button})
        return event

    def _handle_gameplay_pointer(self, mapped: pygame.event.Event) -> None:
        if self.state != GameState.PLAYING:
            return
        if mapped.type == pygame.MOUSEBUTTONDOWN and mapped.button == 1:
            river_x = self.virtual_size[0] // 2 - 100
            river_rect = pygame.Rect(river_x, 0, 200, self.virtual_size[1])
            if river_rect.collidepoint(mapped.pos):
                self.river.add_ripple(mapped.pos[0], mapped.pos[1], strength=1.15)

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.VIDEORESIZE:
                        self.screen_size = (max(320, event.w), max(480, event.h))
                        self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
                        self.ui.mark_layout_dirty()
                    else:
                        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                            mapped = self._map_mouse_event_to_virtual(event)
                            if mapped is not None:
                                self._handle_gameplay_pointer(mapped)
                        self._dispatch_event(event)
            except SystemExit:
                running = False

            self._update(dt)
            self._draw()

        pygame.quit()
