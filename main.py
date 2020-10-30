
def read_rom(dir):
    with open(dir,'rb') as fp:
        buf = fp.read(16)
        prg_size = buf[4]*0x4000
        chr_size = buf[5]*0x2000
        prg = fp.read(prg_size)
        chr = fp.read(chr_size)

    return prg,chr
        
def show_chr(chr:bytes,save=False):

    W_SIZE = 32

    from PIL import Image
    import numpy as np

    print("size:"+str(len(chr)))
    out = []
    for i in range(int(len(chr)/16)):
        #print([[int(b) for b in format(c, '0>8b')] for c in chr[i*16:i*16+8]])
        m1 = np.array([[(c >> (7-i) & 0b1) for i in range(8)] for c in chr[i*16:i*16+8]], dtype=np.uint8)
        m2 = np.array([[(c >> (7-i) & 0b1) << 1 for i in range(8)] for c in chr[i*16+8:i*16+16]], dtype=np.uint8)
        m = np.apply_along_axis(lambda x:x*85,1,m1+m2)
        out.append(m)
        # img = Image.fromarray(m)
        # img.show()

    dst = Image.new('L',(8*W_SIZE,int(8*len(chr)/16/W_SIZE)))
    for y in range(int(len(chr)/16/W_SIZE)):
        for x in range(W_SIZE):
            dst.paste(Image.fromarray(out[y*W_SIZE+x]),(x*8,y*8))
    if save:
        dst.save("chrout.png")
    else:
        show_plt(out)
        #return out

counter = 0
start = 0
fps = 0
def show_plt(out):
    from PIL import Image
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import time
    import random

    def plot(data):
        global counter
        global start
        global fps

        W_SIZE = 32
        dst = Image.new('L', (8*W_SIZE, int(8*len(chr)/16/W_SIZE)))
        for y in range(int(len(chr)/16/W_SIZE)):
            for x in range(W_SIZE):
                dst.paste(Image.fromarray(out[random.randint(0,len(out)-1)]), (x*8, y*8))

        if counter % 10 == 0:
            fps = 10/(time.time()-start)
            start = time.time()
        plt.cla()
        counter = counter + 1
        im = plt.imshow(dst)
        plt.title("FPS:{:.2f}".format(fps))

    fig = plt.figure()    
    ani = animation.FuncAnimation(fig,plot,interval=16)
    plt.show()

if __name__ == '__main__':
    import ppu,threading
    from cpu import CPU

    prg,chr = read_rom("roms/giko005.nes")
    print(len(prg))
    show_chr(chr,save=True)
