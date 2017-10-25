from lib import Particle, Vector
from matplotlib import pyplot as plt
from statistics import stdev, mean
from math import sqrt
from multiprocessing import Process, Manager

class Universe:
    def __init__(self, tickScalingFactor, density=2650):
        self.parts = []
        self.tickLen = 0
        self.tickSF = tickScalingFactor
        self.density = density
        plt.ion()
        self.touches = 0
        self.g = 6.67*(10**(-11))
        self.cullat = 40000000000000

    def randomize(self, numParts, minPos, maxPos, minVel, maxVel, minSize, maxSize,):
        self.parts = [Particle.rand_part(minPos, maxPos, minSize, maxSize, minVel, maxVel, self.density) for i in range(numParts)]
        self.xmin = minPos.x
        self.xmax = maxPos.x
        self.ymin = minPos.y
        self.ymax = maxPos.y
        self.avgVel = sum(abs(p.velocity) for p in self.parts) / len(self.parts)
        self.avgSize = sum(p.size for p in self.parts) / len(self.parts)
        self.totalMass = sum(p.size for p in self.parts)


    def par_run_helper(self, part, destroy, add):
        for other in self.parts:
            if other not in destroy and other is not part:
                if part.touches(other):
                    add.append(part + other)
                    destroy.append(other)
                    destroy.append(part)
                    self.touches += 1
                    #print("TOUCH " + str(part.size + other.size))
                else:
                    part.interact(other, self.g)

    def par_run(self, numTicks=1, visualizeEvery=1, visualizeAfter=0):
        manager = Manager()
        destroy = manager.list()
        add = manager.list()
        for tick in range(numTicks):
            #print(tick)
            processes = []
            for part in self.parts:
                p = Process(target=self.par_run_helper, args=(part, destroy, add))
                p.start()
                processes+=[p]
                print(len(processes))
            print('start')
            for p in processes:
                p.join()
            print('end')
            for p in destroy:
                try:
                    self.parts.remove(p)
                except Exception:
                    pass
            for p in add:
                self.parts.append(p)

            self.avgVel = sum(abs(p.velocity) for p in self.parts) / len(self.parts)
            self.avgSize = sum(p.size for p in self.parts) / len(self.parts)
            #self.tickLen = 500000000 / self.avgVel#(((self.avgSize/self.density)**(1/3)) * 2) / self.avgVel

            for part in self.parts:
                part.move(self.tickLen)
                # if part.position.x < self.xmin:
                #     self.xmin = part.position.x
                # if part.position.x > self.xmax:
                #     self.xmax = part.position.x
                # if part.position.y < self.ymin:
                #     self.ymin = part.position.y
                # if part.position.y > self.ymax:
                #     self.ymax = part.position.y

            self.visualize(tick)

    def run(self, numTicks=1, visualizeEvery=1, visualizeAfter=0):
        for tick in range(numTicks):
            if len(self.parts) == 1:
                exit()

            destroy = []
            add = []
            for i, part in enumerate(self.parts):


                for other in self.parts[i+1:]:
                    if other not in destroy:
                        if part.touches(other):
                            #add.extend(part.collide(other))
                            add.append(part + other)
                            destroy.append(other)
                            destroy.append(part)
                            self.touches += 1
                            #print("TOUCH " + str(part.size + other.size))
                        else:
                            part.interact(other, self.g)
                # if abs(part.velocity) > sqrt((2*self.g * (self.totalMass - part.size))/abs(part.position)):
                #     #destroy.append(part)
                #     part.velocity *= .75
                #     # print(abs(part.velocity))
                #     # print(sqrt((2*self.g * (self.totalMass - part.size))/abs(part.position)))
                #     # print("Escape velocity reached!")

                if part.total_dist > self.cullat:
                    print('part destroyed with dist ' + str(part.total_dist))
                    print(len(self.parts))
                    destroy.append(part)

            for p in destroy:
                try:
                    self.parts.remove(p)
                except Exception:
                    pass
            for p in add:
                self.parts.append(p)

            self.avgVel = sum(abs(p.velocity) for p in self.parts) / len(self.parts)
            self.avgSize = sum(p.size for p in self.parts) / len(self.parts)
            self.cullat = max(self.cullat - tick*1000000000, 10000000000000)
            # print(self.cullat)
            # print(max(p.total_dist for p in self.parts), max(abs(p.velocity) for p in self.parts))
            #self.tickLen = 500000000 / self.avgVel#(((self.avgSize/self.density)**(1/3)) * 2) / self.avgVel

            for part in self.parts:
                part.move(self.tickLen)
                # if part.position.x < self.xmin:
                #     self.xmin = part.position.x
                # if part.position.x > self.xmax:
                #     self.xmax = part.position.x
                # if part.position.y < self.ymin:
                #     self.ymin = part.position.y
                # if part.position.y > self.ymax:
                #     self.ymax = part.position.y

            self.visualize(tick)

    def visualize(self, tick):
        plt.subplot().clear()
        axes = plt.gca()
        sf = 10

        try:
            xmean = mean(p.position.x for p in self.parts)
            xstdev = stdev(p.position.x for p in self.parts)

            ymean = mean(p.position.y for p in self.parts)
            ystdev = stdev(p.position.y for p in self.parts)

            self.xmin = xmean - 1.5 * xstdev
            self.xmax = xmean + 1.5 * xstdev
            self.ymin = ymean - 1.5 * ystdev
            self.ymax = ymean + 1.5 * ystdev
        except:
            pass

        self.tickLen = self.tickSF * (((self.xmax - self.xmin) + (self.ymax - self.ymin)) / 50000000000)

        axes.set_xlim([self.xmin, self.xmax])
        axes.set_ylim([self.ymin, self.ymax])
        plt.subplot().set_title('tick: ' + str(tick) + '\nUnits: ' + str(len(self.parts)) + '\nTick Length: ' + str(self.tickLen))
        for part in self.parts:
            c = plt.Circle(part.get_pos(), ((part.size/self.density)**(1/3))*sf, fill=True)
            plt.gca().add_artist(c)
        plt.pause(.001)

    def test(self):
        import pickle
        for i in range(300):
            pickle.loads(pickle.dumps(self))


if __name__ == '__main__':
    destroy = []
    add = []
    uni = Universe(.9)
    # uni.xmin = -100000000
    # uni.xmax = 100000000
    # uni.ymin = -100000000
    # uni.ymax = 100000000
    # uni.parts.append(Particle(Vector(-100000000, 100000), 5*10**25, Vector(1, 0), uni.density))
    # uni.parts.append(Particle(Vector(100000000, -100000), 5*10**25, Vector(-1, 0), uni.density))
    uni.randomize(600, Vector(-1.5*(10**11), -1.5*(10**11)), Vector(1.5*(10**11), 1.5*(10**11)), Vector(-10, -10), Vector(10, 10), 10**23, 10**25)
    import timeit
    timeit.Timer()
    uni.run(100000)
    print('next')
    uni.test()
    print('done')
    #uni.par_run(1)
    #print(timeit.timeit(uni.par_run))
    #uni.par_run(numTicks=10000)