import pytest

from assembler.tokenizer import Token, Tokenizer, TokenType as T


@pytest.fixture
def tokenizer():
    return Tokenizer()


def test_assign_number(tokenizer):
    tokens = tokenizer.tokenize("age = 37")

    assert tokens == [Token(T.IDENTIFIER, "age"),
                      Token(T.EQUAL, "="),
                      Token(T.NUMBER, "37", value=37.0),
                      Token(T.EOF, "")]


def test_if_statement(tokenizer):
    tokens = tokenizer.tokenize("if (x > 10)")

    assert tokens == [Token(T.IF, "if"),
                      Token(T.LEFT_PAREN, "("),
                      Token(T.IDENTIFIER, "x"),
                      Token(T.GREATER, ">"),
                      Token(T.NUMBER, "10", value=10.0),
                      Token(T.RIGHT_PAREN, ")"),
                      Token(T.EOF, "")]

def test_plus_operation(tokenizer):
    tokens = tokenizer.tokenize("a + b")

    assert tokens == [Token(T.IDENTIFIER, "a"),
                      Token(T.PLUS, "+"),
                      Token(T.IDENTIFIER, "b")]
