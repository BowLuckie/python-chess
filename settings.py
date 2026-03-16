import pygame
import pygame_gui
import menu
import chess

pygame.init()

ICON = pygame.image.load(chess.resource_path("pieces/bp.png"))
screen = pygame.display.set_mode((chess.WIDTH, chess.HEIGHT))
pygame.display.set_caption("Chess")
pygame.display.set_icon(ICON)

clock: pygame.Clock = pygame.time.Clock()
running: bool = True

manager = pygame_gui.UIManager((chess.WIDTH, chess.HEIGHT))

settings_text = menu.font_big.render("Settings", True, (0,0,0))
settings_rect = settings_text.get_rect(center=(chess.WIDTH//2, chess.HEIGHT//4))

bg = pygame.Surface((chess.WIDTH, chess.HEIGHT))
for row in range(8):
    for col in range(8):
        colour = chess.COLOURS[(row + col) % 2]
        pygame.draw.rect(bg, colour,
                         (col * chess.SQUARE_SIZE, row * chess.SQUARE_SIZE,
                          chess.SQUARE_SIZE, chess.SQUARE_SIZE))

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(menu.blur_surface(bg), (0, 0))
    screen.blit(settings_text, settings_rect)

    pygame.display.flip()

pygame.quit()