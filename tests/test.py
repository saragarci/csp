from csp import csp_solver

import unittest
import copy


class CSPSolverTestSuite(unittest.TestCase):
    def setUp(self):
        # Problem 1
        # Assign a number to each letter with 'diff all' constraint
        self.letters_numbers_assignment = csp_solver.CSP()
        self.letters_numbers_assignment.add_variable('A', [1, 2, 3])
        self.letters_numbers_assignment.add_variable('B', [2])
        self.letters_numbers_assignment.add_variable('C', [3])
        self.letters_numbers_assignment.add_all_different_constraint(
            ['A', 'B', 'C'])

        # Problem 2
        # Assign a color to each number with 'diff all' constraint
        self.numbers_colors_assignment = csp_solver.CSP()
        self.create_assign_colors_to_numbers_csp(
            self.numbers_colors_assignment)

        # Problem 3
        # Map coloring of Australia
        self.map_coloring = csp_solver.CSP()
        self.create_map_coloring_csp(self.map_coloring)

    def create_assign_colors_to_numbers_csp(self, csp):
        csp.add_variable('1', ['R'])
        csp.add_variable('2', ['R', 'G', 'B'])
        csp.add_variable('3', ['R', 'G', 'B'])
        csp.add_variable('4', ['R', 'G', 'B'])
        csp.add_variable('5', ['R', 'B'])
        edges = {
            '1': ['2', '3'], 
            '2': ['1', '3', '4'], 
            '3': ['1', '2', '4', '5'], 
            '4': ['2', '3', '5'], 
            '5': ['3', '4']
        }
        for state, other_states in edges.items():
            for other_state in other_states:
                csp.add_constraint_one_way(state, other_state, 
                                           lambda i, j: i != j)
                csp.add_constraint_one_way(other_state, state,
                                           lambda i, j: i != j)

    def create_map_coloring_csp(self, csp):
        states = ['WA', 'NT', 'Q', 'NSW', 'V', 'SA', 'T']
        edges = {
            'SA': ['WA', 'NT', 'Q', 'NSW', 'V'], 
            'NT': ['WA', 'Q'], 
            'NSW': ['Q', 'V']
        }
        colors = ['red', 'green', 'blue']
        for state in states:
            csp.add_variable(state, colors)
        for state, other_states in edges.items():
            for other_state in other_states:
                csp.add_constraint_one_way(state, other_state, 
                                           lambda i, j: i != j)
                csp.add_constraint_one_way(other_state, state,
                                           lambda i, j: i != j)

    def test_csp_sets_constraints_correctly(self):
        self.assertEqual(self.letters_numbers_assignment.variables, 
            ['A', 'B', 'C']
        )
        self.assertEqual(self.letters_numbers_assignment.domains, {
            'A': [1, 2, 3], 'B': [2], 'C': [3]
        })
        self.assertEqual(self.letters_numbers_assignment.constraints, {
            'A': {'B': [(1, 2), (3, 2)], 'C': [(1, 3), (2, 3)]},
            'B': {'A': [(2, 1), (2, 3)], 'C': [(2, 3)]},
            'C': {'A': [(3, 1), (3, 2)], 'B': [(3, 2)]}
        })

    def test_AC3_algorithm_on_problem_1(self):
        assignment = copy.deepcopy(self.letters_numbers_assignment.domains)
        queue = [('C', 'A'), ('C', 'B'), ('B', 'A'), ('B', 'C'),
            ('A', 'B'), ('A', 'C')]
        self.letters_numbers_assignment.inference(assignment, queue)
        self.assertEqual(queue, [])
        self.assertEqual(assignment, {'A': [1], 'B': [2], 'C': [3]})

    def test_AC3_algorithm_on_problem_2(self):
        assignment = copy.deepcopy(self.numbers_colors_assignment.domains)
        queue = [('1', '3'), ('1', '2'), ('2', '1'), ('2', '3'), ('2', '4'),
                ('4', '2'), ('4', '3'), ('4', '5'), ('3', '1'), ('3', '2'), 
                ('3', '5'), ('3', '4'), ('5', '3'), ('5', '4')]
        self.numbers_colors_assignment.inference(assignment, queue)
        self.assertEqual(queue, [])
        self.assertEqual(assignment, {'1': ['R'], '2': ['G', 'B'], 
            '3': ['G', 'B'], '4': ['R', 'G', 'B'], '5': ['R', 'B']})

    def test_backtracking_search_on_problem_2(self):
        solution = self.numbers_colors_assignment.backtracking_search()
        self.assertEqual(solution, {'1': ['R'], '2': ['B'], '3': ['G'], 
                         '4': ['R'], '5': ['B']})
        self.assertEqual(
            self.numbers_colors_assignment.backtrack_calls_count, 2)
        self.assertEqual(
            self.numbers_colors_assignment.backtrack_returns_failure_count, 0)

    def test_backtracking_search_on_problem_3(self):
        solution = self.map_coloring.backtracking_search()
        self.assertEqual(solution, {'WA': ['green'], 'NT': ['blue'], 
                         'Q': ['green'], 'NSW': ['blue'], 'V': ['green'],
                         'SA': ['red'], 'T': ['red']})
        self.assertEqual(self.map_coloring.backtrack_calls_count, 4)
        self.assertEqual(self.map_coloring.backtrack_returns_failure_count, 0)


if __name__ == "__main__":
    unittest.main()
