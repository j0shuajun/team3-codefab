from assembler.tokenizer import Token, Tokenizer, TokenType as T

def test_equal():
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize("age = 37")

    assert tokens == [Token(T.IDENTIFIER, "age"),
                      Token(T.EQUAL, "="),
                      Token(T.NUMBER, "37", value=37.0),
                      Token(T.EOF, "")]
