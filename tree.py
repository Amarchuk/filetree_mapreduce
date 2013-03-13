# Python 2/3 Tree Implementation
#
# Copyright (C) 2011
# Brett Alistair Kromkamp - brettkromkamp@gmail.com
# Copyright (C) 2012
# Xiaming Chen - chenxm35@gmail.com
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of the contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import unittest

from node import Node

# Module constants
(_ADD, _DELETE, _INSERT) = range(3)
(_ROOT, _DEPTH, _WIDTH) = range(3)

def add_file(dirs, filename, tree):
    curr_node = tree.get_node(tree.root)
    for dir in dirs:
        if dir in curr_node.fpointer:
            curr_node = tree.get_node(dir)
        else:
            tree.create_node("dir", dir, parent = curr_node.identifier)
            curr_node = tree.get_node(dir)
    tree.create_node("file", filename, parent = curr_node.identifier)

class MultipleRootError(Exception):
	pass

class Tree(object):
	def __init__(self):
		self.nodes = []		# Node object
		self.root = None	# identifier

	def add_node(self, node, parent=None):
		"""
		Add a new node to tree. 
		The 'node' parameter refers to an instance of Class::Node
		"""
		if parent is None:
			if self.root is not None:
				raise MultipleRootError
			else:
				self.root = node.identifier
		self.nodes.append(node)
		self.__update_fpointer(parent, node.identifier, _ADD)
		node.bpointer = parent

	def create_node(self, name, identifier=None, parent=None):
		"""
		Create a child node for the node indicated by the 'parent' parameter
		"""
		node = Node(name, identifier)
		self.add_node(node, parent)
		return node

	def expand_tree(self, nid = None, mode=_DEPTH, filter = None):
		# Python generator. Loosly based on an algorithm from 'Essential LISP' by
		# John R. Anderson, Albert T. Corbett, and Brian J. Reiser, page 239-241
		def real_true(pos):
			return True

		if nid is None:
			nid = self.root
		if filter is None:
			filter = real_true

		if filter(nid):
			yield nid
			queue = self[nid].fpointer
			while queue:
				if filter(queue[0]):
					yield queue[0]
					expansion = self[queue[0]].fpointer
					if mode is _DEPTH:
						queue = expansion + queue[1:]  # depth-first
					elif mode is _WIDTH:
						queue = queue[1:] + expansion  # width-first
				else:
					queue = queue[1:]

	def get_index(self, nid):
		for index, node in enumerate(self.nodes):
			if node.identifier == nid:
				break
		return index
		
	def get_node(self, nid):
		return self.nodes[self.get_index(nid)]

	def is_branch(self, nid):
		"""
		Return the following nodes of [nid]
		"""
		return self[nid].fpointer

	def move_node(self, source, destination):
		""" 
		Move a node indicated by the 'source' parameter to the parent node
		indicated by the 'dest' parameter
		"""
		parent = self[source].bpointer
		self.__update_fpointer(parent, source, _DELETE)
		self.__update_fpointer(destination, source, _ADD)
		self.__update_bpointer(source, destination)

	def paste(self, nid, new_tree):
		"""
		Paste a new tree to the original one by linking the root 
		of new tree to nid.
		"""
		assert isinstance(new_tree, Tree)

		# check identifier replication
		all_nodes = self.nodes + new_tree.nodes
		ids = [i.identifier for i in all_nodes]
		idset = set(ids)
		if len(idset) != len(ids):
			raise ValueError, 'Duplicated nodes exists.'

		new_tree[new_tree.root].bpointer = nid
		self.__update_fpointer(nid, new_tree.root, _ADD)
		self.nodes += new_tree.nodes

	def remove_node(self, identifier):
		"""
		Remove a node indicated by 'identifier'. All the successors are removed, too.
		"""
		parent = self[identifier].bpointer
		for id in self.expand_tree(identifier):
			self.nodes.remove(self[id])
		self.__update_fpointer(parent, identifier, _DELETE)

	def rsearch(self, nid, filter=None):
		"""
		Search the tree from nid to the root along links reversedly.
		"""
		def real_true(p):
			return True

		if filter is None:
			filter = real_true
		current = nid
		while current != None:
			if filter(current):
				yield current
			current = self[current].bpointer

	def show(self, nid = None, level=_ROOT):
		""""
			Another implementation of printing tree using Stack
			Print tree structure in hierarchy style.
			For example:
				Root
				|___ C01
				|	 |___ C11
				|		  |___ C111
				|		  |___ C112
				|___ C02
				|___ C03
				|	 |___ C31
			A more elegant way to achieve this function using Stack structure, 
			for constructing the Nodes Stack push and pop nodes with additional level info. 
		"""
		leading = '' 
		lasting = '|___ '

		if nid is None:
			nid = self.root
		label = "{0}[{1}]".format(self[nid].name, self[nid].identifier)

		queue = self[nid].fpointer
		#print level
		if level == _ROOT:
			print(label)
		else:
			if level <= 1:
				leading += ('|'+' '*4)*(level-1)
			else:
				leading += ('|'+' '*4) + (' '*5*(level-2))
			print("{0}{1}{2}".format(leading, lasting, label))

		if self[nid].expanded:
			level += 1
			for element in queue:
				self.show(element, level)  # recursive call
				
	def subtree(self, nid):
		"""
		Return a COPY of subtree of the whole tree with the nid being the new root.
		And the structure of the subtree is maintained from the old tree.
		"""
		st = Tree()
		st.root = nid
		for node_n in self.expand_tree(nid):
			st.nodes.append(self[node_n])
		return st

	def __contains__(self, identifier):
		return [node.identifier for node in self.nodes
				if node.identifier is identifier]

	def __getitem__(self, key):
		return self.nodes[self.get_index(key)]

	def __len__(self):
		return len(self.nodes)

	def __setitem__(self, key, item):
		self.nodes[self.get_index(key)] = item

	def __update_bpointer(self, nid, identifier):
		self[nid].bpointer = identifier

	def __update_fpointer(self, nid, identifier, mode):
		if nid is None:
			return
		else:
			self[nid].update_fpointer(identifier, mode)

#--------------------------------------------------------------------------------

# Test suite

class TestTree(unittest.TestCase):
	def setUp(self):
		pass

	def test_initialization(self):
		pass

	def tearDown(self):
		pass

