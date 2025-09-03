import chess
import chess.engine
from vars import BG, PIECES

engine = chess.engine.SimpleEngine.popen_uci(r"./Stockfish/src/stockfish")
chessboard = chess.Board()

board: list[list[str]] = [[PIECES['none'] for _ in range(8)] for _ in range(8)]


screen_cleared = False


def print_board_white():
    global screen_cleared
    if (not screen_cleared):
        print("\033[2J")
        screen_cleared = True
    print("\033[H")
    for i in range(8):
        for j in range(8):
            print(BG['white' if (i+j) % 2 == 0 else 'black'], end='')
            print(f" {board[i][j]} ", end='')
            print(BG['reset'], end='')
        print("")


def parse(m):
    x0, y0, x1, y1, *p = m
    return ord(x0) - ord("a"), \
        ord(y0) - ord("1"), \
        ord(x1) - ord("a"), \
        ord(y1) - ord("1")


# all the moves should be valid
def move(m):
    y0, x0, y1, x1, *p = parse(m)

    if abs(y0 - y1) > 1 and (
            board[x0][y0] == PIECES['K'] or
            board[x0][y0] == PIECES['k']):
        board[x0][y0+1], board[x1][y1+1] = board[x0][y1+1], PIECES['none']

    # todo:handle en-passant

    board[x0][y0], board[x1][y1] = PIECES['none'], board[x0][y0]


def set_board_from_fen(fen):
    x: int = 0
    y: int = 0
    for f in fen:
        if f == '/':
            x += 1
            y = 0
        elif f in 'rnbqkpRNBQKP':
            board[x][y] = PIECES[f]
            y += 1
        elif f.isdigit():
            for i in range(int(f)):
                board[x][y] = PIECES['none']
                y += 1
    # todo: use the last part of the fen


def set_starting_position():
    set_board_from_fen(chess.STARTING_BOARD_FEN)


def bot_move():
    result = engine.play(chessboard, chess.engine.Limit(time=1))
    chessboard.push(result.move)
    move(result.move.uci())


def user_move():
    while (1):
        uci = input("\033[Kmove: ")
        mov = chess.Move.from_uci(uci)
        if (mov in chessboard.legal_moves):
            break
        print("Invalid move")
    chessboard.push(mov)
    move(uci)


def main():
    set_starting_position()
    print_board_white()
    while not chessboard.is_game_over():
        user_move()
        print_board_white()
        bot_move()
        print_board_white()

    engine.quit()


if __name__ == '__main__':
    main()
