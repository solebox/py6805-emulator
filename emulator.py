from commands import Commands
from memory import Memory
from registers import Registers


class OpCodeParser(object):

    def __init__(self, command_execution):

        self._commands = command_execution
        self._opcode_index = self._init_opcodes(self._commands)

    def _init_opcodes(self, commands):
        opcodes = {
            0x01: commands.nop,
        }
        return opcodes

    def parse(self, code_buffer):
        pass


if __name__ == "__main__":
    buffer = ""  # insert image here?
    registers = Registers()
    memory = Memory()
    commands = Commands(registers, memory)
    opcode_parser = OpCodeParser(commands)
    opcode_parser.parse(buffer)