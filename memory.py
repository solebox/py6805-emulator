import inspect
import random
import struct


class Memory(object):

    def __init__(self):
        self._ram = range(0x0, 0x20)
        self._rom = range(0x100, )
        self.address_size = 0xFFFF
        self._memory = {}

    def __str__(self):
        result = ""
        for address, value in self._memory.items():
            result += "{0:#06X}: {1:#04X}\n".format(address, value)
        return str(result)

    def __next__(self):
        for address, value in self._memory.items():
            yield "{0:#06X}: {1:#04X}\n".format(address, value)

    def write_buffer_to_memory(self, start_address, buffer):

        address = start_address
        for value in buffer:
            self.write(address, value)
            address += 1

    def read(self, read_address):
        address = self._convert_address(read_address)
        value = self._memory.get(address, 0x9d)
        return value

    def write(self, write_address, value):
        address = self._convert_address(write_address)
        self._memory[address] = value

    def _convert_address(self, original_address):
        """
        converts address that comes in few different formats into int
        accepts bytes, string and int
        :param original_address: int/bytes/string address representation
        :return: int address representation
        :throws: ValueError - if invalid address format
        """
        if type(original_address) == bytes:
            address = struct.unpack(">H", original_address)[0]  # big endian 2 bytes address
        elif type(original_address) == str:
            address = int(original_address, 16)
        elif type(original_address) == int:
            address = original_address
        else:
            raise ValueError("invalid address format")
        return address


class Metalog(type):

    def logit(cls, value):
        def zz():
            print("zzz")
        return zz

    def __new__(mcs, classname, bases, body):
        for name, value in body.items():
            if not inspect.isfunction(value):
                continue
            body[name] = mcs.logit(value)
        return super(Metalog, mcs).__new__(mcs, classname, bases, body)


class Stack(object):

    def __init__(self, size=64, start=0x00FF):
        """
            defaults are from the 6800 family ref
            size - size of the stack in bytes
            start - the start address

            this is our stack , its supposed to be circular , hardware controlled and it grows downwards.
        """
        self._stack_size = size
        self._stack_top = start
        self._stack_bottom = self._stack_top - self._stack_size + 1
        self._sp = self._stack_top - self._stack_bottom
        self._stack = [int(random.random()*100) for _ in range(size)]
        print("sp: {}".format(self._sp))
        print("stack bottom: {}".format(hex(self._stack_bottom)))
        print("stack top: {}".format(hex(self._stack_top)))

    @property
    def sp(self):
        return self._sp + self._stack_bottom

    @sp.setter
    def sp(self, value):
        if value not in range(0x0, 0xFFFF):
            raise ValueError("sp should be 16 bit max")
        self._sp = value - self._stack_bottom

    def push(self, value):
        # fist we put the value then we check if its the last memory address, if it is we come back to the start
        self._sp -= 1
        self._set_push_val(value)
        if self.sp == (self._stack_bottom):
            self.sp = self._stack_top

    def pop(self):
        if self.sp == self._stack_top:
            self.sp = self._stack_bottom
        value = self._get_pop_val()
        self._sp += 1
        return value

    def reset_stack_pointer(self, address):
        self.sp = address

    def _set_push_val(self, value):
        self._stack[self._sp] = value

    def _get_pop_val(self):
        value = self._stack[self._sp]
        return value


def test_underflow():
    stack = Stack(size=64, start=0x00FF)
    stack.pop()
    assert(stack.sp == stack._stack_bottom+1)


def test_overflow():
    stack = Stack(size=64, start=0x00FF)
    for num in range(64):
        stack.push(num)
    assert(stack.sp == stack._stack_top - 1)

if __name__ == "__main__":

    test_underflow()
    test_overflow()
