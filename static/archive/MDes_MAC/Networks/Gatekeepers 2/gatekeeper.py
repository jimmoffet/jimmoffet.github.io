__author__ = 'Lihan'
from infrastructure import time
import itertools as it
import networkx as nx
from copy import deepcopy
from operator import attrgetter,itemgetter
from sets import Set
import itertools as it
#from itertools import chain, combinations
from numpy import random
import random as r
from collections import defaultdict
from copy import deepcopy


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

#node_connected_component(G, node):
#   return list of nodes in component of G containing 'node'

def threshhold_check(G, component, threshhold):

    sigma_sum = 0
    for vertex in component:
        #print vertex
        #print G.node[vertex]
        sigma_sum += float(G.node[vertex]['money'])

    return sigma_sum < threshhold

def below_viable(G, new_node, threshhold):

    c_nodes = nx.node_connected_component(G, new_node)
    #new_node is included in component nodes
    return threshhold_check(G, c_nodes, threshhold)

W  = nx.path_graph(30)

#P = nx.petersen_graph()
P = nx.karate_club_graph()

distribution = [1, 2, 1, 1, 2, 1, 1, 3, 10, 1, 1, 2, 1, 1, 2, 1, 1, 3, 10, 1, 1, 2, 1, 1, 2, 1, 1, 3, 10, 1, 1, 1, 1, 1]
#r.shuffle(distribution)
for vertex in P.nodes():
    P.node[vertex]['money'] = str(distribution.pop())#str(sample(distribution,probability))






def minimal_subset(subsets):

    s = subsets
    #s.sort(key = len)

    repet = []
    for pos1 in range(len(s)):
        for pos2 in range(pos1+1, len(s)):
            if set(s[pos1]).intersection(set(s[pos2])) == set(s[pos1]):
                repet.append(s[pos2])

    lol = [x for x in s if x not in repet]
    return lol
s = [[1, 2], [2, 3], [1,2,3], [1,2,5], [1,3,5], [1,5,4,6]]

def validate_rich(G, threshold):

    rich = []
    money = nx.get_node_attributes(G,'money')
    #money1 = [float(i) for i in money.values()]
    #L = sorted(money1, reverse = True)

    for node in money:
        if float(money[node]) >= threshold:
            #print node
            #print money[node]
            rich.append(node)

    for node_index in rich:
        G.remove_node(node_index)

    print nx.number_of_nodes(G)

    return rich

S = [1,8,10,675,3500]

def gen_partitions_ms(n):
    """Generate all partitions of integer n (>= 0).

    Each partition is represented as a multiset, i.e. a dictionary
    mapping an integer to the number of copies of that integer in
    the partition.  For example, the partitions of 4 are {4: 1},
    {3: 1, 1: 1}, {2: 2}, {2: 1, 1: 2}, and {1: 4}.  In general,
    sum(k * v for k, v in a_partition.iteritems()) == n, and
    len(a_partition) is never larger than about sqrt(2*n).

    Note that the _same_ dictionary object is returned each time.
    This is for speed:  generating each partition goes quickly,
    taking constant time independent of n.
    """

    if n < 0:
        raise ValueError("n must be >= 0")

    if n == 0:
        yield {}
        return

    ms = {n: 1}
    keys = [n]  # ms.keys(), from largest to smallest
    yield ms

    while keys != [1]:
        # Reuse any 1's.
        if keys[-1] == 1:
            del keys[-1]
            reuse = ms.pop(1)
        else:
            reuse = 0

        # Let i be the smallest key larger than 1.  Reuse one
        # instance of i.
        i = keys[-1]
        newcount = ms[i] = ms[i] - 1
        reuse += i
        if newcount == 0:
            del keys[-1], ms[i]

        # Break the remainder into pieces of size i-1.
        i -= 1
        q, r = divmod(reuse, i)
        ms[i] = q
        keys.append(i)
        if r:
            ms[r] = 1
            keys.append(r)

        yield ms

# for p in gen_partitions_ms(200):
#     print p

H = [1,3,4]

