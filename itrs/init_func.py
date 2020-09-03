from vyper.itrs.const import BUILT_IN, ENV_VAR, CONSTS

"""
return a dict with state variables, func parameters, consts, built_in variables and local function variables
"""
def get_env_var(procedure, state_variables, state_types, structs):
	variables = state_variables
	types = state_types
	for obj in procedure['args']['args']:
		variables[obj['arg']] = obj['arg']
		types[obj['arg']] = obj['annotation']['id']
	for s in ENV_VAR:
		variables[s] = s
	for s in CONSTS:
		variables[s] = s
	m = {}
	variables = get_variables(procedure['body'].copy(), structs, types, variables, m)
	#variables = create_len_var(variables, types, m)
	print("out get var")
	print(variables)
	return variables, types, m


def create_len_var(variables, types, m):
	for i in range(m[0]):
		variables['v'+str(i)] = i
		types['v'+str(i)] = "Int"
	return variables

"""
return a dict with the ast of the whiles inside the procedure. As keys they will have their node_id
"""

def get_whiles(procedure, whiles = {}):
	if isinstance(procedure, list):
		for obj in procedure:
			whiles = get_whiles(obj, whiles)
	elif procedure['ast_type'] == "If":
		whiles = get_whiles(procedure['body'], whiles)
		whiles = get_whiles(procedure['orelse'], whiles)
	elif procedure['ast_type'] == "For":
		whiles = get_whiles(procedure['body'], whiles)
	elif procedure['ast_type'] == "While":
		whiles[procedure['node_id']] = procedure
		whiles = get_whiles(procedure['body'], whiles)
	return whiles.copy()

"""
return a dict with all the local variables
"""


def get_variables(procedure, structs, types, variables = {}, m = {}):
	print("get_variables")
	print(procedure)
	if isinstance(procedure, list):
		for i in procedure:
			print("in loop")
			print(i)
			variables = get_variables(i, structs, types, variables, m)
			print("end loop")
	elif procedure['ast_type'] == "If":
		variables = get_variables(procedure['body'], structs, types, variables, m)
		variables = get_variables(procedure['orelse'], structs, types, variables, m)
	elif procedure['ast_type'] == "While":
		variables = get_variables(procedure['body'], structs, types, variables, m)
	elif procedure['ast_type'] == "For":
		variables[procedure['target']['id']] = '0'
		types[procedure['target']['id']] = 'uint256'
		variables = get_variables(procedure['body'], structs, types, variables, m)
		if procedure['iter']['ast_type'] == "Call":
			variables['count'] = 'count' #else, give error, we don't know list length yet
			types['count'] = 'uint256'
	elif procedure['ast_type'] == "Call":
		return variables
		#if procedure['value']['func']['id'] in self.structs:
	elif procedure['ast_type'] == "Assign" or procedure['ast_type'] == "AnnAssign":
		s = get_full_name(procedure['target'], variables, types)
		print("fff")
		print(s)
		if len(s.split('_e(')) == 1:
			if 'value' in procedure.keys() and procedure['value']['ast_type'] == "List": #if a list is the right expression
				#s = get_full_name(procedure['target'], variables, types)
				variables[s] = s
				types[s] = "List"
				variables = manage_list(procedure['value'], s, variables, types)
				m[s] = get_list_length(procedure['value'])
			elif procedure['value']['ast_type'] == "Name" and procedure['value']['id'] in types.keys() and (types[procedure['value']['id']] == "List" or types[procedure['value']['id']] == "Struct"):
				if types[procedure['value']['id']] == "List":
					el = [key for key in variables.keys() if procedure['value']['id']+"_e" in key]
				if types[procedure['value']['id']] == "Struct":
					el = [key for key in variables.keys() if procedure['value']['id']+"." in key]
				fname = get_full_name(procedure['target'], variables, types)
				variables[fname] = variables[procedure['value']['id']]
				types[fname] = types[procedure['value']['id']]
				for obj in el:
					name = fname+obj[len(procedure['value']['id'])::]
					variables[name] = variables[obj]
					types[name] = types[obj]

			elif 'value' in procedure.keys() and procedure['value']['ast_type'] == "Call": #if a struct is the right expression
				print(structs.keys())
				if procedure['value']['func']['id'] in structs.keys():
					print("ent")
					#s = get_full_name(procedure['target'], variables, types)
					variables[s] = s
					types[s] = "Struct"
					for pos in range(len(structs[procedure['value']['func']['id']])):
						i = structs[procedure['value']['func']['id']][pos]
						if procedure['value']['args'][0]['values'][pos]['ast_type'] == "Name":
							t = procedure['value']['args'][0]['values'][pos]['id']
							if types[t] == "List" or types[t] == "Struct":
								#i = structs[procedure['value']['func']['id']][pos]
								print("ent2")
								print(s+"."+i[0])
								if types[t] == "List":
									el = [key for key in variables.keys() if t+"_e" in key]
								if types[t] == "Struct":
									el = [key for key in variables.keys() if t+"." in key]
								for obj in el:
									name = s+"."+i[0]+obj[len(t)::]
									variables[name] = variables[obj]
									types[name] = types[obj]
						if procedure['value']['args'][0]['values'][pos]['ast_type'] == "List":
							variables = manage_list(procedure['value']['args'][0]['values'][pos]['value'], s+"."+i[0], variables, types, m)
						variables[s+"."+i[0]] = s+"."+i[0]
						types[s+"."+i[0]] = i[1]
						print(variables)
						print(types)
					print("out")
			else:
				#s = get_full_name(procedure['target'], variables, types)
				variables[s] = s
				if 'annotation' in procedure.keys():
					types[s] = procedure['annotation']['id']
	print("ret var")
	print(variables)
	return variables
	#elif procedure['ast_type'] == "AnnAssign":
		#self.variables[procedure['target']['id']] = procedure['target']['id']

