from commands import Commands
from memory import Memory
from registers import Registers


class OpCodeParser(object):

    def __init__(self, code_buffer, commands, memory, state):

        self._commands = commands
        self._memory = memory
        self._state = registers
        self._opcode_map_file = "./opcode_map.csv"
        self._opcode_map = self._init_opcodes(self._commands)
        self._code_buffer = code_buffer

    def _init_opcodes(self, commands):
        opcodes = self._get_opcodes_from_file(self._opcode_map_file)
        # print(opcodes)
        # opcodes = {
        #     0x01: {'mnemon': commands.nop, 'argument_sizes': []},
        #     0x04: {'mnemon': commands.nop, 'argument_sizes': [1]},
        # }
        return opcodes

    def step(self, fake=False):
        pc = self._state.pc
        opcode = self._code_buffer[pc]
        opcode = self._parse_opcode(opcode) if type(opcode) != int else '{0:#04x}'.format(opcode)
        pc += 1
        mnemon = self._opcode_map.get(opcode, None).get('mnemon')
        argument_sizes = self._opcode_map.get(opcode, None).get('argument_sizes') # get amount and size of arguments for this opcode
        arguments = []
        for argument_size in argument_sizes:
            argument = self._code_buffer[pc:argument_size+1]
            argument = self._unpack_argument(argument)
            arguments.append(argument)
            pc += argument_size

        if fake:
            message = "{mnemon} {arguments}".format(mnemon=mnemon, arguments=arguments)
            print(message)
        else:
            self._commands.execute_command(mnemon, *arguments)

    def _unpack_argument(self, argument):
        argument_bytesize = len(argument)
        result = ord(argument[0]) if argument_bytesize > 1 else ord(argument)
        if type(argument) == list:
            for index in range(argument_bytesize):
                result += 255*argument[index]*index
        else:
            for index in range(argument_bytesize):
                result += 255*ord(argument[index])*index
        return argument

    def _parse_opcode(self, opcode):
        opcode = '{0:#04X}'.format(ord(opcode)).lower()
        return opcode

    def parse(self):
        pass

    def _get_opcodes_from_file(self, opcode_map_file):
        opcode_map = {}
        with open(opcode_map_file) as input_file:
            lines = input_file.readlines()
            for line in lines:
                line = line.rstrip("\n")
                mnemon, op, argument_sizes = line.split(",")
                argument_sizes = argument_sizes.split("|")
                argument_sizes = [int(argument_size) for argument_size in argument_sizes]
                opcode_map[op.rstrip(" ").lower()] = {'mnemon': mnemon.rstrip(" "), 'argument_sizes': argument_sizes}
        return opcode_map


if __name__ == "__main__":
    buffer = ""  # insert image here?
    registers = Registers()
    memory = Memory()
    commands = Commands(registers, memory)
    opcode_parser = OpCodeParser("\xfb\x02\x04", commands, memory, registers)

    print(registers)
    opcode_parser.step(fake=True)
    print(registers)



