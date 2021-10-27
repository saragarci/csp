import copy
import itertools


class CSP:
    def __init__(self):
        # self.variables is a list of the variable names in the CSP
        self.variables = []

        # self.domains[i] is a list of legal values for variable i
        self.domains = {}

        # self.constraints[i][j] is a list of legal value pairs for
        # the variable pair (i, j)
        self.constraints = {}

    def add_variable(self, name, domain):
        """Add a new variable to the CSP. 'name' is the variable name
        and 'domain' is a list of the legal values for the variable.
        """
        self.variables.append(name)
        self.domains[name] = list(domain)
        self.constraints[name] = {}

    def get_all_possible_pairs(self, a, b):
        """Get a list of all possible pairs (as tuples) of the values in
        the lists 'a' and 'b', where the first component comes from list
        'a' and the second component comes from list 'b'.
        """
        return itertools.product(a, b)

    def get_all_arcs(self):
        """Get a list of all arcs/constraints that have been defined in
        the CSP. The arcs/constraints are represented as tuples (i, j),
        indicating a constraint between variable 'i' and 'j'.
        """
        return [(i, j) for i in self.constraints for j in self.constraints[i]]

    def get_all_neighboring_arcs(self, var):
        """Get a list of all arcs/constraints going to/from variable
        'var'. The arcs/constraints are represented as in get_all_arcs().
        """
        return [(i, var) for i in self.constraints[var]]

    def add_constraint_one_way(self, i, j, filter_function):
        """Add a new constraint between variables 'i' and 'j'. The legal
        values are specified by supplying a function 'filter_function',
        that returns True for legal value pairs and False for illegal
        value pairs. This function only adds the constraint one way,
        from i -> j. You must ensure that the function also gets called
        to add the constraint the other way, j -> i, as all constraints
        are supposed to be two-way connections!
        """
        if not j in self.constraints[i]:
            # First, get a list of all possible pairs of values between variables i and j
            self.constraints[i][j] = self.get_all_possible_pairs(self.domains[i], self.domains[j])

        # Next, filter this list of value pairs through the function
        # 'filter_function', so that only the legal value pairs remain
        self.constraints[i][j] = list(filter(lambda value_pair: filter_function(*value_pair), self.constraints[i][j]))

    def add_all_different_constraint(self, variables):
        """Add an Alldiff constraint between all of the variables in the
        list 'variables'.
        """
        for (i, j) in self.get_all_possible_pairs(variables, variables):
            if i != j:
                self.add_constraint_one_way(i, j, lambda x, y: x != y)

    def backtracking_search(self):
        """This functions starts the CSP solver and returns the found
        solution.
        """
        # Make a so-called "deep copy" of the dictionary containing the
        # domains of the CSP variables. The deep copy is required to
        # ensure that any changes made to 'assignment' does not have any
        # side effects elsewhere.
        assignment = copy.deepcopy(self.domains)

        # Run AC-3 on all constraints in the CSP, to weed out all of the
        # values that are not arc-consistent to begin with
        self.inference(assignment, self.get_all_arcs())

        # Call backtrack with the partial assignment 'assignment'
        return self.backtrack(assignment)

    def backtrack(self, assignment):
        """The function 'Backtrack' from the pseudocode in the
        textbook.

        The function is called recursively, with a partial assignment of
        values 'assignment'. 'assignment' is a dictionary that contains
        a list of all legal values for the variables that have *not* yet
        been decided, and a list of only a single value for the
        variables that *have* been decided.

        When all of the variables in 'assignment' have lists of length
        one, i.e. when all variables have been assigned a value, the
        function should return 'assignment'. Otherwise, the search
        should continue. When the function 'inference' is called to run
        the AC-3 algorithm, the lists of legal values in 'assignment'
        should get reduced as AC-3 discovers illegal values.

        IMPORTANT: For every iteration of the for-loop in the
        pseudocode, you need to make a deep copy of 'assignment' into a
        new variable before changing it. Every iteration of the for-loop
        should have a clean slate and not see any traces of the old
        assignments and inferences that took place in previous
        iterations of the loop.
        """
        # TODO: IMPLEMENT THIS
        if self.is_complete(assignment):
            print("Solution found!: ", assignment)
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            asg = copy.deepcopy(assignment)
            # check that value is consistent with the assignment
            if self.is_consistent(value, var, asg):
                asg[var] = [value]
                inferences = self.inference(asg, self.get_all_neighboring_arcs(var))
                if inferences:
                    result = self.backtrack(asg)
                    if result is not None:
                        return result
                # remove var=value from assignment
                if var in asg:
                    del asg[var]
        return None

    def is_complete(self, assignment):
        # for all the variables in assignment
        for var in assignment.values():
            # if the variable does not have exactly one value, return false
            if len(var) != 1:
                return False

        # if all variables have exactly one value, then the assignment is complete
        return True

    def select_unassigned_variable(self, assignment):
        """The function 'Select-Unassigned-Variable' from the pseudocode
        in the textbook. Should return the name of one of the variables
        in 'assignment' that have not yet been decided, i.e. whose list
        of legal values has a length greater than one.
        """
        # TODO: IMPLEMENT THIS
        # TODO: is there a better way to select this variable?
        # for every variable in assignment
        for var in assignment.keys():
            # return the first one that has more than one value in its domain
            if len(assignment[var]) > 1:
                return var

    def order_domain_values(self, var, asg):
        # TODO: can we order this to optimize the search?
        return self.domains[var]

    def is_consistent(self, val, var, asg):
        for var2 in self.constraints[var].keys():
            is_consistent = False
            for val2 in asg[var2]:
                if (val, val2) in self.constraints[var][var2]:
                    is_consistent = True
            if not is_consistent:
                return False
        return True

    def inference(self, assignment, queue):
        """The function 'AC-3' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'queue'
        is the initial queue of arcs that should be visited.
        """
        # TODO: IMPLEMENT THIS
        # while we there are edges to revise
        while len(queue) > 0:
            (i, j) = queue.pop(0)
            if self.revise(assignment, i, j):
                # if i and j are not consistent, return false
                if len(assignment[i]) == 0:
                    return False
                # add the edges needed to re-revise
                for x in self.get_edges_to(i, exclude=j):
                    if x not in queue:
                        queue.append(x)
        # when every edge has been revised (they are consistent), return true
        return True

    def get_edges_to(self, i, exclude):
        """
        Returns all the edges from the neighbors of i (except j) to i

        :param i: all the neighbors to be found from
        :param exclude: neighbor not to be tracked from i
        :return: edges from all the neighbors of i (except j) to i
        """
        edges = []
        for x in self.constraints[i].keys():
            if x != exclude:
                edges.append((x, i))
        return edges

    def revise(self, asg, i, j):
        """The function 'Revise' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'i' and
        'j' specifies the arc that should be visited. If a value is
        found in variable i's domain that doesn't satisfy the constraint
        between i and j, the value should be deleted from i's list of
        legal values in 'assignment'.
        """
        # TODO: IMPLEMENT THIS
        revised = False
        is_satisfied = False
        # for every value x in the domain of i
        for x in asg[i]:
            # find at least one value y in the domain of j that satisfies the constraint
            for y in asg[j]:
                if (x, y) in self.constraints[i][j]:
                    is_satisfied = True
                    break
                else:
                    is_satisfied = False
            # if no value is found
            if not is_satisfied:
                # then remove x (since it is not satisfied)
                asg[i].remove(x)
                # and make sure to revise again
                revised = True
        return revised


