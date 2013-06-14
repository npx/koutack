import pyglet

class GUI(object):
    colors = {'.': (0,0,0), 'R': (0.5,0,0), 'G': (0,0.5,0), 'W': (0.9, 0.9, 0.9)}
    def __init__(self, width, height, size=100, offset=5):
        self.width = width
        self.height = height
        self.size = size
        self.offset = offset

        self.window = pyglet.window.Window()
        self.window.set_size(width*size + (width+1)*offset, height*size + (height+1)*offset)
        self.on_draw = self.window.event(self.on_draw)

        self.map = 'G'*(width*height)


    def on_draw(self):
        self.window.clear()
        #print 'drawing',
        for x in xrange(self.width):
            for y in xrange(self.height):
                c = (GUI.colors[self.map[y*self.width+x]])
                pyglet.gl.glColor3f(*c)
                xo = x*self.size + (x+1)*self.offset
                yo = y*self.size + (y+1)*self.offset
                pyglet.graphics.draw(4, pyglet.gl.GL_POLYGON,
                            ('v2i', (xo, yo,
                                     xo, yo+self.size,
                                     xo+self.size, yo+self.size,
                                     xo+self.size, yo)),
                            )
        #print 'done'

    def redraw(self):
        self.window.invalid = True
        #print 'redraw',

    def schedule(self, f, interval=None):
        if interval:
            pyglet.clock.schedule_interval(lambda x: f(), interval)
        else:
            pyglet.clock.schedule(lambda x: f())

    def display(self):
        pyglet.app.run()


def guiprocess(s, q):
    from gui import GUI
    g = GUI(s,s)

    def f():
        try:
            m = q.get(False)
            g.map = m
        except:
            pass

    g.schedule(f)

    g.display()

if __name__ == "__main__":
    from koutack import koutack, KoutackSolver
    # map to play
    mymap, s = "..W.W...R...R..W#R#W.G.R.R.GGW#R#WR.RG.GR...W*.W..", 7
    #mymap, s = "G.G....G.", 3

    # create emu and parse state
    emu = koutack()
    state = emu.parse(mymap, s)

    # print the game field
    print emu.render(state)

    # initialize GUI

    from multiprocessing import Process, Queue
    q = Queue()
    def cb(x, solved=False):
        q.put(x.getMap())


    # solve!
    def solve():
        sol = KoutackSolver.solve(emu, state, cb)
        print sol if sol else "No Solution found!"


    thread = Process(target=guiprocess, args=(s, q,))
    thread.start()

    solve()

