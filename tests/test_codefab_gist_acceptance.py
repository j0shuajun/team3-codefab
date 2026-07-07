import pytest

from assembler.assembler import Assembler, AssemblerError
from assembler.tokenizer import Tokenizer
from checker.checker import Checker
from executor.executor import CodeFabRuntimeError, Executor


def run_source(source):
    try:
        tokens = Tokenizer().tokenize(source)
        statements = Assembler(tokens).parse()
    except (ValueError, AssemblerError) as error:
        return [], [str(error)]

    errors = Checker().check(statements)
    if errors:
        return [], errors

    executor = Executor()
    try:
        executor.execute(statements)
    except CodeFabRuntimeError as error:
        return [], [str(error)]

    return executor.outputs, []


ACCEPTANCE_OUTPUT_CASES = [
    ("arithmetic_precedence", "print 1 + 2 * 3;", ["7"]),
    ("grouping_precedence", "print (1 + 2) * 3;", ["9"]),
    ("left_associative_subtraction", "print 10 - 4 - 3;", ["3"]),
    ("left_associative_division", "print 8 / 2 / 2;", ["2"]),
    ("unary_minus_with_addition", "print -3 + 2;", ["-1"]),
    ("less_than", "print 1 < 2;", ["true"]),
    ("greater_than", "print 3 > 5;", ["false"]),
    ("string_concatenation", 'print "Hello, " + "CodeFab!";', ["Hello, CodeFab!"]),
    ("integer_format", "print 5;", ["5"]),
    ("float_integer_format", "print 5.0;", ["5"]),
    ("float_fraction_format", "print 3.14;", ["3.14"]),
    ("true_literal", "print true;", ["true"]),
    ("false_literal", "print false;", ["false"]),
    (
        "variables_and_addition",
        """
        var a = 10;
        var b = 20;
        print a + b;
        """,
        ["30"],
    ),
    (
        "reassignment",
        """
        var a = 10;
        a = a + 5;
        print a;
        """,
        ["15"],
    ),
    (
        "block_shadowing",
        """
        var x = "global";
        {
          var x = "inner";
          print x;
        }
        print x;
        """,
        ["inner", "global"],
    ),
    (
        "outer_assignment_from_block",
        """
        var count = 0;
        {
          count = count + 1;
        }
        print count;
        """,
        ["1"],
    ),
    (
        "nested_scope_resolution",
        """
        var outer = "A";
        {
          var inner = "B";
          {
            print outer + inner;
          }
        }
        """,
        ["AB"],
    ),
    ("if_then", 'if (true) print "bbq";', ["bbq"]),
    ("if_else", 'if (false) print "no"; else print "kfc";', ["kfc"]),
    (
        "dangling_else",
        """
        if (true)
        {
          if (false) print "kfc";
          else print "bbq";
        }
        """,
        ["bbq"],
    ),
    (
        "for_loop",
        "for (var j = 0; j < 3; j = j + 1) { print j; }",
        ["0", "1", "2"],
    ),
]

ACCEPTANCE_ERROR_CASES = [
    ("missing_semicolon", "print 1 + 2", "Expected ';' after value."),
    ("missing_right_paren", "print (1 + 2;", "Expected ')' after expression."),
    (
        "invalid_assignment_target",
        """
        var a = 1;
        var b = 2;
        a + b = 3;
        """,
        "Invalid assignment target.",
    ),
    ("missing_expression", "print * 5;", "Expected expression."),
    ("self_reference_initializer", "{ var a = a; }", "initialization"),
    (
        "duplicate_local_declaration",
        '{ var a = "hi"; var a = 3; }',
        "already declared",
    ),
    ("undefined_variable", "print notDefined;", "Undefined variable 'notDefined'."),
    (
        "mixed_plus_operands",
        'print 1 + "HI";',
        "Operands must be two numbers or two strings.",
    ),
    ("unary_minus_string", 'print -"FabCoding";', "Operand must be a number."),
]


@pytest.mark.parametrize(
    ("name", "source", "expected"),
    ACCEPTANCE_OUTPUT_CASES,
    ids=[case[0] for case in ACCEPTANCE_OUTPUT_CASES],
)
def test_gist_output_case(name, source, expected):
    output, errors = run_source(source)

    assert errors == [], name
    assert output == expected


@pytest.mark.parametrize(
    ("name", "source", "expected_error"),
    ACCEPTANCE_ERROR_CASES,
    ids=[case[0] for case in ACCEPTANCE_ERROR_CASES],
)
def test_gist_error_case(name, source, expected_error):
    output, errors = run_source(source)

    assert output == [], name
    assert any(expected_error in error for error in errors), errors
