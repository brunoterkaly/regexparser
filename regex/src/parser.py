from io import StringIO
import json
import pprint
import sys
import re
import os

from subprocess import Popen, PIPE, STDOUT

# ===============================================================
# https://deniskyashif.com/2020/08/17/parsing-regex-with-recursive-descent/
# ===============================================================


class TreeNode:
	def __init__(self, label, children):
		self._label = label
		self._children = children
		self._pattern = ""
		self._pos = 0
		self._ = None
		self._ = None
		self._ = None
		self._ = None

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
  		match(ch)
		return ch

	# ===========================================================
	# Grammar Functions
	# ===========================================================
	def toParseTree(self, regex):
		self._pattern = regex
		self._pos = 0
		return self.expr()


	def expr(self):
		term = self.term()
		if self.hasMoreChars() and self.peek() == '|':
			match('|')
			expression = self.expr()
			return TreeNode('Expr', [term, TreeNode('Or', '|'), expression])
		return TreeNode('Expr', [term])

	def term(self):
		factor = self.factor()
		if self.hasMoreChars() and self.peek() != '|':
			term = self.term()
			return TreeNode('Term', [factor, term])
		return TreeNode('Term', [factor])
					   

	def factor(self):
		atom = self.atom()
		if self.hasMoreChars() and self.isMetaChar(self.peek()):
			meta = self.next()
			return TreeNode('Factor', [atom, TreeNode('meta', meta)])
		return TreeNode('Factor', [atom])

	def atom(self):
		if self.peek() == '(':
			match('(')
			expression = self.expr()
			match(')')
			return TreeNode('Atom', 
				[TreeNode('paren', '('), expression, TreeNode('paren', ')')])

	def char(self):
		if self.isMetaChar(self.peek()):
			raise ("Unexpected symbol = ".format(self.peek()))
		if self.peek() == '\\':
			match('\\');
			return TreeNode('Char', [TreeNode('slash', '\\'), TreeNode('next', next())])

		return TreeNode('Char', [TreeNode('next', self.next())])

	def any_char_except_meta(self):
		pass


class Node:
	def __init__(self):
		self._dataval = ""
		self._nextnode = None