import sys
sys.setrecursionlimit(10000) # 10000 is an example, try with different values

def partitions_tuple(n):
    # tuple version
    if n == 0:
        yield ()
        return



    for p in partitions_tuple(n-1):
        #if set(p)&set(H):
        #if set((h,)+p) <= set(H):
            yield (1, ) + p

            #for h in H:
            if p and (len(p) < 2 or p[1] > p[0]):
                yield (p[0] + 1, ) + p[1:]

def big_partition(n):
    #for h in H:
    for p in gen_partitions_ms(n):
            #if set(p) <= set(H):
        #print p
        total = 0
        for num in p:
           total += num
        #print total
    return 0



#big_partition(15)

#print time(big_partition,1200,1)

# for p in partitions_tuple(15):
#     print p

#print time(partitions_tuple, 2100, 1)

#print refine_partition(200, S)
#print partition(10)

def coin_change(threshold,distribution): #takes in threshhold value and discrete distribution values, returns integer partitions
    i_partitions = []

    return 0




def search(): #returns a list with nodes of certain $
    return 0

def viable_sets(): # takes in graph, a node, integer partitions, and returns
    return 0

def iterate_nodes():
    return 0


def hitting_set(): #takes a set of sets and returns a minimum gatekeeper set
    return 0

#include nodes that are self viable then delete them


def powerset(iterable):
    s = list(iterable)
    return it.chain.from_iterable(it.combinations(s, r) for r in range(len(s)+1))

def viableSubgraphs(G, threshold):
    ps = list(powerset(xrange(G.number_of_nodes())))    
    connectedSets = Set()
    for n in ps:
        x = 0
        for l in n:
            x+=int(G.node[l]['money'])
            #if x > threshold: #is this actually faster than not having it?
            #    break
        if x >= threshold:
            g = G.subgraph(n)
            if len(n) > 0:
                if nx.is_connected(g):
                    fs = frozenset(g.nodes())
                    connectedSets.add(fs)
                #    print str(n) + ' is connected'
                #else:
                #    print str(n) + ' is not connected'
    return connectedSets

threshold = 5      
allconnectedsets = viableSubgraphs(P,threshold)
#print len(allconnectedsets)

smvs = deepcopy(allconnectedsets)

for s in allconnectedsets:
    for t in allconnectedsets:
        if t > s:
            smvs.discard(t)
    
#print smvs

goal = len(smvs)
print 'goal is ' + str(goal)

vdict = {}

for v in P.nodes():
    vsets = Set()
    for s in smvs:
        if v in s:
            vsets.add(s)
    vdict[v] = vsets
    
#print vdict
winners = Set()
found = False

for i in xrange(P.number_of_nodes()):
    combolist = it.combinations('0123456789', i)
    for combo in combolist:
        combocount = Set()
        for v in combo:
            for s in vdict[int(v)]:
                combocount.add(s)
        #print str(combo) + ' has length ' + str(len(combocount))
        if len(combocount) == goal:
            winners.add(combo)
            found = True
    if found:
        #print 'A WINNER HAS BEEN FOUND'
        break
    
print winners
i = 0
for w in winners.pop():
    for x in w:
        P.node[int(x)]['gatekeeper'] = 'True'
                   
            

                
nx.write_graphml(P,'P.graphml')

#for v in P.nodes():
#    winners1[v] = 0
#    for s in smvs:
#        if v in s:
#            winners1[v]+=1
#    print winners1[v]
#    if winners1[v] == 12:
#        print 'win'


#winners2 = {}
#d = ()
#for v in P.nodes():
#    for n in P.nodes():
#        vsets = Set()
#        nsets = Set()
#        asets = Set()
#        c = (v,n)
#        for s in smvs:
#            if v in s:
#                vsets.add(s)
#            if n in s:
#                nsets.add(s)
#        asets = vsets.union(nsets)
#        count = len(asets)
#        if count == goal:
#            d+=c
#            #winners2[c] = len(asets)
#e = Set(d)
#print e
#for x in e:
#    P.node[x]['gatekeeper'] = 'True'
