from shell.shell import CodeFabRunner


class FileMode:
    def __init__(self, runner=None):
        self.runner = runner or CodeFabRunner()

    def run_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                source = file.read()
        except FileNotFoundError:
            return [f"Error: file not found: {file_path}"]

        return self.runner.run_code(source)

    def run(self, file_path):
        outputs = self.run_file(file_path)

        for output in outputs:
            print(output)