from vyper.itrs.const import BUILT_IN, ENV_VAR, CONSTS

"""
return a dict with state variables, func parameters, consts, built_in variables and local function variables
"""
def get_env_var(procedure, state_variables, structs):
	variables = state_variables
	for obj in procedure['args']['args']:
		variables[obj['arg']] = obj['arg']
	for s in ENV_VAR:
		variables[s] = s
	for s in CONSTS:
		variables[s] = s
	variables = get_variables(procedure['body'].copy(), structs, variables)
	print("aia")
	return variables

"""
return a dict with the ast of the whiles inside the procedure. As keys they will have their node_id
"""

def get_whiles(procedure, whiles = {}):
	print("init")
	print(whiles)
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
	print("return while")
	print(whiles.keys())
	return whiles.copy()

"""
return a dict with all the local variables
"""


def get_variables(procedure, structs, variables = {}):
	print("get_variables")
	print(procedure)
	print(variables)
	if isinstance(procedure, list):
		for i in procedure:
			variables = get_variables(i, structs, variables)
	elif procedure['ast_type'] == "If":
		variables = get_variables(procedure['body'], structs, variables)
		variables = get_variables(procedure['orelse'], structs, variables)
	elif procedure['ast_type'] == "While":
		variables = get_variables(procedure['body'], structs, variables)
	elif procedure['ast_type'] == "For":
		variables[procedure['target']['id']] = '0'
		variables = get_variables(procedure['body'], structs, variables)
		if procedure['iter']['ast_type'] == "Call":
			variables['count'] = 'count' #else, give error, we don't know list length yet
	elif procedure['ast_type'] == "Call":
		return variables
	elif procedure['ast_type'] == "Assign" or procedure['ast_type'] == "AnnAssign":
		if 'value' in procedure.keys() and procedure['value']['ast_type'] == "List": #if a list is the right expression
			s = get_full_name(procedure['target'])
			variables = manage_list(procedure, s, variables)
		elif 'value' in procedure.keys() and procedure['value']['ast_type'] == "Call": #if a struct is the right expression
			if procedure['value']['func']['id'] in structs.keys():
				for i in structs[procedure['value']['func']['id']]:
					s = get_full_name(procedure['target'])
					variables[s+"."+i] = s+"."+i
		else:
			s = get_full_name(procedure['target'])
			variables[s] = s
	return variables
	#elif procedure['ast_type'] == "AnnAssign":
		#self.variables[procedure['target']['id']] = procedure['target']['id']

"""
return the name of the variable, considering also subscripts(example, var[1]), structs (with points)
"""

def get_full_name(procedure):
	if procedure['ast_type'] == "Name":
		return procedure['id']
	if procedure['ast_type'] == "Int":
		return str(procedure['value'])
	if procedure['ast_type'] == "Attribute":
		return get_full_name(procedure['value'])+"."+procedure['attr']
	if procedure['ast_type'] == "Subscript": #check for matrixes and test
		return get_full_name(procedure['value'])+"_e"+get_full_name(procedure['slice'])
	if procedure['ast_type'] == "Index":
		if procedure['value']['ast_type'] == "Int":
			return get_full_name(procedure['value'])
		else:
			#TODO: give error
			pass
"""
return the variables obtained from a list that is a right expression
"""

def manage_list(procedure, target_id, variables, s = ""):
	for i in range(len(procedure['value']['elements'])):
		if procedure['value']['elements'][i]['ast_type'] == "List":
			variables = manage_list(procedure['value']['elements'][i], target_id, variables, s+str(i)+"_")
		else:
			variables[target_id+"_e"+s+str(i)] = target_id+"_e"+s+str(i)
	return variables