def create_map_coloring_csp():
    """Instantiate a CSP representing the map coloring problem f rom the
    textbook. This can be useful for testing your CSP solver as you
    develop your code.
    """
    csp = CSP()
    states = ['WA', 'NT', 'Q', 'NSW', 'V', 'SA', 'T']
    edges = {'SA': ['WA', 'NT', 'Q', 'NSW', 'V'], 'NT': ['WA', 'Q'], 'NSW': ['Q', 'V']}
    colors = ['red', 'green', 'blue']
    for state in states:
        csp.add_variable(state, colors)
    for state, other_states in edges.items():
        for other_state in other_states:
            csp.add_constraint_one_way(state, other_state, lambda i, j: i != j)
            csp.add_constraint_one_way(other_state, state, lambda i, j: i != j)
    return csp


def create_sudoku_csp(filename):
    """Instantiate a CSP representing the Sudoku board found in the text
    file named 'filename' in the current directory.
    """
    csp = CSP()
    board = list(map(lambda x: x.strip(), open(filename, 'r')))

    for row in range(9):
        for col in range(9):
            if board[row][col] == '0':
                csp.add_variable('%d-%d' % (row, col), list(map(str, range(1, 10))))
            else:
                csp.add_variable('%d-%d' % (row, col), [board[row][col]])

    for row in range(9):
        csp.add_all_different_constraint(['%d-%d' % (row, col) for col in range(9)])
    for col in range(9):
        csp.add_all_different_constraint(['%d-%d' % (row, col) for row in range(9)])
    for box_row in range(3):
        for box_col in range(3):
            cells = []
            for row in range(box_row * 3, (box_row + 1) * 3):
                for col in range(box_col * 3, (box_col + 1) * 3):
                    cells.append('%d-%d' % (row, col))
            csp.add_all_different_constraint(cells)

    return csp


