from dataclasses import dataclass
import numpy

@dataclass(frozen = True)
class Position():
    x : int
    y : int

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)
    
    def __mul__(self, other):
        return Position(self.x * other, self.y * other)
    
    def __rmul__(self, other):
        return self * other

@dataclass(frozen = True)
class Move():
    src : Position
    dst : Position

class Board:
    board : numpy.array = numpy.zeros([8, 8]).astype(int)
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

    def can_move_space(self, pos):
        x = pos.x
        y = pos.y
        if y >= 0 and y < self.board.shape[0] and x >= 0 and x < self.board.shape[1]:
            if self.board[y, x] == 0:
                return True
            else:
                return False
        return False

    def can_capture_space(self, pos, player_sign):
        x = pos.x
        y = pos.y
        if y >= 0 and y < self.board.shape[0] and x >= 0 and x < self.board.shape[1]:
            if player_sign * self.board[y, x] < 0:
                return True
            else:
                return False
        return False
    
    def __getitem__(self, pos : Position):
        x = pos.x
        y = pos.y

        if y < 0 or y >= self.board.shape[0] or x < 0 or x >= self.board.shape[1]:
            raise Exception(f"{pos} is not a valid position")

        return self.board[y, x]
    
    def __setitem__(self, pos : Position, val):
        x = pos.x
        y = pos.y

        if y < 0 or y >= self.board.shape[0] or x < 0 or x >= self.board.shape[1]:
            raise Exception(f"{pos} is not a valid position")

        self.board[y, x] = val
    
    def occupied(self, pos : Position):
      return self[pos] != 0

    def move(self, src : Position, dst : Position, replacement_piece : int = 0):
        # Update the board with a new move
        previous_piece = self[dst]
        self[dst] = self[src]
        self[src] = replacement_piece
        return previous_piece
