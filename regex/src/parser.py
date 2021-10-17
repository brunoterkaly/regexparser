from io import StringIO
import copy
import json
import pprint
import sys
import re
import os

from subprocess import Popen, PIPE, STDOUT
from typing_extensions import Literal

"""

<expr> ::= <term>
	| <term>'|'<expr>
<term> ::= <factor>
	| <factor><term>
<factor> ::= <atom>
	| <atom><meta-char>
<atom> ::= <char>
	| '('<expr>')'
<char> ::= <any-char-except-meta>
	| '\'<any-char>
<meta-char> ::= '?' | '*' | '+'
"""

mystack = None

# ===============================================================
# https://deniskyashif.com/2020/08/17/parsing-regex-with-recursive-descent/
# ===============================================================
class MyStack:
    def __init__(self):
        self.container = []
        mystack = self.container

    def isEmpty(self):
        return self.size() == 0

    def isExpr(self):
        stack_len = len(self.container)
        return self.container[stack_len - 1]._label == "expr"

    def isAtom(self):
        stack_len = len(self.container)
        return self.container[stack_len - 1]._label == "atom"

    def push(self, item):
        self.container.append(
            item
        )  # appending to the *container*, not the instance itself.

    def pop(self):
        element = (
            self.container.pop()
        )  # pop from the container, this was fixed from the old version which was wrong
        # self.container[len(self.container)-1] = None
        return element

    def pop2(self, pop2to):
        start = pop2to
        element = self.container.pop()
        while start != element._label:
            element = self.container.pop()
        return element

    def peek(self):
        if self.isEmpty():
            raise Exception("Stack empty!")
        return self.container[-1]  # View element at top of the stack

    def size(self):
        return len(self.container)  # length of the container

    def show(self):
        for s in reversed(self.container):
            print(s._label)


class RegExNode:
    def __init__(self, label, children=[]):
        self._label = label
        self._children = children


