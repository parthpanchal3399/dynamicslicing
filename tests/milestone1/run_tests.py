import json
import libcst as cst
from os import walk
from os.path import join
from os.path import realpath, dirname, sep

from dynamicslicing.utils import remove_lines
from dynamicslicing.utils import negate_odd_ifs


def correct_output(expected: str, actual: str) -> bool:
    if actual == expected or actual == expected + "\n":
        return True
    expected_lines = expected.split("\n")
    actual_lines = actual.split("\n")
    expected_trimmed = "\n".join([l for l in expected_lines if l.strip() != ""])
    actual_trimmed = "\n".join([l for l in actual_lines if l.strip() != ""])
    expected_ast = cst.parse_module(expected_trimmed)
    actual_ast = cst.parse_module(actual_trimmed)
    return expected_ast.deep_equals(actual_ast)


current_dir = dirname(realpath(__file__))
start_dir = current_dir

for root, dirs, files in walk(start_dir):
    if all([f in files for f in ["program.py", "expected.py", "lines.py"]]):
        program_file = join(root, "program.py")
        expected_file = join(root, "expected.py")
        lines = join(root, "lines.py")
        with open(program_file, "r") as file:
            program = file.read()

        with open(lines, "r") as file:
            lines = json.loads(file.read())

        actual = remove_lines(program, list(lines))

        # actual = negate_odd_ifs(program)

        with open(expected_file, "r") as file:
            expected = file.read()

        rel_dir = root[len(current_dir) + len(sep):]
        if not correct_output(expected, actual):
            print(
                f"Output of {rel_dir} does not match expected output.\n--> Expected:\n{expected}\n--> Actual:\n{actual}")
        else:
            print(f"{rel_dir} Passed!!")
