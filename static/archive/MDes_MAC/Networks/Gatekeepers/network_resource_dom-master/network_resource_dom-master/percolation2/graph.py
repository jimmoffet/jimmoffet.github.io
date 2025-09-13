__author__ = 'Lihan'
import random as r
import networkx as nx
import numpy as np


from operator import itemgetter

def compute_composite(graph):
    #nx.set_node_attributes(graph,'comp_score','NULL')
    nx.set_node_attributes(graph, 'repo', 'NULL')
    nx.set_node_attributes(graph, 'members', 'NULL')

    #eigenvalue = nx.eigenvector_centrality(graph)
    #e_denom = max(eigenvalue.iteritems(), key=itemgetter(1))[1]

    money_dict = dict()
    for key,data in graph.nodes(data = True):
        money_dict[key] = float(data['money'])
    #m_denom = max(money_dict.iteritems(), key=itemgetter(1))[1]

    for vertex in graph.nodes():

        #e_norm = eigenvalue.get(vertex)/e_denom
        #m_norm = float(graph.node[vertex]['money'])/m_denom
        #graph.node[vertex]['comp_score'] = str(1/(e_norm+m_norm))
        if 'club' in graph.node[vertex]:
            del graph.node[vertex]['club']

        graph.node[vertex]['repo'] = graph.node[vertex]['money']
    return graph

def assign_contribution(P,v,p):
    i = 0
    values = gave_pair(v,p)[0]
    probabilities = gave_pair(v,p)[1]
    for vertex in P.nodes():
        P.node[vertex]['money'] = str(sample(values,probabilities))#str(sample(distribution,probability))

        #graph.add_node(new_vertex, {'money': str(sample(values,probabilities)), 'contribution': str(0)})
        i+=1
    return 0


def getDense(H, num):
    r.seed(0)
    for i in range(num+1):
          first_node = r.choice(H.nodes())                  # pick a random node
          possible_nodes = set(H.nodes())
          neighbours = H.neighbors(first_node) + [first_node]
          possible_nodes.difference_update(neighbours)    # remove the first node and all its neighbours from the candidates
          second_node = r.choice(list(possible_nodes))      # pick second node
          H.add_edge(first_node, second_node)
    return H


from numpy.random import random_sample

def sample(values,probabilities):
    bins = np.add.accumulate(probabilities)
    #print bins
    return values[np.digitize(random_sample(), bins)]

def gave_pair( switch1, switch2 ):

    output = []
    values = [np.array([2, 2, 2, 2]),
              np.array([0, 8, 675, 3500]), #original
              np.array([2, 8, 675, 3500]),
              np.array([0, 1, 700, 700]),
              np.array([50, 50, 50, 50])]

    output.append(values[switch1])
    probabilities = [np.array([0.50, 0.3, 0.2, 0.1]),
                     np.array([0.80, 0.18, 0.01, 0.01]),
                     np.array([0.90, 0.0965, 0.003, 0.0005]), #original
                     np.array([0.95, 0.045, 0.005, 0.0000])]
    output.append(probabilities[switch2])
    return output

def init():
    #g = graph.copy()
    #r.seed(0)

    threshold = [34,17,7]
    extra_edges = [0, 62, 202]

    #P = nx.karate_club_graph()
    P = nx.read_graphml(path = 'C:\Users\Lihan\Documents\WORD\FULBRIGHT\\network theory\percolation\james.graphml')#nx.fast_gnp_random_graph(500,0.017)
    #P.add_node(35)
    distribution = [[35, 20, 5, 3, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [11, 10, 5, 3, 3, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    [2 for i in range(40)]]

    d = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 10, 10, 10]
    #getDense(P,202)
    #graph.add_node(new_vertex, {'money': str(sample(values,probabilities)), 'contribution': str(0)})

    #assign_contribution(P,0,2)
    compute_composite(P)

    #print P.nodes(data=True)
    return P


def dist(G, node, distance):
    snowball = [set([node])]

    innerSet = set()
    outerSet = set()
    for i in range(distance):

        for j in snowball[i]:

            for k in G.neighbors(j):
                #if k != node:  #why is this check needed?
                outerSet.add(k)

        innerSet = innerSet.union(snowball[i])
        snowball.append(outerSet.difference(innerSet))
    return snowball[distance]