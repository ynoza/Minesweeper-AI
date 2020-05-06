import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count
    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        ret=set()
        if len(self.cells) == self.count:
            for c in self.cells:
                ret.add(c)
        return ret

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count==0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count-=1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if self.count !=0 and cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)
        ret=set()
        ret.add(cell)
        new_v=Sentence(cells=ret, count=1)
        self.knowledge.append(new_v)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def adjacent_cell(self,cell):
        ret=set()
        for n1 in range(-1,2):
            for n2 in range(-1,2):
                ret.add((cell[0]+n1,cell[1]+n2))
        r=ret.copy()
        for c in ret:
            i,j=c
            if i<0 or j<0 or i>7 or j>7:
                r.remove(c)
        return r

    def valid_adj(self,ret):
        for c in self.moves_made:
            if c in ret:
                ret.remove(c)
        return ret

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for i,j in self.safes:
            if (not (i,j) in self.mines) and (not (i,j) in self.moves_made):
                return (i,j)
        return None

    def update_safes(self):
        #updates safes based on new sentences
        k=self.knowledge.copy()
        for sentence in k:
            ks=sentence.known_safes().copy()
            for c in ks:
                lst=self.safes.copy()
                if c not in lst:
                    self.mark_safe(c)
            km=sentence.known_mines().copy()
            for c in km:
                lst=self.mines.copy()
                if c not in lst:
                    self.mark_mine(c)

    def diff(self,i,j):
        #assumes len(j) >= len(i)
        ret=set()
        for item in j:
            if item not in i:
                ret.add(item)
        return ret


    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        self.moves_made.add(cell)
        self.mark_safe(cell)

        adj_cell=self.adjacent_cell(cell)
        adj_cell=self.valid_adj(adj_cell) #no cells already there
        new_s=Sentence(cells=adj_cell, count=count)
        boo=True
        for sentence in self.knowledge:
            if new_s == sentence:
                boo=False
        if boo:
            self.knowledge.append(new_s)

        # for o in self.knowledge:
        #     print((o.cells, o.count))

        self.update_safes()


        if self.make_safe_move()==None:

            for i in range(0,3):
                k=self.knowledge.copy()
                for s1 in k:
                    for s2 in k:
                        if len(s1.cells) > 0 and len(s2.cells)>0 and s1!= s2 and s1.cells.issubset(s2.cells) and len(s1.cells)!= len(s2.cells):
                            # print(s1.cells, s2.cells)
                            # t+=1
                            s=self.diff(s1.cells,s2.cells)
                            new_v=Sentence(cells=s, count = s2.count-s1.count)
                            # print("diff")
                            # print(new_v.cells, new_v.count)
                            self.knowledge.append(new_v)
                res = []
                for i in self.knowledge:
                    if i in res or len(i.cells)==0:
                        pass
                    else:
                        res.append(i)
                self.knowledge=res

                self.update_safes()


        # import pdb
        # pdb.set_trace()


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        print("mines")
        print(self.mines)
        # for o in self.knowledge:
        #     print((o.cells, o.count))

        lst=set()
        for sentence in self.knowledge:
            if sentence.count>0:
                lst.update(sentence.cells)

        for i in range(0, self.width):
            for j in range(0, self.height):
                if (not (i,j) in self.mines) and (not (i,j) in self.moves_made) and (not (i,j) in lst):
                    print(i,j)
                    return (i,j)

        for i in range(0, self.width):
            for j in range(0, self.height):
                if (not (i,j) in self.mines) and (not (i,j) in  self.moves_made):
                    print(i,j)
                    return (i,j)
        return None
