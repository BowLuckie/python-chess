from copy import deepcopy

import pygame
from pieces import King, move_helper, Pawn, Soldier, Piece
from typing import TypeAlias
import math
import random

coordinate: TypeAlias = tuple[int, int]

# constants; adjust to change the motivations of at ai

ACTIVITY_BONUS = 0.41
CENTER_BONUS = 0.3
TRADE_SCALE = 0.8
DANGER_PENALTY = 1.03
king_move_penalty = 6
variation = 0.4
edge_pawn_penalty = 5
DOUBLE_MOVE_PAWN_BONUS = 5

PROGRESSION_TABLE = [
    [-5,-4,-3,-3,-3,-3,-4,-5],
    [-4,-2, 0, 0, 0, 0,-2,-4],
    [-3, 0, 1, 1, 1, 1, 0,-3],
    [-3, 0, 1, 2, 2, 1, 0,-3],
    [-3, 0, 1, 2, 2, 1, 0,-3],
    [-3, 0, 1, 1, 1, 1, 0,-3],
    [-4,-2, 0, 0, 0, 0,-2,-4],
    [-5,-4,-3,-3,-3,-3,-4,-5]
]

def move_ai(gamestate, double: bool=False) -> float | None:
    global king_move_penalty, edge_pawn_penalty, variation
    from random import choice
    from chess import PIECE_VALUES, insufficient_mat, king_in_check, move_piece, simulate_move, classes_options, move_counter
    ai_legal_moves = []
    best_score = -float("inf")
    best_moves = []
    
    if move_counter > 20:
        king_move_penalty *= 0.2
        edge_pawn_penalty *= 0.1
        variation *= 5 

    if move_counter < 5:
        variation *= 3
    else:
        variation /= 3

    for row in range(8):
        for col in range(8):
            piece_to_move = gamestate.board[row][col]
            if piece_to_move is not None and piece_to_move.colour == "b":
                for target in piece_to_move.get_legal_moves(gamestate.board, row, col, gamestate):
                    move = ((row, col), target) # origin target

                    if simulate_move(gamestate, move[0], move[1]): # if the move is allowed
                        
                        temp_board = deepcopy(gamestate.board) # high cost function
                        temp_board[target[0]][target[1]] = piece_to_move
                        temp_board[row][col] = None

                        ai_legal_moves.append(move)

                        target_piece: Piece = gamestate.board[target[0]][target[1]]

                        # base score
                        score: float = 0

                        # capture scoring
                        if target_piece is not None and target_piece.colour != piece_to_move.colour:
                            score += PIECE_VALUES.get(type(target_piece), 0) * TRADE_SCALE

                        score += ACTIVITY_BONUS

                        # center control
                        if not isinstance(piece_to_move, (Pawn, Soldier)):
                            score += PROGRESSION_TABLE[row][col]

                        if col in (7,6,5,0,1,2):
                            score -= edge_pawn_penalty

                        if isinstance(piece_to_move, King):
                            score -= king_move_penalty

                        if isinstance(piece_to_move, (Pawn, Soldier)) and row == 2:
                            score -= DOUBLE_MOVE_PAWN_BONUS

                        if ai_square_is_attacked(temp_board, target, "w"):
                            score -= PIECE_VALUES.get(type(piece_to_move), 0) * DANGER_PENALTY

                        score += random.random() * variation # avoid deterministic play

                        if score > best_score:
                            best_score = score
                            best_moves = [move]
                        elif score == best_score:
                            best_moves.append(move)

    try:
        # pick best move if exists, otherwise random legal move
        ai_chosen_move = choice(best_moves if best_moves else ai_legal_moves)

        move_piece(gamestate, ai_chosen_move[0], ai_chosen_move[1], ai_move=True, double=double)

        ai_piece = gamestate.board[ai_chosen_move[1][0]][ai_chosen_move[1][1]]

        # promotion
        if (isinstance(ai_piece, Pawn) or isinstance(ai_piece, Soldier)) and ai_chosen_move[1][0] == 7:
            gamestate.promotion_active = False
            gamestate.promotion_square = None
            gamestate.promotion_color = None

            newp = choice(classes_options)
            gamestate.board[ai_chosen_move[1][0]][ai_chosen_move[1][1]] = newp[0]("b", newp[1])
            if not double:
                gamestate.white_turn = False # to be swapped later

    except IndexError:
        # no moves available
        gamestate.game_over = True
        if insufficient_mat(board=gamestate.board):
            gamestate.winner = "d"
            gamestate.draw_type = "insufficient material"
            return
        
        if king_in_check(gamestate=gamestate, colour="b"):
            gamestate.winner = "w"
        else:
            gamestate.winner = "d"
            gamestate.draw_type = "stalemate"
            print("ai_stalemate")

    return best_score

# these functions are diffrent from Piece.get_legal_moves() becuase legal moves are not nescasarily the attack map (eg, legal moves stop at own pieces)
def ai_sliding_attacks(board, row, col, directions, colour):
    return move_helper(
        board,
        row,
        col,
        directions,
        colour,
        max_distance=8,
        capture=True,
        jump=False,
        self_captures=True
    )

def ai_knight_attacks(row, col):
    deltas = [
        (-2,-1), (-2,1), (-1,-2), (-1,2),
        (1,-2), (1,2), (2,-1), (2,1)
    ]
    return [
        (row+dr, col+dc)
        for dr, dc in deltas
        if 0 <= row+dr < 8 and 0 <= col+dc < 8
    ]

def ai_pawn_attacks(row, col, colour):
    direction = -1 if colour == "w" else 1
    attacks = []
    for dc in (-1, 1):
        r = row + direction
        c = col + dc
        if 0 <= r < 8 and 0 <= c < 8:
            attacks.append((r, c))
    return attacks

def ai_king_attacks(row, col):
    deltas = [
        (1,0),(-1,0),(0,1),(0,-1),
        (1,1),(1,-1),(-1,1),(-1,-1)
    ]
    return [
        (row+dr, col+dc)
        for dr, dc in deltas
        if 0 <= row+dr < 8 and 0 <= col+dc < 8
    ]

def ai_attack_squares(piece, board, row, col):
    from pieces import Pawn, Knight, Bishop, Rook, Queen, King

    if isinstance(piece, Pawn):
        return ai_pawn_attacks(row, col, piece.colour)

    if isinstance(piece, Knight):
        return ai_knight_attacks(row, col)

    if isinstance(piece, King):
        return ai_king_attacks(row, col)

    if isinstance(piece, Rook):
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        return ai_sliding_attacks(board, row, col, dirs, piece.colour)

    if isinstance(piece, Bishop):
        dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]
        return ai_sliding_attacks(board, row, col, dirs, piece.colour)

    if isinstance(piece, Queen):
        dirs = [
            (1,0),(-1,0),(0,1),(0,-1),
            (1,1),(1,-1),(-1,1),(-1,-1)
        ]
        return ai_sliding_attacks(board, row, col, dirs, piece.colour)

    return []

def ai_square_is_attacked(board, square, by_colour):
    sr, sc = square

    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p is None or p.colour != by_colour:
                continue

            if square in ai_attack_squares(p, board, r, c):
                return True

    return False

if __name__ == "__main__":
    import chess
    try:
        chess.main()
    except pygame.error as e:  
        print(e)
