#from pyeda.inter import *
#import pyeda.parsing.boolexpr
#import pyeda.boolalg.expr as pyeda
from sympy import symbols
from sympy.logic.boolalg import to_dnf

class ITRS:

	def __init__(self, procedure):
		print("in init")
		self.procedure = procedure['body']
		self.state_counter = 1
		self.listvariable_counter = 1

		"""
		for 29/07/2020, self.variables is a mapping between var_names to 0 or 1, and self.variable_names is not used.
		it needs to be checked whether there may be issues with variable overriding
		Specially, FOR loop iteration variables need to be properly parsed
		"""
		self.variables = {}
		for obj in procedure['args']['args']:
			self.variables[obj['arg']] = obj['arg']
		#PROBLEMS: the variables mapping is still not right (0,1). There is a problem with variables with the same name
		self.get_variables(self.procedure.copy()) #dict of all variable ids (including for iteration variables) to values (0 if value = 0 else 1)
		#self.variable_names = variables_names #mapping of variable ids to names
		self.graph = {}
		#return self.calculate()

	def get_variables(self, procedure):
		if isinstance(procedure, list):
			for i in procedure:
				self.get_variables(i)
		elif procedure['ast_type'] == "If":
			self.get_variables(procedure['body'])
			self.get_variables(procedure['orelse'])
		elif procedure['ast_type'] == "While":
			self.get_variables(procedure['body'])
		elif procedure['ast_type'] == "For":
			self.variables[procedure['target']['id']] = '0'
			if procedure['iter']['ast_type'] == "Call":
				self.variables['count'] = 'count' #else, give error, we don't know list length yet
		elif procedure['ast_type'] == "Assign" or procedure['ast_type'] == "AnnAssign":
			if 'value' in procedure.keys() and procedure['value']['ast_type'] == "List":
				self.manage_list(procedure, procedure['target']['id'])
			else:
				self.variables[procedure['target']['id']] = procedure['target']['id']
		#elif procedure['ast_type'] == "AnnAssign":
			#self.variables[procedure['target']['id']] = procedure['target']['id']

	def manage_list(self, procedure, target_id, s = ""):
		for i in range(len(procedure['value']['elements'])):
			if procedure['value']['elements'][i]['ast_type'] == "List":
				self.manage_list(procedure['value']['elements'][i], target_id, s+str(i)+"_")
			else:
				self.variables[target_id+"_e"+s+str(i)] = target_id+"_e"+s+str(i)

	def calculate(self):
		print("in calculate")
		source_init = """(GOAL COMPLEXITY)\n(STARTTERM (FUNCTIONSYMBOLS l0))\n"""

		if not self.variables:
			return -1
		else:
			var_string = "(VAR"
			param = "("
			for s in self.variables.keys():
				var_string = var_string + " " + s
				param += ("," if param != "(" else "") + s #param is only used inside set_rules. It makes easier to output (A,B,C,...) strings
			var_string += ")\n"
			param += ")"
			source_init += var_string

			#0 if key value is = 0, else != 0

			self.graph['l0'] = []
			self.make_graph(self.procedure, 'l0', self.variables.copy())

			source_init += self.set_rules(param)
			return source_init

	def get_new_stname(self):
		stname = "l"+str(self.state_counter)
		self.state_counter += 1
		return stname

	def set_rules(self, param):
		rules = "(RULES\n\t"
		print("in rules")
		print(self.graph)
		for i in self.graph.keys():
			print("in in rules")
			for state in range(len(self.graph[i])):
				rules += i+param+" -> Com_1("
				rules += self.graph[i][state][0]+"("
				print(self.graph[i][state][1])
				for s in range(len(self.graph[i][state][1])):
					rules += ("," if s > 0  else "") + self.graph[i][state][1][s]
				print(self.graph[i][state][2])
				rules += ")) :|: "
				print("test")
				for rule in self.graph[i][state][2]:
					rules += (" || " if rule != self.graph[i][state][2][0] else "") + rule
				rules += "\n\t"
		rules += ")"

		return rules
	"""
	make_graph will set the graph attribute. The outcoming structure will be a dictionary with:

	- Keys: the name of the state (l0,l1,l2...)
	- Values: lists of transitions. The transitions will be of the form [state_name, parameters, rules] where:
		- state_name: str with the name of the state (l0,l1,l2...)
		- parameters: tuple of str indicating how the variables change (A, B+1, C...)
		- rules: list of str indicating the constraints to apply the transition (derived from while, if, assert... conditions)
	"""

	def make_graph(self, procedure, stname, variables):
		print("In make_graph")
		print(variables)
		print(procedure)
		base_vars = list((str(value) for value in self.variables.values()))
		if isinstance(procedure, list):
			for com in procedure:
				stname, variables = self.make_graph(com, stname, variables)
			#if isinstance(variables, dict):
			#	variables = list((str(value) for value in variables.values()))
		elif procedure['ast_type'] == "If":
			vars = list((value for value in variables.values()))
			str_rules = self.parse_condition(procedure['test'])
			rules = str_rules.split(" | ")
			new_name = self.get_new_stname()
			self.graph[stname].append([new_name, vars, rules])
			self.graph[new_name] = []
			new_stname, variables = self.make_graph(procedure['body'], new_name, self.variables.copy())
			out_block = self.get_new_stname()
			self.graph[new_stname].append([out_block, variables.copy(), ["TRUE"]])
			if procedure['orelse'] and len(procedure['orelse']) > 0: #else
				else_rules = []
				for i in range(len(rules)):
					else_rules.append("!("+rules[i]+")")
				new_name2 = self.get_new_stname()
				self.graph[stname].append([new_name2, vars, else_rules])
				self.graph[new_name2] = []
				new_stname2, variables = self.make_graph(procedure['orelse'], new_name2, self.variables.copy())
				self.graph[new_stname2].append([out_block, variables.copy(), ["TRUE"]])
				#gestisci caso di elif
			stname = out_block
			self.graph[stname] = []
		elif procedure['ast_type'] == "For":
			vars = list((value for value in variables.values()))
			if procedure['iter']['ast_type'] == "Call":
				rule = procedure['target']['id'] + " < count"
			else:
				rule = procedure['target']['id'] + " < " + procedure['iter']['id']
			new_name = self.get_new_stname()
			self.graph[stname].append([new_name, vars, [rule]])
			self.graph[new_name] = []
			new_stname, variables = self.make_graph(procedure['body'], new_name, self.variables.copy())
			if isinstance(variables, dict):
				variables[procedure['target']['id']] = procedure['target']['id']+"+1" #to be checked
				lst = list((str(value) for value in variables.values()))
			if new_stname not in self.graph.keys():
				self.graph[new_stname] = []
			self.graph[new_stname].append([new_name, lst, [rule]])
			out_block = self.get_new_stname()
			not_rule = "!("+rule+")"
			self.graph[new_name].append([out_block, base_vars, [not_rule]])
			stname = out_block
		elif procedure['ast_type'] == "While":
			vars = list((value for value in variables.values()))
			str_rules = self.parse_condition(procedure['test'])
			rules = str_rules.split(" | ")
			new_name = self.get_new_stname()
			self.graph[stname].append([new_name, vars, rules])
			self.graph[new_name] = []
			new_stname, variables = self.make_graph(procedure['body'], new_name, self.variables.copy())
			if isinstance(variables, dict):
				lst = list((str(value) for value in variables.values()))
			if new_stname not in self.graph.keys():
				self.graph[new_stname] = []
			self.graph[new_stname].append([new_name, lst, rules])
			out_block = self.get_new_stname()
			exit_rules = []
			for i in range(len(rules)):
				exit_rules.append("!("+rules[i]+")")
			self.graph[stname].append([out_block, base_vars, exit_rules])
			self.graph[new_name].append([out_block, base_vars, exit_rules])
			stname = out_block
		else:
			variables = self.get_expr(procedure, variables.copy())
			print("var")
			print(variables)
			#variables = list((str(value) for value in variables.values()))
		return stname, variables

	def get_expr(self, procedure, variables):
		print("in get_expr")
		print(procedure)
		if procedure['ast_type'] == "Assign" or procedure['ast_type'] == "AnnAssign": #lists have to be managed properly yet
			print("assign annassing")
			if procedure['value']['ast_type'] == "List":
				self.manage_list_expr(procedure, procedure['target']['id'], variables)
			else:
				print("in else")
				variables[procedure['target']['id']] = self.get_expr(procedure['value'], variables)
			print(variables)
			return variables
		elif procedure['ast_type'] == "AugAssign":
			op = self.get_op(procedure)
			variables[procedure['target']['id']] = procedure['target']['id'] + op + self.get_expr(procedure['value'], variables)
			print("Augassign")
			print(variables)
			return variables
		elif procedure['ast_type'] == "Subscript":
			if procedure['slice']['ast_type'] == "Index":
				if procedure['slice']['value']['ast_type'] == "Int":
					print("Subscript")
					print(variables)
					return procedure['value']['id']+"_e"+procedure['slice']['value']['value']
				else:
					#TODO: give error
					print("error")
					pass
		elif procedure['ast_type'] == "BinOp":
			op = self.get_op(procedure)
			print("BinOp")
			print(variables)
			c = self.get_expr(procedure['left'], variables) + op + self.get_expr(procedure['right'], variables)
			print("ccc")
			print(c)
			print(variables)
			return c
		elif procedure['ast_type'] == "Name":
			print("name")
			print(variables)
			return procedure['id']
		elif procedure['ast_type'] == "Int":
			print("int")
			print(variables)
			return str(procedure['value'])

	def manage_list_expr(self, procedure, target_id, variables, s = ""):
		for i in range(len(procedure['value']['elements'])):
			if procedure['value']['elements'][i]['ast_type'] == "List":
				variables = self.manage_list_expr(procedure['value']['elements'][i], target_id, s+str(i)+"_")
			else:
				variables[target_id+"_e"+s+str(i)] = self.get_expr(procedure['value']['elements'][i], variables)
		return variables

	def get_op(self, procedure):
		if procedure['op']['ast_type'] == "Add":
			op = "+"
		elif procedure['op']['ast_type'] == "Sub":
			op = "-"
		elif procedure['op']['ast_type'] == "Mult":
			op = "*"
		elif procedure['op']['ast_type'] == "Div": #to be checked
			op = "/"
		return op

	def create_sat_expression(self, condition, m): #map is used to map linear expression to boolean values, so that pyade can generate the 
		print("condition")
		print(condition)
		if "op" in condition.keys() and (condition['ast_type'] == "BinOp" or condition['ast_type'] == "UnaryOp") or condition['ast_type'] == "BoolOp":
			if condition['op']['ast_type'] == "Or":
				return self.create_sat_expression(condition['values'][0], m) | self.create_sat_expression(condition['values'][1], m)
			elif condition['op']['ast_type'] == "And":
				return self.create_sat_expression(condition['values'][0], m) & self.create_sat_expression(condition['values'][1], m)
			elif condition['op']['ast_type'] == "Not":
				return ~self.create_sat_expression(condition['operand'], m)
			elif condition['op']['ast_type'] == "Add":
				return self.create_sat_expression(condition['left'], m) + " + " + self.create_sat_expression(condition['right'], m)
			elif condition['op']['ast_type'] == "Mult":
				return self.create_sat_expression(condition['left'], m) + " * " + self.create_sat_expression(condition['right'], m)
			elif condition['op']['ast_type'] == "Sub":
				return self.create_sat_expression(condition['left'], m) + " - " + self.create_sat_expression(condition['right'], m)
			elif condition['op']['ast_type'] == "Div":
				return self.create_sat_expression(condition['left'], m) + " / " + self.create_sat_expression(condition['right'], m)


		elif condition['ast_type'] == "Compare":
			if condition['op']['ast_type'] == "Gt":
				s = self.create_sat_expression(condition['left'], m) + " > " + self.create_sat_expression(condition['right'], m)
			elif condition['op']['ast_type'] == "Lt":
				s = self.create_sat_expression(condition['left'], m) + " < " + self.create_sat_expression(condition['right'], m)
			elif condition['op']['ast_type'] == "Eq":
				s = self.create_sat_expression(condition['left'], m) + " = " + self.create_sat_expression(condition['right'], m)
			m.append(s)
			return symbols("v"+str(len(m)-1))

		elif condition['ast_type'] == "Subscript":
			if condition['slice']['ast_type'] == "Index":
				if condition['slice']['value']['ast_type'] == "Int":
					return condition['target']['id']+"_e"+condition['slice']['value']['value']
				else:
					#TODO: give error
					pass

		elif condition['ast_type'] == "Name":
			return condition['id']
		elif condition['ast_type'] == "Int":
			return str(condition['value'])

	"""def parse_boolean_expr(self, f):
		if isinstance(f, pyeda.OrOp):
			print(list(f))
			for i in range(len(f)):
				s = (" || " if i > 0 else "")+self.parse_boolean_expr(f[i])
			return s
		elif isinstance(f, pyeda.AndOp):
			for i in range(len(f)):
				s = (" && " if i > 0 else "")+self.parse_boolean_expr(f[i])
			return s
		else:
			return str(f)
	"""
	def parse_condition(self, condition):
		m = []
		f = to_dnf(self.create_sat_expression(condition, m)) #side-effect: to_dnf changes the form of the boolean expression
		#f = self.parse_boolean_expr(str(f))
		#f = str(f)
		f = str(f)
		for i in range(len(m)):
			f = f.replace("v"+str(i), "("+m[i]+")") #there will be problem if variables like v1 are declared
		f = f.replace('~','!')
		f = f.replace('&', '&&')
		return f
