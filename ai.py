from typing import List, Tuple, Deque
from collections import deque
from board import Board, PromotionMove, Move, Unmove, Position, diagonal_directions, file_directions, knight_directions
import numpy

def find_any_attacking_move(board: Board, pos: Position, player_sign):
    # Search for pawns
    for side in [-1, 1]:
        src = pos + Position(side, -player_sign)

        if not board.is_valid_position(src):
            continue

        if board[src] == player_sign * 1:
            return Move(src, pos)

    # Search for rooks/queens
    for dir in file_directions:
        for dist in range(1, 8):
            src = pos + dist * dir

            if not board.is_valid_position(src):
                break
            
            if board.occupied(src):
                piece = player_sign * board[src]
                if piece in [4, 5]:
                    return Move(src, pos)
                break

    # Search for bishops/queens
    for dir in diagonal_directions:
        for dist in range(1, 8):
            src = pos + dist * dir

            if not board.is_valid_position(src):
                break

            if board.occupied(src):
                piece = player_sign * board[src]
                if piece in [3, 5]:
                    return Move(src, pos)
                break
    
    # Search for horses
    for dir in knight_directions:
        src = pos + dir

        if not board.is_valid_position(src):
            continue

        if player_sign * board[src] == 2:
            return Move(src, pos)

    # Search for kings
    for dir in file_directions + diagonal_directions:
        src = pos + dir

        if not board.is_valid_position(src):
            continue
            
        if board[src] == player_sign * 6:
            return Move(src, pos)
    
    return None

def find_all_possible_attacks(board: Board, pos: Position, player_sign):
    attacking_moves = []
    # Search for pawns
    for side in [-1, 1]:
        src = pos + Position(side, -player_sign)

        if not board.is_valid_position(src):
            continue

        if board[src] == player_sign * 1:
            attacking_moves.append(Move(src, pos))

    # Search for rooks/queens
    for dir in file_directions:
        for dist in range(1, 8):
            src = pos + dist * dir

            if not board.is_valid_position(src):
                break
            
            if board.occupied(src):
                piece = board[src]
                if player_sign == numpy.sign(piece):
                    if abs(piece) in [4, 5]:
                        attacking_moves.append(Move(src, pos))
                    else:
                        break

    # Search for bishops/queens
    for dir in diagonal_directions:
        for dist in range(1, 8):
            src = pos + dist * dir

            if not board.is_valid_position(src):
                break

            if board.occupied(src):
                piece = player_sign * board[src]
                if player_sign == numpy.sign(piece):
                    if abs(piece) in [3, 5]:
                        attacking_moves.append(Move(src, pos))
                    else:
                        break
    
    # Search for horses
    for dir in knight_directions:
        src = pos + dir

        if not board.is_valid_position(src):
            continue

        if board.occupied(src):
            piece = board[src]
            if player_sign == numpy.sign(piece) and abs(piece) == 2:
                attacking_moves.append(Move(src, pos))

    # Search for kings
    for dir in file_directions + diagonal_directions:
        src = pos + dir

        if not board.is_valid_position(src):
            continue
        
        if board[src] == player_sign * 6:
            attacking_moves.append(Move(src, pos))

    return attacking_moves

def castling_possible(board, king_position, rook_position, player_sign):
    dir = Position(-1 if king_position.x > rook_position.x else 1, 0)
    for dist in range(1, abs(rook_position.x - king_position.x)):
        middle_position = king_position + dist * dir
        if board[middle_position] != 0:
            return False

        if dist < 3:
            if find_any_attacking_move(board, middle_position, -1 * player_sign) is not None:
                return False

    if not board.has_moved(king_position) and not board.has_moved(rook_position):
        return True
    else:
        return False

def promote_move_if_possible(moves, src, dst, player_sign):
    if dst.y in [0, 7]:
        moves.append(PromotionMove(src, dst, player_sign * 2))
        moves.append(PromotionMove(src, dst, player_sign * 5))
    else:
        moves.append(Move(src, dst))

