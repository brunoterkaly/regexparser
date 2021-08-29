from io import StringIO
import json
import pprint
import sys
import re
import os

from subprocess import Popen, PIPE, STDOUT

'''

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
'''

# ===============================================================
# https://deniskyashif.com/2020/08/17/parsing-regex-with-recursive-descent/
# ===============================================================
class MyStack:
     def __init__(self):
         self.container = []  # You don't want to assign [] to self - when you do that, you're just assigning to a new local variable called `self`.  You want your stack to *have* a list, not *be* a list.

     def isEmpty(self):
         return self.size() == 0   # While there's nothing wrong with self.container == [], there is a builtin function for that purpose, so we may as well use it.  And while we're at it, it's often nice to use your own internal functions, so behavior is more consistent.

     def push(self, item):
         self.container.append(item)  # appending to the *container*, not the instance itself.

     def pop(self):
         element = self.container.pop()  # pop from the container, this was fixed from the old version which was wrong
         #self.container[len(self.container)-1] = None
         return element

     def peek(self):
         if self.isEmpty():
             raise Exception("Stack empty!")
         return self.container[-1]  # View element at top of the stack

     def size(self):
         return len(self.container)  # length of the container

     def show(self):
         return self.container  # display the entire stack as list

class RegExNode:
    def __init__(self, label, children = []):
        self._label = label
        self._children.append(children)

class TreeNode:
    def __init__(self, label, children):
        self._label = label
        self._children.append(children)
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

    # ===========================================================
    # New Grammar Functions
    # ===========================================================
    def toParseTree2(self, regex, regex_node):
        self._pattern = regex
        self._pos = 0
        self._stack.push(regex_node)
        return self.expr2()

    def expr2(self):
        # Call down the chain pushing

        while not self._stack.isEmpty():
            self.term2()
            if self.hasMoreChars() and self.peek() == "|":
                self.match("|")
                # Recurse
                regex_node = RegExNode('expr', [])
                self._stack.push(regex_node)
                expression = self.expr()

    def term2(self):
        term = RegExNode('term')
        self._stack.push(term)
        factor = self.factor2()
        if self.hasMoreChars() and self.peek() != "|":
            # Recurse 1
            self.term2()

    def factor2(self):
        factor = RegExNode('factor')
        self._stack.push(factor)
        atom = self.atom2()
        # before looking for meta, let's process stack
        # pop until 'factor'

        try:
            while True:
                topoffset = len(self._stack.container)-1
                topnode = self._stack.container[topoffset]
                trgoffset = topoffset-1
                trgnode = self._stack.container[trgoffset]
                trgnode.children.append(topnode)
                currtop = self._stack.pop()
                if currtop._label == 'factor':
                    exit
        except Exception as ex:
            print(ex)
        while not currtop._label == 'factor':
            peektop = self._stack.container[topoffset]
            peektop._children.append(currtop)

            currtop = self._stack.pop()

            pass

        if self.hasMoreChars() and self.isMetaChar(self.peek()):

            meta = self.next()
            return TreeNode("Factor", [atom, TreeNode(meta, None)])

    def atom2(self):
        atom = RegExNode('atom')
        self._stack.push(atom)
        if self.peek() == "(":
            self.match("(")
            # Recurse 3
            expression = self.expr()
            self.match(")")
            return TreeNode(
                "Atom", [TreeNode("lparen", "("), expression, TreeNode("rparen", ")")]
            )
        ch = self.char2()

    def char2(self):
        if self.isMetaChar(self.peek()):
            raise ("Unexpected symbol = ".format(self.peek()))
        if self.peek() == "\\":
            self.match("\\")
            return TreeNode("Char", [TreeNode("slash", "\\"), TreeNode("next", self.next())])

        literal = RegExNode(self.next(), None)
        char = RegExNode("Char", literal)
        self._stack.push(char)

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
            return TreeNode("Char", [TreeNode("slash", "\\"), TreeNode("next", self.next())])

        return TreeNode("Char", [TreeNode(self.next(), None)])

    def any_char_except_meta(self):
        pass

if __name__ == "__main__":
    expr = "ab*|ac"
    expr = "a+b?"

    tree_node = TreeNode("Begin", [])
    regex_node = RegExNode('expr', [])
    final_tree2 = tree_node.toParseTree2(expr, regex_node)
    print(final_tree2)
    # Old code
    tree_node2 = TreeNode("Begin", [])
    final_tree = tree_node2.toParseTree(expr)
