from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, List, Optional, Sequence, Tuple

import pygame

from .entity import Entity, Side
from .river_system import RiverSystem
from .ui_theme import Theme, vertical_gradient
from .ui_widgets import Button, Transition


@dataclass(frozen=True)
class GameVisuals:
    screen_size: Tuple[int, int]


class UIManager:
    def __init__(self, visuals: GameVisuals) -> None:
        self.visuals = visuals
        self.language = "en"
        self.high_contrast = False
        self.reduced_motion = False
        self.large_text = False
        self._text_scale = 1.0

        self.theme = Theme.modern(self.high_contrast)
        self.transition = Transition(reduced_motion=self.reduced_motion)

        self._menu_buttons: List[Button] = []
        self._end_buttons: List[Button] = []
        self._paused_buttons: List[Button] = []
        self._instructions_buttons: List[Button] = []
        self._layout_dirty = True
        self.visual_time = 0.0

        self.translations: Dict[str, Dict[str, str]] = {
            "en": {
                "title": "River Crossing Puzzle Adventure",
                "subtitle": "Fantasy Kingdom Escape",
                "start": "Start Game",
                "instructions": "Instructions",
                "quit": "Quit",
                "back": "Back",
                "paused": "Paused",
                "resume": "Resume",
                "restart": "Restart",
                "main_menu": "Main Menu",
                "win": "Victory!",
                "lose": "Defeat!",
                "next_level": "Next Level",
                "retry": "Retry",
                "timer": "Time",
                "moves": "Moves",
                "score": "Score",
                "best": "Best",
                "level": "Level",
                "level_1": "Level 1: Safe Crossing",
                "level_2": "Level 2: Raging Current",
                "level_3": "Level 3: Final Escape",
                "wizard": "Wizard",
                "dragon": "Dragon",
                "crystal": "Magic Crystal",
                "chest": "Potion Chest",
                "phoenix": "Baby Phoenix",
                "hint_controls": "TAB select | B wizard | E load/unload | ENTER cross | P pause | R restart | L language",
                "water_level": "Water Level",
                "flow_rate": "Flow Rate",
                "temperature": "Temperature",
                "quality": "Quality",
                "anomaly": "Anomaly",
                "season": "Season",
                "mist": "Mist",
                "history": "History",
                "sync": "Sync",
                "flood_mode": "Flood",
                "status_ok": "Stable",
                "status_alert": "Alert",
                "rule_dragon_phoenix": "Rule broken: Dragon and Baby Phoenix cannot be left alone together without Wizard.",
                "rule_crystal_chest": "Rule broken: Magic Crystal and Potion Chest cannot be left alone together without Wizard.",
                "timeout": "Time ran out!",
                "instructions_text": (
                    "Goal: Move everyone to the right bank before the timer hits 00:00.\n\n"
                    "Boat Rules:\n"
                    "- Boat capacity = Wizard + 1 entity\n"
                    "- Only the Wizard can make the boat cross\n\n"
                    "Safety Rules (lose immediately if violated):\n"
                    "- Dragon + Baby Phoenix cannot be left alone together without Wizard\n"
                    "- Magic Crystal + Potion Chest cannot be left alone together without Wizard\n\n"
                    "Controls:\n"
                    "- TAB: cycle selection\n"
                    "- B: wizard board/unboard (when docked)\n"
                    "- E: load/unload selected entity (when docked)\n"
                    "- ENTER: cross river (wizard must be on boat)\n"
                    "- P: pause, R: restart, L: language"
                ),
            },
            "ms": {
                "title": "Pengembaraan Teka-teki Menyeberangi Sungai",
                "subtitle": "Pelarian Kerajaan Fantasi",
                "start": "Mula",
                "instructions": "Arahan",
                "quit": "Keluar",
                "back": "Kembali",
                "paused": "Jeda",
                "resume": "Sambung",
                "restart": "Mula Semula",
                "main_menu": "Menu Utama",
                "win": "Menang!",
                "lose": "Kalah!",
                "next_level": "Tahap Seterusnya",
                "retry": "Cuba Lagi",
                "timer": "Masa",
                "moves": "Langkah",
                "score": "Skor",
                "best": "Terbaik",
                "level": "Tahap",
                "level_1": "Tahap 1: Menyeberang Selamat",
                "level_2": "Tahap 2: Arus Deras",
                "level_3": "Tahap 3: Pelarian Akhir",
                "wizard": "Ahli Sihir",
                "dragon": "Naga",
                "crystal": "Kristal Ajaib",
                "chest": "Peti Ramuan",
                "phoenix": "Anak Phoenix",
                "hint_controls": "TAB pilih | B ahli sihir | E naik/turun | ENTER seberang | P jeda | R mula semula | L bahasa",
                "water_level": "Paras Air",
                "flow_rate": "Kadar Aliran",
                "temperature": "Suhu",
                "quality": "Kualiti",
                "anomaly": "Anomali",
                "season": "Musim",
                "mist": "Kabus",
                "history": "Sejarah",
                "sync": "Segerak",
                "flood_mode": "Banjir",
                "status_ok": "Stabil",
                "status_alert": "Amaran",
                "rule_dragon_phoenix": "Peraturan dilanggar: Naga dan Anak Phoenix tidak boleh ditinggalkan berdua tanpa Ahli Sihir.",
                "rule_crystal_chest": "Peraturan dilanggar: Kristal Ajaib dan Peti Ramuan tidak boleh ditinggalkan berdua tanpa Ahli Sihir.",
                "timeout": "Masa telah tamat!",
                "instructions_text": (
                    "Matlamat: Pindahkan semua ke tebing kanan sebelum masa habis.\n\n"
                    "Peraturan Bot:\n"
                    "- Kapasiti bot = Ahli Sihir + 1 entiti\n"
                    "- Hanya Ahli Sihir boleh menggerakkan bot\n\n"
                    "Peraturan Keselamatan (kalah jika dilanggar):\n"
                    "- Naga + Anak Phoenix tidak boleh ditinggalkan berdua tanpa Ahli Sihir\n"
                    "- Kristal Ajaib + Peti Ramuan tidak boleh ditinggalkan berdua tanpa Ahli Sihir\n\n"
                    "Kawalan:\n"
                    "- TAB: tukar pilihan\n"
                    "- B: ahli sihir naik/turun (bila bot berlabuh)\n"
                    "- E: naik/turun entiti dipilih (bila bot berlabuh)\n"
                    "- ENTER: seberang sungai (ahli sihir mesti di bot)\n"
                    "- P: jeda, R: mula semula, L: bahasa"
                ),
            },
        }

        pygame.font.init()
        self._rebuild_fonts()

    def _rebuild_fonts(self) -> None:
        scale = self._text_scale
        self.font_title = pygame.font.Font(None, int(64 * scale))
        self.font_subtitle = pygame.font.Font(None, int(34 * scale))
        self.font_ui = pygame.font.Font(None, int(28 * scale))
        self.font_small = pygame.font.Font(None, int(22 * scale))

    def toggle_language(self) -> None:
        self.language = "ms" if self.language == "en" else "en"

    def toggle_high_contrast(self) -> None:
        self.high_contrast = not self.high_contrast
        self.theme = Theme.modern(self.high_contrast)

    def toggle_reduced_motion(self) -> None:
        self.reduced_motion = not self.reduced_motion
        self.transition.reduced_motion = self.reduced_motion

    def toggle_large_text(self) -> None:
        self.large_text = not self.large_text
        self._text_scale = 1.18 if self.large_text else 1.0
        self._rebuild_fonts()
        self._layout_dirty = True

    def t(self, key: str) -> str:
        return self.translations.get(self.language, {}).get(key, key)

    def _season_land_color(self, season: str) -> Tuple[int, int, int]:
        colors = {
            "spring": (52, 148, 94),
            "summer": (78, 152, 82),
            "autumn": (146, 110, 62),
            "winter": (94, 128, 146),
        }
        return colors.get(season, self.theme.land)

    def _draw_river_water(self, surface: pygame.Surface, river: pygame.Rect, river_system: Optional[RiverSystem]) -> None:
        river_surf = pygame.Surface((river.w, river.h), pygame.SRCALPHA)
        vertical_gradient(river_surf, self.theme.river_top, self.theme.river_bottom)

        for y in range(-24, river.h + 24, 18):
            phase = self.visual_time * 1.7 + y * 0.05
            points: List[Tuple[float, float]] = []
            for x in range(0, river.w + 10, 16):
                amp = 8 + 4 * math.sin(self.visual_time * 0.6 + x * 0.03)
                yy = y + math.sin(phase + x * 0.045) * amp
                points.append((x, yy))
            pygame.draw.lines(river_surf, (*self.theme.accent_2, 95), False, points, 2)

        for i in range(8):
            band_y = int((i / 8.0) * river.h)
            width = river.w - 24
            rect = pygame.Rect(12, band_y + int(math.sin(self.visual_time * 1.2 + i) * 8), width, 26)
            pygame.draw.arc(river_surf, (255, 255, 255, 24), rect, 0.0, math.pi, 2)

        if river_system:
            for ripple in river_system.ripples:
                local_x = int(ripple.x - river.x)
                local_y = int(ripple.y)
                if 0 <= local_x < river.w:
                    pygame.draw.circle(river_surf, (255, 255, 255, int(ripple.alpha)), (local_x, local_y), int(ripple.radius), 2)

        surface.blit(river_surf, river.topleft)

    def _draw_mist(self, surface: pygame.Surface, river_rect: pygame.Rect) -> None:
        mist = pygame.Surface((river_rect.w + 140, 120), pygame.SRCALPHA)
        for idx in range(7):
            x = 20 + idx * 44 + math.sin(self.visual_time * 0.6 + idx) * 16
            y = 26 + (idx % 3) * 18
            pygame.draw.ellipse(mist, (255, 255, 255, 20), pygame.Rect(x, y, 80, 28))
        surface.blit(mist, (river_rect.x - 70, 62))

    def _draw_land_details(self, surface: pygame.Surface, river_rect: pygame.Rect, season: str) -> None:
        shore_color = {
            "spring": (194, 178, 114),
            "summer": (188, 176, 102),
            "autumn": (174, 146, 92),
            "winter": (176, 184, 194),
        }.get(season, (190, 176, 108))

        left_shore = pygame.Rect(river_rect.x - 10, 0, 10, river_rect.h)
        right_shore = pygame.Rect(river_rect.right, 0, 10, river_rect.h)
        pygame.draw.rect(surface, shore_color, left_shore)
        pygame.draw.rect(surface, shore_color, right_shore)

        for y in range(36, river_rect.h, 84):
            pygame.draw.line(surface, (255, 255, 255), (river_rect.x - 6, y), (river_rect.x + 10, y + 14), 2)
            pygame.draw.line(surface, (255, 255, 255), (river_rect.right + 6, y), (river_rect.right - 10, y + 14), 2)

        dock_w = 54
        dock_h = 84
        dock_y = river_rect.h - 178
        for dock_x in (river_rect.x - dock_w, river_rect.right):
            deck = pygame.Rect(dock_x, dock_y, dock_w, dock_h)
            pygame.draw.rect(surface, (108, 78, 48), deck, border_radius=8)
            pygame.draw.rect(surface, (224, 210, 182), deck, width=2, border_radius=8)
            for plank in range(deck.y + 12, deck.bottom - 4, 16):
                pygame.draw.line(surface, (146, 110, 74), (deck.x + 8, plank), (deck.right - 8, plank), 3)

        for x in range(26, river_rect.x - 22, 110):
            y = 72 + int(18 * math.sin(self.visual_time * 0.55 + x * 0.02))
            pygame.draw.ellipse(surface, (255, 255, 255, 18), pygame.Rect(x, y, 86, 28))

        for x in range(river_rect.right + 24, self.visuals.screen_size[0] - 100, 120):
            y = 84 + int(14 * math.sin(self.visual_time * 0.5 + x * 0.015))
            pygame.draw.ellipse(surface, (255, 255, 255, 14), pygame.Rect(x, y, 76, 24))

    def draw_background(self, surface: pygame.Surface, river_system: Optional[RiverSystem] = None) -> None:
        w, h = self.visuals.screen_size
        vertical_gradient(surface, self.theme.bg_top, self.theme.bg_bottom)

        river_width = 200
        river_x = w // 2 - river_width // 2
        left_land = pygame.Rect(0, 0, river_x, h)
        right_land = pygame.Rect(river_x + river_width, 0, w - (river_x + river_width), h)
        river = pygame.Rect(river_x, 0, river_width, h)

        season = river_system.preferences.season if river_system else "spring"
        land_color = self._season_land_color(season)

        pygame.draw.rect(surface, land_color, left_land)
        pygame.draw.rect(surface, land_color, right_land)
        self._draw_river_water(surface, river, river_system)
        self._draw_land_details(surface, river, season)
        if river_system and river_system.preferences.show_mist:
            self._draw_mist(surface, river)

    def _panel(self, surface: pygame.Surface, rect: pygame.Rect, alpha: int = 210) -> None:
        panel = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        panel.fill((*self.theme.panel_bg, alpha))
        surface.blit(panel, (rect.x, rect.y))
        shine = pygame.Surface((rect.w, max(20, rect.h // 4)), pygame.SRCALPHA)
        pygame.draw.rect(shine, (255, 255, 255, 20), shine.get_rect(), border_radius=self.theme.radius_l)
        surface.blit(shine, (rect.x, rect.y))
        pygame.draw.rect(surface, self.theme.panel_border, rect, width=2, border_radius=self.theme.radius_l)

    def _draw_selected_chip(self, surface: pygame.Surface, label: str) -> None:
        text = f"Selected: {label}"
        text_w, text_h = self.font_small.size(text)
        chip = pygame.Rect(16, 92, max(196, text_w + 52), 36)

        shadow = pygame.Surface((chip.w + 8, chip.h + 8), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 50), pygame.Rect(4, 4, chip.w, chip.h), border_radius=18)
        surface.blit(shadow, (chip.x - 4, chip.y - 1))

        pygame.draw.rect(surface, (22, 34, 42), chip, border_radius=18)
        inner = chip.inflate(-4, -4)
        pygame.draw.rect(surface, (34, 52, 60), inner, border_radius=16)
        highlight = pygame.Rect(inner.x + 6, inner.y + 4, inner.w - 12, 10)
        highlight_surf = pygame.Surface((highlight.w, highlight.h), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (255, 255, 255, 22), highlight_surf.get_rect(), border_radius=8)
        surface.blit(highlight_surf, highlight.topleft)

        accent_dot_center = (chip.x + 18, chip.centery)
        pygame.draw.circle(surface, self.theme.accent, accent_dot_center, 6)
        pygame.draw.circle(surface, (255, 255, 255), accent_dot_center, 6, 2)

        pygame.draw.rect(surface, self.theme.panel_border, chip, width=2, border_radius=18)
        title = self.font_small.render(text, True, self.theme.text_primary)
        surface.blit(title, (chip.x + 32, chip.y + (chip.h - text_h) // 2 - 1))

    def _ensure_layout(self) -> None:
        if not self._layout_dirty:
            return
        w, h = self.visuals.screen_size

        menu_panel = pygame.Rect(w // 2 - 280, 220, 560, 260)
        btn_h = 54
        btn_w = 420
        btn_x = w // 2 - btn_w // 2
        top = menu_panel.y + 34
        gap = 18
        self._menu_buttons = [
            Button("start", pygame.Rect(btn_x, top + 0 * (btn_h + gap), btn_w, btn_h)),
            Button("instructions", pygame.Rect(btn_x, top + 1 * (btn_h + gap), btn_w, btn_h)),
            Button("quit", pygame.Rect(btn_x, top + 2 * (btn_h + gap), btn_w, btn_h)),
        ]

        self._instructions_buttons = [
            Button("back", pygame.Rect(w // 2 - 160, h - 96, 320, 54)),
        ]

        self._paused_buttons = [
            Button("resume", pygame.Rect(w // 2 - 180, h // 2 - 40, 360, 54)),
            Button("restart", pygame.Rect(w // 2 - 180, h // 2 + 28, 360, 54)),
            Button("menu", pygame.Rect(w // 2 - 180, h // 2 + 96, 360, 54)),
        ]

        self._end_buttons = [
            Button("ok", pygame.Rect(w // 2 - 180, h - 120, 360, 54)),
        ]

        self._layout_dirty = False

    def update(self, dt: float) -> None:
        self.visual_time += dt
        self.transition.update(dt)
        for btn in (*self._menu_buttons, *self._instructions_buttons, *self._paused_buttons, *self._end_buttons):
            btn.update(dt, self.reduced_motion)

    def _active_buttons(self, screen: str) -> Sequence[Button]:
        if screen == "menu":
            return self._menu_buttons
        if screen == "instructions":
            return self._instructions_buttons
        if screen == "paused":
            return self._paused_buttons
        if screen in ("win", "lose"):
            return self._end_buttons
        return ()

    def handle_mouse_event(self, event: pygame.event.Event, screen: str) -> Optional[str]:
        self._ensure_layout()
        for btn in self._active_buttons(screen):
            action = btn.handle_event(event)
            if action:
                return action
        return None

    def mark_layout_dirty(self) -> None:
        self._layout_dirty = True

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        wrapped: List[str] = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                wrapped.append("")
                continue

            words = line.split()
            current = words[0]
            for word in words[1:]:
                trial = f"{current} {word}"
                if font.size(trial)[0] <= max_width:
                    current = trial
                else:
                    wrapped.append(current)
                    current = word
            wrapped.append(current)
        return wrapped

    def _instruction_text_layout(self, max_width: int, max_height: int) -> Tuple[pygame.font.Font, List[str], int]:
        candidate_sizes = [int(size * self._text_scale) for size in (28, 24, 22, 20, 18)]
        for size in dict.fromkeys(max(16, s) for s in candidate_sizes):
            font = pygame.font.Font(None, size)
            lines = self._wrap_text(self.t("instructions_text"), font, max_width)
            line_height = max(18, font.get_linesize() - 2)
            if len(lines) * line_height <= max_height:
                return font, lines, line_height

        fallback_font = pygame.font.Font(None, max(16, int(18 * self._text_scale)))
        fallback_lines = self._wrap_text(self.t("instructions_text"), fallback_font, max_width)
        fallback_height = max(18, fallback_font.get_linesize() - 2)
        return fallback_font, fallback_lines, fallback_height

    def draw_menu(self, surface: pygame.Surface, options: Sequence[str], selected: int) -> None:
        self._ensure_layout()
        self.draw_background(surface)
        w, h = self.visuals.screen_size

        title = self.font_title.render(self.t("title"), True, self.theme.text_primary)
        subtitle = self.font_subtitle.render(self.t("subtitle"), True, self.theme.text_secondary)
        surface.blit(title, title.get_rect(center=(w // 2, 120)))
        surface.blit(subtitle, subtitle.get_rect(center=(w // 2, 165)))

        panel_rect = pygame.Rect(w // 2 - 280, 220, 560, 260)
        self._panel(surface, panel_rect)

        for i, btn in enumerate(self._menu_buttons):
            btn.set_focus(i == selected)
            btn.draw(surface, self.theme, self.font_ui, self.t(btn.key))

        hint = self.font_small.render("L: Language   H: Contrast   M: Motion   T: Text", True, self.theme.text_secondary)
        surface.blit(hint, (16, h - 26))

    def draw_instructions(self, surface: pygame.Surface) -> None:
        self._ensure_layout()
        self.draw_background(surface)
        w, h = self.visuals.screen_size
        panel_rect = pygame.Rect(40, 24, w - 80, h - 48)
        self._panel(surface, panel_rect)

        title = self.font_title.render(self.t("instructions"), True, self.theme.text_primary)
        surface.blit(title, title.get_rect(center=(w // 2, panel_rect.y + 54)))

        btn = self._instructions_buttons[0]
        btn.set_focus(True)
        text_x = panel_rect.x + 28
        text_top = panel_rect.y + 108
        text_bottom = btn.rect.y - 24
        instruction_font, lines, line_height = self._instruction_text_layout(panel_rect.w - 56, text_bottom - text_top)
        y = text_top
        for line in lines:
            if line:
                surf = instruction_font.render(line, True, self.theme.text_primary)
                surface.blit(surf, (text_x, y))
            y += line_height
        btn.draw(surface, self.theme, self.font_ui, self.t("back"))

    def draw_hud(
        self,
        surface: pygame.Surface,
        level_name: str,
        timer_text: str,
        moves: int,
        score: int,
        best: int,
        message: Optional[str],
        selected_label: Optional[str],
    ) -> None:
        w, _ = self.visuals.screen_size
        bar = pygame.Rect(0, 0, w, 64)
        self._panel(surface, bar, alpha=160)

        left = self.font_ui.render(f"{self.t('level')}: {level_name}", True, self.theme.text_primary)
        mid = self.font_ui.render(f"{self.t('timer')}: {timer_text}", True, self.theme.text_primary)
        right = self.font_ui.render(
            f"{self.t('moves')}: {moves}   {self.t('score')}: {score}   {self.t('best')}: {best}",
            True,
            self.theme.text_primary,
        )

        surface.blit(left, (16, 20))
        surface.blit(mid, (w // 2 - mid.get_width() // 2, 20))
        surface.blit(right, (w - right.get_width() - 16, 20))

        if message:
            msg_surf = self.font_small.render(message, True, self.theme.accent)
            surface.blit(msg_surf, (16, 68))
        if selected_label:
            self._draw_selected_chip(surface, selected_label)

    def draw_game(
        self,
        surface: pygame.Surface,
        river: RiverSystem,
        entities: Sequence[Entity],
        entity_labels: Dict[str, str],
        selected_entity_id: Optional[str],
        timer_text: str,
        level_name: str,
        moves: int,
        score: int,
        best: int,
        message: Optional[str],
    ) -> None:
        self.draw_background(surface, river)
        selected_label = entity_labels.get(selected_entity_id) if selected_entity_id else None
        self.draw_hud(surface, level_name, timer_text, moves, score, best, message, selected_label)

        hint = self.font_small.render(self.t("hint_controls"), True, self.theme.text_secondary)
        surface.blit(hint, (16, self.visuals.screen_size[1] - 26))

        for e in entities:
            label = entity_labels.get(e.entity_id, e.entity_id)
            e.draw(surface, self.font_ui, label, selected_entity_id == e.entity_id)

    def draw_pause(self, surface: pygame.Surface) -> None:
        self._ensure_layout()
        w, h = self.visuals.screen_size
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        panel = pygame.Rect(w // 2 - 260, h // 2 - 160, 520, 320)
        self._panel(surface, panel)
        title = self.font_title.render(self.t("paused"), True, self.theme.text_primary)
        surface.blit(title, title.get_rect(center=(w // 2, h // 2 - 110)))

        keys = self.font_small.render("P: " + self.t("resume") + "   R: " + self.t("restart") + "   ESC: " + self.t("main_menu"), True, self.theme.text_secondary)
        surface.blit(keys, keys.get_rect(center=(w // 2, h // 2 - 60)))

        for i, btn in enumerate(self._paused_buttons):
            btn.set_focus(i == 0)
            btn.draw(surface, self.theme, self.font_ui, self.t(btn.key))

    def draw_end_screen(self, surface: pygame.Surface, title_key: str, body_lines: List[str]) -> None:
        self._ensure_layout()
        self.draw_background(surface)
        w, h = self.visuals.screen_size
        panel = pygame.Rect(w // 2 - 320, 110, 640, 380)
        self._panel(surface, panel)
        title = self.font_title.render(self.t(title_key), True, self.theme.text_primary)
        surface.blit(title, title.get_rect(center=(w // 2, 170)))
        y = 230
        for line in body_lines:
            surf = self.font_ui.render(line, True, self.theme.text_primary)
            surface.blit(surf, surf.get_rect(center=(w // 2, y)))
            y += 34

        btn = self._end_buttons[0]
        btn.set_focus(True)
        btn.draw(surface, self.theme, self.font_ui, "OK")

        footer = self.font_small.render("ENTER: OK   R: Restart   ESC: Menu   L: Language   H: Contrast   M: Motion   T: Text", True, self.theme.text_secondary)
        surface.blit(footer, footer.get_rect(center=(w // 2, panel.bottom - 26)))

    def draw_transition_overlay(self, surface: pygame.Surface) -> None:
        if not self.transition.active:
            return
        a = self.transition.overlay_alpha()
        if a <= 0:
            return
        w, h = self.visuals.screen_size
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, a))
        surface.blit(overlay, (0, 0))
