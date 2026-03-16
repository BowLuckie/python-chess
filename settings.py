import pygame
import pygame_gui
import chess

pygame.init()

ICON = pygame.image.load(chess.resource_path("pieces/bp.png"))
screen = pygame.display.set_mode((chess.WIDTH, chess.HEIGHT))
pygame.display.set_caption("Chess")
pygame.display.set_icon(ICON)

clock: pygame.Clock = pygame.time.Clock()
running: bool = True

theme_file = chess.resource_path("theme.json")
manager = pygame_gui.UIManager((chess.WIDTH, chess.HEIGHT), theme_path=theme_file)

font_big = pygame.font.SysFont("Arial", 40, bold=True)

settings_text = chess.text_outline("Settings", font_size=100, outline_width=4)
settings_rect = settings_text.get_rect(center=(chess.WIDTH//2, chess.HEIGHT//4))

bg = chess.build_bg()

size600_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(chess.WIDTH//2 - 100, chess.HEIGHT//2 - 60, 200, 50),
    text="600 x 600",
    manager=manager,
)

size800_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(chess.WIDTH//2 - 100, chess.HEIGHT//2 , 200, 50),
    text="800 x 800",
    manager=manager
)

size1000_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(chess.WIDTH//2 - 100, chess.HEIGHT//2 + 60, 200, 50),
    text="1000 x 1000",
    manager=manager
)

back_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(chess.WIDTH//2 - 100, chess.HEIGHT//2 + 120, 200, 50),
    text="back",
    manager=manager,
)



def main():
    global running
    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == back_button:
                    import menu # putting the import here avoid the circular import error (this is messy)
                    menu.main()
            
                if event.ui_element == size600_button:
                    chess.settings["screen_size"] = 600
                    chess.save_settings(chess.settings)
                    chess.restart_program()

                if event.ui_element == size800_button:
                    chess.settings["screen_size"] = 800
                    chess.save_settings(chess.settings)
                    chess.restart_program()

                if event.ui_element == size1000_button:
                    chess.settings["screen_size"] = 1000
                    chess.save_settings(chess.settings)
                    chess.restart_program()

            manager.process_events(event)

        manager.update(time_delta)

        screen.blit(pygame.transform.box_blur(bg, radius=7)) # gaussian blur could also be used, but it is much slower so we will have to take the quality tradeoff
        screen.blit(settings_text, settings_rect)

        manager.draw_ui(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()