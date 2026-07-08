import sys

from shell.file_mode import FileMode
from shell.shell import PromptShell


def main():
    if len(sys.argv) == 1:
        PromptShell().run()
        return

    if sys.argv[1] in ("repl", "--repl"):
        PromptShell().run()
        return

    if sys.argv[1] in ("file", "--file"):
        if len(sys.argv) < 3:
            print("Usage: python main.py file <source_file>")
            return

        FileMode().run(sys.argv[2])
        return

    FileMode().run(sys.argv[1])


if __name__ == "__main__":
    main()