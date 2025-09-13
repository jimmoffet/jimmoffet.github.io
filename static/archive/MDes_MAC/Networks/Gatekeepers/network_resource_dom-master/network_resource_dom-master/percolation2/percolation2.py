from __future__ import division

def build_D(graph, digraph, v):

    # { v: [ root vertex, members, aggregate value ]  }
    #  int    int            str     float

    s = set(digraph.keys()).intersection(set(graph[v]))

    if not s:
        digraph[v] = [v, str(v)+'.', float(graph.node[v]['money'])]
        return digraph

    #digraph[v] = []

    roots = set()
    for n in s:
        roots.add(digraph[n][0])

    big_root = roots.pop()
    #print digraph[big_root][2]

    members = digraph[big_root][1]+str(v)+'.'
    agg_value = float(graph.node[v]['money'])+digraph[big_root][2]
    #digraph[v] = [0, 0, 0]

    for ro in list(roots):
        members += digraph[ro][1]
        agg_value += digraph[ro][2]

    digraph = update_comp(digraph, big_root, members, agg_value)

        #member_list = parse_members(members)
        #for member in member_list:

    return digraph

    #return [0, ]

def parse_members(string):
    members = []
    member = str()
    for letter in string:
        if letter == '.':
            members.append(member)
            member = str()
            continue
        member += letter
    return members

def update_comp(table, root, members, value):
    member_list = parse_members(members)
    for member in member_list:
        if member not in table.keys():
            table[member] = [0,0,0]
        table[member] = [root, members, value]#[0] = root
        #table[member][1] = members
        #table[member][2] += value
    return table
#print parse_members('11.21.1993.')

def find_neighbors(graph, digraph, v):
    comp_with_v = parse_members(digraph[v][1])
    neighbors = list()
    for node in comp_with_v:
        neighbors += graph[node].keys()
    nbr = set(neighbors) - set(comp_with_v)
    return nbr