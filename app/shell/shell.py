from collections import Counter

from app.shell.commands import ShellCommandFactory
from app.shell.explain_mode import ExplainMode
from app.shell.runner import CodeFabRunner


class PromptShell:
    def __init__(self, history_size=10, runner=None, explainer=None):
        self.runner = runner or CodeFabRunner()
        self.explainer = explainer or ExplainMode()

        self.history_size = history_size
        self.command_history = []
        self.recommended_command = None
        self.is_running = True

    @property
    def history(self):
        return [command.history_key() for command in self.command_history]

    def run(self):
        print("CodeFab Prompt Shell")
        print("Type exit or quit to quit, ctrlc to recommend, ctrlv to rerun.")
        print("Type explain <code> to inspect the CodeFab pipeline.")

        while self.is_running:
            source = input("CodeFab> ")
            outputs = self.run_line(source)

            for output in outputs:
                print(output)

    def run_line(self, source):
        source = source.strip()

        if source == "":
            return []

        command = ShellCommandFactory.create(source)

        if command.should_save_history():
            self.save_history(command)

        return command.execute(self)

    def run_code(self, source):
        return self.runner.run_code(source)

    def save_history(self, command):
        self.command_history.append(command)

        if len(self.command_history) > self.history_size:
            self.command_history.pop(0)

    def recommend_command(self):
        if not self.command_history:
            return ["추천할 명령어가 없습니다."]

        command_counts = Counter(
            command.history_key() for command in self.command_history
        )
        max_count = max(command_counts.values())

        for command in reversed(self.command_history):
            if command_counts[command.history_key()] == max_count:
                self.recommended_command = command
                return [
                    f"Ctrl+C 추천 명령어: {command.history_key()}",
                    "ctrlv 를 입력하면 추천 명령어를 다시 실행합니다.",
                ]

        return ["추천할 명령어가 없습니다."]

    def run_recommended_command(self):
        if self.recommended_command is None:
            return ["먼저 ctrlc 로 추천 명령어를 생성해주세요."]

        return self.recommended_command.execute(self)


ReplMode = PromptShell
