# MTSP-using-sectors
An attempt at solving the Multiple Travelling Salesman Problem.

This project was made for the Pravega Hackathon - 2021.

Please refer to 'Project on MTSP - Pravega.pdf' for details regarding how the code works.

# Running the program

To run the program, first clone this repository to a local directory.

Then run the following command in a terminal opened from this directory to install all required dependencies:

```
pip install -r requirements.txt
```

Finally run general_line_division.py from the same terminal and input the parameters to see the program in action.

```
python general_line_division.py
```

# Implementation

There are three modes to run the program:

1) Manual mode (m): The user has to input the node positions and number of sectors manually.
2) Automatic mode (a): The user has to enter the number of nodes and sectors. The program will
    then automatically generate the nodes with randomised positions.
3) Json input mode (j): The program takes the input from data.json. Final images is stored inside Solution images

# Known issues

1)  The program returns an error for certain node positions and sector numbers.

# Credits

This project was done in collaboration with Agamdeep Singh(https://github.com/jnash10).

python-tsp is a python implementation for solving the Travelling Salesman Problem. https://pypi.org/project/python-tsp/
