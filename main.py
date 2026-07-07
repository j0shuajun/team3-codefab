from assembler.assembler import Assembler
from shell import PromptShell


def main():
    shell = PromptShell(assembler_class=Assembler)
    shell.run()


if __name__ == "__main__":
    main()