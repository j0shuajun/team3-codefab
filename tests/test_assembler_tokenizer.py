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
