from dataclasses import dataclass
import numpy

@dataclass(frozen = True)
class Position():
    x : int
    y : int

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
    
    def occupied(self, pos):
      return self.board[pos.y, pos.x] != 0

    def move(self, src, dst, replacement_piece = 0):
        # Update the board with a new move
        if not self.occupied(src):
            raise Exception(f"No piece at {src} to move")

        previous_piece = self.board[dst.y, dst.x]
        self.board[dst.y, dst.x] = self.board[src.y, src.x]
        self.board[src.y, src.x] = replacement_piece
        return previous_piece
