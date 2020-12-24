import os
from vyper.itrs.__init__ import ITRS
from vyper.itrs.koat import KOAT

class ITRS_global:

	def __init__(self, procedure):
		self.state_vars, self.state_types, self.functions, self.structs = self.get_globals(procedure)
		self.bounds = []
		self.itrs = [] #itrs will have the dicts of the parsed whiles in each function
		for i in self.functions:
			self.itrs.append(ITRS(i, self.state_vars.copy(), self.state_types.copy(), self.structs.copy()).run())

		print("itrk")
		print(self.itrs)
		self.bounds = KOAT().get_bounds(self.itrs)
		i = 0
		while i < len(self.bounds):
			if self.bounds[i] == "":
				self.bounds = self.bounds[:i]+self.bounds[i+1:]
				i -= 1
			i += 1

	"""
	return global variables. functions, structs
	"""

	def get_globals(self, procedure):
		vars = {}
		types = {}
		functions = []
		structs = {}

		for obj in procedure:
			if obj['ast_type'] == "Assign" or obj['ast_type'] == "AnnAssign":
				vars["self." + obj['target']['id']] = "self." + obj['target']['id']
				types["self." + obj['target']['id']] = obj['target']['ast_type']
			elif obj['ast_type'] == "FunctionDef":
				functions.append(obj)
			elif obj['ast_type'] == "ClassDef" and obj['class_type'] == "struct":
				structs[obj['name']] = []
				for i in obj['body']:
					structs[obj['name']].append([i['target']['id'], i['annotation']['id']])
		return vars, types, functions, structs
