import pytest

from app.assembler.tokenizer import Token, Tokenizer
from app.assembler.tokenizer import TokenType as T


@pytest.fixture
def tokenizer():
    return Tokenizer()


# ===== 값 (var) =====


def test_alias_var(tokenizer):
    # 원본: var a = 3;
    # alias: 값 a = 3;
    tokens = tokenizer.tokenize("값 a = 3;")

    assert tokens == [
        Token(T.VAR, "값"),
        Token(T.IDENTIFIER, "a"),
        Token(T.EQUAL, "="),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


# ===== 출력 / 보여줘 (print) =====


def test_alias_print_1(tokenizer):
    # 원본: print a;
    # alias: 출력 a;
    tokens = tokenizer.tokenize("출력 a;")

    assert tokens == [
        Token(T.PRINT, "출력"),
        Token(T.IDENTIFIER, "a"),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


def test_alias_print_2(tokenizer):
    # 원본: print a;
    # alias: 보여줘 a;
    tokens = tokenizer.tokenize("보여줘 a;")

    assert tokens == [
        Token(T.PRINT, "보여줘"),
        Token(T.IDENTIFIER, "a"),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


# ===== 함수 (Func) =====


def test_alias_func(tokenizer):
    # 원본: Func add() {}
    # alias: 함수 add() {}
    tokens = tokenizer.tokenize("함수 add() {}")

    assert tokens == [
        Token(T.FUNC, "함수"),
        Token(T.IDENTIFIER, "add"),
        Token(T.LEFT_PAREN, "("),
        Token(T.RIGHT_PAREN, ")"),
        Token(T.LEFT_BRACE, "{"),
        Token(T.RIGHT_BRACE, "}"),
        Token(T.EOF, ""),
    ]


# ===== 반환 / 돌려줘 (return) =====


def test_alias_return_1(tokenizer):
    # 원본: return a;
    # alias: 반환 a;
    tokens = tokenizer.tokenize("반환 a;")

    assert tokens == [
        Token(T.RETURN, "반환"),
        Token(T.IDENTIFIER, "a"),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


def test_alias_return_2(tokenizer):
    # 원본: return a;
    # alias: 돌려줘 a;
    tokens = tokenizer.tokenize("돌려줘 a;")

    assert tokens == [
        Token(T.RETURN, "돌려줘"),
        Token(T.IDENTIFIER, "a"),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


# ===== 클래스 (Class) =====


def test_alias_class(tokenizer):
    # 원본: Class Robot {}
    # alias: 클래스 Robot {}
    tokens = tokenizer.tokenize("클래스 Robot {}")

    assert tokens == [
        Token(T.CLASS, "클래스"),
        Token(T.IDENTIFIER, "Robot"),
        Token(T.LEFT_BRACE, "{"),
        Token(T.RIGHT_BRACE, "}"),
        Token(T.EOF, ""),
    ]


# ===== 이것 (This) =====


def test_alias_this(tokenizer):
    # 원본: This.a;
    # alias: 이것.a;
    tokens = tokenizer.tokenize("이것.a;")

    assert tokens == [
        Token(T.THIS, "이것"),
        Token(T.DOT, "."),
        Token(T.IDENTIFIER, "a"),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


# ===== 부모 (Super) =====


def test_alias_super(tokenizer):
    # 원본: Super.a;
    # alias: 부모.a;
    tokens = tokenizer.tokenize("부모.a;")

    assert tokens == [
        Token(T.SUPER, "부모"),
        Token(T.DOT, "."),
        Token(T.IDENTIFIER, "a"),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


# ===== 만약 (if) =====


def test_alias_if(tokenizer):
    # 원본: if (a > 3) {}
    # alias: 만약 (a 크다 3) {}
    tokens = tokenizer.tokenize("만약 (a 크다 3) {}")

    assert tokens == [
        Token(T.IF, "만약"),
        Token(T.LEFT_PAREN, "("),
        Token(T.IDENTIFIER, "a"),
        Token(T.GREATER, "크다"),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.RIGHT_PAREN, ")"),
        Token(T.LEFT_BRACE, "{"),
        Token(T.RIGHT_BRACE, "}"),
        Token(T.EOF, ""),
    ]


# ===== 아니면 (else) =====


def test_alias_else(tokenizer):
    # 원본: if (a > 3) {} else {}
    # alias: 만약 (a 크다 3) {} 아니면 {}
    tokens = tokenizer.tokenize("만약 (a 크다 3) {} 아니면 {}")

    assert tokens == [
        Token(T.IF, "만약"),
        Token(T.LEFT_PAREN, "("),
        Token(T.IDENTIFIER, "a"),
        Token(T.GREATER, "크다"),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.RIGHT_PAREN, ")"),
        Token(T.LEFT_BRACE, "{"),
        Token(T.RIGHT_BRACE, "}"),
        Token(T.ELSE, "아니면"),
        Token(T.LEFT_BRACE, "{"),
        Token(T.RIGHT_BRACE, "}"),
        Token(T.EOF, ""),
    ]


# ===== 반복 (for) =====


def test_alias_for(tokenizer):
    # 원본: for (;;) {}
    # alias: 반복 (;;) {}
    tokens = tokenizer.tokenize("반복 (;;) {}")

    assert tokens == [
        Token(T.FOR, "반복"),
        Token(T.LEFT_PAREN, "("),
        Token(T.SEMICOLON, ";"),
        Token(T.SEMICOLON, ";"),
        Token(T.RIGHT_PAREN, ")"),
        Token(T.LEFT_BRACE, "{"),
        Token(T.RIGHT_BRACE, "}"),
        Token(T.EOF, ""),
    ]


# ===== 참 / ㅇㅇ (true) =====


def test_alias_true_1(tokenizer):
    # 원본: true;
    # alias: 참;
    tokens = tokenizer.tokenize("참;")

    assert tokens == [
        Token(T.TRUE, "참"),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


def test_alias_true_2(tokenizer):
    # 원본: true;
    # alias: ㅇㅇ;
    tokens = tokenizer.tokenize("ㅇㅇ;")

    assert tokens == [
        Token(T.TRUE, "ㅇㅇ"),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


# ===== 거짓 / ㄴㄴ (false) =====


def test_alias_false_1(tokenizer):
    # 원본: false;
    # alias: 거짓;
    tokens = tokenizer.tokenize("거짓;")

    assert tokens == [
        Token(T.FALSE, "거짓"),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


def test_alias_false_2(tokenizer):
    # 원본: false;
    # alias: ㄴㄴ;
    tokens = tokenizer.tokenize("ㄴㄴ;")

    assert tokens == [
        Token(T.FALSE, "ㄴㄴ"),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


# ===== 그리고 (and) =====


def test_alias_and(tokenizer):
    # 원본: a and b;
    # alias: a 그리고 b;
    tokens = tokenizer.tokenize("a 그리고 b;")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.AND, "그리고"),
        Token(T.IDENTIFIER, "b"),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


# ===== 또는 (or) =====


def test_alias_or(tokenizer):
    # 원본: a or b;
    # alias: a 또는 b;
    tokens = tokenizer.tokenize("a 또는 b;")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.OR, "또는"),
        Token(T.IDENTIFIER, "b"),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


# ===== 크다 (>) =====


def test_alias_greater(tokenizer):
    # 원본: a > 3;
    # alias: a 크다 3;
    tokens = tokenizer.tokenize("a 크다 3;")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.GREATER, "크다"),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


# ===== 작다 (<) =====


def test_alias_less(tokenizer):
    # 원본: a < 3;
    # alias: a 작다 3;
    tokens = tokenizer.tokenize("a 작다 3;")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.LESS, "작다"),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


# ===== 같다 (==) =====


def test_alias_equal_equal(tokenizer):
    # 원본: a == 3;
    # alias: a 같다 3;
    tokens = tokenizer.tokenize("a 같다 3;")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.EQUAL_EQUAL, "같다"),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


# ===== 다르다 (!=) =====


def test_alias_bang_equal(tokenizer):
    # 원본: a != 3;
    # alias: a 다르다 3;
    tokens = tokenizer.tokenize("a 다르다 3;")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.BANG_EQUAL, "다르다"),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


# ===== 크거나같다 (>=) =====


def test_alias_greater_equal(tokenizer):
    # 원본: a >= 3;
    # alias: a 크거나같다 3;
    tokens = tokenizer.tokenize("a 크거나같다 3;")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.GREATER_EQUAL, "크거나같다"),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


# ===== 작거나같다 (<=) =====


def test_alias_less_equal(tokenizer):
    # 원본: a <= 3;
    # alias: a 작거나같다 3;
    tokens = tokenizer.tokenize("a 작거나같다 3;")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.LESS_EQUAL, "작거나같다"),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]
