from dataclasses import dataclass
from typing import List


def piece_name(piece: int):
    idx = abs(piece)
    player = "White" if piece > 0 else "Black"
    player = "" if piece == 0 else player
    pieces = ["None", "Pawn", "Knight", "Bishop", "Rook", "Queen", "King"]
    return player + " " + pieces[idx]


def piece_letter(piece: int):
    pieces = ["-", "", "N", "B", "R", "Q", "K"]
    return pieces[piece]


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Position(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self * other

    def __repr__(self):
        files = ["a", "b", "c", "d", "e", "f", "g", "h"]
        ranks = ["1", "2", "3", "4", "5", "6", "7", "8"]
        return files[self.x] + ranks[self.y]


@dataclass(frozen=True)
class PiecePosition:
    piece: int
    pos: Position

    def __repr__(self):
        if self.piece == 0:
            return "-"
        return piece_name(self.piece) + " at " + str(self.pos)


@dataclass(frozen=True)
class Move:
    src: Position
    dst: Position


@dataclass(frozen=True)
class PromotionMove(Move):
    promoted_piece: int


@dataclass(frozen=True)
class Unmove:
    removes: List[PiecePosition]
    adds: List[PiecePosition]
    en_passant_pos: Position
    has_moved: int

    def human_readable(self):
        return "add = " + str(self.removes) + ", remove = " + str(self.adds)



