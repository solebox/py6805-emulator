from memory import Memory
from registers import Registers


class Commands(object):

    def __init__(self, state: Registers, memory: Memory):
        self._state = state
        self._memory = memory
        self._address_size = self._memory.address_size
        self._register_size = self._state.general_register_size     # assuming opcode size and rgeneral
        #  register size are always the same

    def execute_command(self, opcode, command, *args):
        command = command.lower()
        if command == 'and':
            self.logical_and(*args)
        elif command in ['bset', 'bclr', 'brset', 'brclear', 'jsr', 'jmp', 'adc', 'add']:
            method = getattr(self, command)
            method(int(opcode, 16), *args)
        else:
            method = getattr(self, command)
            method(*args)

    def nop(self):
        self._state.pc += 1

    def __update_flags_for_add_op(self, target, value):
        if self.__valid_register_size(target) and self.__valid_register_size(value):
            result = (target + value) % (0xFF+1)
            half_result = result & 0x0F
            half_target = target & 0x0F

            c = 1 if result < target else 0
            h = 1 if half_result < half_target else 0
            n = (result & 0x80) >> 7
            z = 0 if result else 1

            self._state.update_flags({'C': c, 'H': h, 'N': n, 'Z': z})

    def __valid_register_size(self, value):
        return self._state.is_valid_general_register_value(value)

    def _get_flag_change(self, before, after, wrap_type):
        bits_in_general_reg = len(bin(self._state.general_register_size)) - 2
        negative = 1 if after >> (bits_in_general_reg - 1) else 0
        zero = 0 if after else 1
        if wrap_type == "underflow":
            carry = 1 if after > before else 0
        else:
            carry = 1 if after < before else 0
        return {'N': negative, 'Z': zero, 'C': carry}

    def _add(self, value):
        """
            add to accumulator
        """
        self.__update_flags_for_add_op(self._state.a, value)
        self._state.a = (self._state.a + value) % (self._state.general_register_size+1)

    def add(self, opcode, value):

        if opcode == 0xAB:  # IMM ii
            self._state.pc += 2
        if opcode == 0xBB:  # DIR dd
            value = self._memory.read(value)
            self._state.pc += 2
        if opcode == 0xCB:  # EXT hh kk
            value = self._memory.read(value)
            self._state.pc += 3
        if opcode == 0xDB:  # IX2 ee ff
            effective_address = value + self._state.x
            value = self._memory.read(effective_address)
            self._state.pc += 3
        if opcode == 0xEB:  # IX1 ff
            effective_address = value + self._state.x
            value = self._memory.read(effective_address)
            self._state.pc += 2
        if opcode == 0xFB:  # IX
            value = self._memory.read(self._state.x)
            self._state.pc += 1

        self._add(value)

    def adc(self, opcode, value=None):
        """
            add to the accumulator with carry
        """
        carry = self._state.ccr.get('C')
        self._add(carry)

        if opcode == 0xA9:  # IMM ii
            self._state.pc += 2

        if opcode == 0xB9:  #DIR dd - direct addressing
            value = self._memory.read(value)
            self._state.pc += 2

        if opcode == 0xC9:  # EXT hh ll - extended direct addressing
            value = self._memory.read(value)
            self._state.pc += 3 # one more because we have an extra byte in ext

        if opcode == 0xD9:  # IX2 ee ff - indexed 16 bit
            effective_address = self._state.x + value
            value = self._memory.read(effective_address)
            self._state.pc += 3

        if opcode == 0xE9:  # IX1 ff - indexed 8 bit
            effective_address = self._state.x + value
            value = self._memory.read(effective_address)
            self._state.pc += 2

        if opcode == 0xF9:  # IX - indexed no offset
            effective_address = self._state.x
            value = self._memory.read(effective_address)
            self._state.pc += 1  # just opcode baby

        self._add(value)

    def _sub(self, value):
        bits_in_general_reg = len(bin(self._state.general_register_size)) - 2
        result = (self._state.a - value) % (self._state.general_register_size+1)
        flags = self._get_flag_change(value, result, "underflow")
        negative, zero, carry = flags['N'], flags['Z'], flags['C']
        self._state.update_flags({'N': negative, 'Z': zero, 'C': carry})
        self._state.a = result

    def sub(self, opcode, value):
        """
            subtract from accumulator
        """
        if opcode == 0xA0:  # IMM ii
            self._state.pc += 2
        if opcode == 0xB0:  # DIR dd
            value = self._memory.read(value)
            self._state.pc += 2
        if opcode == 0xC0:  # EXT hh kk
            value = self._memory.read(value)
            self._state.pc += 3
        if opcode == 0xD0:  # IX2 ee ff
            effective_address = value + self._state.x
            value = self._memory.read(effective_address)
            self._state.pc += 3
        if opcode == 0xE0:  # IX1 ff
            effective_address = value + self._state.x
            value = self._memory.read(effective_address)
            self._state.pc += 2
        if opcode == 0xF0:  # IX
            value = self._memory.read(self._state.x)
            self._state.pc += 1

        self._sub(value)

    def sbc(self, opcode, value):
        """
            suntract from accumulator with borrow
        """

        if opcode == 0xA2:  # IMM ii
            self._state.pc += 2

        if opcode == 0xB2:  #DIR dd - direct addressing
            value = self._memory.read(value)
            self._state.pc += 2

        if opcode == 0xC2:  # EXT hh ll - extended direct addressing
            value = self._memory.read(value)
            self._state.pc += 3 # one more because we have an extra byte in ext

        if opcode == 0xD2:  # IX2 ee ff - indexed 16 bit
            effective_address = self._state.x + value
            value = self._memory.read(effective_address)
            self._state.pc += 3

        if opcode == 0xE2:  # IX1 ff - indexed 8 bit
            effective_address = self._state.x + value
            value = self._memory.read(effective_address)
            self._state.pc += 2

        if opcode == 0xF2:  # IX - indexed no offset
            effective_address = self._state.x
            value = self._memory.read(effective_address)
            self._state.pc += 1  # just opcode baby

        current_carry = self._state.ccr.get('C')
        self._sub(value)
        self._sub(current_carry)

    def mul(self):
        """
            doesnt exist in 6805 microprocessor opcodes , maybe just for younger family members
            multiply the accumulator by index register (x)
        """
        self._state.a *= self._state.x  # fixme - need to look for opcode and add flag stuff (mul doesnt exist in doc)
        self._state.pc += 1

    def _neg(self, value):
        result = value ^ 0xFF % (self._state.general_register_size+1)
        bits_in_general_reg = len(bin(self._state.general_register_size)) - 2
        # negative = 1 if result >> (bits_in_general_reg - 1) else 0
        # zero = 0 if result else 1
        # carry = 1 if result > value else 0
        flags = self._get_flag_change(value, result, "overflow")
        negative, zero, carry = flags['N'], flags['Z'], flags['C']
        self._state.update_flags({'N': negative, 'Z': zero, 'C': carry})
        return result

    def neg(self, opcode, operand):
        """
            negate a memory location
        """
        value = None
        address = operand
        if opcode == 0xB2:  #DIR dd - direct addressing
            value = self._memory.read(operand)
            self._state.pc += 2

        if opcode == 0xE2:  # IX1 ff - indexed 8 bit
            address = self._state.x + operand
            value = self._memory.read(address)
            self._state.pc += 2

        if opcode == 0xF2:  # IX - indexed no offset
            address = self._state.x
            value = self._memory.read(address)
            self._state.pc += 1  # just opcode baby

        value = self._neg(value)
        self._memory.write(address, value)


    def nega(self):
        """
            negate the accumulator
        """
        value = self._neg(self._state.a)
        self._state.a = value
        self._state.pc += 1

    def negx(self):
        """
            negate the index register
        """

        value = self._neg(self._state.x)
        self._state.x = value
        self._state.pc += 1

    def lda(self, address):
        """
            load the accumulator
        """
        bits_in_general_reg = len(bin(self._state.general_register_size)) - 2
        self._state.a = self._memory.read(address)
        result = self._state.a
        flags = self._get_flag_change(result, result, "overflow")
        negative, zero = flags['N'], flags['Z']
        self._state.update_flags({'N': negative, 'Z': zero})
        self._state.pc += 2

    def ldx(self, address):
        """
            load the index register
        """
        self._memory.write(address, self._state.x)
        result = self._state.x
        flags = self._get_flag_change(result, result, "overflow")
        negative, zero = flags['N'], flags['Z']
        self._state.update_flags({'N': negative, 'Z': zero})
        self._state.pc += 2

    def sta(self, address):
        """
            store the accumulator
        """
        self._memory.write(address, self._state.a)
        result = self._state.a
        flags = self._get_flag_change(result, result, "overflow")
        negative, zero = flags['N'], flags['Z']
        self._state.update_flags({'N': negative, 'Z': zero})
        self._state.a += 2

    def stx(self, address):
        """
            store the index register
        """
        self._memory.write(address, self._state.x)
        result = self._state.x
        flags = self._get_flag_change(result, result, "overflow")
        negative, zero = flags['N'], flags['Z']
        self._state.update_flags({'N': negative, 'Z': zero})
        self._state.pc += 2

    def tax(self):
        """
            transfer the accumulator to the index register
        """
        self._state.x = self._state.a
        self._state.pc += 1

    def txa(self):
        """
            transfer the index register to the accumulator
        """
        self._state.a = self._state.x
        self._state.pc += 1

    def clr(self, address):
        """
            clear a memory location
        """
        self._memory.write(address, 0x0)
        self._state.update_flags({'N': 0, 'Z': 1})
        self._state.pc += 2

    def clra(self):
        """
            clear the accumulator
        """
        self._state.a = 0x0
        self._state.update_flags({'N': 0, 'Z': 1})
        self._state.pc += 1

    def clrx(self):
        """
            clear the index register
        """
        self._state.x = 0x0
        self._state.update_flags({'N': 0, 'Z': 1})
        self._state.pc += 1

    def inc(self, address):
        """
            increment a memory location by one
        """
        value = self._memory.read(address)
        result = (value + 1) & 0xFF
        flags = self._get_flag_change(result, result, "overflow")
        negative, zero = flags['N'], flags['Z']
        self._state.update_flags({'N': negative, 'Z': zero})
        self._memory.write(address, result)
        self._state.pc += 2

    def inca(self):
        """
            increment the acuumulator by one
        """
        result = self._state.a + 1
        flags = self._get_flag_change(result, result, "overflow")
        negative, zero = flags['N'], flags['Z']
        self._state.update_flags({'N': negative, 'Z': zero})
        self._state.a = result
        self._state.pc += 1

    def incx(self):
        """
            increment the index register by one
        """
        result = self._state.x + 1
        flags = self._get_flag_change(result, result, "overflow")
        negative, zero = flags['N'], flags['Z']
        self._state.update_flags({'N': negative, 'Z': zero})
        self._state.x = result
        self._state.pc += 1

    def dec(self, address):
        """
            decrement a memory location by one
        """
        value = self._memory.read(address)
        result = (value - 1) & 0xFF
        flags = self._get_flag_change(result, result, "underflow")
        negative, zero = flags['N'], flags['Z']
        self._state.update_flags({'N': negative, 'Z': zero})
        self._memory.write(address, result)
        self._state.pc += 2

    def deca(self):
        """
            decrement accumulator by one
        """
        result = self._state.a - 1
        flags = self._get_flag_change(result, result, "underflow")
        negative, zero = flags['N'], flags['Z']
        self._state.update_flags({'N': negative, 'Z': zero})
        self._state.a = result
        self._state.pc += 1

    def decx(self):
        """
            decrement index register by one
        """
        result = self._state.x - 1
        flags = self._get_flag_change(result, result, "underflow")
        negative, zero = flags['N'], flags['Z']
        self._state.update_flags({'N': negative, 'Z': zero})
        self._state.x = result
        self._state.pc += 1

    def logical_and(self, value):
        """
            logical and of the accumulator and operand
        """
        self._state.a &= value
        flags = self._get_flag_change(self._state.a, self._state.a, "underflow")
        negative, zero = flags['N'], flags['Z']
        self._state.update_flags({'N': negative, 'Z': zero})
        self._state.pc += 2

    def ora(self, value):
        """
            logical or of the accumulator and operand
        """
        self._state.a |= value
        flags = self._get_flag_change(self._state.a, self._state.a, "underflow")
        negative, zero = flags['N'], flags['Z']
        self._state.update_flags({'N': negative, 'Z': zero})
        self._state.pc += 2

    def eor(self, value):
        """
            exclusivve or of the accumulator and an operand
        """
        self._state.a ^= value
        flags = self._get_flag_change(self._state.a, self._state.a, "underflow")
        negative, zero = flags['N'], flags['Z']
        self._state.update_flags({'N': negative, 'Z': zero})
        self._state.pc += 2

    def _com(self, target, size):
        target = (~target) % size  # artifacts of 2's compliment and dynamic sizes(meh)
        carry = 1  # according to the doc its always turned into 1 , makes sense i guess...
        flags = self._get_flag_change(self._state.a, self._state.a, "underflow")
        negative, zero = flags['N'], flags['Z']
        self._state.update_flags({'C': carry, 'N': negative, 'Z': zero})
        return target

    def com(self, address):
        """
            get one's complement of a memory location (the 'not' bitwise operation)
        """
        value = self._memory.read(address)
        value = self._com(value, self._address_size)
        self._memory.write(address, value)
        self._state.pc += 2

    def coma(self):
        """
            get ones complement of the accumulator
        """
        value = self._com(self._state.a, self._register_size)
        self._state.a = value
        self._state.pc += 1

    def comx(self):
        """
            get ones complement of the index register
        """
        value = self._com(self._state.a, self._register_size)
        self._state.x = value
        self._state.pc += 1

    def asl(self, address):
        """
            arithmetically shift a memory location left by one bit
        """
        if self._state._is_valid_address(address):
            value = self._memory.read(address)
            value = self._arithmetical_left_shift(value)
            self._memory.write(address, value)
            self._state.pc += 2

    def asla(self):
        """
            arithmetically shift the accumulator left by one bit
        """
        value = self._state.a
        self._state.a = self._arithmetical_left_shift(value)
        self._state.pc += 1

    def aslx(self):
        """
            arithmetically shift the index register left by one bit
        """
        value = self._state.x
        self._state.x = self._arithmetical_left_shift(value)
        self._state.pc += 1

    def asr(self, address):
        """
            arithmetically shift a memory location right by one bit
        """
        if self._state._is_valid_address(address):
            value = self._memory.read(address)
            value = self._arithmetic_right_shift(value)
            self._memory.write(address, value)
            self._state.pc += 2

    def asra(self):
        """
            arithmetically shift the accumulator right by one bit
        """
        value = self._state.a
        self._state.a = self._arithmetic_right_shift(value)
        self._state.pc += 1

    def asrx(self):
        """
            arithmetically shift the index register by one bit
        """
        value = self._state.x
        self._state.x = self._arithmetic_right_shift(value)
        self._state.pc += 1

    def lsl(self, address):
        """
            logically shift a memory location left by one bit
        """
        if self._state._is_valid_address(address):
            value = self._memory.read(address)
            value = self._logical_left_shift(value)
            self._memory.write(address, value)
            self._state.pc += 2

    def lsla(self):
        """
            LSLA logically shift the accumulator left by one bit
        """
        value = self._state.a
        self._state.a = self._logical_left_shift(value)
        self._state.pc += 1

    def lslx(self):
        """
            LSLX logically shift the index register left by one bit
        """
        value = self._state.x
        self._state.x = self._logical_left_shift(value)
        self._state.pc += 1

    def lsr(self, address):
        """
            LSR logically shift a memory location right by one bit
        """
        if self._state._is_valid_address(address):
            value = self._memory.read(address)
            value = self._logical_right_shift(value)
            self._memory.write(address, value)
            self._state.pc += 2

    def lsra(self):
        """
            LSRA logically shift the accumulator right by one bit
        """
        value = self._state.a
        self._state.a = self._logical_right_shift(value)
        self._state.pc += 1

    def lsrx(self):
        """
            LSRX logically shift the index register right by one bit
        """
        value = self._state.x
        self._state.x = self._logical_right_shift(value)
        self._state.pc += 1

    def rol(self, address):
        """
            ROL rotate a memory location left by one bit
        """
        value = self._memory.read(address)
        value = self._rol(value, 1)
        self._memory.write(address, value)
        self._state.pc += 2

    def rola(self):
        """
            ROLA rotate the accumulator left by one bit
        """
        self._state.a = self._rol(self._state.a, 1)
        self._state.pc += 1

    def rolx(self):
        """
            ROLX rotate the index register left by one bit
        """
        self._state.x = self._rol(self._state.x, 1)
        self._state.pc += 1

    def ror(self, address):
        """
            ROR rotate a memory location right by one bit
        """
        value = self._memory.read(address)
        value = self._ror(value, 1)
        self._memory.write(address, value)
        self._state.pc += 2

    def rora(self):
        """
            RORA rotate the accumulator right by one bit
        """
        self._state.a = self._ror(self._state.a, 1)
        self._state.pc += 1

    def rorx(self):
        """
            RORX rotate the index register right by one bit
        """
        self._state.x = self._ror(self._state.x, 1)
        self._state.pc += 1

    def bit(self):
        """
            BIT bit test the accumulator and set the N or Z flags
        """
        self._test(self._state.a)
        self._state.pc += 1

    def cmp(self, value):
        """
            CMP compare an operand to the accumulator
        """
        self._cmp(self._state.a, value)
        self._state.pc += 2

    def cpx(self, value):
        """
            CPX compare an operand to the index register
        """
        self._cmp(self._state.x, value)
        self._state.pc += 2

    def tst(self, address):
        """
            TST test a memory location and set the N or Z flags
        """
        value = self._memory.read(address)
        self._test(value)
        self._state.pc += 2

    def tsta(self):
        """
            TSTA test the accumulator and set the N or Z flags
        """
        value = self._state.a
        self._test(value)
        self._state.pc += 1

    def tstx(self):
        """
            TSTX test the index register and set the N or Z flags
        """
        self._test(self._state.x)
        self._state.pc += 1

    def bcc(self, address_offset):
        """
            BCC branch if carry clear (C = 0)
        """
        if self._state.ccr.get('C') == 0:
            self._branch(address_offset)
        self._state.pc += 2

    def bcs(self, address_offset):
        """
            BCS branch if carry set (C = 1)
        """
        if self._state.ccr.get('C') == 1:
            self._branch(address_offset)
        self._state.pc += 2

    def beq(self, address_offset):
        """
            BEQ branch if equal (Z = 0)
        """
        if self._state.ccr.get('Z') == 0:
            self._branch(address_offset)
        self._state.pc += 2

    def bne(self, address_offset):
        """
            BNE branch if not equal (Z = 1)
        """
        if self._state.ccr.get('Z') == 1:
            self._branch(address_offset)
        self._state.pc += 2

    def bhcc(self, address_offset):
        """
            branch if half carry clear (H = 0)
        """
        if self._state.ccr.get('H') == 0:
            self._branch(address_offset)
        self._state.pc += 2

    def bhcs(self, address_offset):
        """
            branch if half carry set (H = 1)
        """
        if self._state.ccr.get('H') == 1:
            self._branch(address_offset)
        self._state.pc += 2

    def bhi(self, address_offset):
        """
            branch if higher (C or Z = 0)
        """
        c_flag = self._state.ccr.get('C')
        z_flag = self._state.ccr.get('Z')

        if c_flag == 0 or z_flag == 0:
            self._branch(address_offset)
        self._state.pc += 2

    def bhs(self, address_offset):
        """
            branch if half carry is set (H =1)
        """
        if self._state.ccr.get('H') == 1:
            self._branch(address_offset)

        self._state.pc += 2

    def bls(self, address_offset):
        """
            BLS branch if lower or same (C or Z = 1)
        """
        c_flag = self._state.ccr.get('C')
        z_flag = self._state.ccr.get('Z')

        if c_flag or z_flag:
            self._branch(address_offset)

        self._state.pc += 2

    def blo(self, address_offset):
        """
            BLO branch if lower (C = 1)
        """
        if self._state.ccr.get('C') == 1:
            self._branch(address_offset)
        self._state.pc += 2

    def bmi(self, address_offset):
        """
            branch if minus (N = 1)
        """
        if self._state.ccr.get('N') == 1:
            self._branch(address_offset)
        self._state.pc += 2

    def bpl(self, address_offset):
        """
            branch if plus (N = 0)
        """
        if self._state.ccr.get('N') == 0:
            self._branch(address_offset)
        self._state.pc += 2

    def bmc(self, address_offset):
        """
            BMC branch if interrupts are not masted (I = 0)
        """
        if self._state.ccr.get('I') == 0:
            self._branch(address_offset)
        self._state.pc += 2

    def bms(self, address_offset):
        """
            BMS branch if interrupts are masked (I = 1)
        """
        if self._state.ccr.get('I') == 1:
            self._branch(address_offset)
        self._state.pc += 2

    # special branches

    def bih(self, address_offset):
        """
            branch if IRQ pin is high
        """
        #fixme implement
        self._state.pc += 2

    def bil(self, address_offset):
        """
            branch if IRQ pin is low
        """
        # fixme implement
        self._state.pc += 2

    def bra(self, address_offset):
        """
            branch always
        """
        self._branch(address_offset)
        self._state.pc += 2

    def brn(self, address_offset):
        """
            branch never ( another nop? )
        """
        # todo - is this another nop?
        self._state.pc += 2

    def bsr(self, address_offset):
        """
            branch to subroutine and save return address on stack
        """
        self._state.push(self._state.pc)
        self._state._sp -= 1
        self._state.pc += 2
        self._branch(address_offset)


    # single bit operations

    def bclr(self, opcode, address):
        """
            clear the designated memory bit
        """
        bit = (opcode & 0xE) / 2
        value = self._memory.read(address)
        mask = (1 << bit) ^ 0xFF
        value &= mask
        self._memory.write(address, value)
        self._state.pc += 2

    def bset(self, opcode, address):
        """
            set the designated memory bit
        """
        bit = (opcode & 0xE) / 2
        value = self._memory.read(address)
        mask = (1 << bit)
        value |= mask
        self._memory.write(address, value)
        self._state.pc += 2

    def brclr(self, opcode, value, address):
        """
            branch if the designated memory bit is clear
        """
        bit = (opcode & 0x0E) / 2
        mask = (1 << bit)
        address = self._state.pc + address if (value & mask) == 0 else self._state.pc
        self._state.pc = address

    def brset(self, opcode, value, address_offset):
        """
            branch if the designated memory bit is set
        """
        bit = (opcode & 0x0E) / 2
        address = self._state.pc + address_offset
        mask = (1 << bit)
        address = self._state.pc + address_offset if (value & mask) != 0 else self._state.pc
        self._state.pc = address

    # jumps and returns
    def jmp(self, opcode, address=0x00):
        """
            JMP jumpt to specified address
        """

        self._state.push(self._state.pc) # save the return address hun , its dangerous outside ;)

        if opcode == 0xfc:  # indexed no offser (first bytes is 0x00 second is from the index reg)
            self._state.pc += 1 # just the instruction , no params
            self._state.pc = self._state.x

        if opcode == 0xec:  # indexed 8bit offset (
            self._state.pc += 2  # opcode + rel (i know it doesnt matter but i used em for ref - dont judge me :))
            effective_address = self._state.x + address # index reg plus the following byte (both unsigned) (can access up to 0x01fe) looks legit
            self._state.pc = effective_address

        if opcode == 0xdc:  # Indexed, 16-bit offset addressing mode
            self._state.pc += 3
            effective_address = self._state.x + address  # this offset is 2 bytes in size not one , dont be fooled
            self._state.pc = effective_address

        if opcode == 0xcc:  # this is extended mode
            self._state.pc += 3
            self._state.pc = address  # 2 bytes, simply go there biach

        if opcode == 0xbc:  # direct
            self._state.pc += 2
            self._state.pc = address


    def jsr(self, opcode, address=0x00):
        """
            JSR jump to subroutine and save return address on stack
        """
        self._state.push(self._state.pc) # save the return address hun , its dangerous outside ;)

        if opcode == 0xfd:  # indexed no offser (first bytes is 0x00 second is from the index reg)
            self._state.pc += 1 # just the instruction , no params
            self._state.pc = self._state.x
        if opcode == 0xed:  # indexed 8bit offset (
            self._state.pc += 2  # opcode + rel (i know it doesnt matter but i used em for ref - dont judge me :))
            effective_address = self._state.x + address # index reg plus the following byte (both unsigned) (can access up to 0x01fe) looks legit
            self._state.pc = effective_address
        if opcode == 0xdd:  # Indexed, 16-bit offset addressing mode
            self._state.pc += 3
            effective_address = self._state.x + address  # this offset is 2 bytes in size not one , dont be fooled
            self._state.pc = effective_address
        if opcode == 0xcd:  # this is extended mode
            self._state.pc += 3
            self._state.pc = address  # 2 bytes, simply go there biach
        if opcode == 0xbd:  # direct
            self._state.pc += 2
            self._state.pc = address

    def rts(self):
        """
            RTS pull address from stack and return from subroutine
        """
        address = self._state.pop()
        self._state.pc += 1
        self._state.pc = address

    def rti(self):
        """
            RTI pull registers from stack and return from interrupt
        """
        ccr = self._state.pop()
        a = self._state.pop()
        x = self._state.pop()
        pc = self._state.pop()  # fixme - PCL PCH (does it matter if its all hardware?)
        self._state.update_flags(ccr)
        self._state.a = a
        self._state.x = x
        self._state.pc = pc

    # misc control
    def clc(self):
        """
            CLC clear the condition code register carry bit
        """
        self._state.clear_flag('C')
        self._state.pc += 1

    def sec(self):
        """
            SEC set the condition code register carry bit
        """
        self._state.set_flag('C')
        self._state.pc += 1

    def cli(self):
        """
            CLI clear the condition code register interrupt mask bit
        """
        self._state.clear_flag('I')
        self._state.pc += 1

    def sei(self):
        """
            SEI set the condition code register interrupt mask bit
        """
        self._state.set_flag('I')
        self._state.pc += 1

    def swi(self):
        """
            SWI software initiated interrupt
        """
        ccr = self._state.ccr
        a = self._state.a
        x = self._state.x
        pc = self._state.pc
        self._state.push(pc) # fixme - PCL PCH (does it matter if its all hardware?)
        self._state.push(x)
        self._state.push(a)
        self._state.push(ccr)

    def rsp(self):
        """
            RSP reset the stack pointer to $00FF
        """
        self._state.reset_stack_pointer(0x00FF)
        self._state.pc += 1

    def wait(self):
        """
            WAIT enable interrupts and halt the CPU
        """
        # fixme - yet again - wat - hardware software watware?

    def stop(self):
        """
            STOP enable interrupts and stop the oscillator
        """
        # fixme - if i halt myself how can i stop halting? man this pic emulation is becoming philosophical

    # helper functions

    def _arithmetic_right_shift(self, value):
        most_segnificant_bit = 0x80 & value
        value >>= 1
        value |= most_segnificant_bit
        return value

    def _logical_right_shift(self, value):
        result = value >> 1
        negative = 0  # doc
        zero = 0 if value else 1
        carry = 1 if result < value else 0
        self._state.update_flags({'N': negative, 'Z': zero, 'C': carry})
        return result

    def _arithmetical_left_shift(self, value):
        result = self._left_shift(value)
        negative = 1 if result < 0 else 0
        zero = 0 if result else 1
        carry = 1 if result < value else 0
        self._state.update_flags({'N': negative, 'Z': zero, 'C': carry})
        return result

    def _logical_left_shift(self, value):
        result = self._left_shift(value)
        negative = 0  # doc said it , what are you looking at me for?!
        zero = 0 if result else 1
        carry = 1 if result < value else 0
        self._state.update_flags({'N': negative, 'Z': zero, 'C': carry})
        return result

    def _rol(self, value, rotate_by):
        """
            bitwise rotate left
        """

        max_bits = 8
        result = (value << rotate_by % max_bits) & (2 ** max_bits - 1) | \
                 ((value & (2 ** max_bits - 1)) >> (max_bits - (rotate_by % max_bits)))
        negative = 1 if result < 0 else 0
        zero = 0 if result else 1
        carry = 1 if result < value else 0
        self._state.update_flags({'N': negative, 'Z': zero, 'C': carry})
        return result

    def _ror(self, value, rotate_by):
        """
            bitwise rotate right
        """
        max_bits = 8
        result = ((value & (2 ** max_bits - 1)) >> rotate_by % max_bits) | \
                 (value << (max_bits - (rotate_by % max_bits)) & (2 ** max_bits - 1))
        negative = 1 if result < 0 else 0
        zero = 0 if result else 1
        carry = 1 if result < value else 0
        self._state.update_flags({'N': negative, 'Z': zero, 'C': carry})
        return result

    def _test(self, value):
        if value == 0:
            self._state.set_flag('Z')
        elif value < 0:
            self._state.set_flag('N')
        else:
            self._state.clear_flag('Z')
            self._state.clear_flag('N')

    def _cmp(self, register, operand):
        result = (register - operand) % (self._state.general_register_size+1)
        zero = 0 if result else 1
        negative = 1 if result < 0 else 1
        carry = 1 if result < register else 1
        self._state.update_flags({'Z': zero, 'N': negative, 'C': carry})

    def _branch(self, relative_address):
        self._state.pc += relative_address

    def _left_shift(self, value):
        value <<= 1
        return value