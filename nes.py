from cpu import CPU
from ppu import PPU
import matplotlib.pyplot as plt

class NES():

    def __init__(self,prg,chr):
        self.ppu = PPU(chr)
        self.cpu = CPU(prg,self.ppu)
        self.frame = self.ppu.init_frame()

    def cycle(self):
        out = None
        while not out:
            cycle = self.cpu.run()
            out = self.ppu.run(cycle*3)
        self.frame = out
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

    prg,chr = main.read_rom("roms/sample1.nes")

    nes = NES(prg,chr)
    t = threading.Thread(target=nes.run)
    t.setDaemon(True)
    t.start()
    renderer = Renderer(nes)
    renderer.run()