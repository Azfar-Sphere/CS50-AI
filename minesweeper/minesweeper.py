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
        mines = set()
        if self.count == 0:
            return mines
        
        if self.count == len(self.cells):
            return self.cells
        
        return mines
            
    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        safes = set()
        if self.count == 0:
            return self.cells
        
        if self.count == len(self.cells):
            return safes
        
        return safes
        
    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

        if len(self.cells) == 0:
            del self

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        self.cells.discard(cell)
        if len(self.cells) == 0:
            del self


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

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

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

        for sentence in self.knowledge:
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)

        self.moves_made.add(cell)

        self.mark_safe(cell)
        
        neighbours = self.get_neighbours(cell)

        self.add_sentence(neighbours, count)

        for i, sentence in enumerate(self.knowledge):
            
            try:
                mines = sentence.known_mines().copy()
                safes = sentence.known_safes().copy()
            
            except:
                pass

            else:
                if mines:
                    for mine in mines:
                        self.mark_mine(mine)
                
                if safes:
                    for safe in safes:
                        self.mark_safe(safe)

        for i in range(len(self.knowledge.copy()) - 1):
            for j in range(i + 1, len(self.knowledge.copy())):

                set1 = self.knowledge[i]
                set2 = self.knowledge[j]
                
                if len(set1.cells) == 0 or len(set2.cells) == 0:
                    break

                if set1.cells.issubset(set2.cells) and set1.cells != set2.cells:

                    set3_cells = list(set2.cells - set1.cells)

                    count3 = set2.count - set1.count

                    if len(set3_cells) > 0:

                        print(
                            f"Set1 is Subset of Set2....   set1:{set1.cells}{set1.count}, set2:{set2.cells}{set2.count},  set3:{set3_cells}{count3}")
                        self.add_sentence(set3_cells, count3)

                if set2.cells.issubset(set1.cells) and set1.cells != set2.cells:

                    set3_cells = list(set1.cells - set2.cells)

                    count3 = set1.count - set2.count

                    if len(set3_cells) > 0:

                        print(
                            f"Set2 is Subset of Set1....   set2:{set2.cells}{set2.count}, set1:{set1.cells}{set1.count},  set3:{set3_cells}{count3}")
                        self.add_sentence(set3_cells, count3)

        for i, sentence in enumerate(self.knowledge):
            
            try:
                mines = sentence.known_mines().copy()
                safes = sentence.known_safes().copy()
            
            except:
                pass

            else:
                if mines:
                    for mine in mines:
                        self.mark_mine(mine)
                
                if safes:
                    for safe in safes:
                        self.mark_safe(safe)

    def get_neighbours(self, cell):

        neighbours = []
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                if (i, j) != cell and -1 < i < self.height and -1 < j < self.width:
                    neighbours.append((i, j))

        return neighbours
    
    def add_sentence(self, cells, count):

        mines = list(self.mines)
        safes = list(self.safes)

        cells_copy = cells.copy()

        for mine in mines:
            if mine in cells_copy:
                cells.remove(mine)
                count -= 1

        for safe in safes:
            if safe in cells_copy:
                cells.remove(safe)
        
        if len(cells) != 0:
            new_sentence = Sentence(cells, count)

            if new_sentence in self.knowledge:
                pass

            else:
                print("Adding Sentence: ", new_sentence)
                self.knowledge.append(new_sentence)
                return new_sentence

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        unmoved_safes = list(self.safes - self.moves_made)
 
        if not unmoved_safes:
            return None
        
        cell = random.choice(unmoved_safes)

        if cell:
            return cell
        
        else:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        cell = (random.randrange(self.height - 1), random.randrange(self.width - 1))

        if cell not in self.moves_made and cell not in self.mines:
            return cell
        
        else:
            return None
        
        return None
