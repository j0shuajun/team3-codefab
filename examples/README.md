# CodeFab examples

기능별로 나눈 CodeFab 예제 소스입니다. `make run <file>`로 실행합니다.

## 01. 변수, print

`01_variable_print.ctrlc`

```
var name = "CodeFab";
print name;

name = "Ctrl-C";
print name;

print 1 + 2;
print true;
```

`01_variable_print.ctrlc (alias)`

```
값 name = "CodeFab";
보여줘 name;

name = "Ctrl-C";
보여줘 name;

보여줘 1 + 2;
보여줘 참;
```

실행 결과:

```
CodeFab
Ctrl-C
3
true
```

## 02. if/else 조건문

`02_condition.ctrlc`

```
var score = 90;

if (score >= 80) {
  print "pass";
} else {
  print "retry";
}
```

`02_condition.ctrlc (alias)`

```
값 score = 90;

만약 (score 크거나같다 80) {
  보여줘 "pass";
} 아니면 {
  보여줘 "retry";
}
```

실행 결과:

```
pass
```

## 03. for 반복문

`03_loop.ctrlc`

```
var total = 0;

for (var i = 0; i < 3; i = i + 1) {
  total = total + i;
}

print total;
```

`03_loop.ctrlc (alias)`

```
값 total = 0;

반복 (값 i = 0; i 작다 3; i = i + 1) {
  total = total + i;
}

보여줘 total;
```

실행 결과:

```
3
```

## 04. Func 선언, return, 함수 호출

`04_function.ctrlc`

```
Func addOne(x) {
  return x + 1;
}

print addOne(10);
```

`04_function.ctrlc (alias)`

```
펑펑 addOne(x) {
  돌려줘 x + 1;
}

보여줘 addOne(10);
```

실행 결과:

```
11
```

## 05. Class, 상속, instanceof

`05_class_inheritance.ctrlc`

```
Class Animal {
  speak() {
    print "sound";
  }
}

Class Dog: Animal {
  speak() {
    print "bark";
  }
}

var dog = Dog();
dog.speak();
print dog instanceof Dog;
```

`05_class_inheritance.ctrlc (alias)`

```
클래스 Animal {
  speak() {
    보여줘 "sound";
  }
}

붕어빵틀 Dog: Animal {
  speak() {
    보여줘 "bark";
  }
}

값 dog = Dog();
dog.speak();
보여줘 dog instanceof Dog;
```

실행 결과:

```
bark
true
```

> 이 예제는 `Class`/상속/`instanceof`에 집중한 예제라 `This`/`Super`를 직접 쓰지 않습니다. 실제 사용은 12번 예제에서 보여줍니다.

## 06. Array(size), index get/set

`06_array.ctrlc`

```
var arr = Array(3);
arr[0] = "first";
arr[1] = "second";

print arr[0];
print arr[1];
```

`06_array.ctrlc (alias)`

```
값 arr = Array(3);
arr[0] = "first";
arr[1] = "second";

보여줘 arr[0];
보여줘 arr[1];
```

실행 결과:

```
first
second
```

## 07. Checker가 실행 전에 잡는 오류

`07_checker_error.ctrlc` (같은 스코프에 변수를 중복 선언 → 의도적으로 오류를 냄)

```
var a = 1;
var a = 2;
print a;
```

`07_checker_error.ctrlc (alias)`

```
값 a = 1;
값 a = 2;
보여줘 a;
```

실행 결과:

```
Variable 'a' already declared in this scope.
```

## 08. 커스텀 내장 함수 `ctrl_c()`

`08_ctrl_c.ctrlc`

```
print 36;
ctrl_c();
```

실행 결과는 지면에 옮기기엔 너무 화려합니다 (색상 + 이모지로 꾸며진 팀 소개 박스가 통째로 출력됩니다). 직접 실행해서 확인해보세요:

```
make run examples/08_ctrl_c.ctrlc
```

(`36`이 먼저 찍히고, 이어서 팀명/팀원/역할/한 줄 소감이 담긴 표가 출력됩니다. 콘솔이 cp949 등 non-UTF-8 인코딩이면 이모지 때문에 `UnicodeEncodeError`가 날 수 있으니, 그럴 땐 `PYTHONIOENCODING=utf-8 make run examples/08_ctrl_c.ctrlc`로 실행하세요.)

## 09. import

`09_import_lib.ctrlc` (불러올 모듈)

```
var pi = 3.14;

Func add(a, b) {
  return a + b;
}
```

`09_import.ctrlc` (진입점 — import 경로는 이 파일 자신의 위치를 기준으로 한 상대 경로)

