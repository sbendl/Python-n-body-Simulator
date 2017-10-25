import random
from math import sqrt

class Particle:
    def __init__(self, pos, size, vel, density):
        self.position = pos
        self.size = size
        self.velocity = vel
        self.density = density
        self.total_dist = 0

    @staticmethod
    def rand_part(minPos, maxPos, minSize, maxSize, minVel, maxVel, density):
        pos = Vector.randVec(minPos, maxPos)
        #size = random.uniform(minSize, maxSize)
        size = min(abs(pos)**(-2) * 10**46, 2 * 10**25)
        vel = Vector(-pos.y / 200, pos.x / 200)
        #vel = Vector.randVec(minVel, maxVel)
        return Particle(pos, size, vel, density)

    def __add__(self, other):
        return Particle(pos=(self.position*self.size+other.position*other.size)/(self.size+other.size), size=(self.size + other.size), vel=((self.velocity * self.size + other.velocity * other.size) / (self.size + other.size))*.5, density=self.density)

    def collide(self, other, new_part_size=5*10**24):
        if self.size <= new_part_size * 5 and other.size <= new_part_size * 5:
            return [self + other]
        else:
            new_parts = []
            remaining_size_self = self.size
            remaining_size_other = other.size
            while (remaining_size_self > new_part_size):
                radius = 2*(self.size/self.density)**(1/3)
                newpos = Vector.randVec(self.position + Vector(radius, radius), self.position + Vector(-radius, -radius))
                new_parts.append(Particle(newpos, new_part_size, self.velocity, self.density))
                remaining_size_self -= new_part_size
            while (remaining_size_self > new_part_size):
                radius = (other.size/other.density)**(1/3)
                newpos = Vector.randVec(other.position + Vector(radius, radius), other.position + Vector(-radius, -radius))
                new_parts.append(Particle(newpos, new_part_size, other.velocity, other.density))
                remaining_size_other -= new_part_size
            new_parts.append(Particle(Vector.randVec(self.position + Vector((self.size/self.density)**(1/3), (self.size/self.density)**(1/3)), self.position + Vector(-(self.size/self.density)**(1/3), -(self.size/self.density)**(1/3))), remaining_size_self, self.velocity, self.density))
            new_parts.append(Particle(Vector.randVec(other.position + Vector((other.size/other.density)**(1/3), (other.size/other.density)**(1/3)), other.position + Vector(-(other.size/other.density)**(1/3), -(other.size/other.density)**(1/3))), remaining_size_other, other.velocity, other.density))
            destroy=[]
            add=[]
            for i, part in enumerate(new_parts):
                for other in new_parts[i+1:]:
                    if other not in destroy:
                        if part.touches(other):
                            add.append(part + other)
                            destroy.append(other)
                            destroy.append(part)
            for p in destroy:
                try:
                    new_parts.remove(p)
                except Exception:
                    pass
            return new_parts

    def move(self, time):
        self.position += self.velocity * time
        self.total_dist = 0

    def touches(self, other):
        return (abs(self.position - other.position) / 1) < ((self.size/self.density)**(1/3)) + ((other.size/other.density)**(1/3))

    def interact(self, other, g):
        f = g * ((self.size * other.size)/abs(self.position - other.position))
        unitVec = (self.position - other.position) / abs((self.position - other.position))
        self.velocity += (-unitVec * f) / self.size
        other.velocity += (unitVec * f) / other.size
        self.total_dist += abs(self.position - other.position)

    def get_pos(self):
        return [self.position.x, self.position.y]

    def __repr__(self):
        return "Particle@(" + str(self.position.x) + ',' + str(self.position.y) + '):(' + str(self.velocity.x) + ',' + str(self.velocity.y) + ')'

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)

    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __abs__(self):
        return sqrt(self.x**2 + self.y**2)

    def __repr__(self):
        return "Vector(%s, %s)" % (self.x, self.y)

    @staticmethod
    def randVec(minVec, maxVec):
        return Vector(random.uniform(minVec.x, maxVec.x), random.uniform(minVec.y, maxVec.y))
        #return Vector(random.gauss(0, (maxVec.x-minVec.x)/8), random.gauss(0, (maxVec.y - minVec.y)/8))
