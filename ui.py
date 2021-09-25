import pygame
from board import Position
import numpy


def create_background(screen):
    background = pygame.Surface(screen.get_size()).convert()
    background.fill((120, 120, 120))
    colors = [(80, 80, 80), (160, 160, 160)]
    for x in range(8):
        for y in range(8):
            color = colors[(x + y) % 2]
            base_x = x * 60 + 1
            base_y = (7 - y) * 60 + 1
            rect = (base_x, base_y, 58, 58)
            background.fill(color, rect)
    return background


def create_square_sprites(size: int):
    square_size = (size, size)
    hover_color = (240, 80, 80)
    select_color = (240, 240, 80)
    ai_highlight_color = (80, 80, 180)
    hover_sprite = pygame.Surface(square_size)
    hover_sprite.fill(hover_color)
    selected_sprite = pygame.Surface(square_size)
    selected_sprite.fill(select_color)
    ai_sprite = pygame.Surface(square_size)
    ai_sprite.fill(ai_highlight_color)
    return ai_sprite, hover_sprite, selected_sprite


def piece_sprite(col, typ, size: int):
    im = pygame.image.load("sprites/" + col + "_" + typ + "_png_128px.png")
    return pygame.transform.scale(im.convert_alpha(), (size, size))


def create_piece_sprites(size: int):
    piece_sprites = {
        1: {
            1: piece_sprite("w", "pawn", size),
            2: piece_sprite("w", "knight", size),
            3: piece_sprite("w", "bishop", size),
            4: piece_sprite("w", "rook", size),
            5: piece_sprite("w", "queen", size),
            6: piece_sprite("w", "king", size),
        },
        -1: {
            1: piece_sprite("b", "pawn", size),
            2: piece_sprite("b", "knight", size),
            3: piece_sprite("b", "bishop", size),
            4: piece_sprite("b", "rook", size),
            5: piece_sprite("b", "queen", size),
            6: piece_sprite("b", "king", size),
        }
    }
    return piece_sprites


def draw_square_background(screen, x, y, state, square_sprites, square_size):
    ai_sprite = square_sprites[0]
    hover_sprite = square_sprites[1]
    selected_sprite = square_sprites[2]
    if state.ai_src is not None and state.ai_src.x == x and state.ai_src.y == y:
        screen.blit(ai_sprite, (x * 60 + 1, (420 - y * 60) + 1, square_size, square_size))

    if state.ai_dst is not None and state.ai_dst.x == x and state.ai_dst.y == y:
        screen.blit(ai_sprite, (x * 60 + 1, (420 - y * 60) + 1, square_size, square_size))

    if state.hovered is not None and state.hovered.x == x and state.hovered.y == y:
        screen.blit(hover_sprite, (x * 60 + 1, (420 - y * 60) + 1, square_size, square_size))

    if state.selected is not None and state.selected.x == x and state.selected.y == y:
        screen.blit(selected_sprite, (x * 60 + 1, (420 - y * 60) + 1, square_size, square_size))


def draw_board(screen, background, state, piece_sprites, square_sprites, square_size, controls_text):
    screen.blit(background, (0, 0))
    for x in range(8):
        for y in range(8):

            # Draw square background
            draw_square_background(screen, x, y, state, square_sprites, square_size)

            # Draw piece
            pos = Position(x, y)
            signed_piece = state.board[pos]
            piece = abs(signed_piece)
            player_sign = numpy.sign(signed_piece)
            if piece == 0:
                continue
            sprite = piece_sprites[player_sign][piece]
            centerx = 30 + x * 60
            centery = 480 - 30 - y * 60
            pos = sprite.get_rect(centerx=centerx, centery=centery)
            screen.blit(sprite, pos)

            # Draw the AI info text
            text = state.get_ai_text()
            if text is not None:
                pos = text.get_rect(centerx=320, centery=500)
                screen.blit(text, pos)

            # Draw the turn info text
            text = state.get_turn_text()
            if text is not None:
                pos = text.get_rect(centerx=90, centery=500)
                screen.blit(text, pos)

            # Draw controls text
            _, HEIGHT = pygame.display.get_surface().get_size()
            screen.blit(controls_text, (10, HEIGHT - 30))
    pygame.display.flip()
