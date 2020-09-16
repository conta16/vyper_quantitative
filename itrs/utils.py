from sympy import symbols
from sympy.parsing.sympy_parser import parse_expr
from sympy.logic.boolalg import to_dnf

def string_to_dnf(rule):
	rule = rule.replace("&&", "&")
	rule = rule.replace("||", "|")
	rule = rule.replace("!","~")
	i = 1
	c = 0
	m = {}
	symb = {'(',')','|','&','~'} #{'(',')','|','&','~','>=','<=','>','<','=='}
	extr1 = 0 #(0 if rule[0] in symb else -1)
	rule = "("+rule+")"

	while i<len(rule):
		if rule[i] in symb or i == len(rule)-1:
			if i-extr1 <= 1 or (rule[extr1+1:i] == (i-extr1-1) * rule[extr1+1] and rule[extr1+1] == ' '):
				extr1 = i
			else:
				#if i == len(rule)-1:
				#	m['v'+str(c)] = rule[extr1+1:]
				#else:
				m['v'+str(c)] = rule[extr1+1:i]
				if rule[i:i+2] in symb:
					extr1 = i+1
				else:
					extr1 = i
				c += 1
		i+=1

	for i in m.keys():
		rule = rule.replace(m[i], i)

	rule = str(to_dnf(parse_expr(rule, evaluate = False)))
	for i in m.keys():
		rule = rule.replace(i, m[i])
	#rule = remove_parenthesis(rule)
	rule = rule.replace("&", "&&")
	rule = rule.replace("|", "||")
	rule = rule.replace("~", "!")

	return rule

def remove_first_parenthesis(s):
	s = s.strip()
	if s[0] == '(':
		return remove_first_parenthesis(s[1:])
	return s

def remove_parenthesis(rule):
	rule = rule.split('|')
	for s in range(len(rule)):
		i = 0
		j = len(rule[s])-1
		while i<j:
			if rule[s][i] == ' ' or rule[s][i] == '\t':
				i+=1
			elif rule[s][i] != '(':
				break
			if rule[s][j] == ' ' or rule[s][j] == '\t':
				j-=1
			elif rule[s][j] != ')':
				break
			if rule[s][i] == '(' and rule[s][j] == ')':
				rule[s] = rule[s].replace('(','',1)
				rule[s] = rule[s].replace(')','',-1)
				break

	rule = '|'.join(rule)
	return rule

def get_substrs(var):
	m = []
	if isinstance(var,str):
		while "_e[" in var:
			m.append(var[var.find('[')+1: var.find(']')])
			var = var[0: var.find('['):] + var[var.find(']')+1::]
	return m

def separate_by_op(var):
#	names = []
#	tmp = var.split('_e')
	op_map = []
	symb = {'+','*','-','/','<=','>=','&&'}
	composite = {'<','>'}
#	for i in range(len(tmp)):
	#for j in range(len(var)):
	#	if var[j] in symb:
	#		if var[j+1] in symb:
	#			op_map.append(var[j]+var[j+1])
	#			var = var[:j] + '+' + var[j+2:]
	#		else:
	#			op_map.append(var[j])
	#			var = var[:j] + '+' + var[j+1:]
	for st in symb:
		var = var.replace(st,'+')
	for st in composite:
		var = var.replace(st,'+')
		#for st in symb:
		#	tmp[i] = tmp[i].replace(st,'+')
	vars = var.split('+')
	for i in range(len(vars)):
		vars[i] = vars[i].strip()
#	for i in range(len(vars)):
#		vars[i] = vars[i].strip()
#		if vars[i][0] == '[':
#			vars[i] = vars[i][1:]
#		if vars[i][-1] == ']':
#			vars[i] == vars[:-1]
#		if vars[i] in types.keys() and types[vars[i]] == "List":
#			names.append(vars[i])
	return vars, op_map

def list_sub(list, max):
	index = 0
	for i in range(len(list)):
		if list[i] > 0:
			index = i
			break
		if list[i] == 0:
			list[i] = max[i]

	list[index] -= 1
	return list

def get_reduced_list(list, num):
	lst = []
	if len(list) > num:
		lst = list[num:]
	return lst

def reduce_list(list, num):
	lst = []
	if len(list) >= num:
		lst = list[:num]
	#for i in range(len(list)):
	#	if "_e(" in list[i]:
			
	return lst

def reduce_variables(variables):
	for s in list(variables):
		if "_e[" in s:
			del variables[s]
	return variables

