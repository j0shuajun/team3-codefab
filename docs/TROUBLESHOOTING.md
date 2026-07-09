# Troubleshooting

이 문서는 PR 리뷰와 코멘트에서 반복해서 나온 문제를 먼저 다룬다. GitHub Actions 실패는 중요한 신호지만,
대부분의 원인은 코드 계약, scope 흐름, 테스트 경계, 파일 경로 변경 같은 리뷰 논점에서 먼저 발견된다.

## Symptom: 정상 AST인데 checker가 `Unknown statement type`을 낸다

Likely cause:
새 `Stmt` 또는 `Expr` 타입을 추가했지만 resolver dispatch map에 등록하지 않았을 수 있다. PR #22 리뷰에서는
`PrintStmt`가 resolver map에 없어 정상 AST가 `CodeFabTypeError`로 이어질 수 있다는 코멘트가 있었다.

How to confirm:

- 새 노드 클래스가 `app/assembler/statement.py` 또는 `app/assembler/expr.py`에 추가됐는지 본다.
- 같은 타입이 `StatementResolver` 또는 `ExpressionResolver`의 처리 경로에 있는지 확인한다.
- 해당 노드가 들어간 최소 AST 테스트를 만든다.

Resolution:
새 AST 노드를 추가할 때 assembler, checker, executor 중 어느 단계가 그 노드를 읽어야 하는지 함께 등록한다.

Prevention:
문법을 추가하는 PR에는 "AST 노드 생성", "checker resolve", "executor evaluate/execute" 체크를 같이 둔다.

## Symptom: `if` 또는 `for` 뒤에 미초기화 변수를 놓친다

Likely cause:
분기와 반복문을 하나의 직선 흐름처럼 처리했을 수 있다. PR #22 리뷰에서는 `if`의 then/else를 독립 경로로
검사하고, merge 시 모든 경로에서 초기화된 변수만 initialized로 봐야 한다는 코멘트가 있었다. `for`도 body가
0번 실행될 수 있으므로 body 내부 초기화를 항상 믿으면 안 된다.

How to confirm:

```txt
var a;
if (cond) {
  a = 1;
} else {
  print a;
}
```

또는 다음처럼 loop body가 한 번도 실행되지 않을 수 있는 코드를 확인한다.

```txt
var a;
for (var i = 0; i < 0; i = i + 1) {
  a = 1;
}
print a;
```

Resolution:
`ScopeStack.snapshot()`/`restore()`를 사용해 경로별 상태를 분리하고, merge는 보수적으로 처리한다.

Prevention:
checker 변경에는 then-only 초기화, else-only 초기화, loop 0회 실행, increment/body 순서 반례를 테스트로 넣는다.

## Symptom: 함수나 method 선언만 했는데 바깥 변수 초기화 상태가 바뀐다

Likely cause:
함수나 method body를 선언 시점에 resolve하면서 body 안의 대입 효과가 바깥 `ScopeStack`에 누수됐을 수 있다.
PR #52 리뷰에서는 method body 안의 `a = 1`이 클래스 선언 이후 top-level의 `a`를 초기화한 것처럼 보이는
문제가 지적됐다. 함수와 method body는 선언 시점에 실행되지 않는다.

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

checker가 이 코드를 통과시키면 의심해야 한다. 반대로 아래처럼 런타임에서 나중에 초기화될 수 있는 값을
선언 시점에 오탐하는지도 확인한다.

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
function/method body resolve 전후로 enclosing scope snapshot을 복원하거나, callable body 내부의 flow effect가
선언 위치의 outer scope로 반영되지 않도록 분리한다.

Prevention:
class/function checker PR에는 "body 내부 대입이 outer scope를 오염시키지 않음", "선언 후 초기화 가능 값 오탐 없음",
"nested function도 enclosing function local 상태를 오염시키지 않음"을 테스트한다.

## Symptom: static binding 최적화 뒤 undefined variable 의미가 달라진다

