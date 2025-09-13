from __future__ import division

import networkx as nx
import copy as cp


from infrastructure import display, time
from network import grow2,write_cs, restricted_grow, assign_contribution, gave_pair, GPfree
from analysis import analyze, connectivity,path, sum_contribution
#from campaign import run, C, parallel_run#, actions, run_campaign
from gatekeeper import below_viable

# G=nx.Graph()
# G.add_edges_from([(1,2)])


def seed():
    graph_array = []

    for i in range(8):
        graph_array.append(nx.path_graph(10))

    G = nx.disjoint_union_all(graph_array)

    assign_contribution(G)
    return G

def gp_percentage(G):

    tally = 0
    for vertex in G.nodes(data=False):
        #print vertex
        if G.node[vertex]['gatekeeper'] == 'True':
            #print vertex
            tally += 1
            #print tally

    #print G.number_of_nodes()

    return tally / G.number_of_nodes()

# G = seed()
# print time(grow2, 1000, G, 200)
# print gp_percentage(G)
#
# F = cp.deepcopy(G)
# F = GPfree(F, [])
#
# F = write_cs(F)
# nx.write_graphml(G,'G_version.graphml')
# nx.write_graphml(F,'F_version.graphml')



def so_meta():
    threshold = [100, 200, 300, 400, 500, 1000, 4000]


    for t in threshold:

        print t
        percent_array = []
        for i in range(5):

            G = seed()
            time(grow2, 1000, G, t, 0, 0)
            percent_array.append(gp_percentage(G))

        print sum(percent_array)/len(percent_array)
        print percent_array

    return 0

def more_metar():

    threshold = 500
    for v in range(0,4):
        for p in range(0,4):
            print gave_pair(v,p)[0]
            print gave_pair(v,p)[1]
            percent_array = []

            for i in range(5):
                G = seed()
                time(grow2, 1000, G, threshold, v, p)
                percent_array.append(gp_percentage(G))

            print sum(percent_array)/len(percent_array)
            print percent_array

    return 0

more_metar()
#so_meta()


