import sys

from shell.debug_mode import DebugMode
from shell.file_mode import FileMode
from shell.shell import PromptShell


def main():
    args = sys.argv[1:]

    if not args:
        PromptShell().run()
        return

    mode = args[0]

    if mode in ("repl", "--repl"):
        PromptShell().run()
        return

    if mode in ("file", "--file"):
        if len(args) < 2:
            print("Usage: python main.py file <source_file>")
            return

        FileMode().run(args[1])
        return

    if mode in ("debug", "--debug"):
        if len(args) < 2:
            print("Usage: python main.py debug <source_file>")
            return

        DebugMode().run(args[1])
        return

    FileMode().run(mode)


if __name__ == "__main__":
    main()