Likely cause:
`distance` 기반 `get_at()`/`assign_at()`이 기존 dynamic `get()`/`assign()`과 다른 오류 의미를 가질 수 있다.
PR #43 리뷰에서는 `assign_at()`이 대상 scope에 이름이 없어도 새 key를 만들어 local initializer 안의 자기 대입이
기존 런타임 오류를 우회할 수 있다고 지적됐다.

How to confirm:

```txt
{
  var a = a = 1;
}
```

기존 의미라면 initializer 평가 시점에는 아직 `a`가 environment에 define되지 않았으므로 undefined variable
오류가 나야 한다.

Resolution:
`get_at()`과 `assign_at()`도 target environment에 이름이 없으면 `CodeFabRuntimeError`를 내도록 dynamic 경로와
의미를 맞춘다.

Prevention:
최적화 PR은 속도나 구조뿐 아니라 기존 오류 의미가 보존되는지 테스트한다.

## Symptom: constant folding 때문에 checker 자체가 예외로 터진다

Likely cause:
constant folding은 checker 단계에서 literal expression을 미리 평가한다. 이때 evaluator 내부의 예상 밖 예외가
그대로 새면 "fold 실패 시 원본 유지"라는 계약이 깨진다. PR #43 리뷰에서는 literal 비교 중 executor 내부
예외가 checker로 새어 나오는 사례가 지적됐다.

How to confirm:

```txt
print "a" == "a";
print true == false;
```

Resolution:
정상 literal 비교가 값 또는 `CodeFabRuntimeError`로 귀결되게 executor 타입 검사를 고치고, constant folder의
예외 경계도 방어적으로 둔다.

Prevention:
constant folding 테스트에는 "fold 가능", "fold 불가라 원본 유지", "런타임 오류 후보지만 checker는 터지지 않음"
세 종류를 포함한다.

## Symptom: 테스트 파일 이름을 바꿨는데 리뷰에서 이유를 묻는다

Likely cause:
PR #55처럼 `test_*`를 `test_app_*`로 바꾸면 단순 rename처럼 보여도 의도를 설명해야 한다. 이 프로젝트에서는
`docs`, `.github`처럼 CodeFab 런타임이 아닌 최상위 디렉터리도 함께 있으므로, 테스트 대상이 `app` 아래 코드임을
파일명에 드러내기 위해 prefix를 붙였다.

How to confirm:
테스트 파일명이 대상 모듈 경로를 설명하는지 확인한다.

```txt
app/assembler/tokenizer.py -> tests/test_app_assembler_tokenizer.py
app/shell/shell.py -> tests/test_app_shell_shell.py
```

Resolution:
파일명 변경 PR에는 naming rule과 예시를 PR 본문 또는 README에 같이 적는다.

Prevention:
테스트 파일명 규칙은 "나중에 디렉터리가 늘어나도 대상이 보이는가"를 기준으로 정한다.

## Symptom: Tokenizer가 커질수록 조건문이 복잡해진다

Likely cause:
토큰 종류가 늘어날 때마다 분기문을 추가하면 tokenizer가 읽기 어려워진다. PR #40 리뷰에서는 token value를
하나의 map으로 관리하는 방식이 더 깔끔하다는 코멘트가 있었다.

How to confirm:

- 새 keyword나 operator를 추가할 때 tokenizer 본문에 if/elif가 계속 늘어나는지 본다.
- `TokenType`과 tokenizer의 실제 문자열 매칭 정보가 중복 관리되는지 확인한다.

Resolution:
문자열과 token type의 대응은 가능한 한 `TokenType` 값과 `_TOKENS` map으로 통합한다.

Prevention:
새 token PR은 "TokenType 추가만으로 tokenizer matching이 자연스럽게 확장되는가"를 확인한다.

## Symptom: AST 노드에 문자열을 넣어도 되는지 Token을 넣어야 하는지 헷갈린다

Likely cause:
Issue #21과 PR #24에서 다룬 AST 계약 문제다. `VariableExpr.name`, `AssignExpr.name`, `VarStmt.name`,
operator field 등은 executor와 checker가 `Token.origin`, `Token.type`을 기대하는 경우가 많다.

