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

        # counters to compare results
        self.backtrack_calls_count = 0
        self.backtrack_returns_failure_count = 0

        # strategies for selecting unassigned variable
        self.select_unassigned_strategy_static = False
        self.select_unassigned_strategy_mrv = True
        self.select_unassigned_strategy_degree = True

        # strategies for ordering domain values
        self.order_domain_values_strategy_static = False
        self.order_domain_values_strategy_least_constraint = True

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
        from i -> j. NB!: Ensure that the function also gets called
        to add the constraint the other way, j -> i, as all constraints
        are supposed to be two-way connections.
        """
        if not j in self.constraints[i]:
            # First, get a list of all possible pairs of values between
            # variables i and j
            self.constraints[i][j] = self.get_all_possible_pairs(
                self.domains[i], self.domains[j])

        # Next, filter this list of value pairs through the function
        # 'filter_function', so that only the legal value pairs remain
        self.constraints[i][j] = list(filter(lambda value_pair: 
            filter_function(*value_pair), self.constraints[i][j]))

    def add_all_different_constraint(self, variables):
        """Add an Alldiff constraint between all of the variables in the
        list 'variables'.
        """
        for (i, j) in self.get_all_possible_pairs(variables, variables):
            if i != j:
                self.add_constraint_one_way(i, j, lambda x, y: x != y)

    def backtracking_search(self):
        """Starts the CSP solver and returns the found solution.
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
        function will return 'assignment'. Otherwise, the search
        continues. When the function 'inference' is called to run
        the AC-3 algorithm, the lists of legal values in 'assignment'
        gets reduced as AC-3 discovers illegal values.
        """
        self.backtrack_calls_count += 1

        # return if the assignment is complete
        if self.is_complete(assignment):
            return assignment

        # select the next variable to expand
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            asg = copy.deepcopy(assignment)
            # check that value is consistent with the assignment
            if self.is_consistent(value, var, asg):
                # add { var = value } to assignment
                asg[var] = [value]
                # perform AC-3 on the assignment passing as the queue all the
                # edges of the selected variable with its neighbours
                inferences = self.inference(asg, 
                    self.get_all_neighboring_arcs(var))
                # if the CSP is solved
                if inferences:
                    # the we call recursively call backtrack with the current 
                    # assignment
                    result = self.backtrack(asg)
                    if result is not None:
                        return result
                # if failure, remove { var = value } from the assignment
                if var in asg:
                    del asg[var]

        # return failure if no solution is found
        self.backtrack_returns_failure_count += 1
        return None

    def is_complete(self, assignment):
        """Returns true if the assignment is complete, i.e. if all the 
        variables have been assigned exactly one value.
        """
        # for all the variables in assignment
        for var in assignment.values():
            # if the variable does not have exactly one value, return false
            if len(var) != 1:
                return False
        # if all variables have exactly one value, then the assignment is
        # complete
        return True

    def select_unassigned_variable(self, assignment):
        """The function 'Select-Unassigned-Variable' from the pseudocode
        in the textbook. Returns the name of one of the variables
        in 'assignment' that have not yet been decided, i.e. whose list
        of legal values has a length greater than one.
        """
        # if static strategy is selected
        if self.select_unassigned_strategy_static:
            # for every variable in assignment
            for var in assignment.keys():
                # return the first one that has more than one value in its
                # domain
                if len(assignment[var]) > 1:
                    return var
        # if minimum remaining values heuristic is selected
        elif self.select_unassigned_strategy_mrv:
            # if degree heuristic is select and it is the first iteration
            if self.select_unassigned_strategy_degree \
                 and self.backtrack_calls_count == 1:
                # return degree heuristic
                return self.degree_heuristic(assignment)
            # return mrv heuristic
            return self.mrv_heuristic(assignment)

    def degree_heuristic(self, assignment):
        """Returns the variable with the highest number of constraints.
        """
        max_var = None
        max_value = None
        # for all the constraints
        for var in self.constraints.keys():
            # if the variable is not yet assigned, find the number of 
            # dependencies it has with the rest of the variables
            if len(assignment[var]) > 1:
                if max_var is None and max_value is None:
                    max_var = var
                    max_value = len(self.constraints[var])
                else:
                    if max_value < len(self.constraints[var]):
                        max_var = var
                        max_value = len(self.constraints[var])
        # return the variable with the highest number of constraints
        return max_var

    def mrv_heuristic(self, asg):
        """Returns de variable that has the fewest legal values.
        """
        min_var = None
        min_value = None
        # for all the variables in the assignment
        for var in asg.keys():
            # if the variable is not yet assigned, find the number of
            # possible values
            if len(asg[var]) > 1:
                if min_var is None and min_value is None:
                    min_var = var
                    min_value = len(asg[var])
                else:
                    if min_value > len(asg[var]) > 1:
                        min_var = var
                        min_value = len(asg[var])
        # return the variable with the lowest number of legal values
        return min_var

    def order_domain_values(self, var, asg):
        """Returns a list of the domain values of the variable 'var' for
        assignment 'asg'.
        """
        # if the static strategy is selected
        if self.order_domain_values_strategy_static:
            # return the domain of var
            return self.domains[var]
        # if least constraining value is selected
        elif self.order_domain_values_strategy_least_constraint:
            # create a dictionary to keep track of the number of constraints
            # for each value in the domain
            domain_count = {}
            for d in self.domains[var]:
                count = 0
                for c in self.constraints[var]:
                    for values in asg[c]:
                        if d in values:
                            count += 1
                domain_count[d] = count
            # return a list of the values sorted from lowest to highest 
            # occurrences
            return list(dict(sorted(domain_count.items(), 
                key=lambda item: item[1])).keys())

    def is_consistent(self, val, var, asg):
        """Returns true if value 'val' is consistent with the assignment 'asg'.
        """
        # for all the variables that have a constraint with the
        # current variable 'var'
        for var2 in self.constraints[var].keys():
            is_consistent = False
            # check if it exists a pair where 'value' appears for variable 
            # 'var' and 'var2'
            for val2 in asg[var2]:
                if (val, val2) in self.constraints[var][var2]:
                    is_consistent = True
            # if only one pair does not exist return false
            if not is_consistent:
                return False
        # otherwise the value is consistent, and we return true
        return True

    def inference(self, assignment, queue):
        """The function 'AC-3' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'queue'
        is the initial queue of arcs that should be visited.
        """
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
        """Returns all the edges from the neighbors of i (except j) to i.
        """
        edges = []
        for x in self.constraints[i].keys():
            if x != exclude:
                edges.append((x, i))
        # return all the edges from all the neighbors of i (except j) to i
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
        revised = False
        is_satisfied = False
        # for every value x in the domain of i
        for x in asg[i]:
            # find at least one value y in the domain of j that satisfies the
            # constraint
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