def generate_moves(board: Board, player_sign: int, killer_moves: deque):
    # Return a list of moves for the given board state and player
    home_row = 0 if player_sign == 1 else 7

    if player_sign not in [1, -1]:
        raise ValueError("Player sign must be 1 or -1")

    moves: List[Move] = []

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
                promote_move_if_possible(moves, src, dst, player_sign)

                dst = Position(src.x, src.y + 2 * player_sign)
                if src.y == home_row + player_sign and board.can_move_space(dst):
                    moves.append(Move(src, dst))

            for side in [-1, 1]:
                dst = Position(src.x + side, src.y + player_sign)
                if (
                    board.can_capture_space(dst, player_sign) or
                    board.en_passant_pos == Position(src.x + side, src.y)
                ):
                    promote_move_if_possible(moves, src, dst, player_sign)

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
                    move = Move(src, dst)
                    unmove = board.move(move)
                    if find_any_attacking_move(board, dst, -1 * player_sign) is None:
                        moves.append(move)
                    board.unmove(unmove)

            if src == Position(4, home_row):
                dst = Position(6, home_row)
                if castling_possible(board, src, Position(7, home_row), player_sign):
                    moves.append(Move(src, dst))

                dst = Position(2, home_row)
                if castling_possible(board, src, Position(0, home_row), player_sign):
                    moves.append(Move(src, dst))
    
    valid_moves = []
    scores = []
    attack_moves = find_all_possible_attacks(board, king_position, -1 * player_sign)
    for move in moves:
        unmove = board.move(move)
        if move.src == king_position or king_position is None:
            valid_move = True
        else:
            valid_move = True
            for attack_move in attack_moves:
                attacking_piece = board[attack_move.src]

                if abs(attacking_piece) in [1, 2]:
                    valid_move = False
                else:
                    if abs(attacking_piece) in [3, 5]:
                        offset = attack_move.dst - attack_move.src

                        dir = Position(1 if offset.x > 0 else -1, 1 if offset.y > 0 else -1)
                        distance = offset.x
                    elif abs(attacking_piece) in [4, 5]:
                        offset = attack_move.dst - attack_move.src

                        if offset.x == 0:
                            dir = Position(0, 1 if offset.y > 0 else -1)
                            distance = abs(offset.y)
                        else:
                            dir = Position(1 if offset.x > 0 else -1, 0)
                            distance = abs(offset.x)

                    for dist in range(1, distance):
                        midpoint = attack_move.src + dist * dir

                        if board.occupied(midpoint):
                            valid_move = False
                            break
                
                if not valid_move:
                    break

        if valid_move:
            valid_moves.append(move)
            score = 0
            piece = abs(board[move.dst])
            if piece != 0:
                score += values[piece]
            #score = player_sign * evaluate_position(board)
            if move in killer_moves:
                score += 1000
            scores.append(score)
        board.unmove(unmove)
    
    sorted_idx = numpy.argsort(scores)
    return [valid_moves[idx] for idx in reversed(sorted_idx)]

values = numpy.array([0.0, 100.0, 300.0, 320.0, 500.0, 900.0, 200000.0])

