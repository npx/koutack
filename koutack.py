#!/usr/bin/env/python

from sets import Set


class koutack(object):
    """
    This class implements the game logik of koutack:

        http://armorgames.com/play/14715/koutack
    """
    # valid map symbols
    __SYMBOLS__ = {'goal': "*",
                   'floor': ".",
                   'tiles': "GR",
                   'joker': "W",
                   'special': "#"}

    class __state(object):
        """
        This class represents the state of a koutack game.
        """
        def __init__(self, m, g, s, d, sol=None):
            self.__map = m
            self.__goal = g
            self.__specials = s
            self.__size = d
            self.__solution = [] if sol is None else sol

        def getMap(self):
            return self.__map

        def getGoal(self):
            return self.__goal

        def getSize(self):
            return self.__size

        def getSpecials(self):
            return self.__specials

        def getSolution(self):
            return self.__solution

        def addMove(self, mv):
            self.__solution.append(mv)

        def __eq__(self, o):
            return self.__map == o.getMap()

        def __hash__(self):
            return hash(self.__map)

        def __setitem__(self, key, value):
            w, h = self.__size
            if not isinstance(key, tuple):
                raise TypeError("Please use coordinates! (obj[x, y])")
            x, y = key
            t = list(self.__map)
            t[x * w + y] = value
            self.__map = ''.join(t)

        def __getitem__(self, key):
            w, h = self.__size
            # koutack[x,y]
            if not isinstance(key, tuple):
                raise TypeError("Please use coordinates! (obj[x, y])")
            # linear transform (throws exception by itself)
            x, y = key
            return self.__map[x * w + y]

    def parse(self, istr, w):
        """
        Parses the String and returns a 'koutack.state' instance
        """
        # pseudo copy for later use
        tmap = istr

        # handle multiple goals
        goalC = self.__symbols("goal")
        goals = tmap.count(goalC)
        if goals > 2:
            raise ValueError("Invalid Mapstring! (too many goals)")

        # determine goal
        goal = None
        if goals == 1:
            pos = tmap.find(goalC)
            goal = (pos / w, pos % w)
            tmap = tmap.replace(goalC, '')

        # determine special fields (colorswitcher)
        specials = []
        specC = self.__symbols("special")
        for n in range(tmap.count(specC)):
            pos = tmap.find(specC)
            specials.append((pos / w, pos % w))
            tmap = tmap.replace(specC, '.', 1)

        # check if all symbols are valid
        for c in tmap:
            if c not in self.__symbols("all"):
                raise ValueError("Invalid Mapstring! (invalid char %s)" % (c))

        # length should be dividable by w
        h = len(tmap) / w
        if len(tmap) % w:
            raise ValueError("Invalid Mapstring! (length < %d)" % (w * h))

        # parsed a valid map
        return self.__state(tmap, goal, specials, (w, h))

    def __validMove(self, state, mv):
        """
        Checks if a move is valid and returns the resulting Tile or None resp.

        Implements the weird game logic. *sighs*

        Copied the weird logic.
        """
        # preparation
        n = self.__getNeighbors(state, mv, order=True)
        tiles = self.__symbols("colors")
        # let's goooo :|
        tile = None
        count = 0
        if n["L"] is not None and state[n["L"]] in tiles:
            count += 1
            tile = state[n["L"]]
            if n["R"] is not None and state[n["R"]] == tile:
                count += 1

        if n["T"] is not None and state[n["T"]] in tiles:
            if state[n["T"]] == tile:
                count += 1
            else:
                if count < 2:
                    count = 1
                    tile = state[n["T"]]

        if n["R"] is not None and state[n["R"]] in tiles:
            if state[n["R"]] == tile:
                count += 1
            else:
                if count < 2:
                    count = 1
                    tile = state[n["R"]]

        if n["B"] is not None and state[n["B"]] in tiles:
            if state[n["B"]] == tile:
                count += 1
            else:
                if count < 2:
                    count = 1
                    tile = state[n["B"]]
                    if n["L"] is not None and state[n["L"]] == tile:
                        count += 1
        # handle jokers
        if count > 0:
            joker = self.__symbols("joker")
            for d in "LTRB":
                if n[d] is not None and state[n[d]] == joker:
                    count += 1
        # final check
        if count >= 2:
            return tile
        return None

    def getMoves(self, state):
        """
        Returns all valid moves on the field.
        """
        w, h = state.getSize()
        # get all adjacent, empty platforms
        possible = Set()
        for x in range(h):
            for y in range(w):
                cur = (x, y)
                if state[cur] in self.__symbols("tiles"):
                    for n in self.__getNeighbors(state, cur):
                        if state[n] not in self.__symbols("tiles"):
                            possible.add(n)
        # check for valid moves
        moves = []
        for p in possible:
            if self.__validMove(state, p):
                moves.append(p)
        # got dem moves
        return moves

    def __getNeighbors(self, state, coords, order=False):
        """
        Returns the neighboring positions on the field.
        """
        w, h = state.getSize()
        x, y = coords
        n = {"L": (x - 1, y), "R": (x + 1, y),
             "T": (x, y - 1), "B": (x, y + 1)}
        # a filter: returns True if coords are on map
        onMap = lambda (x, y): 0 <= x <= h - 1 and 0 <= y <= w - 1
        # if there is no order required return neighbors on map
        if not order:
            r = n.itervalues()
            return filter(onMap, r)
        # else return dict to access properly >_>
        else:
            for (k, v) in n.iteritems():
                if not onMap(v):
                    n[k] = None
            return n

    def copy(self, state):
        """
        Returns a copy of the given state. [copy of specials not necessary]
        """
        return self.__state(state.getMap(), state.getGoal(),
                            state.getSpecials()[:], state.getSize(),
                            sol=state.getSolution()[:])

    def move(self, state, mv):
        """
        Performs the given move on the given state.
        """
        tile = self.__validMove(state, mv)
        if not tile:
            raise Exception("Invalid Move! [%r]" % (mv,))
        # neighboring positions
        npos = self.__getNeighbors(state, mv)
        # free the target tile and jokers
        for n in npos:
            if state[n] in [tile, self.__symbols("joker")]:
                state[n] = '.'
        # check if colorswitcher
        if mv in state.getSpecials():
            tiles = self.__symbols("colors")
            # assumes 2 tiles max
            state[mv] = tiles[(tiles.find(tile) + 1) % len(tiles)]
        else:
            state[mv] = tile
        state.addMove(mv)

    def isSolved(self, state):
        """
        Returns whether the given state is solved or not.
        """
        # count piles left
        piles = 0
        for s in self.__symbols("tiles"):
            piles += state.getMap().count(s)

        # if there is a goal achieve 'perfect' solution
        solution = (piles == 1)
        if state.getGoal():
            perfect = state[state.getGoal()] in self.__symbols("tiles")
            return solution and perfect
        return solution

    def __symbols(self, s):
        """
        Returns values from __SYMBOLS__.
        """
        if s == "all":
            return ''.join(koutack.__SYMBOLS__.values())
        if s == "tiles":
            return koutack.__SYMBOLS__["tiles"] + koutack.__SYMBOLS__["joker"]
        if s == "colors":
            return koutack.__SYMBOLS__["tiles"]
        return koutack.__SYMBOLS__[s]

    def render(self, state):
        """
        Renders the state to a nicely formatted string.
        """
        w, h = state.getSize()
        r = ""
        rows = []
        for r in range(h):
            # transform row to list and add spaces
            row = list(state.getMap()[r * w:(r + 1) * w])
            row = ' '.join(row)
            row = ' ' + row + ' '
            row = list(row)
            # check if goal is on that line
            g = state.getGoal()
            gr, gc = g if g else (None, None)
            if gr == r:
                pos = (gc * 2 + 1)
                l, r = pos - 1, pos + 1
                row[l], row[r] = "[", "]"
            # find all specials on that line
            specials = filter(lambda c: c[0] == r, state.getSpecials())
            if specials:
                for (x, y) in specials:
                    pos = (y * 2 + 1)
                    if row[pos] == self.__symbols("floor"):
                        row[pos] = self.__symbols("special")
            # glue things back together
            rows.append(''.join(row))
        return '\n'.join(rows)


