
dmax = 3
moves : List[List[Move]] = dmax * [[]]
mptr : List[int] = dmax * [0]
scores : List[float] = (dmax + 1) * [0]
pc : List[List[Move]] = dmax * [[]]
clist : List[Tuple[Move, int]] = []
ply = 0
player_sign = 1

def generate_moves(board : Board, player_sign : int):
    if player_sign not in [1, -1]:
        raise Exception("Player sign must be 1 or -1")

    moves : List[Move] = []

    # Return a list (100x4) of moves for the given board state and ply
    for x in range(8):
        for y in range(8):
            src = Position(x, y)
            signed_piece = board.board[x, y]

            if signed_piece * player_sign < 0:
                continue

            piece = abs(signed_piece)
            if piece == 1:
                dst = Position(x, y + player_sign)
                if board.can_move_space(dst):
                    moves.append(Move(src, dst))

                    dst = Position(x, y + 2 * player_sign)
                    if y == player_sign or (y - 7) == player_sign and can_move_space(dst):
                        moves.append(Move(src, dst))

                dst = Position(x + 1, y + player_sign)
                if board.can_capture_space(dst, player_sign):
                    moves.append(Move(src, dst))

                dst = Position(x - 1, y + player_sign)
                if board.can_capture_space(dst, player_sign):
                    moves.append(Move(src, dst))
    
    return moves

values : Dict[int, float] = {
    0 : 0.0,
    1 : 100.0,
    2 : 300.0,
    3 : 320.0,
    4 : 500.0,
    5 : 900.0,
    6 : 1000000.0
}

pawn_position_bonus = numpy.array([
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 100, 100, 0, 0, 0],
    [0, 0, 100, 300, 300, 100, 0, 0],
    [0, 0, 100, 300, 300, 100, 0, 0],
    [0, 0, 0, 100, 100, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
])

def evaluate_position(board):
    # Return score of current board
    total_value = 0.0

    for x in range(8):
        for y in range(8):
            signed_piece = board.board[x, y]
            sign = numpy.sign(signed_piece)
            piece = abs(signed_piece)
            value = abs(values[piece])
            if piece == 1:
                value += pawn_position_bonus[x, y]
            total_value += sign * value
    
    return total_value

def update_position(move : Move):
    # Update the board with a new move
    if board[move.src.x, move.src.y] == 0:
        raise Exception(f"No piece at {move.src} to move")
    
    previous_piece = board[move.dst.x, move.dst.y]
    board[move.dst.x, move.dst.y] = board[move.src.x, move.src.y]
    board[move.src.x, move.src.y] = 0
    clist.append((move, previous_piece))

    global ply
    ply += 1

def restore_position():
    # Pop a board change off the clist to return the board to a previous state
    move, previous_piece = clist.pop()

    board[move.src.x, move.src.y] = board[move.dst.x, move.dst.y]
    board[move.dst.x, move.dst.y] = previous_piece

    global ply
    ply -= 1

def pc_update(self, mptr, moves, scores, pc, ply):
    # Update the principle continuation for ply - 1
    if ply == 0:
        return

    if (ply - 1) == 0:
        a = 1

    # Odd plies minimize, even plies maximize
    if (ply - 1) % 2 == 0:
        do_update = scores[ply] > scores[ply - 1]
    else:
        do_update = scores[ply] < scores[ply - 1]

    if do_update:
        scores[ply - 1] = scores[ply]
        if ply < len(pc):
            current_pc = pc[ply]
        else:
            current_pc = []
        pc[ply - 1] = [moves[ply - 1][mptr[ply - 1]]] + current_pc

def pick_next_move():
    moves[ply] = generate_moves(player_sign)
    mptr[ply] = 0
    scores[ply] = -float('inf')

    while True:
        if mptr[ply] == len(moves[ply]):
            if ply == 2:
                a = 1
            pc_update()

            if ply == 0:
                break

            restore_position()

            mptr[ply] += 1
        else:
            update_position(moves[ply][mptr[ply]])
            if ply == 1:
                a = 1
            if ply < dmax:
                # If not at last layer, advance layer
                moves[ply] = generate_moves(player_sign * (-1)**ply)
                mptr[ply] = 0
                scores[ply] = -1 * (-1)**ply * float('inf')
            elif ply == dmax:
                # If at last layer, evaluate score
                scores[ply] = evaluate_position()

                pc_update()

                restore_position()

                mptr[ply] += 1
            else:
                raise Exception("Unhandled state")

    return pc[0][0]