import pygame


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
    hover_color = (200, 120, 120)
    select_color = (220, 220, 120)
    ai_highlight_color = (120, 120, 220)
    hover_sprite = pygame.Surface(square_size)
    hover_sprite.fill(hover_color)
    selected_sprite = pygame.Surface(square_size)
    selected_sprite.fill(select_color)
    ai_sprite = pygame.Surface(square_size)
    ai_sprite.fill(ai_highlight_color)
    return hover_sprite, selected_sprite, ai_sprite


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
