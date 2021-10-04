from dataclasses import dataclass
import copy
import numpy
from typing import List, Dict, Set

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
class PiecePosition:
    piece: int
    pos: Position

@dataclass(frozen=True)
class Move:
    src: Position
    dst: Position

@dataclass(frozen = True)
class Unmove:
    removes: List[PiecePosition]
    adds: List[PiecePosition]
    en_passant_pos: Position
    has_moved: Set[Position]

class Board:
    board: numpy.array = numpy.zeros([8, 8]).astype(int)
    # en_passant_pos stores the en passant position
    # so for e2e4, the en_passant_pos would be e3
    en_passant_pos: Position = None
    _has_moved: Set[Position] = set()

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
        self.en_passant_pos = None
        self._has_moved = set()
    
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

    def has_moved(self, pos):
        if pos in self._has_moved:
            return True
        else:
            return False

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

    def move(self, move: Move):
        piece = self[move.src]

        if piece == 0:
            raise Exception(f"No piece to move with {move}")
        
        removes = []
        adds = []

        def record_move(src, dst):
            piece = self[src]
            removes.append(PiecePosition(piece, dst))
            adds.append(PiecePosition(piece, src))
            adds.append(PiecePosition(self[dst], dst))
            self[dst] = piece
            self[src] = 0
        
        record_move(move.src, move.dst)

        has_moved_copy = copy.deepcopy(self._has_moved)

        # If a king, deal with castling logic
        if abs(piece) == 6:
            for side in [0, 7]:
                if move.src == Position(4, side):
                    if move.dst == Position(2, side):
                        rook_position = Position(0, side)
                        self._has_moved.add(rook_position)
                        record_move(rook_position, Position(3, side))
                    elif move.dst == Position(6, side):
                        rook_position = Position(7, side)
                        self._has_moved.add(rook_position)
                        record_move(rook_position, Position(5, side))

        self._has_moved.add(move.src)
        unmove = Unmove(removes, adds, self.en_passant_pos, has_moved_copy)

        return unmove

    def unmove(self, move: Unmove):
        # Update the board with a new move
        for pp in move.removes:
            self[pp.pos] = 0
            self._has_moved.add(pp.pos)

        for pp in move.adds:
            self[pp.pos] = pp.piece
        
        self.en_passant_pos = move.en_passant_pos
        self._has_moved = move.has_moved
