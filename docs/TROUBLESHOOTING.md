# Troubleshooting

이 문서는 PR 리뷰 댓글이 실제 결함이나 누락을 발견했고, 그 뒤 후속 커밋이나 후속 PR로 반영된 사례를 기준으로
정리한다. 단순 질문, 설계 의도 확인, 승인 코멘트, Codecov/Actions 알림만으로 끝난 항목은 제외했다.

Actions 실패는 보조 신호로만 본다. 이 문서의 중심은 "리뷰에서 작성자가 놓친 문제가 발견됐는가"와 "그 발견이
어떤 수정으로 이어졌는가"이다.

## 빠른 분류표

| 증상 | 리뷰에서 발견한 지점 | 반영 흐름 |
| --- | --- | --- |
| 정상 AST가 checker에서 `Unknown statement type`으로 실패 | 새 `Stmt`/`Expr`가 resolver에 등록되지 않음 | PR #22, #45, #50 후속 반영 |
| 분기나 반복문 뒤 미초기화 변수를 놓침 | `if`/`for`를 직선 흐름처럼 처리함 | PR #22 후속 커밋 |
| 함수나 method 선언만으로 outer scope가 바뀜 | 선언 시점 resolve가 실행 효과처럼 누수됨 | PR #52 리뷰 반영 |
| static binding 뒤 undefined variable 의미가 달라짐 | `get_at()`/`assign_at()`이 기존 runtime 계약을 보존하지 않음 | PR #43 리뷰 반영 |
| constant folding 중 checker가 예외로 터짐 | folding 실패가 원본 유지로 복구되지 않음 | PR #43 리뷰 반영 |
| runtime error가 테스트 helper 밖으로 샘 | Python `RuntimeError`가 `CodeFabRuntimeError` 경계를 우회함 | PR #14, #39, #41, #44 리뷰 반영 |
| 배열 index가 조용히 변환됨 | `int()` coercion이 `0.9`, `1.9`, 음수 길이를 숨김 | PR #45 리뷰 반영 |
| tokenizer는 되는데 parser/checker/executor가 뒤처짐 | 문법 확장이 파이프라인 전체 계약으로 검증되지 않음 | PR #19, #23, #26, #29 후속 반영 |
| debug/file mode 줄 번호가 틀림 | nested statement나 조건 평가 오류의 line 정보가 끊김 | PR #46, #51, #54 후속 반영 |

## Symptom: 정상 AST인데 checker가 `Unknown statement type`을 낸다

Likely cause:
새 AST 노드를 만들었지만 checker resolver dispatch에 등록하지 않았을 수 있다. PR #22에서는 `PrintStmt`가
resolver map에 없어 정상적인 출력문 AST가 `Unknown statement type`으로 이어질 수 있다는 리뷰가 있었다.
비슷하게 PR #45에서는 배열 index expression이 checker에 연결되지 않았고, PR #50에서는 `SuperExpr`와 알 수
없는 statement 처리 경계가 다시 확인됐다.

How to confirm:

- 새 `Stmt` 또는 `Expr` 타입이 `app/assembler/statement.py`나 `app/assembler/expr.py`에 추가됐는지 확인한다.
- 같은 타입이 checker resolver와 executor 처리 경로에 모두 들어갔는지 본다.
- 해당 노드를 직접 포함하는 최소 코드나 AST 테스트를 만든다.

Resolution:
AST 노드를 추가할 때 "assembler가 만든다", "checker가 읽는다", "executor/debugger가 실행한다"를 하나의
계약으로 확인한다.

Prevention:
새 문법 PR에는 AST 생성 테스트만 두지 말고 checker와 executor까지 지나는 대표 예제를 포함한다.

## Symptom: `if` 또는 `for` 뒤에 미초기화 변수를 놓친다

Likely cause:
control flow를 하나의 직선 흐름처럼 처리했을 수 있다. PR #22 리뷰에서는 `if`의 then/else를 독립 경로로
검사하고, 두 경로 모두에서 초기화된 변수만 이후에 initialized로 봐야 한다는 점이 지적됐다. `for` body는
0번 실행될 수 있으므로 body 내부 대입을 무조건 이후 상태로 믿으면 안 된다.

How to confirm:

```txt
var a;
if (cond) {
  a = 1;
} else {
  print a;
}
```

```txt
var a;
for (var i = 0; i < 0; i = i + 1) {
  a = 1;
}
print a;
```

