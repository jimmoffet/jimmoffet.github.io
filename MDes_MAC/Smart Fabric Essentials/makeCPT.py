import csv
import numpy
import sys
import pandas as pd

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

U={} # 0 means -1, 10 is zero, 20 is +1, 21 is empty
#asdf = pd.DataFrame(keys = ['all possible size four combos of 0-21'])
V={} # 0 means -1, 10 is zero, 21 is +1, 21 is empty

for i in xrange(-10,12):
	for j in xrange(-10,12):
		for k in xrange(-10,12):
			for l in xrange(-10,12):
				U[(i,j,k,l)] = [0] * 22
				V[(i,j,k,l)] = [0] * 22

with open('C:\\Users\\jim\\Google Drive\\MDes\\Artificial Intelligence\\out200.csv') as myFile:  
    reader = csv.reader(myFile)
    for row in reader:
        vals = row
        print vals[64]
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
	        	u_minusv = 11
	    		v_minusv = 11
	    		u_plusv = 11
	    		v_plusv = 11
	    		u_minusu = 11
	    		v_minusu = 11
	    		v_plusu = 11
	    		u_plusu = 11

	        	if udex - 1 > 0:
	        		u_minusv = int(round(float(vals[udex - 1])*10))
	        		u_minusv = clamp(u_minusv,-10,10)
	        		v_minusv = int(round(float(vals[vdex - 1])*10))
	        		v_minusv = clamp(v_minusv,-10,10)

	    		if udex + 1 < 7:
	        		u_plusv = int(round(float(vals[udex + 1])*10))
	        		u_plusv = clamp(u_plusv,-10,10)
	        		v_plusv = int(round(float(vals[vdex + 1])*10))
	        		v_plusv = clamp(v_plusv,-10,10)

        		if row - 1 > 0: 
	        		u_minusu = int(round(float(vals[udex + 1 - row])*10))
	        		u_minusu = clamp(u_minusu,-10,10)
	        		v_minusu = int(round(float(vals[vdex + 1 - row])*10))
	        		v_minusu = clamp(v_minusu,-10,10)

        		if row + 1 < 7:
	        		u_plusu = int(round(float(vals[udex + 1 + row])*10))
	        		u_plusu = clamp(u_plusu,-10,10)
	        		v_plusu = int(round(float(vals[vdex + 1 + row])*10))
	        		v_plusu = clamp(v_plusu,-10,10)

    			#print cu
        		U[(u_minusv,u_plusv,u_minusu,u_plusu)][cu+10] += 1 # dictionary with tuples for keys
        		V[(v_minusv,v_plusv,v_minusu,v_plusu)][cv+10] += 1 # dictionary with tuples for keys
        		## need to initialize with keys as below, all size 4 combos of 0-21
        		

#print U(11,0,11,0)