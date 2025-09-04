import curses
import chess
import chess.engine

PIECES = {
    'Q': str("󰡚"),    'q': str("󰡚"),
    'K': str("󰡗"),    'k': str("󰡗"),
    'N': str("󰡘"),    'n': str("󰡘"),
    'B': str("󰡜"),    'b': str("󰡜"),
    'R': str("󰡛"),    'r': str("󰡛"),
    'P': str("󰡙"),    'p': str("󰡙"),
    'none': str(" "),
}

global selected_cell
selected_cell = (-1, 0)

engine = chess.engine.SimpleEngine.popen_uci(r"./Stockfish/src/stockfish")
chessboard = chess.Board()

board: list[list[str]] = [['none' for _ in range(8)] for _ in range(8)]


def print_board_white(stdscr):
    for i in range(8):
        for j in range(8):
            stdscr.addstr(7-i, j*3, f" {PIECES[board[i][j]]} ",
                          curses.color_pair(1 +
                                            board[i][j].islower()*2 +
                                            (i+j) % 2 +
                                            4*((i, j) == selected_cell)))

    stdscr.refresh()


def parse(m):
    x0, y0, x1, y1, *p = m
    return ord(x0) - ord("a"), \
        ord(y0) - ord("1"), \
        ord(x1) - ord("a"), \
        ord(y1) - ord("1"), p


# all the moves should be valid
def move(m):
    y0, x0, y1, x1, p = parse(m)

    if board[x0][y0] in ('K', 'k'):  # 0-0
        if y1 - y0 > 1:
            board[x0][y0+1], board[x1][y1+1] = board[x0][y1+1], 'none'
        if y0 - y1 > 1:
            board[x0][y0-1], board[x1][y1-2] = board[x0][y1-2], 'none'

    elif y0 != y1 and \
            board[x0][y0] in ('P', 'p') and \
            board[x1][y1] in (' ', 'none'):
        board[x0][y1] = 'none'  # en - passant

    if len(p) == 1:
        board[x0][y0] = p[0].upper() if chessboard.turn else p[0]  # promotion

    board[x0][y0], board[x1][y1] = 'none', board[x0][y0]


def set_board_from_fen(fen):
    x: int = 0
    y: int = 0
    for f in fen:
        if f == '/':
            x += 1
            y = 0
        elif f in 'rnbqkpRNBQKP':
            board[x][y] = f
            y += 1
        elif f.isdigit():
            for i in range(int(f)):
                board[x][y] = 'none'
                y += 1
    # todo: use the last part of the fen


def set_starting_position():
    set_board_from_fen(chess.STARTING_BOARD_FEN)


def bot_move():
    result = engine.play(chessboard, chess.engine.Limit(time=0.01))
    chessboard.push(result.move)
    move(result.move.uci())


def user_move_text(stdscr):
    curses.echo()
    curses.curs_set(1)
    while (1):
        curses.color_pair(8)
        uci = stdscr.getstr(8, 0).decode("utf-8")
        mov = chess.Move.from_uci(uci)
        if (mov in chessboard.legal_moves):
            break
        print("Invalid move")
    chessboard.push(mov)
    move(uci)
    curses.curs_set(0)
    curses.noecho()


def get_select_cell(stdscr):
    global selected_cell
    x, y = selected_cell
    while (1):
        stdscr.keypad(True)
        ch = stdscr.getch()
        if (ch in (curses.KEY_LEFT, ord("h"))):
            if y > 0:
                y -= 1
        elif (ch in (curses.KEY_RIGHT, ord("l"))):
            if y < 7:
                y += 1
        elif (ch in (curses.KEY_DOWN, ord("j"))):
            if x < 7:
                x += 1
        elif (ch in (curses.KEY_UP, ord("k"))):
            if x > 0:
                x -= 1
        elif (ch in (curses.KEY_ENTER, 10, ord("\t"))):
            break
        else:
            continue
        selected_cell = x, y
        print_board_white(stdscr)
    return selected_cell


def user_move_raw(stdscr):
    x0, y0 = get_select_cell(stdscr)
    x1, y1 = get_select_cell(stdscr)
    uci = chr(y0+ord("a")) +\
        chr(x0+ord("1")) +\
        chr(y1+ord("a")) +\
        chr(x1+ord("1"))

    if x0 == x1 and y0 == y1:
        return user_move_raw(stdscr)

    mov = chess.Move.from_uci(uci)
    if (mov not in chessboard.legal_moves):
        return user_move_raw(stdscr)

    chessboard.push(mov)
    move(uci)


def main(stdscr):
    global chessboard
    curses.mousemask(curses.ALL_MOUSE_EVENTS)
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLUE)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_GREEN)
    curses.init_pair(8, curses.COLOR_RED, curses.COLOR_GREEN)
    curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLACK)

    set_starting_position()
    print_board_white(stdscr)

    while not (out := chessboard.outcome()):
        if chessboard.turn == chess.WHITE:
            bot_move()
        else:
            # user_move_raw(stdscr)
            bot_move()

        print_board_white(stdscr)

    else:
        match out.winner:
            case chess.WHITE:
                stdscr.addstr(8, 0, "White win")
            case chess.BLACK:
                stdscr.addstr(8, 0, "Black win")
            case _:
                stdscr.addstr(8, 0, "Draw")

        match out.termination:
            case chess.Termination.CHECKMATE: stdscr.addstr(" by checkmate")
            case chess.Termination.STALEMATE: stdscr.addstr(" by stalemate")
            case chess.Termination.INSUFFICIENT_MATERIAL: stdscr.addstr(" by insufficient material")
            case chess.Termination.SEVENTYFIVE_MOVES: stdscr.addstr(" by seventyfive moves")
            case chess.Termination.FIVEFOLD_REPETITION: stdscr.addstr(" by fivefold repetition")
            case chess.Termination.FIFTY_MOVES: stdscr.addstr(" by fifty moves")
            case chess.Termination.THREEFOLD_REPETITION: stdscr.addstr(" by threefold repetition")
            case chess.Termination.VARIANT_WIN: stdscr.addstr(" by variant win")
            case chess.Termination.VARIANT_LOSS: stdscr.addstr(" by variant loss")
            case chess.Termination.VARIANT_DRAW: stdscr.addstr(" by variant draw")
            case _: stdscr.addstr(f" by {out.termination}")
    stdscr.getstr()
    chessboard = chess.Board()


if __name__ == '__main__':
    while True:
        curses.wrapper(main)
    engine.quit()
