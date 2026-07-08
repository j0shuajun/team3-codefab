# CodeFab 언어 동작 구조

CodeFab은 Lox 스타일의 트리워킹 인터프리터로 구현된 커스텀 언어입니다.
현재 function, class 등 복잡한 기능은 지원하지 않으며, 변수 선언/대입, 산술·논리·비교 연산,
`if/else`, `for`, `print`, 블록 스코프까지 지원합니다.

## 전체 파이프라인

```
소스 코드(문자열)
    │
    ▼
[1] Tokenizer   (assembler/tokenizer.py)  — 문자열 → 토큰 리스트
    │
    ▼
[2] Assembler   (assembler/assembler.py)  — 토큰 리스트 → AST(Stmt/Expr 트리)
    │
    ▼
[3] Checker     (checker/checker.py)      — AST 정적 검사 (변수 초기화 여부 등)
    │
    ▼
[4] Executor    (executor/executor.py)    — AST를 직접 순회하며 실행 (트리워킹 인터프리터)
```

각 단계는 독립적인 모듈(디렉토리)로 분리되어 있고, 이전 단계의 산출물을 입력으로 받습니다.

---

## 1. Tokenizer (`assembler/tokenizer.py`)

역할: 소스 코드 문자열을 스캔하여 `Token` 객체의 리스트로 변환합니다.

- `TokenType`: 지원하는 모든 토큰 종류를 정의하는 Enum
  - 단일 문자: `( ) { } , ;` `+ - * /` `! = < >`
  - 두 문자 조합: `!= == >= <=`
  - 키워드: `var true false print and or if else for`
  - 리터럴: `IDENTIFIER`, `STRING`, `NUMBER`
  - 종료 토큰: `EOF`
- `Token`: `type`(TokenType), `origin`(원본 문자열), `value`(리터럴 값, 선택)를 가짐
- `Tokenizer.tokenize(string)`:
  - 공백은 건너뜀
  - `"` 로 시작하면 문자열 리터럴로 읽음 (`"`부터 `"`까지, 값은 따옴표 제거된 내용)
  - 숫자로 시작하면 숫자 리터럴로 읽음 (선행 0 불가, 소수점 지원, `value`는 `float`)
  - 알파벳으로 시작하면 식별자로 읽고, 예약어 테이블(`_RESERVED_TOKENS`)에 있으면 키워드 토큰으로 변환
  - `!`, `=`, `>`, `<` 뒤에 `=`가 오면 두 글자 토큰(`!=`, `==`, `>=`, `<=`)으로 합침
  - 인식 불가 문자는 `ValueError` 발생
  - 마지막에 항상 `EOF` 토큰을 추가

---

## 2. Assembler (`assembler/assembler.py`, `expr.py`, `statement.py`) — 파서

역할: 토큰 리스트를 재귀 하강 파싱(recursive descent parsing)하여 AST를 생성합니다.

### 문법 (표현식)

```
assignment -> IDENTIFIER "=" assignment | logic_or
logic_or   -> logic_and ("or" logic_and)*
logic_and  -> equality ("and" equality)*
equality   -> comparison (("!=" | "==") comparison)*
comparison -> term ((">" | ">=" | "<" | "<=") term)*
term       -> factor (("+" | "-") factor)*
factor     -> unary (("*" | "/") unary)*
unary      -> ("!" | "-") unary | primary
primary    -> NUMBER | STRING | true | false | IDENTIFIER | "(" expression ")"
```

이 문법은 연산자 우선순위를 그대로 반영합니다 (아래로 갈수록 우선순위가 높음: `assignment` < `or` < `and` < `equality` < `comparison` < `term` < `factor` < `unary` < `primary`).

### 문법 (구문/선언)

`Assembler.parse()`는 EOF를 만날 때까지 `declaration()`을 반복 호출합니다.

