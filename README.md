# Code Review Agent Team3

[![codecov](https://codecov.io/gh/j0shuajun/team3-codefab/branch/main/graph/badge.svg)](https://codecov.io/gh/j0shuajun/team3-codefab)

- 팀명: Ctrl-C
- 의미: 서로의 강점을 복사(Copy)해 함께 성장하는 팀
- 팀원: 김명준님(팀장), 권소영님, 김민준님, 박진우님, 이예진님

## CodeFab 구현 범위 체크리스트

CRA/교안/CodeFab PDF에서 다룬 언어 기능을 기준으로 보면, `import`/`alias` 흐름을 제외한 핵심 기능은 구현되어 있다.
`ctrlc`/`ctrlv`는 prompt shell 기능이고, `ctrl_c()`는 custom language 안에서 팀 Ctrl-C를 소개하는 내장 함수로
구분한다.

| 상태 | 기능 | 현재 범위 |
| --- | --- | --- |
| [x] | Tokenizer | 예약어, identifier, 숫자, 문자열, boolean, 단일/복합 연산자를 token으로 변환한다. |
| [x] | Parser/Assembler | expression, statement, block, condition, loop, function, class, array 문법을 AST로 만든다. |
| [x] | Checker | 중복 선언, 미초기화 변수, 잘못된 `This`/`Super`, 함수/class/array 사용 오류를 실행 전에 잡는다. |
| [x] | Executor | 변수 scope, 산술/비교/논리 연산, 출력, 함수 호출, class instance, inheritance, array 동작을 실행한다. |
| [x] | Function/Class | `Func`, `return`, parameter/arity 검사, `Class`, method, `This`, `Super`, `instanceof`를 지원한다. |
| [x] | Array | `Array(size)`, index get/set, 정수 index, 범위 검사, 잘못된 길이 검사를 지원한다. |
| [x] | Optimizer | static binding과 constant folding으로 의미를 유지하면서 일부 expression을 정리한다. |
| [x] | Shell/File/Debug | `make run`, `make run <file>`, `make debug <file>`로 shell, 파일 실행, step/break/watch debug를 실행한다. |
| [x] | Shell `ctrlc`/`ctrlv` | prompt shell에서 이전 입력을 추천하고 추천 명령을 다시 실행한다. |
| [x] | Custom `ctrl_c()` | CodeFab 코드 안에서 호출해 팀명, 팀 의미, 팀원을 소개하는 내장 함수로 정리했다. |
| [x] | Custom `explain`/한글 키워드 | 발표용 custom language 기능으로 코드 해석 과정과 한글 alias 방향을 정리했다. |
| [ ] | `import`/`alias` | token은 존재하지만, 외부 CodeFab 파일을 불러와 namespace로 연결하는 흐름은 아직 구현 대상이다. |

## Ground Rules

### PR/코드 리뷰 규칙
- [PR Template](.github/pull_request_template.md)을 준수해야 하며, 최소 두 명의 Approve가 필요하다. Merge는 PR을 생성한 사람이 직접 진행한다.
- Commit message는 다음 [양식](https://wikidocs.net/332862)을 준수한다. 
- Branch 이름은 `feature/`, `refactor/`, `chore/` 등의 형식을 따른다.
- 테스트파일은 `tests/` 디렉토리 하위에 테스트 대상 파일이름을 경로에 담아 작성한다.
  - ex) `tests/test_app_assembler_tokenizer.py`

### CI / Lint

```bash
make install   # requirements-dev.txt 설치
make lint      # black / isort / ruff --fix 실행
make test      # pytest 실행
make run       # 프롬프트 쉘 실행
make run <file>    # 파일 실행
make debug <file>  # 디버그 모드 실행
```

### 문서

- [CONCEPTS](docs/CONCEPTS.md): CodeFab이 어떤 언어이고 어떤 흐름으로 동작하는지 설명한다.
- [custom_language](docs/custom_language.md): CodeFab 문법, 특이 기능, 사용 예시를 정리한다.
- [DETAILS](docs/DETAILS.md): `app/` 패키지 기준 구현 구조와 데이터 흐름을 설명한다.
- [TROUBLESHOOTING](docs/TROUBLESHOOTING.md): PR 리뷰와 Actions 결과에서 나온 문제 진단법을 정리한다.
- [CHANGELOG](docs/CHANGELOG.md): merge된 코드 PR 기준 변경 이력을 정리한다.

### 팀 협업 규칙
- 45분 활동, 15분 휴식 / 17:00 마감 후 저녁 테이크아웃 꼭 받기
- 디스코드에 github noti 오면 확인 즉시 들어가보기
- 퇴근 전 쉬는시간에 다음날 todo 정하기 & 다음날에는 todo 확인하기
- 아침에 인사하기, 퇴근할 때 인사하기!
