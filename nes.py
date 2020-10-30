from cpu import CPU
from ppu import PPU
import matplotlib.pyplot as plt
import time

class NES():

    def __init__(self,prg,chr):
        self.ppu = PPU(chr)
        self.cpu = CPU(prg,self.ppu)
        self.frame = self.ppu.init_frame()

    def cycle(self):
        start = time.time()
        ##########

        out = None
        while not out:
            cycle = self.cpu.run()
            out = self.ppu.run(cycle*3)
        self.frame = out

        ###########
        #time.sleep(max(0,(1.0/60-(time.time() - start))))
        #time.sleep(0.01)
        return

    def run(self):
        while True:
            self.cycle()
            # plt.imshow(self.frame)
            # plt.show()

if __name__ == "__main__":
    import main
    import threading
    from renderer import Renderer
    import sys
    
    #DEFAULT

    args = sys.argv
    if len(args) > 1 and not args[1].startswith("-"):
        dir = args[1]
    else:
        dir = "roms/giko008.nes"
        
    prg,chr = main.read_rom(dir)

    nes = NES(prg,chr)
    nes.cpu.ISDEBUG = False
    nes.ppu.ISDEBUG = True
    t = threading.Thread(target=nes.run)
    t.setDaemon(True)
    t.start()
    renderer = Renderer(nes)
    renderer.run()
