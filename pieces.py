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
# [ ] Implement King class

from typing import TypeAlias
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chess import GameState # only when the interpreter is type checking, not at runtime

coordinate: TypeAlias = tuple[int, int]

# Right now, every piece moves like a pawn, but it works

def move_helper(board, row, col, directions, colour, max_distance=8) -> list[coordinate]:
    moves: list[coordinate] = []
    for drow, dcol in directions:
        trow, tcol = row + drow, col + dcol
        distance = 0
        while 0 <= trow < 8 and 0 <= tcol < 8 and distance < max_distance:
            target: Piece | None = board[trow][tcol]

            if target is None:
                moves.append((trow, tcol))
            elif target.colour != colour:
                moves.append((trow, tcol))
                break
            else:
                break

            trow += drow
            tcol += dcol
            distance += 1
    return moves

class Piece:
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
        raise NotImplementedError("Sub-class of piece unspecified: Piece is the parent class, and so there is no movement options defined")

    def image_key(self):
        return self.colour + self.name.lower()
    
class Pawn(Piece):
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

        return moves

class Knight(Piece):
    def get_legal_moves(self, board, row, col, gamestate):
        moves: list[coordinate] = []
        offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for dr, dc in offsets:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target: Piece | None = board[r][c]
                if target is None or target.colour != self.colour:
                    moves.append((r, c))
        return moves
    
# the rest of the pieces require no specialized behavior for base movement
class Bishop(Piece):
    def get_legal_moves(self, board, row, col, gamestate):
        directions = [(1,1), (-1,1), (-1,-1), (1,-1)]
        return move_helper(board, row, col, directions, self.colour)
    
class Rook(Piece):
    def get_legal_moves(self, board, row, col, gamestate):
        directions = [(1,0), (-1,0), (0, 1), (0,-1)]
        return move_helper(board, row, col, directions, self.colour)
    
class Queen(Piece):
    def get_legal_moves(self, board, row, col, gamestate):
        directions = [(1,0), (-1,0), (0, 1), (0,-1), (1,1), (-1,1), (-1,-1), (1,-1)]
        return move_helper(board, row, col, directions, self.colour)


class King(Piece):  
    def get_legal_moves(self, board, row, col, gamestate):
        from chess import king_in_check, square_is_attacked

        directions = [(1,0), (-1,0), (0, 1), (0,-1), (1,1), (-1,1), (-1,-1), (1,-1)]
        moves: list[coordinate] = []

        enemy = "w" if self.colour == "b" else "b"

        # Queenside castling
        if not self.has_moved and not king_in_check(gamestate, self.colour):
            rook_spot = board[row][0]
            if (rook_spot is not None and isinstance(rook_spot, Rook) and
                rook_spot.colour == self.colour and not rook_spot.has_moved and
                board[row][1] is None and board[row][2] is None and board[row][3] is None):

                if (not square_is_attacked((row, col-1),enemy,gamestate=gamestate) and 
                    not square_is_attacked((row, col-2),enemy,gamestate=gamestate)):
                    moves.append((row, 2))

        # Kingside castling
        if not self.has_moved and not king_in_check(gamestate, self.colour):
            rook_spot = board[row][7]
            if (rook_spot is not None and isinstance(rook_spot, Rook) and
                rook_spot.colour == self.colour and not rook_spot.has_moved and
                board[row][5] is None and board[row][6] is None):

                if (not square_is_attacked((row, col+1),enemy,gamestate=gamestate) and 
                    not square_is_attacked((row, col+2),enemy,gamestate=gamestate)):
                    moves.append((row, 6))

        # Normal king moves
        moves += move_helper(board, row, col, directions, self.colour, max_distance=1)

        return moves
        
if __name__ == '__main__':
    # --- ai generated code ---
    # when this module is executed as a script, delegate to the
    # main chess program instead of trying to import the pieces again.
    # we use subprocess to avoid creating a circular import: chess.py
    # already imports this module at the top level.
    import subprocess, sys, os

    # figure out the path to the chess script relative to this file
    script_dir = os.path.dirname(__file__)
    chess_path = os.path.join(script_dir, 'chess.py')

    # run the chess program with the same interpreter
    subprocess.run([sys.executable, chess_path])
    