How to confirm:
테스트에서 `VarStmt("a", ...)`처럼 문자열을 직접 넣고 있지 않은지 본다.

Resolution:
AST 생성 시 이름과 연산자는 `Token`을 전달한다. 테스트 helper가 필요하면 Token 생성 helper를 둔다.

Prevention:
AST 계약 변경은 checker와 executor 담당자가 함께 볼 수 있게 PR 설명에 노드별 field 의미를 적는다.

## Symptom: Debug mode에서 `for` loop가 한 번에 지나간다

Likely cause:
`ForStmt`를 일반 statement처럼 executor에 통째로 넘기면 반복문 내부 statement 단위로 멈출 수 없다.
PR #54에서 이 문제를 `DebugFrame` 기반 loop frame으로 해결했다.

How to confirm:
다음 파일을 debug mode로 실행하고 loop body line에 breakpoint를 둔다.

```txt
var total = 0;
for (var i = 0; i < 3; i = i + 1) {
  total = total + i;
  print total;
}
```

Resolution:
`DebugSession.enter_for_loop`, `normalize_for_frame`, `push_for_body_frame`이 loop body를 별도 frame으로
관리하는지 확인한다.

Prevention:
새 statement 타입을 추가할 때 debug mode에서 step/next/continue 동작도 같이 검증한다.

## Symptom: 파일 실행 중 오류 줄 번호가 없거나 틀리다

Likely cause:
Tokenizer, AST statement, runtime error 사이에 line 정보가 끊겼을 수 있다.
PR #46과 #51에서 file/debug mode를 위해 `Token.line`과 `Stmt.line` 전달을 추가했다.

How to confirm:

```txt
print 1;
print 10 / 0;
print 3;
```

`make run sample.cfab` 결과가 `Error at line 2: Division by zero.` 형태인지 확인한다.

Resolution:
새 parser branch가 statement를 만들 때 시작 token의 `line`을 넘기는지 확인한다.

Prevention:
문장 AST를 추가할 때 `line` 필드를 생성자와 테스트에 포함한다.

## Symptom: CI가 실패했지만 원인이 workflow인지 코드인지 애매하다

Likely cause:
Actions는 결과 신호일 뿐이고, 원인은 파일 경로 변경, 테스트명 변경, coverage 대상 변경, lint 미실행 등일 수 있다.
PR #55에서는 `app/` 패키지화 뒤 gist acceptance 파일명과 coverage 대상도 함께 바꿔야 했다.

How to confirm:

```bash
make lint
make test
python -m pytest -q tests/test_app_codefab_gist_acceptance.py
python -m pytest -q --cov=app --cov-report=xml --cov-report=term
```

Resolution:
실패한 workflow의 step을 보고, 그 명령을 로컬에서 같은 경로로 실행한다. 코드 이동 PR이라면 `.github/workflows`,
README, 테스트 파일명을 같이 검색한다.

Prevention:
CI 실패를 문서화할 때는 "어떤 workflow가 실패했는가"보다 "그 실패가 알려준 계약/경로/테스트 규칙은 무엇인가"를
먼저 남긴다.

## Symptom: PR에서 Codecov가 patch coverage 경고를 남긴다

Likely cause:
리팩토링성 변경이어도 새 줄 기준 patch coverage가 낮게 보일 수 있다. PR #55에서는 `app/main.py`의 일부 줄이
patch coverage 경고로 표시됐지만, 기능 오류와 coverage comment는 구분해서 봐야 한다.

How to confirm:
Codecov comment에서 전체 프로젝트 coverage와 patch coverage를 분리해서 확인한다.

Resolution:
동작을 바꾼 코드라면 테스트를 추가한다. 순수 이동/경로 변경이라면 PR 설명에 검증 명령과 영향 범위를 명확히 적는다.

Prevention:
리팩토링 PR은 "동작 변화 없음", "실행한 테스트", "경로 변경으로 같이 바꾼 CI 항목"을 PR 본문에 남긴다.
