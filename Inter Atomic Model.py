#Testing Coulomb + Strong Force

import math
from PIL import Image, ImageDraw, ImageFont
import random
import time
start_time = time.time()

width = 1000*2
height = 1000*2

img=Image.new('RGB',(width,height),'white') 
draw=ImageDraw.Draw(img)
t=3 #line thickness

#template: draw.line([(x1,y1),(x2,y2)], fill ="black", width = t)
#template: draw.ellipse((x-r/2, y-r/2, x+r/2, y+r/2), fill = 'red', outline ='red')
font = ImageFont.truetype("cmunit.ttf",50)
#tempate: draw.text((x,y),string,font=font,fill='black')

class Vec2D:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def __str__(self):
        return f"({self.x},{self.y})"
    def __repr__(self):
        return f"Vec2D({self.x},{self.y})"
    def __add__(self,other):
        return Vec2D(self.x+other.x,self.y+other.y)
    def __neg__(self):
        return Vec2D(-self.x,-self.y)
    def __sub__(self,other):
        return self + (-other)
    def __mul__(self,k):
        return Vec2D(k * self.x, k*self.y)
    def __rmul__(self,k):
        return self * k
    def magn(self):
        return pow(self.x**2 + self.y**2, 0.5)
    def dist(self,other):
        return (self - other).magn()
    def unit(self):
        return self*(1/self.magn())

#If all masses are one, then Sum F = ma = a = dv/dt, SumF*dt = dv
#In each time step, we must:
    #calculate the total forces on each particle
    #update the velocity vector using a force * time step
    #update the position vector using a velocity * time step
    #Repeat ad infinitum
'''
Forces Involved: Between each point there are
1. Springs. F = k(x-x0)r-hat. k = spring constant, x = distance between points, x0 = equilibrium length
2. Repulsion by Coulomb forces. F = kq1q2 / r^2 r-hat. join kq1q2 into K constant, r = distance between two vectors
3. Damping. F - -bv. b = damping constant, v = velocity vector
'''

class Node:
    def __init__(self,n,pos,vel,Fnet):
        self.number = n
        self.position = pos
        self.velocity = vel
        self.netforce = Fnet
    def __str__(self):
        return "Node "+str(self.number)+" at position "+str(self.position)
    def __repr__(self):
        return "Node #"+str(self.number)+", pos:"+str(self.position)+", vel:"+str(self.velocity)+", Fnet:"+str(self.netforce)

#GENESIS!   
# template: p_1 = Node(1,Vec2D(,),Vec2D(,),Vec2D(,))

p_1 = Node(1,Vec2D(250,500),Vec2D(0,0),Vec2D(0,0))
p_2 = Node(2,Vec2D(750,500),Vec2D(0,0),Vec2D(0,0))
p_3 = Node(3,Vec2D(500,750),Vec2D(0,0),Vec2D(0,0))
p_4 = Node(4,Vec2D(500,0),Vec2D(0,0),Vec2D(0,0))
nodes = [p_1,p_2,p_3,p_4]
'''


p_5 = Node(5,Vec2D(500,500),Vec2D(0,0),Vec2D(0,0))
nodes = [p_1,p_2,p_3,p_4,p_5]

nodes = []
for n in range(1,3+1):
    x0 = random.randrange(200,800)
    y0 = random.randrange(200,800)
    nodes.append(Node(n,Vec2D(x0,y0),Vec2D(0,0),Vec2D(0,0)))
'''
p_1_history = []
p_2_history = []

def spring_force(p_1,p_2):
    #take in nodes, returns force on 1 by 2
    #F = k * ((r_2 distance r_1)-r0) * r-hat
    k = 0.04 #Spring constant
    r0 = 300 #Natural length of the spring
    return k*(p_1.position.dist(p_2.position)-r0)*(p_2.position-p_1.position).unit()

def coulomb_force(p_1,p_2):
    #take in nodes, returns force on 1 by 2
    #F = +Q / (r_1 distance r_2)^2 * r-hat
    Q = 0 #Repulsion constant #Made it 0 for now to not have it act
    return Q/(p_1.position.dist(p_2.position))**2*(p_2.position-p_1.position).unit()

def atomic_force(p_1,p_2):
    #take in node, returns force on it
    #F = a(-(r0/r)^2+(r0/r)^5)
    r0 = 250 #equilibrium distance
    a = 50 #relatively how strong the force is
    r = p_1.position.dist(p_2.position)
    r_hat = -1*(p_2.position-p_1.position).unit()
    return a*(-1*(r0/r)**2+(r0/r)**5)*r_hat

def damping_force(p):
    #take in node, returns force on it
    #F = -b*v (v = velocity vector)
    b = 0.01 #Damping constant
    return -b*p.velocity

def print_point(p,color):
    #take in node, print position to picture
    r = 10
    x = int(p.position.x)
    y = int(p.position.y)
    draw.ellipse((x-r/2, y-r/2, x+r/2, y+r/2), fill = color, outline = color)

#TIME EVOLUTION
divisions = 30 #dt represents 1 divisionth of a second
dt = 1/divisions
runtime = 800 #number of seconds to simulate
img.show()

for t in range(0,divisions*runtime):
    for node in nodes:
        #Clear the picture
        print_point(node,'white')
        #Calculate forces acting on point
        netinteractionforce = Vec2D(0,0)
        for other in nodes:
            if other.number != node.number:
                netinteractionforce += atomic_force(node,other)
        node.netforce = netinteractionforce + damping_force(node)
        #Update vel and pos by a step
        node.velocity += node.netforce*dt
        node.position += node.velocity*dt
        #Plot point:
        print_point(node,'red')

        #Store point:
        if node.number == 1 and t%10 == 0:
            p_1_history.append((t,p_1.position.x))
        if node.number == 2 and t%10 == 0:
            p_2_history.append((t,p_2.position.x))

    if t%(divisions*100) == 0:
        img.show()

#img.show()

#print(p_1_history)


#graph position
img2=Image.new('RGB',(divisions*runtime,height),'white') 
draw=ImageDraw.Draw(img2)

for history in [p_1_history,p_2_history]:
    for point in history:
        time = point[0]
        position = point[1]

        #We need time to run rightward, equal to x.
        #We need position to run up from the baseline, so 1000-pos = y
        r=10
        x = time
        y = 1000-position
        color = 'blue'
        draw.ellipse((x-r/2, y-r/2, x+r/2, y+r/2), fill = color, outline = color)
img2.show()


#print ("The program took", time.time() - start_time, "seconds to run")

