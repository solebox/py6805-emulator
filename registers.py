from memory import Stack


class Registers(object):

    def __init__(self):
        self._address_size = 0xFFFF
        self._general_register_size = 0xFF
        self._a = 0x0
        self._x = 0x0
        self._pc = 0x0
        self._CCR = {'C': 0, 'Z': 0, 'N': 0, 'I': 0, 'H': 0, 5: 1, 6: 1, 7: 1}
        self._stack = Stack(size=64, start=0x00FF)  # fixme find out real specs of stack
        self._sp = self._stack.sp
        self._hardware_interrupt_queue = []

    def enqueue_hardware_interrupt(self, interrupt):
        self._hardware_interrupt_queue.push(interrupt)

    def dequeue_hardware_interrupt(self):
        interrupt = self._hardware_interrupt_queue.pop(0)
        return interrupt

    def are_there_any_hardware_interruprs(self):
        return len(self._hardware_interrupt_queue) > 0

    def __str__(self):
        flags = {'C': self._CCR['C'], 'Z': self._CCR['Z'], 'N': self._CCR['N'], 'I': self._CCR['I'], 'H': self._CCR['H']}
        string_representation = """
            a: {a:#0{register_hex_length}x}, x: {x:#0{register_hex_length}x}
            flags: {flags}
            pc: {pc:#0{address_hex_length}x}, sp: {sp:#0{address_hex_length}x}
        """.format(a=self._a, x=self._x, flags=flags, pc=self._pc, sp=self._sp, address_hex_length=6, register_hex_length=4)
        return string_representation

    def is_valid_general_register_value(self, value):
        if value not in range(0x0, self.general_register_size+1):
            raise ValueError("value exceeding register size {}".format(hex(value)))
        return True

    def _is_valid_address(self, address):
        if address not in range(0x0, self._address_size+1):
            raise ValueError("address out of range {}".format(address))
        return True

    @property
    def general_register_size(self):
        return self._general_register_size

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, value):
        if self.is_valid_general_register_value(value):
            self._a = value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if self.is_valid_general_register_value(value):
            self._x = value

    @property
    def pc(self):
        return self._pc

    @pc.setter
    def pc(self, value):
        if value not in  range(0x0, 0xFFFF):
            raise ValueError("pc should be 16 bit max")
        self._pc = value

    @property
    def ccr(self):
        return self._CCR

    def toggle_half_carry(self):
        self.toggle_flag('H')

    def toggle_interrupt_mask(self):
        self.toggle_flag('I')

    def toggle_negative_flag(self):
        self.toggle_flag('N')

    def toggle_zero_flag(self):
        self.toggle_flag('Z')

    def toggle_carry_flag(self):
        self.toggle_flag('C')

    def toggle_flag(self, flag):
        self._CCR[flag] ^= 0x1

    def set_flag(self, flag):
        self._CCR[flag] = 0x1

    def clear_flag(self, flag):
        self._CCR[flag] = 0x0

    def update_flags(self, flag_dictionary):
        for flag, value in flag_dictionary.items():
            self._CCR[flag] = value

    def push(self, value):
        self._stack.push(value)

    def pop(self):
        return self._stack.pop()

    def reset_stack_pointer(self, address):
        self._stack.reset_stack_pointer(address)
