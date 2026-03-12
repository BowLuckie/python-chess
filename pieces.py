# Pieces.py 
# Bowie Luckie
#
# This is a library that contains all the piece logic
#
# @TODO
# [ ] Implement Knight class
# [ ] Implement Bishop class
# [ ] Implement Rook class
# [ ] Implement Queen class
# [ ] Implement King class

from typing import TypeAlias

coordinate: TypeAlias = tuple[int, int]

# Right now, every piece moves like a pawn, but it works

class Piece:
    def __init__(self, color: str, name: str):
        self.color = color
        self.name = name

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
    # @TODO
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
    
class Bishop(Piece):
    # @TODO
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
    
class Rook(Piece):
    # @TODO
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
    
class Queen(Piece):
    # @TODO
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
    
class King(Piece):
    # @TODO
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