"""
return the name of the variable, considering also subscripts(example, var[1]), structs (with points)
"""

def get_full_name(procedure, variables = {}, types = {}, first = 1):
	print("getfullname")
	print(procedure)
	if procedure['ast_type'] == "BinOp":
		s = get_full_name(procedure['left'], variables, types, 0) + get_op(procedure) + get_full_name(procedure['right'], variables, types, 0)
	if procedure['ast_type'] == "Name":
		s = procedure['id']
	if procedure['ast_type'] == "Int":
		s = str(procedure['value'])
	if procedure['ast_type'] == "Attribute":
		s = get_full_name(procedure['value'], variables, types, 0)+"."+procedure['attr']
	if procedure['ast_type'] == "Subscript": #check for matrixes and test
		s = get_full_name(procedure['value'], variables, types, 0)+"_e"+get_full_name(procedure['slice'], variables, types, 0)
	if procedure['ast_type'] == "Index":
		if procedure['value']['ast_type'] != "Int":
			s = "("+get_full_name(procedure['value'], variables, types, 0)+")"
		else:
			s = get_full_name(procedure['value'], variables, types, 0)

	if first:
		print("boh")
		if "_e(" in s:
			variables[s] = s
			types[s] = "NameIndex"

	return s

"""
return the variables obtained from a list that is a right expression
"""

def get_list_length(procedure):
	m = []
	if procedure['elements'][0]['ast_type'] == "List":
		m = get_list_length(procedure["elements"][0])
	m.insert(0,len(procedure['elements']))
	return m

def manage_list(procedure, target_id, variables, types, s = ""):
	for i in range(len(procedure['elements'])):
		if procedure['elements'][i]['ast_type'] == "List":
			variables = manage_list(procedure['elements'][i], target_id, variables, types, s+str(i)+"_e")
		else:
			variables[target_id+"_e"+s+str(i)] = target_id+"_e"+s+str(i)
			types[target_id+"_e"+s+str(i)] = procedure['elements'][i]['ast_type']
	return variables

def get_op(procedure):
	if procedure['op']['ast_type'] == "Add":
		op = "+"
	elif procedure['op']['ast_type'] == "Sub":
		op = "-"
	elif procedure['op']['ast_type'] == "Mult":
		op = "*"
	elif procedure['op']['ast_type'] == "Div": #mod to be added
		op = "/"
	return op

