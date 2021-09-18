from typing import List, Tuple, Dict
from board import Board, Move, Position

import numpy

def generate_moves(board : Board, player_sign : int):
    if player_sign not in [1, -1]:
        raise Exception("Player sign must be 1 or -1")

    moves : List[Move] = []

    # Return a list (100x4) of moves for the given board state and ply
    for x in range(8):
        for y in range(8):
            src = Position(x, y)
            signed_piece = board[src]

            if signed_piece * player_sign < 0:
                continue

            piece = abs(signed_piece)
            if piece == 1:
                dst = Position(x, y + player_sign)
                if board.can_move_space(dst):
                    moves.append(Move(src, dst))

                    dst = Position(x, y + 2 * player_sign)
                    if y == player_sign or (y - 7) == player_sign and can_move_space(dst):
                        moves.append(Move(src, dst))

                dst = Position(x + 1, y + player_sign)
                if board.can_capture_space(dst, player_sign):
                    moves.append(Move(src, dst))

                dst = Position(x - 1, y + player_sign)
                if board.can_capture_space(dst, player_sign):
                    moves.append(Move(src, dst))
    
    return moves

values : Dict[int, float] = {
    0 : 0.0,
    1 : 100.0,
    2 : 300.0,
    3 : 320.0,
    4 : 500.0,
    5 : 900.0,
    6 : 1000000.0
}

pawn_position_bonus = numpy.array([
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 100, 100, 0, 0, 0],
    [0, 0, 100, 300, 300, 100, 0, 0],
    [0, 0, 100, 300, 300, 100, 0, 0],
    [0, 0, 0, 100, 100, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
])

def evaluate_position(board):
    # Return score of current board
    total_value = 0.0

    for x in range(8):
        for y in range(8):
            signed_piece = board[Position(x, y)]
            sign = numpy.sign(signed_piece)
            piece = abs(signed_piece)
            value = abs(values[piece])
            if piece == 1:
                value += pawn_position_bonus[y, x]
            total_value += sign * value
    
    return total_value

class AIGame:
    board : Board
    dmax : int = 3

    def __init__(self, board_ : Board):
        self.board = board_

    def update_position(self, move : Move, clist : List[Move], ply : int):
        # Update the board with a new move
        previous_piece = self.board.move(move.src, move.dst)
        clist.append((move, previous_piece))
        ply += 1

    def restore_position(self, clist : List[Move], ply : int):
        # Pop a board change off the clist to return the board to a previous state
        move, previous_piece = clist.pop()
        ply -= 1
        self.board.move(move.dst, move.src, previous_piece)

    def pc_update(self, mptr, moves, scores, pc, ply, player_sign):
        # Update the principle continuation for ply - 1
        if ply == 0:
            return

        # Odd plies minimize, even plies maximize
        if (ply - 1) % 2 == 0:
            do_update = scores[ply] > scores[ply - 1]
        else:
            do_update = scores[ply] < scores[ply - 1]

        # Invert the logic for other player
        if player_sign == -1:
            do_update = not do_update

        if do_update:
            scores[ply - 1] = scores[ply]
            if ply < len(pc):
                current_pc = pc[ply]
            else:
                current_pc = []
            pc[ply - 1] = [moves[ply - 1][mptr[ply - 1]]] + current_pc

    def pick_next_move(self, active_player_sign : int):
        moves : List[List[Move]] = self.dmax * [[]]
        mptr : List[int] = self.dmax * [0]
        scores : List[float] = (self.dmax + 1) * [0]
        pc : List[List[Move]] = self.dmax * [[]]
        clist : List[Tuple[Move, int]] = []
        ply : int = 0
        player_sign : int = 1

        moves[ply] = generate_moves(self.board, player_sign)
        mptr[ply] = 0
        scores[ply] = player_sign * -float('inf')

        while True:
            if mptr[ply] == len(moves[ply]):
                self.pc_update(mptr, moves, scores, pc, ply, player_sign)

                if ply == 0:
                    break

                self.restore_position(clist, ply)
                mptr[ply] += 1
            else:
                next_move = moves[ply][mptr[ply]]
                self.update_position(next_move, clist, ply)
                if ply < self.dmax:
                    # If not at last layer, advance layer
                    moves[ply] = generate_moves(self.board, player_sign * (-1)**ply)
                    mptr[ply] = 0
                    scores[ply] = player_sign * (-1)**ply * -float('inf')
                elif ply == self.dmax:
                    # If at last layer, evaluate score
                    scores[ply] = evaluate_position(self.board)
                    self.pc_update(mptr, moves, scores, pc, ply, player_sign)
                    self.restore_position(clist, ply)
                    mptr[ply] += 1
                else:
                    raise Exception("Unhandled state")

        return pc[0][0]