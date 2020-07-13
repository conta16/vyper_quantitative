import matrix_utils
from vyper.exception import VariableDeclarationException
#from inspect import currentframe, getframeinfo

class mwp:

	def __init__(self)->None:
		self.context = {}
		self.matrix = []
                #self.frameinfo = getframeinfo(currentframe()) #if variable depends on op other than =, +, *, then use frameinfo to update self.context[variable_name] value to line number

	def new_variable(self, name, value):
		if name not in self.context.keys():
			self.context[name] = value #save state (1 fine 0 error in reduction for variable) instead of vector
			#self.matrix = matrix_utils.extend_matrix(self.matrix, self.context[name])

	def assign_reduction(self, operation):
		

	def binop_reduction(self, left, right):
		return matrix_utils.merge_vectors(left, right)




        def expr_reduction(self, operation):
                if operation.ast_type == "BinOp":
                        boundedr = expr_reduction(operation.right)
                        boundedl = expr_reduction(operation.left)
			if (boundedr and boundedl and (operation.op.ast_type == "Add" or operation.op.ast_type == "Mult") == 0):
				return 0
                elif (operation.ast_type == "Name" and operation.id in self.context.keys()) or operation.ast_type == "Int":
			if (operation.id and self.context[operation.id] == 0):
                        	return 0
			return 1
                elif operation.ast_type == "Name" and operation.id not in self.context.keys():
                        raise VariableDeclarationException(operation.id + " is not defined. This is probably a compiler bug, please report")

		#create variable m-flow vectors (change return 1 with return vector)

		left = matrix_utils.get_vector(operation.left.id if operation.left.ast_type == "Name" else "number")
		right = matrix_utils.get_vector(operation.right.id if operation.right.ast_type == "Name" else "number")

		return self.binop_reduction(left, right)


	def matrix_reduction(self,operation):
		if isinstance(operation,list):
			skip = skip()
			for i in operation:
				skip = matrix_utils.mult(skip, matrix_reduction(operation[i]))
		return skip

		elif operation.ast_type == "Assign": #and operation.target.id not in self.context.keys()
			bounded = expr_reduction(operation.value)
			if not bounded:
				self.new_variable(operation.target.id, 0) #maybe this assign case can be moved to another function. if rule_reduction returns 0 eventually, then transform the matrix into skip
				return skip()
			else:
				self.new_variable(operation.target.id, bounded)
				return add_vector_to_skip(operation.target.id, bounded)

		elif operation.ast_type == "If":
			body = matrix_reduction(operation.body)
			orelse = matrix_reduction(operation.orelse)
			return matrix_utils.sum(body, orelse)

		elif operation.ast_type == "For":
			#create iter variable
			#recursively call body
			#apply closure
			#return closed matrix + vector p

		elif operation.ast_type == "While":
			#define
