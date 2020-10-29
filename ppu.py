import matplotlib.pyplot as plt
import matplotlib.animation as anim
import threading
from PIL import Image
import random
import time
import numpy as np

class VRAM():
    def __init__(self):
        self.patern0 = np.zeros(0x1000,dtype=np.uint8)
        self.patern1 = np.zeros(0x1000,dtype=np.uint8)
        self.name0 = np.zeros(0x03c0,dtype=np.uint8)
        self.pallet0 = np.zeros(0x0040,dtype=np.uint8)
        self.name1 = np.zeros(0x03c0,dtype=np.uint8)
        self.pallet1 = np.zeros(0x0040,dtype=np.uint8)
        self.name2 = np.zeros(0x03c0,dtype=np.uint8)
        self.pallet2 = np.zeros(0x0040,dtype=np.uint8)
        self.name3 = np.zeros(0x03c0,dtype=np.uint8)
        self.pallet3 = np.zeros(0x0040,dtype=np.uint8)
        self.bgpallet = np.zeros(0x0010,dtype=np.uint8)
        self.sppallet = np.zeros(0x0010,dtype=np.uint8)
        
class PPU():
    def __init__(self,chr):
        self.reg = np.zeros(0x0008,dtype=np.uint8)
        self.cycle = 0
        self.color_pallet = [
            [0x80, 0x80, 0x80], [0x00, 0x3D, 0xA6], [0x00, 0x12, 0xB0], [0x44, 0x00, 0x96],
            [0xA1, 0x00, 0x5E], [0xC7, 0x00, 0x28], [0xBA, 0x06, 0x00], [0x8C, 0x17, 0x00],
            [0x5C, 0x2F, 0x00], [0x10, 0x45, 0x00], [0x05, 0x4A, 0x00], [0x00, 0x47, 0x2E],
            [0x00, 0x41, 0x66], [0x00, 0x00, 0x00], [0x05, 0x05, 0x05], [0x05, 0x05, 0x05],
            [0xC7, 0xC7, 0xC7], [0x00, 0x77, 0xFF], [0x21, 0x55, 0xFF], [0x82, 0x37, 0xFA],
            [0xEB, 0x2F, 0xB5], [0xFF, 0x29, 0x50], [0xFF, 0x22, 0x00], [0xD6, 0x32, 0x00],
            [0xC4, 0x62, 0x00], [0x35, 0x80, 0x00], [0x05, 0x8F, 0x00], [0x00, 0x8A, 0x55],
            [0x00, 0x99, 0xCC], [0x21, 0x21, 0x21], [0x09, 0x09, 0x09], [0x09, 0x09, 0x09],
            [0xFF, 0xFF, 0xFF], [0x0F, 0xD7, 0xFF], [0x69, 0xA2, 0xFF], [0xD4, 0x80, 0xFF],
            [0xFF, 0x45, 0xF3], [0xFF, 0x61, 0x8B], [0xFF, 0x88, 0x33], [0xFF, 0x9C, 0x12],
            [0xFA, 0xBC, 0x20], [0x9F, 0xE3, 0x0E], [0x2B, 0xF0, 0x35], [0x0C, 0xF0, 0xA4],
            [0x05, 0xFB, 0xFF], [0x5E, 0x5E, 0x5E], [0x0D, 0x0D, 0x0D], [0x0D, 0x0D, 0x0D],
            [0xFF, 0xFF, 0xFF], [0xA6, 0xFC, 0xFF], [0xB3, 0xEC, 0xFF], [0xDA, 0xAB, 0xEB],
            [0xFF, 0xA8, 0xF9], [0xFF, 0xAB, 0xB3], [0xFF, 0xD2, 0xB0], [0xFF, 0xEF, 0xA6],
            [0xFF, 0xF7, 0x9C], [0xD7, 0xE8, 0x95], [0xA6, 0xED, 0xAF], [0xA2, 0xF2, 0xDA],
            [0x99, 0xFF, 0xFC], [0xDD, 0xDD, 0xDD], [0x11, 0x11, 0x11], [0x11, 0x11, 0x11],
        ]
        
        self.sprites = self.init_sprites(chr)

        self.write_addr = 0x0000
        self.is_waddr_up = True
    
        self.vram = VRAM()

    def init_frame(self):
        return Image.new(mode="RGB",size=(256,240),color="red")

    def init_sprites(self,chr):
        sprites = []
        for i in range(int(len(chr)/16)):
            m1 = np.array([[(c >> (7-i) & 0b1) for i in range(8)] for c in chr[i*16:i*16+8]], dtype=np.uint8)
            m2 = np.array([[(c >> (7-i) & 0b1) << 1 for i in range(8)] for c in chr[i*16+8:i*16+16]], dtype=np.uint8)
            sprites.append(m1+m2)
        return sprites

    def run(self,cycle):
        self.cycle += cycle
        if self.cycle > 1000:
            self.cycle -= 1000
            return self.draw_frame()
        return None

    def write_reg(self,addr,data):
        #TODO
        if addr == 0x0000:
            self.reg[addr] = data
        elif addr == 0x0006:
            if self.is_waddr_up:
                self.write_addr = 0x0000
                self.write_addr += data << 8
            else:
                self.write_addr += data
            self.is_waddr_up = not self.is_waddr_up
        elif addr == 0x0007:
            self.write(self.write_addr,data)
            self.write_addr += 0x0001
        else:
            self.reg[addr] = data

    def write(self,addr,data):
        if addr < 0x1000:
            self.vram.pattern0[addr] = data
        elif addr < 0x2000:
            self.vram.pattern1[addr-0x1000] = data
        elif addr < 0x23c0:
            self.vram.name0[addr-0x2000] = data
        elif addr < 0x2400:
            self.vram.pallet0[addr-0x23c0] = data
        elif addr < 0x27c0:
            self.vram.name1[addr-0x2400] = data
        elif addr < 0x2800:
            self.vram.pallet1[addr-0x27c0] = data
        elif addr < 0x2bc0:
            self.vram.name2[addr-0x2800] = data
        elif addr < 0x2c00:
            self.vram.pallet2[addr-0x2bc0] = data
        elif addr < 0x2fc0:
            self.vram.name3[addr-0x2c00] = data
        elif addr < 0x3000:
            self.vram.pallet3[addr-0x2fc0] = data
        elif addr < 0x3f10:
            self.vram.bgpallet[addr-0x3f00] = data
        elif addr < 0x3f20:
            self.vram.sppallet[addr-0x3f10] = data
        else:
            raise Exception("PPU MEMORY ERROR")

    def draw_frame(self):
        bg = self.draw_bg(self.init_frame())
        return bg

    def draw_bg(self,base):
        for coly in range(7):
            for colx in range(8):
                pb = self.vram.pallet0[coly*8+colx]
                pallets = ((pb >> 6) & 0b11, (pb >> 4) & 0b11,
                          (pb >> 2) & 0b11, pb & 0b11)
                for bloy in range(2):
                    for blox in range(2):
                        pallet = pallets[bloy*2+blox]
                        for my in range(2):
                            y = coly*4 + bloy*2 + my
                            for mx in range(2):
                                x = colx*4 + blox*2 + mx
                                sprite = self.sprites[self.vram.name0[y*32+x]]
                                array = np.zeros(shape=(8, 8, 3),dtype=np.uint8)
                                np.place(array,np.stack((sprite,)*3, axis=-1) == 0x0,self.color_pallet[self.vram.bgpallet[pallet*4]])
                                np.place(array,np.stack((sprite,)*3, axis=-1) == 0x1,self.color_pallet[self.vram.bgpallet[pallet*4+1]])
                                np.place(array,np.stack((sprite,)*3, axis=-1) == 0x2,self.color_pallet[self.vram.bgpallet[pallet*4+2]])
                                np.place(array,np.stack((sprite,)*3, axis=-1) == 0x3,self.color_pallet[self.vram.bgpallet[pallet*4+3]])
                                base.paste(Image.fromarray(array, "RGB"), (x*8, y*8))
        return base