Resolution:
분기별 `ScopeStack` 상태를 분리하고 merge 시 보수적으로 합친다. loop는 initializer, condition, body,
increment가 서로 다른 실행 가능성을 갖는다는 점을 반영한다.

Prevention:
checker 테스트에는 then-only 초기화, else-only 초기화, loop 0회 실행, body와 increment 순서 반례를 넣는다.

## Symptom: 함수나 method 선언만 했는데 바깥 변수 초기화 상태가 바뀐다

Likely cause:
function/method body를 선언 시점에 resolve하면서 body 안의 대입 효과가 outer scope에 누수됐을 수 있다.
PR #52 리뷰에서는 method body 안의 `a = 1`이 class 선언 이후 top-level의 `a`를 초기화한 것처럼 보이는
문제가 발견됐다. 함수와 method body는 선언될 뿐, 그 자리에서 실행되지 않는다.

How to confirm:

```txt
var a;
Class C {
  m() {
    a = 1;
  }
}
print a;
```

반대로 아래처럼 선언 뒤 runtime에서 초기화될 수 있는 값을 선언 시점에 오탐하는지도 확인한다.

```txt
var a;
Class C {
  m() {
    print a;
  }
}
a = 1;
```

Resolution:
callable body를 resolve할 때 enclosing scope의 실행 효과와 body 내부 흐름을 분리한다.

Prevention:
class/function checker PR에는 "body 내부 대입이 outer scope를 오염시키지 않음", "선언 후 초기화 가능 값 오탐
없음", "nested function도 enclosing function local 상태를 오염시키지 않음"을 테스트한다.

## Symptom: static binding 최적화 뒤 undefined variable 의미가 달라진다

Likely cause:
`distance` 기반 `get_at()`/`assign_at()`이 기존 dynamic `get()`/`assign()`과 다른 오류 의미를 가질 수 있다.
PR #43 리뷰에서는 `assign_at()`이 target environment에 이름이 없어도 새 key를 만들어 local initializer 안의
자기 대입이 기존 runtime error를 우회할 수 있다는 점이 발견됐다.

How to confirm:

```txt
{
  var a = a = 1;
}
```

Resolution:
`get_at()`과 `assign_at()`도 target environment에 이름이 없으면 `CodeFabRuntimeError`를 내도록 dynamic 경로와
의미를 맞춘다.

Prevention:
최적화 PR은 성능이나 구조뿐 아니라 기존 오류 의미가 유지되는지 확인한다.

## Symptom: constant folding 때문에 checker 자체가 예외로 터진다

Likely cause:
constant folding은 checker 단계에서 literal expression을 미리 평가한다. 이때 evaluator 내부 예외가 그대로
새면 "fold 실패 시 원본 expression 유지"라는 계약이 깨진다. PR #43 리뷰에서는 boolean/string 비교 중 내부
예외가 checker로 새는 사례가 발견됐다.

How to confirm:

```txt
print "a" == "a";
print true == false;
```

Resolution:
literal 비교의 타입 검사를 executor 의미와 맞추고, constant folder는 fold할 수 없는 expression을 원본으로
남겨야 한다.

Prevention:
constant folding 테스트는 "fold 가능", "fold 불가라 원본 유지", "runtime error 후보지만 checker는 터지지
않음"을 나눠서 둔다.

## Symptom: runtime error가 acceptance helper 밖으로 샌다

Likely cause:
CodeFab 실행 오류가 Python `RuntimeError`나 일반 `Exception`으로 던져지면 acceptance helper와 shell이
프로젝트의 오류 형식으로 다루지 못한다. PR #14에서는 이름 충돌 때문에 `RuntimeError`가 `CodeFabRuntimeError`로
정리됐고, PR #39와 #44에서는 callable/class runtime error가 같은 경계로 들어오도록 고쳐졌다. PR #41에서는
`CodeFabRuntimeError`가 기존 `RuntimeError` 기대와도 호환되도록 상속 구조가 조정됐다.

How to confirm:

```txt
print 1();
```

```txt
Class Robot {}
var r = Robot();
print r.missing;
```

Resolution:
사용자 코드에서 발생하는 runtime 문제는 `CodeFabRuntimeError`로 통일한다.

Prevention:
새 runtime 기능 PR에는 "잘못된 호출", "잘못된 property", "잘못된 operand"처럼 실패 경로 acceptance 테스트를
같이 둔다.

