# Code Review Agent Team3

[![codecov](https://codecov.io/gh/j0shuajun/team3-codefab/branch/main/graph/badge.svg)](https://codecov.io/gh/j0shuajun/team3-codefab)

- 팀명: Ctrl-C
- 의미: 서로의 강점을 복사(Copy)해 함께 성장하는 팀
- 팀원: 김명준님(팀장), 권소영님, 김민준님, 박진우님, 이예진님

## Custom Language

- [CUSTOM_LANGUAGE](CodeFab/docs/CUSTOM_LANGUAGE.md) 가이드 문서

## CodeFab 구현 체크리스트

| 상태 | 기능 | 역할                                                                                          |
|----| --- |---------------------------------------------------------------------------------------------|
| ✅ | Tokenizer | 예약어, identifier, 숫자, 문자열, boolean, 단일/복합 연산자를 token으로 변환한다.                                 |
| ✅ | Assembler | expression, statement, block, condition, loop, function, class, array 문법을 AST로 만든다.         |
| ✅ | Checker | 중복 선언, 미초기화 변수, 잘못된 `This`/`Super`, 함수/class/array 사용 오류를 실행 전에 잡는다.                        |
| ✅ | Executor | 변수 scope, 산술/비교/논리 연산, 출력, 함수 호출, class instance, inheritance, array 동작을 실행한다.              |
| ✅ | Function/Class | `Func`, `return`, parameter/arity 검사, `Class`, method, `This`, `Super`, `instanceof`를 지원한다. |
| ✅ | Array | `Array(size)`, index get/set, 정수 index, 범위 검사, 잘못된 길이 검사를 지원한다.                             |
| ✅ | Optimizer | static binding과 constant folding으로 의미를 유지하면서 일부 expression을 정리한다.                           |
| ✅ | Shell | shell, 파일 실행, step/break/watch debug를 실행한다.                                                 |
| ✅ | `import` | 외부 CodeFab 파일을 불러와 namespace로 연결한다.                                                         |

## Ground Rules

### PR/코드 리뷰 규칙
- [PR Template](.github/pull_request_template.md)을 준수해야 하며, 최소 두 명의 Approve가 필요하다. Merge는 PR을 생성한 사람이 직접 진행한다.
- Commit message는 다음 [양식](https://wikidocs.net/332862)을 준수한다. 
- Branch 이름은 `feature/`, `refactor/`, `chore/` 등의 형식을 따른다.
- 테스트파일은 `tests/` 디렉토리 하위에 테스트 대상 파일이름을 경로에 담아 작성한다.
  - ex) `tests/test_app_assembler_tokenizer.py`

### CI / Lint

```bash
make install       # requirements-dev.txt 설치
make lint          # black / isort / ruff --fix 실행
make test          # pytest 실행
make run           # 프롬프트 쉘 실행
make run <file>    # 파일 실행
make debug <file>  # 디버그 모드 실행
```

### 팀 협업 규칙
- 45분 활동, 15분 휴식 / 17:00 마감 후 저녁 테이크아웃 꼭 받기
- 디스코드에 github noti 오면 확인 즉시 들어가보기
- 퇴근 전 쉬는시간에 다음날 todo 정하기 & 다음날에는 todo 확인하기
- 아침에 인사하기, 퇴근할 때 인사하기!
