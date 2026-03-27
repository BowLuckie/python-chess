# Pieces.py 
# Bowie Luckie
#
# This is a library that contains all the piece logic
#
# @TODO
# Piece Logic
# [/] Implement Knight class
# [/] Implement Bishop class
# [/] Implement Rook class
# [/] Implement Queen class
# [/] Implement King class

from typing import TypeAlias
from typing import TYPE_CHECKING
from pygame import error

if TYPE_CHECKING:
    from chess import GameState # only when the interpreter is type checking, not at runtime

coordinate: TypeAlias = tuple[int, int]

# Right now, every piece moves like a pawn, but it works

def move_helper(board, row, col, directions, colour, max_distance=8, capture=True, jump=False, self_captures=False) -> list[tuple[int, int]]:
    """
    Return a list of valid target squares from a given position based on movement rules.

    Iterates over the provided directions and collects reachable coordinates,
    respecting board bounds, maximum distance, and interaction rules:
    - empty squares are always valid
    - enemy pieces can be captured if `capture` is True
    - friendly pieces can be included if `self_captures` is True
    - movement can continue past pieces if `jump` is True

    Returns unique (row, col) tuples.
    """
    moves: list[tuple[int, int]] = []

    for drow, dcol in directions:
        trow, tcol = row + drow, col + dcol
        distance = 0

        while 0 <= trow < 8 and 0 <= tcol < 8 and distance < max_distance:
            target = board[trow][tcol]

            if target is None:
                moves.append((trow, tcol))
            elif self_captures and target is not None:
                moves.append((trow, tcol))
                if not jump:
                    break
            elif capture and target.colour != colour:
                moves.append((trow, tcol))
                if not jump:
                    break
            else:
                if not jump:
                    break

            trow += drow
            tcol += dcol
            distance += 1

    return list(set(moves))


class Piece:
    """
    The base class that all other pieces work off of. 
    each subclass inherints the `color`, `name` and `has_moved` variables and the `get_legal_moves()` and `image_key()` functions
    """
    def __init__(self, colour: str, name: str, has_moved: bool=False):
        
        self.colour = colour
        self.name = name
        self.has_moved = has_moved

    def get_legal_moves(self, board, row, col, gamestate):
        """
        Return all legal destination squares for the piece from a given position.

        Evaluates valid forward movement, optional extended movement from the
        initial position, and diagonal captures against opposing pieces.
        Moves are constrained by board boundaries and occupied squares.

        Args:
            board: 2D board structure containing piece objects or None.
            row (int): Current row of the piece.
            col (int): Current column of the piece.

        Returns:
            list[coordinate]: List of valid (row, col) squares the piece can move to.
        """

        # if get_legal_moves is called on the Pieces parent class, raise this error
        raise NotImplementedError("Sub-class of piece unspecified: Piece is the parent class, and so there is no movement options defined")

    def image_key(self) -> str:
        """
        returns the colour and name name of a peice as a two character string.

        for example:
        
        (White Bishop).image_key() -> "wb"
        """
        return self.colour.lower() + self.name.lower()
    
class Pawn(Piece):
    """
    moves one square forward. can only attack on its two forward diagonals. if it has not move it can move forward 2 squares as well as 1
    if it gets to the end you can chose to promote it to any piece of higher value except the king
    """
    def get_legal_moves(self, board, row: int, col: int, gamestate):
        moves: list[coordinate] = []
        direction = -1 if self.colour == "w" else 1

        if 0 <= row + direction < 8 and board[row + direction][col] is None:
            moves.append((row + direction, col))

        starting_row = 6 if self.colour == "w" else 1
        if row == starting_row:
            if board[row + direction][col] is None and board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))

        for dc in [-1, 1]:
            c = col + dc
            if 0 <= c < 8 and 0 <= row + direction < 8:
                target = board[row + direction][c]
                if target is not None and target.colour != self.colour: # if piece is of the opposite colour, then you can move there (capture)
                    moves.append((row + direction, c))

        for dc in [-1, 1]:
            c = col + dc
            if 0 <= c < 8:
                if (row, c) == gamestate.last_double_pawn:
                    moves.append((row + direction, c))

        return list(set(moves))

class Knight(Piece):
    """
    Jumps in the direction of one of its deltas, skipping over any pieces in its path. it deltas are defined as 

    ```python
    deltas = [
        (-2, -1), (-2, 1), (-1, -2), (-1, 2),
        (1, -2), (1, 2), (2, -1), (2, 1)
    ]
    ```

    this means the night can move 2 squares in any direction and then one square perpendicular to its ending point
    """
    def get_legal_moves(self, board, row, col, gamestate):
        deltas = [
        (-2, -1), (-2, 1), (-1, -2), (-1, 2),
        (1, -2), (1, 2), (2, -1), (2, 1)
    ]
        moves: list[coordinate] = []

        for dr, dc in deltas:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target: Piece | None = board[r][c]
                if target is None or target.colour != board[row][col].colour:
                    moves.append((r, c))
        return list(set(moves))

    
# the rest of the pieces require no specialized behavior for base movement
class Bishop(Piece):
    """
    Can move infinitley in one direction, as long as it is diagonal to the bishops origin.
    """
    def get_legal_moves(self, board, row, col, gamestate):
        directions = [(1,1), (-1,1), (-1,-1), (1,-1)]
        return move_helper(board, row, col, directions, self.colour)
    
class Rook(Piece):
    """
    Can move infinitley in one direction, as long as it is directly across or directly up from the rooks origin.
    """
    def get_legal_moves(self, board, row, col, gamestate):
        directions = [(1,0), (-1,0), (0, 1), (0,-1)]
        return move_helper(board, row, col, directions, self.colour)
    
