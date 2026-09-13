"""
keyboard_map.py
Physical proximity lookup table for standard US QWERTY keyboard layout.
Used by engine.py to simulate realistic adjacent-key typographical errors.
"""

import random

# Proximity graph for standard US QWERTY physical key positions
QWERTY_NEIGHBORS = {
    # Number Row
    '1': ['2', 'q'],
    '2': ['1', '3', 'q', 'w'],
    '3': ['2', '4', 'w', 'e'],
    '4': ['3', '5', 'e', 'r'],
    '5': ['4', '6', 'r', 't'],
    '6': ['5', '7', 't', 'y'],
    '7': ['6', '8', 'y', 'u'],
    '8': ['7', '9', 'u', 'i'],
    '9': ['8', '0', 'i', 'o'],
    '0': ['9', '-', 'o', 'p'],
    '-': ['0', '=', 'p', '['],
    '=': ['-', ']'],

    # Top Row
    'q': ['1', '2', 'w', 'a'],
    'w': ['2', '3', 'q', 'e', 'a', 's'],
    'e': ['3', '4', 'w', 'r', 's', 'd'],
    'r': ['4', '5', 'e', 't', 'd', 'f'],
    't': ['5', '6', 'r', 'y', 'f', 'g'],
    'y': ['6', '7', 't', 'u', 'g', 'h'],
    'u': ['7', '8', 'y', 'i', 'h', 'j'],
    'i': ['8', '9', 'u', 'o', 'j', 'k'],
    'o': ['9', '0', 'i', 'p', 'k', 'l'],
    'p': ['0', '-', 'o', '[', 'l', ';'],
    '[': ['p', ']', ';', '\''],
    ']': ['[', '\\'],

    # Home Row
    'a': ['q', 'w', 's', 'z'],
    's': ['w', 'e', 'a', 'd', 'z', 'x'],
    'd': ['e', 'r', 's', 'f', 'x', 'c'],
    'f': ['r', 't', 'd', 'g', 'c', 'v'],
    'g': ['t', 'y', 'f', 'h', 'v', 'b'],
    'h': ['y', 'u', 'g', 'j', 'b', 'n'],
    'j': ['u', 'i', 'h', 'k', 'n', 'm'],
    'k': ['i', 'o', 'j', 'l', 'm', ','],
    'l': ['o', 'p', 'k', ';', ',', '.'],
    ';': ['p', '[', 'l', '\'', '.', '/'],
    '\'': ['[', ';', '/'],

    # Bottom Row
    'z': ['a', 's', 'x'],
    'x': ['z', 's', 'd', 'c'],
    'c': ['x', 'd', 'f', 'v', ' '],
    'v': ['c', 'f', 'g', 'b', ' '],
    'b': ['v', 'g', 'h', 'n', ' '],
    'n': ['b', 'h', 'j', 'm', ' '],
    'm': ['n', 'j', 'k', ',', ' '],
    ',': ['m', 'k', 'l', '.'],
    '.': [',', 'l', ';', '/'],
    '/': ['.', ';', '\''],
}


def get_neighbor(char: str) -> str:
    """
    Returns a random physically adjacent character on the keyboard.
    Preserves uppercase casing if the original character was uppercase.
    Falls back to the original character if it has no mapping.
    """
    if not char:
        return char

    is_upper = char.isupper()
    lookup = char.lower()
    neighbors = QWERTY_NEIGHBORS.get(lookup)

    if not neighbors:
        return char

    chosen = random.choice(neighbors)
    return chosen.upper() if is_upper else chosen
