from sympy import symbols
from sympy.logic.boolalg import to_dnf
from vyper.itrs.const import BUILT_IN, ENV_VAR, CONSTS
from vyper.itrs.init_func import *

class ITRS:

	def __init__(self, procedure, state_variables, state_structs):
		#take whiles ast in function, pass them to calculate, return itrs to while in dictionary. In itrs_global, in the end, we will have all the functions with their iteration upper bound
		#TODO: fix increasing variable problem(x=x+z+2; x=x+5 gives only x+5). aka replace var x with its current value, so x+z+2
		self.graph = {} #explained in make_graph
		self.state_counter = 1 #counts the number of states. Is used in l1,l2,l3...
		self.func_needed = [] #stores the names of the functions in which the procedure depends
		self.structs = state_structs
		self.whiles = get_whiles(procedure['body']) #mapping from node_id of while to while ast. In the end, instead of while ast, there will be the while itrs code
		print("whiles")
		print(self.whiles)
		self.variables = get_env_var(procedure, state_variables, state_structs)
		#self.procedure = procedure['body']
		#PROBLEMS: the variables mapping is still not right (0,1). There is a problem with variables with the same name
		#dict of all variable ids (including for iteration variables) to values (0 if value = 0 else 1)
		#self.variable_names = variables_names #mapping of variable ids to names

	"""
	start the translation, the outputs are the itrs codes stored in a dict in their corresponding node_id
	"""

	def run(self):
		print("run")
		print(self.whiles.keys())
		for obj in self.whiles.keys():
			print("while")
			print(self.whiles[obj])
			self.whiles[obj] = self.calculate(self.whiles[obj])
		return self.whiles

	def calculate(self, procedure):
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
			self.make_graph(procedure, 'l0', self.variables.copy())
			source_init += self.set_rules(param)
			self.graph = {}
			print(source_init)
			return source_init

	"""
	return the string of the rules part in the itrs code
	"""

	def set_rules(self, param):
		rules = "(RULES\n\t"
		for i in self.graph.keys():
			for state in range(len(self.graph[i])):
				rules += i+param+" -> Com_1("
				rules += self.graph[i][state][0]+"("
				for s in range(len(self.graph[i][state][1])):
					rules += ("," if s > 0  else "") + self.graph[i][state][1][s]
				rules += ")) :|: "
				for rule in self.graph[i][state][2]:
					rules += (" || " if rule != self.graph[i][state][2][0] else "") + rule
				rules += "\n\t"
		rules += ")"

		return rules

	"""
	IF-ELSE, WHILE, FOR PARSING
	"""

	"""
	make_graph will set the graph attribute. The outcoming structure will be a dictionary with:

	- Keys: the name of the state (l0,l1,l2...)
	- Values: lists of transitions. The transitions will be of the form [state_name, parameters, rules] where:
		- state_name: str with the name of the state (l0,l1,l2...)
		- parameters: tuple of str indicating how the variables change (A, B+1, C...)
		- rules: list of str indicating the constraints to apply the transition (derived from while, if, assert... conditions)
	"""

	def make_graph(self, procedure, stname, variables):
		print("oppala")
		#print(procedure)
		base_vars = list((str(value) for value in self.variables.values()))
		if isinstance(procedure, list):
			for com in procedure:
				stname, variables = self.make_graph(com, stname, variables)
		elif procedure['ast_type'] == "If":
			vars = list((value for value in variables.values())) #make the variables dict a list
			str_rules = self.parse_condition(procedure['test'])
			rules = str_rules.split(" | ") 
			new_name = self.get_new_stname()
			self.graph[stname].append([new_name, vars, rules]) #transition from start(stname) to this "if"(new_name) saved
			self.graph[new_name] = []
			new_stname, variables = self.make_graph(procedure['body'], new_name, self.variables.copy())
			vars = list((value for value in variables.values())) #variables has now the variable changes occurred at the end of the if body, so it needs to be reparsed to list
			out_block = self.get_new_stname() #name for the state outside the if block
			if new_stname not in self.graph.keys():
				self.graph[new_stname] = []
			self.graph[new_stname].append([out_block, vars, ["TRUE"]]) #transition from end of if block to outblock is always true. There may be variable changes if the end of the "if" block doesn't correspond to the end of another block
			if procedure['orelse'] and len(procedure['orelse']) > 0:
				else_rules = []
				for i in range(len(rules)):
					else_rules.append("!("+rules[i]+")")
				new_name2 = self.get_new_stname()
				self.graph[stname].append([new_name2, vars, else_rules])
				self.graph[new_name2] = []
				new_stname2, variables = self.make_graph(procedure['orelse'], new_name2, self.variables.copy())
				if new_stname2 not in self.graph.keys():
					self.graph[new_stname2] = []
				vars = list((value for value in variables.values()))
				self.graph[new_stname2].append([out_block, vars, ["TRUE"]])
				#gestisci caso di elif
			stname = out_block #out_block will be the current state name
			self.graph[stname] = []
		elif procedure['ast_type'] == "For":
			vars = list((value for value in variables.values()))
			if procedure['iter']['ast_type'] == "Call": #range
				rule = procedure['target']['id'] + " < count"
			else:
				rule = procedure['target']['id'] + " < " + procedure['iter']['id'] #in (to be checked)
			new_name = self.get_new_stname()
			self.graph[stname].append([new_name, vars, [rule]])
			self.graph[new_name] = []
			new_stname, variables = self.make_graph(procedure['body'], new_name, self.variables.copy())
			if isinstance(variables, dict):
				variables[procedure['target']['id']] = procedure['target']['id']+"+1" #to be checked
				lst = list((str(value) for value in variables.values()))
			if new_stname not in self.graph.keys():
				self.graph[new_stname] = []
			self.graph[new_stname].append([new_name, lst, [rule]]) #back_edge
			out_block = self.get_new_stname()
			not_rule = "!("+rule+")"
			self.graph[new_name].append([out_block, base_vars, [not_rule]]) #exit
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
		return stname, variables

	def get_new_stname(self):
		stname = "l"+str(self.state_counter)
		self.state_counter += 1
		return stname

	"""
	EXPRESSION PARSING
	"""

	"""
	manage variable changes for assign, annassign, augassign. It parses also right hand-side expressions
	"""

	def get_expr(self, procedure, variables):
		if procedure['ast_type'] == "Assign" or procedure['ast_type'] == "AnnAssign":
			if procedure['value']['ast_type'] == "List":
				self.manage_list_expr(procedure, procedure['target']['id'], variables)
			elif procedure['target']['ast_type'] == "Attribute":
				variables[get_full_name(procedure['target'])] = self.get_expr(procedure['value'], variables)
			else:
				variables[get_full_name(procedure['target'])] = self.get_expr(procedure['value'], variables)
			return variables
		elif procedure['ast_type'] == "AugAssign":
			op = self.get_op(procedure)
			if procedure['target']['ast_type'] == "Attribute":
				variables[get_full_name(procedure['target'])] = self.get_expr(procedure['target'], variables) + op + self.get_expr(procedure['value'], variables)
			else:
				variables[get_full_name(procedure['target'])] = self.get_expr(procedure['target'], variables) + op + self.get_expr(procedure['value'], variables)
			return variables
		elif procedure['ast_type'] == "Subscript": #matrixes should have problems
			if procedure['slice']['ast_type'] == "Index":
				if procedure['slice']['value']['ast_type'] == "Int":
					return procedure['value']['id']+"_e"+str(procedure['slice']['value']['value'])
				else:
					#TODO: give error
					pass
		elif procedure['ast_type'] == "Call":
			if procedure['value']['id'] in BUILT_IN:
				return
			else:
				self.func_needed.append(procedure['func']['id']) #missing: external function handling
		elif procedure['ast_type'] == "BinOp":
			op = self.get_op(procedure)
			c = self.get_expr(procedure['left'], variables) + op + self.get_expr(procedure['right'], variables)
			return c
		elif procedure['ast_type'] == "Attribute":
			return self.get_expr(procedure['value'], variables) + "." + procedure['attr']
		elif procedure['ast_type'] == "Name":
			return procedure['id']
		elif procedure['ast_type'] == "Int":
			return str(procedure['value'])

	"""
	manages lists in right hand-side expressions. It's similar to manage_list, but it changes the variables' values
	"""

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
		elif procedure['op']['ast_type'] == "Div": #mod to be added
			op = "/"
		return op

	"""
	RULE PARSING
	"""

	"""
	create conditions (derived from if, for, while entry conditions) in a format such that sympy can parse them into dnf (disjunctive normal forms)
	"""

	def create_sat_expression(self, condition, m): #map is used to map linear expression to boolean values, so that pyade can generate the 
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
				return self.create_sat_expression(condition['left'], m) + " / " + self.create_sat_expression(condition['right'], m) #mod to be added


		elif condition['ast_type'] == "Compare":
			if condition['op']['ast_type'] == "Gt":
				s = self.create_sat_expression(condition['left'], m) + " > " + self.create_sat_expression(condition['right'], m)
			elif condition['op']['ast_type'] == "Lt":
				s = self.create_sat_expression(condition['left'], m) + " < " + self.create_sat_expression(condition['right'], m)
			elif condition['op']['ast_type'] == "Eq":
				s = self.create_sat_expression(condition['left'], m) + " = " + self.create_sat_expression(condition['right'], m)
			m.append(s)
			return symbols("v"+str(len(m)-1)) #sympy can't parse to dnf unless the expression is in propositional logic. With this, every compare command is mapped to a term

		elif condition['ast_type'] == "Subscript":
			if condition['slice']['ast_type'] == "Index":
				if condition['slice']['value']['ast_type'] == "Int":
					return condition['value']['id']+"_e"+str(condition['slice']['value']['value'])
				else:
					#TODO: give error
					pass

		elif condition['ast_type'] == "Attribute":
			return condition['attr']
		elif condition['ast_type'] == "Name":
			return condition['id']
		elif condition['ast_type'] == "Int":
			return str(condition['value'])

	def parse_condition(self, condition):
		m = []
		f = to_dnf(self.create_sat_expression(condition, m))
		f = str(f)
		for i in range(len(m)):
			f = f.replace("v"+str(i), "("+m[i]+")") #Change terms into their compare values. There will be problem if variables like v1 are declared
		f = f.replace('~','!')
		f = f.replace('&', '&&')
		return f
