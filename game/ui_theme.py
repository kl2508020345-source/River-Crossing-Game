from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pygame


Color = Tuple[int, int, int]


@dataclass(frozen=True)
class Theme:
    bg_top: Color
    bg_bottom: Color
    land: Color
    river_top: Color
    river_bottom: Color
    panel_bg: Color
    panel_border: Color
    text_primary: Color
    text_secondary: Color
    accent: Color
    accent_2: Color
    danger: Color
    success: Color

    radius_l: int
    radius_m: int
    radius_s: int

    pad_l: int
    pad_m: int
    pad_s: int

    @staticmethod
    def modern(high_contrast: bool) -> "Theme":
        if high_contrast:
            return Theme(
                bg_top=(0, 0, 0),
                bg_bottom=(16, 16, 16),
                land=(12, 48, 26),
                river_top=(20, 70, 160),
                river_bottom=(10, 35, 80),
                panel_bg=(10, 10, 14),
                panel_border=(255, 255, 255),
                text_primary=(255, 255, 255),
                text_secondary=(225, 225, 225),
                accent=(255, 214, 102),
                accent_2=(120, 220, 255),
                danger=(255, 96, 96),
                success=(120, 240, 150),
                radius_l=22,
                radius_m=16,
                radius_s=12,
                pad_l=28,
                pad_m=18,
                pad_s=12,
            )

        return Theme(
            bg_top=(18, 22, 40),
            bg_bottom=(12, 14, 26),
            land=(40, 132, 88),
            river_top=(50, 140, 235),
            river_bottom=(18, 55, 115),
            panel_bg=(14, 16, 24),
            panel_border=(255, 255, 255),
            text_primary=(244, 246, 252),
            text_secondary=(206, 212, 226),
            accent=(255, 214, 102),
            accent_2=(124, 236, 255),
            danger=(255, 120, 120),
            success=(125, 245, 170),
            radius_l=22,
            radius_m=16,
            radius_s=12,
            pad_l=28,
            pad_m=18,
            pad_s=12,
        )


def vertical_gradient(surface: pygame.Surface, top: Color, bottom: Color) -> None:
    w, h = surface.get_size()
    for y in range(h):
        t = y / max(1, h - 1)
        c = (
            int(top[0] + (bottom[0] - top[0]) * t),
            int(top[1] + (bottom[1] - top[1]) * t),
            int(top[2] + (bottom[2] - top[2]) * t),
        )
        pygame.draw.line(surface, c, (0, y), (w, y))

