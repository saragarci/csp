# Solving Constraint Satisfaction Problems

This application uses Constraint Satisfaction Problems (CSPs) by implementing a CSP solver and using it to solve Sudoku boards. Specifically it uses *backtracking search* and the arc-consistency algorithm *AC-3*.

The code reads Sudoku boards from text files and represents them as CSPs. Next, the CSP solver prints out the solution to these.

## Usage

### Dependencies

* Python3

### Running the program

To run the program you will need to specify the level of sudoku board: `easy`, `medium`, `hard` or `veryhard`:
```
$ python3 csp/main.py --level hard
```

To run the tests:
```
python3 -m unittest tests/test.py
```

## Credits

### Used resources

* Russell, Stuart J.; Norvig, Peter 2021, *Artificial Intelligence: A Modern Approach* (4th Edition, Global Edition) Pearson Education.

### Contributors

* [Sara Garci](s@saragarci.com)

## License

© Copyright 2021 by Sara Garci. All rights reserved.
