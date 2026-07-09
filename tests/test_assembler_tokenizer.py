import pytest

from assembler.tokenizer import Token, Tokenizer
from assembler.tokenizer import TokenType as T


@pytest.fixture
def tokenizer():
    return Tokenizer()


# ===== 단일문자 토큰 =====


def test_assign_number(tokenizer):
    tokens = tokenizer.tokenize("age = 37")

    assert tokens == [
        Token(T.IDENTIFIER, "age"),
        Token(T.EQUAL, "="),
        Token(T.NUMBER, "37", value=37.0),
        Token(T.EOF, ""),
    ]


def test_assign_zero(tokenizer):
    tokens = tokenizer.tokenize("age = 0")

    assert tokens == [
        Token(T.IDENTIFIER, "age"),
        Token(T.EQUAL, "="),
        Token(T.NUMBER, "0", value=0.0),
        Token(T.EOF, ""),
    ]


def test_assign_zero_point_zero(tokenizer):
    tokens = tokenizer.tokenize("age = 0.0")

    assert tokens == [
        Token(T.IDENTIFIER, "age"),
        Token(T.EQUAL, "="),
        Token(T.NUMBER, "0.0", value=0.0),
        Token(T.EOF, ""),
    ]


def test_error_assign_number_start_with_zero(tokenizer):
    with pytest.raises(ValueError, match="cannot start with zero"):
        tokenizer.tokenize("age = 01")


def test_error_assign_number_point_number_start_with_zero(tokenizer):
    with pytest.raises(ValueError, match="cannot start with zero"):
        tokenizer.tokenize("age = 01.01")


def test_assign_number_point_number(tokenizer):
    tokens = tokenizer.tokenize("point = 10.1")

    assert tokens == [
        Token(T.IDENTIFIER, "point"),
        Token(T.EQUAL, "="),
        Token(T.NUMBER, "10.1", value=10.1),
        Token(T.EOF, ""),
    ]


def test_assign_number_point_number_2_digit(tokenizer):
    tokens = tokenizer.tokenize("point = 10.11")

    assert tokens == [
        Token(T.IDENTIFIER, "point"),
        Token(T.EQUAL, "="),
        Token(T.NUMBER, "10.11", value=10.11),
        Token(T.EOF, ""),
    ]


def test_assign_zero_point_number(tokenizer):
    tokens = tokenizer.tokenize("point = 0.11")

    assert tokens == [
        Token(T.IDENTIFIER, "point"),
        Token(T.EQUAL, "="),
        Token(T.NUMBER, "0.11", value=0.11),
        Token(T.EOF, ""),
    ]


@pytest.mark.skip(reason="DOT 토큰 추가로, tokenize 단계에서 에러 처리 불가")
def test_error_assign_point_number(tokenizer):
    with pytest.raises(ValueError):
        tokenizer.tokenize("point = .11")


@pytest.mark.skip(reason="DOT 토큰 추가로, tokenize 단계에서 에러 처리 불가")
def test_error_assign_number_point_number_point_number(tokenizer):
    with pytest.raises(ValueError):
        tokenizer.tokenize("point = 10.10.10")


def test_plus_operator(tokenizer):
    tokens = tokenizer.tokenize("a + b")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.PLUS, "+"),
        Token(T.IDENTIFIER, "b"),
        Token(T.EOF, ""),
    ]


def test_multiply_operator(tokenizer):
    tokens = tokenizer.tokenize("b * 3")

    assert tokens == [
        Token(T.IDENTIFIER, "b"),
        Token(T.STAR, "*"),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.EOF, ""),
    ]


def test_plus_multiply_operator(tokenizer):
    tokens = tokenizer.tokenize("a + b * 3")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.PLUS, "+"),
        Token(T.IDENTIFIER, "b"),
        Token(T.STAR, "*"),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.EOF, ""),
    ]


def test_minus_operator(tokenizer):
    tokens = tokenizer.tokenize("a - b")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.MINUS, "-"),
        Token(T.IDENTIFIER, "b"),
        Token(T.EOF, ""),
    ]


