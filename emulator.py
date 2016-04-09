from commands import Commands
from memory import Memory
from registers import Registers


class OpCodeParser(object):
    ADDRESS = 2
    OPERAND = 1

    def __init__(self, command_execution):

        self._commands = command_execution
        self._opcode_map_file = "./opcode_map.csv"
        self._opcode_index = self._init_opcodes(self._commands)

    def _init_opcodes(self, commands):
        opcodes = self._get_opcodes_from_file(self._opcode_map_file)
        # print(opcodes)
        # opcodes = {
        #     0x01: {'command': commands.nop, 'operands': []},
        #     0xF9: {'command': commands.adc, 'operands': [self.OPERAND]},u
        #     0xDB: {'command': commands.add, 'operands': [self.OPERAND]},
        # }
        return opcodes

    def parse(self, code_buffer):
        pass

    def _get_opcodes_from_file(self, opcode_map_file):
        opcode_map = {}
        with open(opcode_map_file) as input_file:
            lines = input_file.readlines()
            for line in lines:
                mnemon, op = line.split(",")
                opcode_map[op.rstrip("\n")] = mnemon.rstrip(" ")
        return opcode_map


if __name__ == "__main__":
    buffer = ""  # insert image here?
    registers = Registers()
    memory = Memory()
    commands = Commands(registers, memory)
    opcode_parser = OpCodeParser(commands)
    opcode_parser.parse(buffer)
    print(registers)

    commands.add(0x1)
    commands.sub(0x2)


    print(registers)
