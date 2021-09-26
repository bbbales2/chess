from typing import List, Tuple
from board import Board, Move, Position, diagonal_directions, file_directions, knight_directions
import numpy

def find_attacking_moves(board: Board, pos: Position, player_sign: None):
    attacking_moves = []
    # Search for rooks/queens/kings
    for dir in file_directions:
        for dist in range(1, 8):
            src = pos + dist * dir

            if not board.is_valid_position(src):
                break
            
            if board.occupied(src):
                piece = abs(board[src])
                if piece == 4 or piece == 5 or piece == 6:
                    attacking_moves.append(Move(src, pos))
                break

    # Search for bishops/queens/kings
    for dir in diagonal_directions:
        for dist in range(1, 8):
            src = pos + dist * dir

            if not board.is_valid_position(src):
                break

            if board.occupied(src):
                piece = abs(board[src])
                if piece == 3 or piece == 5 or piece == 6:
                    attacking_moves.append(Move(src, pos))
                break
    
    # Search for horses
    for dir in knight_directions:
        src = pos + dir

        if not board.is_valid_position(src):
            continue

        if board.occupied(src):
            piece = abs(board[src])
            if piece == 2:
                attacking_moves.append(Move(src, pos))

    if player_sign is not None:
        attacking_moves = [
            move for move in attacking_moves if board[move.src] * player_sign > 0
        ]
    return attacking_moves

def generate_moves(board: Board, player_sign: int):
    if player_sign not in [1, -1]:
        raise ValueError("Player sign must be 1 or -1")

    moves: List[Move] = []

    # Return a list of moves for the given board state and player
    positions = board.find_piece_positions(player_sign)
    king_position = None
    for src in positions:
        signed_piece = board[src]

        if signed_piece * player_sign <= 0:
            continue

        piece = abs(signed_piece)
        if piece == 1:
            dst = Position(src.x, src.y + player_sign)
            if board.can_move_space(dst):
                moves.append(Move(src, dst))

                dst = Position(src.x, src.y + 2 * player_sign)
                if src.y == player_sign or (src.y - 7) == player_sign and board.can_move_space(dst):
                    moves.append(Move(src, dst))

            dst = Position(src.x + 1, src.y + player_sign)
            if board.can_capture_space(dst, player_sign):
                moves.append(Move(src, dst))

            dst = Position(src.x - 1, src.y + player_sign)
            if board.can_capture_space(dst, player_sign):
                moves.append(Move(src, dst))
        elif piece == 2:
            for dir in knight_directions:
                dst = src + dir

                if board.can_move_space(dst):
                    moves.append(Move(src, dst))
                elif board.can_capture_space(dst, player_sign):
                    moves.append(Move(src, dst))
        elif piece == 3 or piece == 5:
            for dir in diagonal_directions:
                for dist in range(1, 8):
                    dst = src + dist * dir

                    if board.can_move_space(dst):
                        moves.append(Move(src, dst))
                    elif board.can_capture_space(dst, player_sign):
                        moves.append(Move(src, dst))
                        break
                    else:
                        break
        
        if piece == 4 or piece == 5:
            for dir in file_directions:
                for dist in range(1, 8):
                    dst = src + dist * dir

                    if board.can_move_space(dst):
                        moves.append(Move(src, dst))
                    elif board.can_capture_space(dst, player_sign):
                        moves.append(Move(src, dst))
                        break
                    else:
                        break
        elif piece == 6:
            king_position = src
            for dir in diagonal_directions + file_directions:
                dst = src + dir
                if board.can_move_space(dst) or board.can_capture_space(dst, player_sign):
                    replacement_piece = board.move(src, dst)
                    attacking_moves = find_attacking_moves(board, dst, -1 * player_sign)
                    board.move(dst, src, replacement_piece)
                    if len(attacking_moves) == 0:
                        moves.append(Move(src, dst))
    
    if king_position is None:
        return moves

    valid_moves = []
    for move in moves:
        if move.src == king_position:
            valid_moves.append(move)
        else:
            replacement_piece = board.move(move.src, move.dst)
            attacking_moves = find_attacking_moves(board, king_position, -1 * player_sign)
            board.move(move.dst, move.src, replacement_piece)
            if len(attacking_moves) == 0:
                valid_moves.append(move)
    return valid_moves


