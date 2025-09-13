__author__ = 'Lihan'



def make_table(graph):

    table = dict()
    for vertex in graph.nodes():
        table[vertex] = [0,1,float(graph.node[vertex]['repo']),0,0]
    return table

def count(string):
    member_size = 0
    for letter in string:
        if letter == '.':
            member_size += 1
    return member_size

def update_v2(graph, digraph, t, v):

    if float(graph.node[v]['money']) >= t:
        return [-1]
    s = set(digraph.keys()).intersection(set(graph[v]))

    if not s:
        return [0, 1, float(graph.node[v]['money']), 0, 0]

    roots = set()
    for n in s:
        roots.add(digraph[n][0])

    big_root = roots.pop()

    agg_value = float(graph.node[v]['money']) + digraph[big_root][2]
    membersize = count(digraph[big_root][1])

    if agg_value >= t:
        #print float(graph.node[v]['money']), digraph[big_root][2]
        return [-1]

    if not roots:
        return [0, membersize, agg_value, 0,0]

    for ro in roots:
        agg_value += digraph[ro][2]

        if agg_value >= t:
            return [-1]
        
        membersize = membersize * count(digraph[ro][1])

    return [0, membersize, agg_value, 0, 0]

import operator

def return_gp(table):
    gp = []
    for vertex, data in table.iteritems():
        if data[0] == -1:
            gp.append(vertex)
    return gp

def update_table(table,nbr,graph,dg,t):

    #if not table:
    #    return table

    #only need to update vertices around recently added v
    # need to  re-calculate probability for all
    active_table = {k:table[k] for k in nbr if k in table}

    for vertex in active_table:
        table[vertex] = update_v2(graph,dg,t,vertex)

    gp = return_gp(table)
    if len(gp) == len(table):   #remaining vertices are all gp
        return table

    score_list = []

    for vertex2 in table:
        if vertex2 in gp:
            continue

        s = score(table[vertex2])
        #print table[vertex2]
        table[vertex2][3] = s
        score_list.append(s)

    # make a dictionary out of unevaluated vertices?
    index, max_score = max(enumerate(score_list),key=operator.itemgetter(1))
    total_score = sum(score_list)
    num_undec_v = len(table)
    # p(v) = (max_score - score(v))/(total_score)
    for vertex, data in table.items():
        if vertex in gp:
            continue
        table[vertex][4] = (p(table[vertex][3],max_score,total_score,num_undec_v))

    #display(table)
    return table

def score(list_data):
    #print list_data
    if list_data[0] != 0:
        #print list_data
        raise Exception("can't compute probability for a GP vertex/ Digraph vertex ")

    alpha = 0 #product size
    beta = 1 #aggregate component value
    score = alpha*list_data[1] + beta*list_data[2]

    return score

def p(score, max_score,total_score, num_undec_v):

    if max_score == score:
        return 1/total_score
    #return 1-score/max_score
    return (max_score-score)/ total_score
#
# def prod(comp_size,num_members):
#
#     mem_sizes = []
#
#     for comp_members in num_members: #comp member has the form '22.19.1.90', type = str
#         mem_sizes.append(count(comp_members)) #e.g. mem_sizes can be [7,2,1,3]
#
#     #prod_size = mem_sizes.pop()
#
#     for a_number in mem_sizes:
#         comp_size = comp_size*a_number
#
#     return comp_size
#
# from percolation import get_roots2
#
# def update_v(graph,dg,t,v):
#     # state  | product size | aggregate value | score sum | p
#     # data[0]| data[1]      | data[2]         | data[3]   | data[4]
#     # state:
#     # -1 -> v is a GP, compute nothing
#     # 0 -> not evaluated, initial state for new digraph
#
#     d_graph = dg.copy()
#
#     #print graph.node[v]
#     if float(graph.node[v]['money']) >= t:
#         return [-1]
#
#     #print str(v)+ "| | d_graph size: "+ str(len(d_graph.nodes()))+ " current GP size: " + str(len(gp))
#     #print present_v
#
#     d_graph.add_node(v, graph.node[v])
#     #adds v hypothetically
#     s = set(d_graph.nodes()).intersection(set(graph[v])) #are there neighbors in original graph and digraph?
#
#     if not s:   #node does not have any neighbors from G in current digraph
#                 #node starts as a root, with a loop
#         #d_graph.add_edge(v,v)
#         return [0, 1, float(d_graph.node[v]['repo']),0,0]
#
#     for w in s:
#         #if (w,v) in edges or (v,w) in edges:
#         #    print d_graph.edges()
#         #    raise Exception("this exception")
#         d_graph.add_edge(v,w)
#
#     roots = set(get_roots2(d_graph, v))
#
#     #print "possible directions are:" + str(d_graph.edges(v))
#     #print "roots of vertex " + str(v)+ " are: " +str(list(roots))
#
#     big_root = roots.pop()
#
#     agg_value = float(d_graph.node[v]['repo'])+float(d_graph.node[big_root]['repo'])
#     comp_size = count(d_graph.node[big_root]['members'])
#     #d_graph.node[v]['repo'] = str(0)
#
#     if agg_value >= t:
#         #print str(v) + " is a gatekeeper since adding it to " + str(big_root) + " has a value of " + d_graph.node[big_root]['repo']
#         return [-1]
#
#     if not roots:
#         return [0, comp_size, agg_value, 0,0]
#
#         # otheriwse multiple components are being merged into 1
#         #print v, roots
#
#     all_members = []
#     for ro in roots:
#         agg_value += float(d_graph.node[ro]['repo'])
#
#         if agg_value >= t:
#                 #print str(v)+" is a GP since it connected "+ str(ro) +" and " + str(big_root)
#             return [-1]
#                 #return table
#
#         all_members.append(d_graph.node[ro]['members'])#concate. membership list
#
#         # value of component containing v has been computed
#         # now we compute the product of component sizes
#
#     comp_size = prod(comp_size,all_members)
#
#     return [0, comp_size, agg_value, 0,0]


#import networkx as nx


# def undecided_v(table):    # gathers from dict all vertices not in digraph/GP
#     active_table = dict()
#     for vertex, data in table.items():
#         if data[0] == 0:
#             #if data[-1] > 0.001: # if p(v) < 0.1% chance, discount
#             active_table[vertex] = data
#     return active_table