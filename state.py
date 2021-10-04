import pygame
import math
from ai import AIGame
from board import Board, Move, Position


def do_ai(board: Board, active_player_sign: int):
    ai = AIGame(board)
    return ai.pick_next_move(active_player_sign)


class GameState:
    def __init__(self, board):
        self.board = board
        self.selected = None
        self.hovered = None
        self.hovered_left = 1
        self.hovered_top = 2
        self.moves = []
        self.ai = None
        self.ai_move = None
        text_font = pygame.font.Font(None, 32)
        ai_text_color = (60, 70, 200)
        self.compute_text = text_font.render("Computing...", 1, ai_text_color)
        self.done_text = text_font.render("Done! (press SPACE)", 1, ai_text_color)
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
        self.hovered_left = int(screen_x / 30) % 2 == 0
        self.hovered_top = int(screen_y / 30) % 2 == 0
        if x < 8 and y < 8:
            self.hovered = pos
        else:
            self.hovered = None
        return pos, screen_x, screen_y

    def rewind(self):
        """Undo previous move and update state."""
        if len(self.moves) > 0:
            unmove = self.moves.pop()
            self.board.unmove(unmove)
            self.ai_move = None

    def reset_ui(self):
        """Reset highlighting things (except hover)."""
        self.selected = None
        self.ai_move = None

    def update_selected(self, pos):
        """Make position pos selected if it is occupied"""
        if self.board.occupied(pos):
            self.selected = pos

    def perform_move(self, move: Move):
        """Perform specified move and update state, if it is source occupiers turn."""
        unmove = self.board.move(move)
        self.moves.append(unmove)

    def start_ai_computation(self, executor, player_sign):
        """Send AI computation to executor and update state."""
        self.ai = executor.submit(do_ai, self.board, player_sign)

    def check_ai_status(self):
        """Check if AI is done and update state."""
        ai = self.ai
        if ai is not None and ai.done():
            result = ai.result()
            if result is not None:
                self.ai_move = result
            self.ai = None

    def get_ai_text(self):
        """Get the current AI info text."""
        if self.ai is not None:
            text = self.compute_text
        elif self.ai_move is not None:
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

    def execute_ai_move(self):
        """Execute the current suggested AI move."""
        if self.ai_move is not None:
            self.perform_move(self.ai_move)

    def print_move_history(self):
        """Print current game history."""
        print(" ")
        print("---------------------------- MOVES ----------------------------------")
        L = len(self.moves)
        if L == 0:
            print("No moves yet.")
        else:
            for m_idx in range(0, L):
                move_str = self.moves[m_idx].human_readable()
                print("(" + str(m_idx) + ") " + move_str)