values = numpy.array([0.0, 100.0, 300.0, 320.0, 500.0, 900.0, 200000.0])

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

    for sign in [1, -1]:
        # Create a board where the pieces of the side we're considering are positive
        positive_perspective_board = board.board * sign
        pieces = positive_perspective_board[positive_perspective_board > 0]
        total_value += sign * (
            numpy.sum(values[pieces]) +
            numpy.sum(pawn_position_bonus * (positive_perspective_board == 1))
        )
    
    return total_value


class AIGame:
    board: Board
    dmax: int = 3

    def __init__(self, board_: Board):
        self.board = board_

    def update_position(self, move: Move, clist: List[Move], ply: int):
        # Update the board with a new move
        previous_piece = self.board.move(move.src, move.dst)
        clist.append((move, previous_piece))
        return ply + 1

    def restore_position(self, clist : List[Move], ply : int):
        # Pop a board change off the clist to return the board to a previous state
        move, previous_piece = clist.pop()
        self.board.move(move.dst, move.src, previous_piece)
        return ply - 1

    def pc_update(self, mptr, moves, scores, pc, ply, player_sign):
        # Update the principle continuation for ply - 1
        if ply == 0:
            return False

        if player_sign == 1:
            # Odd plies minimize, even plies maximize
            if (ply - 1) % 2 == 0:
                do_update = scores[ply] > scores[ply - 1]
            else:
                do_update = scores[ply] < scores[ply - 1]
        else:
            # Invert the logic for other player
            if (ply - 1) % 2 == 0:
                do_update = scores[ply] < scores[ply - 1]
            else:
                do_update = scores[ply] > scores[ply - 1]
        
        if ply > 1:
            if player_sign == 1:
                if (ply - 1) % 2 == 0:
                    do_prune = scores[ply] > scores[ply - 2]
                else:
                    do_prune = scores[ply] < scores[ply - 2]
            else:
                if (ply - 1) % 2 == 0:
                    do_prune = scores[ply] < scores[ply - 2]
                else:
                    do_prune = scores[ply] > scores[ply - 2]
        else:
            do_prune = False

        if do_update:
            scores[ply - 1] = scores[ply]
            if ply < len(pc):
                current_pc = pc[ply]
            else:
                current_pc = []
            pc[ply - 1] = [moves[ply - 1][mptr[ply - 1]]] + current_pc

        return do_prune

    def pick_next_move(self, active_player_sign : int):
        moves: List[List[Move]] = self.dmax * [[]]
        mptr: List[int] = self.dmax * [0]
        scores: List[float] = (self.dmax + 1) * [0]
        pc: List[List[Move]] = self.dmax * [[]]
        clist: List[Tuple[Move, int]] = []
        ply: int = 0
        player_sign: int = active_player_sign

        moves[ply] = generate_moves(self.board, player_sign)
        mptr[ply] = 0
        scores[ply] = player_sign * -float('inf')

        while True:
            if mptr[ply] == len(moves[ply]):
                if numpy.isinf(scores[ply]):
                    b = 1
                prune = self.pc_update(mptr, moves, scores, pc, ply, player_sign)

                if ply == 0:
                    break

                ply = self.restore_position(clist, ply)
                if prune:
                    mptr[ply] = len(moves[ply]) # skip the rest of the moves
                else:
                    mptr[ply] += 1
            else:
                next_move = moves[ply][mptr[ply]]
                if next_move.dst == Position(2, 7):
                    a = 1
                ply = self.update_position(next_move, clist, ply)
                if ply < self.dmax:
                    # If not at last layer, advance layer
                    moves[ply] = generate_moves(self.board, player_sign * (-1)**ply)
                    mptr[ply] = 0
                    if len(moves[ply]) == 0:
                        scores[ply] = evaluate_position(self.board)
                    elif ply > 1:
                        scores[ply] = scores[ply - 2]
                    else:
                        scores[ply] = player_sign * (-1)**ply * -float('inf')
                elif ply == self.dmax:
                    # If at last layer, evaluate score
                    scores[ply] = evaluate_position(self.board)
                    if numpy.isinf(scores[ply]):
                        b = 1
                    prune = self.pc_update(mptr, moves, scores, pc, ply, player_sign)
                    ply = self.restore_position(clist, ply)
                    if prune:
                        mptr[ply] = len(moves[ply]) # skip the rest of the moves
                    else:
                        mptr[ply] += 1
                else:
                    raise Exception("Unhandled state")

        if len(pc[0]) > 0:
            return pc[0][0]
        else:
            return None
