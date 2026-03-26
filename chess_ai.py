from copy import deepcopy
import pygame
import pieces

coordinate = pieces.coordinate

# the ai's internal motivations and punishment scalars
ACTIVITY_BONUS = 0.1
CENTER_BONUS = 0.3
TRADE_SCALE = 0.8
DANGER_PENALTY = 1.1
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
    """
    calculates the most favourable move, preforms that move in this position and returns its score
    """
    # making a proper ai was never my intention, but the infastructure is there and there is some basic logic behind it although right now it not very strong and tends to really like certian openings
    global king_move_penalty, edge_pawn_penalty, variation

    from random import choice, random
    from copy import deepcopy
    from chess import (
        PIECE_VALUES, insufficient_mat, king_in_check,
        move_piece, simulate_move, classes_options, move_counter
    )

    ai_legal_moves = []
    best_moves = []
    best_score = -float("inf")

    # Adjust dynamic parameters
    if move_counter > 20:
        king_move_penalty *= 0.2
        edge_pawn_penalty *= 0.1
        variation *= 5
    elif move_counter < 5:
        variation *= 3
    else:
        variation /= 3

    board: list[list[pieces.Piece | None]] = gamestate.board

    # Iterate over all black pieces
    for row in range(8):
        for col in range(8):
            origin_piece: pieces.Piece | None = board[row][col]
            if origin_piece is None or origin_piece.colour != "b":
                continue

            legal_move = origin_piece.get_legal_moves(board, row, col, gamestate)

            for target_square in legal_move:
                move = ((row, col), target_square)

                if not simulate_move(gamestate, move[0], move[1]):
                    continue

                # simulate the move
                temp_board = deepcopy(board)
                temp_board[target_square[0]][target_square[1]] = origin_piece
                temp_board[row][col] = None

                ai_legal_moves.append(move)

                target_piece: pieces.Piece = board[target_square[0]][target_square[1]]
                score = 0.0

                # Capture scoring
                if target_piece and target_piece.colour != origin_piece.colour:
                    score += PIECE_VALUES.get(type(target_piece), 0) * TRADE_SCALE

                # Activity
                score += ACTIVITY_BONUS

                # center control 
                if not isinstance(origin_piece, (pieces.Pawn, pieces.Soldier, pieces.Queen, pieces.Vampire)):
                    score += PROGRESSION_TABLE[row][col]
                elif isinstance(origin_piece, pieces.Queen):
                    score -= PROGRESSION_TABLE[row][col] * 0.5

                # edge pawn penalty
                if col in (0, 1, 2, 5, 6, 7):
                    score -= edge_pawn_penalty

                # try to avoid getting the queen out to early
                if isinstance(origin_piece, (pieces.Queen, pieces.Vampire)) and move_counter < 12:
                    score -= 8

                # king movement penalty
                if isinstance(origin_piece, pieces.King):
                    score -= king_move_penalty

                # pawn double-move penalty
                if isinstance(origin_piece, (pieces.Pawn, pieces.Soldier)) and row == 2:
                    score -= DOUBLE_MOVE_PAWN_BONUS

                # danger penalty
                if ai_square_is_attacked(temp_board, target_square, "w"):
                    score -= PIECE_VALUES.get(type(origin_piece), 0) * DANGER_PENALTY

                # Random variation
                score += random() * variation

                # Track best moves
                if score > best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)

    # No legal moves means game over
    if not ai_legal_moves:
        gamestate.game_over = True

        if insufficient_mat(board=board):
            gamestate.winner = "d"
            gamestate.draw_type = "insufficient material"
            return

        if king_in_check(gamestate=gamestate, colour="b"):
            gamestate.winner = "w"
        else:
            gamestate.winner = "d"
            gamestate.draw_type = "stalemate"

        return None

    # Choose best move (or fallback to any legal move)
    chosen_move = choice(best_moves if best_moves else ai_legal_moves)
    move_piece(gamestate, chosen_move[0], chosen_move[1], ai_move=True, double=double)

    # Promotion
    end_row = chosen_move[1][0]
    moved_piece = gamestate.board[end_row][chosen_move[1][1]]

    if isinstance(moved_piece, (pieces.Pawn, pieces.Soldier)) and end_row == 7:
        gamestate.promotion_active = False
        gamestate.promotion_square = None
        gamestate.promotion_color = None

        newp = choice(classes_options)
        gamestate.board[end_row][chosen_move[1][1]] = newp[0]("b", newp[1])

        if not double:
            gamestate.white_turn = False

    return best_score


# these functions are diffrent from Piece.get_legal_moves() becuase legal moves are not nescasarily the attack map (eg, legal moves stop at own pieces)
def sliding_attacks(board, row, col, directions, colour):
    return pieces.move_helper(
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

def knight_attacks(row, col):
    deltas = [
        (-2,-1), (-2,1), (-1,-2), (-1,2),
        (1,-2), (1,2), (2,-1), (2,1)
    ]
    return [
        (row+dr, col+dc)
        for dr, dc in deltas
        if 0 <= row+dr < 8 and 0 <= col+dc < 8
    ]

def pawn_attacks(row, col, colour):
    direction = -1 if colour == "w" else 1
    attacks = []
    for dc in (-1, 1):
        r = row + direction
        c = col + dc
        if 0 <= r < 8 and 0 <= c < 8:
            attacks.append((r, c))
    return attacks

def king_attacks(row, col):
    deltas = [
        (1,0),(-1,0),(0,1),(0,-1),
        (1,1),(1,-1),(-1,1),(-1,-1)
    ]
    return [
        (row+dr, col+dc)
        for dr, dc in deltas
        if 0 <= row+dr < 8 and 0 <= col+dc < 8
    ]

def attack_map(piece, board, row, col):
    """
    returns a the squares that are under fire
    """
    from pieces import Pawn, Knight, Bishop, Rook, Queen, King

    if isinstance(piece, Pawn):
        return pawn_attacks(row, col, piece.colour)

    if isinstance(piece, Knight):
        return knight_attacks(row, col)

    if isinstance(piece, King):
        return king_attacks(row, col)

    if isinstance(piece, Rook):
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        return sliding_attacks(board, row, col, dirs, piece.colour)

    if isinstance(piece, Bishop):
        dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]
        return sliding_attacks(board, row, col, dirs, piece.colour)

    if isinstance(piece, Queen):
        dirs = [
            (1,0),(-1,0),(0,1),(0,-1),
            (1,1),(1,-1),(-1,1),(-1,-1)
        ]
        return sliding_attacks(board, row, col, dirs, piece.colour)

    return []

def ai_square_is_attacked(board, square, by_colour) -> bool:
    sr, sc = square

    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p is None or p.colour != by_colour:
                continue

            if square in attack_map(p, board, r, c):
                return True

    return False

if __name__ == "__main__":
    import chess
    try:
        chess.main()
    except pygame.error as e:  
        print(e)
