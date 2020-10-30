import numpy as np

class CPUReg():
    def __init__(self):
        self.reg8 = np.array([0,0,0,0],dtype=np.uint8)
        self.reg16 = np.array([0],dtype=np.uint16)
        self.N = False
        self.V = False
        self.R = False
        self.B = False
        self.D = False
        self.I = False
        self.Z = False
        self.C = False

    @property
    def A(self):
        return self.reg8[0]
    @A.setter
    def A(self,v):
        self.reg8[0] = np.uint8(v)
    
    @property
    def X(self):
        return self.reg8[1]
    @X.setter
    def X(self,v):
        self.reg8[1] = np.uint8(v)
    
    @property
    def Y(self):
        return self.reg8[2]
    @Y.setter
    def Y(self,v):
        self.reg8[2] = np.uint8(v)
    
    @property
    def S(self):
        return self.reg8[3]
    @S.setter
    def S(self,v):
        self.reg8[3] = np.uint8(v)

    @property
    def PC(self):
        return self.reg16[0]
    @PC.setter
    def PC(self,v):
        self.reg16[0] = np.uint16(v)


class CPU():
    def __init__(self,prg,ppu):
        self.prg_rom = prg
        self.ppu = ppu

        self.op_table = (
            #0x00
            (self.BRK, self.implied), (self.ORA, self.Xindirect), (None, None), (None, None), (None, None), (self.ORA, self.zeropage), (self.ASL, self.zeropage), (None, None), (self.PHP, self.implied), (self.ORA, self.immediate), (self.ASL, self.accumulator), (None, None), (None, None), (self.ORA, self.absolute), (self.ASL, self.absolute), (None, None),
            #0x10
            (self.BPL, self.relative), (self.ORA, self.indirectY), (None, None), (None, None), (None, None), (self.ORA, self.zeropageX), (self.ASL, self.zeropageX), (None, None), (self.CLC, self.implied), (self.ORA, self.absoluteY), (None, None), (None, None), (None, None), (self.ORA, self.absoluteX), (self.ASL, self.absoluteX), (None, None),
            #0x20
            (self.JSR, self.absolute), (self.AND, self.Xindirect), (None, None), (None, None), (self.BIT, self.zeropage), (self.AND, self.zeropage), (self.ROL, self.zeropage), (None, None), (self.PLP, self.implied), (self.AND, self.immediate), (self.ROL, self.accumulator), (None, None), (self.BIT, self.absolute), (self.AND, self.absolute), (self.ROL, self.absolute), (None, None),
            #0x30
            (self.BMI, self.relative), (self.AND, self.indirectY), (None, None), (None, None), (None, None), (self.AND, self.zeropageX), (self.ROL, self.zeropageX), (None, None), (self.SEC, self.implied), (self.AND, self.absoluteY), (None, None), (None, None), (None, None), (self.AND, self.absoluteX), (self.ROL, self.absoluteX), (None, None),
            #0x40
            (self.RTI, self.implied), (self.EOR, self.Xindirect), (None, None), (None, None), (None, None), (self.EOR, self.zeropage), (self.LSR, self.zeropage), (None, None), (self.PHA, self.implied), (self.EOR, self.immediate), (self.LSR, self.accumulator), (None, None), (self.JMP, self.absolute), (self.EOR, self.absolute), (self.LSR, self.absolute), (None, None),
            #0x50
            (self.BVC, self.relative), (self.EOR, self.indirectY), (None, None), (None, None), (None, None), (self.EOR, self.zeropageX), (self.LSR, self.zeropageX), (None, None), (self.CLI, self.implied), (self.EOR, self.absoluteY), (None, None), (None, None), (None, None), (self.EOR, self.absoluteX), (self.LSR, self.absoluteX), (None, None),
            #0x60
            (self.RTS, self.implied), (self.ADC, self.Xindirect), (None, None), (None, None), (None, None), (self.ADC, self.zeropage), (self.ROR, self.zeropage), (None, None), (self.PLA, self.implied), (self.ADC, self.immediate), (self.ROR, self.accumulator), (None, None), (self.JMP, self.indirect), (self.ADC, self.absolute), (self.ROR, self.absolute), (None, None),
            #0x70
            (self.BVS, self.relative), (self.ADC, self.indirectY), (None, None), (None, None), (None, None), (self.ADC, self.zeropageX), (self.ROR, self.zeropageX), (None, None), (self.SEI, self.implied), (self.ADC, self.absoluteY), (None, None), (None, None), (None, None), (self.ADC, self.absoluteX), (self.ROR, self.absoluteX), (None, None),
            #0x80
            (None,None), (self.STA, self.Xindirect), (None, None), (None, None), (self.STY, self.zeropage), (self.STA, self.zeropage), (self.STX, self.zeropage), (None, None), (self.DEY, self.implied), (None, None), (self.TXA, self.implied), (None, None), (self.STY, self.absolute), (self.STA, self.absolute), (self.STX, self.absolute), (None, None),
            #0x90
            (self.BCC, self.relative), (self.STA, self.indirectY), (None, None), (None, None), (self.STY, self.zeropageX), (self.STA, self.zeropageX), (self.STX, self.zeropageY), (None, None), (self.TYA, self.implied), (self.STA, self.absoluteY), (self.TXS, self.implied), (None, None), (None, None), (self.STA, self.absoluteX), (None,None), (None, None),
            #0xa0
            (self.LDY, self.immediate), (self.LDA, self.Xindirect), (self.LDX, self.immediate), (None, None), (self.LDY, self.zeropage), (self.LDA, self.zeropage), (self.LDX,self.zeropage), (None, None), (self.TAY, self.implied), (self.LDA, self.immediate), (self.TAX, self.implied), (None, None), (self.LDY, self.absolute), (self.LDA, self.absolute), (self.LDX, self.absolute), (None, None),
            #0xb0
            (self.BCS, self.relative), (self.LDA, self.indirectY), (None, None), (None, None), (self.LDY, self.zeropageX), (self.LDA, self.zeropageX), (self.LDX, self.zeropageY), (None, None), (self.CLV, self.implied), (self.LDA, self.absoluteY), (self.TSX, self.implied), (None, None), (self.LDY, self.absoluteX), (self.LDA, self.absoluteX), (self.LDX, self.absoluteY), (None, None),
            #0xc0
            (self.CPY, self.immediate), (self.CMP, self.Xindirect), (None, None), (None, None), (self.CPY, self.zeropage), (self.CMP, self.zeropage), (self.DEC, self.zeropage), (None, None), (self.INY, self.implied), (self.CMP, self.immediate), (self.DEX, self.implied), (None, None), (self.CPY, self.absolute), (self.CMP, self.absolute), (self.DEC, self.absolute), (None, None),
            #0xd0
            (self.BNE, self.relative), (self.CMP, self.indirectY), (None, None), (None, None), (None, None), (self.CMP, self.zeropageX), (self.DEC, self.zeropageX), (None, None), (self.CLD, self.implied), (self.CMP, self.absoluteY), (None,None), (None, None), (None, None), (self.CMP, self.absoluteX), (self.DEC, self.absoluteX), (None, None),
            #0xe0
            (self.CPX, self.immediate), (self.SBC, self.Xindirect), (None, None), (None, None), (self.CPX, self.zeropage), (self.SBC, self.zeropage), (self.INC, self.zeropage), (None, None), (self.INX, self.implied), (self.SBC, self.immediate), (self.NOP, self.implied), (None, None), (self.CPX, self.absolute), (self.SBC, self.absolute), (self.INC, self.absolute), (None, None),
            #0xf0
            (self.BEQ, self.relative), (self.SBC, self.indirectY), (None, None), (None, None), (None, None), (self.SBC, self.zeropageX), (self.INC, self.zeropageX), (None, None), (self.SED, self.implied), (self.SBC, self.absoluteY), (None, None), (None, None), (None, None), (self.SBC, self.absoluteX), (self.INC, self.absoluteX), (None, None),
        )
        self.cycle_table = (
            7, 6, 2, 8, 3, 3, 5, 5, 3, 2, 2, 2, 4, 4, 6, 6,
            2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 6, 7,
            6, 6, 2, 8, 3, 3, 5, 5, 4, 2, 2, 2, 4, 4, 6, 6,
            2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 6, 7,
            6, 6, 2, 8, 3, 3, 5, 5, 3, 2, 2, 2, 3, 4, 6, 6,
            2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 6, 7,
            6, 6, 2, 8, 3, 3, 5, 5, 4, 2, 2, 2, 5, 4, 6, 6,
            2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 6, 7,
            2, 6, 2, 6, 3, 3, 3, 3, 2, 2, 2, 2, 4, 4, 4, 4,
            2, 6, 2, 6, 4, 4, 4, 4, 2, 4, 2, 5, 5, 4, 5, 5,
            2, 6, 2, 6, 3, 3, 3, 3, 2, 2, 2, 2, 4, 4, 4, 4,
            2, 5, 2, 5, 4, 4, 4, 4, 2, 4, 2, 4, 4, 4, 4, 4,
            2, 6, 2, 8, 3, 3, 5, 5, 2, 2, 2, 2, 4, 4, 6, 6,
            2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 7, 7,
            2, 6, 3, 8, 3, 3, 5, 5, 2, 2, 2, 2, 4, 4, 6, 6,
            2, 5, 2, 8, 4, 4, 6, 6, 2, 4, 2, 7, 4, 4, 7, 7,
        )

        self.reg: CPUReg = CPUReg()
        self.wram = np.zeros(0x0800, dtype=np.uint8)

        #init regs
        self.reg.R = True
        self.reg.S = 0x01fd

        self.RESET()

    def read(self,addr):
        if addr < 0x2000:
            return self.wram[addr]
        elif addr < 0x2008:
            return self.ppu.reg[addr-0x2000]
        elif addr < 0xFFFF:
            return self.prg_rom[addr-0x8000]

    def write(self,addr,data):
        if addr < 0x0800:
            self.wram[addr] = data
        elif addr < 0x2008:
            self.ppu.write_reg(addr-0x2000,data)
        elif addr < 0x4020:
            #TODO APU,PAD
            raise Exception("WRITE APUPAD")
        else:
            self.prg_rom[addr-0x8000] = data

    def push(self,data):
        self.write(self.reg.S,data)
        self.reg.S -= 0x0001
        return

    def pop(self):
        self.reg.S += 0x0001
        return self.read(self.reg.S)

    def run(self):
        opcode = self.read(self.reg.PC)
        self.reg.PC += 0x0001
        self.excute(opcode)
        return self.cycle_table[opcode]

    def excute(self,opcode):
        op,addr = self.op_table[opcode]
        print("[0x{0:02x}] OP 0x{1:02x} {3} {2}(".format(self.reg.PC,opcode,op.__name__,addr.__name__),end="")
        a = addr()
        print(hex(a)+")" if a is not None else ")")
        if not a is None:
            op(a)
        else:
            op()

    #Adressing
    def accumulator(self):
        return None
    def implied(self):
        return None
    def immediate(self):
        self.reg.PC += 0x01
        return self.reg.PC - 0x01
    def zeropage(self):
        self.reg.PC += 0x01
        return self.read(self.reg.PC - 0x01)
    def zeropageX(self):
        self.reg.PC += 0x01
        return self.read(self.reg.PC - 0x01)+self.reg.X
    def zeropageY(self):
        self.reg.PC += 0x01
        return self.read(self.reg.PC - 0x01)+self.reg.Y
    def absolute(self):
        self.reg.PC += 0x02
        return (self.read(self.reg.PC - 0x01) << 8) + self.read(self.reg.PC - 0x02)
    def absoluteX(self):
        self.reg.PC += 0x02
        return (self.read(self.reg.PC - 0x01) << 8) + self.read(self.reg.PC - 0x02) + self.reg.X
    def absoluteY(self):
        self.reg.PC += 0x02
        return (self.read(self.reg.PC - 0x01) << 8) + self.read(self.reg.PC - 0x02) + self.reg.Y
    def indirect(self):
        self.reg.PC += 0x02
        addr = self.read(self.reg.PC - 0x01) << 8 + self.read(self.reg.PC - 0x02)
        return self.read(addr+0x01) << 8 + self.read(addr)
    def Xindirect(self):
        self.reg.PC += 0x01
        ind = self.read(self.reg.PC - 0x01) + self.reg.X
        return self.read(ind+0x01) << 8 + self.read(ind)
    def indirectY(self):
        self.reg.PC += 0x01
        ind = self.read(self.reg.PC - 0x01)
        return self.read(ind + 1) << 8 + self.read(ind) + self.reg.Y
    def relative(self):
        self.reg.PC += 0x01
        return self.reg.PC + np.int8(self.read(self.reg.PC - 0x01))

    #Operation

    def set_nz(self,a):
        self.reg.N = a >> 7
        self.reg.Z = a == 0x00
        return

    def get_stat_reg(self):
        p = self.reg.N << 7 + self.reg.V << 6 + self.reg.R << 5\
            + self.reg.B << 4 + self.reg.D << 3 + self.reg.I << 2\
            + self.reg.Z << 1 + self.reg.C
        return p

    def set_stat_reg(self,p):
        self.N = p >> 7 & 0x01
        self.V = p >> 6 & 0x01
        self.R = p >> 5 & 0x01
        self.B = p >> 4 & 0x01
        self.D = p >> 3 & 0x01
        self.I = p >> 2 & 0x01
        self.Z = p >> 1 & 0x01
        self.C = p & 0x01
        return

    #演算
    def ADC(self,M):
        m = self.read(M)
        ans = self.reg.A + m + self.reg.C
        self.reg.C = ans > 0xff
        self.reg.V = (self.reg.A^m)&0x80 == 0x00\
             and (self.reg.A^ans)&0x80 != 0x00
        self.reg.A = ans
        self.set_nz(self.reg.A)
        return

    def SBC(self,M):
        m = self.read(M)
        ans = self.reg.A - m - (not self.reg.C)
        self.reg.C = ans >= 0x00
        self.reg.V = (self.reg.A ^ m) & 0x80 == 0x00\
            and (self.reg.A ^ ans) & 0x80 != 0x00
        self.reg.A = ans
        self.set_nz(self.reg.A)
        return
    
    #論理演算
    def AND(self,M):
        self.reg.A = self.reg.A & self.read(M)
        self.set_nz(self.reg.A)
        return
    def ORA(self,M):
        self.reg.A = self.reg.A | self.read(M)
        self.set_nz(self.reg.A)
        return
    def EOR(self,M):
        self.reg.A = self.reg.A ^ self.read(M)
        self.set_nz(self.reg.A)
        return
    #シフト，ローテーション
    def ASL(self):
        self.reg.C = self.reg.A >> 7
        self.reg.A = self.reg.A << 1
        self.set_nz(self.reg.A)
        return
    def LSR(self):
        self.reg.C = self.reg.A & 0x01
        self.reg.A = self.reg.A >> 1
        self.set_nz(self.reg.A)
        return
    def ROL(self):
        self.reg.C,self.reg.A = self.reg.A >> 7, self.reg.A << 1 + self.reg.C
        self.set_nz(self.reg.A)
        return
    def ROR(self):
        self.reg.C,self.reg.A = self.reg.A & 0x01,self.reg.A >> 1 + self.reg.C << 7
        self.set_nz(self.reg.A)
        return
    #条件分岐
    def BCC(self,addr):
        if not self.reg.C:
            self.reg.PC = addr
        return
    def BCS(self,addr):
        if self.reg.C:
            self.reg.PC = addr
        return
    def BEQ(self,addr):
        if self.reg.Z:
            self.reg.PC = addr
        return
    def BNE(self,addr):
        if not self.reg.Z:
            self.reg.PC = addr
        return
    def BVC(self,addr):
        if not self.reg.V:
            self.reg.PC = addr
        return
    def BVS(self, addr):
        if self.reg.V:
            self.reg.PC = addr
        return
    def BPL(self, addr):
        if not self.reg.N:
            self.reg.PC = addr
        return
    def BMI(self, addr):
        if self.reg.N:
            self.reg.PC = addr
        return
    #ビット検査
    def BIT(self,M):
        m = self.read(M)
        self.reg.Z = bool(self.reg.A & m)
        self.reg.N = m >> 7
        self.reg.V = m >> 6 & 0x1
        return
    #ジャンプ
    def JMP(self,addr):
        self.reg.PC = addr
        return
    def JSR(self,addr):
        word = self.reg.PC - 0x0001
        self.push(word >> 8 & 0xff)
        self.push(word & 0xff)
        self.reg.PC = addr
        return
    def RTS(self,addr):
        wlow = self.pop()
        wup = self.pop()
        self.reg.PC = ((wup >> 8) + wlow) + 0x0001
        return
    #ソフトウェア割り込み
    def BRK(self):
        if not self.reg.I:
            self.reg.B = True
            self.reg.PC += 0x0001
            self.push(self.reg.PC >> 8)
            self.push(self.reg.PC & 0xff)
            self.push(self.get_stat_reg())
            self.reg.I = True
            self.reg.PC = (self.read(0xffff) >> 8) + self.read(0xfffe)
            
    def RTI(self):
        self.set_stat_reg(self.pop())
        plow = self.pop()
        pup = self.pop()
        self.reg.PC = (pup >> 8) + plow
        return
    #比較
    def CMP(self,M):
        a = self.reg.A - self.read(M)
        self.reg.C = a >= 0x00
        self.set_nz(a)
        return
    def CPX(self,M):
        a = self.reg.X - self.read(M)
        self.reg.C = a >= 0x00
        self.set_nz(a)
        return
    def CPY(self,M):
        a = self.reg.Y - self.read(M)
        self.reg.C = a >= 0x00
        self.set_nz(a)
        return
    #インクリメント，デクリメント
    def INC(self,M):
        a = self.read(M)+0x0001
        self.write(M,a)
        self.set_nz(a)
        return
    def DEC(self,M):
        a = self.read(M)-0x0001
        self.write(M, a)
        self.set_nz(a)
        return
    def INX(self):
        self.reg.X += 0x01
        self.set_nz(self.reg.X)
        return
    def DEX(self):
        self.reg.X -= 0x01
        self.set_nz(self.reg.X)
        return
    def INY(self):
        self.reg.Y += 0x01
        self.set_nz(self.reg.Y)
        return
    def DEY(self):
        self.reg.Y -= 0x01
        self.set_nz(self.reg.Y)
    #フラグ操作
    def CLC(self):
        self.reg.C = False
        return
    def SEC(self):
        self.reg.C = True
        return
    def CLI(self):
        self.reg.I = False
        return
    def SEI(self):
        self.reg.I = True
        return
    def CLD(self):
        self.reg.D = False
        return
    def SED(self):
        self.reg.D = True
        return
    def CLV(self):
        self.reg.V = False
        return
    #ロード
    def LDA(self,M):
        self.reg.A = self.read(M)
        self.set_nz(self.reg.A)
        return
    def LDX(self,M):
        self.reg.X = self.read(M)
        self.set_nz(self.reg.X)
        return
    def LDY(self,M):
        self.reg.Y = self.read(M)
        self.set_nz(self.reg.Y)
        return
    #ストア
    def STA(self,M):
        self.write(M,self.reg.A)
        return
    def STX(self,M):
        self.write(M,self.reg.X)
        return
    def STY(self, M):
        self.write(M, self.reg.Y)
        return
    #レジスタ間転送
    def TAX(self):
        self.reg.X = self.reg.A
        self.set_nz(self.reg.X)
        return
    def TXA(self):
        self.reg.A = self.reg.X
        self.set_nz(self.reg.A)
        return
    def TAY(self):
        self.reg.Y = self.reg.A
        self.set_nz(self.reg.Y)
        return
    def TYA(self):
        self.reg.A = self.reg.Y
        self.set_nz(self.reg.A)
        return
    def TSX(self):
        self.reg.X = self.reg.S
        self.set_nz(self.reg.X)
        return
    def TXS(self):
        self.reg.S = self.reg.X
        return
    #スタック
    def PHA(self):
        self.push(self.reg.A)
        return
    def PLA(self):
        self.reg.A = self.pop()
        self.set_nz(self.reg.A)
    def PHP(self):
        p = self.get_stat_reg()
        self.push(p)
        return
    def PLP(self):
        p = self.pop()
        self.set_stat_reg(p)
    #No Operation
    def NOP(self):
        return

    #ハードウェア割り込み
    def NMI(self):
        self.reg.B = False
        self.push(self.reg.PC >> 8)
        self.push(self.reg.PC & 0xff)
        self.push(self.get_stat_reg())
        self.reg.I = True
        self.reg.PC = (self.read(0xfffb) >> 8) + self.read(0xfffa)
        return

    def IRQ(self):
        if not self.reg.I:
            self.reg.B = False
            self.push(self.reg.PC >> 8)
            self.push(self.reg.PC & 0xff)
            self.push(self.get_stat_reg())
            self.reg.I = True
            self.reg.PC = (self.read(0xffff) >> 8) + self.read(0xfffa)
        return

    def RESET(self):
        self.reg.I = True
        self.reg.PC = (self.read(0xfffd) << 8) + self.read(0xfffc)

if __name__ == "__main__":
    import main
    prg,chr = main.read_rom("roms/sample1.nes")
    cpu = CPU(prg)
    print("start from "+hex(cpu.reg.PC))
    while True:
        cpu.run()
        #input()
