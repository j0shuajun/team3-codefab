# Code Review Agent Team3
- 팀명: Ctrl-C
- 의미: 서로의 강점을 복사(Copy)해 함께 성장하는 팀
- 팀원: 김명준님(팀장), 권소영님, 김민준님, 박진우님, 이예진님

## Ground Rules

### PR/코드 리뷰 규칙
- PR merge 하기 위해서는 최소 두 명 이상의 Approve가 필요하다. ([PR Template](#pr-template) 준수)
- PR의 Merge는 PR을 생성(요청)한 사람이 직접 진행한다.
- 최소 승인 조건(2명 Approve)을 충족한 이후에 merge 한다.
- Commit/PR 전 Reformat Code (Ctrl+Alt+L)를 실행하여 스타일을 통일한다.
- Commit message는 다음 페이지 양식을 준수한다. (https://wikidocs.net/332862)
- Branch 이름은 `feature/<기능>` 형식을 따른다.
- 테스트파일은 `tests/` 디렉토리 하위에 테스트 대상 파일이름을 경로에 담아 작성한다. ex) `tests/test_assembler_tokenizer.py`

### 팀 협업 규칙
- 45분 활동, 15분 휴식 / 17:00 마감 후 저녁 테이크아웃 꼭 받기
- 디스코드에 github noti 오면 확인 즉시 들어가보기
- 퇴근 전 쉬는시간에 다음날 todo 정하기 & 다음날에는 todo 확인하기
- 아침에 인사하기, 퇴근할 때 인사하기!

### PR 태그 기준

각 변경 사항에 맞는 태그를 선택해주세요:

| 태그 | 사용 기준 | 예시 |
|------|---------|------|
| `feature` | 새로운 기능을 추가하는 경우 | 새로운 모듈 추가, 새로운 API 엔드포인트 |
| `bug` | 기존 기능의 버그를 수정하는 경우 | 예상과 다른 동작 수정, 에러 처리 개선 |
| `refactor` | 기능 변화 없이 코드 구조/품질을 개선하는 경우 | 함수 분리, 변수명 개선, 로직 정리 |
| `documentation` | 문서, README, 주석 등을 추가/수정하는 경우 | README 업데이트, API 문서 작성 |
| `chore` | 테스트, 빌드, 의존성 등 개발 환경 관련 변경 | 테스트 추가, 패키지 업데이트, CI 설정 |
