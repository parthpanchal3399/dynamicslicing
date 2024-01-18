# dynamicslicing
Program Analysis WS2023 - Course Project on Dynamic Slicing

Uses:
* [DynaPyt](https://github.com/sola-st/DynaPyt) - A Dynamic Analysis Framework for Python
* [LibCST](https://github.com/Instagram/LibCST) - A Concrete Syntax Tree (CST) parser
* [PyTest](https://github.com/pytest-dev/pytest/) - A Python testing framework

## Aim
The goal of this project is to implement dynamic backward slicing for Python. Given a Python program and a slicing criterion( #slicing criterion), the final output of the analysis should keep only the code needed for the slice, e.g., by removing subtrees from the AST that are not part of the slice.

## Applications
* Locating the root cause of a bug
* Reduce code size

## Scope & Limitations
* Implementation is based on intra-procedural analysis, ie. the analysis is limited to the execution inside a function, here slice_me().
* Calls to exec and eval, and with statements are considered out of the scope of this project, and will not appear in the test cases.
* The left-hand side of every assignment (or augmented assignment) is either a variable (foo=), an attribute access (foo.bar=), or an index access (foo[bar]=).
* The analysis should be able to handle complex objects and arrays, but you can assume that any modifications to the object or array causes a dataflow edge to any read of attributes or any index accesses of the object or array.
* When slicing the function, all function arguments remain intact, even if an argument is not needed in the slice.
* There are no definitions of other functions or classes inside the analyzed function.
* print() only to be included in the slice if it's in the #slicing criterion line.


## Installation & Commands

To Install, run:
```console
pip install -r requirements.txt
pip install -e .
```

For only Data-flow: to perform the analysis on a single Python file, run:
```console
python -m dynapyt.instrument.instrument --analysis dynamicslicing.slice_dataflow.SliceDataflow:"../../relative_path_to_input_file/slice_me.py" --files "absolute_path_to_input_file/slice_me.py"

python -m dynapyt.run_analysis --entry "absolute_path_to_input_file/slice_me.py/slice_me.py" --analysis dynamicslicing.slice_dataflow.SliceDataflow:"../../relative_path_to_input_file/slice_me.py"
```

For only Data-flow + Control Flow: to perform the analysis on a single Python file, run:
```console
python -m dynapyt.instrument.instrument --analysis dynamicslicing.slice.Slice:"../../relative_path_to_input_file/slice_me.py" --files "absolute_path_to_input_file/slice_me.py"

python -m dynapyt.run_analysis --entry "absolute_path_to_input_file/slice_me.py/slice_me.py" --analysis dynamicslicing.slice.Slice:"../../relative_path_to_input_file/slice_me.py"
```

Alternatively, you can run:
```console
python dynamicslicing/tests/run_single_test.py
```
This will run tests in milestone2 and milestone3 subfolders

OR 

## Running the test

To run the test cases in the tests directory, you can use the following command:
```console
pytest tests
```
To run the tests for one of the milestones only, run:
```console
pytest tests --only tests/milestoneX
```
where milestoneX can be milestone2 or milestone3.

## Examples
Example 1: Only Data Flow
```console
def slice_me():
  x = 1
  y = 2
  x = x + y
  y += 2
  return y # slicing criterion
slice_me()
```

Output of Analysis:
```console
def slice_me():
  y = 2
  y += 2
  return y # slicing criterion
slice_me()
```


Example 2: Data Flow + Control Flow
```console
def slice_me():
  x = 1
  y = 2
  z = 3
  if x < 4:
    y += 2
  if x > 0:
    z -= 5
  return y # slicing criterion
slice_me()
```

Output of Analysis:
```console
def slice_me():
  x = 1
  y = 2
  if x < 4:
    y += 2
  return y # slicing criterion
slice_me()
```

## Known Issues
1. The analysis is not able to handle Python's match case (introduced in 3.10) due to it being not handled by DynaPyt
2. Object aliases are not handled perfectly. Refer milestone2/test_2/
3. Since modifications to the code are based on ASTs, not all possible types of nodes and all possible combinations are covered yet.
4. 
