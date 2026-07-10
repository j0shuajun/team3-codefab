# CodeFab custom language

## 실행

| 목적 | 명령 |
|---|---|
| Prompt shell 실행 | `make run` |
| 파일 실행 | `make run examples/01_variable_print.ctrlc` |
| Debug mode 실행 | `make debug examples/debug_test.ctrlc` |

직접 실행할 때는 다음 명령을 사용할 수 있다.

```bash
python -m app.main
python -m app.main file examples/01_variable_print.ctrlc
python -m app.main debug examples/debug_test.ctrlc
```

## 기본 규칙

- 문장은 `;`로 끝낸다.
- 블록은 `{ ... }`로 묶는다.
- 조건식과 `for` 절은 `( ... )`로 감싼다.
- 문자열은 큰따옴표(`"`)로 감싼다.
- 문자열 안의 backslash(`\`)는 사용할 수 없다.
- 한글 alias를 포함한 소스 파일은 UTF-8로 저장한다.

## 값과 출력

```txt
print 1 + 2;
print "Code" + "Fab";
print true;
print false;
```

출력:

```txt
3
CodeFab
true
false
```

## 변수

```txt
var name = "CodeFab";
print name;

name = "Ctrl-C";
print name;
```

초깃값을 생략하면 `nil`이다.

```txt
var value;
print value;
```

출력:

```txt
nil
```

## 연산자

```txt
print 1 + 2 * 3;
print (1 + 2) * 3;
print 10 - 4 - 3;
print 8 / 2;
print -3 + 2;

print 1 < 2;
print 3 >= 5;
print 1 == 1;
print 1 != 2;
print !false;

print true and false;
print true or false;
```

출력:

```txt
7
9
3
4
-1
true
false
true
true
true
false
true
```

## 조건문

```txt
var score = 90;

if (score >= 80) {
  print "pass";
} else {
  print "retry";
}
```

## 반복문

```txt
var total = 0;

for (var i = 0; i < 3; i = i + 1) {
  total = total + i;
}

print total;
```

출력:

```txt
3
```

## 함수

```txt
Func addOne(x) {
  return x + 1;
}

print addOne(10);
```

출력:

```txt
11
```

## 내장 함수

### add(a, b)

```txt
print add(1, 2);
```

출력:

```txt
3
```

### Array(size)

```txt
var arr = Array(3);
arr[0] = "first";
arr[1] = "second";

print arr[0];
print arr[1];
```

출력:

```txt
first
second
```

`size`와 index는 정수 숫자여야 한다. 범위를 벗어난 index는 실행 오류다.

### ctrl_c()

```txt
print 36;
ctrl_c();
```

`ctrl_c()`는 Ctrl-C 팀 소개를 출력한다.

## 클래스

```txt
Class Robot {
  init(name) {
    This.name = name;
  }

  greet() {
    print This.name;
  }
}

var robot = Robot("Bolt");
robot.greet();
```

출력:

```txt
Bolt
```

## 상속

```txt
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
print dog instanceof Dog;
print dog instanceof Animal;
```

출력:

```txt
sound
bark
true
true
```

## import

불러올 파일에는 `import`, `var`, `Func`, `Class` 선언만 둘 수 있다.

`examples/09_import_lib.ctrlc`

```txt
var pi = 3.14;

Func add(a, b) {
  return a + b;
}
```

`examples/09_import.ctrlc`

```txt
import "09_import_lib.ctrlc" alias lib;

print lib.pi;
print lib.add(1, 2);
```

출력:

```txt
3.14
3
```

import 경로는 실행 파일 위치를 기준으로 해석된다.

## 이름 궁합 연산자

```txt
print "김철수" ♡ "이영희";
```

출력:

```txt
57
```

`♡`는 비어 있지 않은 한글 문자열 두 개에만 사용할 수 있다.

## Prompt shell 명령

Prompt shell은 `make run`으로 실행한다.

| 명령 | 사용법 |
|---|---|
| `exit` / `quit` | shell 종료 |
| `ctrlc` | 실행 기록에서 자주 쓴 CodeFab 명령 추천 |
| `ctrlv` | `ctrlc`가 추천한 명령 재실행 |
| `explain <code>` | token, AST, checker, 실행 결과 확인 |

예시:

```txt
CodeFab> print 36;
36
CodeFab> ctrlc
Ctrl+C 추천 명령어: print 36;
ctrlv 를 입력하면 추천 명령어를 다시 실행합니다.
CodeFab> ctrlv
36
```

```txt
CodeFab> explain print 1 + 2 * 3;
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

## Debug mode 명령

Debug mode는 `make debug <file>`로 실행한다.

| 명령 | 사용법 |
|---|---|
| `step` | 현재 문장을 실행하고 블록, 조건문, 반복문 안으로 들어감 |
| `next` | 현재 문장을 실행하되 블록 안으로 들어가지 않음 |
| `continue` | 다음 breakpoint 또는 프로그램 종료까지 실행 |
| `break <line>` | breakpoint 추가 |
| `breakpoints` | breakpoint 목록 출력 |
| `remove <line>` | breakpoint 제거 |
| `watch <name>` | 변수 감시 추가 |
| `unwatch <name>` | 변수 감시 제거 |
| `watches` | 감시 중인 변수 출력 |
| `inspect` | 현재 scope 변수 출력 |
| `exit` / `quit` | debug mode 종료 |

## 한글 alias

| 원본 | alias |
|---|---|
| `var` | `값`, `만들게` |
| `print` | `출력`, `보여줘`, `찍어줘` |
| `Func` | `함수`, `펑펑` |
| `return` | `반환`, `돌려줘` |
| `Class` | `클래스`, `틀`, `붕어빵틀` |
| `This` | `이것`, `나야` |
| `Super` | `부모`, `엄빠` |
| `if` | `만약`, `혹시` |
| `else` | `아니면` |
| `for` | `반복`, `또또` |
| `true` | `참`, `ㅇㅇ` |
| `false` | `거짓`, `ㄴㄴ` |
| `and` | `그리고`, `이랑` |
| `or` | `또는`, `이나` |
| `>` | `크다` |
| `<` | `작다` |
| `==` | `같다`, `똑같아` |
| `!=` | `다르다`, `달라` |
| `>=` | `크거나같다` |
| `<=` | `작거나같다` |

예시:

```txt
값 total = 0;

반복 (값 i = 0; i 작다 3; i = i + 1) {
  total = total + i;
}

보여줘 total;
```

출력:

```txt
3
```