class Queen(Piece):
    """
    can move infinitley in any 1 direction from its origin
    """
    def get_legal_moves(self, board, row, col, gamestate):
        directions = [(1,0), (-1,0), (0, 1), (0,-1), (1,1), (-1,1), (-1,-1), (1,-1)]
        return move_helper(board, row, col, directions, self.colour, max_distance=8)


class King(Piece):
    """
    can only move to one of the 8 adjacent squares. can also move squares horizontally on its starting rank if there is a rook on the end of that rank
    and both pieces havent moved. If evil mode is active, it transforms into a dictator which functions the exact same except it can take any peiece, regardless of colour
    """
    def get_legal_moves(self, board, row, col, gamestate):
        from chess import king_in_check, square_is_attacked

        directions = [(1,0), (-1,0), (0, 1), (0,-1), (1,1), (-1,1), (-1,-1), (1,-1)]
        moves: list[coordinate] = []

        enemy = "w" if self.colour == "b" else "b"

        # Queenside castling
        if not self.has_moved and not king_in_check(gamestate, self.colour):
            rook_spot = board[row][0]
            if (rook_spot is not None and isinstance(rook_spot, (Rook, Elephant)) and
                rook_spot.colour == self.colour and not rook_spot.has_moved and
                board[row][1] is None and board[row][2] is None and board[row][3] is None):

                if (not square_is_attacked((row, col-1),enemy,gamestate=gamestate) and 
                    not square_is_attacked((row, col-2),enemy,gamestate=gamestate)):
                    moves.append((row, 2))

        # Kingside castling
        if not self.has_moved and not king_in_check(gamestate, self.colour):
            rook_spot = board[row][7]
            if (rook_spot is not None and isinstance(rook_spot, (Rook, Elephant)) and
                rook_spot.colour == self.colour and not rook_spot.has_moved and
                board[row][5] is None and board[row][6] is None):

                if (not square_is_attacked((row, col+1),enemy,gamestate=gamestate) and 
                    not square_is_attacked((row, col+2),enemy,gamestate=gamestate)):
                    moves.append((row, 6))

        # Normal king moves
        print(gamestate.evil_mode)
        moves += move_helper(board, row, col, directions, self.colour, max_distance=1, self_captures=gamestate.evil_mode)

        return list(set(moves))
    
class Soldier(Piece):
    """moves like a pawn but has no capture restrictions"""
    def get_legal_moves(self, board, row, col, gamestate):
        d = -1 if self.colour == "w" else 1
        directions = [(d,-1), (d,0), (d,1)]
        if (row == 6 and self.colour == "w") or (row == 1 and self.colour == "b"):
            moves = move_helper(board, row, col, [(d,0)], self.colour, max_distance=2)
            moves += move_helper(board, row, col, directions, self.colour, max_distance=1)
            moves = list(set(moves))
        else:
            moves = move_helper(board, row, col, directions, self.colour, max_distance=1)

        return list(set(moves))
        
class Elephant(Piece):
    """moves like a rook and a king"""
    def get_legal_moves(self, board, row, col, gamestate):
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
        king_directions = [(1,0), (-1,0), (0, 1), (0,-1), (1,1), (-1,1), (-1,-1), (1,-1)]
        moves: list[tuple[int, int]] = []

        moves += move_helper(board, row, col, directions, self.colour)
        moves += move_helper(board, row, col, king_directions, self.colour, max_distance=1)

        return list(set(moves))
    
class Dog(Piece):
    """moves like a rook but jumps over every second square. it can also move one square diagonal ro its origin"""
    def get_legal_moves(self, board, row, col, gamestate):
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
        diagonal_deltas = [(1,1), (-1,1), (-1,-1), (1,-1)]
        moves: list[tuple[int, int]] = []

        for drow, dcol in directions:
            trow, tcol = row + drow, col + dcol
            distance = 0
            while 0 <= trow < 8 and 0 <= tcol < 8 and distance < 4:
                target = board[trow][tcol]

                # Only add every second square
                if distance % 2 == 1:
                    if target is None or target.colour != self.colour:
                        moves.append((trow, tcol))
                    else:
                        break  # can't land on own piece

                # Always jump over intermediate squares
                trow += drow
                tcol += dcol
                distance += 1

        moves += move_helper(board, row, col, directions=diagonal_deltas, colour=self.colour, max_distance=1)
        return moves
    
class Vampire(Piece):
    """moves like a queen and a knight combined"""
    def get_legal_moves(self, board, row, col, gamestate):
        moves = []

        # Queen-like sliding directions
        directions = [
            (1,0), (-1,0), (0,1), (0,-1),
            (1,1), (-1,1), (-1,-1), (1,-1)
        ]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board[r][c]

                if target is None:
                    moves.append((r, c))  # empty square → legal
                else:
                    if target.colour != self.colour:
                        moves.append((r, c))  # capture enemy
                    break  # stop sliding after any piece

                r += dr
                c += dc

        knight_deltas = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for dr, dc in knight_deltas:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = board[r][c]
                if target is None or target.colour != self.colour:
                    moves.append((r, c))

        return list(set(moves))
    
class Planet(Piece):
    """moves like a horse but jumps directly diagonally a max of 2 squares"""
    def get_legal_moves(self, board, row, col, gamestate):
        moves: list[tuple] = []
        # Diagonal knight jumps (2 squares diagonally)
        jumps = [(2,2), (2,-2), (-2,2), (-2,-2), (1,1), (1,-1), (-1,1), (-1,-1)]
        for dr, dc in jumps:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target: Piece = board[r][c]
                if target is None or target.colour != self.colour:
                    moves.append((r, c))

        return list(set(moves))

if __name__ == "__main__":
    try:
        import chess
        chess.main()
    except error as e:
        if str(e) != "video system not initialized" or str(e) != "Surface is not initialized":
            print(e)
    