- `declaration` → `var` 선언 또는 일반 `statement`
- `statement` → `print` 문 / `if` 문 / `for` 문 / `{` 블록 / 표현식 문(expression statement)
- `var_declaration`: `var IDENTIFIER ("=" expression)? ";"`
- `if_statement`: `if "(" expression ")" statement ("else" statement)?`
- `for_statement`: `for "(" (초기화; 조건; 증감) ")" statement`
  - 초기화는 없음/`var` 선언/표현식문 중 하나
  - 파서 단계에서 별도 desugaring 없이 `ForStmt` 노드 그대로 유지 (Lox처럼 while로 변환하지 않음)
- `block`: `{` 여러 `declaration` `}`
- `print_statement`, `expression_statement`: 각각 `expression ";"`

### AST 노드

**표현식 (`assembler/expr.py`)**: `Expr` 를 상속
- `LiteralExpr(value)` — 숫자/문자열/불리언 리터럴
- `VariableExpr(name)` — 변수 참조
- `AssignExpr(name, value)` — 대입식
- `BinaryExpr(left, operator, right)` — 산술/비교/동등 연산
- `UnaryExpr(operator, right)` — 단항 연산(`-`, `!`)
- `GroupingExpr(expression)` — 괄호로 묶인 식
- `LogicalExpr(left, operator, right)` — `and`/`or` (단락 평가 대상)

**구문 (`assembler/statement.py`)**: `Stmt` 를 상속
- `ExpressionStmt(expression)`
- `PrintStmt(expression)`
- `VarStmt(name, initializer=None)`
- `BlockStmt(statements)` — 새 스코프를 여는 문 목록
- `IfStmt(condition, then_branch, else_branch=None)`
- `ForStmt(initializer, condition, increment, body)`

파싱 중 문법 오류는 `AssemblerError` 예외로 표현됩니다.

---

## 3. Checker (`checker/checker.py`, `resolver.py`, `scope_stack.py`) — 정적 검사

역할: 실행 전에 AST를 순회하며 "선언되었지만 초기화되지 않은 변수 사용", "같은 스코프 내 중복 선언" 등을 검사합니다. 실행기와 별개의 정적 분석 단계입니다.

- `Checker.check(statements)`: 스코프 상태와 에러 목록을 초기화한 뒤 `StatementResolver`로 전체 문장을 순회하고, 수집된 에러 메시지 리스트를 반환
- `ScopeStack` (`checker/scope_stack.py`): `{변수명: 초기화 여부}` 딕셔너리의 스택
  - `declare(name)`: 현재 스코프에 미초기화 상태로 등록 (중복 시 `False` 반환)
  - `initialize`/`mark_initialized`: 초기화 완료로 표시
  - `is_uninitialized(name)`: 선언은 됐지만 미초기화인지 확인
  - `snapshot()`/`restore()`: 분기(`if`)나 반복(`for`) 처리를 위해 스코프 상태를 저장/복원
- `ExpressionResolver` / `StatementResolver` (`checker/resolver.py`): 노드 타입별 딕셔너리 디스패치 방식으로 각 `Expr`/`Stmt` 하위 클래스를 처리
  - `VariableExpr` 방문 시 미초기화 변수 사용을 에러로 보고
  - `AssignExpr` 방문 시 해당 변수를 초기화 상태로 표시
  - `VarStmt`는 같은 스코프 재선언 검사 + 초기화 여부 반영
  - `BlockStmt`는 새 스코프(`with self._scopes.new_scope()`)를 열고 내부 문장 처리
  - `IfStmt`: `then`/`else` 분기를 각각 독립적으로 검사한 뒤, **두 분기 모두 초기화한 변수만 초기화된 것으로 병합**(`_merge_snapshots`)
  - `ForStmt`: 조건이 처음부터 거짓이라 본문이 한 번도 실행되지 않을 수 있으므로, 진입 전 상태와 "한 번 실행한 후" 상태를 병합해 보수적으로 계산
- `ErrorReporter`: 에러 메시지를 단순히 리스트에 누적하는 헬퍼

