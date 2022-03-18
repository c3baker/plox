import plox_utilities as utilities
from plox_syntax_trees import *

@utilities.singleton
class Resolver:

    def __init__(self):
        self.scopes = []

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if len(self.scopes) == 0:
            return
        self.scopes.pop()

    def resolve(self, syntax):
        syntax.accept(self)

    def declare(self, name):
        if len(self.scopes) == 0:
            return
        self.scopes[-1][name] = False

    def define(self, name):
        if len(self.scopes) == 0:
            return
        self.scopes[-1][name] = True

    def resolve_local(self, expr, name):
        scopes_depth = len(self.scopes)
        for i in range(scopes_depth):
            if name in self.scopes[scopes_depth - i]:
                self.resolve(expr)





