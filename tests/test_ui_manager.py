import pygame

from game.ui_manager import GameVisuals, UIManager


def test_pause_buttons_ignore_hidden_menu_buttons() -> None:
    pygame.init()
    ui = UIManager(GameVisuals(screen_size=(1000, 600)))

    pause_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (500, 355), "button": 1})
    pause_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": (500, 355), "button": 1})

    assert ui.handle_mouse_event(pause_down, "paused") is None
    assert ui.handle_mouse_event(pause_up, "paused") == "restart"


def test_instruction_text_layout_fits_available_panel_space() -> None:
    pygame.init()
    ui = UIManager(GameVisuals(screen_size=(1000, 600)))

    panel_rect = pygame.Rect(40, 24, 920, 552)
    button_rect = pygame.Rect(1000 // 2 - 160, 600 - 96, 320, 54)
    text_top = panel_rect.y + 108
    text_bottom = button_rect.y - 24

    _, lines, line_height = ui._instruction_text_layout(panel_rect.w - 56, text_bottom - text_top)

    assert len(lines) * line_height <= text_bottom - text_top
