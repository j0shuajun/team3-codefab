# CodeFab examples

기능별로 나눈 CodeFab 예제 소스입니다. `make run <file>`로 실행합니다.

| 파일 | 데모하는 기능 | 상태 |
|---|---|---|
| `01_variable_print.ctrlc` | 변수, 재대입, print, 숫자/문자열/boolean 출력 | 동작 |
| `02_condition.ctrlc` | if/else 조건문 | 동작 |
| `03_loop.ctrlc` | for 반복문 | 동작 |
| `04_function.ctrlc` | Func 선언, return, 함수 호출 | 동작 |
| `05_class_inheritance.ctrlc` | Class, 상속, This, Super, instanceof | 동작 |
| `06_array.ctrlc` | Array(size), index get/set | 동작 |
| `07_checker_error.ctrlc` | Checker가 실행 전에 잡는 중복 선언 오류 | 동작 (의도적으로 오류를 출력) |
| `08_ctrl_c.ctrlc` | 커스텀 내장 함수 `ctrl_c()` (팀 소개) | **TODO** - 아직 미구현. 토크나이저가 식별자에 `_`를 허용하지 않아 `ctrl_c`부터 파싱 실패함 (`Unexpected character: '_'`) |
| `debug_test.ctrlc` | `make debug`용 디버그 모드 데모 | 동작 |

## 다음에 할 일

- 한글 alias(`값`, `만약`, `반복`, `함수`, `클래스`, `보여줘`, `펑펑` 등)를 적용한 버전을 파일별로 추가할 예정.
- `08_ctrl_c.ctrlc`는 `ctrl_c()` 내장 함수와 식별자 `_` 지원이 구현되면 채울 예정.
