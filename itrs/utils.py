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
