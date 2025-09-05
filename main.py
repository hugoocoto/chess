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
    ' ': str(" "),
}

termination = ['' for _ in range(12)]
termination[chess.Termination.CHECKMATE.value] = " by checkmate"
termination[chess.Termination.STALEMATE.value] = " by stalemate"
termination[chess.Termination.INSUFFICIENT_MATERIAL.value] = " by insufficient material"
termination[chess.Termination.SEVENTYFIVE_MOVES.value] = " by seventyfive moves"
termination[chess.Termination.FIVEFOLD_REPETITION.value] = " by fivefold repetition"
termination[chess.Termination.FIFTY_MOVES.value] = " by fifty moves"
termination[chess.Termination.THREEFOLD_REPETITION.value] = " by threefold repetition"
termination[chess.Termination.VARIANT_WIN.value] = " by variant win"
termination[chess.Termination.VARIANT_LOSS.value] = " by variant loss"
termination[chess.Termination.VARIANT_DRAW.value] = " by variant draw"

global selected_cell
selected_cell = (-1, 0)

engine = chess.engine.SimpleEngine.popen_uci(r"./Stockfish/src/stockfish")
engine.configure({"UCI_LimitStrength": True, "UCI_Elo": 1320})
chessboard = chess.Board()

board: list[list[str]] = [[' ' for _ in range(8)] for _ in range(8)]


def print_board_white(stdscr):
    for i in range(8):
        for j in range(8):
            stdscr.addstr(7-i, j*3, f" {PIECES[board[i][j]]} ",
                          curses.color_pair(1 +
                                            board[i][j].islower()*2 +
                                            (i+j) % 2 +
                                            4*((i, j) == selected_cell))
                          | curses.A_REVERSE
                          | curses.A_BOLD)

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
            board[x0][y0+1], board[x1][y1+1] = board[x0][y1+1], ' '
        if y0 - y1 > 1:
            board[x0][y0-1], board[x1][y1-2] = board[x0][y1-2], ' '

    elif y0 != y1 and \
            board[x0][y0] in ('P', 'p') and \
            board[x1][y1] == ' ':
        board[x0][y1] = ' '  # en - passant

    if len(p) == 1:
        board[x0][y0] = p[0].upper() if chessboard.turn else p[0]  # promotion

    board[x0][y0], board[x1][y1] = ' ', board[x0][y0]


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
                board[x][y] = ' '
                y += 1
    # todo: use the last part of the fen


def set_starting_position():
    set_board_from_fen(chess.STARTING_BOARD_FEN)


def bot_move(t=0.01):
    result = engine.play(chessboard, chess.engine.Limit(time=t))
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
        if ch == curses.KEY_MOUSE:
            id, my, mx, z, bstate = curses.getmouse()
            x = 7-mx
            y = my//3
            selected_cell = (x, y)
            print_board_white(stdscr)
            if bstate & curses.BUTTON1_RELEASED | curses.BUTTON1_PRESSED:
                if my//3 >= 0 and my//3 <= 7 and mx >= 0 and mx <= 7:
                    return selected_cell

        elif (ch in (curses.KEY_LEFT, ord("h"))):
            if y > 0:
                y -= 1
        elif (ch in (curses.KEY_RIGHT, ord("l"))):
            if y < 7:
                y += 1
        elif (ch in (curses.KEY_DOWN, ord("j"))):
            if x > 0:
                x -= 1
        elif (ch in (curses.KEY_UP, ord("k"))):
            if x < 7:
                x += 1
        elif (ch in (curses.KEY_ENTER, 10, ord("\t"))):
            break
        else:
            continue
        selected_cell = x, y
        print_board_white(stdscr)
    return selected_cell


def user_move_raw(stdscr):
    global selected_cell
    if selected_cell == (-1, -1):
        selected_cell = (4, 2)
        print_board_white(stdscr)

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


def play(stdscr):
    global chessboard
    chessboard = chess.Board()
    set_starting_position()
    print_board_white(stdscr)

    while not (out := chessboard.outcome()):
        if chessboard.turn == chess.WHITE:
            user_move_raw(stdscr)

        else:
            bot_move()

        print_board_white(stdscr)

    stdscr.move(8, 0)
    match out.winner:
        case chess.WHITE: stdscr.addstr("White win")
        case chess.BLACK: stdscr.addstr("Black win")
        case _:           stdscr.addstr("Draw")

    stdscr.addstr(termination[out.termination.value])
    stdscr.refresh()
    stdscr.getstr()
    stdscr.move(8, 0)
    stdscr.clrtoeol()


def main(stdscr):
    global chessboard
    curses.mousemask(curses.ALL_MOUSE_EVENTS)
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLUE, -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_RED)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(5, curses.COLOR_GREEN, -1)
    curses.init_pair(6, curses.COLOR_GREEN, -1)
    curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_RED)
    curses.init_pair(8, curses.COLOR_GREEN, curses.COLOR_RED)
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_WHITE)

    while (True):
        play(stdscr)
    engine.quit()


if __name__ == '__main__':
    curses.wrapper(main)
