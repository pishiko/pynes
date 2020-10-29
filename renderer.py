import matplotlib.pyplot as plt
import matplotlib.animation as anim
import time

class Renderer():
    def __init__(self,nes):
        self.nes = nes
        self.counter = 0
        self.fps = 0
        self.start = time.time()

    def run(self):
        def plot(data):
            self.counter += 1
            if self.counter % 10 == 0:
                self.counter = 0
                self.fps = 10/(time.time()-self.start)
                self.start = time.time()
            plt.cla()
            im = plt.imshow(self.nes.frame)
            plt.title("FPS:{:.2f}".format(self.fps))
        
        fig = plt.figure()
        ani = anim.FuncAnimation(fig,plot,interval=17)
        plt.show()
