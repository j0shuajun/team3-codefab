# CodeFab custom language

이 문서는 CodeFab 언어를 어떻게 쓰는지 설명한다. GitHub issue #12의 ideation에서는 이모티콘,
한글 keyword, `ctrl c` 기능이 후보로 나왔다. 현재 문서는 그중 `ctrl_c()`, `explain`, 한글 키워드 별칭을
CodeFab에서 사용할 기능으로 정리한다.

## 언어의 현재 방향

CodeFab은 "작게 시작해 언어 구성요소를 직접 구현해보는" 학습형 언어다. 문법은 Lox 계열과 비슷하지만,
팀 프로젝트에서 직접 설계한 기능이 조금씩 붙어 있다.

- 변수, 조건문, 반복문으로 기본 흐름을 만든다.
- 함수와 클래스로 코드를 묶는다.
- 배열과 property 접근으로 상태를 다룬다.
- CodeFab 코드 안에서 `ctrl_c()`를 호출해 Ctrl-C 팀원을 소개한다.
- `explain`으로 코드가 해석되는 흐름을 확인한다.
- 한글 키워드 별칭으로 더 친숙하게 코드를 작성한다.
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

## CodeFab 특화 기능

Issue #12의 `ctrl c 기능` 아이디어는 두 갈래로 구분해서 이해하는 편이 자연스럽다. prompt shell의 `ctrlc`와
`ctrlv`는 이전 입력을 바탕으로 명령을 추천하고 다시 실행하는 shell 기능이다. 반면 custom language의
`ctrl_c()`는 CodeFab 코드 안에서 호출하는 내장 함수이며, 팀 Ctrl-C와 팀원들을 소개하는 역할을 한다.

```txt
print 36;
ctrl_c();
```

예상되는 사용 방식:

- 사용자가 CodeFab 코드를 실행한다.
- `ctrl_c()`가 팀명, 팀 의미, 팀원 목록을 출력한다.
- 발표나 예제 코드에서 "우리 팀이 만든 custom language"라는 정체성을 보여준다.

예상 출력:

```txt
36
Ctrl-C: 서로의 강점을 복사해 함께 성장하는 팀
김명준, 권소영, 김민준, 박진우, 이예진
```

## 구현 중인 기능

| 기능 | 의도 | 예시 방향 |
|---|---|---|
| `ctrl_c()` | CodeFab 코드 안에서 Ctrl-C 팀 소개 | `ctrl_c();` |
| `explain` | 코드, 오류, 실행 흐름을 사람이 읽기 쉽게 설명 | `explain { print 1 + 2; }` 또는 유사 구문 |
| 한글 키워드 | 영어 키워드가 낯선 사용자도 읽기 쉽게 작성 | `출력`, `만약`, `반복`, `함수`, `클래스` 같은 alias |

세 기능은 문법과 사용자 경험이 아직 조정 중이다. 따라서 문서의 예시는 방향을 보여주는 것이며,
최종 token 이름이나 정확한 호출 형태는 구현 PR에서 확정한다.

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
| 한글 keyword | 구현 중 | 기존 영어 키워드와 alias를 같이 둘지, 한글 전용 흐름을 둘지 결정 필요 |
| `ctrl_c()` 팀 소개 | 구현 방향 확정 | 출력 문구와 팀원 표기 형식을 확정해야 함 |
| `explain` | 구현 중 | statement block을 받을지, 직전 실행 결과를 설명할지 결정 필요 |
