from dataclasses import dataclass
import numpy
from typing import List, Dict, Tuple
#import pygame

# pygame.init()
# screen = pygame.display.set_mode((640, 480))
# pygame.display.set_caption("Chess")

@dataclass(frozen = True)
class Position():
    x : int
    y : int

@dataclass(frozen = True)
class Move():
    src : Position
    dst : Position

dmax = 3
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
board : numpy.array = numpy.zeros([8, 8]).astype(int)
moves : List[List[Move]] = dmax * [[]]
mptr : List[int] = dmax * [0]
scores : List[float] = (dmax + 1) * [0]
pc : List[List[Move]] = dmax * [[]]
clist : List[Tuple[Move, int]] = []
ply = 0
player_sign = 1

def reset_board():
    global board
    board = numpy.zeros([8, 8]).astype(int)
    for i in range(8):
        board[i, 1] = 1
        board[i, 6] = -1
    board[0, 0] = 4
    board[7, 0] = 4
    board[0, 7] = -4
    board[7, 7] = -4
    board[1, 0] = 2
    board[6, 0] = 2
    board[1, 7] = -2
    board[6, 7] = -2
    board[2, 0] = 3
    board[5, 0] = 3
    board[2, 7] = -3
    board[5, 7] = -3
    board[3, 0] = 5
    board[4, 0] = 6
    board[3, 7] = -5
    board[4, 7] = -6

def can_move_space(pos):
    x = pos.x
    y = pos.y
    if x >= 0 and x < board.shape[0] and y >= 0 and y < board.shape[1]:
        if board[x, y] == 0:
            return True
        else:
            return False
    return False

def can_capture_space(pos, player_sign):
    x = pos.x
    y = pos.y
    if x >= 0 and x < board.shape[0] and y >= 0 and y < board.shape[1]:
        if player_sign * board[x, y] < 0:
            return True
        else:
            return False
    return False

def generate_moves(player_sign):
    if player_sign not in [1, -1]:
        raise Exception("Player sign must be 1 or -1")

    moves : List[Move] = []

    # Return a list (100x4) of moves for the given board state and ply
    for x in range(8):
        for y in range(8):
            src = Position(x, y)
            signed_piece = board[x, y]

            if signed_piece * player_sign < 0:
                continue

            piece = abs(signed_piece)
            if piece == 1:
                dst = Position(x, y + player_sign)
                if can_move_space(dst):
                    moves.append(Move(src, dst))

                    dst = Position(x, y + 2 * player_sign)
                    if y == player_sign or (y - 7) == player_sign and can_move_space(dst):
                        moves.append(Move(src, dst))

                dst = Position(x + 1, y + player_sign)
                if can_capture_space(dst, player_sign):
                    moves.append(Move(src, dst))

                dst = Position(x - 1, y + player_sign)
                if can_capture_space(dst, player_sign):
                    moves.append(Move(src, dst))
    
    return moves


def evaluate_position():
    # Return score of current board
    total_value = 0.0

    for x in range(8):
        for y in range(8):
            signed_piece = board[x, y]
            sign = numpy.sign(signed_piece)
            piece = abs(signed_piece)
            value = abs(values[piece])
            if piece == 1:
                value += pawn_position_bonus[x, y]
            total_value += sign * value
    
    return total_value

def update_position(move : Move):
    # Update the board with a new move
    if board[move.src.x, move.src.y] == 0:
        raise Exception(f"No piece at {move.src} to move")
    
    previous_piece = board[move.dst.x, move.dst.y]
    board[move.dst.x, move.dst.y] = board[move.src.x, move.src.y]
    board[move.src.x, move.src.y] = 0
    clist.append((move, previous_piece))

    global ply
    ply += 1

def restore_position():
    # Pop a board change off the clist to return the board to a previous state
    move, previous_piece = clist.pop()

    board[move.src.x, move.src.y] = board[move.dst.x, move.dst.y]
    board[move.dst.x, move.dst.y] = previous_piece

    global ply
    ply -= 1

def pc_update():
    # Update the principle continuation for ply - 1
    if ply == 0:
        return

    if (ply - 1) == 0:
        a = 1

    # Odd plies minimize, even plies maximize
    if (ply - 1) % 2 == 0:
        do_update = scores[ply] > scores[ply - 1]
    else:
        do_update = scores[ply] < scores[ply - 1]

    if do_update:
        scores[ply - 1] = scores[ply]
        if ply < len(pc):
            current_pc = pc[ply]
        else:
            current_pc = []
        pc[ply - 1] = [moves[ply - 1][mptr[ply - 1]]] + current_pc

def print_board():
    symbols = {
        0 : "-",
        1 : "p",
        2 : "h",
        3 : "b",
        4 : "r",
        5 : "q",
        6 : "k"
    }
    blue = "\033[91m"
    green = "\033[92m"
    yellow = "\033[93m"
    end = "\033[0m"
    for y in range(7, -1, -1):
        characters = []
        for x in range(8):
            signed_piece = board[x, y]
            piece = abs(signed_piece)
            if signed_piece > 0:
                color = green
            elif signed_piece < 0:
                color = yellow
            else:
                color = blue
            characters.append(f"{color}{symbols[piece]}{end}")

        print("".join(characters))

reset_board()

print_board()

moves[ply] = generate_moves(player_sign)
mptr[ply] = 0
scores[ply] = -float('inf')

while True:
    if mptr[ply] == len(moves[ply]):
        if ply == 2:
            a = 1
        pc_update()

        if ply == 0:
            break

        restore_position()

        mptr[ply] += 1
    else:
        update_position(moves[ply][mptr[ply]])
        if ply == 1:
            a = 1
        if ply < dmax:
            # If not at last layer, advance layer
            moves[ply] = generate_moves(player_sign * (-1)**ply)
            mptr[ply] = 0
            scores[ply] = -1 * (-1)**ply * float('inf')
        elif ply == dmax:
            # If at last layer, evaluate score
            scores[ply] = evaluate_position()

            pc_update()

            restore_position()

            mptr[ply] += 1
        else:
            raise Exception("Unhandled state")

print(pc[0][0])