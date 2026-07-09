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
        "remark": None,
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

BOX_WIDTH = 56
TOP_BORDER = "┏" + "━" * BOX_WIDTH + "┓"
MID_BORDER = "┣" + "━" * BOX_WIDTH + "┫"
BOTTOM_BORDER = "┗" + "━" * BOX_WIDTH + "┛"


def member_label(member):
    label = f"{member['name']}님"
    if member["role"]:
        label += f"({member['role']})"
    return label


def build_ctrl_c_lines():
    lines = [
        TOP_BORDER,
        f"┃ 🏷️  팀명: {TEAM_NAME}",
        f"┃ 💡  의미: {TEAM_MEANING}",
        MID_BORDER,
        "┃ 👥 팀원 & 취미",
    ]

    for member in TEAM_MEMBERS:
        hobby = member["hobby"] or "-"
        lines.append(f"┃   🙋 {member_label(member)} — 취미: {hobby}")

    lines.append(MID_BORDER)
    lines.append("┃ 🛠️  담당 역할")

    for member in TEAM_MEMBERS:
        lines.append(f"┃   🔧 {member['name']}: {', '.join(member['parts'])}")

    lines.append(MID_BORDER)
    lines.append("┃ 💬 한 줄 소감")

    for member in TEAM_MEMBERS:
        lines.append(f"┃   🗨️  {member['name']}")
        if member["remark"]:
            lines.append(f'┃      "{member["remark"]}"')
        else:
            lines.append("┃      (작성한 소감이 없습니다)")

    lines.append(BOTTOM_BORDER)
    return lines


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