def test_divide_operator(tokenizer):
    tokens = tokenizer.tokenize("10 / 2")

    assert tokens == [
        Token(T.NUMBER, "10", value=10.0),
        Token(T.SLASH, "/"),
        Token(T.NUMBER, "2", value=2.0),
        Token(T.EOF, ""),
    ]


def test_grouping(tokenizer):
    tokens = tokenizer.tokenize("( a + b )")

    assert tokens == [
        Token(T.LEFT_PAREN, "("),
        Token(T.IDENTIFIER, "a"),
        Token(T.PLUS, "+"),
        Token(T.IDENTIFIER, "b"),
        Token(T.RIGHT_PAREN, ")"),
        Token(T.EOF, ""),
    ]


def test_block_scope(tokenizer):
    tokens = tokenizer.tokenize("{ a + b }")

    assert tokens == [
        Token(T.LEFT_BRACE, "{"),
        Token(T.IDENTIFIER, "a"),
        Token(T.PLUS, "+"),
        Token(T.IDENTIFIER, "b"),
        Token(T.RIGHT_BRACE, "}"),
        Token(T.EOF, ""),
    ]


def test_semicolon(tokenizer):
    tokens = tokenizer.tokenize("a=3;b=4")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.EQUAL, "="),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.SEMICOLON, ";"),
        Token(T.IDENTIFIER, "b"),
        Token(T.EQUAL, "="),
        Token(T.NUMBER, "4", value=4.0),
        Token(T.EOF, ""),
    ]


def test_less_than(tokenizer):
    tokens = tokenizer.tokenize("a < 3")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.LESS, "<"),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.EOF, ""),
    ]


def test_greater_than(tokenizer):
    tokens = tokenizer.tokenize("a > 3")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.GREATER, ">"),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.EOF, ""),
    ]


def test_comma(tokenizer):
    tokens = tokenizer.tokenize("a, b")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.COMMA, ","),
        Token(T.IDENTIFIER, "b"),
        Token(T.EOF, ""),
    ]


def test_assign_with_comma(tokenizer):
    tokens = tokenizer.tokenize("a, b = 3, 4")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.COMMA, ","),
        Token(T.IDENTIFIER, "b"),
        Token(T.EQUAL, "="),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.COMMA, ","),
        Token(T.NUMBER, "4", value=4.0),
        Token(T.EOF, ""),
    ]


def test_bang(tokenizer):
    tokens = tokenizer.tokenize("!a")

    assert tokens == [Token(T.BANG, "!"), Token(T.IDENTIFIER, "a"), Token(T.EOF, "")]


# ===== 여러문자 토큰 =====


def test_if_condition(tokenizer):
    tokens = tokenizer.tokenize("if (x > 10)")

    assert tokens == [
        Token(T.IF, "if"),
        Token(T.LEFT_PAREN, "("),
        Token(T.IDENTIFIER, "x"),
        Token(T.GREATER, ">"),
        Token(T.NUMBER, "10", value=10.0),
        Token(T.RIGHT_PAREN, ")"),
        Token(T.EOF, ""),
    ]


def test_else_if_condition(tokenizer):
    tokens = tokenizer.tokenize("else if (x > 10)")

    assert tokens == [
        Token(T.ELSE, "else"),
        Token(T.IF, "if"),
        Token(T.LEFT_PAREN, "("),
        Token(T.IDENTIFIER, "x"),
        Token(T.GREATER, ">"),
        Token(T.NUMBER, "10", value=10.0),
        Token(T.RIGHT_PAREN, ")"),
        Token(T.EOF, ""),
    ]


def test_else_block(tokenizer):
    tokens = tokenizer.tokenize("else {a=1}")

    assert tokens == [
        Token(T.ELSE, "else"),
        Token(T.LEFT_BRACE, "{"),
        Token(T.IDENTIFIER, "a"),
        Token(T.EQUAL, "="),
        Token(T.NUMBER, "1", value=1.0),
        Token(T.RIGHT_BRACE, "}"),
        Token(T.EOF, ""),
    ]


