"""
This short example shows how you can mine frequent graphs using the wrapper
"""
from parsemis.parsemis_wrapper import ParsemisMiner
import networkx as nx
import os

# Load our graphs
graph_folder = "example_dataset"
graphs = []
for f in os.listdir(graph_folder):
    path = "%s/%s" % (graph_folder, f)
    graphs.append(nx.read_gml(path))

frequent_graphs = ParsemisMiner(
    "data", minimum_frequency="1%", close_graph=True, store_embeddings=False, debug=True,
    mine_undirected=True
).mine_graphs(graphs)

# Count our subgraphs
frequent_graph_counts = []
for frequent_graph in frequent_graphs:
    count = 0
    for graph in graphs:
        if graph.graph['id'] in frequent_graph.appears_in:
            count += 1
    frequent_graph_counts.append((count, frequent_graph))

for frequent_graph in sorted(frequent_graph_counts, key=lambda subgraph: subgraph[0], reverse=True):
    if len(frequent_graph[1].graph.edges()) == 0:
        print("%i - %s" % (frequent_graph[0], frequent_graph[1].graph.nodes()))
    else:
        print("%i - %s" % (frequent_graph[0], frequent_graph[1].graph.edges()))
