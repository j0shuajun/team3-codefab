# CodeFab custom language

이 문서는 CodeFab 언어를 어떻게 쓰는지 설명한다. GitHub issue #12의 ideation에서는 이모티콘,
한글 keyword, `ctrl c` 기능이 후보로 나왔고, 현재 구현에는 그중 prompt shell의 `ctrlc`/`ctrlv`
추천 흐름이 프로젝트 고유 기능으로 반영되어 있다.

## 언어의 현재 방향

CodeFab은 "작게 시작해 언어 구성요소를 직접 구현해보는" 학습형 언어다. 문법은 Lox 계열과 비슷하지만,
팀 프로젝트의 실험 기능이 조금씩 붙어 있다.

- 변수, 조건문, 반복문으로 기본 흐름을 만든다.
- 함수와 클래스로 코드를 묶는다.
- 배열과 property 접근으로 상태를 다룬다.
- prompt shell의 `ctrlc`/`ctrlv`로 자주 쓰는 명령을 다시 실행한다.
- debug mode에서 줄 단위 실행과 watch를 관찰한다.

## 빠른 예시

```txt
var total = 0;

for (var i = 0; i < 3; i = i + 1) {
  total = total + i;
}

print total;
```

예상 출력:

```txt
3
```

## 기본 문법

### 값과 출력

```txt
print 1 + 2;
print "Code" + "Fab";
print true;
```

- 숫자는 내부적으로 `float`로 읽지만, 정수값이면 `1`처럼 출력한다.
- 문자열끼리는 `+`로 연결할 수 있다.
- 숫자와 문자열을 섞어 더하면 런타임 오류다.

### 변수

```txt
var name = "CodeFab";
print name;

name = "Ctrl-C";
print name;
```

같은 스코프에서 같은 이름을 다시 선언하면 checker가 오류로 잡는다.

### 조건문

```txt
var score = 90;

if (score >= 80) {
  print "pass";
} else {
  print "retry";
}
```

### 반복문

```txt
for (var i = 0; i < 3; i = i + 1) {
  print i;
}
```

Debug mode에서는 `for` 전체가 한 번에 지나가지 않고 body 안쪽 statement까지 step으로 들어갈 수 있다.

## 함수

```txt
Func addOne(x) {
  return x + 1;
}

print addOne(10);
```

함수는 parameter 개수와 호출 인자 수가 맞아야 한다. 함수 밖에서 `return`을 쓰거나 parameter 이름을 중복하면
checker가 오류로 보고한다.

## 배열

```txt
var arr = Array(3);
arr[0] = "first";
arr[1] = "second";

print arr[0];
```

주의할 점:

- `Array(size)`의 size는 0 이상의 정수여야 한다.
- 배열이 아닌 값에 `value[index]`를 쓰면 오류다.
- index는 정수 숫자여야 하며 범위를 벗어나면 오류다.

## 클래스와 상속

```txt
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

지원되는 개념:

- `Class` 선언
- method 호출
- `This`로 현재 인스턴스 접근
- `Super.method()`로 부모 method 접근
- `instanceof`로 인스턴스와 클래스 관계 확인

checker가 막는 대표 사례:

- 클래스 밖에서 `This` 사용
- 부모 클래스가 없는데 `Super` 사용
- 클래스가 자기 자신을 상속
- `init`에서 값을 반환

## Prompt shell 특화 기능

Issue #12의 `ctrl c 기능` 아이디어는 prompt shell 안의 명령으로 구현되어 있다.

```txt
CodeFab> print 36;
36
CodeFab> print 36;
36
CodeFab> ctrlc
Ctrl+C 추천 명령어: print 36;
ctrlv 를 입력하면 추천 명령어를 다시 실행합니다.
CodeFab> ctrlv
36
```

여기서 `ctrlc`와 `ctrlv`는 키보드 단축키가 아니라 shell에 입력하는 문자열 명령이다.

## 실행 방법

| 하고 싶은 일 | 명령 |
|---|---|
| 한 줄씩 실행 | `make run` |
| 파일 실행 | `make run sample.cfab` |
| 디버그 실행 | `make debug sample.cfab` |

## 아직 ideation으로 남은 것

| 아이디어 | 현재 상태 | 다음에 정할 점 |
|---|---|---|
| 이모티콘 문법 | 미구현 | 토큰으로 읽을지, 표준 함수/별칭으로 둘지 결정 필요 |
| 한글 keyword | 미구현 | `출력`, `만약`, `반복` 같은 alias를 허용할지 결정 필요 |
| `ctrlc` 추천 | 구현됨 | 추천 기준을 빈도 외에 최근성/문맥까지 넓힐지 검토 가능 |

