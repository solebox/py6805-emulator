import inspect
import random
import struct

class Memory(object):

    def __init__(self):
        self._ram = range(0x0, 0x20)
        self._rom = range(0x100, )
        self.address_size = 0xFFFF
        self._memory = {}

    def write_buffer_to_memory(self, start_address, buffer):
        if type(start_address) == bytes:
            address = struct.unpack(">H", start_address)[0] # big endian 2 bytes address
        elif type(start_address) == str:
            address = int(start_address, 16)
        elif type(start_address) == int:
            address = start_address
        else:
            raise ValueError("invalid address format")

        for value in buffer:
            self.write(address, value)
            address += 1

    def read(self, address):
        value = self._memory.get(address, 0)
        return value

    def write(self, address, value):
        self._memory[address] = value

    def negate(self, address):
        pass  # fixme - implement please

    def clear_location(self, address):
        self._memory[address] = 0x00

    def increment(self, address):
        self._memory[address] += 1

    def decrement(self, address):
        self._memory[address] -= 1


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
        # fixme - make the stack circular
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
