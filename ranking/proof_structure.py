#class for generating a counter optimal proof structure for static bound analysis of while loops

#P: procedure (in ast)
#S: set of counters inserted
#G: DAG
#backedges: back gotos (end of while loop iterations)
#M: maps each backedge to a certain counter
#B: maps each backedge to a linear bound

#Theoretically, a proof structure is defined as a (S,M,G,B) tuple. For simplicity, other attributes have been added inside the class.

import ast
import codegen

class ProofStructure:

	def __init__(self, ast_dict):
		self.P = ast_dict
		self.S = set()
		self.G = {}
		self.M = []
		self.B = []
		self.backedges = []
		self.calculate()

	def calculate(self):
		self.list_backedges(self.P)
		self.make_counter_optimal()

	def list_backedges(self, procedure):
		if isinstance(procedure,list):
			for i in range(len(procedure)):
				self.list_backedges(procedure[i])
		else:
			if procedure['ast_type'] == "While":
				#TODO: if-else backedges to be added
				self.backedges.append((procedure['end_lineno'], procedure['lineno']))
				self.list_backedges(procedure['body'])
			elif procedure['ast_type'] == "For":
				self.list_backedges(procedure['body'])
			elif procedure['ast_type'] == "If":
				self.list_backedges(procedure['body'])
				self.list_backedges(procedure['orelse'])
		return

	def make_counter_optimal(self):
		for i in range(len(self.backedges)):
			self.M[i] = None
			self.B[i] = None
		change = True
		while change:
			change = False
			iter = (i for i in range(len(self.backedges)) if self.M[i] == None)
			for i in iter:
				for c in self.S:
					M = self.M.copy()
					M[i] = c
					B = self.gen(self.S, M, self.G)
					if B != False:
						self.M[i] = c
						self.B = B.copy()
						change = True
						break
				if change == False:
					c = create_counter_variable()

					S = self.S.copy()
					M = self.M.copy()
					G = self.G.copy()
					B = self.B.copy()

					S.add(c)
					M[i] = c
					check = (c1 for c1 in S if c1 != c)
					for c1 in check:
						G[c1].append(c)
					G['root'].append(c)

					B = self.gen(S,M,G)
					if (B == False):
						continue
					self.S, self.M, self.G, self.B = S, M, G, B
					change = True
					for c1 in self.G.keys():
						if c1 in self.G[c] and c in self.G[c1]:
							tmp = self.G.copy()
							tmp[c].remove(c1) #this seems strange, maybe a typo in the code of the article
							B = self.gen(S,M,tmp).copy()
							if B != False:
								self.G[c1].remove(c)
								self.B = B
		return self.S, self.M, self.G, self.B if all(q for q in range(len(self.backedges)) if self.M[q] is not None) else -1


	def gen(self, S, M, G):
		P = self.instr(self.P, S, M, G)

		#TODO: run invariant generation tool here to generate Iq at any back-edge q in P

		B = []
		lst = (i for i in range(len(self.backedges)) if M[i] is not None)

		for i in lst:
			#TODO: eliminate all counters from Iq except counter and inputs
			#TODO: if Iq -> M(q) <= u -> B = B[q <- u] else false
			pass
		return B

	def instr(self, P, S, M, G): #P is the function body
		dest = G['root']
		for var in dest:
			command = var+" = 0"
			P = [ast.parse(command)] + P
		for i in range(len(M)):
			block = self.get_backedge_struct(P,i)
			command = M[i]+" = "+M[i]+"+1"
			block = block + [ast.parse(command)] #block is passed by reference, so any change on it is reflected on P

			lst = (obj for obj in G[M[i]] if M[i] in G.keys())
			for obj in lst:
				command = obj+" = 0"
				block = block + [ast.parse(command)] #check if references don't mess up

	def get_backedge_struct(self, P, var):
		if isinstance(P,list):
			for i in range(len(P)):
				self.get_backedge_struct(P[i], var)
		else:
			if P['ast_type'] == "While":
				backedge = (i for i in range(len(self.M)) if self.M[i] == var and P['end_lineno'] == self.backedges[i][0])
				
		return

