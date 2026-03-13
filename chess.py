# Chess_class.py
# Bowie Luckie
#
# Made from scratch with NO chess libraries
# TODO LIST
#
# Core gameplay DONE!
# [/] Implement move system (select piece → click destination)
# [/] Validate moves using get_legal_moves()
# [/] Switch turns after valid move
#
# Piece logic [/]
#
# special rules
# [ ] En passant
# [/] Promotion
# [ ] Castling
#
# game rules
# [ ] Check detection
# [ ] Prevent moves that leave king in check
# [ ] Checkmate detection
# [ ] Stalemate detection
#
# UI improvements
# [/] Highlight legal moves
# [ ] Display check/checkmate message
#
# code improvements
# [ ] Separate code into modules?
#       board.py
#       pieces.py
#       game.py
#       main.py
#
# [ ] AI opponent?

import pygame
from typing import TypeAlias
from pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King

coordinate: TypeAlias = tuple[int, int]

# /----------- DATA -----------/


size = 800
WIDTH, HEIGHT = size, size
square_size = size // 8 # each square length is 80 pixels
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")

icon = pygame.image.load("python chess/pieces/bp.png")
pygame.display.set_icon(icon)

white_turn = True
turn = "w" if white_turn else "b"
running = True
selected_square: None | coordinate = None
selecting: bool = False

light = (240,217,181)
dark = (181,136,99)
colors = [light, dark] 
light_selected = (234, 125, 107)
dark_selected = (211, 109, 81)

legal_moves: list[tuple[int,int]] = []

# ------------------- LOAD PIECE IMAGES -------------------

IMAGES = {}

pieces_list = ["wp", "wr", "wn", "wb", "wq", "wk",
               "bp", "br", "bn", "bb", "bq", "bk"]

for piece in pieces_list:
    p = pygame.image.load("python chess/pieces/" + piece + ".png")
    IMAGES[piece] = pygame.transform.scale(p, (square_size, square_size))

# ------------------- BOARD SETUP -------------------
Board: TypeAlias = list[list[None | Piece]]
def create_board() -> Board:
    board: list[list[None | Piece]] = [[None]*8 for _ in range(8)]

    # black pieces
    board[0] = [
        Rook("b", "R"), Knight("b", "N"), Bishop("b", "B"), Queen("b", "Q"),
        King("b", "K"), Bishop("b", "B"), Knight("b", "N"), Rook("b", "R")
    ]
    board[1] = [Pawn("b", "P") for _ in range(8)]

    # white pieces
    board[6] = [Pawn("w", "P") for _ in range(8)]
    board[7] = [
        Rook("w", "R"), Knight("w", "N"), Bishop("w", "B"), Queen("w", "Q"),
        King("w", "K"), Bishop("w", "B"), Knight("w", "N"), Rook("w", "R")
    ]
    return board

board: Board = create_board()

# ------------------- DRAWING FUNCTIONS -------------------

def draw_board(screen, highlighted: coordinate | None = None):
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]

            if highlighted == (row, col):
                
                if color == light:
                    color = light_selected
                else:
                    color = dark_selected

            pygame.draw.rect(
                screen,
                color,
                (col * square_size, row * square_size, square_size, square_size)
            )

def draw_pieces(screen, board):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece is not None:
                screen.blit(IMAGES[piece.image_key()],
                            (col * square_size, row * square_size))

def draw_legal_moves(screen, moves: list[coordinate]):
    # creates a temp surface with an alpha channel and blits that to the main screen surface
    for row, col in moves:
        circle_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)

        pygame.draw.circle(
            circle_surface,
            (0, 0, 0, 100),  # RGBA → last value is transparency (0–255)
            (square_size // 2, square_size // 2),
            square_size // 6
        )

        screen.blit(circle_surface, (col * square_size, row * square_size))
# ------------------- LOGIC -------------------

def move_piece(origin: coordinate, destination: coordinate):
    global white_turn
    orow, ocol = origin # origin-x and origin-y
    drow, dcol = destination
    
    board[drow][dcol] = board[orow][ocol] # dupe the piece into the new position
    board[orow][ocol] = None # remove old piece

    white_turn = not white_turn # toggle the turn state

    piece = board[drow][dcol]
    if piece is not None and hasattr(piece, "has_moved"): # checks if the peice has the "has_moved" attribute
        piece.has_moved = True

    # promotiom
    if isinstance(piece, Pawn) and drow == 7 or drow == 0:
        old_col = piece.color if piece is not None else "w"
        board[drow][dcol] = Queen(old_col, "Q")

    print(f"DEBUG: move piece at {origin} to {destination}")

def draw_promotion(color):
    options: list[str] = ["Q", "R", "B", "K"]
    menu = pygame.Surface((square_size * 4, square_size))
    for i, piece_name in enumerate(options):
        prom_menu_img = IMAGES[color.lower() + piece_name.lower()]
        menu.blit(prom_menu_img, (i * square_size, 0))
    return menu, color
    
def display_prom_menu(color, screen=screen):
    # @TODO
    menu, color = draw_promotion(color=color)
    

# ------------------- MOUSE CLICK -------------------

def piece_clicked():
    global selecting, selected_square, white_turn, legal_moves

    mouse_x, mouse_y = pygame.mouse.get_pos()
    row = mouse_y // square_size
    col = mouse_x // square_size

    piece = board[row][col]

    # If a piece is already selected, try to move it
    if selected_square:
        if (row, col) in legal_moves:
            move_piece(selected_square, (row, col))
            selected_square = None
            legal_moves = []
            return None

    # Select a piece
    if piece is not None:
        if (white_turn and piece.color == "w") or (not white_turn and piece.color == "b"):
            legal_moves = piece.get_legal_moves(board, row, col)
            return (row, col)

    # otherwise clear selection
    legal_moves = []
    return None

# ------------------- MAIN LOOP -------------------
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            selected_square = piece_clicked()

    draw_board(screen, highlighted=selected_square)
    draw_legal_moves(screen, legal_moves)
    draw_pieces(screen, board)
    pygame.display.flip()

pygame.quit()