from commands import Commands
from memory import Memory
from registers import Registers


class OpCodeParser(object):
    ADDRESS = 2
    OPERAND = 1

    def __init__(self, command_execution):

        self._commands = command_execution
        self._opcode_index = self._init_opcodes(self._commands)

    def _init_opcodes(self, commands):
        opcodes = {
            0x01: {'command': commands.nop, 'operands': []},
            0xF9: {'command': commands.adc(), 'operands': [self.OPERAND]},
            0xDB: {'command': commands.add(), 'operands': [self.OPERAND]},
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