class TreeNode:
    def __init__(self, label, children):
        self._label = label
        self._children = children
        self._pattern = ""
        self._pos = 0
        self._stack = MyStack()

    def isStackEmpty(self):
        return len(self._stack) == 0

    # ===========================================================
    # Text Functions
    # ===========================================================
    def peek(self):
        return self._pattern[self._pos]

    def hasMoreChars(self):
        return self._pos < len(self._pattern)

    def isMetaChar(self, ch):
        return ch == "*" or ch == "+" or ch == "?"

    def match(self, ch):
        if self.peek() != ch:
            raise ("Unexpected symbol = ".format(ch))
        self._pos += 1

    def next(self):
        ch = self.peek()
        self.match(ch)
        return ch

    def connect_stack(self):
        topoffset = len(self._stack.container) - 1
        topnode = self._stack.container[topoffset]
        trgoffset = topoffset - 1
        trgnode = self._stack.container[trgoffset]
        copytopnode = copy.deepcopy(topnode)
        copytrgnode = copy.deepcopy(trgnode)
        trgnode = copytrgnode
        trgnode._children.append(copytopnode)
        self._stack.container[trgoffset] = trgnode

    # New Grammar Functions
    # ===========================================================
    def toParseTree2(self, regex, regex_node):
        self._pattern = regex
        self._pos = 0
        # self._stack.push(regex_node)
        self.expr4()
        self.expr3()
        self.expr2()
        # self.connect_stack()
        # self._stack.pop()

    """
	<expr> ::= <term>
		| <term>'|'<expr>
	"""

    def connect_children(self, number_children):
        for i in range(0, number_children):
            self.connect_stack()
            self._stack.pop()

    def push1(self):
        node = RegExNode("expr")
        self._stack.push(node)

    def push4(self):
        node = RegExNode("expr")
        self._stack.push(node)
        node = RegExNode("term")
        self._stack.push(node)
        node = RegExNode("factor")
        self._stack.push(node)
        node = RegExNode("atom")
        self._stack.push(node)

    def expr4(self):
        # The code reflects teh grammar
        try:
            while True:
                while self.hasMoreChars():
                    if self.peek() == "(":
                        node = RegExNode("expr")
                        self._stack.push(node)
                        node = RegExNode("term")
                        self._stack.push(node)
                        node = RegExNode("factor")
                        self._stack.push(node)
                        node = RegExNode("atom")
                        self._stack.push(node)
                        literal = RegExNode(self.next(), None)
                        self._stack.push(literal)
                        self.connect_children(1)
                        while self.hasMoreChars():
                            if self.peek().isalnum():
                                node = RegExNode("expr")
                                self._stack.push(node)
                                node = RegExNode("term")
                                self._stack.push(node)
                                node = RegExNode("factor")
                                self._stack.push(node)
                                node = RegExNode("atom")
                                literal = RegExNode(self.next(), None)
                                self._stack.push(literal)
                                self.connect_children(3)
                            if self.peek() == "|":
                                literal = RegExNode(self.next(), None)
                                self._stack.push(literal)
                                self.connect_children(1)
                            if self.peek() == ")":
                                self.connect_children(1)
                                break

        except Exception as ex:
            pass

    def expr3(self):
        # The code reflects teh grammar
        try:
            while self.hasMoreChars():
                # if lparen, then expr -> char
                if self.peek() == "(":
                    node = RegExNode("expr")
                    self._stack.push(node)
                    node = RegExNode("term")
                    self._stack.push(node)
                    node = RegExNode("factor")
                    self._stack.push(node)
                    node = RegExNode("atom")
                    self._stack.push(node)
                    ch = self.lparen()  # autoconnect
                    # At this level I can expect expr or )

                if self.peek() == ")":
                    self.connect_children(1)
                    ch = self.rparen()  # autoconnect
                    self.connect_children(1)
                    continue
                # if alnum, then expr -> char
                if self.peek().isalnum():
                    self.push4()
                    ch = self.char2()
                    self.connect_children(3)
                    continue
                # if |, then add to expr
                if self.peek() == "|":
                    # self.push1()
                    self.pipe()
                    self.connect_children(1)
                    continue

        except Exception as ex:
            pass

    def expr2(self):
        # The code reflects teh grammar
        expr = RegExNode("expr")
        self._stack.push(expr)

        # expressions need atleast one term. a term is
        self.term2()
        if self.hasMoreChars() and self.peek() == "|":
            self.pipe()
            expression = self.expr2()
        self.connect_stack()
        self._stack.pop()
        pass

    def term2(self):
        term = RegExNode("term")
        self._stack.push(term)
        factor = self.factor2()
        if self.hasMoreChars() and self.peek() != "|":
            # Recurse 1
            self.term2()

        self.connect_stack()
        self._stack.pop()
        pass

    def factor2(self):
        factor = RegExNode("factor")
        self._stack.push(factor)
        atom = self.atom2()
        if self.hasMoreChars() and self.isMetaChar(self.peek()):
            atom = self.factor2()

        self.connect_stack()  # pop 'atom' off stack
        self._stack.pop()
        pass

    def atom2(self):
        # Push
        if self.peek().isalnum():
            atom = RegExNode("atom")
            self._stack.push(atom)
            ch = self.char2()
            self.connect_stack()
            self._stack.pop()
            return

        # About to return but first add meta and add to parent from here
        # When I return, atom should NOT be on stack

        if self.isMetaChar(self.peek()):
            atom = RegExNode("atom")
            self._stack.push(atom)
            ch = self.meta2()
            self.connect_stack()
            self._stack.pop()
            return

        if self.peek() == "(":
            atom = RegExNode("atom")
            self._stack.push(atom)
            ch = self.lparen()
            expression = self.expr2()
            self.connect_stack()
            self._stack.pop()
            return

        if self.peek() == ")":
            atom = RegExNode("atom")
            self._stack.push(atom)
            ch = self.rparen()
            self.connect_stack()
            self._stack.pop()
            return

        if self.peek() == "|":
            atom = RegExNode("atom")
            self._stack.push(atom)
            ch = self.pipe()
            self.connect_stack()
            self._stack.pop()
            return

    def pipe(self):

        literal = RegExNode(self.next(), None)
        self._stack.push(literal)
        self.connect_stack()
        self._stack.pop()
        pass

    def meta2(self):

        meta = RegExNode("Meta")
        self._stack.push(meta)
        literal = self.literal()
        self.connect_stack()
        self._stack.pop()
        pass

    def lparen(self):

        literal = RegExNode(self.next(), None)
        self._stack.push(literal)
        self.connect_stack()
        self._stack.pop()
        pass

    def rparen(self):
        literal = RegExNode(self.next(), None)
        self._stack.push(literal)
        self.connect_stack()
        self._stack.pop()
        pass

    def char2(self):
        if self.isMetaChar(self.peek()):
            raise ("Unexpected symbol = ".format(self.peek()))
        if self.peek() == "\\":
            self.match("\\")
            pass

        char = RegExNode("Char")
        self._stack.push(char)
        literal = self.literal()
        self.connect_stack()
        self._stack.pop()
        pass

    def literal(self):
        literal = RegExNode(self.next(), None)
        self._stack.push(literal)
        # Connect and pop before leaving
        self.connect_stack()
        self._stack.pop()
        pass

    # ===========================================================
    # Old Grammar Functions
    # ===========================================================
    def toParseTree(self, regex):
        self._pattern = regex
        self._pos = 0
        return self.expr()

    def expr(self):
        term = self.term()
        if self.hasMoreChars() and self.peek() == "|":
            self.match("|")
            # Recurse
            expression = self.expr()
            return TreeNode("Expr", [term, TreeNode("Or", "|"), expression])
        return TreeNode("Expr", [term])

    def term(self):
        factor = self.factor()
        if self.hasMoreChars() and self.peek() != "|":
            # Recurse 1
            term = self.term()
            return TreeNode("Term", [factor, term])
        return TreeNode("Term", [factor])

    def factor(self):
        atom = self.atom()
        if self.hasMoreChars() and self.isMetaChar(self.peek()):
            meta = self.next()
            return TreeNode("Factor", [atom, TreeNode(meta, None)])
        return TreeNode("Factor", [atom])

    def atom(self):
        if self.peek() == "(":
            self.match("(")
            # Recurse 3
            expression = self.expr()
            self.match(")")
            return TreeNode(
                "Atom", [TreeNode("lparen", "("), expression, TreeNode("rparen", ")")]
            )
        ch = self.char()
        return TreeNode("Atom", [ch])

    def char(self):
        if self.isMetaChar(self.peek()):
            raise ("Unexpected symbol = ".format(self.peek()))
        if self.peek() == "\\":
            self.match("\\")
            return TreeNode(
                "Char", [TreeNode("slash", "\\"), TreeNode("next", self.next())]
            )

        return TreeNode("Char", [TreeNode(self.next(), None)])

    def any_char_except_meta(self):
        pass


