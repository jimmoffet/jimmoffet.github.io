

# def wrapper(func, *args, **kwargs):
#     def wrapped():
#         return func(*args, **kwargs)
#     return wrapped
#
# import timeit as ti
#
# def time(func, obj, runs):
#     wrapped = wrapper(func, obj)
#     #print 'THAT TOOK THIS MUCH TIME: '+ str(ti.timeit(wrapped, number=runs))
#     return ti.timeit(wrapped, number=runs)

def wrapper(func, *args):
    def wrapped():
        return func(*args)
    return wrapped

import timeit as ti

def time(func, runs, *args):
    wrapped = wrapper(func, *args)
    #print 'THAT TOOK THIS MUCH TIME: '+ str(ti.timeit(wrapped, number=runs))
    return ti.timeit(wrapped, number=runs)


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

