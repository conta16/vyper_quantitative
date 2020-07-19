import numpy as np

class Matrix_utils:

	def sum(self,m1,m2):
		if len(m1) == len(m2) and len(m1[0]) == len(m2[0]):
			s = self.create_zero_matrix(len(m1), len(m1[0]))
			for row in range(len(m1)):
				for col in range(len(m1[row])):
					if m1[row][col] > m2[row][col]:
						s[row][col] = m1[row][col]
					else:
						s[row][col] = m2[row][col]
			return np.copy(s)
		else:
			print("number of rows and cols different")
			return -1

	def mult(self,m1,m2):
		if len(m1[0]) == len(m2):
			m = self.create_zero_matrix(len(m1), len(m2[0]))
			for row in range(len(m1)):
				for col in range(len(m2[0])):
					for k in range(len(m2)):
						if m1[row][k] != 0 and m2[k][col] != 0:
							if m1[row][k] > m2[k][col] and m1[row][k] > m[row][col]:
								m[row][col] = m1[row][k]
							elif m2[k][col] >= m1[row][k] and m2[k][col] > m[row][col]:
								m[row][col] = m2[k][col]
			return np.copy(m)
		else:
			print("can't multiply matrix with different num of row and col")
			return -1

	def create_zero_matrix(self,rows, cols):
		#return [([0]*cols) for i in range(rows)]
		return np.zeros((rows,cols), dtype=int)

	def eq_matrix(self,right, left):
		or_lenr_right = len(right)
		or_lenr_left = len(left)
		or_lenc_right = len(right[0])
		or_lenc_left = len(left[0])

		if len(right) < len(left):
			right = np.vstack((right, np.array(np.zeros((len(left)-len(right), len(right[0])),dtype=int))))
		elif len(left) < len(right):
			left = np.vstack((left, np.array(np.zeros((len(right)-len(left), len(left[0])),dtype=int))))

		if len(right[0]) < len(left[0]):
			right = np.hstack((right, np.array(np.zeros((len(right), len(left[0])-len(right[0])),dtype=int))))
		elif len(left[0]) < len(right[0]):
			left = np.hstack((left, np.array(np.zeros((len(left), len(right[0])-len(left[0])),dtype=int))))

		while(or_lenr_right < len(right)):
			right[or_lenr_right][or_lenr_right] = 1
			or_lenr_right+=1

		while(or_lenr_left < len(left)):
			left[or_lenr_left][or_lenr_left] = 1
			or_lenr_left+=1

		return np.copy(right),np.copy(left)


	def skip(self, num):
		return np.identity(num)

	def substitute_column(self, matrix, column, pos):
		matrix[:, pos] = column
		return np.copy(matrix)

	def get_closure(self, matrix):
		old_s = np.array([])
		s = self.skip(len(matrix[0]))
		cmatrix = np.copy(s)
		while not np.array_equal(old_s, s):
			old_s = np.copy(s)
			cmatrix = self.mult(cmatrix, matrix)
			s = self.sum(s, cmatrix)
		return np.copy(s)

	def is_lmatrix_valid(self, matrix):
		check = self.skip(len(matrix[0]))
		return np.array_equal(np.diag(matrix), np.diag(check))

	def make_matrix_loop(self, matrix, pos):
		p = set()
		for i in range(len(matrix)):
			for j in range(len(matrix[0])):
				if matrix[i][j] == 3:
					p.add(j)
		for i in p:
			matrix[pos][i] = 3
		return np.copy(matrix)
