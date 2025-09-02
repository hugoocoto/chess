import sys
import termios
import tty

FG = dict({
    'white': '\033[31m',
    'black': '\033[30m',
    'reset': '\033[0m'
})

BG = dict({
    'black': '\033[47m',
    'white': '\033[44m',
    'reset': '\033[0m'
})


class Pos():
    x: int
    y: int

    def __init__(self, x=-1, y=-1):
        self.x = x
        self.y = y

    def get(self):
        return self.x, self.y

    def getx(self):
        return self.x

    def gety(self):
        return self.y


class Piece():
    pos: Pos
    name: str
    show: str
    col: int

    def __init__(self, name='none', pos=Pos(), show=' ', col='white'):
        self.name = name
        self.show = show
        self.col = col
        if self.name != 'none':
            self.pos = pos
            board[pos.x][pos.y] = self
        pass

    def can_move(self, new_pos: Pos):
        pass

    def move(self, pos: Pos):
        pass

    def __repr__(self):
        return "".join([FG[self.col], " ", self.show, " "])


board: list[list[Piece]] = [[Piece() for _ in range(8)] for _ in range(8)]


def set_starting_position():
    Piece("King", Pos(0, 0), "󰡛", "white")
    Piece("King", Pos(0, 1), "󰡘", "white")
    Piece("King", Pos(0, 2), "󰡜", "white")
    Piece("King", Pos(0, 3), "󰡚", "white")
    Piece("King", Pos(0, 4), "󰡗", "white")
    Piece("King", Pos(0, 5), "󰡜", "white")
    Piece("King", Pos(0, 6), "󰡘", "white")
    Piece("King", Pos(0, 7), "󰡛", "white")
    Piece("King", Pos(1, 0), "󰡙", "white")
    Piece("King", Pos(1, 1), "󰡙", "white")
    Piece("King", Pos(1, 2), "󰡙", "white")
    Piece("King", Pos(1, 3), "󰡙", "white")
    Piece("King", Pos(1, 4), "󰡙", "white")
    Piece("King", Pos(1, 5), "󰡙", "white")
    Piece("King", Pos(1, 6), "󰡙", "white")
    Piece("King", Pos(1, 7), "󰡙", "white")

    Piece("King", Pos(7, 0), "󰡛", "black")
    Piece("King", Pos(7, 1), "󰡘", "black")
    Piece("King", Pos(7, 2), "󰡜", "black")
    Piece("King", Pos(7, 3), "󰡚", "black")
    Piece("King", Pos(7, 4), "󰡗", "black")
    Piece("King", Pos(7, 5), "󰡜", "black")
    Piece("King", Pos(7, 6), "󰡘", "black")
    Piece("King", Pos(7, 7), "󰡛", "black")
    Piece("King", Pos(6, 0), "󰡙", "black")
    Piece("King", Pos(6, 1), "󰡙", "black")
    Piece("King", Pos(6, 2), "󰡙", "black")
    Piece("King", Pos(6, 3), "󰡙", "black")
    Piece("King", Pos(6, 4), "󰡙", "black")
    Piece("King", Pos(6, 5), "󰡙", "black")
    Piece("King", Pos(6, 6), "󰡙", "black")
    Piece("King", Pos(6, 7), "󰡙", "black")


def print_board_white():
    print('\033[H\033[2J', end='')
    bg = 'black'
    for i, line in enumerate(reversed(board)):
        print("\n\r", f"{8-i} ", end='')
        bg = 'white' if bg == 'black' else 'black'
        for p in line:
            bg = 'white' if bg == 'black' else 'black'
            print(BG[bg], p, sep='', end='')
    print(BG['reset'], "\r")
    for a in " ABCDEFG":
        print(f" {a} ", end='')
    print("")


def main():
    print("Chess TUI by Hugo Coto (github.com/hugoocoto/chess)")
    print("Pulsa teclas (ESC para salir):")

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    set_starting_position()
    try:
        tty.setraw(fd)  # raw mode
        while True:
            print_board_white()
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # ESC
                print("\nSaliendo...")
                break
            elif ch.isprintable():
                print(f"alphanumeric key '{ch}' pressed")
            else:
                print(f"special key {repr(ch)} pressed")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    main()
    main()
    main()
