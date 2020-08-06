from vyper.itrs.__init__ import ITRS

class ITRS_global:

	def __init__(self, procedure):
		self.state_vars, self.functions, self.structs = self.get_globals(procedure)
		self.itrs = [] #itrs will have the dicts of the parsed whiles in each function
		for i in self.functions:
			print("func")
			print(i)
			self.itrs.append(ITRS(i, self.state_vars.copy(), self.structs.copy()).run())
		print(self.itrs)

	"""
	return global variables. functions, structs
	"""

	def get_globals(self, procedure):
		vars = {}
		functions = []
		structs = {}

		for obj in procedure:
			if obj['ast_type'] == "Assign" or obj['ast_type'] == "AnnAssign":
				vars["self." + obj['target']['id']] = "self." + obj['target']['id']
			elif obj['ast_type'] == "FunctionDef":
				functions.append(obj)
			elif obj['ast_type'] == "ClassDef" and obj['class_type'] == "struct":
				structs[obj['name']] = []
				for i in obj['body']:
					structs[obj['name']].append(i['target']['id'])
		return vars, functions, structs