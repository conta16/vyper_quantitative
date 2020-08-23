import os
import subprocess

class KOAT:

	"""
	get_bounds takes an itrs (which is an array that, for every element, it has a dict containing the itrs code of while loops)
	outputs the same array, but with the bound instead of the itrs code
	"""

#	def __init__(self):
#		pass

	def get_bounds(self, itrs):
		for func in itrs:
			for k in func.keys():
				func[k] = self.itrs_to_bound(func[k])

	def itrs_to_bound(self, code):
		#code = code.decode('unicode_escape')
		file_name = 'tmp.koat'
		f = open(file_name, 'w+', newline="\n")
		f.write(code)
		f.close()

		proc = subprocess.Popen(["koat.native tmp.koat"], stdout=subprocess.PIPE, shell=True)
		(bound, err) = proc.communicate()
		#bound = os.popen('koat.native tmp.koat').read()
		#os.remove('tmp.koat')

		print(bound)
		bound = bound.decode('UTF-8')
		bound = bound.split('\n', 1)[0]
		outcome = bound.split('(', 1)[0]

		if outcome == "YES":
			bound = bound.split(',',2)[1]
			bound = bound[1:]
			bound = bound[:-1]
		elif outcome == "NO":
			bound = "-1"
		elif outcome == "MAYBE":
			bound = "Couldn't calculate"

		return bound
