from collections import Counter
from app.shell.explain_mode import ExplainMode
from app.shell.runner import CodeFabRunner



class PromptShell:
    EXIT_COMMANDS = ("exit", "quit")
    EXPLAIN_COMMAND = "explain"

    def  __init__(self, history_size=10):
        self.runner = CodeFabRunner()
        self.explainer = ExplainMode()

        self.history_size = history_size
        self.history = []
        self.recommended_command = None
        self.is_running = True

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

        shell_outputs = self.run_shell_command(source)
        if shell_outputs is not None:
            return shell_outputs

        self.save_history(source)
        return self.run_code(source)

    def run_shell_command(self, source):
        if source in self.EXIT_COMMANDS:
            self.is_running = False
            return ["Bye!"]

        if source == "ctrlc":
            return self.recommend_command()

        if source == "ctrlv":
            return self.run_recommended_command()

        if source == self.EXPLAIN_COMMAND:
            return ["Usage: explain <code>"]

        if source.startswith(f"{self.EXPLAIN_COMMAND} "):
            code = source[len(self.EXPLAIN_COMMAND) :].strip()

            if code == "":
                return ["Usage: explain <code>"]

            return self.explainer.explain_source(code)

        return None

    def run_code(self, source):
        return self.runner.run_code(source)

    def save_history(self, source):
        self.history.append(source)

        if len(self.history) > self.history_size:
            self.history.pop(0)

    def recommend_command(self):
        if not self.history:
            return ["추천할 명령어가 없습니다."]

        command_counts = Counter(self.history)
        max_count = max(command_counts.values())

        for command in reversed(self.history):
            if command_counts[command] == max_count:
                self.recommended_command = command
                return [
                    f"Ctrl+C 추천 명령어: {command}",
                    "ctrlv 를 입력하면 추천 명령어를 다시 실행합니다.",
                ]

        return ["추천할 명령어가 없습니다."]

    def run_recommended_command(self):
        if self.recommended_command is None:
            return ["먼저 ctrlc 로 추천 명령어를 생성해주세요."]

        return self.run_code(self.recommended_command)


ReplMode = PromptShell
