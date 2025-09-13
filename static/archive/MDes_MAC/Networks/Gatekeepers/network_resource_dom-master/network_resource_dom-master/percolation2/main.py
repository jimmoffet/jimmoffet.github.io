from __future__ import division

from graph import init
from auxiliary import display, time

from table import make_table, return_gp, update_table
from get_v2 import next_v

from percolation2 import build_D, find_neighbors

import networkx as nx
#
import random as r

#r.seed(0)

def percolate():
    threshold = 10000

    P = init()
    #P = nx.read_graphml(path = 'C:\Users\Lihan\Documents\WORD\FULBRIGHT\\network theory\percolation\james.graphml')
    #D = nx.DiGraph()
    D = dict()

    table = make_table(P)
    gp = []
    i = 0

    while 1 == 1:#for i in range(len(P.nodes())):
        i += 1

        v_to_add = next_v(table)
       # time(next_v,1,table)
        # if i % 5 == 0:
        #      print "%d %% left" %(len(table)*100/P.number_of_nodes())
        #      print "||%s||p: %d %%||" %(v_to_add, table[v_to_add][4]*100)
        #      if gp:
        #          print "Found GP    " + str(gp)

        #if i == 700:
            #display(table)

        if not v_to_add: #v_to_add = false if active table is too small
            break

        #D = make_Di(P,D,v_to_add)
        D = build_D(P,D,v_to_add)
        #time(build_D,1,P,D,v_to_add)
        nbr = find_neighbors(P,D,v_to_add)

        del table[v_to_add]

        update_table(table, nbr,P,D,threshold)
        #time(update_table,1,table, nbr,P,D,threshold)
        # scan table for GP, remove them from table
        new_gp = return_gp(table)
        if new_gp:
            gp += new_gp
            for v in new_gp:
                del table[v]
        #

        #table[v_to_add] = update_v(P,D,threshold,v_to_add)
        #print v_to_add
    print gp, len(gp)

    #nx.write_graphml(D,'digraph.graphml')
    nx.write_graphml(P, 'original.graphml')

    return gp

import itertools

def meta(num_runs):
    gp = []

    for run in range(num_runs):
        gp.append(percolate())

    gp.sort()
    print list(gp for gp,_ in itertools.groupby(gp))
    return 0

#percolate()
time(percolate, 1)
#time(meta,1,9)

#display(table)






#for v in P.nodes():
#    if table[v][0] == 0:
#        table[v] = update_v(P,D,threshold,v)


#display(table)
#print P.neighbors(5)



# for i in range(500):
#
#     current = step(P,D,threshold, gp)
#
#
#     if len(D.nodes()) + len(gp) == len(P.nodes())-5:
#         break
#
#     if type(current) == int:
#         #print current
#         gp.append(current)
#         #current = step(P,D,threshold,gp)
#         #if len(D.nodes()) + len(gp) == len(P.nodes())-5:
#         #    break
#
#     #print len(D.nodes()),len(gp),len(P.nodes())-5
#
#     else:
#         D = current
#
# print gp



#for v,dat in D.nodes(data=True):
    #print v,dat



# P = nx.karate_club_graph()
#
# G = init(P).copy()
# print G.nodes(data=True)
# nx.write_graphml(G,'zach.graphml')
#
# #print run(P,threshold[0])
#
# #time(run, 1, P, 7)
#
# #calculate composite score