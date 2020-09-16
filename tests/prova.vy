struct Funder :
  sender: int128
  value: uint256

#@private
#def insertion_sort():
#        a: int128 = [5,2,10]
#        c: int128 = 1
#        x = 3
#        while c < x:
#                i: int128 = c-1
#                b: int128 = c
#                while i>=0:
#                        if a[b] < a[i]:
#                                tmp: int128 = a[i]
#                                a[i] = a[b]
#                                a[b] = tmp
#                                b -= 1
#                        i -= 1
#                c += 1

@private
def fibonacci(limit: int128):
	res: int128 = 0
	limi: int128 = limit
	first: int128 = 0
	second: int128 = 1
	tmp : int128 = 0
	if limit == 0:
		res = 0
	elif limit == 1:
		res = 1
	else:
		limi -= 2
		while limi >= 0:
			tmp = second
			second = first + second
			first = tmp
			limi -= 1
		res = second


@private
def binary_search(item: int128):
	lst: int128[9] = [2,5,9,15,44,67,111,423,543]
	begin: int128 = 0
	end: int128 = 9
	middle: int128 = 0
	r: int128 = -1
	while begin <= end and r < 0:
		middle = (begin+end)/2 #this gives problems, see TODO file
		if lst[middle] == item:
			r = 0
		else:
			if item > lst[middle]:
				begin = middle+1
			else:
				end = middle-1


#def cammini_minimi(root: int128):
#	graph: int128 = [[1,0,0],[1,0,1],[1,1,0]]
#	d: int128 = [-1,-1,-1]
#	b: bool = [0,0,0]
#	d[root] = 0
#	b[root] = true
	

@private
def knapsack():
	v: int128[2] = [5,2]
	w: int128[2] = [3,1]
	n: int128 = 2
	W: int128 = 2

	m: int128[2][2] = [[0,0],[0,0]]

	j: int128 = 0
	i: int128 = 1

	while i < n:
		while j < W:
			p: int128 = i-1
			tmp: int128 = j-w[i]
			if w[i] > j:
				m[i][j] = m[p][j]
			else:
				if m[p][j] > m[p][tmp] + v[i]:
					m[i][j] = m[p][j]
				else:
					m[i][j] = m[p][tmp] + v[i]
			j += 1
		i += 1
