import os


def backtracking_search_sudoku(file, csp):
    """Perform backtracking search on the sudoku board matching 'file'
    and print the board if a solution is found.
    """
    print(file)
    csp = create_sudoku_csp(file, csp)
    solution = csp.backtracking_search()
    if solution is not None:
        print_sudoku_solution(solution)
    print("BACKTRACK being called count: ", csp.backtrack_calls_count)
    print("BACKTRACK returns failure count: ",
          csp.backtrack_returns_failure_count)


def create_sudoku_csp(filename, csp):
    """Instantiate a CSP representing the Sudoku board found in the text
    file named 'filename' in the boards directory.
    """
    path = os.path.realpath(__file__)
    dir = os.path.dirname(path)
    dir.join("boards")
    os.chdir(dir)
    board = list(map(lambda x: x.strip(), open(filename, 'r')))
    for row in range(9):
        for col in range(9):
            if board[row][col] == '0':
                csp.add_variable('%d-%d' % (row, col),
                                 list(map(str, range(1, 10))))
            else:
                csp.add_variable('%d-%d' % (row, col), [board[row][col]])

    for row in range(9):
        csp.add_all_different_constraint(
            ['%d-%d' % (row, col) for col in range(9)])
    for col in range(9):
        csp.add_all_different_constraint(
            ['%d-%d' % (row, col) for row in range(9)])
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
