import os
import subprocess

class KOAT:

	"""
	get_bounds takes an itrs (which is an array that, for every element, it has a dict containing the itrs code of while loops)
	outputs the same array, but with the bound instead of the itrs code
	"""

	def get_bounds(self, itrs):
		bounds = []
		for func in itrs:
			for k in func.keys():
				b = self.itrs_to_bound(func[k])
				bounds.append(b)
		return bounds

	def itrs_to_bound(self, code):
		file_name = 'tmp.koat'
		f = open(file_name, 'w+', newline="\n")
		f.write(code)
		f.close()

		proc = subprocess.Popen(["koat.native tmp.koat"], stdout=subprocess.PIPE, shell=True)
		(bound, err) = proc.communicate()

		bound = bound.decode('UTF-8')
		bound = bound.split('\n', 1)[0]
		outcome = bound.split('(', 1)[0]

		print("outcome")
		print(outcome)

		if outcome == "YES":
			bound = bound.split(',',2)[1]
			bound = bound[1:]
			bound = bound[:-1]
		elif outcome == "NO":
			bound = "-1"
		elif outcome == "MAYBE":
			bound = "-1"

		print("bound")
		print(bound)

		os.remove("tmp.koat")

		return bound
