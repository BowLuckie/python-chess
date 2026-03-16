# Chess.py
# Bowie Luckie
# @TODO LIST

# Core gameplay DONE!
# [/] Implement move system (select piece → click destination)
# [/] Validate moves using get_legal_moves()
# [/] Switch turns after valid move
# [/] Piece logic 

# special rules
# [ ] En passant
# [/] Promotion
# [/] Castling
# [ ] other draws
#
# game rules
# [/] Check detection
# [/] Prevent moves that leave king in check
# [/] display checks
# [/] Checkmate detection
# [/] Stalemate detection

# UI improvements
# [/] Highlight legal moves
# [/] Display check/checkmate message
# [ ] flip board after each move

# code improvements
# [/] Separate code into modules?
# 
#
# [ ] AI opponent?

# made from scratch with NO chess libraries
# ALL assets stolen from chess.com
# some ai written code

# /----------- CODE -----------/

from types import FunctionType

import pygame
from typing import TypeAlias
from pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King
import subprocess, sys, os, json

def resource_path(relative_path: str) -> str:
    # _MEIPASS exists only when bundled by PyInstaller
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def restart_program():
    pygame.quit()
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit()

# ----------- DATA/SETUP -----------

# aliases
coordinate: TypeAlias = tuple[int, int]
Board: TypeAlias = list[list[None | Piece]]
Color: TypeAlias = tuple[int, int, int]

