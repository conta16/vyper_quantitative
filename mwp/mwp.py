from vyper.mwp.matrix_utils import Matrix_utils
import numpy as np
from vyper.mwp.const import Const
#from vyper.exception import VariableDeclarationException
#from inspect import currentframe, getframeinfo

class Mwp:

	def __init__(self)->None:
		self.context = {}
		self.num_constants = 0
		self.matrix = []
		self.utils = Matrix_utils()
		self.const = Const()
		#print(globals.init())
                #self.frameinfo = getframeinfo(currentframe()) #if variable depends on op other than =, +, *, then use frameinfo to update self.context[variable_name] value to line number

	def new_variable(self, name, value):
		if name not in self.context.keys():
			self.context[name] = value #save state (1 fine 0 error in reduction for variable) instead of vector
			#self.matrix = matrix_utils.extend_matrix(self.matrix, self.context[name])
		else:
			#VariableDeclarationException(name+" is already declared")
			print(str(name)+" is already declared")

	def new_constant_variable(self, op):
		self.num_constants+=1
		if "c"+str(self.num_constants) in self.context.keys(): #c needs to be changed with something that can't be used as a normal variable
			self.new_constant_variable(op)
		else:
			op['id'] = "c"+str(self.num_constants)
			self.new_variable(op['id'], 1)
		return

	def generate_vector(self, name):
		array = np.array([], dtype=int)
		l = list(self.context)
		for i in range(len(self.context)):
			if i == l.index(name):
				array = np.append(array, self.const.DEF_M)
			else:
				array = np.append(array, self.const.DEF_NOFLOW)
		return array

	def binop_reduction(self, right, left):
		right = np.array(right) #temporary convert list to np array
		left = np.array(left) #temporary convert list to np array
		right,left = self.utils.eq_matrix(right,left)
		right[right>0] = 3
		return self.utils.sum(left, right)

	def expr_reduction(self, operation):
		if operation['ast_type'] == "BinOp" and (operation['op']['ast_type'] == "Add" or operation['op']['ast_type'] == "Mult"):
			boundedr = self.expr_reduction(operation['right'])
			boundedl = self.expr_reduction(operation['left'])
			if (boundedr is None or boundedl is None == 1):
				return None

			return self.binop_reduction(boundedr, boundedl)
		elif operation['ast_type'] == "BinOp" and (operation['op']['ast_type'] != "Add" and operation['op']['ast_type'] != "Mult"):
			return None
		elif (operation['ast_type'] == "Name" and operation['id'] in self.context.keys()) or operation['ast_type'] == "Int" or operation['ast_type'] == "NameConstant":
			if (operation['ast_type'] == "Int" or operation['ast_type'] == "NameConstant"):
				self.new_constant_variable(operation)
			if (operation['id'] and self.context[operation['id']] == 0):
				return None
			return [self.generate_vector(operation['id'])]
		elif operation['ast_type'] == "Name" and operation['id'] not in self.context.keys():
			raise VariableDeclarationException(operation['id'] + " is not defined. This is probably a compiler bug, please report")


	def matrix_reduction(self, operation):
		if isinstance(operation,list):
			skip = self.utils.skip(1)
			for i in operation:
				m = self.matrix_reduction(i)
				if isinstance(m, int) and m == -1:
					skip = m
					break
				else:
					m, skip = self.utils.eq_matrix(m, skip)
					skip = self.utils.mult(skip, m)
			print(self.context)
			return skip

		elif operation['ast_type'] == "Assign" or operation['ast_type'] == "AnnAssign" or operation['ast_type'] == "AugAssign": #and operation.target.id not in self.context.keys()
			bounded = self.expr_reduction(operation['value'])
			if bounded is None:
				self.new_variable(operation['target']['id'], 0)
				return self.utils.skip(1) #if expression contains op other than plus and mult, parse it to skip (aka it does nothing)
			else:
				if operation['target']['id'] not in self.context.keys():
					self.new_variable(operation['target']['id'], 1)
					bounded = [np.hstack((np.array(bounded[0]), np.array([0])))]

				#m, bounded = self.utils.eq_matrix(self.utils.skip(len(bounded[0])), bounded)
				return self.utils.substitute_column(self.utils.skip(len(bounded[0])), bounded[0], list(self.context).index(operation['target']['id']))

		elif operation['ast_type'] == "If":
			body = self.matrix_reduction(operation['body'])
			orelse = self.matrix_reduction(operation['orelse'])
			return self.utils.sum(body, orelse)

		elif operation['ast_type'] == "For":
			if operation['iter']['ast_type'] == "Call":
				if operation['iter']['args'][0]['ast_type'] == "Int":
					self.new_constant_variable(operation['iter']['args'][0]) #TODO: now it only manages range(var) or range(int)
			body = self.utils.get_closure(self.matrix_reduction(operation['body']))
			if self.utils.is_lmatrix_valid(body):
				pmatrix = self.utils.make_matrix_loop(np.copy(body), list(self.context).index(operation['iter']['args'][0]['id']))
				#print("pmatrix")
				#print(body)
				#print(pmatrix)
				#print(self.context)
				return pmatrix
			else:
				return -1

		elif operation['ast_type'] == "While":
			body = self.utils.get_closure(self.matrix_reduction(operation['body']))
			if self.utils.is_lmatrix_valid(body) and self.const.DEF_P not in body:
				return body
			else:
				return -1
