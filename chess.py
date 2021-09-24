import math
import numpy
import sys
from typing import List, Dict, Tuple
import pygame
from pygame.locals import KEYDOWN, MOUSEBUTTONDOWN, QUIT, K_b, K_c, K_v
import concurrent.futures

from ai import AIGame
from board import Board, Move, Position
from ui import create_background, create_piece_sprites, create_square_sprites

# Initialize and create UI
executor = concurrent.futures.ThreadPoolExecutor(max_workers = 1)
pygame.init()
screen = pygame.display.set_mode((480, 520))
pygame.display.set_caption("Chess")
background = create_background(screen)

# Create sprites and fonts
piece_sprites = create_piece_sprites(40)
hover_sprite, selected_sprite, ai_sprite = create_square_sprites(58)
text_color = (250, 250, 250)
bottom_font = pygame.font.Font(None, 36)
computing_text = bottom_font.render("Computing next move...", 1, text_color)
done_text = bottom_font.render("Done!", 1, text_color)

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

def do_ai(board : Board, active_player_sign : int):
    ai = AIGame(board)
    move = ai.pick_next_move(active_player_sign)
    return (move.src, move.dst)

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
        if event.type == QUIT:
            sys.exit()
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
        elif event.type == MOUSEBUTTONDOWN:
            if screen_y < 480:
                if selected == None:
                    if board.occupied(pos):
                        selected = pos
                else:
                    previous_piece = board.move(selected, pos)
                    moves.append(((selected, pos), previous_piece))
                    selected = None
                    ai_src = None
                    ai_dst = None
    if ai is not None and ai.done():
        ai_src, ai_dst = ai.result()
        ai = None

    # Draw sprites
    screen.blit(background, (0, 0))
    for x in range(8):
        for y in range(8):
            if ai_src is not None and ai_src.x == x and ai_src.y == y:
                screen.blit(ai_sprite, (x * 60 + 1, (420 - y * 60) + 1, 58, 58))

            if ai_dst is not None and ai_dst.x == x and ai_dst.y == y:
                screen.blit(ai_sprite, (x * 60 + 1, (420 - y * 60) + 1, 58, 58))

            if hovered is not None and hovered.x == x and hovered.y == y:
                screen.blit(hover_sprite, (x * 60 + 1, (420 - y * 60) + 1, 58, 58))
            
            if selected is not None and selected.x == x and selected.y == y:
                screen.blit(selected_sprite, (x * 60 + 1, (420 - y * 60) + 1, 58, 58))

            pos = Position(x, y)
            signed_piece = board[pos]
            piece = abs(signed_piece)
            player_sign = numpy.sign(signed_piece)

            if piece == 0:
                continue
            sprite = piece_sprites[player_sign][piece]

            centerx = 30 + x * 60
            centery = 480 - 30 - y * 60
            pos = sprite.get_rect(centerx = centerx, centery = centery)
            screen.blit(sprite, pos)

            if ai is not None:
                text = computing_text
            elif ai_src is not None:
                text = done_text
            else:
                text = None

            if text is not None:
                pos = text.get_rect(centerx = 240, centery = 500)
                screen.blit(text, pos)

    pygame.display.flip()

# Game loop
while 1:
    draw()
    clock.tick(60)
