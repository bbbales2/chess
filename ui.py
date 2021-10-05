import pygame
from board import Position
import numpy


def create_background(screen):
    background = pygame.Surface(screen.get_size()).convert()
    background.fill((100, 100, 100))
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
    square_size_small = (int(size / 2), int(size / 2))
    hover_color = (235, 85, 85)
    select_color = (235, 235, 85)
    ai_highlight_color = (75, 105, 200)
    hover_sprite = pygame.Surface(square_size)
    hover_sprite.fill(hover_color)
    hover_sprite_small = pygame.Surface(square_size_small)
    hover_sprite_small.fill(hover_color)
    selected_sprite = pygame.Surface(square_size)
    selected_sprite.fill(select_color)
    ai_sprite = pygame.Surface(square_size)
    ai_sprite.fill(ai_highlight_color)
    return ai_sprite, hover_sprite, hover_sprite_small, selected_sprite


def piece_sprite(col, typ, size: int):
    im = pygame.image.load("sprites/" + col + "_" + typ + "_png_128px.png")
    return pygame.transform.scale(im.convert_alpha(), (size, size))


def create_piece_sprites(size: int):
    piece_sprites = {
        "regular": {
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
        },
        "small": {
            1: {
                2: piece_sprite("w", "knight", int(size / 2)),
                3: piece_sprite("w", "bishop", int(size / 2)),
                4: piece_sprite("w", "rook", int(size / 2)),
                5: piece_sprite("w", "queen", int(size / 2)),
            },
            -1: {
                2: piece_sprite("b", "knight", int(size / 2)),
                3: piece_sprite("b", "bishop", int(size / 2)),
                4: piece_sprite("b", "rook", int(size / 2)),
                5: piece_sprite("b", "queen", int(size / 2)),
            }
        }
    }
    return piece_sprites


def create_sprites(piece_size: int, square_size: int):
    """Create all game sprites."""
    piece_sprites = create_piece_sprites(piece_size)
    square_sprites = create_square_sprites(square_size)
    return {"pieces": piece_sprites, "squares": square_sprites}


def draw_square_background(screen, x, y, state, square_sprites, square_size):
    ai_sprite = square_sprites[0]
    hover_sprite = square_sprites[1]
    hover_sprite_small = square_sprites[2]
    selected_sprite = square_sprites[3]

    if state.ai_move is not None:
        for pos in [state.ai_move.src, state.ai_move.dst]:
            if pos.x == x and pos.y == y:
                x0 = x * 60 + 1
                y0 = (420 - y * 60) + 1
                screen.blit(ai_sprite, (x0, y0, square_size, square_size))

    if state.hovered is not None and state.hovered.x == x and state.hovered.y == y:
        if state.selected is not None:
            signed_selected_piece = state.board[state.selected]
        else:
            signed_selected_piece = 0

        if abs(signed_selected_piece) == 1 and y in [0, 7]:
            if state.hovered_left:
                x_offset = 0
            else:
                x_offset = 29
            if state.hovered_top:
                y_offset = 0
            else:
                y_offset = 29
            x0 = x * 60 + 1 + x_offset
            y0 = (420 - y * 60) + 1 + y_offset
            blit_rect = (x0, y0, int(square_size / 2), int(square_size / 2))
            screen.blit(hover_sprite_small, blit_rect)
        else:
            x0 = x * 60 + 1
            y0 = (420 - y * 60) + 1
            screen.blit(hover_sprite, (x0, y0, square_size, square_size))

    if state.selected is not None and state.selected.x == x and state.selected.y == y:
        x0 = x * 60 + 1
        y0 = (420 - y * 60) + 1
        screen.blit(selected_sprite, (x0, y0, square_size, square_size))


def draw_board(screen, background, state, sprites, square_size, controls_text):
    screen.blit(background, (0, 0))
    square_sprites = sprites["squares"]
    piece_sprites = sprites["pieces"]
    for x in range(8):
        for y in range(8):
            # Draw square background
            draw_square_background(screen, x, y, state, square_sprites, square_size)

            # Draw piece
            pos = Position(x, y)
            if state.selected is not None:
                signed_selected_piece = state.board[state.selected]
            else:
                signed_selected_piece = 0

            ssel = abs(signed_selected_piece) == 1
            if pos == state.hovered and ssel and pos.y in [0, 7]:
                player_sign = numpy.sign(signed_selected_piece)

                sprite = piece_sprites["small"][player_sign][2]
                centerx = 15 + x * 60
                centery = 480 - 45 - y * 60
                pos = sprite.get_rect(centerx=centerx, centery=centery)
                screen.blit(sprite, pos)

                sprite = piece_sprites["small"][player_sign][3]
                centerx = 45 + x * 60
                centery = 480 - 45 - y * 60
                pos = sprite.get_rect(centerx=centerx, centery=centery)
                screen.blit(sprite, pos)

                sprite = piece_sprites["small"][player_sign][4]
                centerx = 15 + x * 60
                centery = 480 - 15 - y * 60
                pos = sprite.get_rect(centerx=centerx, centery=centery)
                screen.blit(sprite, pos)

                sprite = piece_sprites["small"][player_sign][5]
                centerx = 45 + x * 60
                centery = 480 - 15 - y * 60
                pos = sprite.get_rect(centerx=centerx, centery=centery)
                screen.blit(sprite, pos)
            else:
                signed_piece = state.board[pos]
                piece = abs(signed_piece)
                player_sign = numpy.sign(signed_piece)
                if piece == 0:
                    continue
                sprite = piece_sprites["regular"][player_sign][piece]
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
