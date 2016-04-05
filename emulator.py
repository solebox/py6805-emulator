import sys


class Memory(object):

    def __init__(self):
        self._ram = range(0x0, 0x20)
        self._rom = range(0x100, )
        self._memory = {}

    def read(self, address):
        return self._memory.get(address, None)

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


class State(object):

    def __init__(self):
        self._a = 0x0
        self._x = 0x0
        self._sp = 0x0000000011
        self._pc = 0x0
        self._CCR = {'C':0, 'Z': 0, 'N': 0, 'I': 0, 'H': 0, 5: 1, 6: 1, 7: 1}

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, value):
        if value not in range(0x0, 0xFF):
            raise ValueError("pc should be 8 bit max")
        self._a = value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if value not in range(0x0, 0xFF):
            raise ValueError("pc should be 8 bit max")
        self._x = value

    @property
    def sp(self):
        return self._sp

    @sp.setter
    def sp(self, value):
        if value not in range(0x0, 0xFFFF):
            raise ValueError("sp should be 16 bit max")
        self._sp = value

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


class OpCodeParser(object):

    def __init__(self, commands_and_control):
        self._commands_and_control = commands_and_control
        self._opcode_index = self._init_opcodes(self._commands_and_control)


    def _init_opcodes(self, commands_and_control):
        opcodes = {
            0x01 : commands_and_control.nop,
        }
        return opcodes


