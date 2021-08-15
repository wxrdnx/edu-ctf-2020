import base64
from pwn import *
tr = {
    'v': 'A',
    'w': 'B',
    'x': 'C',
    'y': 'D',
    'z': 'E',
    'A': 'F',
    'B': 'G',
    'C': 'H',
    'D': 'I',
    'E': 'J',
    'F': 'K',
    'G': 'L',
    'H': 'M',
    'I': 'N',
    'J': 'O',
    'K': 'P',
    'L': 'Q',
    'M': 'R',
    'N': 'S',
    'O': 'T',
    'P': 'U',
    'Q': 'V',
    'R': 'W',
    'S': 'X',
    'T': 'Y',
    'U': 'Z',
    'V': 'a',
    'W': 'b',
    'X': 'c',
    'Y': 'd',
    'Z': 'e',
    '!': 'f',
    '"': 'g',
    '#': 'h',
    '$': 'i',
    '%': 'j',
    '&': 'k',
    '\x27': 'l',
    '(': 'm',
    ')': 'n',
    '*': 'o',
    '+': 'p',
    ',': 'q',
    '-': 'r',
    '.': 's',
    '/': 't',
    ':': 'u',
    ';': 'v',
    '<': 'w',
    '=': 'x',
    '>': 'y',
    '?': 'z',
    '@': '0',
    '[': '1',
    '\\': '2',
    ']': '3',
    '^': '4',
    '_': '5',
    '`': '6',
    '{': '7',
    '|': '8',
    '}': '9',
    '~': '+',
    'o': '/',
    ' ': '='
}
encode = 'M&=wM].]VyA?GR&[GRA%I]Q#HOA_GRz/T%M?H?T@UR_%HBL?GRA.U?w>HSM*WS@ '
result = ''
for i in range(len(encode)):
    result += tr[encode[i]]
result = base64.b64decode(result).decode()
print(result)