def print_sudoku_solution(solution):
    """Convert the representation of a Sudoku solution as returned from
    the method CSP.backtracking_search(), into a human readable
    representation.
    """
    for row in range(9):
        for col in range(9):
            print(solution['%d-%d' % (row, col)][0], end=" "),
            if col == 2 or col == 5:
                print('|', end=" "),
        print("")
        if row == 2 or row == 5:
            print('------+-------+------')


def create_example_1_csp():
    """Instantiate a CSP representing the example of AC-3 done in the assignment lecture.
    """
    csp = CSP()
    csp.add_variable('A', [1, 2, 3])
    csp.add_variable('B', [2])
    csp.add_variable('C', [3])
    csp.add_all_different_constraint(['A', 'B', 'C'])
    return csp


def ac3_example_1():
    csp_example = create_example_1_csp()
    print("Variables: ", csp_example.variables)
    print("Domains: ", csp_example.domains)
    print("Constraints: ", csp_example.constraints)
    print("\n")

    # AC-3
    assignment = copy.deepcopy(csp_example.domains)
    queue = [('C', 'A'), ('C', 'B'), ('B', 'A'), ('B', 'C'), ('A', 'B'), ('A', 'C')]
    print("Assignment before: ", assignment)
    print("Queue before: ", queue)
    csp_example.inference(assignment, queue)
    print("Queue after: ", queue)
    print("Assignment after: ", assignment)


def create_example_2_csp():
    """Instantiate a CSP representing the backtrack search example done in the assignment lecture.
    """
    csp = CSP()
    csp.add_variable('1', ['R'])
    csp.add_variable('2', ['R', 'G', 'B'])
    csp.add_variable('3', ['R', 'G', 'B'])
    csp.add_variable('4', ['R', 'G', 'B'])
    csp.add_variable('5', ['R', 'B'])

    edges = {'1': ['2', '3'], '2': ['1', '3', '4'], '3': ['1', '2', '4', '5'], '4': ['2', '3', '5'], '5': ['3', '4']}
    for state, other_states in edges.items():
        for other_state in other_states:
            csp.add_constraint_one_way(state, other_state, lambda i, j: i != j)
            csp.add_constraint_one_way(other_state, state, lambda i, j: i != j)
    return csp


def ac3_example_2():
    csp_example = create_example_2_csp()
    print("Variables: ", csp_example.variables)
    print("Domains: ", csp_example.domains)
    print("Constraints: ", csp_example.constraints)
    print("\n")

    # AC-3
    assignment = copy.deepcopy(csp_example.domains)
    queue = [('1', '3'), ('1', '2'), ('2', '1'), ('2', '3'), ('2', '4'), ('4', '2'),
             ('4', '3'), ('4', '5'), ('3', '1'), ('3', '2'), ('3', '5'), ('3', '4'),
             ('5', '3'), ('5', '4')]
    print("Assignment before: ", assignment)
    print("Queue before: ", queue)
    csp_example.inference(assignment, queue)
    print("Queue after: ", queue)
    print("Assignment after: ", assignment)


def backtrack_search_example_2():
    csp_example = create_example_2_csp()
    print("Variables: ", csp_example.variables)
    print("Domains: ", csp_example.domains)
    print("Constraints: ", csp_example.constraints)
    print("\n")

    # Backtracking search
    csp_example.backtracking_search()


def backtrack_search_map_coloring():
    csp_example = create_map_coloring_csp()
    print("Variables: ", csp_example.variables)
    print("Domains: ", csp_example.domains)
    print("Constraints: ", csp_example.constraints)
    print("\n")

    # Backtracking search
    csp_example.backtracking_search()


def backtrack_search_sudoku(file):
    csp_example = create_sudoku_csp(file)
    solution = csp_example.backtracking_search()
    if solution is not None:
        print_sudoku_solution(solution)


if __name__ == "__main__":
    #ac3_example_1()
    #ac3_example_2()
    #backtrack_search_example_2()
    #backtrack_search_map_coloring()
    #backtrack_search_sudoku("easy.txt")
    #backtrack_search_sudoku("medium.txt")
    #backtrack_search_sudoku("hard.txt")
    backtrack_search_sudoku("veryhard.txt")