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
# [/] Castling
#
# game rules
# [/] Check detection
# [/] Prevent moves that leave king in check
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


# /----------- CODE -----------/

import pygame
from typing import TypeAlias
from pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King



# /----------- DATA/SETUP -----------/

# aliases
coordinate: TypeAlias = tuple[int, int]
Board: TypeAlias = list[list[None | Piece]]

# ------------------- BOARD SETUP -------------------
def standard_board() -> Board:
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

def promotion_test_board() -> Board:
    board: Board = [[None]*8 for _ in range(8)]
    # white pawns ready to promote
    for col in range(8):
        board[6][col] = Pawn("w", "P")
    # black pawns ready to promote
    for col in range(8):
        board[1][col] = Pawn("b", "P")
    # kings in the center
    board[0][4] = King("w", "K")
    board[7][4] = King("b", "K")
    return board

def empty_board() -> Board:
    return [[None]*8 for _ in range(8)]

def castling_test_board() -> Board:
    board: Board = [[None]*8 for _ in range(8)]

    # white pieces
    board[7][4] = King("w", "K")
    board[7][0] = Rook("w", "R")
    board[7][7] = Rook("w", "R")

    # black pieces
    board[0][4] = King("b", "K")
    board[0][0] = Rook("b", "R")
    board[0][7] = Rook("b", "R")

    return board

BOARDS = {
    "standard": standard_board,
    "promotion": promotion_test_board,
    "empty": empty_board,
    "castling": castling_test_board,
}

board_mode = "promotion" # change to match keys in BOARDS dictionary

class GameState:  # this class contains all the mutable variables that migtht need to be accsed throughout the code
    def __init__(self):
        self.board: Board = BOARDS[board_mode]()

        self.white_turn = True

        self.selected_square: None | coordinate = None
        self.legal_moves: list[coordinate] = []

        self.promotion_active = False
        self.promotion_square: coordinate | None = None
        self.promotion_color: str | None = None
        self.promotion_options: list[coordinate] = []

        self.white_king_pos: coordinate = (7, 4)
        self.black_king_pos: coordinate = (0, 4)

pygame.init()

size = 800
WIDTH, HEIGHT = size, size
square_size = size // 8 # each square length is 80 pixels

icon = pygame.image.load("pieces/bp.png")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")
pygame.display.set_icon(icon)

running = True

light = 237, 214, 176
dark = 184, 135, 98
colors = [light, dark] 
light_selected = (247, 235, 114)
dark_selected = (220, 196, 75)

options_pieces: list[str] = ["Q", "R", "B", "N"]

# ------------------- LOAD PIECE IMAGES -------------------

IMAGES = {}

pieces_list = ["wp", "wr", "wn", "wb", "wq", "wk",
               "bp", "br", "bn", "bb", "bq", "bk"]

for piece in pieces_list:
    p = pygame.image.load("pieces/" + piece + ".png")
    IMAGES[piece] = pygame.transform.scale(p, (square_size, square_size))

gamestate = GameState()

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

def move_piece(gamestate: GameState, origin: coordinate, destination: coordinate, simulate=False):
    orow, ocol = origin # origin-x and origin-y
    trow, tcol = destination
    
    gamestate.board[trow][tcol] = gamestate.board[orow][ocol] # dupe the piece into the new position
    gamestate.board[orow][ocol] = None # remove old piece

   

    piece = gamestate.board[trow][tcol]
    if piece is not None and hasattr(piece, "has_moved") and not simulate: # checks if the peice has the "has_moved" attribute
        piece.has_moved = True

    # promotion
    if isinstance(piece, Pawn) and (trow == 7 or trow == 0) and not simulate:
        gamestate.promotion_active = True
        gamestate.promotion_square = (trow, tcol)
        gamestate.promotion_color = piece.color
        
        # calculate and store the four squares where the player can click
        gamestate.promotion_options = []
        start_row = trow if piece.color == "w" else trow - 3 # 3 squares towards the top
        for i in range(4):
            gamestate.promotion_options.append((start_row + i, tcol))
    
    if isinstance(piece, King) and abs(tcol - ocol) == 2: # checks if distance between origin and target is 2, hence a castle has happened
        if tcol == 6:
            rook = gamestate.board[trow][7]
            gamestate.board[trow][5] = rook
            gamestate.board[trow][7] = None
            if rook is not None and hasattr(rook, "has_moved") and not simulate:
                rook.has_moved = True # type: ignore

        if tcol == 2:
            rook = gamestate.board[trow][0]
            gamestate.board[trow][3] = rook
            gamestate.board[trow][0] = None
            if rook is not None and hasattr(rook, "has_moved") and not simulate:
                rook.has_moved = True # type: ignore

    if isinstance(piece, King):
        if piece.color == "w":
            gamestate.white_king_pos = (trow, tcol)
        else:
            gamestate.black_king_pos = (trow, tcol)

    # flip turn after moving (even during a promotion selection state we consider the move done)
    if not simulate:
        gamestate.white_turn = not gamestate.white_turn

def square_is_attacked(square: coordinate, looking_color: str, gamestate: GameState):
    for r in range(8):
        for c in range(8):
            piece = gamestate.board[r][c]

            if piece is None:
                continue

            if piece.color != looking_color:
                continue

            # pawn attacks
            if isinstance(piece, Pawn):

                direction = 1 if piece.color == "b" else -1

                attack_squares = [
                    (r + direction, c + 1),
                    (r + direction, c - 1)
                ]

                for ar, ac in attack_squares:
                    if 0 <= ar < 8 and 0 <= ac < 8:
                        if (ar, ac) == square:
                            return True
            else:
                moves = piece.get_attack_squares(gamestate.board, r, c)

                if square in moves:
                    return True

    return False

