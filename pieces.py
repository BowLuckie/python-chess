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

def move_helper(board, row, col, directions, color, max_distance=8):
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
    def get_legal_moves(self, board, row, col):
        directions = [(1,0), (-1,0), (0, 1), (0,-1), (1,1), (-1,1), (-1,-1), (1,-1)]
        # max_distance=1 ensures only single-square moves
        return move_helper(board, row, col, directions, self.color, max_distance=1)