import pytest

from app.assembler.assembler import Assembler, AssemblerError
from app.assembler.tokenizer import Tokenizer
from app.checker.checker import Checker
from app.exceptions import CodeFabRuntimeError
from app.executor.executor import Executor


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


# This/Super는 실제 executor 바인딩이 소스에 쓰인 alias origin(나야/부모 등)과 무관하게
# 고정 키("This"/"Super")로 저장되어 있어야 한다. 예전에는 environment.get(expr.keyword)가
# 별칭의 origin으로 조회해서 `Undefined variable '나야'` 같은 런타임 에러가 났었다.
ALIAS_ACCEPTANCE_CASES = [
    (
        "this_original",
        """
        Class Robot {
          setName(n) {
            This.name = n;
          }
          greet() {
            print This.name;
          }
        }

        var r = Robot();
        r.setName("SpeedRobot");
        r.greet();
        """,
        ["SpeedRobot"],
    ),
    (
        "this_alias",
        """
        클래스 Robot {
          setName(n) {
            나야.name = n;
          }
          greet() {
            보여줘 나야.name;
          }
        }

        값 r = Robot();
        r.setName("SpeedRobot");
        r.greet();
        """,
        ["SpeedRobot"],
    ),
    (
        "super_original",
        """
        Class Animal {
          speak() {
            print "sound";
          }
        }

        Class Dog: Animal {
          speak() {
            Super.speak();
            print "bark";
          }
        }

        var dog = Dog();
        dog.speak();
        """,
        ["sound", "bark"],
    ),
    (
        "super_alias",
        """
        클래스 Animal {
          speak() {
            보여줘 "sound";
          }
        }

        붕어빵틀 Dog: Animal {
          speak() {
            부모.speak();
            보여줘 "bark";
          }
        }

        값 dog = Dog();
        dog.speak();
        """,
        ["sound", "bark"],
    ),
    (
        "this_and_super_alias_mixed_with_original",
        """
        Class Animal {
          speak() {
            print "sound";
          }
        }

        클래스 Dog: Animal {
          speak() {
            엄빠.speak();
            print "bark";
          }
        }

        var dog = Dog();
        dog.speak();
        """,
        ["sound", "bark"],
    ),
]


@pytest.mark.parametrize(
    ("name", "source", "expected"),
    ALIAS_ACCEPTANCE_CASES,
    ids=[case[0] for case in ALIAS_ACCEPTANCE_CASES],
)
def test_this_super_alias_acceptance(name, source, expected):
    output, errors = run_source(source)

    assert errors == [], name
    assert output == expected