def king_in_check(gamestate: GameState, color):
    # build args
    king_pos = gamestate.white_king_pos if color == "w" else gamestate.black_king_pos
    enemy = "b" if color == "w" else "w"
    return square_is_attacked(king_pos, enemy, gamestate) # pass the args

def simulate_move(gamestate: GameState, origin: coordinate, target: coordinate):
    # Save original state
    orow, ocol = origin
    trow, tcol = target

    orig_piece = gamestate.board[orow][ocol]
    target_piece = gamestate.board[trow][tcol]
    white_king_pos = gamestate.white_king_pos
    black_king_pos = gamestate.black_king_pos
    promotion_active = gamestate.promotion_active
    promotion_square = gamestate.promotion_square
    promotion_color = gamestate.promotion_color
    promotion_options = gamestate.promotion_options.copy()

    # Save has_moved flags
    orig_has_moved = orig_piece.has_moved if orig_piece and hasattr(orig_piece, "has_moved") else None
    target_has_moved = target_piece.has_moved if target_piece and hasattr(target_piece, "has_moved") else None

    # For castling, save rook has_moved
    rook_has_moved = None
    if isinstance(orig_piece, King) and abs(tcol - ocol) == 2:
        if tcol == 6:  # kingside
            rook = gamestate.board[trow][7]
        else:  # queenside
            rook = gamestate.board[trow][0]
        if rook and hasattr(rook, "has_moved"):
            rook_has_moved = rook.has_moved

    # Make the move
    move_piece(gamestate, origin, target, simulate=True)

    # Check if king is in check
    if orig_piece is not None:
        in_check = king_in_check(gamestate, orig_piece.color)
    else:
        in_check = False

    # Undo move
    gamestate.board[orow][ocol] = orig_piece
    gamestate.board[trow][tcol] = target_piece
    gamestate.white_king_pos = white_king_pos
    gamestate.black_king_pos = black_king_pos
    gamestate.promotion_active = promotion_active
    gamestate.promotion_square = promotion_square
    gamestate.promotion_color = promotion_color
    gamestate.promotion_options = promotion_options

    # Restore has_moved flags
    if orig_piece and hasattr(orig_piece, "has_moved") and orig_has_moved is not None:
        orig_piece.has_moved = orig_has_moved
    if target_piece and hasattr(target_piece, "has_moved") and target_has_moved is not None:
        target_piece.has_moved = target_has_moved
    if rook_has_moved is not None:
        if tcol == 6:
            rook = gamestate.board[trow][7]
        else:
            rook = gamestate.board[trow][0]
        if rook and hasattr(rook, "has_moved"):
            rook.has_moved = rook_has_moved

    return not in_check

# ------------------- MOUSE CLICK -------------------

def piece_clicked(gamestate: GameState) -> coordinate | None:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    row = mouse_y // square_size
    col = mouse_x // square_size

    piece = gamestate.board[row][col]
    # If a piece is already selected, try to move it
    if gamestate.selected_square:
        if (row, col) in gamestate.legal_moves:
            move_piece(gamestate, gamestate.selected_square, (row, col))
            gamestate.selected_square = None
            gamestate.legal_moves = []
            return None

    # Select a piece
    if piece is not None:
        if (gamestate.white_turn and piece.color == "w") or (not gamestate.white_turn and piece.color == "b"):
            pseudo_moves = piece.get_legal_moves(gamestate.board, row, col)
            gamestate.legal_moves = [move for move in pseudo_moves if simulate_move(gamestate, (row, col), move)]
            return (row, col)

    # otherwise clear selection
    gamestate.legal_moves = []
    return None

def handle_promotion(gamestate: GameState):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    row, col = mouse_y // square_size, mouse_x // square_size
    if (row, col) in gamestate.promotion_options and gamestate.promotion_square is not None:
        options_classes = [Queen, Rook, Bishop, Knight]
        options_letters = ["Q", "R", "B", "N"]  # must match the image keys

        chosen_index = row - gamestate.promotion_options[0][0]
        gamestate.board[gamestate.promotion_square[0]][gamestate.promotion_square[1]] = options_classes[chosen_index](
            gamestate.promotion_color,
            options_letters[chosen_index]
        )

        # reset all the promotion related values
        gamestate.promotion_active = False
        gamestate.promotion_square = None
        gamestate.promotion_color = None
        gamestate.promotion_options = []
        

            
# ------------------- MAIN LOOP -------------------

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif gamestate.promotion_active and event.type == pygame.MOUSEBUTTONDOWN:
            handle_promotion(gamestate)
        elif not gamestate.promotion_active and event.type == pygame.MOUSEBUTTONDOWN:
            gamestate.selected_square = piece_clicked(gamestate)

    draw_board(screen, highlighted=gamestate.selected_square)
    draw_legal_moves(screen, gamestate.legal_moves)
    draw_pieces(screen, gamestate.board)
    if gamestate.promotion_active and gamestate.promotion_square:
        piece = gamestate.board[gamestate.promotion_square[0]][gamestate.promotion_square[1]]
        if piece is not None:
            display_prom_menu(piece.color, gamestate.promotion_square)
    pygame.display.flip()

pygame.quit()