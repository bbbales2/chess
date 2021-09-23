from ai import AIGame
import math
import numpy
import sys
from typing import List, Dict, Tuple
import pygame
from pygame.locals import KEYDOWN, MOUSEBUTTONDOWN, QUIT, K_b, K_c, K_v
import concurrent.futures

from board import Board, Move, Position

executor = concurrent.futures.ThreadPoolExecutor(max_workers = 1)

pygame.init()
screen = pygame.display.set_mode((480, 520))
pygame.display.set_caption("Chess")

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((120, 120, 120))
colors = [(80, 80, 80), (160, 160, 160)]
for x in range(8):
    for y in range(8):
        color = colors[(x + y) % 2]
        base_x = x * 60 + 1
        base_y = (7 - y) * 60 + 1
        rect = (base_x, base_y, 58, 58)
        background.fill(color, rect)

font = pygame.font.Font(None, 36)
PIECE_SIZE = 40


def piece_sprite(col, typ, SIZE: int):
    im = pygame.image.load("sprites/" + col + "_" + typ + "_png_128px.png")
    return pygame.transform.scale(im.convert_alpha(), (SIZE, SIZE))


piece_sprites = {
    1 : {
        1 : piece_sprite("w", "pawn", PIECE_SIZE),
        2 : piece_sprite("w", "knight", PIECE_SIZE),
        3 : piece_sprite("w", "bishop", PIECE_SIZE),
        4 : piece_sprite("w", "rook", PIECE_SIZE),
        5 : piece_sprite("w", "queen", PIECE_SIZE),
        6 : piece_sprite("w", "king", PIECE_SIZE),
    },
    -1 : {
        1 : piece_sprite("b", "pawn", PIECE_SIZE),
        2 : piece_sprite("b", "knight", PIECE_SIZE),
        3 : piece_sprite("b", "bishop", PIECE_SIZE),
        4 : piece_sprite("b", "rook", PIECE_SIZE),
        5 : piece_sprite("b", "queen", PIECE_SIZE),
        6 : piece_sprite("b", "king", PIECE_SIZE),
    }
}

computing_text = font.render("Computing next move...", 1, (250, 250, 250))
done_text = font.render("Done!", 1, (250, 250, 250))
hover_sprite = pygame.Surface((58, 58))
hover_sprite.fill((200, 120, 120))
selected_sprite = pygame.Surface((58, 58))
selected_sprite.fill((220, 220, 120))
ai_sprite = pygame.Surface((58, 58))
ai_sprite.fill((120, 120, 220))

clock = pygame.time.Clock()

board = Board()

def do_ai(board : Board, active_player_sign : int):
    ai = AIGame(board)
    move = ai.pick_next_move(active_player_sign)
    return (move.src, move.dst)

selected = None
hovered = None
moves = []
ai = None
ai_src = None
ai_dst = None

def draw():
    global selected
    global hovered
    global moves
    global ai
    global ai_src
    global ai_dst
    screen_x, screen_y = pygame.mouse.get_pos()

    x = math.floor(screen_x / 60)
    y = math.floor((480 - screen_y) / 60)
    pos = Position(x, y)

    if x < 8 and y < 8:
        hovered = pos
    else:
        hovered = None

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

while 1:
    draw()
    clock.tick(60)