class KoutackSolver(object):
    """
    Solver is supposed to solve the given State
    """
    @classmethod
    def solve(self, emu, state, callback=None):
        """
        The solving algorithm.
        """
        if not (emu and state):
            raise Exception("No Emulator or State given!")

        # queues
        todo = []
        done = Set()
        todo.append(state)

        # loop
        while todo:
            cur = todo.pop(-1)
            moves = emu.getMoves(cur)
            for m in moves:
                copy = emu.copy(cur)
                emu.move(copy, m)
                if emu.isSolved(copy):
                    if callback:
                        callback(cur, solved=True)
                    return copy.getSolution()
                if not copy.getMap() in done:
                    if not copy in todo:
                        if callback:
                            callback(cur, solved=False)
                        #todo.append(copy)
                        todo.append(copy)
            done.add(cur.getMap())
            #print len(todo), len(done)
        return None


def myTimeit():
    maps = "......GGG.....GR#.#R.*RRR."
    K = koutack()
    s = K.parse(maps, 5)
    KoutackSolver.solve(K, s)

if __name__ == "__main__":
    # map to play
    mymap, s = "..W.W...R...R..W#R#W.G.R.R.GGW#R#WR.RG.GR...W*.W..", 7
    #mymap, s = "......GGG.....GR#.#R.*RRR.", 5
    #mymap, s = "G.G....G.", 3

    # create emu and parse state
    emu = koutack()
    state = emu.parse(mymap, s)

    # print the game field
    print emu.render(state)

    # solve!
    sol = KoutackSolver.solve(emu, state)
    print sol if sol else "No Solution found!"