def data_path(filename: str) -> str:
    # ai code
    """
    Returns the path to a file next to the executable.
    Works both in dev and PyInstaller builds.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller: sys.executable is the exe path
        base_path = os.path.dirname(sys.executable)
    else:
        # Normal Python execution
        base_path = os.path.abspath(".")
    return os.path.join(base_path, filename)


SETTINGS_FILE = data_path("settings.json")

# Default settings
DEFAULT_SETTINGS = {
    "screen_size": 800  # default value
}

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            print("an error has occured")
            pass
    # If file missing or corrupted, return defaults
    return DEFAULT_SETTINGS.copy() # creates a new pointer in this scope and returns it


def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

# ------------------- BOARD SETUP -------------------
def standard_board() -> Board:
    board: Board = [[None]*8 for _ in range(8)]

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
    board[7][4] = King("w", "K")
    board[0][4] = King("b", "K")
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

def check_test_board() -> Board:
    board: Board = [[None]*8 for _ in range(8)]
    board[7][4] = King("w", "K")
    board[0][4] = King("b", "K")
    board[1][3] = Pawn("b", "p")
    board[6][5] = Pawn("w", "p")
    return board

def checkmate_test_board() -> Board:
    board: list[list[None | Piece]] = [[None]*8 for _ in range(8)]

    # Black king trapped on back rank
    board[0][4] = King("b", "K")      # e8
    board[1][3] = Pawn("b", "P")      # d7
    board[1][4] = Pawn("b", "P")      # e7
    board[1][5] = Pawn("b", "P")      # f7

    # White pieces delivering mate
    board[7][4] = King("w", "K")      # e1 (safe king)
    board[7][7] = Rook("w", "R")      # h1

    return board

def stalemate_test_board() -> Board:
    board: list[list[None | Piece]] = [[None]*8 for _ in range(8)]

    # Black king
    board[0][7] = King("b", "K")   # h8

    # White pieces
    board[1][5] = Queen("w", "Q")  # f7
    board[2][6] = King("w", "K")   # g6

    return board

def en_passant_test_board() -> Board:
    board: Board = [[None]*8 for _ in range(8)]

    # kings (to keep position legal)
    board[0][4] = King("b", "K")   # black king on e8
    board[7][4] = King("w", "K")   # white king on e1

    # pawns for en passant test
    board[6][4] = Pawn("w", "P")   # white pawn on e5
    board[4][3] = Pawn("b", "P")   # black pawn on d5 (just moved from d7)

    return board

print("\033[33mif you made a new board, add it to BOARDS and json.dump method below and delete settings.json to rebuild it. " 
"then change the board mode in the .json. board mode can only be changed if your running the .py file not the .exe\033[0m")
print("if you are running the exe, and can see this terminal, you are running a pre-release or a debug release.")

BOARDS: dict[str, FunctionType] = {
"standard": standard_board,
"promotion": promotion_test_board,
"castling": castling_test_board,
"check": check_test_board,
"checkmate": checkmate_test_board,
"stalemate": stalemate_test_board,
"enpassant": en_passant_test_board
}

def get_board_mode() -> str:
    path = resource_path("settings.json")
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data.get("board_mode", "standard")
    except FileNotFoundError:
        # create file with default modes if missing
        with open(path, "w") as f:
            json.dump({
                "board_mode": "standard",
                "available_modes": list(BOARDS.keys())
            }, f)
        return "standard"

board_mode = get_board_mode() # change to match keys in BOARDS dictionary

class GameState:  # this class contains all the mutable variables that migtht need to be accsed throughout the code
    def __init__(self):
        # adding type annotations can often catch runtime errors before as they are interpreted
        self.board: Board = BOARDS.get(board_mode, standard_board)() # .get allows us to specify a default value as apposeded to indexing which raises an error

        self.white_turn = True

        self.selected_square: None | coordinate = None
        self.legal_moves: list[coordinate] = []

        self.promotion_active = False
        self.promotion_square: coordinate | None = None
        self.promotion_color: str | None = None
        self.promotion_options: list[coordinate] = []

        self.white_king_pos: coordinate = (7, 4)
        self.black_king_pos: coordinate = (0, 4)

        if board_mode == "stalemate":
            self.black_king_pos = (0,7)
            self.white_king_pos = (2,6)

        self.last_double_pawn: coordinate | None = None

        self.game_over: bool = False
        self.winner: str | None = None

def set_screen_size(size: int):
    global WIDTH, HEIGHT, SQUARE_SIZE

    WIDTH = size
    HEIGHT = size
    SQUARE_SIZE = WIDTH // 8
    pygame.display.set_mode((WIDTH, HEIGHT))

settings = load_settings()

pygame.init()
pygame.font.init()
gamestate = GameState()

set_screen_size(settings.get("screen_size", 800))

ICON = pygame.image.load(resource_path("pieces/bp.png"))
screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")
pygame.display.set_icon(ICON)

running = True

LIGHT: Color = 230, 210, 170
DARK: Color = 184, 135, 98
COLOURS: list[Color] = [LIGHT, DARK] 
LIGHT_SELECTED: Color = 255, 250, 125
DARK_SELECTED: Color = 235, 205, 90
CHECKED_LIGHT: Color = 235, 121, 99
CHECKED_DARK: Color = 225, 105, 84

OPTIONS: list[str] = ["Q", "R", "B", "N"]

# ------------------- LOAD PIECE IMAGES -------------------

IMAGES = {}

pieces_list = ["wp", "wr", "wn", "wb", "wq", "wk",
            "bp", "br", "bn", "bb", "bq", "bk"]

for piece in pieces_list:
    p = pygame.image.load(resource_path("pieces/" + piece + ".png"))
    IMAGES[piece] = pygame.transform.scale(p, (SQUARE_SIZE, SQUARE_SIZE))

c = pygame.image.load(resource_path("pieces/crown.png"))
CROWN = pygame.transform.scale(c, (SQUARE_SIZE, SQUARE_SIZE))

d = pygame.image.load(resource_path("pieces/draw.png"))
DRAW = pygame.transform.scale(d, (SQUARE_SIZE, SQUARE_SIZE))

# ------------------- DRAWING FUNCTIONS -------------------

def text_outline(text, font_size=20, font_name="Arial", text_color=(255,255,255), outline_color=(0,0,0), outline_width=2, alpha=255, surf_size: int | None=None):
    font = pygame.font.SysFont(font_name, font_size)
    base = font.render(text, True, text_color).convert_alpha()
    size = (base.get_width() + outline_width*2, base.get_height() + outline_width*2)
    surf = pygame.Surface(size if surf_size is None else (surf_size, surf_size), pygame.SRCALPHA)

    for dx in range(-outline_width, outline_width+1):
        for dy in range(-outline_width, outline_width+1):
            if dx != 0 or dy != 0:
                outline = font.render(text, True, outline_color).convert_alpha()
                surf.blit(outline, (dx + outline_width, dy + outline_width))

    surf.blit(base, (outline_width, outline_width))
    surf.set_alpha(alpha)
    return surf


text_surf = text_outline(text="Press ESC to return to the main menu", alpha=150)

# Bottom-left position
text_rect: pygame.Rect = text_surf.get_rect(bottomleft=(10, HEIGHT - 10))

def draw_board(screen, highlighted: coordinate | None = None, checked: coordinate | None = None):
    for row in range(8):
        for col in range(8):
            colour = COLOURS[(row + col) % 2]

            if (row, col) == checked:
                if colour == LIGHT:
                    colour = CHECKED_LIGHT
                else:
                    colour = CHECKED_DARK

            if (row, col) == highlighted: # highlighted squares take priority over checked squares
                if colour == LIGHT or colour == CHECKED_LIGHT:
                    colour = LIGHT_SELECTED
                else:
                    colour = DARK_SELECTED

            pygame.draw.rect(
            screen,
            colour,
            (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        )

def draw_pieces(screen, board):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece is not None:
                screen.blit(IMAGES[piece.image_key()],
                        (col * SQUARE_SIZE, row * SQUARE_SIZE))

def draw_legal_moves(screen, moves: list[coordinate]):
# creates a temp surface with an alpha channel and blits that to the main screen surface
    for row, col in moves:
        circle_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)

        pygame.draw.circle(
        circle_surface,
        (0, 0, 0, 100),  # RGBA → last value is transparency (0–255)
        (SQUARE_SIZE // 2, SQUARE_SIZE // 2),
        SQUARE_SIZE // 6
    )

        screen.blit(circle_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))
    
def draw_promotion(colour):
    global OPTIONS
    menu = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE * 4))
    menu.fill((255,255,255)) 
    for i, piece_name in enumerate(OPTIONS):
        prom_menu_img = IMAGES[colour.lower() + piece_name.lower()]
        menu.blit(prom_menu_img, (0, i * SQUARE_SIZE))
    return menu

def display_prom_menu(color_in, promotion_square: coordinate, screen=screen):
    menu = draw_promotion(colour=color_in)
    prow, pcol = promotion_square
    x = pcol * SQUARE_SIZE
    y = prow * SQUARE_SIZE
    if prow == 0:
        screen.blit(menu, (x, y))
    else:
        y = (prow - 3) * SQUARE_SIZE
        screen.blit(menu, (x, y))

def draw_outcome(winner: str):
    global button

    BOX_HEIGHT = 4 * SQUARE_SIZE
    BOX_WIDTH = 6 * SQUARE_SIZE
    BORDER = 8

    draw = winner == "d"
    white_wins = winner == "w"

    box = pygame.Surface((BOX_WIDTH, BOX_HEIGHT), pygame.SRCALPHA)

    pygame.draw.rect(box, (30,30,30), (0,0,BOX_WIDTH,BOX_HEIGHT), border_radius=12)
    pygame.draw.rect(
        box,
        (240,240,240),
        (BORDER,BORDER,BOX_WIDTH-BORDER*2,BOX_HEIGHT-BORDER*2),
        border_radius=10
    )

    font_big = pygame.font.SysFont("Arial", 40, bold=True)
    font_btn = pygame.font.SysFont("Arial", 24)

    # --- TEXT ---
    if draw:
        text = "Draw by stalemate!"
    else:
        text = "White wins!" if white_wins else "Black wins!"

    victory_text = font_big.render(text, True, (0,0,0))
    text_rect = victory_text.get_rect(center=(BOX_WIDTH//2, (BOX_HEIGHT//4)-(SQUARE_SIZE*0.5)))
    box.blit(victory_text, text_rect)

    # --- IMAGE ---
    if draw:
        img = DRAW
    else:
        img = IMAGES["wp"] if white_wins else IMAGES["bp"]

    img_size = int(SQUARE_SIZE * 0.9)
    img = pygame.transform.smoothscale(img, (img_size, img_size))

    img_rect = img.get_rect(center=(BOX_WIDTH//2, BOX_HEIGHT//2))
    box.blit(img, img_rect)

    # --- CROWN (only for wins) ---
    if not draw:
        crown_size = int(SQUARE_SIZE * 0.7)
        crown = pygame.transform.smoothscale(CROWN, (crown_size, crown_size))

        crown_rect = crown.get_rect(
            midbottom=(img_rect.centerx, img_rect.top + 8)
        )
        box.blit(crown, crown_rect)

    # --- RESTART BUTTON ---
    BTN_W, BTN_H = 140, 80
    btn_x = BOX_WIDTH//2 - BTN_W//2
    btn_y = BOX_HEIGHT - BTN_H - 15

    button = pygame.Rect(btn_x, btn_y, BTN_W, BTN_H)

    pygame.draw.rect(box, (60,140,220), button, border_radius=8)
    pygame.draw.rect(box, (20,60,120), button, 2, border_radius=8)

    btn_text = font_btn.render("Restart", True, (255,255,255))
    btn_rect = btn_text.get_rect(center=button.center)
    box.blit(btn_text, btn_rect)

    return box


def display_outcome(winner: str, screen=screen):
    box = draw_outcome(winner)

    x = WIDTH // 2 - box.get_width() // 2
    y = HEIGHT // 2 - box.get_height() // 2

    screen.blit(box, (x, y))
    

    return pygame.Rect(x + button.x, y + button.y, button.width, button.height)

def build_bg() -> pygame.Surface:
    bg = pygame.Surface((WIDTH, HEIGHT))
    for row in range(8):
        for col in range(8):
            colour = COLOURS[(row + col) % 2]
            pygame.draw.rect(bg, colour,
                            (col * SQUARE_SIZE, row * SQUARE_SIZE,
                            SQUARE_SIZE, SQUARE_SIZE))
    return bg

# ------------------- LOGIC -------------------

def move_piece(gamestate: GameState, origin: coordinate, destination: coordinate, simulate=False):
    """
    Move a piece from `origin` to `destination` and update the game state. does not check if the move is legal
    """
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
        gamestate.promotion_color = piece.colour
    
        # calculate and store the four squares where the player can click
        gamestate.promotion_options = []
        start_row = trow if piece.colour == "w" else trow - 3 # 3 squares towards the top
        for i in range(4):
            gamestate.promotion_options.append((start_row + i, tcol))

    # castling
    if isinstance(piece, King) and abs(tcol - ocol) == 2: # checks if distance between origin and target is 2, hence a castle has happened
        if tcol == 6:
            rook = gamestate.board[trow][7]
            gamestate.board[trow][5] = rook
            gamestate.board[trow][7] = None
            if rook is not None and hasattr(rook, "has_moved") and not simulate:
                rook.has_moved = True # type: ignore
                # SAFTEY: the king can only move two squares if the rook exists in the right square, so the rook square will always contain a rook

        if tcol == 2:
            rook = gamestate.board[trow][0]
            gamestate.board[trow][3] = rook
            gamestate.board[trow][0] = None
            if rook is not None and hasattr(rook, "has_moved") and not simulate:
                rook.has_moved = True # type: ignore
                # SAFTEY: the king can only move two squares if the rook exists in the right square, so the rook square will always contain a rook 


    # update king position
    if isinstance(piece, King):
        if piece.colour == "w":
            gamestate.white_king_pos = (trow, tcol)
        else:
            gamestate.black_king_pos = (trow, tcol)

    # checkmat and stalemate detection
    if piece is not None and not simulate:
        # even though this looks like alot of code, its actually extremely simple

        enemy = "w" if piece.colour == "b" else "b"
        enemy_has_move = False

        for r in range(8):
            for c in range(8):
                p = gamestate.board[r][c]

                if p is None or p.colour != enemy: # only picks up pieces of the opposite colour
                    continue

                moves = p.get_legal_moves(gamestate.board, r, c)

                for move in moves:
                    if simulate_move(gamestate, (r, c), move): # if the move is allowed (hence it is a legal move), then the enemy has atleast 1 legal move and we dont have to check anymore moves
                        enemy_has_move = True
                        break

                if enemy_has_move:
                    break
            if enemy_has_move:
                break

        if not enemy_has_move:
            if king_in_check(gamestate, enemy):
                print("checkmate!")
                gamestate.game_over = True
                gamestate.winner = piece.colour
            else:
                print("stalemate!")
                gamestate.game_over = True
                gamestate.winner = "d"

        
            

    

    # flip turn after moving (even during a promotion selection state we consider the move done)
    if not simulate:
        gamestate.white_turn = not gamestate.white_turn

def square_is_attacked(square: coordinate, looking_color: str, gamestate: GameState):
    for r in range(8):
        for c in range(8):
            piece = gamestate.board[r][c]

            if piece is None:
                continue

            if piece.colour != looking_color:
                continue

            # pawn attacks
            if isinstance(piece, Pawn):
                direction = 1 if piece.colour == "b" else -1

                attack_squares = [
                (r + direction, c + 1),
                (r + direction, c - 1)
            ]

                for ar, ac in attack_squares:
                    if 0 <= ar < 8 and 0 <= ac < 8:
                        if (ar, ac) == square:
                            return True
            else:
                moves = piece.get_legal_moves(gamestate.board, r, c)

                if square in moves:
                    return True

    return False

def king_in_check(gamestate: GameState, colour):
    # build args
    king_pos = gamestate.white_king_pos if colour == "w" else gamestate.black_king_pos
    enemy = "b" if colour == "w" else "w"
    return square_is_attacked(king_pos, enemy, gamestate) # pass the args

def simulate_move(gamestate: GameState, origin: coordinate, target: coordinate) -> bool:
    """
    returns if a move is allowed (does not result in check)
    """
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

# For castling, save rook origin/destination so it can be restored after simulation
    rook_origin = None
    rook_dest = None
    rook_piece = None
    rook_dest_piece = None
    rook_has_moved = None

    if (isinstance(orig_piece, King) and abs(tcol - ocol) == 2): # if the king ever moves two squares, its a castle
        # save the rooks positions so they can be returned after the move is simulated
        if tcol == 6:  # kingside
            rook_origin = (trow, 7)
            rook_dest = (trow, 5)
        else:  # queenside
            rook_origin = (trow, 0)
            rook_dest = (trow, 3)

        rook_piece = gamestate.board[rook_origin[0]][rook_origin[1]]
        rook_dest_piece = gamestate.board[rook_dest[0]][rook_dest[1]]
        if rook_piece and hasattr(rook_piece, "has_moved"):
            rook_has_moved = rook_piece.has_moved

        # 1) King cannot castle out of check
        if king_in_check(gamestate, orig_piece.colour):
            return False

        # 2) King cannot castle through check (intermediate square)
        enemy = "b" if orig_piece.colour == "w" else "w"
        step = 1 if tcol > ocol else -1
        intermediate = (orow, ocol + step) # the square directly next to the king in the direction of the castle

        saved_intermediate = gamestate.board[intermediate[0]][intermediate[1]]
        gamestate.board[orow][ocol] = None
        gamestate.board[intermediate[0]][intermediate[1]] = orig_piece

        # temporarily update king position so square_is_attacked sees the king move
        if orig_piece.colour == "w":
            gamestate.white_king_pos = intermediate
        else:
            gamestate.black_king_pos = intermediate

        through_check = square_is_attacked(intermediate, enemy, gamestate)

        # restore
        gamestate.board[orow][ocol] = orig_piece
        gamestate.board[intermediate[0]][intermediate[1]] = saved_intermediate
        gamestate.white_king_pos = white_king_pos
        gamestate.black_king_pos = black_king_pos

        if through_check:
            return False
    
    move_piece(gamestate, origin, target, simulate=True)

# Check if king is in check
    if orig_piece is not None:
        in_check = king_in_check(gamestate, orig_piece.colour)
    else:
        in_check = False

    # return to original state
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

    # Restore castling rook position
    if rook_origin is not None and rook_dest is not None:
        gamestate.board[rook_origin[0]][rook_origin[1]] = rook_piece
        gamestate.board[rook_dest[0]][rook_dest[1]] = rook_dest_piece

        if rook_piece and hasattr(rook_piece, "has_moved") and rook_has_moved is not None:
            rook_piece.has_moved = rook_has_moved

    return (not in_check)

# ------------------- MOUSE CLICK -------------------

def piece_clicked(gamestate: GameState) -> coordinate | None:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    row = mouse_y // SQUARE_SIZE
    col = mouse_x // SQUARE_SIZE
    print(row,col)

    piece = gamestate.board[row][col]

    if ((row,col) == (5,4) or (row,col) == (5,3)) and gamestate.game_over == True: # (5,4) and (5,3) are roughly the squares that the reset button sits on
        # return all settings to defaults        
        gamestate.board = BOARDS.get(board_mode, standard_board)() # reset board back to the current board mode
        
        gamestate.selected_square = None
        gamestate.legal_moves = []

        gamestate.promotion_active = False
        gamestate.promotion_square = None
        gamestate.promotion_color = None
        gamestate.promotion_options = []

        gamestate.white_king_pos = (7, 4)
        gamestate.black_king_pos = (0, 4)
        if board_mode == "stalemate":
            gamestate.black_king_pos = (0,7)
            gamestate.white_king_pos = (2,6)
        gamestate.white_turn = True
        gamestate.game_over = False

        return None

    # If a piece is already selected, try to move it
    if gamestate.selected_square:
        if (row, col) in gamestate.legal_moves:
            move_piece(gamestate, gamestate.selected_square, (row, col)) # becuase legal moves is built on selection, we dont have to simulate the move
            gamestate.selected_square = None
            gamestate.legal_moves = []
            return None

    # Select a piece
    if piece is not None:
        if (gamestate.white_turn and piece.colour == "w") or (not gamestate.white_turn and piece.colour == "b"):
            pseudo_moves = piece.get_legal_moves(gamestate.board, row, col)
            gamestate.legal_moves = [move for move in pseudo_moves if simulate_move(gamestate, (row, col), move)]
            return (row, col)

    # otherwise clear selection
    gamestate.legal_moves = []
    return None

def handle_promotion(gamestate: GameState):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    row, col = mouse_y // SQUARE_SIZE, mouse_x // SQUARE_SIZE
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
def main():
    global running
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif gamestate.promotion_active and event.type == pygame.MOUSEBUTTONDOWN: # for some reason, scrolling also trigger this, and i dont know how to fix that
                handle_promotion(gamestate)
            elif not gamestate.promotion_active and event.type == pygame.MOUSEBUTTONDOWN:
                gamestate.selected_square = piece_clicked(gamestate)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("escape")
                    import menu
                    menu.main()


        square_in_check = gamestate.white_king_pos if king_in_check(gamestate, "w") else gamestate.black_king_pos if king_in_check(gamestate, "b") else None
        draw_board(screen, highlighted=gamestate.selected_square, checked=square_in_check)
        draw_pieces(screen, gamestate.board)
        draw_legal_moves(screen, gamestate.legal_moves)

        if gamestate.promotion_active and gamestate.promotion_square:
            piece = gamestate.board[gamestate.promotion_square[0]][gamestate.promotion_square[1]]
            if piece is not None:
                display_prom_menu(piece.colour, gamestate.promotion_square)

        if gamestate.game_over and gamestate.winner is not None:
            display_outcome(winner=gamestate.winner)
        
        screen.blit(text_surf, text_rect)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except pygame.error:
        print("pygame has been closed in another module or location.")
