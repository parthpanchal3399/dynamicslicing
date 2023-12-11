from typing import List, Callable, Any, Tuple, Dict
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.IIDs import IIDs
from dynapyt.utils.nodeLocator import get_node_by_location

from dynamicslicing import utils
import os
import libcst.matchers as m

class SliceDataflow(BaseAnalysis):

    def __init__(self, source_path):
        super().__init__()
        self.source_path = source_path
        with open(source_path, "r") as file:
            source = file.read()
        iid_object = IIDs(source_path)

        self.lines_to_keep = []
        self.target_variables = []
        self.slicing_line = -1
        self.class_def_lines = []
        self.datastore = dict()  # to store line numbers, variable reads and writes

    def begin_execution(self) -> None:
        with open(os.path.splitext(self.source_path)[0] + '.py.orig', "r") as file:
            source = file.read()
        if "DYNAPYT: DO NOT INSTRUMENT" not in source:  # only on un-Instrumented file
            return_vals = utils.get_slice_line(source)
            self.lines_to_keep = return_vals[0]
            self.target_variables = return_vals[1]
            self.slicing_line = return_vals[2]
            self.class_def_lines = return_vals[3]
        # print(self.lines_to_keep)
        # print(self.target_variables)
        # print(self.slicing_line)
        # print(self.class_def_lines)

    def write(self, dyn_ast: str, iid: int, old_vals: List[Callable], new_val: Any) -> Any:
        location = self.iid_to_location(dyn_ast, iid)
        node = get_node_by_location(self._get_ast(dyn_ast)[0], location)
        if location.start_line <= self.slicing_line and location.start_line not in self.class_def_lines:
            if location.start_line in self.datastore:
                if m.matches(node, m.Assign()):
                    if m.matches(node.targets[0].target, m.Attribute()):  # to handle obj access eg. p2.name
                        self.datastore[location.start_line][
                            "write"] = f"{node.targets[0].target.value.value}.{node.targets[0].target.attr.value}"
                    else:
                        if m.matches(node.targets[0].target,
                                     m.Subscript()):  # to handle ages[2] = 23 ie subscript as target
                            self.datastore[location.start_line]["write"] = node.targets[0].target.value.value
                        else:  # to handle y = 2
                            self.datastore[location.start_line]["write"] = node.targets[0].target.value
                elif m.matches(node, m.AugAssign()):  # to handle y += 2
                    self.datastore[location.start_line]["write"] = node.target.value
            else:
                if m.matches(node, m.Assign()):
                    if m.matches(node.targets[0].target, m.Attribute()):  # to handle obj access eg. p2.name
                        self.datastore[location.start_line] = {"read": [],
                                                               "write": f"{node.targets[0].target.value.value}.{node.targets[0].target.attr.value}"}
                    else:
                        if m.matches(node.targets[0].target,
                                     m.Subscript()):  # to handle ages[2] = 23 ie subscript as target
                            self.datastore[location.start_line] = {"read": [],
                                                                   "write": node.targets[0].target.value.value}
                        else:  # to handle y = 2
                            self.datastore[location.start_line] = {"read": [], "write": node.targets[0].target.value}
                elif m.matches(node, m.AugAssign()):  # to handle y += 2
                    self.datastore[location.start_line] = {"read": [], "write": node.target.value}

    def read(self, dyn_ast: str, iid: int, val: Any) -> Any:
        location = self.iid_to_location(dyn_ast, iid)
        node = get_node_by_location(self._get_ast(dyn_ast)[0], location)
        if location.start_line <= self.slicing_line and location.start_line not in self.class_def_lines and not m.matches(node, m.Subscript()):
            if location.start_line in self.datastore:
                if m.matches(node, m.Attribute()):  # to handle object access eg: p.name
                    self.datastore[location.start_line]["read"].append(f"{node.value.value}.{node.attr.value}")
                else:
                    self.datastore[location.start_line]["read"].append(node.value)
            else:
                if m.matches(node, m.Attribute()):  # To handle object access eg: p.name
                    self.datastore[location.start_line] = {"read": [f"{node.value.value}.{node.attr.value}"],
                                                           "write": ""}
                else:
                    self.datastore[location.start_line] = {"read": [node.value], "write": ""}

    def post_call(self, dyn_ast: str, iid: int, result: Any, call: Callable, pos_args: Tuple, kw_args: Dict, ) -> Any:
        location = self.iid_to_location(dyn_ast, iid)
        node = get_node_by_location(self._get_ast(dyn_ast)[0], location)
        if location.start_line <= self.slicing_line and location.start_line not in self.class_def_lines:
            if location.start_line in self.datastore:
                if m.matches(node.func, m.Attribute()):  # to handle normal function calls eg. a.append(), obj.funct()
                    for arg in node.args:   # to handle all positional arguments
                        if m.matches(arg.value, m.Attribute()):   # to handle l.append(p.name)
                            self.datastore[location.start_line]["read"].append(f"{arg.value.value.value}.{arg.value.attr.value}")
                            if not self.datastore[location.start_line]["write"]:
                                self.datastore[location.start_line]["write"] = node.func.value.value
                        elif m.matches(arg.value, m.Name()):  # to handle normal args (func(12), func(x))
                            self.datastore[location.start_line]["read"].append(arg.value.value)
                            if not self.datastore[location.start_line]["write"]:
                                self.datastore[location.start_line]["write"] = node.func.value.value
            else:
                if m.matches(node.func, m.Attribute()):  # to handle normal function calls eg. a.append(), obj.funct()
                    for arg in node.args:  # to handle all positional arguments
                        if m.matches(arg.value, m.Attribute()):  # to handle l.append(p.name)
                            self.datastore[location.start_line] = {"read": f"{arg.value.value.value}.{arg.value.attr.value}", "write": node.func.value.value}
                        elif m.matches(arg.value, m.Name()):  # to handle normal args (func(12), func(x))
                            self.datastore[location.start_line] = {"read": arg.value.value, "write": node.func.value.value}

    def end_execution(self) -> None:
        with open(os.path.splitext(self.source_path)[0] + '.py.orig', "r") as file:
            source = file.read()

        self.datastore = dict(sorted(self.datastore.items(), reverse=True))
        self.lines_to_keep = self.lines_to_keep + self.class_def_lines
        # print(self.datastore)

        for line, val in self.datastore.items():
            # print(self.target_variables)
            # print(line, val)
            # TODO: Handle overwrite of variables
            if val["write"] in self.target_variables or (
                    "." in val["write"] and val["write"][:val["write"].index(".")] in self.target_variables):
                self.lines_to_keep.append(line)
                if len(val["read"]) > 0 and len([x for x in val["read"] if x not in self.target_variables]) > 0:
                    self.target_variables.extend(val["read"])

        sliced = utils.remove_lines(source, self.lines_to_keep)
        with open(os.path.dirname(self.source_path) + '\\sliced.py', "w") as updated_file:
            updated_file.write(sliced)