def test_var_statement(tokenizer):
    tokens = tokenizer.tokenize("var a = 37")

    assert tokens == [
        Token(T.VAR, "var"),
        Token(T.IDENTIFIER, "a"),
        Token(T.EQUAL, "="),
        Token(T.NUMBER, "37", value=37.0),
        Token(T.EOF, ""),
    ]


def test_true(tokenizer):
    tokens = tokenizer.tokenize("var a = true")

    assert tokens == [
        Token(T.VAR, "var"),
        Token(T.IDENTIFIER, "a"),
        Token(T.EQUAL, "="),
        Token(T.TRUE, "true"),
        Token(T.EOF, ""),
    ]


def test_false(tokenizer):
    tokens = tokenizer.tokenize("var a = false")

    assert tokens == [
        Token(T.VAR, "var"),
        Token(T.IDENTIFIER, "a"),
        Token(T.EQUAL, "="),
        Token(T.FALSE, "false"),
        Token(T.EOF, ""),
    ]


def test_and(tokenizer):
    tokens = tokenizer.tokenize("a and b")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.AND, "and"),
        Token(T.IDENTIFIER, "b"),
        Token(T.EOF, ""),
    ]


def test_or(tokenizer):
    tokens = tokenizer.tokenize("a or b")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.OR, "or"),
        Token(T.IDENTIFIER, "b"),
        Token(T.EOF, ""),
    ]


def test_string(tokenizer):
    tokens = tokenizer.tokenize('"hi"')

    assert tokens == [Token(T.STRING, '"hi"', value="hi"), Token(T.EOF, "")]


def test_string_not_closed(tokenizer):
    with pytest.raises(ValueError):
        tokenizer.tokenize('"hi')


def test_assign_string(tokenizer):
    tokens = tokenizer.tokenize('var a = "hi"')

    assert tokens == [
        Token(T.VAR, "var"),
        Token(T.IDENTIFIER, "a"),
        Token(T.EQUAL, "="),
        Token(T.STRING, '"hi"', value="hi"),
        Token(T.EOF, ""),
    ]


def test_print_statement(tokenizer):
    tokens = tokenizer.tokenize('print("hi")')

    assert tokens == [
        Token(T.PRINT, "print"),
        Token(T.LEFT_PAREN, "("),
        Token(T.STRING, '"hi"', value="hi"),
        Token(T.RIGHT_PAREN, ")"),
        Token(T.EOF, ""),
    ]


def test_print_expression(tokenizer):
    tokens = tokenizer.tokenize("print(a+b)")

    assert tokens == [
        Token(T.PRINT, "print"),
        Token(T.LEFT_PAREN, "("),
        Token(T.IDENTIFIER, "a"),
        Token(T.PLUS, "+"),
        Token(T.IDENTIFIER, "b"),
        Token(T.RIGHT_PAREN, ")"),
        Token(T.EOF, ""),
    ]


def test_bang_equal(tokenizer):
    tokens = tokenizer.tokenize("a != b")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.BANG_EQUAL, "!="),
        Token(T.IDENTIFIER, "b"),
        Token(T.EOF, ""),
    ]


def test_bang_equal_without_blank(tokenizer):
    tokens = tokenizer.tokenize("a!=b")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.BANG_EQUAL, "!="),
        Token(T.IDENTIFIER, "b"),
        Token(T.EOF, ""),
    ]


def test_equal_equal(tokenizer):
    tokens = tokenizer.tokenize("a == b")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.EQUAL_EQUAL, "=="),
        Token(T.IDENTIFIER, "b"),
        Token(T.EOF, ""),
    ]


def test_equal_equal_without_blank(tokenizer):
    tokens = tokenizer.tokenize("a==b")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.EQUAL_EQUAL, "=="),
        Token(T.IDENTIFIER, "b"),
        Token(T.EOF, ""),
    ]


def test_greater_equal(tokenizer):
    tokens = tokenizer.tokenize("a >= b")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.GREATER_EQUAL, ">="),
        Token(T.IDENTIFIER, "b"),
        Token(T.EOF, ""),
    ]


def test_greater_equal_without_blank(tokenizer):
    tokens = tokenizer.tokenize("a>=b")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.GREATER_EQUAL, ">="),
        Token(T.IDENTIFIER, "b"),
        Token(T.EOF, ""),
    ]


