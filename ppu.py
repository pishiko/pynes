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
        
#TODO PPU flag
# 0x2000 bit 7,6,5,2,1-0
# 0x2001 bit 7-5,4,3,2,1,0
class PPU():
    def __init__(self,chr):
        self.ISDEBUG = False
        self.reg = np.zeros(0x0008,dtype=np.uint8)
        self.cycle = 0
        self.line = 0
        self.frame = self.init_frame()
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

        self.wppu_addr = 0x0000
        self.is_wppu_addr_up = True
        self.wsp_addr = 0x00
    
        self.vram = VRAM()
        self.spram = np.zeros(0x00ff,dtype=np.uint8)

        #control register 0x2000
        self.is_vblank_nmi = False          #7
        self.sprite_size_h = 8              #5
        self.bg_table_offset = 0x0000       #4
        self.sp_table_offset = 0x0000       #3
        self.ppu_inc = 0x0010               #2
        self.name_table = self.vram.name0   #0-1
        #control register 0x2001
        self.bg_color = "red"               #7-5
        self.is_active_sprite = True        #4
        self.is_active_bg = True            #3
        self.is_draw_spmask = False     #2
        self.is_draw_bgmask = False         #1
        self.is_color = True                #0

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
        if self.cycle >= 341:
            self.cycle -= 341
            self.line += 1
        
            if self.line <= 240-16 and self.line % 32 == 0:
                self.frame = self.draw_frame()
            if self.line == 241:
                self.write_reg(0x0002, 0b10000000 + (self.reg[2] & 0b01111111))
            if self.line == 262:
                self.write_reg(0x0002, self.reg[2] & 0b01111111)
                self.line = 0
                return self.frame
            #TODO DEBUG FRAME
            if self.ISDEBUG:
                return self.frame
        return None

    def write_reg(self,addr,data):
        #TODO
        if addr == 0x0000:
            self.is_vblank_nmi = data >> 7
            self.sprite_size_h = 16 if (data >> 5) & 0b1 else 8
            self.bg_table_offset = 0x0100 if (data >> 4) & 0b1 else 0x0000
            self.sp_table_offset = 0x0100 if (data >> 3) & 0b1 else 0x0000
            self.ppu_inc = 0x0001 if (data >> 2) & 0b1 else 0x0020
            n = data & 0b11
            if n == 0:
                self.name_table = self.vram.name0
            elif n == 1:
                self.name_table = self.vram.name1
            elif n == 2:
                self.name_table = self.vram.name2
            elif n == 3:
                self.name_table = self.vram.name3
        elif addr == 0x0001:
            n = (data >> 5) & 0b111
            if n == 0b000:
                self.bg_color = "black"
            elif n == 0b001:
                self.bg_color = "green"
            elif n == 0b010:
                self.bg_color = "blue"
            elif n == 0b100:
                self.bg_color = "red"
            self.is_active_sprite = (data >> 4) & 0b1
            self.is_active_bg = (data >> 3) & 0b1
            self.is_draw_spmask = (data >> 2) & 0b1
            self.is_draw_bgmask = (data >> 1) & 0b1
            self.is_color = data & 0b1

        elif addr == 0x0002:
            self.reg[addr] = data
        elif addr == 0x0003:
            self.wsp_addr = data
        elif addr == 0x0004:
            self.spram[self.wsp_addr] = data
            self.wsp_addr += 0x01
        elif addr == 0x0006:
            if self.is_wppu_addr_up:
                self.wppu_addr = 0x0000
                self.wppu_addr += data << 8
            else:
                self.wppu_addr += data
            self.is_wppu_addr_up = not self.is_wppu_addr_up
        elif addr == 0x0007:
            self.write(self.wppu_addr,data)
            self.wppu_addr += 0x0001
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
        bg = self.draw_bg(self.frame)
        bg = self.draw_sprite(bg)
        return bg

    def draw_bg(self,base):
        if True:
        #if self.is_active_bg:
            coly = int(self.line/32)-1
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
                                sprite = self.sprites[self.vram.name0[y*32+x]+self.bg_table_offset]
                                array = np.zeros(shape=(8, 8, 3),dtype=np.uint8)
                                np.place(array,np.stack((sprite,)*3, axis=-1) == 0x0,self.color_pallet[self.vram.bgpallet[pallet*4]])
                                np.place(array,np.stack((sprite,)*3, axis=-1) == 0x1,self.color_pallet[self.vram.bgpallet[pallet*4+1]])
                                np.place(array,np.stack((sprite,)*3, axis=-1) == 0x2,self.color_pallet[self.vram.bgpallet[pallet*4+2]])
                                np.place(array,np.stack((sprite,)*3, axis=-1) == 0x3,self.color_pallet[self.vram.bgpallet[pallet*4+3]])
                                base.paste(Image.fromarray(array, "RGB"), (x*8, y*8))
        return base

    def draw_sprite(self,base):
        if self.is_active_sprite:
            draw_sprites = []
            for i in range(int(len(self.spram)/4)):
                index = i*4
                if self.line - 32 <= self.spram[index]+1 < self.line:
                    if len(draw_sprites) >= 8:
                        #TODO set sprite overflow flag
                        self.write_reg(0x0002,0b00100000 + self.reg[2] & 0b11011111)
                        break
                    draw_sprites.append(self.spram[index:index+4])
            
            for sp in draw_sprites:
                y = sp[0]+1
                x = sp[3]
                pallet = (sp[2] & 0b11)
                sprite = self.sprites[sp[1]+self.sp_table_offset]
                if (sp[2] >> 6) & 0b1:
                    sprite = np.fliplr(sprite.copy())
                if (sp[2] >> 7) & 0b1:
                    sprite = np.flipud(sprite.copy())

                array = np.zeros(shape=(8, 8, 3),dtype=np.uint8)
                np.place(array,np.stack((sprite,)*3, axis=-1) == 0x0,self.color_pallet[self.vram.sppallet[pallet*4]])
                np.place(array,np.stack((sprite,)*3, axis=-1) == 0x1,self.color_pallet[self.vram.sppallet[pallet*4+1]])
                np.place(array,np.stack((sprite,)*3, axis=-1) == 0x2,self.color_pallet[self.vram.sppallet[pallet*4+2]])
                np.place(array,np.stack((sprite,)*3, axis=-1) == 0x3,self.color_pallet[self.vram.sppallet[pallet*4+3]])

                base.paste(Image.fromarray(array,"RGB"), (x,y))
            return base