```
import "09_import_lib.ctrlc" alias lib;

print lib.pi;
print lib.add(1, 2);
```

실행 결과:

```
3.14
3
```

## 10. `♡` 이름 궁합 연산자

`10_name_compatibility.ctrlc`

```
print "김철수" ♡ "이영희";
```

실행 결과:

```
57
```

두 문자열의 각 글자 초성/중성/종성 획수를 엇갈려 더해가며 두 자리 숫자로 줄이는 손가락 이름궁합 계산 방식입니다 (`app/custom_function/name_compatibility.py`).

## 11. and/or 논리 연산자

`11_logical.ctrlc`

```
var a = true;
var b = false;

print a and b;
print a or b;
```

`11_logical_alias.ctrlc`

```
값 a = 참;
값 b = 거짓;

보여줘 a 그리고 b;
보여줘 a 또는 b;
```

실행 결과:

```
false
true
```

## 12. This/Super 실제 사용 (필드 접근 + 부모 method 호출)

`12_this_super.ctrlc`

```
Class Robot {
  init(name) {
    This.name = name;
  }
  greet() {
    print This.name;
  }
}

var r = Robot("Bolt");
r.greet();

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
```

`12_this_super_alias.ctrlc`

```
클래스 Robot {
  init(name) {
    나야.name = name;
  }
  greet() {
    보여줘 나야.name;
  }
}

값 r = Robot("Bolt");
r.greet();

클래스 Animal {
  speak() {
    보여줘 "sound";
  }
}

붕어빵틀 Dog: Animal {
  speak() {
    엄빠.speak();
    보여줘 "bark";
  }
}

값 dog = Dog();
dog.speak();
```

실행 결과:

```
Bolt
sound
bark
```

## 13. Checker 오류 — 초기화 전 사용

`13_checker_error_uninitialized.ctrlc`

```
{
  var a = a;
}
```

실행 결과:

```
Variable 'a' is used before initialization.
```

## 14. Checker 오류 — 클래스 밖에서 This 사용

`14_checker_error_this_outside_class.ctrlc`

```
print This;
```

실행 결과:

```
Cannot use 'This' outside of a class.
```

## 15. 실행 중 오류 — 함수 인자 개수 불일치

`15_runtime_error_function_arity.ctrlc`

```
Func add(a, b) {
  return a + b;
}

print add(1);
```

실행 결과:

```
Error at line 5: Expected 2 arguments but got 1.
```

## 16. 실행 중 오류 — Array 크기가 음수

`16_array_negative_size_error.ctrlc`

```
var arr = Array(-1);
```

실행 결과:

```
Error at line 1: Array size must not be negative.
```

## 17. 실행 중 오류 — Array index 범위 초과

`17_array_out_of_range_error.ctrlc`

```
var arr = Array(2);
print arr[5];
```

실행 결과:

```
Error at line 2: Array index out of range.
```

## 부록. 디버그 모드

`debug_test.ctrlc` — `make debug <file>`로 실행하면 줄 단위 실행/breakpoint/watch를 확인할 수 있습니다.

```
var a = 3;
var b = a + 1;
print a + b;
```

실행 결과 (`make run`/`make debug` 공통):

```
7
```

## 부록. prompt shell 전용 기능 (`ctrlc`/`ctrlv`, `explain`)

이 두 기능은 `.ctrlc` 파일로 만들 수 없습니다 — 파일을 실행하는 게 아니라, `make run`으로 들어가는 prompt shell 안에서 직접 입력하는 명령이기 때문입니다.

```
make run
> print 36;
36
> print 36;
36
> print 35;
35
> ctrlc
Ctrl+C 추천 명령어: print 36;
ctrlv 를 입력하면 추천 명령어를 다시 실행합니다.
> ctrlv
36
```

- `ctrlc`: 지금까지 입력한 명령 중 가장 많이 쓴 것(동률이면 가장 최근 것)을 추천만 하고, 바로 실행하지는 않습니다.
- `ctrlv`: `ctrlc`가 추천한 명령을 그대로 실행합니다.
- `explain <code>`: 코드 한 줄을 토큰 → AST → checker → 실행 결과 순서로 보여줍니다.

```
make run
> explain print 1 + 2 * 3;
[Tokens]
PRINT NUMBER PLUS NUMBER STAR NUMBER SEMICOLON EOF

[AST]
PrintStmt(BinaryExpr(LiteralExpr(1.0), +, BinaryExpr(LiteralExpr(2.0), *, LiteralExpr(3.0))))

[Checker]
No errors

[Result]
[Output]
7
```
