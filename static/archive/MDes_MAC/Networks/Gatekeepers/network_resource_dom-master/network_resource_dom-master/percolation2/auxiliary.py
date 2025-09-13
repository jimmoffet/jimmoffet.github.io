__author__ = 'Lihan'
def wrapper(func, *args):
    def wrapped():
        return func(*args)
    return wrapped

import timeit as ti

def time(func, runs, *args):
    wrapped = wrapper(func, *args)
    print '%s completed in %s' %(func.__name__,str(ti.timeit(wrapped, number=runs)))
    return 0

import matplotlib.pyplot as plt
import networkx as nx

def display(G):

    pos = nx.fruchterman_reingold_layout(G, 2)

    dmin=1
    ncenter=3 #int(new_G.number_of_nodes()/2)
    for n in pos:
        x,y=pos[n]
        d=(x-0.5)**2+(y-0.5)**2
        if d<dmin:
            ncenter=n
            dmin=d

    # color by path length from node near center
    p=nx.single_source_shortest_path_length(G,ncenter)

    plt.figure(figsize=(8,8))
    nx.draw_networkx_edges(G,pos,nodelist=[ncenter],alpha=0.4)
    nx.draw_networkx_nodes(G,pos,nodelist=p.keys(),
                           node_size=80,
                           node_color=p.values(),
                           cmap=plt.cm.Reds_r)

    plt.xlim(-0.05,1.05)
    plt.ylim(-0.05,1.05)
    plt.axis('off')
    plt.savefig('random_geometric_graph.png')
    plt.show()
    return 0

#node_connected_component(G, node):
#   return list of nodes in component of G containing 'node'

def count(input):
    size = 0
    for element in input:
        if type(element) != int:
            size += count(element)
        else:
            size += 1
    return size

def partition(number):
    answer = set()
    answer.add((number, ))
    for x in range(1, number):
        for y in partition(number - x):
            answer.add(tuple(sorted((x, ) + y)))
    return answer

def collapse_ds(input):
    collector = []
    for element in input:
        if type(element) != int:
            collector += collapse_ds(element)
        else:
            collector.append(element)
    return collector

def parse(string):
    l = []
    cache = str()
    for letter in string:
        if letter == '.':
            l.append(int(cache))
            cache = str()
            continue

        cache+=letter

    if cache:
        l.append(int(cache))
    return l

#print parse('123.444.6')

def display(t):
    table = t
    GP = []
    for v,data in table.iteritems():

        #if data[0]>0:


        #print v,data
        print v,data, ("%.2f" % data[-1])

        #if data[0] > 0:
           # print data

        if table[v][0] == -1:
            GP.append(v)
        #     print str([v]) + " is GP"
        # #if table[v][0] == 0:
        # #    print str([v]) + " not processed"
        # if table[v][0] > 0:
        #     #print len(table[v])
        #     print v, data
    print GP, len(GP)


    return 0

        #print str([v])+ ''

import csv

def csvExport(H, name, GPs):
    neighbors = []
    nodes = []
    money = []
    GP = []
    GPsets = [0 for x in xrange(H.number_of_nodes())]
    centrality = []
    eccentricity = []
    dispersion = [0 for x in xrange(H.number_of_nodes())]
    globalGPList = []
    eigenvalue = nx.eigenvector_centrality(H)
    eigenvector = []
    between = nx.betweenness_centrality(H)
    betweenness = []
    tri = nx.average_clustering(H)
    clustering = []
    shortypath = nx.average_shortest_path_length(H)
    avgshortypath = []

    communicate = nx.communicability_centrality(H)
    communicability = []

    connect = nx.average_node_connectivity(H)
    connectivity = []

    allGP = set()
    for y in GPs:
        for x in y:
            allGP.add(int(x))
    allGPList = list(allGP)

    for n in H.nodes():
        nodes.extend([n])
        neighbors.append(H.neighbors(n))
        money.append(float(H.node[n]['money']))
        GP.append(H.node[int(n)]['gatekeeper'])
        centrality.append(nx.load_centrality(H,n))
        eccentricity.append(nx.eccentricity(H,n))
        globalGPList.append(allGPList)
        eigenvector.append(eigenvalue.get(n))
        betweenness.append(between.get(n))
        clustering.append(tri)
        avgshortypath.append(shortypath)
        connectivity.append(connect)



        communicability.append(communicate.get(n))

        if H.node[int(n)]['gatekeeper'] == True:
            temp = []
            tempD = []
            for x in allGPList:
                tempD.append(nx.dispersion(H,n,x))
            for y in GPs:
                for x in y:
                    if n == x:
                        temp.append(y)
            dispersion[int(n)] = tempD
            GPsets[int(n)] = temp
        else:
            GPsets[int(n)] = ''
            dispersion[int(n)] = ''

    export = [nodes,neighbors,money,GP,GPsets,eccentricity,globalGPList,dispersion,eigenvector,centrality,betweenness,communicability,clustering,avgshortypath,connectivity]
    export = list(zip(*export))
    with open(name+'.csv', "wb") as f:
        writer = csv.writer(f)
        writer.writerow(['nodes','neighbors','money','GP','GPsets','eccentricity','globalGPList','dispersion','eigenvector','load','betweenness','communicability','avgclustering','avgshortestpath','avg_node_connectivity'])
        writer.writerows(export)
    return 0