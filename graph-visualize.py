import random
import tkinter as tk
import math

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

    @staticmethod
    def zero():
        return Vec2D(0,0)
    @staticmethod
    def inf():
        return Vec2D(math.inf,math.inf)
    @staticmethod
    def randgauss(mu=0,sigma=1):
        return Vec2D(random.gauss(mu,sigma),random.gauss(mu,sigma))

class Graph:
    def __init__(self):
        """Make an empty graph"""
        self.neighbors = []
        self.positions = []
        self.velocities = []
        self.lowest = Vec2D.inf()
        self.highest = -Vec2D.inf()
        self.buckets = {}
        self.bucket_size = 10
        self.count = 0
    def is_edge(self,i,j):
        """Return true if (i,j) is an edge"""
        if i > j:
            i,j = j,i
        # i is older (smaller index) than j
        # so it will be present in j's adjacency list
        return i in self.neighbors[j]
    def insert_node(self,where,adjacent=[]):
        """Insert a node at `where`, and edges between j and everything in `adjancent`.
           Returns the index of the new node"""
        idx = self.count
        # append the adjacency list. since we're the latest index, we're higher than every one else, so we get our edges
        self.neighbors.append(adjacent[:])
        # record our exact location
        self.positions.append(None)
        self.update_pos(idx,where)
        self.velocities.append(Vec2D.zero())
        # insert into the correct bucket
        key = (where.x//self.bucket_size, where.y//self.bucket_size)
        try:
            self.buckets[key].append(idx)
        except KeyError:
            self.buckets[key] = [idx]
        self.count += 1
        return idx
    def insert_edge(self,i,j):
        """Make (i,j) an edge"""
        if i > j:
            i,j = j,i
        # i is older (smaller index)
        # so it is present in j's adjacency list
        if i in self.neighbors[j]:
            return
        self.neighbors[j].append(i)
    def update_pos(self,i,pos):
        """Updates the position of the node, and the dimensions of the graph"""
        # extend dimensions lower
        if pos.x < self.lowest.x: self.lowest.x = pos.x
        if pos.y < self.lowest.y: self.lowest.y = pos.y
        # extend dimensions higher
        if pos.x > self.highest.x: self.highest.x = pos.x
        if pos.y > self.highest.y: self.highest.y = pos.y
        # update position
        self.positions[i] = pos
    
    def to_latex(self,node_settings=""):
        print("\\begin{tikzpicture}")
        print("    % the nodes")
        for i,where in enumerate(self.positions):
            print(f"    \\node (n{i}){node_settings} at {where} {{ }} ;")
        print("    % the edges")
        for i,neighborhood in enumerate(self.neighbors):
            for j in neighborhood:
                print(f"    \\draw (n{i}) -- (n{j}) ;")
        print("\\end{tikzpicture}")

    def apply_forces(self,repulse_factor=10,spring_factor=1,dx=0.5):
        """attempt to make the graph more balanced by evening out the edge lengths"""
        # calculate the net force on each node
        forces = [Vec2D.zero() for _ in range(self.count)]
        # attractive spring force because of every edge
        for i,adjacent in enumerate(self.neighbors):
            for j in adjacent:
                # imagine the edge is a spring connecting nodes `i` and `j`
                # the force pulling on `i` is proportional to the distance,
                force = spring_factor * (self.positions[j] - self.positions[i])
                forces[i] += force
                forces[j] -= force
        # repulsive force between every node
        for i in range(self.count):
            for j in range(i):
                # each node repulses each other, and it falls off with the square of the distance
                vec = self.positions[j] - self.positions[i]
                # v/(|v|^3) = (v/|v|) * (1/|v|^2)
                dist = vec.magn()
                if dist == 0:
                    dist = 10e-20
                force = repulse_factor * pow(dist, -3) * vec
                forces[i] += force
                forces[j] -= force
        
        # update velocity, position
        for i,force in enumerate(forces):
            self.velocities[i] += force * dx
            pos = self.positions[i] + self.velocities[i] * dx
            self.update_pos(i,pos)

    def print_nodes(self):
        for pos in self.positions:
            print(pos)

def make_example(node_count=10,iters=10_000):
    window_x = (-10,10)
    window_y = (-1,10)
    # picking a random point in our window
    def rand_point():
        x = random.randint(window_x[0],window_x[1])
        y = random.randint(window_y[0],window_y[1])
        return Vec2D(x,y)
    
    # making the example
    g = Graph()
    # first, scatter some nodes accross the window. leave them unconnected for now
    unprocessed = [g.insert_node(where=rand_point()) for _ in range(node_count)]
    random.shuffle(unprocessed) # important for variety in our example graphs

    # builded up a connected component
    connected = [unprocessed.pop()]
    for i in unprocessed:
        degree = random.choice([1,2,2,3]) # todo: better
        for _ in range(degree):
            j = random.choice(connected)
            g.insert_edge(i,j)
        connected.append(i)
        
    return g

class Application(tk.Frame):
    def __init__(self, graph, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.graph = graph
        self.stepno = 0
        
        self.create_widgets()

        self.canvas = tk.Canvas(self, width = 600, height = 400)
        self.canvas.pack(fill=tk.BOTH, expand=1)

        

    def create_widgets(self):
        # step will advance the simulation 1 step
        self.step_button = tk.Button(self, text="Step",
                              command=self.step)
        self.step_button.pack(side="top")

        # show latex will print the latex for the graph
        self.show_latex = tk.Button(self, text="Show Latex",
                                    command=self.show_latex)
        self.show_latex.pack(side="top")

        self.step_large_button = tk.Button(self, text="Step 10",
                                    command=lambda: self.step_by(10))
        self.step_large_button.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def draw(self):
        self.canvas.delete("all")
        # transforms a point in the graph space to the canvas space
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x_scale = canvas_width / 100
        y_scale = canvas_height / 100
        def transform(p):
            p = p - Vec2D(-50, -50)
            return Vec2D(p.x * x_scale, p.y * y_scale)

        # plot all the nodes
        for i,pos in enumerate(self.graph.positions):
            pos = transform(pos)
            self.canvas.create_oval(pos.x-1, pos.y-1, pos.x+1, pos.y+1,
                               width=2)
            for j in self.graph.neighbors[i]:
                end_pos = transform(self.graph.positions[j])
                self.canvas.create_line(pos.x, pos.y, end_pos.x, end_pos.y)        

    def show_latex(self):
        print("Showing latex...")
        self.graph.to_latex()
        
    def step(self):
        self.stepno += 1
        self.graph.apply_forces()
        self.draw()

    def step_by(self,n):
        for _ in range(n):
            self.stepno += 1
            self.graph.apply_forces()
        self.draw()
        

g = Graph()
u = g.insert_node( Vec2D(-10, 0) )
v = g.insert_node( Vec2D( 10, 0) )
g.insert_edge(u, v)


root = tk.Tk()
app = Application(graph = g, master = root)
app.mainloop()
