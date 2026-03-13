# Chess.py
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
# [/] Separate code into modules?
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

options_pieces: list[str] = ["Q", "R", "B", "N"]
promotion_active: bool = False
promotion_square: coordinate | None = None
promotion_color: str | None = None
promotion_options: list[coordinate] = []

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
    # board: list[list[None | Piece]] = [[None]*8 for _ in range(8)]

    # # black pieces
    # board[0] = [
    #     Rook("b", "R"), Knight("b", "N"), Bishop("b", "B"), Queen("b", "Q"),
    #     King("b", "K"), Bishop("b", "B"), Knight("b", "N"), Rook("b", "R")
    # ]
    # board[1] = [Pawn("b", "P") for _ in range(7)]

    # # white pieces
    # board[6] = [Pawn("w", "P") for _ in range(8)]
    # board[7] = [
    #     Rook("w", "R"), Knight("w", "N"), Bishop("w", "B"), Queen("w", "Q"),
    #     King("w", "K"), Bishop("w", "B"), Knight("w", "N"), Rook("w", "R")
    # ]

    # Testing board: promotions
    board: Board = [[None]*8 for _ in range(8)]

    # White pawns ready to promote on row 6 (one move to row 7)
    for col in range(8):
        board[6][col] = Pawn("b", "P")

    # Black pawns ready to promote on row 1 (one move to row 0)
    for col in range(8):
        board[1][col] = Pawn("w", "P")

    # Place kings in the center of opposite rows
    board[3][4] = King("w", "K")  # white king in center-bottom
    board[4][4] = King("b", "N")  # black king in center-top
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
        
def draw_promotion(color):
    global options_pieces
    menu = pygame.Surface((square_size, square_size * 4))
    menu.fill((255,255,255)) 
    for i, piece_name in enumerate(options_pieces):
        prom_menu_img = IMAGES[color.lower() + piece_name.lower()]
        menu.blit(prom_menu_img, (0, i * square_size))
    return menu
    
def display_prom_menu(color_in, promotion_square: coordinate, screen=screen):
    menu = draw_promotion(color=color_in)
    prow, pcol = promotion_square
    x = pcol * square_size
    y = prow * square_size
    if prow == 0:
        screen.blit(menu, (x, y))
    else:
        y = (prow - 3) * square_size
        screen.blit(menu, (x, y))

    
# ------------------- LOGIC -------------------

def move_piece(origin: coordinate, destination: coordinate):
    global white_turn, promotion_square, promotion_active, promotion_color, promotion_options
    orow, ocol = origin # origin-x and origin-y
    drow, dcol = destination
    
    board[drow][dcol] = board[orow][ocol] # dupe the piece into the new position
    board[orow][ocol] = None # remove old piece

   

    piece = board[drow][dcol]
    if piece is not None and hasattr(piece, "has_moved"): # checks if the peice has the "has_moved" attribute
        piece.has_moved = True

    # promotion
    if isinstance(piece, Pawn) and (drow == 7 or drow == 0):
        promotion_active = True
        promotion_square = (drow, dcol)
        promotion_color = piece.color
        
        # calculate and store the four squares where the player can click
        promotion_options = []
        start_row = drow if piece.color == "w" else drow - 3 # 3 squares towards the top
        for i in range(4):
            promotion_options.append((start_row + i, dcol))

    # flip turn after moving (even during a promotion selection state we consider the move done)
    white_turn = not white_turn

# ------------------- MOUSE CLICK -------------------

def piece_clicked() -> coordinate | None:
    global selecting, selected_square, white_turn, legal_moves

    mouse_x, mouse_y = pygame.mouse.get_pos()
    row = mouse_y // square_size
    col = mouse_x // square_size

    piece = board[row][col]
    print(row,col)
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

def handle_promotion():
    global promotion_options, promotion_square, promotion_color, white_turn, promotion_active, options_pieces
    mouse_x, mouse_y = pygame.mouse.get_pos()
    row, col = mouse_y // square_size, mouse_x // square_size
    if (row, col) in promotion_options and promotion_square is not None:
        options_classes = [Queen, Rook, Bishop, Knight]
        options_letters = ["Q", "R", "B", "N"]  # must match the image keys

        chosen_index = row - promotion_options[0][0]
        board[promotion_square[0]][promotion_square[1]] = options_classes[chosen_index](
            promotion_color,
            options_letters[chosen_index]
        )

        board[promotion_square[0]][promotion_square[1]] = options_classes[chosen_index](promotion_color, options_letters[chosen_index])
        print(f"promoted pawn at {promotion_square} to {options_classes[chosen_index]} letter: {options_letters[chosen_index]}")
        # reset all the promotion related values
        promotion_active = False
        promotion_square = None
        promotion_color = None
        promotion_options = []
        

            
# ------------------- MAIN LOOP -------------------

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif promotion_active and event.type == pygame.MOUSEBUTTONDOWN:
            handle_promotion()
        elif not promotion_active and event.type == pygame.MOUSEBUTTONDOWN:
            selected_square = piece_clicked()

    draw_board(screen, highlighted=selected_square)
    draw_legal_moves(screen, legal_moves)
    draw_pieces(screen, board)
    if promotion_active and promotion_square:
        display_prom_menu(board[promotion_square[0]][promotion_square[1]].color, promotion_square)
    pygame.display.flip()

pygame.quit()