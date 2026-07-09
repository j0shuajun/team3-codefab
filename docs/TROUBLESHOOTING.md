# Troubleshooting

이 문서는 PR 코멘트, GitHub Actions 결과, 최근 구조 변경에서 반복될 수 있는 문제를 빠르게 진단하기 위한 문서다.

## Symptom: PR에서 Gist Acceptance만 실패한다

Likely cause:
`app/` 패키지화나 테스트 파일명 변경 뒤 workflow가 옛 테스트 파일명을 참조할 수 있다.
PR #55 초기 실행에서 Gist Acceptance가 실패했고, 이후 workflow를
`tests/test_app_codefab_gist_acceptance.py`로 바꿔 성공했다.

How to confirm:

- GitHub Actions에서 `Gist Acceptance` workflow의 실패 step을 확인한다.
- 로컬에서 다음 명령을 실행한다.

```bash
python -m pytest -q tests/test_app_codefab_gist_acceptance.py
```

Resolution:
`.github/workflows/gist-acceptance.yml`의 테스트 파일 경로가 현재 파일명과 같은지 확인한다.

Prevention:
테스트 파일명을 바꾸면 workflow의 직접 파일 경로도 함께 검색한다.

## Symptom: Unit Tests coverage step이 실패한다

Likely cause:
coverage 대상 패키지가 현재 구조와 맞지 않을 수 있다. `app/` 패키지화 전에는
`--cov=assembler --cov=checker --cov=executor --cov=shell`였지만, 현재는 `--cov=app`이 맞다.

How to confirm:

```bash
python -m pytest -q --cov=app --cov-report=xml --cov-report=term
```

Resolution:
`.github/workflows/test.yml`의 coverage 대상이 `app`인지 확인한다.

Prevention:
코드 디렉터리 이동 PR에는 import 경로, test 파일명, Actions coverage 대상, README 실행법을 한 세트로 점검한다.

## Symptom: Lint workflow만 실패한다

Likely cause:
PR 기록상 Shell/Tokenizer 작업에서 Lint만 실패한 경우가 있었다. 보통 formatter 미적용, import 정렬,
ruff 지적 사항이 원인이다.

How to confirm:

```bash
make lint
```

Resolution:
`make lint`를 실행해 black, isort, ruff fix를 적용한 뒤 diff를 확인한다.

Prevention:
커밋 전 `black .`, `isort .`, `ruff check .` 또는 `make lint`를 실행한다.

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

## Symptom: checker가 맞는 코드까지 막거나, 위험한 코드를 놓친다

Likely cause:
checker는 실행 전 보수적으로 판단한다. 특히 `if`, `for`, function/class 문맥은 scope snapshot과 merge 규칙이
중요하다. PR #52에는 method body resolve가 바깥 변수 초기화 상태를 선언 시점에 오염시키는 문제를 고친
추가 커밋이 포함되어 있다.

How to confirm:

- `tests/test_app_checker_checker.py`
- `tests/test_app_checker_class.py`
- `tests/test_app_checker_static_binding.py`

위 테스트에서 비슷한 시나리오가 있는지 먼저 찾는다.

Resolution:
`StatementResolver`의 scope snapshot/restore/merge 흐름을 확인한다. 함수나 method body는 선언 시점에
주변 scope 상태를 오염시키지 않아야 한다.

Prevention:
checker 변경에는 "then만 초기화", "else만 초기화", "loop가 0번 실행", "method 선언 시점" 같은 반례를
테스트로 추가한다.

## Symptom: `This` 또는 `Super`가 이상하게 동작한다

Likely cause:
class 문맥과 runtime environment가 둘 다 맞아야 한다. checker는 class 내부/상속 여부를 확인하고,
executor는 method bind 시 `This`, subclass method lookup 시 `Super`를 environment에 넣는다.

How to confirm:

```txt
Class Parent {
  speak() { print "parent"; }
}

Class Child: Parent {
  speak() { Super.speak(); }
}

Child().speak();
```

Resolution:
`ClassContext`, `StatementResolver._resolve_class_stmt`, `UserFunction.bind`, `Executor`의 `SuperExpr`
평가 흐름을 함께 확인한다.

Prevention:
class 기능은 checker 테스트와 executor 테스트를 나눠서 작성한다. "사용 금지 문맥"과 "실행 결과"는 다른
문제다.

## Symptom: PR에서 Codecov가 patch coverage 경고를 남긴다

Likely cause:
PR #55처럼 리팩토링성 변경이어도 새 줄 기준 patch coverage가 낮게 보일 수 있다. 기능 오류와 coverage
comment는 구분해서 본다.

How to confirm:
Codecov comment에서 전체 프로젝트 coverage와 patch coverage를 분리해서 확인한다.

Resolution:
동작을 바꾼 코드라면 테스트를 추가한다. 순수 이동/경로 변경이라면 PR 설명에 검증 명령과 영향 범위를
명확히 적는다.

Prevention:
리팩토링 PR은 "동작 변화 없음", "실행한 테스트", "경로 변경으로 같이 바꾼 CI 항목"을 PR 본문에 남긴다.

