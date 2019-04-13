import csv
import numpy
import sys
import pandas as pd
from itertools import islice

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

U={} # 0 means -1, 10 is zero, 20 is +1, 21 is empty
#asdf = pd.DataFrame(keys = ['all possible size four combos of 0-21'])
V={} # 0 means -1, 10 is zero, 21 is +1, 21 is empty

for i in xrange(0,22):
	for j in xrange(0,22):
		for k in xrange(0,22):
			for l in xrange(0,22):
				U[(i,j,k,l)] = [0.0] * 22
				V[(i,j,k,l)] = [0.0] * 22
#print U[(11, 0, 11, 0)]
#sys.exit()

with open('C:\\Users\\jim\\Google Drive\\MDes\\Artificial Intelligence\\out200.csv') as myFile:  
    reader = csv.reader(myFile)
    for row in reader:
        vals = row
        #print vals[64]
        #sys.exit()
        #print vals[128]
    	#print vals[129]
    	cnt = 0
        for i in xrange(8):
        	row = i*8
        	for j in xrange(8):
        		
        		cnt+=1
	        	udex = row + j
	        	vdex = row + j + 64
	        	#print vals[vdex]
	        	cu = int(round(float(vals[udex])*10))
	        	cu = clamp(cu,-10,10)
	        	cv = int(round(float(vals[vdex])*10))
	        	cv = clamp(cv,-10,10)
	        	#print cv
	        	u_minusv = 11 # default, if not updated, indicates a naked vertex
	    		v_minusv = 11
	    		u_plusv = 11
	    		v_plusv = 11
	    		u_minusu = 11
	    		v_minusu = 11
	    		v_plusu = 11
	    		u_plusu = 11

	        	if udex - 1 > 0: # take previous parent along v, skipping initial naked vertex
	        		u_minusv = int(round(float(vals[udex - 1])*10))
	        		u_minusv = clamp(u_minusv,-10,10)
	        		v_minusv = int(round(float(vals[vdex - 1])*10))
	        		v_minusv = clamp(v_minusv,-10,10)

	    		if udex + 1 < 7: # take next parent along v, skipping final naked vertex
	        		u_plusv = int(round(float(vals[udex + 1])*10))
	        		u_plusv = clamp(u_plusv,-10,10)
	        		v_plusv = int(round(float(vals[vdex + 1])*10))
	        		v_plusv = clamp(v_plusv,-10,10)

        		if row - 1 > 0: # take previous parent along u, skipping initial naked vertex
	        		u_minusu = int(round(float(vals[udex + 1 - row])*10))
	        		u_minusu = clamp(u_minusu,-10,10)
	        		v_minusu = int(round(float(vals[vdex + 1 - row])*10))
	        		v_minusu = clamp(v_minusu,-10,10)

        		if row + 1 < 7: # take next parent along u, skipping initial naked vertex
	        		u_plusu = int(round(float(vals[udex + 1 + row])*10))
	        		u_plusu = clamp(u_plusu,-10,10)
	        		v_plusu = int(round(float(vals[vdex + 1 + row])*10))
	        		v_plusu = clamp(v_plusu,-10,10)

    			#print cu
        		U[(u_minusv+10,u_plusv+10,u_minusu+10,u_plusu+10)][cu+10] += 1 # dictionary with tuples for keys whose value is a 21 integer array from -10 to positive 11 (11 represent an edge node with no parent in that direction)
        		V[(v_minusv+10,v_plusv+10,v_minusu+10,v_plusu+10)][cv+10] += 1 # dictionary with tuples for keys whose value is a 21 integer array from -10 to positive 11 (11 represent an edge node with no parent in that direction)
        		

for i in xrange(0,22):
	for j in xrange(0,22):
		for k in xrange(0,22):
			for l in xrange(0,22):
				su = sum(U[(i,j,k,l)][:-1]) # don't sum the final values because they're naked vertex indicators, not counts
				sv = sum(V[(i,j,k,l)][:-1])

				for m in xrange(len(U[(i,j,k,l)])):
					if su > 0:
						U[(i,j,k,l)][m] = U[(i,j,k,l)][m]/su # turn freq count into probability
					if sv > 0:
						V[(i,j,k,l)][m] = V[(i,j,k,l)][m]/sv # turn freq count into probability
				for m in xrange(len(U[(i,j,k,l)])):
					if m == 0:
						U[(i,j,k,l)][m] = (U[(i,j,k,l)][m] + U[(i,j,k,l)][m+1])/2 # kernel [0.5 0.5] on first vertice in row
						V[(i,j,k,l)][m] = (V[(i,j,k,l)][m] + V[(i,j,k,l)][m+1])/2 # kernel [0.5 0.5] on first vertice in row
					elif m == 21:
						U[(i,j,k,l)][m] = (U[(i,j,k,l)][m-1] + U[(i,j,k,l)][m])/2 # kernel [0.5 0.5] on last vertice in row
						V[(i,j,k,l)][m] = (V[(i,j,k,l)][m-1] + V[(i,j,k,l)][m])/2 # kernel [0.5 0.5] on last vertice in row
					elif m == 20:
						foo = 'foo'
					else: # leave value 11 (index 21) val alone because its just a flag naked vertices, not a count   
						U[(i,j,k,l)][m] = (U[(i,j,k,l)][m-1] + U[(i,j,k,l)][m+1])/2 # sobel kernel [-1 0 1]
						V[(i,j,k,l)][m] = (V[(i,j,k,l)][m-1] + V[(i,j,k,l)][m+1])/2 # sobel kernel [-1 0 1]


testList = list(islice(U.iteritems(), 2000))
count = 0
for l in testList:
	count += sum(l)

print l