## Symptom: 배열 index 오류가 조용히 정상 값처럼 바뀐다

Likely cause:
`int()` coercion이 `arr[0.9]`를 `arr[0]`처럼 만들거나, `Array(1.9)`를 길이 1 배열처럼 만들 수 있다.
PR #45 리뷰에서는 이 변환이 사용자 오류를 숨긴다는 점이 발견됐다. 같은 PR에서 배열 expression이 checker에
등록되지 않아 index 내부의 미초기화 변수도 놓칠 수 있다는 후속 과제가 생겼고, 이후 checker 보강으로 이어졌다.

How to confirm:

```txt
var arr = Array(2);
print arr[0.9];
var bad = Array(-1);
```

Resolution:
배열 길이와 index는 정수인지, 음수가 아닌지, 범위 안인지 명시적으로 검사한다.

Prevention:
배열 기능 테스트에는 정상 index뿐 아니라 float index, 음수 길이, 범위 초과, index expression 내부 checker
오류를 포함한다.

## Symptom: tokenizer는 통과하지만 parser나 checker에서 뒤늦게 깨진다

Likely cause:
문법 확장이 token 추가에서 끝나고 parser/checker/executor 계약까지 이어지지 않았을 수 있다. PR #19 리뷰에서는
`a!=b`, `a==b`, `a>=b`, `a<=b`처럼 공백 없는 복합 연산자와 `format`, `before`, `for1`처럼 keyword를 포함한
identifier 반례가 추가됐다. PR #23, #26, #29 리뷰에서는 string/boolean literal과 comparison/equality parsing,
`PrintStmt` 내부 expression resolve가 파이프라인 전체에서 맞물려야 한다는 점이 확인됐다.

How to confirm:

```txt
print true == false;
print "a" != "b";
var format = 1;
print format >= 1;
```

Resolution:
tokenizer, parser, checker, executor를 각각 따로 통과했다고 보지 말고 한 문장 예제가 끝까지 실행되는지 본다.

Prevention:
keyword나 operator PR에는 공백 없는 입력, keyword-like identifier, literal별 parsing, checker resolve,
runtime 결과를 함께 확인한다.

## Symptom: file/debug mode에서 줄 번호가 없거나 틀리다

Likely cause:
Tokenizer, AST statement, runtime error 사이에 line 정보가 끊겼거나 debug frame이 nested statement의 실제
실행 위치를 잃었을 수 있다. PR #46 리뷰에서는 nested statement의 runtime error가 top-level 줄 번호로
보고되는 문제와 debug mode의 `if` condition 오류 line 문제가 발견됐다. PR #51에서는 shell `ctrlc`/`ctrlv`
테스트가 line/index 초기화 제거 때문에 깨진 점이 확인됐고, PR #54에서는 `for` loop 안쪽 statement까지
breakpoint와 step이 들어가도록 보강됐다.

How to confirm:

```txt
print 1;
if (true) {
  print 10 / 0;
}
```

debug mode에서는 loop body line에 breakpoint를 걸어 본다.

```txt
var total = 0;
for (var i = 0; i < 3; i = i + 1) {
  total = total + i;
  print total;
}
```

Resolution:
parser가 statement 생성 시 시작 token의 line을 넘기고, debug frame은 block/if/for 내부 statement를 독립적으로
추적한다.

Prevention:
새 statement 타입을 추가할 때 file mode error line과 debug mode `step`, `next`, `continue`, `break`, `watch`
동작을 같이 확인한다.

## Symptom: 리뷰 코멘트를 문서에 넣어도 되는지 애매하다

Likely cause:
모든 댓글이 troubleshooting 사례는 아니다. 예를 들어 "왜 이렇게 구조를 바꿨는가" 같은 질문은 설계 설명에는
도움이 되지만, 작성자가 놓친 결함을 발견한 것은 아니다.

How to confirm:

- 댓글 뒤에 실제 수정 커밋이 있었는가?
- 댓글이 이후 PR에서 기능 보강이나 테스트 추가로 이어졌는가?
- Actions 실패가 있었다면, 실패 자체가 아니라 원인과 수정이 확인됐는가?

Resolution:
위 세 질문 중 하나라도 명확히 답할 수 있는 항목만 troubleshooting에 넣는다.

Prevention:
향후 PR 리뷰를 정리할 때는 "질문", "설계 논의", "결함 발견", "후속 커밋 반영", "후속 PR 반영"을 분리해서
기록한다.
