FG = {
    'white': '\033[31m',
    'black': '\033[30m',
    'reset': '\033[0m',
}

BG = {
    'black': '\033[47m',
    'white': '\033[44m',
    'reset': '\033[0m',
}

PIECES = {
    'q': FG['white'] + str("󰡚"),
    'k': FG['white'] + str("󰡗"),
    'n': FG['white'] + str("󰡘"),
    'b': FG['white'] + str("󰡜"),
    'r': FG['white'] + str("󰡛"),
    'p': FG['white'] + str("󰡙"),
    'Q': FG['black'] + str("󰡚"),
    'K': FG['black'] + str("󰡗"),
    'N': FG['black'] + str("󰡘"),
    'B': FG['black'] + str("󰡜"),
    'R': FG['black'] + str("󰡛"),
    'P': FG['black'] + str("󰡙"),
    'none': str(" "),
}
