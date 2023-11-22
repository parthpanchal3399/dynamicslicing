from typing import List, Union
import libcst as cst
from libcst import CSTTransformer, Comment
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

    def leave_If(self, original_node: If, updated_node: If) -> BaseStatement | FlattenSentinel[BaseStatement] | RemovalSentinel:
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
    #print(syntax_tree)
    wrapper = cst.metadata.MetadataWrapper(syntax_tree)
    code_modifier = RemoveLinesTransformer(lines_to_keep)
    new_syntax_tree = wrapper.visit(code_modifier)
    # print(new_syntax_tree.code)
    return new_syntax_tree.code
