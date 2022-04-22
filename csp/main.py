import argparse
import csp_solver
import helpers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--level",
        help="specify sudoku level: easy, medium, hard or veryhard")
    args = parser.parse_args()
    if not args.level:
        print("Sudoku board level missing")
    else:
        csp = csp_solver.CSP()
        helpers.backtracking_search_sudoku(f"boards/{args.level}.txt", csp)


if __name__ == "__main__":
    main()
