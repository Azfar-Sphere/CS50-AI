import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for key, value in self.domains.items():
            length = key.length
            for word in value.copy():
                if len(word) != length:
                    self.domains[key].remove(word)
                
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]
        i = overlap[0]
        j = overlap[1]

        if overlap:
            valid_words = set()

            for wordX in self.domains[x]:
                for wordY in self.domains[y]:
                    if wordX[i] == wordY[j]:
                        valid_words.add(wordX)
                        break
            
            if valid_words == self.domains[x]:
                return False
            
            self.domains[x] = valid_words
            return True

        return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs:
            arcs = set(arcs)
        
        if arcs == None:
            arcs = set()
            variables = self.crossword.variables

            for variable in variables:
                neighbors = self.crossword.neighbors(variable)

                for neighbor in neighbors:
                    arc = (variable, neighbor)
                    arcs.add(arc)

        while len(arcs) > 0:
            arc = arcs.pop()
            X = arc[0]
            Y = arc[1]

            if self.revise(X, Y):

                if len(self.domains[X]) == 0:
                    return False
                
                neighbors = self.crossword.neighbors(X)
                if neighbors:
                    for Z in neighbors:
                        arcs.add((X, Z))
                        arcs.add((Z, X))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment:
                return False
            if not assignment[variable]:
                return False
        return True
        
    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for variable in self.crossword.variables:

            if variable in assignment:
                value = assignment[variable]

                if value:
                    if len(value) != variable.length:
                        return False
                    
                    neighbors = self.crossword.neighbors(variable)

                    for neighbor in neighbors:
                        if neighbor in assignment:
                            n_value = assignment[neighbor]

                            if n_value:

                                if value == n_value:
                                    return False
                                
                                overlap = self.crossword.overlaps[variable, neighbor]
                                if overlap:
                                    i = overlap[0]
                                    j = overlap[1]

                                    if value[i] != n_value[j]:
                                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        order_values = {value: 0 for value in self.domains[var]}

        for value in self.domains[var]:
            neighbors = self.crossword.neighbors(var)

            for neighbor in neighbors:

                if neighbor in assignment:
                    continue

                overlap = self.crossword.overlaps[var, neighbor]
                i = overlap[0]
                j = overlap[1]

                for n_value in self.domains[neighbor]:
                    if value[i] != n_value[j]:
                        order_values[value] += 1
        
        sorted_domains = [key for key, value in sorted(
            order_values.items(), key=lambda item: item[1])]
        return sorted_domains

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        variables = self.crossword.variables
        variable_values = {variable: 0 for variable in variables if variable not in assignment}

        for var in variables:
            if var not in assignment:
                variable_values[var] += len(self.domains[var])
        
        sorted_variables = [key for key, value in sorted(
            variable_values.items(), key=lambda item: item[1])]
        
        if len(list(variable_values.values())) == len(set(variable_values.values())):
            return sorted_variables[0]

        sorted_vars = list(sorted_variables)
        sorted_values = []
        for variable in sorted_variables:
            sorted_values.append(variable_values[variable])

        duplicate_indexes = []
        for j in range(1, len(sorted_values)):
            if sorted_values[0] == sorted_values[j]:
                duplicate_indexes.append((0, j))

        num_neigbors = {}
        for index in duplicate_indexes:
            var1 = sorted_vars[index[0]]
            var2 = sorted_vars[index[1]]

            neighbor1 = len(self.crossword.neighbors(var1))
            neighbor2 = len(self.crossword.neighbors(var2))

            num_neigbors.update({var1: neighbor1})           
            num_neigbors.update({var2: neighbor2})           

        sorted_num_neighbors = [key for key, value in sorted(
            num_neigbors.items(), key=lambda item: item[1], reverse=True)]
        if sorted_num_neighbors:
            return sorted_num_neighbors[0]
        else:
            return sorted_variables[0]
    
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        variables = self.crossword.variables

        if len(variables) == len(assignment.values()):
            return assignment
        
        for variable in variables:
            if variable not in assignment:

                for domain in self.domains[variable]:
                    assignment.update({variable: domain})

                    if self.consistent(assignment):

                        result = self.backtrack(assignment)
                        if result:
                            return result
                        
                    assignment.pop(variable)

                return None
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
