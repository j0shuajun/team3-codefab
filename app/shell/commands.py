from abc import ABC, abstractmethod


class ShellCommand(ABC):
    @abstractmethod
    def execute(self, shell):
        pass

    def should_save_history(self):
        return False

    def history_key(self):
        return None


# class ExitCommand(ShellCommand):
#     def execute(self, shell):
#         shell.is_running = False
#         return ["Bye!"]
class ExitCommand(ShellCommand):
    def execute(self, shell):
        shell.is_running = False
        return self.goodbye_banner()

    def goodbye_banner(self):
        return [
            "+--------------------------------------------------------------+",
            "|   _____ _______ _____  _        _____                        |",
            "|  / ____|__   __|  __ \\| |      / ____|                       |",
            "| | |       | |  | |__) | |     | |                            |",
            "| | |       | |  |  _  /| |     | |                            |",
            "| | |____   | |  | | \\ \\| |____ | |____                        |",
            "|  \\_____|  |_|  |_|  \\_\\______| \\_____|                       |",
            "|                                                              |",
            "|                    Made by Team CTRL+C                       |",
            "|                  Thanks for using our shell!                 |",
            "|                        Goodbye :)                            |",
            "+--------------------------------------------------------------+",
        ]


class RecommendCommand(ShellCommand):
    def execute(self, shell):
        return shell.recommend_command()


class RerunCommand(ShellCommand):
    def execute(self, shell):
        return shell.run_recommended_command()


class ExplainCommand(ShellCommand):
    EXPLAIN_COMMAND = "explain"

    def __init__(self, source):
        self.source = source

    def execute(self, shell):
        if self.source == self.EXPLAIN_COMMAND:
            return ["Usage: explain <code>"]

        code = self.source[len(self.EXPLAIN_COMMAND) :].strip()

        if code == "":
            return ["Usage: explain <code>"]

        return shell.explainer.explain_source(code)


class RunCodeCommand(ShellCommand):
    def __init__(self, source):
        self.source = source

    def execute(self, shell):
        return shell.run_code(self.source)

    def should_save_history(self):
        return True

    def history_key(self):
        return self.source


class ShellCommandFactory:
    EXIT_COMMANDS = ("exit", "quit")
    RECOMMEND_COMMAND = "ctrlc"
    RERUN_COMMAND = "ctrlv"
    EXPLAIN_COMMAND = "explain"

    @classmethod
    def create(cls, source):
        if source in cls.EXIT_COMMANDS:
            return ExitCommand()

        if source == cls.RECOMMEND_COMMAND:
            return RecommendCommand()

        if source == cls.RERUN_COMMAND:
            return RerunCommand()

        if source == cls.EXPLAIN_COMMAND:
            return ExplainCommand(source)

        if source.startswith(f"{cls.EXPLAIN_COMMAND} "):
            return ExplainCommand(source)

        return RunCodeCommand(source)
