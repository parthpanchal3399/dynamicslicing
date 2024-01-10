import os
from typing import List, Callable, Any, Optional, Tuple, Dict, Iterable

from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.utils.nodeLocator import get_node_by_location

from dynamicslicing import utils
import libcst.matchers as m


class Slice(BaseAnalysis):
    def __init__(self, source_path):
        super().__init__()
        self.source_path = source_path

        self.lines_to_keep = []
        self.target_variables = []
        self.slicing_line = -1
        self.class_def_lines = []
        self.datastore = dict()  # to store line numbers, variable reads and writes
        self.aliases = dict()   # to store alias variables with line number
        self.code = ""

    def begin_execution(self) -> None:
        with open(os.path.splitext(self.source_path)[0] + '.py.orig', "r") as file:
            source = file.read()
            self.code = source
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
        # print("write:", location.start_line)
        if location.start_line not in self.class_def_lines:
            if location.start_line in self.datastore:
                if m.matches(node, m.Assign()):
                    if m.matches(node.targets[0].target, m.Attribute()):  # to handle obj access eg. p2.name
                        self.datastore[location.start_line][
                            "write"] = f"{node.targets[0].target.value.value}.{node.targets[0].target.attr.value}"
                    else:
                        if m.matches(node.targets[0].target, m.Subscript()):  # to handle ages[2] = 23 ie subscript as target
                            self.check_overwritten(node)  # check if value is overwritten
                            self.datastore[location.start_line]["write"] = node.targets[0].target.value.value
                        else:  # to handle y = 2
                            self.check_overwritten(node)  # check if value is overwritten
                            self.datastore[location.start_line]["write"] = node.targets[0].target.value
                            if m.matches(node, m.Assign(value=m.Name())) and not m.matches(node, m.Assign(value=m.Call())):  # to handle obj aliases p2 = p1
                                self.aliases[node.targets[0].target.value] = [node.value.value, location.start_line]

                elif m.matches(node, m.AugAssign()):  # to handle y += 2
                    if m.matches(node.target, m.Subscript()):  # to handle ages[-1] += 50
                        self.datastore[location.start_line]["write"] = node.target.value.value
                    else:
                        self.datastore[location.start_line]["write"] = node.target.value
            else:
                if m.matches(node, m.Assign()):
                    if m.matches(node.targets[0].target, m.Attribute()):  # to handle obj access eg. p2.name
                        self.datastore[location.start_line] = {"read": set(),
                                                               "write": f"{node.targets[0].target.value.value}.{node.targets[0].target.attr.value}"}
                    else:
                        if m.matches(node.targets[0].target,
                                     m.Subscript()):  # to handle ages[2] = 23 ie subscript as target
                            self.check_overwritten(node)  # check if value is overwritten
                            self.datastore[location.start_line] = {"read": set(),
                                                                   "write": node.targets[0].target.value.value}
                        else:  # to handle y = 2
                            self.check_overwritten(node)  # check if value is overwritten
                            self.datastore[location.start_line] = {"read": set(), "write": node.targets[0].target.value}

                            # TODO: add obj alias code p2 = p1 ?

                elif m.matches(node, m.AugAssign()):  # to handle y += 2
                    if m.matches(node.target, m.Subscript()):  # to handle ages[-1] += 50
                        self.datastore[location.start_line] = {"read": set(), "write": node.target.value.value}
                    else:
                        self.datastore[location.start_line] = {"read": set(), "write": node.target.value}

    def read(self, dyn_ast: str, iid: int, val: Any) -> Any:
        location = self.iid_to_location(dyn_ast, iid)
        node = get_node_by_location(self._get_ast(dyn_ast)[0], location)
        # print("read:", location.start_line)
        if location.start_line not in self.class_def_lines and not m.matches(node, m.Subscript()):
            if location.start_line in self.datastore:
                if m.matches(node, m.Attribute()):  # to handle object access eg: p.name
                    self.datastore[location.start_line]["read"].add(f"{node.value.value}.{node.attr.value}")
                else:
                    self.datastore[location.start_line]["read"].add(node.value)
            else:
                if m.matches(node, m.Attribute()):  # To handle object access eg: p.name
                    self.datastore[location.start_line] = {"read": {f"{node.value.value}.{node.attr.value}"},
                                                           "write": ""}
                else:
                    self.datastore[location.start_line] = {"read": {node.value}, "write": ""}

    def post_call(self, dyn_ast: str, iid: int, result: Any, call: Callable, pos_args: Tuple, kw_args: Dict, ) -> Any:
        location = self.iid_to_location(dyn_ast, iid)
        node = get_node_by_location(self._get_ast(dyn_ast)[0], location)
        # print(node)
        if location.start_line not in self.class_def_lines:
            if location.start_line in self.datastore:
                if m.matches(node.func, m.Attribute()):  # to handle normal function calls eg. a.append(), obj.funct()
                    if not self.datastore[location.start_line]["write"]:  # put object into write
                        self.datastore[location.start_line]["write"] = node.func.value.value
                    for arg in node.args:  # to handle all positional arguments
                        if m.matches(arg.value, m.Attribute()):  # to handle l.append(p.name)
                            self.datastore[location.start_line]["read"].add(
                                f"{arg.value.value.value}.{arg.value.attr.value}")

                        elif m.matches(arg.value, m.Name()):  # to handle normal args (func(12), func(x))
                            self.datastore[location.start_line]["read"].add(arg.value.value)

            else:
                if m.matches(node.func, m.Attribute()):  # to handle normal function calls eg. a.append(), obj.funct()
                    for arg in node.args:  # to handle all positional arguments
                        if m.matches(arg.value, m.Attribute()):  # to handle l.append(p.name)
                            self.datastore[location.start_line] = {
                                "read": {f"{arg.value.value.value}.{arg.value.attr.value}"},
                                "write": node.func.value.value}
                        elif m.matches(arg.value, m.Name()):  # to handle normal args (func(12), func(x))
                            self.datastore[location.start_line] = {"read": {arg.value.value},
                                                                   "write": node.func.value.value}
                elif m.matches(node.func, m.Name()):
                    if node.func.value == "print":  # to handle just print("string")
                        if m.matches(node.args[0].value,
                                     m.SimpleString()):  # TODO: add logic to handle multiple string args
                            self.datastore[location.start_line] = {"read": set(), "write": ''}

    def enter_if(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        location = self.iid_to_location(dyn_ast, iid)
        node = get_node_by_location(self._get_ast(dyn_ast)[0], location)
        # print("entering if:", location.start_line)
        if cond_value:
            self.datastore[location.start_line]["is_cond"] = True
            count = 0
            if m.matches(node.orelse, m.Else()):
                count = str(node.orelse).count("SimpleStatementLine")
            else:
                count = str(node.body).count("SimpleStatementLine")
            self.datastore[location.start_line]["body"] = list(
                range(location.start_line + 1, location.start_line + 1 + count))
        else:
            if m.matches(node.orelse, m.Else()):
                count = str(node.orelse).count("SimpleStatementLine")
                if location.end_line - 1 not in self.datastore:
                    self.datastore[location.end_line - 1] = {"read": {node.test.left.value}, "write": '',
                                                             "is_cond": True, "body": list(
                            range(location.end_line, location.end_line + count))}
                    # TODO: RHS of comparator should also be in read[]

    def enter_for(self, dyn_ast: str, iid: int, next_value: Any, iterable: Iterable) -> Optional[Any]:
        location = self.iid_to_location(dyn_ast, iid)
        node = get_node_by_location(self._get_ast(dyn_ast)[0], location)
        # print("entering for:", location.start_line)
        # print(node)
        self.datastore[location.start_line]["is_cond"] = True
        self.datastore[location.start_line]["body"] = list(range(location.start_line + 1, location.end_line + 1))

    def enter_while(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        location = self.iid_to_location(dyn_ast, iid)
        node = get_node_by_location(self._get_ast(dyn_ast)[0], location)
        if cond_value:
            self.datastore[location.start_line]["is_cond"] = True
            self.datastore[location.start_line]["body"] = list(range(location.start_line + 1, location.end_line + 1))
            for counter in list(self.datastore[location.start_line]["read"]):
                for i, ss in enumerate(m.findall(node, m.SimpleStatementLine())):
                    if m.matches(ss.body[0], m.Assign()):
                        pass  # TODO: add logic to handle assign to counter variable
                    elif m.matches(ss.body[0], m.AugAssign()):
                        if ss.body[0].target.value == counter:
                            counter_line = utils.get_location_from_node(self.code, ss)
                            self.datastore[counter_line] = {"read": set(), "write": counter}

    def end_execution(self) -> None:
        with open(os.path.splitext(self.source_path)[0] + '.py.orig', "r") as file:
            source = file.read()

        self.datastore = dict(sorted(self.datastore.items(), reverse=True))
        self.lines_to_keep = self.lines_to_keep + self.class_def_lines
        # print(self.datastore)
        # print(self.aliases)
        # print(self.target_variables)

        for line, val in self.datastore.items():
            # print(self.target_variables)
            # print(line, val)
            if line <= self.slicing_line:
                # DATA-FLOW
                if (not val.get("is_cond")
                        and val["write"] in self.target_variables
                        or ("." in val["write"] and val["write"][:val["write"].index(".")] in self.target_variables)):
                    self.lines_to_keep.append(line)
                    if len(val["read"]) > 0 and len([x for x in val["read"] if x not in self.target_variables]) > 0:
                        self.target_variables.extend(val["read"])

                # DATA-FLOW : for aliases
                if (not val.get("is_cond")
                        and ("." in val["write"] and val["write"][:val["write"].index(".")] in list(self.aliases.keys()))
                        or (val["write"] in list(self.aliases.keys()) and any(val["write"]+"." in r for r in val["read"]))):
                    left = val["write"][:val["write"].index(".")] if "." in val["write"] else val["write"]
                    right = self.aliases[left][0]
                    loc = self.aliases[left][1]
                    if right in self.target_variables:
                        self.lines_to_keep.append(line)
                        self.lines_to_keep.append(loc)
                        self.target_variables.extend(val["read"])

                # CONTROL-FLOW
                if val.get("is_cond") == True:
                    for body_line in val["body"]:
                        if self.datastore.get(body_line) and body_line <= self.slicing_line:
                            if self.datastore.get(body_line)["write"] in self.target_variables or ("." in self.datastore.get(body_line)["write"] and self.datastore.get(body_line)["write"][:self.datastore.get(body_line)["write"].index(".")] in self.target_variables):
                                self.lines_to_keep.append(body_line)
                                self.lines_to_keep.append(line)
                                if len(val["read"]) > 0 and len([x for x in val["read"] if x not in self.target_variables]) > 0:
                                    self.target_variables.extend(val["read"])

                        if body_line in self.lines_to_keep:  # if the body of conditional is to be kept, then the conditional line should also be kept
                            self.lines_to_keep.append(line)
                            self.target_variables.extend(self.datastore[line]["read"])

                        if line in self.lines_to_keep:  # if the condition is to be kept, the variables in the condition are target vars
                            if self.datastore.get(body_line):
                                if self.datastore.get(body_line)["write"] in list(val["read"]):
                                    self.lines_to_keep.append(body_line)


        sliced = utils.remove_lines(source, self.lines_to_keep)
        with open(os.path.dirname(self.source_path) + '/sliced.py', "w") as updated_file:
            updated_file.write(sliced)

    def check_overwritten(self, node):
        if m.matches(node, m.Assign(value=m.Integer() | m.Float() | m.Imaginary() | m.SimpleString() | m.FormattedString() | m.ConcatenatedString())):
            for line, val in list(self.datastore.items()):
                if node.targets[0].target.value == val["write"]:
                    self.datastore.pop(line, None)  # value of the variable is overwritten, remove from datastore