if __name__ == "__main__":
    expr = "a+b?"
    expr = "(a|b)*c"

    # tree_node2 = TreeNode("Begin", [])
    # final_tree = tree_node2.toParseTree(expr)

    tree_node = TreeNode("Begin", [])
    regex_node = RegExNode("expr", [])
    final_tree2 = tree_node.toParseTree2(expr, regex_node)
    print(final_tree2)
    # Old code

"""
				if self.hasMoreChars() and self.peek() == "|":
					literal = RegExNode(self.next(), None)
					self._stack.push(literal)
					self.connect_stack()
					self._stack.pop()
				term = RegExNode("term")
				self._stack.push(term)
				if self.hasMoreChars() and self.peek() != "|":
					factor = RegExNode("factor")
					self._stack.push(factor)
					if self.peek() == "(":
						atom = RegExNode("atom")
						self._stack.push(atom)
						ch = self.lparen()
						continue
					if self.peek() == ")":
						literal = RegExNode(self.next(), None)
						self._stack.push(literal)
						self.connect_stack()
						self._stack.pop()
						break
					if self.peek().isalnum():
						atom = RegExNode("atom")
						self._stack.push(atom)
						char = RegExNode("Char")
						self._stack.push(char)
						literal = RegExNode(self.next(), None)
						self._stack.push(literal)
						# Pop back 2 atoms
						while not self._stack.isAtom():
							self.connect_stack()
							self._stack.pop()
						self.connect_stack()
						self._stack.pop()
						while not self._stack.isAtom():
							self.connect_stack()
							self._stack.pop()
							#break
							"""
