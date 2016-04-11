import struct

import re

from commands import Commands
from memory import Memory
from registers import Registers


class OpCodeParser(object):

    def __init__(self, code_buffer, commands, memory: Memory, state):

        self._commands = commands
        self._memory = memory
        self._state = registers
        self._opcode_map_file = "./opcode_map.csv"
        self._opcode_map = self._init_opcodes(self._commands)
        self._code_buffer = code_buffer
        self._memory.write_buffer_to_memory(0x0000, self._code_buffer)

    def _init_opcodes(self, commands):
        opcodes = self._get_opcodes_from_file(self._opcode_map_file)
        return opcodes

    def step(self, fake=False):
        pc = self._state.pc
        opcode = self._memory.read(pc)
        opcode = self._parse_opcode(opcode) if type(opcode) != int else '{0:#04x}'.format(opcode)
        pc += 1
        mnemon = self._opcode_map.get(opcode, None).get('mnemon')
        argument_sizes = self._opcode_map.get(opcode, None).get('argument_sizes') # get amount and size of arguments for this opcode
        arguments = []
        hex_encoded_arguments = []
        for argument_size in argument_sizes:
            argument = b''
            for byte_address in range(pc, pc+argument_size):
                argument += struct.pack('B', self._memory.read(byte_address))
            argument = self._unpack_argument(argument)
            hex_encoded_arguments.append(hex(argument))
            arguments.append(argument)
            pc += argument_size

        if fake:
            message = "{mnemon} {arguments}".format(mnemon=mnemon, arguments=hex_encoded_arguments)
            print(message)
        else:
            self._commands.execute_command(opcode, mnemon, *arguments)

    def _unpack_argument(self, argument):
        argument_bytesize = len(argument)

        if type(argument) == list:
            result = ord(argument[0]) if argument_bytesize > 1 else ord(argument)
            for index in range(argument_bytesize):
                result += 255*argument[index]*index
        elif type(argument) == bytes:
            if len(argument) == 1:
                result = struct.unpack("B", argument)[0]
            elif len(argument) == 2:
                result = struct.unpack(">H", argument)[0]
        else:
            result = ord(argument[0]) if argument_bytesize > 1 else ord(argument)
            for index in range(argument_bytesize):
                result += 255*ord(argument[index])*index

        return result

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
                if re.match(r"^\s*\n$", line) or re.match(r"^\/\/.*$", line):
                    continue
                line = line.rstrip("\n")
                line = re.sub("\s+$", "", line)
                line = re.sub(r"\/\/.+$", "", line)  # support for comments, fuck yea!
                mnemon, op, argument_sizes = line.split(",")
                argument_sizes = argument_sizes.split("|")
                argument_sizes = [int(argument_size) for argument_size in argument_sizes]
                if len(argument_sizes) == 1 and argument_sizes[0] == 0:
                    argument_sizes = []
                opcode_map[op.rstrip(" ").lower()] = {'mnemon': mnemon.rstrip(" "), 'argument_sizes': argument_sizes}
        return opcode_map


if __name__ == "__main__":
    buffer = ""  # insert image here?
    registers = Registers()
    memory = Memory()
    commands = Commands(registers, memory)
    rom = b"\xa9\x05"
    opcode_parser = OpCodeParser(rom, commands, memory, registers)

    print(registers)
    opcode_parser.step(fake=False)
    # opcode_parser.step(fake=False)
    # opcode_parser.step(fake=False)
    # opcode_parser.step(fake=False)
    # opcode_parser.step(fake=False)
    print(registers)
