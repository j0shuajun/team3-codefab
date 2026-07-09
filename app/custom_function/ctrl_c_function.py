import textwrap
from app.assembler.runtime import NativeFunction

TEAM_NAME = "Ctrl-C"
TEAM_MEANING = "서로의 강점을 복사(Copy)해 함께 성장하는 팀"

TEAM_MEMBERS = [
    {
        "name": "김명준",
        "role": "팀장",
        "hobby": "런닝, 클라이밍",
        "parts": ["architecture", "infra", "ci", "coverage", "document"],
        "remark": (
            "직접 개발한 내용이 아닌 코드를 리뷰하는 것이 꽤나 노력이 필요하다는 것을 몸소 체감했어요. "
            "디자인 패턴을 생각하면서 구현하는 것도 어려워 보이더라구요. 그래도 코드 리뷰와 평소 개발 습관이 "
            "얼마나 중요한 지 다시 생각해보는 좋은 계기가 되었습니다. 우리 팀원분들 고생하셨고 감사합니다!"
        ),
    },
    {
        "name": "권소영",
        "role": None,
        "hobby": "수영",
        "parts": ["assembler", "executor", "function", "class", "import"],
        "remark": (
            "개발하랴 리뷰하랴 바쁜 일정이었지만 모두들 한 마음 한 뜻으로 진행했던 터라 "
            "큰 이슈 없이 잘 마무리된 것 같습니다. 모두 고생 많으셨어요!!"
        ),
    },
    {
        "name": "김민준",
        "role": None,
        "hobby": "야구 관람, 스타크래프트",
        "parts": ["expr", "statement", "shell"],
        "remark": (
            "여러명이서 개발을 한 경험이 거의 없었는데 이번 기회에 함께 개발하고 리뷰 하면서 "
            "많이 배울 수 있었습니다. 팀원분들 모두 고생 많으셨고 감사드립니다."
        ),
    },
    {
        "name": "박진우",
        "role": None,
        "hobby": "실내 클라이밍",
        "parts": ["tokenizer", "array", "custom language"],
        "remark": (
            "생각했던 것 보다 더 유익한 Code Review Agent 과정이었습니다. "
            "AI 시대에 맞게 나 자신도 발빠르게 변화해야 하는데, 이번 과정을 통해 그 흐름에 "
            "잘 따라갈 수 있었습니다. 그리고 평소에는 뵈기 힘든 타 부서의 동료분들과 협업하면서 "
            "많이 배우고 생각이 넓어질 수 있었습니다. 고생하셨습니다!"
        ),
    },
    {
        "name": "이예진",
        "role": None,
        "hobby": "러닝, 탁구, 독서",
        "parts": ["checker", "optimizer", "custom function"],
        "remark": (
            "unit test를 계속 작성하고 관리하며 개발해 나가는 과정이 처음엔 번거로웠지만, "
            "여러 사람과 협업하며 프로젝트를 진행할 때 기존 코드의 유효성을 위해 꼭 필요한 과정임을 "
            "알게 되었습니다. 리뷰를 주고 받는 과정에서 제가 생각지 못했던 여러 설계 관점을 배울 수 "
            "있었습니다. 모두 고생 많으셨습니다~"
        ),
    },
]


# 터미널 색상 및 스타일 정의 (ANSI Escape Code)
class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"


BOX_WIDTH = 80
TOP_BORDER = f"{Style.GRAY}┏" + "━" * BOX_WIDTH + f"┓{Style.RESET}"
MID_BORDER = f"{Style.GRAY}┣" + "━" * BOX_WIDTH + f"┫{Style.RESET}"
BOTTOM_BORDER = f"{Style.GRAY}┗" + "━" * BOX_WIDTH + f"┛{Style.RESET}"


def member_label(member):
    label = f"{Style.BOLD}{member['name']}{Style.RESET}님"
    if member["role"]:
        label += f"{Style.GRAY}({member['role']}){Style.RESET}"
    return label


def build_ctrl_c_lines():
    lines = [
        TOP_BORDER,
        f"  🏷️  {Style.CYAN}{Style.BOLD}팀명:{Style.RESET} {TEAM_NAME}",
        f"  💡  {Style.CYAN}{Style.BOLD}의미:{Style.RESET} {TEAM_MEANING}",
        MID_BORDER,
        f"  {Style.GREEN}{Style.BOLD}👥 팀원 & 취미{Style.RESET}",
    ]

    for member in TEAM_MEMBERS:
        hobby = member["hobby"] or "-"
        lines.append(f"    🙋 {member_label(member)} — 취미: {Style.WHITE}{hobby}{Style.RESET}")

    lines.append(MID_BORDER)
    lines.append(f"  {Style.YELLOW}{Style.BOLD}🛠️  담당 역할{Style.RESET}")

    for member in TEAM_MEMBERS:
        parts_str = f"{Style.GRAY}, {Style.RESET}".join([f"{Style.WHITE}{p}{Style.RESET}" for p in member['parts']])
        lines.append(f"    🔧 {Style.BOLD}{member['name']}{Style.RESET}: {parts_str}")

    lines.append(MID_BORDER)
    lines.append(f"  {Style.MAGENTA}{Style.BOLD}💬 한 줄 소감{Style.RESET}")

    for member in TEAM_MEMBERS:
        lines.append(f"    🗨️  {Style.BOLD}{member['name']}{Style.RESET}")

        if "remark" in member and member["remark"]:
            wrapped_remarks = textwrap.wrap(member["remark"], width=40)

            for i, chunk in enumerate(wrapped_remarks):
                if i == 0:
                    lines.append(f'       {Style.GRAY}"{chunk}')
                else:
                    lines.append(f'        {chunk}')

            # 마지막 줄 끝에 따옴표 닫기
            lines[-1] = lines[-1] + f'"{Style.RESET}'
        else:
            lines.append(f"       {Style.GRAY}(작성한 소감이 없습니다){Style.RESET}")

    lines.append(BOTTOM_BORDER)
    return lines


# 출력 테스트
for line in build_ctrl_c_lines():
    print(line)


def _make_ctrl_c(executor):
    def ctrl_c():
        executor.outputs.extend(build_ctrl_c_lines())
        return None

    return ctrl_c


CUSTOM_FUNCTIONS = [
    ("ctrl_c", 0, _make_ctrl_c),
]


def register_custom_functions(executor):
    for name, arity, make_function in CUSTOM_FUNCTIONS:
        executor.globals.define(name, NativeFunction(name, arity, make_function(executor)))
