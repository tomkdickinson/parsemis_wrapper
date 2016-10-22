"""
This short example shows how you can mine frequent graphs using the wrapper
"""
from parsemis import ParsemisMiner
import networkx as nx
import os


def subgraph_exists(supergraph, subgraph):
    """
    A quick subgraph method to see if a subgraph exists
    Does not support full subgraph isomorphism.

    :param supergraph: Parent graph
    :param subgraph: sub-graph to check
    :return: True if subgraph exists, false if not
    """

    if len(subgraph.nodes()) > len(supergraph.nodes()):
        return False
    for n in subgraph.nodes():
        if n not in supergraph.nodes():
            return False

    if len(subgraph.edges()) > len(supergraph.edges()):
        return False
    for e in subgraph.edges():
        edge_exist = False
        for e2 in supergraph.edges():
            if sorted(list(e)) == sorted(list(e2)):
                edge_exist = True
        if not edge_exist:
            return False
    return True

# Load our graphs
graph_folder = "example_dataset"
graphs = []
for f in os.listdir(graph_folder):
    path = "%s/%s" % (graph_folder, f)
    graphs.append(nx.read_gml(path))

frequent_graphs = ParsemisMiner("data", "parsemis.jar", minimum_frequency="2%", close_graph=True).mine_graphs(graphs)

# Count our subgraphs
frequent_graph_counts = []
for frequent_graph in frequent_graphs:
    count = 0
    for graph in graphs:
        if subgraph_exists(graph, frequent_graph):
            count += 1
    frequent_graph_counts.append((count, frequent_graph))

for frequent_graph in sorted(frequent_graph_counts, key=lambda subgraph: subgraph[0], reverse=True):
    if len(frequent_graph[1].edges()) == 0:
        print("%i - %s" % (frequent_graph[0], frequent_graph[1].nodes()))
    else:
        print("%i - %s" % (frequent_graph[0], frequent_graph[1].edges()))
