import ast

class NestingDepthVisitor(ast.NodeVisitor):
    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0

    def _visit_nested(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_If(self, node): self._visit_nested(node)
    def visit_For(self, node): self._visit_nested(node)
    def visit_While(self, node): self._visit_nested(node)
    def visit_Try(self, node): self._visit_nested(node)
    def visit_With(self, node): self._visit_nested(node)