def test_less_equal(tokenizer):
    tokens = tokenizer.tokenize("a <= b")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.LESS_EQUAL, "<="),
        Token(T.IDENTIFIER, "b"),
        Token(T.EOF, ""),
    ]


def test_less_equal_without_blank(tokenizer):
    tokens = tokenizer.tokenize("a<=b")

    assert tokens == [
        Token(T.IDENTIFIER, "a"),
        Token(T.LESS_EQUAL, "<="),
        Token(T.IDENTIFIER, "b"),
        Token(T.EOF, ""),
    ]


def test_for_condition(tokenizer):
    tokens = tokenizer.tokenize("for (var i=0; i<5; i=i+1)")

    assert tokens == [
        Token(T.FOR, "for"),
        Token(T.LEFT_PAREN, "("),
        Token(T.VAR, "var"),
        Token(T.IDENTIFIER, "i"),
        Token(T.EQUAL, "="),
        Token(T.NUMBER, "0", value=0.0),
        Token(T.SEMICOLON, ";"),
        Token(T.IDENTIFIER, "i"),
        Token(T.LESS, "<"),
        Token(T.NUMBER, "5", value=5.0),
        Token(T.SEMICOLON, ";"),
        Token(T.IDENTIFIER, "i"),
        Token(T.EQUAL, "="),
        Token(T.IDENTIFIER, "i"),
        Token(T.PLUS, "+"),
        Token(T.NUMBER, "1", value=1.0),
        Token(T.RIGHT_PAREN, ")"),
        Token(T.EOF, ""),
    ]


def test_similar_to_for(tokenizer):
    tokens = tokenizer.tokenize("format before for1")

    assert tokens == [
        Token(T.IDENTIFIER, "format"),
        Token(T.IDENTIFIER, "before"),
        Token(T.IDENTIFIER, "for1"),
        Token(T.EOF, ""),
    ]


def test_similar_to_for_assign(tokenizer):
    tokens = tokenizer.tokenize("form = 1")

    assert tokens == [
        Token(T.IDENTIFIER, "form"),
        Token(T.EQUAL, "="),
        Token(T.NUMBER, "1", value=1.0),
        Token(T.EOF, ""),
    ]


# ===== 배열/필드 접근/상속 토큰 =====


def test_array_index(tokenizer):
    tokens = tokenizer.tokenize("arr[0]")

    assert tokens == [
        Token(T.IDENTIFIER, "arr"),
        Token(T.LEFT_BRACKET, "["),
        Token(T.NUMBER, "0", value=0.0),
        Token(T.RIGHT_BRACKET, "]"),
        Token(T.EOF, ""),
    ]


def test_array_declaration(tokenizer):
    tokens = tokenizer.tokenize("var arr = Array(3);")

    assert tokens == [
        Token(T.VAR, "var"),
        Token(T.IDENTIFIER, "arr"),
        Token(T.EQUAL, "="),
        Token(T.IDENTIFIER, "Array"),
        Token(T.LEFT_PAREN, "("),
        Token(T.NUMBER, "3", value=3.0),
        Token(T.RIGHT_PAREN, ")"),
        Token(T.SEMICOLON, ";"),
        Token(T.EOF, ""),
    ]


def test_field_access(tokenizer):
    tokens = tokenizer.tokenize("r.name")

    assert tokens == [
        Token(T.IDENTIFIER, "r"),
        Token(T.DOT, "."),
        Token(T.IDENTIFIER, "name"),
        Token(T.EOF, ""),
    ]


def test_inheritance_colon(tokenizer):
    tokens = tokenizer.tokenize("Class SpeedRobot : Robot")

    assert tokens == [
        Token(T.CLASS, "Class"),
        Token(T.IDENTIFIER, "SpeedRobot"),
        Token(T.COLON, ":"),
        Token(T.IDENTIFIER, "Robot"),
        Token(T.EOF, ""),
    ]


# ===== function 관련 토큰 =====


