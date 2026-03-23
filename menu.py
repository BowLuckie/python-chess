from time import sleep
import pygame
import pygame_gui
import chess
import settings
import pygame.transform


pygame.init()

ICON = pygame.image.load(chess.resource_path("pieces/bp.png"))
screen = pygame.display.set_mode((chess.WIDTH, chess.HEIGHT))
pygame.display.set_caption("Chess")
pygame.display.set_icon(ICON)


theme_file = chess.resource_path("theme.json")
manager = pygame_gui.UIManager((chess.WIDTH, chess.HEIGHT), theme_path=theme_file)

font_big = pygame.font.SysFont("Arial", 40, bold=True)

title_text = chess.text_outline("Python Chess", font_size=100, outline_width=4)
title_rect = title_text.get_rect(center=(chess.WIDTH//2, chess.HEIGHT//4))

ai_text = chess.text_outline("The AI has gained magic powers...", outline_width=1)
ai_rect: pygame.Rect = ai_text.get_rect(bottomleft=(10, chess.HEIGHT - 10))

ai_boost = False

# --- pygame_gui UI elements ---
friend_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(chess.WIDTH//2 - 100, chess.HEIGHT//2 - 50, 200, 50),
    text="Play against friend",
    manager=manager
)

solo_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(chess.WIDTH//2 - 100, chess.HEIGHT//2 + 10, 200, 50),
    text="Play Against Ai",
    manager=manager
)

settings_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(chess.WIDTH//2 - 100, chess.HEIGHT//2 + 70, 200, 50),
    text="Settings",
    manager=manager
)

quit_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(chess.WIDTH//2 - 100, chess.HEIGHT//2 + 130, 200, 50),
    text="Quit",
    manager=manager
)

clock: pygame.Clock = pygame.time.Clock()

def main():
    global ai_boost
    bg = chess.build_bg()

    try:
        blurred = pygame.transform.box_blur(bg, radius=7)
    except AttributeError:
        blurred = bg

    screen.blit(blurred)

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == friend_button:
                    chess.main(ai=False)
                    
                elif event.ui_element == solo_button:
                    chess.main(ai=True, ai_b=ai_boost)     
                           
                elif event.ui_element == settings_button:
                    settings.main()
                    
                elif event.ui_element == quit_button:
                    running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                row, col = (mouse_x//chess.SQUARE_SIZE, mouse_y//chess.SQUARE_SIZE)

                if (row, col) == (6, 1):
                    ai_boost = not ai_boost

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sleep(.1)
                    running = False

            manager.process_events(event)

        manager.update(time_delta)

        screen.blit(blurred) # gaussian blur could also be used, but it is much slower so we will have to take the quality tradeoff
        screen.blit(title_text, title_rect)

        if ai_boost:  
            screen.blit(ai_text, ai_rect)

        manager.draw_ui(screen)

        if chess.settings.get("evil_mode"):
            screen.blit(settings.evil_text, settings.evil_rect)

        pygame.display.flip()

    pygame.display.quit()
    return 

if __name__ == "__main__":
    try:
        main()
    except pygame.error as e:
        if str(e) != "video system not initialized" or str(e) != "Surface is not initialized":
            print(e)