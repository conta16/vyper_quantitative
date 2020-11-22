struct Funder :
  sender: int128
  value: uint256

# Beneficiary receives money from the highest bidder
beneficiary: public(address)
auctionStart: public(uint256)
auctionEnd: public(uint256)

# Current state of auction
highestBidder: public(address)
highestBid: public(uint256)

# Set to true at the end, disallows any change
ended: public(bool)

# Keep track of refunded bids so we can follow the withdraw pattern
pendingReturns: public(int128)


@private
def __init__(_beneficiary: address, _bidding_time: uint256):
    self.beneficiary = _beneficiary
    self.auctionStart = block.timestamp
    self.auctionEnd = self.auctionStart + _bidding_time

@private
#def insertion_sort():
#        a: int128[3] = [5,2,10]
#        c: int128 = 1
#        x: int128 = 3
#        while c < 3:
#        i: int128 = c-1
#        b: int128 = c
      #  while i>=0:
#        if a[b] < a[i]:
#         tmp: int128 = a[i]
#         a[i] = a[b]
#         a[b] = tmp
#         b -= 1
#         i -= 1
#         c += 1
#        return a



#@private
#def f(limit:int128):
#        l: int128 = limit
#        res: int128 = 0
#        first: int128 = 0
#        second: int128 = 1
#        tmp : int128 = 0
#        while(True):
#         tmp = second
#         second = first + second
#         first = tmp
#         l -= 1


#@private
#def fibonacci(limit: int128):
#        res: int128 = 0
#        first: int128 = 0
#        second: int128 = 1
##        l: int128 = limit
 #       tmp : int128 = 0
  #      if l == 0:
 #               res = 0
 #       elif l == 1:
 #               res = 1
 #       else:
 #               l -= 2
 #               while l > 0:
 #                       tmp = second
 #                       second = first + second
 #                       first = tmp
 #                       l -= 1
 #               res = second

#@private
#def binary_search(item: int128):
#	lst: int128[9] = [2,5,9,15,44,67,111,423,543]
#	begin: int128 = 0
#	end: int128 = 9
#	middle: int128 = 0
#	r: int128 = -1
#	while begin <= end and r < 0:
#		middle = end - begin #this gives problems, see TODO file
#		if lst[middle] == item:
#			r = 0
#		else:
#			if item > lst[middle]:
#				begin = middle+1
#			else:
#				end = middle-1

@private
def s():
        lst: int128[9] = [2,5,9,15,44,67,111,423,543]
        n: int128 = 9
        h: int128 = 1
        p: int128 = lst[h]
#        while h >= 1:
        i: int128 = h+1
                #while i < n:
        tmp: int128 = lst[i]
        j: int128 = i
                        #while j > h: # and lst[j-h] > tmp:
                        #       lst[j] = lst[j-h]
                        #       j = j - h
        lst[j] = tmp
        i += 1
        h = h-3

@private
def shellsort():
	lst: int128[9] = [2,5,9,15,44,67,111,423,543]
	n: int128 = 9
	h: int128 = 1
	p: int128 = lst[h]
	while h <= n:
		h = 3*h + 1
	h = h/3
	while h >= 1:
		i: int128 = h+1
		while i < n:
			tmp: int128 = lst[i]
			j: int128 = i
			#while j > h: # and lst[j-h] > tmp:
			#	lst[j] = lst[j-h]
			#	j = j - h
			lst[j] = tmp
			i += 1
		h = h-3
	return

#def f():
#	h: int128 = 15
#	while h > 0:
#		while
#		h = h/2	


#def cammini_minimi(start: int128, end: int128):
#	graph: int128 = [[1,0,0,3],[2,1,5,0],[5,1,1,3],[7,0,4,1]]
#	min: int128 = 0
#	i: int128 = 0
#	while ():
#		if (graph[start][i] == 0):
#			i += 1
#		else:
			
	

#@private
#def knapsack():
#	v: int128[2] = [5,2]
#	w: int128[2] = [3,1]
#	n: int128 = 2
#	W: int128 = 2
#
#	m: int128[2][2] = [[0,0],[0,0]]
#
#	j: int128 = 0
#	i: int128 = 1
#
#	while i < n:
#		while j < W:
#			p: int128 = i-1
#			tmp: int128 = j-w[i]
#			if w[i] > j:
#				m[i][j] = m[p][j]
#			else:
#				if m[p][j] > m[p][tmp] + v[i]:
#					m[i][j] = m[p][j]
#				else:
#					m[i][j] = m[p][tmp] + v[i]
#			j += 1
#		i += 1


#@private
#def func():
#	b: bool = 0
	
#	while not b:
		
