import pygame
import math
from ai import AIGame
from board import Board, Position


def do_ai(board: Board, active_player_sign: int):
    ai = AIGame(board)
    move = ai.pick_next_move(active_player_sign)
    return move.src, move.dst


class GameState:
    def __init__(self, board):
        self.board = board
        self.selected = None
        self.hovered = None
        self.moves = []
        self.ai = None
        self.ai_src = None
        self.ai_dst = None
        text_font = pygame.font.Font(None, 32)
        text_color = (80, 80, 180)
        self.compute_text = text_font.render("Computing...", 1, text_color)
        self.done_text = text_font.render("Done!", 1, text_color)
        self.black_turn_text = text_font.render("Black to move.", 1, (5, 5, 5))
        self.white_turn_text = text_font.render("White to move.", 1, (250, 250, 250))

    def check_whose_turn(self):
        """Check whose turn it is (1 = white, -1 = black)."""
        if len(self.moves) % 2 > 0:
            return -1
        else:
            return 1

    def update_based_on_cursor(self):
        """Update state based on where cursor is."""
        screen_x, screen_y = pygame.mouse.get_pos()
        x = math.floor(screen_x / 60)
        y = math.floor((480 - screen_y) / 60)
        pos = Position(x, y)
        if x < 8 and y < 8:
            self.hovered = pos
        else:
            self.hovered = None
        return pos, screen_x, screen_y

    def rewind(self):
        """Undo previous move and update state."""
        if len(self.moves) > 0:
            (src, dst), previous_piece = self.moves.pop()
            self.board.move(dst, src, previous_piece)
            self.ai_src = None
            self.ai_dst = None

    def reset_ui(self):
        """Reset highlighting things (except hover)."""
        self.selected = None
        self.ai_src = None
        self.ai_dst = None

    def update_selected(self, pos):
        """Make position pos selected if it is occupied"""
        if self.board.occupied(pos):
            self.selected = pos

    def perform_move(self, src: Position, dst: Position):
        """Perform move from source to destination and update state."""
        previous_piece = self.board.move(src, dst)
        self.moves.append(((src, dst), previous_piece))

    def start_ai_computation(self, executor, player_sign):
        """Send AI computation to executor and update state."""
        self.ai = executor.submit(do_ai, self.board, player_sign)

    def check_ai_status(self):
        """Check if AI is done and update state."""
        ai = self.ai
        if ai is not None and ai.done():
            self.ai_src, self.ai_dst = ai.result()
            self.ai = None

    def get_ai_text(self):
        """Get the current AI info text."""
        if self.ai is not None:
            text = self.compute_text
        elif self.ai_src is not None:
            text = self.done_text
        else:
            text = None
        return text

    def get_turn_text(self):
        """Get the current turn info text."""
        if self.check_whose_turn() == -1:
            text = self.black_turn_text
        else:
            text = self.white_turn_text
        return text