class _CommandsAndControl(object):

    def __init__(self, state, memory):
        self._state = state
        self._memory = memory

    def nop(self):
        self._state.pc += 1


    def add(self, value):
        """
            add to accumulator
        """
        self._state.a += value
        self._state.pc += 2

    def adc(self, state, value):
        """
            add to the accumulator with carry
        """
        #fixme - implement
        pass

    def sub(self, value):
        """
            subtract from accumulator
        """
        self._state.a -= value
        self._state.pc += 2

    def sbc(self, state, value):
        """
            suntract from accumulator with borrow
        """
        #fixme - implement
        pass

    def mul(self):
        """
            multiply the accumulator by index register (x)
        """
        self._state.a *= self._state.x
        self._state.pc += 1

    def neg(self, address):
        """
            negate a memory location
        """
        self._memory.negate(address)
        self._state.pc += 2

    def nega(self):
        """
            negate the accumulator
        """
        self._state.a ^= 0xFF
        self._state.pc += 1

    def negx(self):
        """
            negate the index register
        """
        self._state.x ^= 0xFF
        self._state.pc += 1

    def lda(self, state):
        """
            load the accumulator
        """
        pass

    def ldx(self, state):
        """
            load the index register
        """
        pass

    def sta(self, state):
        """
            store the accumulator
        """
        pass

    def stx(self, state):
        """
            store the index register
        """
        pass

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
        self._memory.clear_location(address)
        self._state.pc += 2

    def clra(self):
        """
            clear the accumulator
        """
        self._state.a = 0x0
        self._state.pc += 1

    def clrx(self):
        """
            clear the index register
        """
        self._state.x = 0x0
        self._state.pc += 1

    def inc(self, address):
        """
            increment a memory location by one
        """
        self._memory.increment(address)
        self._state.pc += 2

    def inca(self):
        """
            increment the acuumulator by one
        """
        self._state.a += 1
        self._state.pc += 1

    def incx(self):
        """
            increment the index register by one
        """
        self._state.x += 1
        self._state.pc += 1

    def dec(self, address):
        """
            decrement a memory location by one
        """
        self._memory.decrement(address)
        self._state.pc += 2

    def deca(self):
        """
            decrement accumulator by one
        """
        self._state.a -= 1
        self._state.pc += 1

    def decx(self):
        """
            decrement index register by one
        """
        self._state.x -= 1
        self._state.pc += 1

    def logical_and(self, value):
        """
            logical and of the accumulator and operand
        """
        self._state.a &= value
        self._state.pc += 2

    def ora(self, value):
        """
            logical or of the accumulator and operand
        """
        self._state.a |= value
        self._state.pc += 2

    def eor(self, value):
        """
            exclusivve or of the accumulator and an operand
        """
        self._state.a ^= value
        self._state.pc =+ 2

    def com(self, address):
        """
            get one's complement of a memory location
        """
        pass

    def coma(self):
        """
            get ones complement of the accumulator
        """
        pass

    def comx(self):
        """
            get ones complement of the index register
        """
        pass

    def asl(self, address):
        """
            arithmetically shift a memory location left by one bit
        """
        pass

    def asla(self):
        """
            arithmetically shift the accumulator left by one bit
        """
        pass

    def aslx(self):
        """
            arithmetically shift the index register left by one bit
        """

    def asr(self, address):
        """
            arithmetically shift a memory location right by one bit
        """
        pass

    def asra(self):
        """
            arithmetically shift the accumulator right by one bit
        """

    def asrx(self):
        """
            arithmetically shift the index register by one bit
        """

    def lsl(self, address):
        """
            logically shift a memory location left by one bit
        """

    def lsla(self):
        """
            LSLA logically shift the accumulator left by one bit
        """

    def lslx(self):
        """
            LSLX logically shift the index register left by one bit
        """

    def lsr(self, address):
        """
            LSR logically shift a memory location right by one bit
        """

    def lsra(self):
        """
            LSRA logically shift the accumulator right by one bit
        """

    def lsrx(self):
        """
            LSRX logically shift the index register right by one bit
        """

    def rol(self, address):
        """
            ROL rotate a memory location left by one bit
        """

    def rola(self):
        """
            ROLA rotate the accumulator left by one bit
        """

    def rolx(self):
        """
            ROLX rotate the index register left by one bit
        """

    def ror(self, address):
        """
            ROR rotate a memory location right by one bit
        """

    def rora(self):
        """
            RORA rotate the accumulator right by one bit
        """

    def rorx(self):
        """
            RORX rotate the index register right by one bit
        """

    def bit(self):
        """
            BIT bit test the accumulator and set the N or Z flags
        """

    def cmp(self, value):
        """
            CMP compare an operand to the accumulator
        """
    def cpx(self, value):
        """
            CPX compare an operand to the index register
        """

    def tst(self, address):
        """
            TST test a memory location and set the N or Z flags
        """

    def tsta(self):
        """
            TSTA test the accumulator and set the N or Z flags
        """

    def testx(self):
        """
            TSTX test the index register and set the N or Z flags
        """

    def bcc(self, address):
        """
            BCC branch if carry clear (C = 0)
        """

    def bcs(self, address):
        """
            BCS branch if carry set (C = 1)
        """

    def beq(self, address):
        """
            BEQ branch if equal (Z = 0)
        """

    def bne(self, address):
        """
            BNE branch if not equal (Z = 1)
        """

    def bhcc(self, address):
        """
            branch if half carry clear (H = 0)
        """

    def bhcs(self, address):
        """
            branch if half carry set (H = 1)
        """

    def bhi(self, address):
        """
            branch if higher (C or Z = 0)
        """

    def bhs(self, address):
        """
            branch if half carry is set (H =1)
        """

    def bls(self, address):
        """
            BLS branch if lower or same (C or Z = 1)
        """

    def blo(self, address):
        """
            BLO branch if lower (C = 1)
        """

    def bmi(self, address):
        """
            branch if minus (N = 1)
        """

    def bpl(self, address):
        """
            branch if plus (N = 0)
        """

    def bmc(self, address):
        """
            BMC branch if interrupts are not masted (I = 0)
        """

    def bms(self, address):
        """
            BMS branch if interrupts are masked (I = 1)
        """

    # special branches

    def bih(self, address):
        """
            branch if IRQ pin is high
        """

    def bil(self, address):
        """
            branch if IRQ pin is low
        """

    def bra(self, address):
        """
            branch always
        """

    def brn(self, address):
        """
            branch never ( another nop? )
        """

    def bsr(self, address):
        """
            branch to subroutine and save return address on stack
        """

    # single bit operations

    def bclr(self, bit):
        """
            clear the designated memory bit
        """

    def bset(self, bit):
        """
            set the designated memory bit
        """

    def brclr(self, bit, address):
        """
            branch if the designated memory bit is clear
        """

    def brset(self, bit, address):
        """
            branch if the designated memory bit is set
        """

    # jumps and returns
    def jmp(self, address):
        """
            JMP jumpt to specified address
        """

    def jsr(self, address):
        """
            JSR jump to subroutine and save return address on stack
        """

    def rts(self):
        """
            RTS pull address from stack and return from subroutine
        """

    def rti(self):
        """
            RTI pull registers from stack and return from interrupt
        """

    # misc control
    def clc(self):
        """
            CLC clear the condition code register carry bit
        """

    def sec(self):
        """
            SEC set the condition code register carry bit
        """

    def cli(self):
        """
            CLI clear the condition code register interrupt mask bit
        """

    def sei(self):
        """
            SEI set the condition code register interrupt mask bit
        """

    def swi(self):
        """
            SWI software initiated interrupt
        """

    def rsp(self):
        """
            RSP reset the stack pointer to $00FF
        """

    def wait(self):
        """
            WAIT enable interrupts and halt the CPU
        """

    def stop(self):
        """
            STOP enable interrupts and stop the oscillator
        """


