from io import StringIO
import json
import pprint
import sys
import re
import os

from subprocess import Popen, PIPE, STDOUT

'''
	1. allocate 'startnode' and 'endnode'. It will have x number of roots. 2 in this case.
	2. Goal is to partition on '|'
	3. Read the 'a' and append to data of curr node
	4. Read 'b' and append to data of curr node
	5. Read '*' and append to data of curr node
	6. Hit '|' so:
		a. 'abc*' node = endnode
		b. startnode.root += node 'ab*'
		c. allocate new node for 'ac'
	7. New node. Read until '|' or end
		a. add to 'ac' node 
	8. Hit end. 
		a. 'ac' node = endnode
		b. startnode.root += node 'ac'
		
'''


class RootNode:
   def __init__(self, dataval=None):
      self._roots = []
    
class Node:
   def __init__(self):
      self._dataval = ""
      self._nextnode = None

class Automata:

    def __init__(self, node):
        super().__init__()
        self._root = node


    # TODO: Add logic for second half
    def parse(self, expression, end_node):
        try:
            
            token_pipe = '|' # represents how many roots from main node
            current_node = Node()
            end = len(expression)
            i = 0
            # loop through reg expression and append until token_pipe
            for i in range(0, end):
                curr_char = expression[i]
                if curr_char != '|' or i == end:
                    current_node._dataval += str(curr_char)
                else:
                    # 'ab*' needs to point to end node
                    # also added to _root collection
                    current_node._nextnode = end_node
                    self._root._roots.append(current_node)
                    current_node = Node()
            if i == end-1 and len(current_node._dataval) > 0:
                # then we have the last node. subtract one in if statement
                # so we can make sure we get here. then point to end
                # and conclude with 2 roots.
                current_node._nextnode = end_node
                self._root._roots.append(current_node)
                pass
        except Exception as ex:
            print(ex)

                


if __name__ == "__main__":
    expr = "ab*|ac"
    # 1.
    start_node = RootNode()
    end_node = RootNode()
    automata = Automata(start_node)
    automata.parse(expr, end_node)
    pass

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
