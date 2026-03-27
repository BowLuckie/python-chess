# Chess.py
# Bowie Luckie
# @TODO LIST
#
# Core gameplay
# [/] Implement move system (select piece → click destination)
# [/] Validate moves using get_legal_moves()
# [/] Switch turns after valid move
# [/] Piece logic 
#
# special rules
# [/] En passant
# [/] Promotion
# [/] Castling
# [/] other draws
#
# game rules
# [/] Check detection
# [/] Prevent moves that leave king in check
# [/] display checks
# [/] Checkmate detection
# [/] Stalemate detection
#
# UI improvements
# [/] Highlight legal moves
# [/] Display check/checkmate message
# [/] flip board after each move?
#
# code improvements
# [/] Separate code into modules?
# 
#
# [/] AI opponent
# [/] fix _MEIPASS handling
#
# made from scratch with NO chess libraries
# ALL assets stolen from chess.com
# some ai written code

# /----------- CODE -----------/

import pygame
import copy
from types import FunctionType
from typing import TypeAlias
import subprocess, sys, os, json
from random import choice

from pieces import (
    # classics
    Piece,
    Pawn,
    Knight,
    Bishop,
    Planet,
    Rook,
    Queen,
    King,
    
    # others
    Soldier,
    Elephant,
    Dog,
    Vampire,
    Planet
)

from chess_ai import move_ai

# ----------- DATA/SETUP -----------

# aliases
coordinate: TypeAlias = tuple[int, int]
Board: TypeAlias = list[list[None | Piece]]
Color: TypeAlias = tuple[int, int, int]

def data_path(filename: str, writeable=False) -> str:
    """
    Returns a path to a file next to the executable.
    If writeable=True, returns a path that can be written to.
    """
    if writeable:
        # always save next to exe or in dev folder
        base_path = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.abspath(".")
    else:
        # read-only bundled resources
        base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, filename)

SETTINGS_FILE = data_path("settings.json", writeable=True)

# Default settings
DEFAULT_SETTINGS = {
    "screen_size": 800,  # default value
    "evil_mode": False
}

def load_settings() -> dict:
    """
    returns a dictionary of all the settings in the settings.json file. it this file doesnt exist, it creates a new one
    """
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            print("an error has occured attempting to load settings.json")
            pass
    return DEFAULT_SETTINGS.copy() # creates a new pointer in this scope and returns it

def save_settings(settings: dict):
    """
    dump any changes made in the dictionary built by `load_settings()` back into settings.json
    """
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

class KingError(Exception):
    """
    Kings Not Found
    """
    pass

LEFTCLICK = 1

# ------------------- BOARD SETUP -------------------

# each board is a function that returns a Board type, which is just an alias for list[list[None | Piece]], so each square will either have a Piece class or a None.

def standard_board() -> Board:
    """
    returns a board object that is the default setup for a chess board.
    """
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
    for col in range(2):
        board[6][col] = Pawn("b", "P")
    for col in range(2):
        board[1][col] = Pawn("w", "P")
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
    board[1][7] = Pawn("w", "P")      # h1

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
    board[5][5] = Rook("w", "R")

    return board

def draw_by_insufmat() -> Board:
    board: Board = [[None]*8 for _ in range(8)]

    # kings
    board[0][4] = King("b", "K")  # black king on e8
    board[7][4] = King("w", "K")  # white king on e1

    # extra pieces
    board[6][3] = Queen("b", "Q")  # white knight on d2


    return board

def test_ai_prom() -> Board:
    board: Board = [[None]*8 for _ in range(8)]

    board[0][0] = King("b", "K")

  
    board[6][1] = Soldier("b", "S")
   
    board[7][7] = King("w", "K")

    board[5][6] = Queen("w", "Q")

    return board

def evil_board() -> Board:
    board: Board = [[None]*8 for _ in range(8)]

# black pieces
    board[0] = [
    Elephant("b", "E"), Dog("b", "H"), Planet("b", "C"), Vampire("b", "V"),
    King("b", "D"), Planet("b", "C"), Dog("b", "H"), Elephant("b", "E")
]
    board[1] = [Soldier("b", "s") for _ in range(8)]

