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
	symb = {'(',')','|','&','~'}
	extr1 = (0 if rule[0] in symb else -1)

	print(rule)

	while i<len(rule):
		if rule[i] in symb or i == len(rule)-1:
			if i-extr1 <= 1 or (rule[extr1+1:i] == (i-extr1-1) * rule[extr1+1] and rule[extr1+1] == ' '):
				extr1 = i
			else:
				m['v'+str(c)] = rule[extr1+1:i]
				extr1 = i
				c += 1
		i+=1

	for i in m.keys():
		print(m[i])
		rule = rule.replace(m[i], i)

	print("strtosympy")
	print(rule)
	print(parse_expr(rule, evaluate = False))
	rule = str(to_dnf(parse_expr(rule, evaluate = False)))
	print("rule")
	print(rule)
	for i in m.keys():
		rule = rule.replace(i, m[i])
	#rule = remove_parenthesis(rule)
	rule = rule.replace("&", "&&")
	rule = rule.replace("|", "||")
	rule = rule.replace("~", "!")

	return rule

def remove_parenthesis(rule):
	rule = rule.split('|')
	for s in range(len(rule)):
		print("in for")
		i = 0
		j = len(rule[s])-1
		while i<j:
			print("while")
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
				print(rule[s])
				break

	rule = '|'.join(rule)
	print("parenthesis")
	print(rule)
	return rule

def get_substrs(var):
	m = []
	if isinstance(var,str):
		while "_e(" in var:
			m.append(var[var.find('(')+1: var.find(')')])
			var = var[0: var.find('('):] + var[var.find(')')+1::]
	return m

def separate_by_op(var):
	op_map = []
	symb = {'+','*','-','/'}
	for i in range(len(var)):
		if var[i] in symb:
			op_map.append(var[i])
			var = var[:i] + '+' + var[i+1:]
	return var.split('+'), op_map

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
		if "_e(" in s:
			del variables[s]
	return variables

