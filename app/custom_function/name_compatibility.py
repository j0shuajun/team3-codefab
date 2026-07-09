from app.exceptions import CodeFabRuntimeError

HANGUL_BASE = 0xAC00
HANGUL_LAST = 0xD7A3
JUNGSUNG_COUNT = 21
JONGSUNG_COUNT = 28

# 초성: ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ
CHOSUNG_STROKES = [2, 4, 2, 3, 6, 5, 4, 4, 8, 2, 4, 1, 3, 6, 4, 3, 4, 4, 3]

# 중성: ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ
JUNGSUNG_STROKES = [2, 3, 3, 4, 2, 3, 3, 4, 2, 4, 5, 3, 3, 2, 4, 5, 3, 3, 1, 2, 1]

# 종성: (없음)ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ
JONGSUNG_STROKES = [
    0,
    2,
    4,
    4,
    2,
    5,
    5,
    3,
    5,
    7,
    9,
    9,
    7,
    9,
    9,
    8,
    4,
    4,
    6,
    2,
    4,
    1,
    3,
    4,
    3,
    4,
    4,
    3,
]


def _char_strokes(ch):
    if not (HANGUL_BASE <= ord(ch) <= HANGUL_LAST):
        raise CodeFabRuntimeError("♡ operator only supports Korean names.")

    offset = ord(ch) - HANGUL_BASE
    cho, remainder = divmod(offset, JUNGSUNG_COUNT * JONGSUNG_COUNT)
    jung, jong = divmod(remainder, JONGSUNG_COUNT)

    return CHOSUNG_STROKES[cho] + JUNGSUNG_STROKES[jung] + JONGSUNG_STROKES[jong]


def _name_to_strokes(name):
    if not name:
        raise CodeFabRuntimeError("♡ operator requires a non-empty name.")
    return [_char_strokes(ch) for ch in name]


def _interleave(left, right):
    length = max(len(left), len(right))
    row = []
    for i in range(length):
        row.append(left[i] if i < len(left) else 0)
        row.append(right[i] if i < len(right) else 0)
    return row


def _reduce(row):
    while len(row) > 2:
        row = [(row[i] + row[i + 1]) % 10 for i in range(len(row) - 1)]
    return row


def calculate_name_compatibility(name_a, name_b):
    if not isinstance(name_a, str) or not isinstance(name_b, str):
        raise CodeFabRuntimeError("♡ operator requires two strings.")

    row = _interleave(_name_to_strokes(name_a), _name_to_strokes(name_b))
    tens_digit, ones_digit = _reduce(row)
    return tens_digit * 10 + ones_digit
