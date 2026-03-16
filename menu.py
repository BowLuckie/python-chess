import pygame
import pygame_gui
import chess
import subprocess, sys, os

def blur_surface(surface: pygame.Surface, scale_factor: float=0.1):
    small = pygame.transform.smoothscale(surface, (int(surface.get_width()*scale_factor),
                                                   int(surface.get_height()*scale_factor)))
    return pygame.transform.smoothscale(small, surface.get_size())

pygame.init()

ICON = pygame.image.load(chess.resource_path("pieces/bp.png"))
screen = pygame.display.set_mode((chess.WIDTH, chess.HEIGHT))
pygame.display.set_caption("Chess")
pygame.display.set_icon(ICON)

manager = pygame_gui.UIManager((chess.WIDTH, chess.HEIGHT))

font_big = pygame.font.SysFont("Arial", 40, bold=True)

title_text = font_big.render("Python Chess", True, (0,0,0))
title_rect = title_text.get_rect(center=(chess.WIDTH//2, chess.HEIGHT//4))

bg = pygame.Surface((chess.WIDTH, chess.HEIGHT))
for row in range(8):
    for col in range(8):
        colour = chess.COLOURS[(row + col) % 2]
        pygame.draw.rect(bg, colour,
                         (col * chess.SQUARE_SIZE, row * chess.SQUARE_SIZE,
                          chess.SQUARE_SIZE, chess.SQUARE_SIZE))

# --- pygame_gui UI elements ---
start_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(chess.WIDTH//2 - 100, chess.HEIGHT//2 - 50, 200, 50),
    text="Start Game",
    manager=manager
)

settings_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(chess.WIDTH//2 - 100, chess.HEIGHT//2 + 10, 200, 50),
    text="Settings",
    manager=manager
)

quit_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(chess.WIDTH//2 - 100, chess.HEIGHT//2 + 70, 200, 50),
    text="Quit",
    manager=manager
)

clock: pygame.Clock = pygame.time.Clock()
running: bool = True
if __name__ == "__main__":
    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button:

                    pygame.quit() # close the menu window

                    # Run chess.py
                    chess_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chess.py')
                    subprocess.run([sys.executable, chess_script])
                    sys.exit()  # Ensure menu process ends
                            
                elif event.ui_element == settings_button:
                    pygame.quit() # close the menu window

                    # Run chess.py
                    chess_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.py')
                    subprocess.run([sys.executable, chess_script])
                    sys.exit()  # Ensure menu process ends

                elif event.ui_element == quit_button:
                    running = False

            manager.process_events(event)

        manager.update(time_delta)

        screen.blit(blur_surface(bg), (0, 0))
        screen.blit(title_text, title_rect)

        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()