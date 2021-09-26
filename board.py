from dataclasses import dataclass
import numpy

@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)
    
    def __mul__(self, other):
        return Position(self.x * other, self.y * other)
    
    def __rmul__(self, other):
        return self * other

file_directions = tuple([
    Position(1, 0), Position(-1, 0),
    Position(0, 1), Position(0, -1)
])

diagonal_directions = tuple([
    Position(1, 1), Position(-1, 1),
    Position(1, -1), Position(-1, -1)
])

knight_directions = tuple([
    Position(1, 2), Position(-1, 2),
    Position(2, -1), Position(2, 1),
    Position(1, -2), Position(-1, -2),
    Position(-2, -1), Position(-2, 1)
])

@dataclass(frozen=True)
class Move:
    src: Position
    dst: Position


class Board:
    board: numpy.array = numpy.zeros([8, 8]).astype(int)

    def __init__(self):
        self.reset()

    def reset(self):
        board = numpy.array([
            [ 4,  2,  3,  5,  6,  3,  2,  4],
            [ 1,  1,  1,  1,  1,  1,  1,  1],
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-4, -2, -3, -5, -6, -3, -2, -4]
        ]).astype(int)

        self.board = board
    
    def is_valid_position(self, pos : Position):
        x = pos.x
        y = pos.y

        if not (y < 0 or y >= self.board.shape[0] or x < 0 or x >= self.board.shape[1]):
            return True
        else:
            return False

    def find_piece_positions(self, player_sign = None):
        ys, xs = numpy.where(self.board * player_sign > 0)

        positions = []
        for x, y in zip(xs, ys):
            positions.append(Position(x, y))
        return positions

    def can_move_space(self, pos):
        if self.is_valid_position(pos):
            if self.board[pos.y, pos.x] == 0:
                return True
            else:
                return False
        return False

    def can_capture_space(self, pos, player_sign):
        if self.is_valid_position(pos):
            if player_sign * self.board[pos.y, pos.x] < 0:
                return True
            else:
                return False
        return False
    
    def __getitem__(self, pos: Position):
        if not self.is_valid_position(pos):
            raise Exception(f"{pos} is not a valid position")

        return self.board[pos.y, pos.x]
    
    def __setitem__(self, pos: Position, val):
        if not self.is_valid_position(pos):
            raise Exception(f"{pos} is not a valid position")

        self.board[pos.y, pos.x] = val
    
    def occupied(self, pos: Position):
        return self[pos] != 0

    def occupying_player(self, pos):
        """Check which player is occupying a position pos."""
        return numpy.sign(self[pos])

    def move(self, src: Position, dst: Position, replacement_piece: int = 0):
        # Update the board with a new move
        previous_piece = self[dst]
        self[dst] = self[src]
        self[src] = replacement_piece
        return previous_piece

