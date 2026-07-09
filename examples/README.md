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

> 이 예제에는 `This`/`Super` 호출이 없어서 그 alias(`이것`/`나야`, `부모`/`엄빠`)는 예제로는 못 보여주지만, `tests/test_app_alias_this_super_acceptance.py`에서 실행까지 확인했습니다.

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