체커는 실행을 막지 않고 에러 메시지 리스트만 반환하므로, 호출부(테스트/CLI)가 이를 어떻게 다룰지 결정합니다.

---

## 4. Executor (`executor/executor.py`) — 트리워킹 인터프리터

역할: AST를 직접 순회하며 실제로 프로그램을 실행합니다. 별도의 바이트코드/VM 없이 `Stmt`/`Expr` 노드를 재귀적으로 평가합니다.

- `Environment`: 변수 저장소. `enclosing`(부모 환경)을 통해 체이닝되어 렉시컬 스코프를 구현
  - `define`: 현재 환경에 변수 정의
  - `get`/`assign`: 현재 환경에 없으면 `enclosing`으로 재귀 탐색, 끝까지 없으면 `CodeFabRuntimeError`
- `Executor`:
  - `globals`/`environment`: 최상위 환경과 현재 환경 (블록 진입 시 새 `Environment`로 교체 후 `finally`에서 복원)
  - `execute_stmt(stmt)`: `isinstance` 체인으로 문장 타입별 처리
    - `PrintStmt`: 값 평가 후 `stringify`하여 `self.outputs`(리스트)에 누적 — 실제 stdout 출력이 아니라 결과 리스트에 쌓는 구조 (테스트 용이성)
    - `VarStmt`: 초기화식이 있으면 평가, 없으면 `None`으로 정의
    - `BlockStmt`: 새 `Environment(self.environment)`를 만들어 `execute_block` 호출
    - `IfStmt`: 조건이 참(`is_truthy`)이면 then, 아니면 else 실행
    - `ForStmt`: `execute_for`에서 자체 반복 루프 실행(While 변환 없이 직접 초기화→조건→본문→증감 반복)
  - `evaluate(expr)`: 표현식 타입별로 값을 계산해 반환
    - `LiteralExpr` → 값 그대로
    - `BinaryExpr` → `evaluate_binary`에서 연산자별 처리, 타입 검사(`check_number_operand(s)`, `check_type_different`) 후 계산
      - `+`: 숫자+숫자 또는 문자열+문자열만 허용
      - `/`: 0으로 나누면 `CodeFabRuntimeError`
      - 비교/동등 연산: 서로 다른 타입 비교 시 에러
    - `UnaryExpr` → `-`(숫자만), `!`(진리값 반전)
    - `GroupingExpr` → 내부 식 평가
    - `VariableExpr`/`AssignExpr` → 환경(Environment)에서 조회/대입
    - `LogicalExpr` → `and`/`or` 단락 평가(`evaluate_logical`)
  - `is_truthy(value)`: `None`은 거짓, `bool`은 그대로, 그 외는 모두 참 (Lox와 동일한 진리값 규칙)
  - `stringify(value)`: 출력용 문자열 변환 (`None` → `"nil"`, `bool` → `"true"/"false"`, 정수값을 가진 `float` → 소수점 없이 출력)
  - 런타임 오류는 모두 `CodeFabRuntimeError` 예외로 표현

---

## 요약: 데이터 흐름 예시

```python
source = 'var x = 1; if (x > 0) { print "positive"; }'

tokens = Tokenizer().tokenize(source)          # [Token(VAR), Token(IDENTIFIER,'x'), ...]
statements = Assembler(tokens).parse()          # [VarStmt(x, LiteralExpr(1.0)), IfStmt(...)]
errors = Checker().check(statements)            # [] (문제 없음)
executor = Executor()
executor.execute(statements)                    # executor.outputs == ["positive"]
```

## 모듈 의존 관계

```
assembler/  (tokenizer, expr, statement, assembler)  ← 다른 모듈이 공용으로 참조하는 AST 정의
checker/    (checker, resolver, scope_stack, error_reporter)  → assembler 의 Expr/Stmt 를 import
executor/   (executor)  → assembler 의 Expr/Stmt/TokenType 을 import
```

`checker`와 `executor`는 서로 의존하지 않고 각각 `assembler`의 AST 정의만 참조하는 독립적인 후행 단계입니다.