def test_func_declaration(tokenizer):
    tokens = tokenizer.tokenize("Func add(a, b)")

    assert tokens == [
        Token(T.FUNC, "Func"),
        Token(T.IDENTIFIER, "add"),
        Token(T.LEFT_PAREN, "("),
        Token(T.IDENTIFIER, "a"),
        Token(T.COMMA, ","),
        Token(T.IDENTIFIER, "b"),
        Token(T.RIGHT_PAREN, ")"),
        Token(T.EOF, ""),
    ]


def test_return_statement(tokenizer):
    tokens = tokenizer.tokenize("return a + b")

    assert tokens == [
        Token(T.RETURN, "return"),
        Token(T.IDENTIFIER, "a"),
        Token(T.PLUS, "+"),
        Token(T.IDENTIFIER, "b"),
        Token(T.EOF, ""),
    ]


# ===== class 관련 토큰 =====


def test_class_declaration(tokenizer):
    tokens = tokenizer.tokenize("Class Robot { }")

    assert tokens == [
        Token(T.CLASS, "Class"),
        Token(T.IDENTIFIER, "Robot"),
        Token(T.LEFT_BRACE, "{"),
        Token(T.RIGHT_BRACE, "}"),
        Token(T.EOF, ""),
    ]


def test_this_field_access(tokenizer):
    tokens = tokenizer.tokenize("This.position")

    assert tokens == [
        Token(T.THIS, "This"),
        Token(T.DOT, "."),
        Token(T.IDENTIFIER, "position"),
        Token(T.EOF, ""),
    ]


def test_super_call(tokenizer):
    tokens = tokenizer.tokenize("Super.move(dist)")

    assert tokens == [
        Token(T.SUPER, "Super"),
        Token(T.DOT, "."),
        Token(T.IDENTIFIER, "move"),
        Token(T.LEFT_PAREN, "("),
        Token(T.IDENTIFIER, "dist"),
        Token(T.RIGHT_PAREN, ")"),
        Token(T.EOF, ""),
    ]


def test_instanceof_operator(tokenizer):
    tokens = tokenizer.tokenize("w instanceof Robot")

    assert tokens == [
        Token(T.IDENTIFIER, "w"),
        Token(T.INSTANCEOF, "instanceof"),
        Token(T.IDENTIFIER, "Robot"),
        Token(T.EOF, ""),
    ]


# ===== import 관련 토큰 =====


def test_import_alias(tokenizer):
    tokens = tokenizer.tokenize('import "sum.txt" alias sum')

    assert tokens == [
        Token(T.IMPORT, "import"),
        Token(T.STRING, '"sum.txt"', value="sum.txt"),
        Token(T.ALIAS, "alias"),
        Token(T.IDENTIFIER, "sum"),
        Token(T.EOF, ""),
    ]


# ===== line 번호 추적 =====


def test_single_line(tokenizer):
    tokens = tokenizer.tokenize("age = 37")

    assert [token.line for token in tokens] == [1, 1, 1, 1]


def test_two_line(tokenizer):
    tokens = tokenizer.tokenize("var a = 1;\nvar b = 2;")

    lines = [token.line for token in tokens]

    assert lines == [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2]


def test_two_line_with_string(tokenizer):
    tokens = tokenizer.tokenize('var a = "hi";\nvar b = 1;')

    assert tokens[3].origin == '"hi"'
    assert tokens[3].line == 1
    assert tokens[5].line == 2


def test_multiple_new_line(tokenizer):
    tokens = tokenizer.tokenize("a;\n\nb;")

    lines = [token.line for token in tokens]

    assert lines == [1, 1, 3, 3, 3]


def test_start_new_line(tokenizer):
    tokens = tokenizer.tokenize("\n\nvar a=1")

    lines = [token.line for token in tokens]

    assert lines == [3, 3, 3, 3, 3]


def test_new_line_implied(tokenizer):
    tokens = tokenizer.tokenize("""var a = 1;
var b = 2;""")

    lines = [token.line for token in tokens]

    assert lines == [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2]


def test_backslash_in_string_not_allowed(tokenizer):
    with pytest.raises(ValueError, match="Backslash is not allowed"):
        tokenizer.tokenize(r'var a = "hi\n world"')
