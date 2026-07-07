import pytest

from assembler.tokenizer import Token, Tokenizer, TokenType as T


@pytest.fixture
def tokenizer():
    return Tokenizer()


# ===== 단일문자 토큰 =====

def test_assign_number(tokenizer):
    tokens = tokenizer.tokenize("age = 37")

    assert tokens == [Token(T.IDENTIFIER, "age"),
                      Token(T.EQUAL, "="),
                      Token(T.NUMBER, "37", value=37.0),
                      Token(T.EOF, "")]


def test_plus_operator(tokenizer):
    tokens = tokenizer.tokenize("a + b")

    assert tokens == [Token(T.IDENTIFIER, "a"),
                      Token(T.PLUS, "+"),
                      Token(T.IDENTIFIER, "b"),
                      Token(T.EOF, "")]


def test_multiply_operator(tokenizer):
    tokens = tokenizer.tokenize("b * 3")

    assert tokens == [Token(T.IDENTIFIER, "b"),
                      Token(T.STAR, "*"),
                      Token(T.NUMBER, "3", value=3.0),
                      Token(T.EOF, "")]


def test_plus_multiply_operator(tokenizer):
    tokens = tokenizer.tokenize("a + b * 3")

    assert tokens == [Token(T.IDENTIFIER, "a"),
                      Token(T.PLUS, "+"),
                      Token(T.IDENTIFIER, "b"),
                      Token(T.STAR, "*"),
                      Token(T.NUMBER, "3", value=3.0),
                      Token(T.EOF, "")]


def test_minus_operator(tokenizer):
    tokens = tokenizer.tokenize("a - b")

    assert tokens == [Token(T.IDENTIFIER, "a"),
                      Token(T.MINUS, "-"),
                      Token(T.IDENTIFIER, "b"),
                      Token(T.EOF, "")]


def test_divide_operator(tokenizer):
    tokens = tokenizer.tokenize("10 / 2")

    assert tokens == [Token(T.NUMBER, "10", value=10.0),
                      Token(T.SLASH, "/"),
                      Token(T.NUMBER, "2", value=2.0),
                      Token(T.EOF, "")]


def test_grouping(tokenizer):
    tokens = tokenizer.tokenize("( a + b )")

    assert tokens == [Token(T.LEFT_PAREN, "("),
                      Token(T.IDENTIFIER, "a"),
                      Token(T.PLUS, "+"),
                      Token(T.IDENTIFIER, "b"),
                      Token(T.RIGHT_PAREN, ")"),
                      Token(T.EOF, "")]


def test_block_scope(tokenizer):
    tokens = tokenizer.tokenize("{ a + b }")

    assert tokens == [Token(T.LEFT_BRACE, "{"),
                      Token(T.IDENTIFIER, "a"),
                      Token(T.PLUS, "+"),
                      Token(T.IDENTIFIER, "b"),
                      Token(T.RIGHT_BRACE, "}"),
                      Token(T.EOF, "")]


def test_semicolon(tokenizer):
    tokens = tokenizer.tokenize("a=3;b=4")

    assert tokens == [Token(T.IDENTIFIER, "a"),
                      Token(T.EQUAL, "="),
                      Token(T.NUMBER, "3", value=3.0),
                      Token(T.SEMICOLON, ";"),
                      Token(T.IDENTIFIER, "b"),
                      Token(T.EQUAL, "="),
                      Token(T.NUMBER, "4", value=4.0),
                      Token(T.EOF, "")]


def test_less_than(tokenizer):
    tokens = tokenizer.tokenize("a < 3")

    assert tokens == [Token(T.IDENTIFIER, "a"),
                      Token(T.LESS, "<"),
                      Token(T.NUMBER, "3", value=3.0),
                      Token(T.EOF, "")]


def test_greater_than(tokenizer):
    tokens = tokenizer.tokenize("a > 3")

    assert tokens == [Token(T.IDENTIFIER, "a"),
                      Token(T.GREATER, ">"),
                      Token(T.NUMBER, "3", value=3.0),
                      Token(T.EOF, "")]


def test_comma(tokenizer):
    tokens = tokenizer.tokenize("a, b")

    assert tokens == [Token(T.IDENTIFIER, "a"),
                      Token(T.COMMA, ","),
                      Token(T.IDENTIFIER, "b"),
                      Token(T.EOF, "")]


def test_assign_with_comma(tokenizer):
    tokens = tokenizer.tokenize("a, b = 3, 4")

    assert tokens == [Token(T.IDENTIFIER, "a"),
                      Token(T.COMMA, ","),
                      Token(T.IDENTIFIER, "b"),
                      Token(T.EQUAL, "="),
                      Token(T.NUMBER, "3", value=3.0),
                      Token(T.COMMA, ","),
                      Token(T.NUMBER, "4", value=4.0),
                      Token(T.EOF, "")]


def test_bang(tokenizer):
    tokens = tokenizer.tokenize("!a")

    assert tokens == [Token(T.BANG, "!"),
                      Token(T.IDENTIFIER, "a"),
                      Token(T.EOF, "")]


# ===== 여러문자 토큰 =====

def test_if_condition(tokenizer):
    tokens = tokenizer.tokenize("if (x > 10)")

    assert tokens == [Token(T.IF, "if"),
                      Token(T.LEFT_PAREN, "("),
                      Token(T.IDENTIFIER, "x"),
                      Token(T.GREATER, ">"),
                      Token(T.NUMBER, "10", value=10.0),
                      Token(T.RIGHT_PAREN, ")"),
                      Token(T.EOF, "")]


def test_var_statement(tokenizer):
    tokens = tokenizer.tokenize("var a = 37")

    assert tokens == [Token(T.VAR, "var"),
                      Token(T.IDENTIFIER, "a"),
                      Token(T.EQUAL, "="),
                      Token(T.NUMBER, "37", value=37.0),
                      Token(T.EOF, "")]


def test_true(tokenizer):
    tokens = tokenizer.tokenize("var a = true")

    assert tokens == [Token(T.VAR, "var"),
                      Token(T.IDENTIFIER, "a"),
                      Token(T.EQUAL, "="),
                      Token(T.TRUE, "true"),
                      Token(T.EOF, "")]


def test_false(tokenizer):
    tokens = tokenizer.tokenize("var a = false")

    assert tokens == [Token(T.VAR, "var"),
                      Token(T.IDENTIFIER, "a"),
                      Token(T.EQUAL, "="),
                      Token(T.FALSE, "false"),
                      Token(T.EOF, "")]


def test_string(tokenizer):
    tokens = tokenizer.tokenize('"hi"')

    assert tokens == [Token(T.STRING, '"hi"', value="hi"),
                      Token(T.EOF, "")]


def test_string_not_closed(tokenizer):
    with pytest.raises(ValueError):
        tokenizer.tokenize('"hi')


def test_print_statement(tokenizer):
    tokens = tokenizer.tokenize('print("hi")')

    assert tokens == [Token(T.PRINT, "print"),
                      Token(T.LEFT_PAREN, "("),
                      Token(T.STRING, '"hi"', value="hi"),
                      Token(T.RIGHT_PAREN, ")"),
                      Token(T.EOF, "")]


def test_print_expression(tokenizer):
    tokens = tokenizer.tokenize("print(a+b)")

    assert tokens == [Token(T.PRINT, "print"),
                      Token(T.LEFT_PAREN, "("),
                      Token(T.IDENTIFIER, "a"),
                      Token(T.PLUS, "+"),
                      Token(T.IDENTIFIER, "b"),
                      Token(T.RIGHT_PAREN, ")"),
                      Token(T.EOF, "")]
