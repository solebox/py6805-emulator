from memory import Memory
from registers import Registers


class Commands(object):

    def __init__(self, state: Registers, memory: Memory):
        self._state = state
        self._memory = memory
        self._address_size = self._memory.address_size
        self._register_size = self._state.general_register_size     # assuming opcode size and rgeneral
                                                                    #  register size are always the same

    def nop(self):
        self._state.pc += 1

    def __update_flags_for_add_op(self, target, value):
        if self.__valid_register_size(target) and self.__valid_register_size(value):
            result = (target + value) % 0xFF
            half_result = result & 0x0F
            half_target = result & 0x0F

            c = 1 if result < target else 0
            h = 1 if half_result < half_target else 0
            n = (result & 0x80) >> 7
            z = 0 if result else 1

            self._state.update_flags({'C': c, 'H': h, 'N': n, 'Z': z})

    def __valid_register_size(self, value):
        return self._state.is_valid_general_register_value(value)

    def add(self, value):
        """
            add to accumulator
        """
        self.__update_flags_for_add_op(self._state.a, value)
        self._state.a += value
        self._state.pc += 2

    def adc(self, value):
        """
            add to the accumulator with carry
        """
        self.add(value)
        self.add(self._state.ccr.get('C'))  # fixme - could work :)
        self._state.pc -= 2  # compansating for the double add call (what a hack ;))

    def sub(self, value):
        """
            subtract from accumulator
        """
        result = self._state.a - value
        negative = 1 if result < 0 else 0
        zero = 0 if result else 1
        carry = 1 if result < self._state.a else 0
        self._state.update_flags({'N': negative, 'Z': zero, 'C': carry})
        self._state.a = result
        self._state.pc += 2

    def sbc(self, value):
        """
            suntract from accumulator with borrow
        """
        current_carry = self._state.ccr.get('C')
        self.sub(value)
        self.sub(current_carry)
        self._state.pc -= 2  # compensating for double sub call

    def mul(self):
        """
            multiply the accumulator by index register (x)
        """
        self._state.a *= self._state.x  # fixme - need to add flag stuff
        self._state.pc += 1

    def neg(self, address):
        """
            negate a memory location
        """
        self._memory.negate(address)  # fixme - need to add flag stuff
        self._state.pc += 3  # one byte for the negate opcode 2 more for the address

    def nega(self):
        """
            negate the accumulator
        """
        self._state.a ^= 0xFF  # fixme - need to add flag stuff
        self._state.pc += 1

    def negx(self):
        """
            negate the index register
        """
        self._state.x ^= 0xFF  # fixme - need to add flag stuff
        self._state.pc += 1

    def lda(self, address):
        """
            load the accumulator
        """
        self._state.a = self._memory.read(address)  # fixme - need to add flag stuff
        self._state.pc += 3

    def ldx(self, address):
        """
            load the index register
        """
        self._memory.write(address, self._state.x)  # fixme - need to add flag stuff
        self._state.pc += 3

    def sta(self, address):
        """
            store the accumulator
        """
        self._memory.write(address, self._state.a)  # fixme - need to add flag stuff
        self._state.a += 3

    def stx(self, address):
        """
            store the index register
        """
        self._memory.write(address, self._state.x)  # fixme - need to add flag stuff
        self._state.pc += 3

    def tax(self):
        """
            transfer the accumulator to the index register
        """
        self._state.x = self._state.a  # fixme - need to add flag stuff
        self._state.pc += 1

    def txa(self):
        """
            transfer the index register to the accumulator
        """
        self._state.a = self._state.x  # fixme - need to add flag stuff
        self._state.pc += 1

    def clr(self, address):
        """
            clear a memory location
        """
        self._memory.clear_location(address)  # fixme - need to add flag stuff
        self._state.pc += 3

    def clra(self):
        """
            clear the accumulator
        """
        self._state.a = 0x0  # fixme - need to add flag stuff
        self._state.pc += 1

    def clrx(self):
        """
            clear the index register
        """
        self._state.x = 0x0  # fixme - need to add flag stuff
        self._state.pc += 1

    def inc(self, address):
        """
            increment a memory location by one
        """
        self._memory.increment(address)  # fixme - need to add flag stuff
        self._state.pc += 3

    def inca(self):
        """
            increment the acuumulator by one
        """
        self._state.a += 1  # fixme - need to add flag stuff
        self._state.pc += 1

    def incx(self):
        """
            increment the index register by one
        """
        self._state.x += 1  # fixme - need to add flag stuff
        self._state.pc += 1

    def dec(self, address):
        """
            decrement a memory location by one
        """
        self._memory.decrement(address)  # fixme - need to add flag stuff
        self._state.pc += 3

    def deca(self):
        """
            decrement accumulator by one
        """
        self._state.a -= 1  # fixme - need to add flag stuff
        self._state.pc += 1

    def decx(self):
        """
            decrement index register by one
        """
        self._state.x -= 1  # fixme - need to add flag stuff
        self._state.pc += 1

    def logical_and(self, value):
        """
            logical and of the accumulator and operand
        """
        self._state.a &= value
        z = 0 if self._state.a else 1
        n = 0 if self._state.a > 0 else 1
        self._state.update_flags({'N': n, 'Z': z})
        self._state.pc += 2

    def ora(self, value):
        """
            logical or of the accumulator and operand
        """
        self._state.a |= value  # fixme - need to add flag stuff
        self._state.pc += 2

    def eor(self, value):
        """
            exclusivve or of the accumulator and an operand
        """
        self._state.a ^= value  # fixme - need to add flag stuff
        self._state.pc += 2

    def _com(self, target, size):
        target = (~target) % size  # artifacts of 2's compliment and dynamic sizes(meh)
        carry = 1  # according to the doc its always turned into 1 , makes sense i guess...
        negative = 1 if target < 0 else 0
        zero = 0 if target else 1
        self._state.update_flags({'C': carry, 'N': negative, 'Z': zero})
        return target

    def com(self, address):
        """
            get one's complement of a memory location (the 'not' bitwise operation)
        """
        value = self._memory.read(address)
        value = self._com(value, self._address_size)
        self._memory.write(address, value)
        self._state.pc += 3

    def coma(self):
        """
            get ones complement of the accumulator
        """
        value = self._com(self._state.a, self._register_size)
        self._state.a = value
        self._state.pc += 2

    def comx(self):
        """
            get ones complement of the index register
        """
        value = self._com(self._state.a, self._register_size)
        self._state.x = value
        self._state.pc += 2

    def asl(self, address):
        """
            arithmetically shift a memory location left by one bit
        """
        if self._state._is_valid_address(address):
            value = self._memory.read(address)
            value = self._arithmetical_left_shift(value)
            self._memory.write(address, value)
            self._state.pc += 3

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
            self._state.pc += 3

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
            self._state.pc += 3

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
            self._state.pc += 3

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
        self._state.pc += 3

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
        self._state.pc += 3

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
        self._test(self._state.a)  # fixme - need to add flag stuff
        self._state.pc += 1

    def cmp(self, value):
        """
            CMP compare an operand to the accumulator
        """
        self._cmp(self._state.a, value)  # fixme - need to add flag stuff
        self._state.pc += 2

    def cpx(self, value):
        """
            CPX compare an operand to the index register
        """
        self._cmp(self._state.x, value)  # fixme - need to add flag stuff
        self._state.pc += 2

    def tst(self, address):
        """
            TST test a memory location and set the N or Z flags
        """
        value = self._memory.read(address)  # fixme - need to add flag stuff
        self._test(value)
        self._state.pc += 3

    def tsta(self):
        """
            TSTA test the accumulator and set the N or Z flags
        """
        value = self._state.a
        self._test(value)  # fixme - need to add flag stuff
        self._state.pc += 1

    def testx(self):
        """
            TSTX test the index register and set the N or Z flags
        """
        self._test(self._state.x)  # fixme - need to add flag stuff
        self._state.pc += 1

    def bcc(self, address_offset):
        """
            BCC branch if carry clear (C = 0)
        """
        if self._state.ccr.get('C') == 0:
            self._branch(address_offset)
        self._state.pc += 3

    def bcs(self, address_offset):
        """
            BCS branch if carry set (C = 1)
        """
        if self._state.ccr.get('C') == 1:
            self._branch(address_offset)
        self._state.pc += 3

    def beq(self, address_offset):
        """
            BEQ branch if equal (Z = 0)
        """
        if self._state.ccr.get('Z') == 0:
            self._branch(address_offset)
        self._state.pc += 3

    def bne(self, address_offset):
        """
            BNE branch if not equal (Z = 1)
        """
        if self._state.ccr.get('Z') == 1:
            self._branch(address_offset)
        self._state.pc += 3

    def bhcc(self, address_offset):
        """
            branch if half carry clear (H = 0)
        """
        if self._state.ccr.get('H') == 0:
            self._branch(address_offset)
        self._state.pc += 3

    def bhcs(self, address_offset):
        """
            branch if half carry set (H = 1)
        """
        if self._state.ccr.get('H') == 1:
            self._branch(address_offset)
        self._state.pc += 3

    def bhi(self, address_offset):
        """
            branch if higher (C or Z = 0)
        """
        c_flag = self._state.ccr.get('C')
        z_flag = self._state.ccr.get('Z')

        if c_flag == 0 or z_flag == 0:
            self._branch(address_offset)
        self._state.pc += 3

    def bhs(self, address_offset):
        """
            branch if half carry is set (H =1)
        """
        if self._state.ccr.get('H') == 1:
            self._branch(address_offset)

        self._state.pc += 3

    def bls(self, address_offset):
        """
            BLS branch if lower or same (C or Z = 1)
        """
        c_flag = self._state.ccr.get('C')
        z_flag = self._state.ccr.get('Z')

        if c_flag or z_flag:
            self._branch(address_offset)

        self._state.pc += 3

    def blo(self, address_offset):
        """
            BLO branch if lower (C = 1)
        """
        if self._state.ccr.get('C') == 1:
            self._branch(address_offset)
        self._state.pc += 3

    def bmi(self, address_offset):
        """
            branch if minus (N = 1)
        """
        if self._state.ccr.get('N') == 1:
            self._branch(address_offset)
        self._state.pc += 3

    def bpl(self, address_offset):
        """
            branch if plus (N = 0)
        """
        if self._state.ccr.get('N') == 0:
            self._branch(address_offset)
        self._state.pc += 3

    def bmc(self, address_offset):
        """
            BMC branch if interrupts are not masted (I = 0)
        """
        if self._state.ccr.get('I') == 0:
            self._branch(address_offset)
        self._state.pc += 3

    def bms(self, address_offset):
        """
            BMS branch if interrupts are masked (I = 1)
        """
        if self._state.ccr.get('I') == 1:
            self._branch(address_offset)
        self._state.pc += 3

    # special branches

    def bih(self, address_offset):
        """
            branch if IRQ pin is high
        """
        #fixme implement

    def bil(self, address_offset):
        """
            branch if IRQ pin is low
        """
        # fixme implement

    def bra(self, address_offset):
        """
            branch always
        """
        self._branch(address_offset)
        self._state.pc += 3

    def brn(self, address_offset):
        """
            branch never ( another nop? )
        """
        # fixme wtf
        self._state.pc += 3

    def bsr(self, address_offset):
        """
            branch to subroutine and save return address on stack
        """
        self._state.push(self._state.pc)
        self._branch(address_offset)
        self._state.pc += 3

    # single bit operations

    def bclr(self, bit):
        """
            clear the designated memory bit
        """
        #fixme - wat?!

    def bset(self, bit):
        """
            set the designated memory bit
        """
        # fixme - ffs

    def brclr(self, bit, address_offset):
        """
            branch if the designated memory bit is clear
        """
        # fixme - come on! wtf is a designated mem bit? i need to rtfm

    def brset(self, bit, address_offset):
        """
            branch if the designated memory bit is set
        """
        # fixme - ok now this is just ridiculous

    # jumps and returns
    def jmp(self, address):
        """
            JMP jumpt to specified address
        """
        self._state.pc += 3  # one byte for the jmp and another 2 bytes for the address
        self._state.pc = address

    def jsr(self, address):
        """
            JSR jump to subroutine and save return address on stack
        """
        self._state.push(self._state.pc)
        self._state.pc += 3
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
        # todo - meh

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
        # fixme - wat

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

    def _cmp(self, value, operand):
        if value == operand:
            self._state.set_flag('Z')
        else:
            self._state.clear_flag('Z')

    def _branch(self, address):
        self._state.pc = address

    def _left_shift(self, value):
        value <<= 1
        return value