from time import sleep
import pygame
import pygame_gui
import src.chess as chess
import src.settings as settings

pygame.init()

ICON = pygame.image.load(chess.asset_path("pieces/bp.png"))
screen = pygame.display.set_mode((chess.WIDTH, chess.HEIGHT))
pygame.display.set_caption("Chess")
pygame.display.set_icon(ICON)

theme_file = chess.asset_path("theme.json")
manager = pygame_gui.UIManager((chess.WIDTH, chess.HEIGHT), theme_path=theme_file)

font_big = pygame.font.SysFont("Arial", 40, bold=True)

title_text = chess.text_outline("Python Chess", font_size=100, outline_width=4)
title_rect = title_text.get_rect(center=(chess.WIDTH // 2, chess.HEIGHT // 4))


ai_boost = False
mod_menu_open = False

friend_button = pygame_gui.elements.UIButton(
    pygame.Rect(chess.WIDTH // 2 - 100, chess.HEIGHT // 2 - 50, 200, 50),
    "Play against friend",
    manager,
)

solo_button = pygame_gui.elements.UIButton(
    pygame.Rect(chess.WIDTH // 2 - 100, chess.HEIGHT // 2 + 10, 200, 50),
    "Play Against AI",
    manager,
)

settings_button = pygame_gui.elements.UIButton(
    pygame.Rect(chess.WIDTH // 2 - 100, chess.HEIGHT // 2 + 70, 200, 50),
    "Settings",
    manager,
)

quit_button = pygame_gui.elements.UIButton(
    pygame.Rect(chess.WIDTH // 2 - 100, chess.HEIGHT // 2 + 130, 200, 50),
    "Quit",
    manager,
)

mods_button = pygame_gui.elements.UIButton(
    pygame.Rect(10, 10, 120, 40),
    "Mods",
    manager,
)

mod_panel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect(10, 60, 220, 180),
    manager=manager,
    visible=0,
)

ai_boost_toggle = pygame_gui.elements.UIButton(
    pygame.Rect(10, 10, 200, 40),
    "MEGA AI: OFF",
    manager,
    container=mod_panel,
)

evil_mode_toggle = pygame_gui.elements.UIButton(
    pygame.Rect(10, 60, 200, 40),
    "Evil Mode: OFF",
    manager,
    container=mod_panel,
)

clock = pygame.time.Clock()


def main():
    global ai_boost, mod_menu_open

    bg = chess.build_bg()

    try:
        blurred = pygame.transform.box_blur(bg, radius=7)
    except AttributeError:
        blurred = bg

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame_gui.UI_BUTTON_PRESSED:

                if event.ui_element == friend_button:
                    chess.main(ai=False)

                elif event.ui_element == solo_button:
                    chess.main(ai=True, ai_b=ai_boost)

                elif event.ui_element == settings_button:
                    settings.main()

                elif event.ui_element == quit_button:
                    return

                elif event.ui_element == mods_button:
                    mod_menu_open = not mod_menu_open
                    mod_panel.show() if mod_menu_open else mod_panel.hide()

                elif event.ui_element == ai_boost_toggle:
                    ai_boost = not ai_boost
                    ai_boost_toggle.set_text(f"MEGA AI: {'ON' if ai_boost else 'OFF'}")

                elif event.ui_element == evil_mode_toggle:
                    current = chess.settings.get("evil_mode", False)
                    chess.settings["evil_mode"] = not current
                    evil_mode_toggle.set_text(
                        f"Evil Mode: {'ON' if not current else 'OFF'}"
                    )

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sleep(0.1)
                    return

            manager.process_events(event)

        manager.update(time_delta)

        screen.blit(blurred)
        screen.blit(title_text, title_rect)

        manager.draw_ui(screen)

        if chess.settings.get("evil_mode"):
            screen.blit(settings.evil_text, settings.evil_rect)

        pygame.display.flip()

    pygame.display.quit()


if __name__ == "__main__":
    try:
        main()
    except pygame.error as e:
        if str(e) not in ("video system not initialized", "Surface is not initialized"):
            print(e)