# white pieces
    board[6] = [Soldier("w", "s") for _ in range(8)]
    board[7] = [
    Elephant("w", "E"), Dog("w", "H"), Planet("w", "C"), Vampire("w", "V"),
    King("w", "D"), Planet("w", "C"), Dog("w", "H"), Elephant("w", "E")
]
    return board

def evil_game_over() -> Board:
    board: Board = [[None]*8 for _ in range(8)]

    board[0][4] = King("b", "D")
    board[7][4] = King("w", "D")
 
    board[1][0] = Soldier("w", "S")
    board[2][1] = Vampire("w", "V")

    return board

BOARDS: dict[str, FunctionType] = {
"standard": standard_board,
"promotion": promotion_test_board,
"castling": castling_test_board,
"check": check_test_board,
"checkmate": checkmate_test_board,
"stalemate": stalemate_test_board,
"enpassant": en_passant_test_board,
"insufficientmat": draw_by_insufmat,
"aipromotion": test_ai_prom,
"evil": evil_board,
"evilcheckmate": evil_game_over,
}

def resource_path(relative_path: str) -> str:
    """
    defines a resource path that is not editable
    """
    # _MEIPASS exists only when bundled by PyInstaller
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def restart_program():
    """
    Restart the application.
    When frozen by PyInstaller --onefile, launch the original exe (sys.argv[0]).
    When running normally, launch the Python interpreter (sys.executable).
    """
    if getattr(sys, "frozen", False):
        # sys.argv[0] is the path to the original exe the user launched
        exe_to_run = os.path.abspath(sys.argv[0])
        args = [exe_to_run]
    else:
        exe_to_run = sys.executable
        args = [exe_to_run] + sys.argv

    try:
        subprocess.Popen(args)
    except Exception:
        # fallback - try launching sys.executable anyway
        subprocess.Popen([sys.executable] + sys.argv)
    finally:
        # exit cleanly
        sys.exit(0)

