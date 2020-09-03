from copy import deepcopy
from sympy import symbols
from sympy.logic.boolalg import to_dnf
from vyper.itrs.const import BUILT_IN, ENV_VAR, CONSTS
from vyper.itrs.init_func import *
from vyper.itrs.utils import *
import os

class ITRS:

	def __init__(self, procedure, state_variables, state_types, state_structs):
		#take whiles ast in function, pass them to calculate, return itrs to while in dictionary. In itrs_global, in the end, we will have all the functions with their iteration upper bound
		#TODO: fix increasing variable problem(x=x+z+2; x=x+5 gives only x+5). aka replace var x with its current value, so x+z+2
		self.graph = {} #explained in make_graph
		self.state_counter = 1 #counts the number of states. Is used in l1,l2,l3...
		self.func_needed = [] #stores the names of the functions in which the procedure depends
		self.structs = state_structs
		self.whiles = get_whiles(procedure['body']) #mapping from node_id of while to while ast. In the end, instead of while ast, there will be the while itrs code
		self.types = state_types
		self.tmp = {}
		self.variables, self.types, self.list_lengths = get_env_var(procedure, state_variables, state_types, state_structs)
		#self.procedure = procedure['body']
		#PROBLEMS: the variables mapping is still not right (0,1). There is a problem with variables with the same name
		#dict of all variable ids (including for iteration variables) to values (0 if value = 0 else 1)
		#self.variable_names = variables_names #mapping of variable ids to names

	"""
	start the translation, the outputs are the itrs codes stored in a dict in their corresponding node_id
	"""

	def run(self):
		for obj in self.whiles.keys():
			self.whiles[obj] = self.calculate(self.whiles[obj])
		return self.whiles

	def calculate(self, procedure):
		source_init = "(GOAL COMPLEXITY)" + os.linesep + "(STARTTERM (FUNCTIONSYMBOLS l0))" + os.linesep #\n

		if not self.variables:
			return -1
		else:
			var_string = "(VAR"
			param = "("
			for s in self.variables.keys():
				var_string = var_string + " " + s
				param += ("," if param != "(" else "") + s #param is only used inside set_rules. It makes easier to output (A,B,C,...) strings
			var_string += ")"+os.linesep #\n
			param += ")"
			source_init += var_string

			#0 if key value is = 0, else != 0

			self.graph['l0'] = []
			self.make_graph(procedure, 'l0', self.variables.copy())
			print("check")
			print(self.variables)
			print(self.graph)
			source_init += self.set_rules(param)
			self.graph = {}
			print("source init")
			print(source_init)
			return source_init

	"""
	return the string of the rules part in the itrs code
	"""

	def set_rules(self, param):
		self.parse_list_indexes()
		print("check2")
		print(self.graph)
		rules = "(RULES"+os.linesep #\n\t
		for i in self.graph.keys():
			for state in range(len(self.graph[i])):
				rules += i+param+" -> Com_1("
				rules += self.graph[i][state][0]+"("
				for s in range(len(self.graph[i][state][1])):
					rules += ("," if s > 0  else "") + str(self.graph[i][state][1][s])
				rules += ")) :|: "
				s = ""
				for rule in self.graph[i][state][2]:
					s += (" && " if rule != self.graph[i][state][2][0] else "") + rule
				rules += remove_parenthesis(s)
				rules += ""+os.linesep #\n\t
		rules += ")"

		return rules

	def parse_list_indexes(self):
		print("in parse_list")
		g = self.graph
		self.variables = reduce_variables(self.variables.copy())
		print("variabless")
		print(self.variables)
		for i in g.keys():
			changes = []
			#for iter in range(len(g[i])):
			#	red_lst = get_reduced_list(g[i][iter][1], len(self.variables))
			#	g[i][iter][1] = reduce_list(g[i][iter][1], len(self.variables))
			#	changes = self.parse_substr_assign(i, iter)
			for iter in range(len(g[i])):
				print("g[i]")
				print(g[i][iter][1])
				print("var")
				print(self.variables)
				g[i][iter][1] = reduce_list(g[i][iter][1], len(self.variables))
				vars = g[i][iter][1]
				print("varse")
				print(vars)
				for j in range(len(vars)):
					m = get_substrs(vars[j])
					if m == []:
						continue
					self.add_list_transitions(m, changes, vars[j], j, i, iter)

	def parse_substr_assign(self, a, b):
		print("parse_substr_assign")
		g = self.graph
		l = list(self.variables.keys())
		changes = []
		for i in range(len(l)):
			if "_e(" in l[i]:
				if l[i] != g[a][b][1][i]:
					changes.append(g[a][b][1][i])
		return changes

	def add_list_transitions(self, m, changes, var, j, i, iter):
		print("in add_list")
		g = self.graph
		div_var, op_map = separate_by_op(var)
		lst = []
		for s in div_var:
			tmp = s.split('_e')
			list_name = tmp[0]
			if list_name in self.types.keys() and self.types[list_name] == "List":
				for x in self.list_lengths[list_name]:
					lst.append(x)
		#tmp = var.split('_e')
		#tmp.pop(0)
		for o in range(len(lst)):
			lst[o] -= 1

		max = deepcopy(lst)
		base = deepcopy(g[i][iter])
		while any(x != 0 for x in lst):
			lst2 = []
			tmp = var.split("_e")
			t = deepcopy(base)
			for o in range(len(lst)):
				if tmp[o+1][0] == '(':
					tmp[o+1] = tmp[o+1][tmp[o+1].find(')')+1:]
					tmp[o+1] = str(lst[o])+tmp[o+1]
					lst2.append(lst[o])
					#it goes here multiple times
			s = '_e'.join(tmp)
			print("outr")
			print(tmp)
			print(s)
			print(lst2)
			print(m)
			print(t)
			t[1][j] = s
			for o in range(len(lst2)):
				t[2].extend([m[o]+"<="+str(lst2[o]), m[o]+">="+str(lst2[o])])
			print("outr2")

			g[i].append(t)
			lst = list_sub(lst, max)
		#g[i].pop(iter)

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
		print("base_vars")
		print(self.variables.values())
		print(procedure)
		#if isinstance(variables, dict):
		base_vars = list((str(value) for value in self.variables.values()))
		#elif isinstance(variables, list):
		#	base_vars = []
		#	for obj in variables:
		#		if isinstance(obj, dict):
		#			base_vars.append(list((str(value) for value in self.variables.values())))
		if isinstance(procedure, list):
			for com in procedure:
				stname, variables = self.make_graph(com, stname, variables)
		elif procedure['ast_type'] == "If":
			#vars = list((value for value in variables.values())) #make the variables dict a list
			print("this is if")
			str_rules = self.parse_condition(procedure['test'])
			rules = str_rules.split(" || ") 
			new_name = self.get_new_stname()
			if isinstance(variables, list):
				for obj in variables:
					vars = []
					if isinstance(obj,dict):
						vars = list((value for value in obj.values()))
						for i in rules:
							self.graph[stname].append([new_name, vars, [i]])
			elif isinstance(variables, dict):
				vars = list((value for value in variables.values())) #[]
				for i in rules:
					self.graph[stname].append([new_name, vars, [i]])
			#for i in rules:
			#	print("ch list1")
			#	print(vars)
			#	self.graph[stname].append([new_name, vars, [i]]) #transition from start(stname) to this "if"(new_name) saved
			self.graph[new_name] = []
			new_stname, tvariables = self.make_graph(procedure['body'], new_name, self.variables.copy())
			if new_stname not in self.graph.keys():
				self.graph[new_stname] = []
			out_block = self.get_new_stname()
			if isinstance(tvariables, list):
				for obj in tvariables:
					vars = []
					if isinstance(obj,dict):
						vars = list((value for value in obj.values())) #variables has now the variable changes occurred at the end of the if body, so it needs to be reparsed to list
						print("ch list2")
						print(vars)
						self.graph[new_stname].append([out_block, vars, ["TRUE"]])
			elif isinstance(tvariables, dict):
				vars = list((value for value in tvariables.values()))
				print("ch list3")
				print(vars)
				self.graph[new_stname].append([out_block, vars, ["TRUE"]]) #transition from end of if block to outblock is always true. There may be variable changes if the end of the "if" block doesn't correspond to the end of another block
			if procedure['orelse'] and len(procedure['orelse']) > 0:
				else_rules = []
				#r = ""
				#for i in range(len(rules)):
					#r += (" ||")
				else_rules.extend(self.negate(str_rules))
				new_name2 = self.get_new_stname()
				if isinstance(variables, list):
					for obj in variables:
						if isinstance(obj,dict):
							for i in else_rules:
								vars = list((value for value in obj.values()))
								self.graph[stname].append([new_name2, vars, [i]])
				elif isinstance(variables, dict):
					vars = list((value for value in variables.values()))
					self.graph[stname].append([new_name, vars, [i]])
				self.graph[new_name2] = []
				new_stname2, tvariables = self.make_graph(procedure['orelse'], new_name2, self.variables.copy())
				if new_stname2 not in self.graph.keys():
					self.graph[new_stname2] = []
				if isinstance(tvariables, list):
					for obj in tvariables:
						vars = []
						if isinstance(obj,dict):
							vars = list((value for value in obj.values())) #variables has now the variable changes occurred at the end of the if body, so it needs to be reparse$
							print("ch list5")
							print(vars)
							self.graph[new_stname2].append([out_block, vars, ["TRUE"]])
				elif isinstance(tvariables, dict):
					vars = list((value for value in tvariables.values()))
					print("ch list6")
					print(vars)
					self.graph[new_stname2].append([out_block, vars, ["TRUE"]])
			else:
				else_rules = []
				else_rules.extend(self.negate(str_rules))
				if isinstance(variables, list):
					for obj in variables:
						if isinstance(obj, dict):
							vars = list((value for value in obj.values()))
							for i in else_rules:
								self.graph[stname].append([out_block, vars, [i]])
				elif isinstance(variables, dict):
					vars = list((value for value in variables.values()))
					for i in else_rules:
						self.graph[stname].append([out_block, vars, [i]])
				#vars = list((value for value in tvariables.values()))
				#self.graph[new_stname2].append([out_block, vars, ["TRUE"]])
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
			new_stname, tvariables = self.make_graph(procedure['body'], new_name, self.variables.copy())
			if isinstance(tvariables, dict):
				tvariables[procedure['target']['id']] = procedure['target']['id']+"+1" #to be checked #added t, to be checked
				lst = list((str(value) for value in tvariables.values()))
			if new_stname not in self.graph.keys():
				self.graph[new_stname] = []
			self.graph[new_stname].append([new_name, lst, [rule]]) #back_edge
			out_block = self.get_new_stname()
			not_rule = self.negate(rule)
			self.graph[new_name].append([out_block, base_vars, not_rule]) #exit
			stname = out_block
		elif procedure['ast_type'] == "While":


			str_rules = self.parse_condition(procedure['test'])
			rules = str_rules.split(" || ") 
			new_name = self.get_new_stname()
			self.graph[new_name] = []
			new_name2 = self.get_new_stname()
			out_block = self.get_new_stname()
			exit_rules = []
			exit_rules.extend(self.negate(str_rules))
			if isinstance(variables, list):
				for obj in variables:
					vars = []
					if isinstance(obj,dict):
						vars = list((value for value in obj.values()))
						for i in rules:
							self.graph[stname].append([new_name, vars, [i]])
							print("new_name")
							print(new_name)
							print(new_name2)
							self.graph[new_name].append([new_name2, base_vars, [i]])
						for i in exit_rules:
							print(out_block)
							self.graph[new_name].append([out_block, base_vars, [i]])
			elif isinstance(variables, dict):
				vars = list((value for value in variables.values()))
				for i in rules:
					self.graph[stname].append([new_name, vars, [i]])
					print("new_name2")
					print(new_name2)
					self.graph[new_name].append([new_name2, base_vars, [i]])
				for i in exit_rules:
					self.graph[new_name].append([out_block, base_vars, [i]])


			#vars = list((value for value in variables.values()))
			#str_rules = self.parse_condition(procedure['test'])
			#rules = str_rules.split(" || ")
			#print("rules")
			#print(rules)
			#new_name = self.get_new_stname()
			#for i in rules:
			#	self.graph[stname].append([new_name, vars, [i]])
			self.graph[new_name2] = []
			new_stname, tvariables = self.make_graph(procedure['body'], new_name2, self.variables.copy())
			if new_stname not in self.graph.keys():
				self.graph[new_stname] = []
			if isinstance(tvariables, list):
				for obj in tvariables:
					lst = []
					if isinstance(obj, dict):
						lst = (list((str(value) for value in obj.values())))
						for i in rules:
							print("ch list8")
							print(lst)
							print("new_stname")
							print(new_stname)
							self.graph[new_stname].append([new_name, lst, [i]])
			elif isinstance(tvariables, dict):
				lst = list((str(value) for value in tvariables.values()))
				for i in rules:
					print("ch list9")
					print(lst)
					print("new_stname")
					print(new_stname)
					self.graph[new_stname].append([new_name, lst, [i]])
			out_block = self.get_new_stname()
			exit_rules = []
			#r = ""
			#for i in range(len(rules)):
				#r += (" || " if i>0 else "")+rules[i]
			exit_rules.extend(self.negate(str_rules))
			for i in exit_rules:
				if isinstance(base_vars, list):
					#if isinstance(base_vars[0], list):
					#	for obj in base_vars:
					#		lst = []
					#		print("ch list10")
					#		print(obj)
					#		self.graph[stname].append([out_block, obj, [i]])
					#		self.graph[new_name].append([out_block, obj, [i]])
					#else:
						#it should only enter here. the other option must be changed
					print("ch list11")
					print(base_vars)
					self.graph[stname].append([out_block, base_vars, [i]])
					self.graph[new_name].append([out_block, base_vars, [i]])
				#elif isinstance(base_vars, dict):
				#	lst = (list((str(value) for value in base_vars.values())))
				#	print("ch list12")
				#	print(lst)
				#	self.graph[stname].append([out_block, lst, [i]])
				#	self.graph[new_name].append([out_block, lst, [i]])
			stname = out_block
		else:
			variables = self.get_expr(procedure, variables, self.types)
			print("back")
			print(variables)
			#insert function to check if subscripts with variables are used.
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

	def get_expr(self, procedure, variables, types):
		print("get_expr")
		print(procedure)
		print(variables)
		if procedure['ast_type'] == "Assign" or procedure['ast_type'] == "AnnAssign":
			if not isinstance(variables,list):
				variables = [variables]
			l = len(variables)
			for i in range(len(variables)):
				print("here1")
				s = get_full_name(procedure['target'], variables[i], types, 0)
				print("here2")
				if procedure['value']['ast_type'] == "List":
	#				if isinstance(variables, list):
	#					for i in range(len(variables)):
					variables[i] = self.manage_list_expr(procedure['value'], s, variables[i])
	#				else:
	#					variables = self.manage_list_expr(procedure['value'], s, variables)
				elif procedure['value']['ast_type'] == "Call":
	#				if isinstance(variables, list):
	#					for i in range(len(variables)):
					variables[i] = self.manage_struct_expr(procedure['value'], s, variables[i])
	#				else:
	#					variables = self.manage_struct_expr(procedure['value'], s, variables)
				#_e cannot be safely used in Vyper for this if case. it needs to be changed. Plus, maybe it can get moved to init_func
				else:
					print("normal")
					variables[i][s] = self.get_expr(procedure['value'], variables[i], types)
					if "_e(" in s:
		#				self.parse_list_assign(variables, i, s)
						self.tmp[s] = variables[i][s]
				print("im here")
				variables = self.parse_list_assign(variables,i,s)
			if "_e(" in s:
				variables = get_reduced_list(variables,l)
			return variables
		elif procedure['ast_type'] == "AugAssign":
			print("aug")
			op = get_op(procedure)
			if not isinstance(variables,list):
				variables = [variables]
			l = len(variables)
			for i in range(len(variables)):
				s = get_full_name(procedure['target'], variables[i], types)
				if procedure['target']['ast_type'] == "Attribute":
					variables[i][s] = self.get_expr(procedure['target'], variables[i], types) + op + self.get_expr(procedure['value'], variables[i], types)
				else:
					variables[i][s] = self.get_expr(procedure['target'], variables[i], types) + op + self.get_expr(procedure['value'], variables[i], types)
				variables = self.parse_list_assign(variables,i,s)
			if "_e(" in s:
				variables = get_reduced_list(variables,l)
			return variables
		elif procedure['ast_type'] == "Subscript": #matrixes should have problems
			if procedure['slice']['ast_type'] == "Index":
				if procedure['slice']['value']['ast_type'] == "Int":
					return variables[get_full_name(procedure, variables, types)] #variables[procedure['value']['id']+"_e"+str(procedure['slice']['value']['value'])]
				else:
					return get_full_name(procedure, variables, types)
		elif procedure['ast_type'] == "Call":
			if procedure['value']['id'] in BUILT_IN:
				return
			else:
				self.func_needed.append(procedure['func']['id']) #missing: external function handling
		elif procedure['ast_type'] == "BinOp":
			op = get_op(procedure)
			c = self.get_expr(procedure['left'], variables, types) + op + self.get_expr(procedure['right'], variables, types)
			return c
		elif procedure['ast_type'] == "Attribute":
			return str(variables[get_full_name(procedure, variables, types)])
			#return self.get_expr(procedure['value'], variables) + "." + procedure['attr']
		elif procedure['ast_type'] == "Name":
			
			return variables[procedure['id']]
		elif procedure['ast_type'] == "Int":
			return str(procedure['value'])

	def parse_list_assign(self, variables, i, s):
		if "_e(" in s:
			name = s.split("_e(")[0]
			for obj in variables[i].keys():
				if "_e" in obj and "(" not in obj:
					base = variables[i].copy()
					el_name = obj.split("_e")[0]
					if name == el_name:
						base[obj] = variables[i][s]
						variables.append(base)
			#variables.pop(i)
		return variables


	def manage_struct_expr(self, procedure, target_id, variables, s=""):
		print("mngstruct")
		for i in range(len(procedure['args'][0]['values'])): #the 0 worries me
			if procedure['args'][0]['values'][i]['ast_type'] == "Int":
				variables[target_id+"."+procedure['args'][0]['keys'][i]['id']] = procedure['args'][0]['values'][i]['value']
			elif procedure['args'][0]['values'][i]['ast_type'] == "Name":