position_bonus = numpy.array([
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 10, 10, 10, 10, 0, 0],
    [0, 0, 10, 30, 30, 10, 0, 0],
    [0, 0, 10, 30, 30, 10, 0, 0],
    [0, 0, 10, 10, 10, 10, 0, 0],
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
        
        # positions = board.find_piece_positions(sign)
        # for pos in positions:
        #     piece = abs(board[pos])
        #     if piece > 1:
        #         total_value += sign * piece_mobility_score[piece] * len(find_moves(board, pos))

        total_value += sign * (
            numpy.sum(values[pieces]) +
            numpy.sum(position_bonus * (positive_perspective_board > 0))
        )
    
    return total_value


class AIGame:
    board: Board
    dmax: int = 5
    killer_move_count: int = 2

    def __init__(self, board_: Board):
        self.board = board_

    def update_position(self, move: Move, clist: List[Unmove], ply: int):
        # Update the board with a new move
        unmove = self.board.move(move)
        clist.append(unmove)
        return ply + 1

    def restore_position(self, clist : List[Unmove], ply : int):
        # Pop a board change off the clist to return the board to a previous state
        unmove = clist.pop()
        self.board.unmove(unmove)
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
                    do_prune = scores[ply] >= scores[ply - 2]
                else:
                    do_prune = scores[ply] <= scores[ply - 2]
            else:
                if (ply - 1) % 2 == 0:
                    do_prune = scores[ply] <= scores[ply - 2]
                else:
                    do_prune = scores[ply] >= scores[ply - 2]
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
        killer_moves: List[Deque[Move]] = self.dmax * [deque()]
        mptr: List[int] = self.dmax * [0]
        scores: List[float] = (self.dmax + 1) * [0]
        pc: List[List[Move]] = self.dmax * [[]]
        clist: List[Unmove] = []
        ply: int = 0
        player_sign: int = active_player_sign

        for current_dmax in range(1, self.dmax + 1):
            moves[ply] = generate_moves(self.board, player_sign, killer_moves[ply])
            mptr[ply] = 0
            scores[ply] = player_sign * -float('inf')
            while ply < len(pc[0]):
                next_move = pc[0][ply]

                moves[ply].remove(next_move)
                moves[ply] = [next_move] + moves[ply]

                ply = self.update_position(next_move, clist, ply)

                moves[ply] = generate_moves(self.board, player_sign * (-1)**ply, killer_moves[ply])
                mptr[ply] = 0
                if len(moves[ply]) == 0:
                    scores[ply] = evaluate_position(self.board)
                elif ply > 1:
                    scores[ply] = scores[ply - 2]
                else:
                    scores[ply] = player_sign * (-1)**ply * -float('inf')

            while True:
                if mptr[ply] == len(moves[ply]):
                    prune = self.pc_update(mptr, moves, scores, pc, ply, player_sign)

                    if ply == 0:
                        break

                    ply = self.restore_position(clist, ply)
                    if prune:
                        if len(killer_moves[ply]) >= self.killer_move_count:
                            killer_moves[ply].popleft()
                        killer_moves[ply].append(moves[ply][mptr[ply]])
                        mptr[ply] = len(moves[ply]) # skip the rest of the moves
                    else:
                        mptr[ply] += 1
                else:
                    next_move = moves[ply][mptr[ply]]
                    ply = self.update_position(next_move, clist, ply)
                    if ply < current_dmax:
                        # If not at last layer, advance layer
                        moves[ply] = generate_moves(self.board, player_sign * (-1)**ply, killer_moves[ply])
                        mptr[ply] = 0
                        if len(moves[ply]) == 0:
                            scores[ply] = evaluate_position(self.board)
                        elif ply > 1:
                            scores[ply] = scores[ply - 2]
                        else:
                            scores[ply] = player_sign * (-1)**ply * -float('inf')
                    elif ply == current_dmax:
                        # If at last layer, evaluate score
                        scores[ply] = evaluate_position(self.board)
                        prune = self.pc_update(mptr, moves, scores, pc, ply, player_sign)
                        ply = self.restore_position(clist, ply)
                        if prune:
                            if len(killer_moves[ply]) >= self.killer_move_count:
                                killer_moves[ply].popleft()
                            killer_moves[ply].append(next_move)
                            mptr[ply] = len(moves[ply]) # skip the rest of the moves
                        else:
                            mptr[ply] += 1
                    else:
                        raise Exception("Unhandled state")

        if len(pc[0]) > 0:
            return pc[0][0]
        else:
            return None
