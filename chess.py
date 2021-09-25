import sys
import pygame
from pygame.locals import KEYDOWN, MOUSEBUTTONDOWN, QUIT, K_b, K_c, K_v
import concurrent.futures
from board import Board
from state import GameState
from ui import create_background, create_piece_sprites, create_square_sprites, draw_board


# Initialize and create UI
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
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
small_font = pygame.font.Font(None, 28)
controls_text = small_font.render("C = AI (white),   V = AI (black),   B = undo", 1, (240, 240, 80))

# Create clock, board and global game state
clock = pygame.time.Clock()
board = Board()
state = GameState(board)


def draw():
    global state

    # Update state depending on where the cursor is
    pos, mouse_x, mouse_y = state.update_based_on_cursor()

    # Event handling, perform moves
    for event in pygame.event.get():

        # Exit
        if event.type == QUIT:
            sys.exit()

        # Key press
        elif event.type == KEYDOWN:
            if event.key == K_b:
                state.rewind()
            elif event.key == K_c:
                state.start_ai_computation(executor, 1)
            elif event.key == K_v:
                state.start_ai_computation(executor, -1)
            state.reset_ui()

        # Mouse click
        elif event.type == MOUSEBUTTONDOWN:
            if mouse_y < 480:
                if state.selected is None:
                    state.update_selected(pos)
                else:
                    state.perform_move(state.selected, pos)
                    state.reset_ui()

    # AI state
    state.check_ai_status()

    # Draw the board
    draw_board(screen, background, state, piece_sprites, square_sprites, square_size, controls_text)


# Game loop
while 1:
    draw()
    clock.tick(60)