def get_board_mode() -> str:
    """
    looks in the settings file for the board mode
    """
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
    """
    Contains all relavant global mutable variables.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        """
        acts like an `__init__` function but can be recalled
        """
        # adding type annotations can often catch runtime errors before as they are interpreted
        self.board: Board = BOARDS.get(board_mode, standard_board)() # .get allows us to specify a default value as apposeded to indexing which raises an error
        if settings.get("evil_mode") and settings.get("board_mode") == "standard":
            self.board = (BOARDS.get("evil") or standard_board)()


        self.white_turn = True

        self.selected_square: None | coordinate = None
        self.legal_moves: list[coordinate] = []

        self.promotion_active = False
        self.promotion_square: coordinate | None = None
        self.promotion_color: str | None = None
        self.promotion_click_locations: list[coordinate] = []

        try:
            self.white_king_pos, self.black_king_pos = self.find_kings()
        except IndexError:
            raise KingError(f"Board is missing a king! kings found: white: {self.white_king_pos if hasattr(GameState, "white_king_pos") else None}, "
                            f"black: {self.black_king_pos if hasattr(GameState, "black_king_pos") else None}")

        self.last_double_pawn: coordinate | None = None
        self.en_passant_square: coordinate | None = None

        self.evil_mode: bool = settings.get("evil_mode", False)

        self.game_over: bool = False
        self.winner: str | None = None
        self.draw_type: str | None = None

    def find_kings(self) -> tuple[coordinate, coordinate]:
        """loops through each square until it finds a king and puts it into that colour"""
        bk = None
        wk = None
        for row in range(8):
            for col in range(8):
                p = self.board[row][col]

                if isinstance(p, King):
                    if p.colour == "w":
                        wk = (row, col)
                    else:
                        bk = (row, col)
        if wk is None or bk is None:
            raise KingError
        return wk, bk

def set_screen_size(size: int):
    """sets the screen width of the display being used in the file you run it in"""
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

ai_glob: bool = True # if chess.py is "__main__" then this is the default it takes
ai_boost = False

move_counter: int = 0

LIGHT: Color = 230, 210, 170
DARK: Color = 184, 135, 98
LIGHT_SELECTED: Color = 255, 250, 125
DARK_SELECTED: Color = 235, 205, 90
CHECKED_LIGHT: Color = 235, 121, 99
CHECKED_DARK: Color = 225, 105, 84

COLOURS: list[Color] = [LIGHT, DARK] 



def build_options(gamestate=gamestate):
    """
    builds the options for promotion based off wether evil mode is on or off. returns two lists that contain the proper promotion options that the promotion functions will use
    """
    CLASSES_OPTIONS = [(Queen, "Q"), (Rook, "R"), (Bishop, "B"), (Knight, "N")]
    if gamestate.evil_mode:
        CLASSES_OPTIONS = [(Vampire, "V"), (Elephant, "E"), (Planet, "C"), (Dog, "H")]
    OPTIONS = [n for _, n in CLASSES_OPTIONS]
    return CLASSES_OPTIONS, OPTIONS

classes_options, options = build_options(gamestate)

# ------------------- LOAD PIECE IMAGES -------------------

IMAGES = {}

original = ["wp", "wr", "wn", "wb", "wq", "wk",
            "bp", "br", "bn", "bb", "bq", "bk",]

evil = ["ws", "we", "wh", "wd", "wv", "wv", "wc", "bc", "bv", "bd", "bh", "bs", "be"]

# Piece prefixes
# s - white soldier
# e - white elephant
# h - white hound (dog)
# d - white dictator (evil mode king)
# v - white vampire
# c - white celestial body (moon or sun)

custom = []

pieces_list = original + evil + custom

try:
    # load images
    for piece in pieces_list:
        # loop through each element in pieces_list and check if it has a corrosponding png in pieces/
        p = pygame.image.load(resource_path("pieces/" + piece + ".png"))
        IMAGES[piece] = pygame.transform.scale(p, (SQUARE_SIZE, SQUARE_SIZE))

    # other images
    c = pygame.image.load(resource_path("pieces/crown.png"))
    CROWN = pygame.transform.scale(c, (SQUARE_SIZE, SQUARE_SIZE))

    d = pygame.image.load(resource_path("pieces/draw.png"))
    DRAW = pygame.transform.scale(d, (SQUARE_SIZE, SQUARE_SIZE))

except FileNotFoundError as e:
        print("\033[31mAn error has occured attempting to load some images!")
        print(f"{e}\033[0m")

# ------------------- DRAWING FUNCTIONS -------------------

def text_outline(text, font_size=20, font_name="Arial", text_color=(255,255,255), outline_color=(0,0,0), outline_width=2, alpha=255, surf_size: int | None=None) -> pygame.Surface:
    """
    Render text with an outline onto a pygame surface.

    Creates a surface containing the given text with a configurable outline,
    font, colors, transparency, and optional fixed surface size.
    """
    font = pygame.font.SysFont(font_name, font_size)
    base = font.render(text, True, text_color).convert_alpha()
    size = (base.get_width() + outline_width*2, base.get_height() + outline_width*2)
    surf = pygame.Surface(size if surf_size is None else (surf_size, surf_size), pygame.SRCALPHA)

    # create copies of each letter slighty larger
    for dirx in range(-outline_width, outline_width+1):
        for diry in range(-outline_width, outline_width+1):
            if dirx != 0 or diry != 0:
                outline = font.render(text, True, outline_color).convert_alpha()
                surf.blit(outline, (dirx + outline_width, diry + outline_width))

    surf.blit(base, (outline_width, outline_width))
    surf.set_alpha(alpha)
    return surf

exit_surf = text_outline(text="Press ESC to return to the main menu", alpha=150)
exit_rect: pygame.Rect = exit_surf.get_rect(bottomleft=(10, HEIGHT - 10)) # Bottom-left position

ai_surf = text_outline(text="Playing against AI", alpha=150)
ai_rect: pygame.Rect = ai_surf.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))

def draw_board(screen, highlighted: coordinate | None = None, checked: coordinate | None = None):
    """
    draws the chess board onto the screen `screen` with and highlighted or checked squares
    """
    for row in range(8):
        for col in range(8):
            colour = COLOURS[(row + col) % 2] # Square color is determined by parity of (col + row)

            # overwrite the colours
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

def draw_pieces(screen, board=gamestate.board, flipped: bool=False):
    """
    draws each piece onto the screen based of the gived board object which is always `gamestate.board` 

    will also draw them flipped in order to compensate for the general rotation that takes place in the `main()` function
    """
    try: # sometimes quitting the program can not communicate to the drawing functions
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece is not None and not flipped:
                    screen.blit(IMAGES[piece.image_key()],
                            (col * SQUARE_SIZE, row * SQUARE_SIZE))
                elif piece is not None and flipped:
                    screen.blit(pygame.transform.rotate(IMAGES[piece.image_key()], 180),
                            (col * SQUARE_SIZE, row * SQUARE_SIZE))
    except KeyError as e:
        print("\033[31mAn error has occured attempting to load some images! if you made a custom piece make sure it add it to custom[]")
        print(f"{e}\033[0m")
        return

def draw_legal_moves(screen, moves: list[coordinate]):
    """
    creates a temp surface with an alpha channel containing small grey dot and blits that to the main screen surface at the specified positions
    """

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
    global options
    menu = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE * 4))
    menu.fill((255,255,255)) 
    for i, piece_name in enumerate(options):
        prom_menu_img = IMAGES[colour.lower() + piece_name.lower()]
        if not gamestate.white_turn:
            prom_menu_img = pygame.transform.rotate(prom_menu_img, 180) # flip promotion options because they are their own surface
        menu.blit(prom_menu_img, (0, i * SQUARE_SIZE))
    return menu

def display_prom_menu(color_in, promotion_square: coordinate, screen=screen):
    """
    displays the created promotion menu to the screen through the `pygame.blit` method
    """
    menu = draw_promotion(colour=color_in)
    prow, pcol = promotion_square
    x = pcol * SQUARE_SIZE
    y = prow * SQUARE_SIZE
    if prow == 0:
        screen.blit(menu, (x, y))
    else:
        y = (prow - 3) * SQUARE_SIZE
        screen.blit(menu, (x, y))

def draw_outcome(winner: str) -> pygame.Surface:
    global button

    BOX_HEIGHT = 4 * SQUARE_SIZE
    BOX_WIDTH = 6 * SQUARE_SIZE
    BORDER = 8

    draw = (winner == "d") # draw is a bool
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

    # TEXT
    if draw and gamestate.draw_type:
        text = "Draw by " + gamestate.draw_type + "!"
    elif draw:
        text = "Draw!"
    else:
        text = "White wins!" if white_wins else "Black wins!"

    victory_text = font_big.render(text, True, (0,0,0))
    text_rect = victory_text.get_rect(center=(BOX_WIDTH//2, (BOX_HEIGHT//4)-(SQUARE_SIZE*0.5)))
    box.blit(victory_text, text_rect)

    # IMAGE
    if draw:
        img = DRAW
    else:
        img = IMAGES["wp"] if white_wins else IMAGES["bp"]

    img_size = int(SQUARE_SIZE * 0.9)
    img = pygame.transform.smoothscale(img, (img_size, img_size))

    img_rect = img.get_rect(center=(BOX_WIDTH//2, BOX_HEIGHT//2))
    box.blit(img, img_rect)

    # CROWN is for wins only
    if not draw:
        crown_size = int(SQUARE_SIZE * 0.7)
        crown = pygame.transform.smoothscale(CROWN, (crown_size, crown_size))

        crown_rect = crown.get_rect(
            midbottom=(img_rect.centerx, img_rect.top + 8)
        )
        box.blit(crown, crown_rect)

    # restart button (i made this before i discovered pygame_gui)
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

def display_outcome(winner: str, screen=screen, flipped: bool=False):
    box = draw_outcome(winner)

    # place the outcome in the middle of the screen
    x = WIDTH // 2 - box.get_width() // 2
    y = HEIGHT // 2 - box.get_height() // 2

    screen.blit(box, (x, y))
    if flipped:
        screen.blit(pygame.transform.rotate(box, 180), (x, y))

    return pygame.Rect(x + button.x, y + button.y, button.width, button.height)

def build_bg() -> pygame.Surface:
    """
    returns a surface object that is a board using the same consts as the `draw_board` funtion but without the highlighting
    """
    bg = pygame.Surface((WIDTH, HEIGHT))
    for row in range(8):
        for col in range(8):
            colour = COLOURS[(row + col) % 2] # Square color is determined by parity of (col + row)
            pygame.draw.rect(bg, colour,
                            (col * SQUARE_SIZE, row * SQUARE_SIZE,
                            SQUARE_SIZE, SQUARE_SIZE))
    return bg

# ------------------- LOGIC -------------------

def insufficient_mat(board: Board) -> bool:
    """
    checks the passed board object and returns a bool based of whether it is insufficient matiriel or not
    """
    white_pieces: list[tuple[Piece, coordinate]] = []
    black_pieces: list[tuple[Piece, coordinate]] = []

    for row in range(8):
        for col in range(8):
            p = board[row][col]
            if isinstance(p, Piece) and not isinstance(p, King):
                if p.colour == "w":
                    white_pieces.append((p, (row, col)))
                else:
                    black_pieces.append((p, (row, col)))

    # ive just added in the evil mode pieces but i havent tested whst situations lead to a draw

    # K vs K
    if len(white_pieces) == 0 and len(black_pieces) == 0:
        return True

    # K+minor vs K
    if len(white_pieces) == 1 and len(black_pieces) == 0:
        if isinstance(white_pieces[0][0], (Bishop, Knight, Dog, Planet)):
            return True

    if len(white_pieces) == 0 and len(black_pieces) == 1:
        if isinstance(black_pieces[0][0], (Bishop, Knight, Dog, Planet)):
            return True

    # K+B vs K+B same square color
    if len(white_pieces) == 1 and len(black_pieces) == 1:
        wp, wsq = white_pieces[0]
        bp, bsq = black_pieces[0]
        if isinstance(wp, (Bishop, Planet)) and isinstance(bp, (Bishop, Planet)):
            if (wsq[0] + wsq[1]) % 2 == (bsq[0] + bsq[1]) % 2:
                return True

    return False

def move_piece(gamestate: GameState, origin: coordinate, target: coordinate, simulate=False, ai_move=False, double: bool=False):
    """
    Move a piece from `origin` to `destination` and update the game state. does not check if the move is legal and only handels promotion, castling and mate
    """
    global move_counter
    orow, ocol = origin # origin-x and origin-y
    trow, tcol = target

    gamestate.board[trow][tcol] = gamestate.board[orow][ocol] # dupe the piece into the new position
    gamestate.board[orow][ocol] = None # remove old piece

    piece = gamestate.board[trow][tcol]
    if piece is not None and hasattr(piece, "has_moved") and not simulate: # checks if the peice has the "has_moved" attribute
        piece.has_moved = True

    # if (trow, tcol) == gamestate.en_passant_square
    promotion_move = False

    # promotion
    if (isinstance(piece, Pawn) or isinstance(piece, Soldier)) and (trow == 7 or trow == 0) and not simulate:
        promotion_move = True
        gamestate.promotion_active = True
        gamestate.promotion_square = (trow, tcol)
        gamestate.promotion_color = piece.colour
    
        # calculate and store the four squares where the player can click
        gamestate.promotion_click_locations = []
        start_row = trow if piece.colour == "w" else trow - 3 # 3 squares towards the top
        for i in range(4):
            gamestate.promotion_click_locations.append((start_row + i, tcol))

    # castling
    if isinstance(piece, King) and abs(tcol - ocol) == 2: # checks if distance between origin and target is 2, hence a castle has happened
        if tcol == 6:
            rook = gamestate.board[trow][7]
            gamestate.board[trow][5] = rook
            gamestate.board[trow][7] = None
            if rook is not None and hasattr(rook, "has_moved") and not simulate:
                rook.has_moved = True 
                
        if tcol == 2:
            rook = gamestate.board[trow][0]
            gamestate.board[trow][3] = rook
            gamestate.board[trow][0] = None
            if rook is not None and hasattr(rook, "has_moved") and not simulate:
                rook.has_moved = True 
                
    if isinstance(piece, Pawn) and abs(trow - orow) == 2:
        direction = -1 if piece.colour == "w" else 1
        gamestate.last_double_pawn = (trow, tcol)
        gamestate.en_passant_square = (trow - direction, tcol)

    if isinstance(piece, Pawn) and target == gamestate.en_passant_square and gamestate.last_double_pawn is not None:
        gamestate.board[gamestate.last_double_pawn[0]][gamestate.last_double_pawn[1]] = None

    # update king position
    if piece is not None and isinstance(piece, King):
        if piece.colour == "w":
            gamestate.white_king_pos = (trow, tcol)
        else:
            gamestate.black_king_pos = (trow, tcol)

    # checkmat and stalemate detection
    if piece is not None and not simulate:

        enemy = "w" if piece.colour == "b" else "b"
        enemy_has_move = False

        # loop through each piece and check if it has a move, if it does then break and communicate through enemy_has_move flag
        for r in range(8):
            for c in range(8):
                p = gamestate.board[r][c]

                if p is None or p.colour != enemy: # only picks up pieces of the opposite colour
                    continue

                moves = p.get_legal_moves(gamestate.board, r, c, gamestate)

                for move in moves:
                    if simulate_move(gamestate, (r, c), move): # if the move is allowed (hence it is a legal move), then the enemy has atleast 1 legal move and we dont have to check anymore moves
                        enemy_has_move = True
                        break

                if enemy_has_move:
                    break
            if enemy_has_move:
                break

        if insufficient_mat(gamestate.board):
                    gamestate.winner = "d"
                    gamestate.game_over = True
                    gamestate.draw_type = "insufficient material"

        if not enemy_has_move:
            if king_in_check(gamestate, enemy):
                gamestate.game_over = True
                gamestate.winner = piece.colour
                return
            else:
                gamestate.game_over = True
                gamestate.winner = "d"
                gamestate.draw_type = "stalemate"
                return

        move_counter += 1

        if not ai_move and ai_glob: # if the last move was human and the gamemode is set to ai
            if not ((isinstance(piece, Pawn) or isinstance(piece, Soldier)) and target[0] == 0): # if human didnt move a pawn to the back rank
                if ai_boost:
                    move_ai(gamestate, double=True) # preform an additional move that doesnt flip the turn so the next move can flip it
                score = move_ai(gamestate, ai_move)
                print(f"ai liked that move: {score}")
                
            else:
                return # breaks out of the function

    # flip turn after moving (even during a promotion selection state we consider the move done)
    if not (simulate or double or (not ai_glob and promotion_move)):
        gamestate.white_turn = not gamestate.white_turn



def square_is_attacked(square: coordinate, looking_color: str, gamestate: GameState) -> bool:
    """
    returns whether a square is being attacked in the current board state. 

    this should not be used as a general attack map function. instead use `chess_ai.attack_map()`
    """
    if gamestate.game_over:
        return False
    
    for r in range(8):
        for c in range(8):
            piece = gamestate.board[r][c]

            if piece is None or piece.colour != looking_color:
                continue

            # pawn attacks
            if isinstance(piece, Pawn):
                direction = 1 if piece.colour == "b" else -1
                attack_squares = [(r + direction, c + 1), (r + direction, c - 1)]

                for ar, ac in attack_squares:
                    if 0 <= ar < 8 and 0 <= ac < 8:
                        if (ar, ac) == square:
                            return True

            # king attacks 
            elif isinstance(piece, King):
                directions = [(1,0), (-1,0), (0,1), (0,-1),
                              (1,1), (-1,1), (-1,-1), (1,-1)]

                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        if (nr, nc) == square:
                            return True

            # all other pieces
            else:
                moves = piece.get_legal_moves(gamestate.board, r, c, gamestate)
                if square in moves:
                    return True

    return False

def king_in_check(gamestate: GameState, colour):
    """
    build king position and enemy arguments and calls square is attacked on them
    """
    # build args
    king_pos = gamestate.white_king_pos if colour == "w" else gamestate.black_king_pos
    enemy = "b" if colour == "w" else "w"
    return square_is_attacked(king_pos, enemy, gamestate) # pass the args

def simulate_move(gamestate: GameState, origin: coordinate, target: coordinate) -> bool:
    """
    moves a piece on a copy of the gamestate and check if any rules are broken
    """
    # create a complete copy of the game state
    if gamestate.game_over:
        return False
    temp_state = copy.deepcopy(gamestate)
    
    piece = temp_state.board[origin[0]][origin[1]] # capture the piece before it was moved
    move_piece(temp_state, origin, target, simulate=True)
    
    # determine color
    colour = piece.colour if piece else None
    if colour is None:
        return True  # nothing to move, technically not illegal
    
    # Check if king is in check after the simulated move
    return not king_in_check(temp_state, colour)

# ------------------- MOUSE CLICK -------------------

def piece_clicked(gamestate: GameState, mouse_pos: coordinate) -> coordinate | None:
    """
    returns a coordinate for highlighting or clicking
    """
    mouse_x, mouse_y = mouse_pos
    row = mouse_y // SQUARE_SIZE
    col = mouse_x // SQUARE_SIZE
    print(row,col)

    piece = gamestate.board[row][col]

    if gamestate.game_over and ((gamestate.white_turn and (row, col) in [(5, 4), (5, 3)])): # (5,4) and (5,3) are roughly the squares that the reset button sits on. 
        gamestate.reset()

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
        if ai_glob and piece.colour == "b": # black pieces can never be selected under any circumstances if ai_mode is on
            return None
        if (gamestate.white_turn and piece.colour == "w") or (not gamestate.white_turn and piece.colour == "b"):
            pseudo_moves = piece.get_legal_moves(gamestate.board, row, col, gamestate)
            gamestate.legal_moves = [move for move in pseudo_moves if simulate_move(gamestate, (row, col), move)] # simulate every move in psuedo moves and if they sucseed add them here
            return (row, col)

    # otherwise clear selection
    gamestate.legal_moves = []
    return None

def handle_promotion(gamestate: GameState, mouse_pos: coordinate):
    mouse_x, mouse_y = mouse_pos
    row, col = mouse_y // SQUARE_SIZE, mouse_x // SQUARE_SIZE
    if (row, col) in gamestate.promotion_click_locations and gamestate.promotion_square is not None:
        options_classes = [p for p, _ in classes_options]
        options_letters = [n for _, n in classes_options]  # must match the image keys

        chosen_index = row - gamestate.promotion_click_locations[0][0]
        gamestate.board[gamestate.promotion_square[0]][gamestate.promotion_square[1]] = options_classes[chosen_index](
        gamestate.promotion_color,
        options_letters[chosen_index])
        gamestate.white_turn = not gamestate.white_turn
        enemy = "w" if gamestate.promotion_color == "b" else "b"

        # check for checkmate or stalemate after promotion
        if king_in_check(gamestate, enemy):
            enemy_has_move = False

            for r in range(8):
                for c in range(8):
                    p = gamestate.board[r][c]

                    if p is None or p.colour != enemy: # only picks up pieces of the opposite colour
                        continue

                    moves = p.get_legal_moves(gamestate.board, r, c, gamestate)

                    for move in moves:
                        if simulate_move(gamestate, (r, c), move): # if the move is allowed (hence it is a legal move), then the enemy has atleast 1 legal move and we dont have to check anymore moves
                            enemy_has_move = True
                            break

                    if enemy_has_move:
                        break
                if enemy_has_move:
                    break

            
            if not enemy_has_move:
                gamestate.game_over = True
                if king_in_check(gamestate, enemy):
                    gamestate.winner = gamestate.promotion_color
                else:
                    gamestate.winner = "d"
                    gamestate.draw_type = "stalemate"


    # reset all the promotion related values
        gamestate.promotion_active = False
        gamestate.promotion_square = None
        gamestate.promotion_color = None
        gamestate.promotion_click_locations = []
        if gamestate.game_over:
            return
        
    if ai_glob and not gamestate.promotion_active: # the ai shouldnt move if promotion is active and should only move at the end of handle_promotion
        if ai_boost:
            move_ai(double=True, gamestate=gamestate)
        move_ai(gamestate=gamestate)
        gamestate.white_turn = True
        
def event_handling():
    """
    checks all current events and acts on them
    """
    global running
    for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFTCLICK:
                mx, my = event.pos

                if not gamestate.white_turn and gamestate.game_over == False: # i forgot to add a check for is the game is over so thats why the menu has to check for squares 5,4
                    # flip the mouses percived position if al elements are flipped 
                    mx = screen.get_width() - mx
                    my = screen.get_height() - my

                if gamestate.promotion_active:
                    handle_promotion(gamestate, (mx, my))
                else:
                    gamestate.selected_square = piece_clicked(gamestate, (mx, my))
                    if gamestate.game_over:
                        gamestate.selected_square = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    import menu # import menu at this scope to avoid circular import
                    menu.main()

# ------------------- MAIN LOOP -------------------

print("\033[33mif you made a new board, add it to BOARDS and json.dump method below and delete settings.json to rebuild it. " 
"then change the board mode in the .json. board mode can only be changed if your running the .py file not the .exe\033[0m")
print("if you are running the exe, and can see this terminal, you are running a pre-release or a debug release.")

def main(ai: bool=ai_glob, ai_b: bool=ai_boost):
    """
    Run the main game loop.

    Initializes game state, handles events, updates visuals, and manages gameplay
    flow including AI, promotions, check states, and endgame display until exit.
    """
    global ai_glob, ai_boost, classes_options, options
    ai_glob = ai
    ai_boost = ai_b
    gamestate.reset()
    running = True  # local running flag

    # overwite board if evil mode is on
    if settings.get("evil_mode") and settings.get("board_mode", "None") in ("standard", "None"):
        gamestate.board = (BOARDS.get("evil") or standard_board)()

    classes_options, options = build_options(gamestate)

    while running:  
        running = event_handling()
        if running is None:
            running = True

        square_in_check = (
            gamestate.white_king_pos if king_in_check(gamestate, "w") else 
            gamestate.black_king_pos if king_in_check(gamestate, "b") else None
            )
        
        # make losing king square checked
        if gamestate.game_over and gamestate.winner is not None:
            square_in_check = gamestate.white_king_pos if gamestate.winner == "b" else gamestate.black_king_pos

        if gamestate.game_over and gamestate.winner == "d":
            square_in_check = None # if its a draw, no one wins

        draw_board(screen, highlighted=gamestate.selected_square, checked=square_in_check)
        draw_pieces(screen, gamestate.board, flipped=not gamestate.white_turn and not gamestate.game_over) # becuase the whole screen will do a full rotation, we need to do a pre-emptive flip to account for it
        draw_legal_moves(screen, gamestate.legal_moves)

        if gamestate.promotion_active and gamestate.promotion_square:
            piece = gamestate.board[gamestate.promotion_square[0]][gamestate.promotion_square[1]]
            if piece is not None:
                display_prom_menu(piece.colour, gamestate.promotion_square)
                

        if gamestate.game_over and gamestate.winner is not None:
            display_outcome(winner=gamestate.winner, flipped=not gamestate.white_turn and not gamestate.game_over)
        
        
        rotated = pygame.transform.rotate(screen, 180)
        if not gamestate.white_turn and not ai and not gamestate.game_over: # rotate the screen if its blacks turn (some elements are unaffected)
            screen.blit(rotated)

        if ai:
            screen.blit(ai_surf, ai_rect)
        screen.blit(exit_surf, exit_rect)
        pygame.display.flip() # updates the whole display

    pygame.display.quit()
    return  

if __name__ == "__main__":
    try:
        main(ai=ai_glob)
    except pygame.error as e:
        if str(e) != "video system not initialized":
            print(e)