#				if procedure['args'][0]['values'][i]['id']+"_e0" in variables.keys():
#					print("here")
#					variables = self.copy_list(procedure, target_id, i, variables)
#				else:
					variables[target_id+"."+procedure['args'][0]['keys'][i]['id']] = procedure['args'][0]['values'][i]['id']
		return variables

	"""
	manages lists in right hand-side expressions. It's similar to manage_list, but it changes the variables' values
	"""

	def manage_list_expr(self, procedure, target_id, variables, s = ""):
		print("mngstruct")
		for i in range(len(procedure['elements'])):
			if procedure['elements'][i]['ast_type'] == "List":
				variables = self.manage_list_expr(procedure['elements'][i], target_id, variables, s+str(i)+"_e")
			else:
				variables[target_id+"_e"+s+str(i)] = self.get_expr(procedure['elements'][i], variables, self.types)
		return variables

	def copy_list(self, procedure, target_id, pos, variables, s="", c=0):
		id = procedure['args'][0]['values'][pos]['id']
		nested_lists = [key for key,value in variables.items() if id+s+"_e"+str(c) in key]
		if id+s+"_e"+str(c) in variables.keys():
			variables[target_id+"."+procedure['args'][0]['keys'][pos]['id']+s+"_e"+str(c)] = variables[id+s+"_e"+str(c)]
			variables = self.copy_list(procedure, target_id, pos, variables, s, c+1)
		else:
			for i in nested_lists:
				variables = self.copy_list(procedure, target_id, pos, variables, s+"_e"+str(c), 0)
		return variables


	"""
	RULE PARSING
	"""

	"""
	create conditions (derived from if, for, while entry conditions) in a format such that sympy can parse them into dnf (disjunctive normal forms)
	"""

	def create_sat_expression(self, condition, m, negate = 0): #map is used to map linear expression to boolean values, so that pyade can generate the 
		if "op" in condition.keys() and (condition['ast_type'] == "BinOp" or condition['ast_type'] == "UnaryOp") or condition['ast_type'] == "BoolOp":
			if condition['op']['ast_type'] == "Or":
				return (self.create_sat_expression(condition['values'][0], m, negate) | self.create_sat_expression(condition['values'][1], m, negate))
			elif condition['op']['ast_type'] == "And":
				return self.create_sat_expression(condition['values'][0], m, negate) & self.create_sat_expression(condition['values'][1], m, negate)
			elif condition['op']['ast_type'] == "Not":
				return self.create_sat_expression(condition['operand'], m, 1-negate)
			elif condition['op']['ast_type'] == "Add":
				return self.create_sat_expression(condition['left'], m, negate) + " + " + self.create_sat_expression(condition['right'], m, negate)
			elif condition['op']['ast_type'] == "Mult":
				return self.create_sat_expression(condition['left'], m, negate) + " * " + self.create_sat_expression(condition['right'], m, negate)
			elif condition['op']['ast_type'] == "Sub":
				return self.create_sat_expression(condition['left'], m, negate) + " - " + self.create_sat_expression(condition['right'], m, negate)
			elif condition['op']['ast_type'] == "Div":
				return self.create_sat_expression(condition['left'], m, negate) + " / " + self.create_sat_expression(condition['right'], m, negate) #mod to be added


		elif condition['ast_type'] == "Compare":
			if condition['op']['ast_type'] == "Gt":
				s = self.create_sat_expression(condition['left'], m, negate) + (" > " if not negate else " <= ") + self.create_sat_expression(condition['right'], m, negate)
			elif condition['op']['ast_type'] == "Lt":
				s = self.create_sat_expression(condition['left'], m, negate) + (" < " if not negate else " >= ") + self.create_sat_expression(condition['right'], m, negate)
			elif condition['op']['ast_type'] == "Eq":
				#koat doesn't have equal
				if not negate:
					s1 = self.create_sat_expression(condition['left'], m, negate) + " <= " + self.create_sat_expression(condition['right'], m, negate)
					s2 = self.create_sat_expression(condition['left'], m, negate) + " >= " + self.create_sat_expression(condition['right'], m, negate)
					m.append(s1)
					m.append(s2)
					
					return symbols("v"+str(len(m)-2)) & symbols("v"+str(len(m)-1))
				else:
					s1 = self.create_sat_expression(condition['left'], m, negate) + " > " + self.create_sat_expression(condition['right'], m, negate)
					s2 = self.create_sat_expression(condition['left'], m, negate) + " < " + self.create_sat_expression(condition['right'], m, negate)
					m.append(s1)
					m.append(s2)
					return symbols("v"+str(len(m)-2)) | symbols("v"+str(len(m)-1))
			elif condition['op']['ast_type'] == "GtE":
				s = self.create_sat_expression(condition['left'], m, negate) + (" >= " if not negate else " < ") + self.create_sat_expression(condition['right'], m, negate)
			elif condition['op']['ast_type'] == "LtE":
				s = self.create_sat_expression(condition['left'], m, negate) + (" <= " if not negate else " > ") + self.create_sat_expression(condition['right'], m, negate)
			elif condition['op']['ast_type'] == "NotEq":
				if not negate:
					s1 = self.create_sat_expression(condition['left'], m, negate) + " < " + self.create_sat_expression(condition['right'], m, negate)
					s2 = self.create_sat_expression(condition['left'], m, negate) + " > " + self.create_sat_expression(condition['right'], m, negate)
					m.append(s1)
					m.append(s2)
					return symbols("v"+str(len(m)-2)) | symbols("v"+str(len(m)-1))
				else:
					s1 = self.create_sat_expression(condition['left'], m, negate) + " >= " + self.create_sat_expression(condition['right'], m, negate)
					s2 = self.create_sat_expression(condition['left'], m, negate) + " <= " + self.create_sat_expression(condition['right'], m, negate)
					m.append(s1)
					m.append(s2)
					return symbols("v"+str(len(m)-2)) & symbols("v"+str(len(m)-1))
			m.append(s)
			return symbols("v"+str(len(m)-1)) #sympy can't parse to dnf unless the expression is in propositional logic. With this, every compare command is mapped to a term

		elif condition['ast_type'] == "Subscript":
			if condition['slice']['ast_type'] == "Index":
				#if condition['slice']['value']['ast_type'] == "Int":
				return get_full_name(condition, self.variables, self.types,0)
				#else:
					#TODO: give error

		elif condition['ast_type'] == "Attribute":
			return get_full_name(condition, self.variables, self.types,0)
		elif condition['ast_type'] == "Name":
			return condition['id']
		elif condition['ast_type'] == "Int":
			return str(condition['value'])
		elif condition['ast_type'] == "NameConstant":
			return str(condition['value']).upper()

	def parse_condition(self, condition):
		m = []
		f = to_dnf(self.create_sat_expression(condition, m))
		f = str(f)
		for i in range(len(m)):
			f = f.replace("v"+str(i), m[i]) #Change terms into their compare values. There will be problem if variables like v1 are declared
		#f = remove_parenthesis(f)
		f = f.replace('~','!')
		f = f.replace('&', '&&')
		f = f.replace('|', '||')
		return f

	def negate(self, rule):
		change = {
			"<" : ">=",
			">" : "<=",
			"<=" : ">",
			">=" : "<",
			"&&" : "||",
			"||" : "&&",
			"True": "False" #find way to translate this
		}

		lst_rule = list(rule)
		i = 0
		while i<len(lst_rule):
			if lst_rule[i] == "<":
				if i+1 < len(lst_rule) and lst_rule[i+1] == "=":
					lst_rule[i] = change["<="]
					lst_rule.pop(i+1)
				else:
					lst_rule[i] = change["<"]
			elif lst_rule[i] == ">":
				if i+1 < len(lst_rule) and lst_rule[i+1] == "=":
					lst_rule[i] = change[">="]
					lst_rule.pop(i+1)
				else:
					lst_rule[i] = change[">"]
			elif lst_rule[i] == "&":
				if i+1 < len(lst_rule):
					lst_rule.pop(i+1)
				lst_rule[i] = change["&&"]
			elif lst_rule[i] == "|":
				if i+1 < len(lst_rule):
					lst_rule.pop(i+1)
				lst_rule[i] = change["||"]
			i+=1
		rule = ''.join(lst_rule)
		rule = string_to_dnf(rule)
		rule = str(rule).split("||") #rule, at this point, is always only one element. If or is in the rule, the conditions get splitted
		return [rule] if isinstance(rule, str) else rule
