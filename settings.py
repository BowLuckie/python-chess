import pygame
import pygame_gui
import chess
import pygame.transform

pygame.init()

ICON = pygame.image.load(chess.resource_path("pieces/bp.png"))
screen = pygame.display.set_mode((chess.WIDTH, chess.HEIGHT))
pygame.display.set_caption("Chess")
pygame.display.set_icon(ICON)

clock: pygame.Clock = pygame.time.Clock()
restart_requested = False

if "evil_mode" not in chess.settings:
    chess.settings["evil_mode"] = False

theme_file = chess.resource_path("theme.json")
manager = pygame_gui.UIManager((chess.WIDTH, chess.HEIGHT), theme_path=theme_file)

font_big = pygame.font.SysFont("Arial", 40, bold=True)

settings_text = chess.text_outline("Settings", font_size=100, outline_width=4)
settings_rect = settings_text.get_rect(center=(chess.WIDTH//2, chess.HEIGHT//4))

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

sb = pygame.image.load(chess.resource_path(r"pieces\ws.png"))
soldier_button = pygame.transform.scale(sb, (chess.SQUARE_SIZE, chess.SQUARE_SIZE))

e = pygame.image.load(chess.resource_path(r"pieces\evil.png"))
evil_text = pygame.transform.scale(e, (chess.SQUARE_SIZE * 4, chess.SQUARE_SIZE*2))
evil_rect = evil_text.get_rect(center=(chess.WIDTH // 2, (chess.HEIGHT // 4) + chess.SQUARE_SIZE * 0.79))

def main():
    global restart_requested, evil_mode
    running = True

    # Build bg and blur here
    bg = chess.build_bg()
    try:
        blurred = pygame.transform.box_blur(bg, radius=7)
    except AttributeError:
        blurred = bg

    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse = pygame.mouse.get_pos()
                mx, my = mouse

                if mx // chess.SQUARE_SIZE == 0 and my // chess.SQUARE_SIZE == 7:
                    print("evil!!")
                    chess.settings["evil_mode"] = not chess.settings["evil_mode"]
                    chess.save_settings(chess.settings)

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == back_button:
                    import menu
                    menu.main()
                elif event.ui_element == size600_button:
                    chess.settings["screen_size"] = 600
                    chess.save_settings(chess.settings)
                    restart_requested = True
                elif event.ui_element == size800_button:
                    chess.settings["screen_size"] = 800
                    chess.save_settings(chess.settings)
                    restart_requested = True
                elif event.ui_element == size1000_button:
                    chess.settings["screen_size"] = 1000
                    chess.save_settings(chess.settings)
                    restart_requested = True
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    import menu
                    menu.main()

            manager.process_events(event)

        manager.update(time_delta)

        screen.blit(blurred)
        screen.blit(settings_text, settings_rect)
        screen.blit(soldier_button, (0*chess.SQUARE_SIZE,7*chess.SQUARE_SIZE))
        manager.draw_ui(screen)

        if chess.settings.get("evil_mode"):
            screen.blit(evil_text, evil_rect)

        pygame.display.flip()

        if restart_requested:
            running = False

    if restart_requested:
        pygame.display.quit()   # close only the window
        chess.restart_program() # never returns

    # normal exit back to menu
    pygame.display.quit()
    return
    

if __name__ == "__main__":
    try:
        main()
    except pygame.error as e:
        if str(e) != "video system not initialized" or str(e) != "Surface is not initialized":
            print(e)