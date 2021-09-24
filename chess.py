import math
import numpy
import sys
from typing import List, Dict, Tuple
import pygame
from pygame.locals import KEYDOWN, MOUSEBUTTONDOWN, QUIT, K_b, K_c, K_v
import concurrent.futures

from ai import AIGame
from board import Board, Move, Position
from ui import create_background, create_piece_sprites, create_square_sprites, draw_square


# Initialize and create UI
executor = concurrent.futures.ThreadPoolExecutor(max_workers = 1)
pygame.init()
WIDTH = 480
HEIGHT = 560
square_size = 58
piece_size = int(0.78*square_size)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")
background = create_background(screen)

# Create sprites and fonts
piece_sprites = create_piece_sprites(piece_size)
square_sprites = create_square_sprites(square_size)
text_color = (250, 250, 250)
main_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)
computing_text = main_font.render("Computing next move...", 1, text_color)
done_text = main_font.render("Done!", 1, text_color)
controls_text = small_font.render("C = AI (white),   V = AI (black),   B = undo", 1, text_color)

# Create clock and board
clock = pygame.time.Clock()
board = Board()

# Global state
selected = None
hovered = None
moves = []
ai = None
ai_src = None
ai_dst = None


def do_ai(board: Board, active_player_sign: int):
    ai = AIGame(board)
    move = ai.pick_next_move(active_player_sign)
    return move.src, move.dst


def draw():
    global selected
    global hovered
    global moves
    global ai
    global ai_src
    global ai_dst

    # Determine what square the cursor is on
    screen_x, screen_y = pygame.mouse.get_pos()
    x = math.floor(screen_x / 60)
    y = math.floor((480 - screen_y) / 60)
    pos = Position(x, y)
    if x < 8 and y < 8:
        hovered = pos
    else:
        hovered = None

    # Event handling, perform moves
    for event in pygame.event.get():

        # Exit
        if event.type == QUIT:
            sys.exit()

        # Key press
        elif event.type == KEYDOWN:
            if event.key == K_b:
                if len(moves) > 0:
                    (src, dst), previous_piece = moves.pop()
                    board.move(dst, src, previous_piece)
                    ai_src = None
                    ai_dst = None
            elif event.key == K_c:
                ai = executor.submit(do_ai, board, 1)
            elif event.key == K_v:
                ai = executor.submit(do_ai, board, -1)
            selected = None
            ai_src = None
            ai_dst = None

        # Mouse click
        elif event.type == MOUSEBUTTONDOWN:
            if screen_y < 480:
                if selected is None:
                    if board.occupied(pos):
                        selected = pos
                else:
                    previous_piece = board.move(selected, pos)
                    moves.append(((selected, pos), previous_piece))
                    selected = None
                    ai_src = None
                    ai_dst = None

    # AI state
    if ai is not None and ai.done():
        ai_src, ai_dst = ai.result()
        ai = None

    # Draw sprites
    screen.blit(background, (0, 0))
    for x in range(8):
        for y in range(8):

            # Draw square
            draw_square(screen, x, y, ai_dst, ai_src, hovered, selected, square_sprites, square_size)

            # Draw piece
            pos = Position(x, y)
            signed_piece = board[pos]
            piece = abs(signed_piece)
            player_sign = numpy.sign(signed_piece)
            if piece == 0:
                continue
            sprite = piece_sprites[player_sign][piece]
            centerx = 30 + x * 60
            centery = 480 - 30 - y * 60
            pos = sprite.get_rect(centerx=centerx, centery=centery)
            screen.blit(sprite, pos)

            # Draw "computing..." or "done" text
            if ai is not None:
                text = computing_text
            elif ai_src is not None:
                text = done_text
            else:
                text = None

            if text is not None:
                pos = text.get_rect(centerx=240, centery=500)
                screen.blit(text, pos)

            # Draw controls text
            screen.blit(controls_text, (10, HEIGHT - 30))

    pygame.display.flip()


# Game loop
while 1:
    draw()
    clock.tick(60)
