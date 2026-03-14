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

coordinate: TypeAlias = tuple[int, int]

# Right now, every piece moves like a pawn, but it works

def move_helper(board, row, col, directions, color, max_distance=8) -> list[coordinate]:
    moves: list[coordinate] = []
    for drow, dcol in directions:
        trow, tcol = row + drow, col + dcol
        distance = 0
        while 0 <= trow < 8 and 0 <= tcol < 8 and distance < max_distance:
            target: Piece | None = board[trow][tcol]

            if target is None:
                moves.append((trow, tcol))
            elif target.color != color:
                moves.append((trow, tcol))
                break
            else:
                break

            trow += drow
            tcol += dcol
            distance += 1
    return moves

class Piece:
    def __init__(self, color: str, name: str, has_moved: bool=False):
        self.color = color
        self.name = name
        self.has_moved = has_moved

    def get_legal_moves(self, board, row, col):
        return []

    def image_key(self):
        return self.color + self.name.lower()
    
    def get_attack_squares(self, board, row, col):
        # to be overriden by the subclasses
        return self.get_legal_moves(board, row, col) 

class Pawn(Piece):
    def get_legal_moves(self, board, row, col):
        moves: list[coordinate] = []
        direction = -1 if self.color == "w" else 1

        if 0 <= row + direction < 8 and board[row + direction][col] is None:
            moves.append((row + direction, col))

        starting_row = 6 if self.color == "w" else 1
        if row == starting_row:
            if board[row + direction][col] is None and board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))

        for dc in [-1, 1]:
            c = col + dc
            if 0 <= c < 8 and 0 <= row + direction < 8:
                target = board[row + direction][c]
                if target is not None and target.color != self.color:
                    moves.append((row + direction, c))

        return moves

class Knight(Piece):
    def get_legal_moves(self, board, row, col):
        moves: list[coordinate] = []
        offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for dr, dc in offsets:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target: Piece | None = board[r][c]
                if target is None or target.color != self.color:
                    moves.append((r, c))
        return moves
    
# the rest of the pieces require no specialized behavior for base movement
class Bishop(Piece):
    def get_legal_moves(self, board, row, col):
        directions = [(1,1), (-1,1), (-1,-1), (1,-1)]
        return move_helper(board, row, col, directions, self.color)
    
class Rook(Piece):
    def get_legal_moves(self, board, row, col):
        directions = [(1,0), (-1,0), (0, 1), (0,-1)]
        return move_helper(board, row, col, directions, self.color)
    
class Queen(Piece):
    def get_legal_moves(self, board, row, col):
        directions = [(1,0), (-1,0), (0, 1), (0,-1), (1,1), (-1,1), (-1,-1), (1,-1)]
        return move_helper(board, row, col, directions, self.color)
    
class King(Piece):
    castle = False
    def get_legal_moves(self, board, row, col):
        directions = [(1,0), (-1,0), (0, 1), (0,-1), (1,1), (-1,1), (-1,-1), (1,-1)]
        # max_distance=1 ensures only single-square moves
        moves: list[coordinate] = []
        if hasattr(board[row][0], "has_moved"):
            if not self.has_moved and not board[row][0].has_moved:
                # check left side
                rook_spot = board[row][0]
                if (
                    board[row][1] is None 
                    and board[row][2] is None 
                    and board[row][3] is None 
                    and isinstance(rook_spot, Rook)
                    and not rook_spot.has_moved
                ):
                    moves.append((row, 2))

                # check right side
                rook_spot = board[row][7]
                if (
                    board[row][6] is None 
                    and board[row][5] is None 
                    and isinstance(rook_spot, Rook) # ensure end square is rook...
                    and not rook_spot.has_moved # ...and has not moved
                ):
                    moves.append((row, 6))

        moves += move_helper(board, row, col, directions, self.color, max_distance=1) # concatenate move calculated from castling to moves made from move helper
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
    