from typing import List, Union
import libcst as cst
from libcst import CSTTransformer, Comment, CSTVisitor, FunctionDef, Call, ClassDef
from libcst._flatten_sentinel import FlattenSentinel
from libcst._nodes.statement import BaseStatement, If, SimpleStatementLine
from libcst._removal_sentinel import RemovalSentinel
from libcst.metadata import (
    ParentNodeProvider,
    PositionProvider,
)
import libcst.matchers as m


class OddIfNegation(m.MatcherDecoratableTransformer):
    """
    Negate the test of every if statement on an odd line.
    """
    METADATA_DEPENDENCIES = (
        ParentNodeProvider,
        PositionProvider,
    )

    def leave_If(self, original_node: If, updated_node: If) -> BaseStatement | FlattenSentinel[
        BaseStatement] | RemovalSentinel:
        location = self.get_metadata(PositionProvider, original_node)
        if location.start.line % 2 == 0:
            return updated_node
        negated_test = cst.UnaryOperation(
            operator=cst.Not(),
            expression=updated_node.test,
        )
        return updated_node.with_changes(
            test=negated_test,
        )


class MyVisitor(CSTVisitor):
    """
    Visitor Class
    """

    def __init__(self):
        super().__init__()
        self.return_vals = [
            [],  # lines_to_keep
            [],  # target_variables
            -1,  # slicing criteria line number
            []  # class definition lines
        ]

    METADATA_DEPENDENCIES = (
        ParentNodeProvider,
        PositionProvider,
    )

    def leave_Comment(self, original_node: "Comment") -> None:
        if original_node.value == "# slicing criterion":
            # extract slicing criterion line number
            self.return_vals[0].append(self.get_metadata(PositionProvider, original_node).start.line)
            self.return_vals[2] = self.get_metadata(PositionProvider, original_node).start.line

            # extract target variable in the slicing criterion
            trailing_whitespace = self.get_metadata(ParentNodeProvider, original_node)
            next_parent = self.get_metadata(ParentNodeProvider, trailing_whitespace).body[0]
            if m.matches(next_parent, m.Return()):
                if m.matches(next_parent.value, m.Name()):  # to handle return x
                    self.return_vals[1].append(next_parent.value.value)
                elif m.matches(next_parent.value, m.Attribute()):  # to handle return p.name
                    self.return_vals[1].append(next_parent.value.value.value)
                    self.return_vals[1].append(f"{next_parent.value.value.value}.{next_parent.value.attr.value}")
                elif m.matches(next_parent.value, m.BinaryOperation()):  # to handle return x + y
                    self.return_vals[1].append(next_parent.value.left.value)
                    self.return_vals[1].append(next_parent.value.right.value)
            elif m.matches(next_parent, m.Assign()):
                if m.matches(next_parent, m.Assign(value=m.BinaryOperation())):     # to handle x + y
                    self.return_vals[1].append(next_parent.value.left.value)
                    self.return_vals[1].append(next_parent.value.right.value)
                elif m.matches(next_parent.targets[0], m.AssignTarget()):
                    if m.matches(next_parent.targets[0].target, m.Subscript()):   # to handle a[2] = 100
                        self.return_vals[1].append(next_parent.targets[0].target.value.value)
                    else:   # to handle a = Hello()
                        self.return_vals[1].append(next_parent.targets[0].target.value)
            elif m.matches(next_parent, m.Expr(value=m.Call())):    # to handle function calls
                if m.matches(next_parent.value, m.Call(func=m.Name())):     # to handle print(x)
                    for arg in next_parent.value.args:
                        self.return_vals[1].append(arg.value.value)
                elif m.matches(next_parent.value, m.Call(func=m.Attribute())):    # to handle p1.funct()
                    self.return_vals[1].append(next_parent.value.func.value.value)

            # TODO: Add more cases of slicing criterion

    def leave_FunctionDef(self, original_node: "FunctionDef") -> None:
        if original_node.name.value == "slice_me":
            self.return_vals[0].append(self.get_metadata(PositionProvider, original_node).start.line)
        else: # to handle any other function defs (We keep them as it is)
            self.return_vals[0].extend(range(self.get_metadata(PositionProvider, original_node).start.line, self.get_metadata(PositionProvider, original_node).end.line + 1))

    def leave_Call_func(self, node: "Call") -> None:
        if node.func.value == "slice_me":
            self.return_vals[0].append(self.get_metadata(PositionProvider, node).start.line)

    def visit_ClassDef(self, node: "ClassDef") -> None:
        self.return_vals[3].extend(range(self.get_metadata(PositionProvider, node).start.line,
                                         self.get_metadata(PositionProvider, node).end.line + 1))


class RemoveLinesTransformer(CSTTransformer):
    """
        Remove lines from source code
    """

    def __init__(self, lines_to_keep):
        super().__init__()
        self.lines_to_keep = lines_to_keep

    METADATA_DEPENDENCIES = (
        ParentNodeProvider,
        PositionProvider,
    )

    def leave_If(
            self, original_node: "If", updated_node: "If"
    ) -> Union["BaseStatement", FlattenSentinel["BaseStatement"], RemovalSentinel]:
        location = self.get_metadata(PositionProvider, original_node)
        if location.start.line not in self.lines_to_keep:
            updated_node = cst.RemoveFromParent()
        return updated_node

    def leave_SimpleStatementLine(
            self, original_node: "SimpleStatementLine", updated_node: "SimpleStatementLine"
    ) -> Union["BaseStatement", FlattenSentinel["BaseStatement"], RemovalSentinel]:
        location = self.get_metadata(PositionProvider, original_node)
        if location.start.line not in self.lines_to_keep:
            updated_node = cst.RemoveFromParent()
        return updated_node

    def leave_Comment(
            self, original_node: "Comment", updated_node: "Comment"
    ) -> "Comment":
        location = self.get_metadata(PositionProvider, original_node)
        if location.start.line not in self.lines_to_keep:
            updated_node = cst.RemoveFromParent()
        return updated_node


def negate_odd_ifs(code: str) -> str:
    syntax_tree = cst.parse_module(code)
    wrapper = cst.metadata.MetadataWrapper(syntax_tree)
    code_modifier = OddIfNegation()
    new_syntax_tree = wrapper.visit(code_modifier)
    return new_syntax_tree.code


def remove_lines(code: str, lines_to_keep: List[int]) -> str:
    syntax_tree = cst.parse_module(code)
    print("Original Code: ")
    print(syntax_tree.code)
    print("")
    wrapper = cst.metadata.MetadataWrapper(syntax_tree)
    code_modifier = RemoveLinesTransformer(lines_to_keep)
    new_syntax_tree = wrapper.visit(code_modifier)
    print(f"Lines to Keep = {lines_to_keep} | New Code: ")
    print(new_syntax_tree.code)
    print("-------------------------------------------------------------")
    return new_syntax_tree.code


def get_slice_line(code: str) -> List:
    """
        Function to extract line number of the slicing criterion,
        function def and function call of slice_me()
    """
    syntax_tree = cst.parse_module(code)
    # print(syntax_tree)
    wrapper = cst.metadata.MetadataWrapper(syntax_tree)
    code_visitor = MyVisitor()
    t = wrapper.visit(code_visitor)
    return code_visitor.return_vals
