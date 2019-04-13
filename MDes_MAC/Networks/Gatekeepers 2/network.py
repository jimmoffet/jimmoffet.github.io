
import networkx as nx
import random as r

import numpy as np
from numpy.random import random_sample

from gatekeeper import below_viable

# def list_sample(values, probabilities, size):
#     bins = np.add.accumulate(probabilities)
#     return values[np.digitize(random_sample(size), bins)]

def assign_contribution(graph):
    output = graph
    nx.set_node_attributes(output, 'money', str(1)) #string attribute compatible with graphml
    #nx.set_node_attributes(output, 'contribution', str(0))
    nx.set_node_attributes(output, 'gatekeeper', str(False))
    #nx.set_node_attributes(output, 'cs', str(0))
    return output
def sample(values,probabilities):
    bins = np.add.accumulate(probabilities)
    #print bins
    return values[np.digitize(random_sample(), bins)]



#--------------------------------------
def pos_sec_nbr(graph, new_vertex, contact_nbrh):
    
    existing_edges = 0              # first check if two initial contact nbrh has an intersection
    for vertex in contact_nbrh:
        if graph.has_edge(vertex,new_vertex):
            existing_edges += 1

    num_sec_nbr = r.randint(0,2)
                    # secondary contacts follow uniform distribution,
                    # determines HOW MANY secondary neighbors are formed, 0 (33%), 1 (33%) or 2 (33%)

    while num_sec_nbr > len(contact_nbrh) - existing_edges:
        num_sec_nbr = r.randint(0,2)
                                    # there is a possibility that we are trying to add more edges between
                                    # secondary contacts and new_vertex than there are neighbors of the initial contact
    return num_sec_nbr

def form_edges(graph, new_vertex, contact_vertex):  # handles all edge formations for 1 initial contact vertex

    contact_nbrh = graph.neighbors(contact_vertex)
    num_sec_nbr = pos_sec_nbr(graph, new_vertex, contact_nbrh)

    vert_to_connect = []
    while num_sec_nbr != 0:       # whenever the edge between new_vertex and a neighbor of contact_vertex is
                                  # added, decrement num_neighbors. Stop when this variable is 0

        candidate = r.choice(contact_nbrh)
                                    # r.choice chooses a random element from (the list of neighbors of (contact_vertex))
        while candidate in vert_to_connect or graph.has_edge(new_vertex, candidate):
            #print candidate
            candidate = r.choice(contact_nbrh)
                    # did we already form an edge here? time to find new neighbor of initial contact

        vert_to_connect.append(candidate) #record
        num_sec_nbr -= 1

    for sec_neigh in vert_to_connect:           #ACTUAL EDGE FORMATION HAPPENS
        graph.add_edge(new_vertex, sec_neigh)

    graph.add_edge(new_vertex, contact_vertex)  # finish by adding an edge between the new vertex and initial contact vertex

    return graph

def grow_network(ori_graph):        #this function adds a new vertex and chooses 1 ~ 2 initial contacts

    ori_size = nx.number_of_nodes(ori_graph)-1
    graph = ori_graph

    new_vertex = ori_size+1   # remember first vertex starts at 0, last vertex in original graph has value ori_size - 1
    graph.add_node(new_vertex, {'money': str(sample(values,probabilities)), 'contribution': str(0)})

    n1 = r.randint(0,ori_size)
    form_edges(graph, new_vertex, n1) # THIS IS THE ONLY FUNCTION WHICH MANIPULATES THE GRAPH

    if r.random() >= 0.95:    # two initial neighbors

        #print 'TIME FOR TWO NEIGHBORS BOOOYYY'          # expect this message 5 times if the function is invoked 100 times, etc.
        n2 = r.randint(0,ori_size)

        while n1 == n2: # or n2 in grown_graph.neighbors(n1):         # check to see if the second initial neighbor is the same as first
            print 'SAME INITIAL CONTACTS MADE'
            n2 = r.randint(0,ori_size)

        form_edges(graph, new_vertex, n2)

    return graph

def GPfree(G, exceptions):

    #first compute non GP vertices
    no_gp = exceptions
    for vertex in G.nodes(data=False):
        if G.node[vertex]['gatekeeper'] == 'False':
            #print G.node[vertex]['gatekeeper']
            no_gp.append(vertex)

    GPfree_graph = G.subgraph(no_gp)
    return GPfree_graph

def reachable_GP(G,special_gp):
    reachable_gatekeepers = []

    all_gp = []
    for vertex in G.nodes(data=False):
        if G.node[vertex]['gatekeeper'] == 'True':
            all_gp.append(vertex)

    for gp in all_gp:
        F = GPfree(G, [gp,special_gp])
        if nx.has_path(F,gp,special_gp) and gp != special_gp:
            reachable_gatekeepers.append(gp)
            print str(special_gp) + '->' + str(gp)
    return reachable_gatekeepers

def min_cut(G, special_gp, array_gp):
    F = GPfree(G, [array_gp,special_gp])
    # induced subgraph of non-gp + 2 gatekeepers in question
    #print array_gp in F.nodes() and special_gp in F.nodes()


    c_nodes = nx.node_connected_component(F, special_gp)
    # consider now only the component within F which links the 2 gp
    #print array_gp in c_nodes and special_gp in c_nodes

    component = F.subgraph(c_nodes)
    # add to the nodes of this component their edges

    m_cut = nx.minimum_node_cut(component, special_gp, array_gp)
    # find the min cut s.t. these two gatekeepers are disconnected

    return m_cut

def check_and_swap(G, special_gp,array_gp):
    m_cut = min_cut(G, special_gp,array_gp)
    node_inbetween = list(m_cut)[0] #only interesting node is the first one

    if len(m_cut) == 0:
        print "something is wrong with reachable_gp (given gps not connected)"

    if len(m_cut) == 1:
        print " %d has been swapped for %d and %d " % (node_inbetween, special_gp, array_gp)
        G.node[special_gp]['gatekeeper'] = str(False)
        G.node[array_gp]['gatekeeper'] = str(False)
        G.node[node_inbetween]['gatekeeper'] = str(True)

    else:
        print "%d and %d are not replaced" % (special_gp, array_gp)
        return False
    return True

def optimality_test(G, gp):

    rgp = reachable_GP(G, gp)

    replacement_found = False
    for another_gp in rgp:
        replacement_found = check_and_swap(G,gp, another_gp)
        if replacement_found:
            return 0
    return 0


def gave_pair( switch1, switch2 ):

    output = []
    values = [np.array([0.00001, 8, 675, 3500]), #original
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

def grow2(G, threshhold, v, p): # grow with gatekeeper tags

    data = gave_pair(v,p)

    ori_size = nx.number_of_nodes(G)-1
    grown = G

    new_vertex = ori_size+1
    grown.add_node(new_vertex, {'money': str(sample(data[0],data[1])), 'gatekeeper': str(False)})

    n1 = r.randint(0,ori_size)
    form_edges(grown, new_vertex, n1)

    if r.random() >= 0.95:

        n2 = r.randint(0,ori_size)

        while n1 == n2:
            #print 'SAME INITIAL CONTACTS MADE'
            n2 = r.randint(0,ori_size)

        form_edges(grown, new_vertex, n2)

    F = GPfree(grown, [])
    if below_viable(F, new_vertex, threshhold):
        grown.node[new_vertex]['gatekeeper'] = str(False)

    else:
        grown.node[new_vertex]['gatekeeper'] = str(True)
        #print "test for %d optimality" %new_vertex
        #optimality_test(grown,new_vertex)
    #else:
    #    grown.node[new_vertex]['gatekeeper'] = str(True)

    return grown

def write_cs(G):
    graph = G
    nx.set_node_attributes(G, 'cs', str(0))
    for component in nx.connected_component_subgraphs(G):
        component_sum = 0
        for vertex in component:
            component_sum += float(G.node[vertex]['money'])
        for vertex in component:
            G.node[vertex]['cs'] = component_sum

    return graph


def restricted_grow(G, threshhold):

    graph = G
    ori_size = nx.number_of_nodes(G) - 1
    new_vertex = ori_size + 1

    viable = True
    while viable:

        graph.add_node(new_vertex, {'money': str(sample(values,probabilities)), 'contribution': str(0)})

        n1 = r.randint(0,ori_size)
        form_edges(graph, new_vertex, n1)

        if r.random() >= 0.95:    # two initial neighbors

            #print 'TIME FOR TWO NEIGHBORS BOOOYYY'          # expect this message 5 times if the function is invoked 100 times, etc.
            n2 = r.randint(0,ori_size)

            while n1 == n2: # or n2 in grown_graph.neighbors(n1):         # check to see if the second initial neighbor is the same as first
                print 'SAME INITIAL CONTACTS MADE'
                n2 = r.randint(0,ori_size)

            form_edges(graph, new_vertex, n2)

        if below_viable(graph,new_vertex,threshhold):
            viable = False

        else:
            graph.remove_node(new_vertex)

    return graph