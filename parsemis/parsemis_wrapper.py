"""
This script is a wrapper script for ParSeMiS

For this example, our graphs are represented using NetworkX

https://www2.informatik.uni-erlangen.de/EN/research/zold/ParSeMiS/index.html
"""
import subprocess
import networkx as nx
import logging as log
import os
import re


class FrequentGraph:

    def __init__(self, graph, appears_in) -> None:
        super().__init__()
        self._graph = graph
        self._appears_in = appears_in
        self._support = len(self._appears_in)

    @property
    def graph(self):
        return self._graph

    @property
    def support(self):
        return self._support

    @property
    def appears_in(self):
        return self._appears_in


class ParsemisMiner:
    """
    A basic wrapper for using ParSeMiS.

    The wrapper itself has one required argument, a location to store the input and output files for the graphs
    that are required for parsing.
    """

    def __init__(self, data_location, parsemis_location=None, minimum_frequency="5%", close_graph=False,
                 maximum_frequency=None, minimum_node_count=None, maximum_node_count=None, minimum_edge_count=None,
                 maximum_edge_count=None, find_paths_only=False, find_trees_only=False, single_rooted=False,
                 connected_fragments=True, algorithm="gspan", subdue=False, zaretsky=False, distribution="local",
                 threads=1, store_embeddings=False, debug=False, mine_undirected=False):

        self.data_location = data_location
        if parsemis_location is None:
            self.parsemis_location = "%s/parsemis.jar" % os.path.dirname(os.path.realpath(__file__))

        os.makedirs(self.data_location, exist_ok=True)

        self.minimum_frequency = minimum_frequency
        self.maximum_frequency = maximum_frequency
        if minimum_node_count is not None and type(minimum_node_count) is not int:
            raise TypeError("Minimum node count must be an integer >= 0")
        self.minimum_node_count = minimum_node_count
        if maximum_node_count is not None and type(maximum_node_count) is not int:
            raise TypeError("Maximum node count must be an integer >= 0")
        self.maximum_node_count = maximum_node_count
        if minimum_edge_count is not None and type(minimum_edge_count) is not int:
            raise TypeError("Minimum edge count must be an integer >= 0")
        self.minimum_edge_count = minimum_edge_count
        if maximum_edge_count is not None and type(maximum_edge_count) is not int:
            raise TypeError("Maximum edge count must be an integer >= 0")
        self.maximum_edge_count = maximum_edge_count
        self.find_paths_only = find_paths_only
        self.find_trees_only = find_trees_only
        self.single_rooted = single_rooted
        self.connected_fragments = connected_fragments
        allowed_algorithms = ["gspan", "gaston", "dagma"]
        if algorithm.lower() in allowed_algorithms:
            self.algorithm = algorithm.lower()
        else:
            raise Exception("Algorithm must be one of: %s" % ",".join(allowed_algorithms))
        self.close_graph = close_graph
        self.subdue = subdue
        self.zaretsky = zaretsky
        allowed_distributions = ["local", "threads", "threads_np"]
        if distribution in allowed_distributions:
            self.distribution = distribution
        else:
            raise Exception("Distribution must be: one of: %s" % ",".join(allowed_distributions))
        self.threads = int(threads)
        self.store_embeddings = store_embeddings
        if debug:
            self.debug_statement = "-Dverbose=true"
        else:
            self.debug_statement = None

        self.mine_undirected = mine_undirected
        if self.mine_undirected:
            self.input_file = "%s/input.g" % self.data_location
            self.output_file = "%s/output.g" % self.data_location
        else:
            self.input_file = "%s/input.lg" % self.data_location
            self.output_file = "%s/output.lg" % self.data_location

        if os.path.exists(self.input_file):
            os.remove(self.input_file)
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def mine_graphs(self, graphs):
        log.debug("Mining %i graphs" % len(graphs))
        self.write_graph(graphs)
        self.perform_mining()
        return self.read_graph(graphs)

    def write_graph(self, graphs):
        if self.mine_undirected:
            self.write_g(graphs)
        else:
            self.write_lg(graphs)

    def read_graph(self, graphs):
        if self.mine_undirected:
            return self.read_g(graphs)
        else:
            return self.read_lg()

    def perform_mining(self):
        commands = ['java', '-jar',
                    "-Xmx10g",
                    self.parsemis_location,
                    "--graphFile=%s" % self.input_file,
                    "--outputFile=%s" % self.output_file,
                    "--minimumFrequency=%s" % self.minimum_frequency,
                    "--findPathsOnly=%s" % self.find_paths_only,
                    "--findTreesOnly=%s" % self.find_trees_only,
                    "--singleRooted=%s" % self.single_rooted,
                    "--connectedFragments=%s" % self.connected_fragments,
                    "--algorithm=%s" % self.algorithm,
                    "--closeGraph=%s" % self.close_graph,
                    "--subdue=%s" % self.subdue,
                    "--zaretsky=%s" % self.zaretsky,
                    "--distribution=%s" % self.distribution,
                    "--threads=%s" % int(self.threads),
                    "--storeEmbeddings=%s" % self.store_embeddings
                    ]
        if self.debug_statement is not None:
            commands.insert(2, self.debug_statement)

        if self.minimum_node_count is not None:
            commands.append("--minimumNodeCount=%i" % self.minimum_node_count)
        if self.maximum_node_count is not None:
            commands.append("--maximumNodeCount=%i" % self.maximum_node_count)
        if self.minimum_edge_count is not None:
            commands.append("--minimumEdgeCount=%i" % self.minimum_edge_count)
        if self.maximum_edge_count is not None:
            commands.append("--maximumEdgeCount=%i" % self.maximum_edge_count)
        if self.maximum_frequency is not None:
            commands.append("--maximumFrequency=%i" % self.maximum_frequency)

        log.debug(commands)
        print(commands)
        subprocess.call(commands)

    def write_lg(self, graphs):
        log.debug("Writing graphs to %s" % self.input_file)
        with open(self.input_file, "w") as f:
            for g_id, graph in enumerate(graphs):
                try:
                    if "id" in graph.graph:
                        f.write("t # %s\n" % graph.graph['id'])
                    else:
                        f.write("t # %s\n" % g_id)
                    node_dict = {}

                    for n_id, n in enumerate(graph.nodes()):
                        node_dict[n] = n_id
                        f.write("v %i %s\n" % (node_dict[n], n))

                    for edge in graph.edges():
                        label = self.get_label_from_edge(graph, edge)
                        if label is not None:
                            f.write("e %i %i %s\n" % (node_dict[edge[0]], node_dict[edge[1]], label))
                        else:
                            f.write("e %i %i\n" % (node_dict[edge[0]], node_dict[edge[1]]))
                except Exception as e:
                    log.error(e)
            f.close()

    def write_g(self, graphs):
        log.debug("Writing graphs to %s" % self.input_file)
        with open(self.input_file, "w") as f:
            for g_id, graph in enumerate(graphs):
                try:
                    f.write("XP\n")
                    node_dict = {}
                    for n_id, n in enumerate(graph.nodes()):
                        node_dict[n] = n_id + 1
                        f.write("v %i %s\n" % (node_dict[n], n))
                    for edge in graph.edges():
                        label = self.get_label_from_edge(graph, edge)
                        if label is not None:
                            f.write("u %i %i %s\n" % (node_dict[edge[0]], node_dict[edge[1]], label))
                        else:
                            f.write("u %i %i\n" % (node_dict[edge[0]], node_dict[edge[1]]))
                except Exception as e:
                    log.error(e)

    @staticmethod
    def get_label_from_edge(g, edge, label='label'):
        label = nx.get_edge_attributes(g, label)
        if label is None:
            return None
        return label[edge]

    @staticmethod
    def get_label_from_nodes(g, start_node, end_node, label='label'):
        return ParsemisMiner.get_label_from_edge(g, (start_node, end_node), label)

    def read_lg(self):
        """
        Reads an LineGraph file and converts it to a list of NetworkX Graph Objects
        :param file: LineGraph file to read
        :return: A list of LineGraph objects
        """
        log.debug("Reading graphs from %s" % self.output_file)
        frequent_graphs = []

        with open(self.output_file, "r") as f:
            graph_map = {}
            node_map = {}
            graph_id = 0
            for line in f.readlines():
                line = line.strip()
                if line.startswith("t #"):
                    node_map = {}
                    graph_id += 1
                    graph = nx.DiGraph(id=graph_id, embeddings=[])
                    graph_map[graph_id] = graph
                elif line.startswith("v"):
                    parts = line.split(" ")
                    label = " ".join(parts[2:]).strip('\'')
                    graph_map[graph_id].add_node(label)
                    node_map[parts[1]] = label
                elif line.startswith("e"):
                    parts = line.split(" ")
                    label = " ".join(parts[3:]).strip('\'')
                    graph_map[graph_id].add_edge(node_map[parts[1]], node_map[parts[2]], label=label)
                elif line.startswith("#=>"):
                    graph_map[graph_id].graph['embeddings'].append(line.split(" ")[1])

            for graph in graph_map:
                fg = FrequentGraph(graph_map[graph], graph_map[graph].graph['embeddings'])
                frequent_graphs.append(fg)

        return frequent_graphs

    def read_g(self, graphs):
        log.debug("Reading graphs from %s" % self.output_file)
        frequent_graphs = []
        with open(self.output_file, "r") as f:
            graph_map = {}
            node_map = {}
            graph_id = 0
            for line in f.readlines():
                line = line.strip()
                if line.startswith("XP"):
                    graph_id += 1
                    node_map = {}
                    graph_map[graph_id] = nx.Graph(id=graph_id, embeddings=[])
                elif line.startswith("v"):
                    node_id = line.split(" ")[1]
                    label = " ".join(line.split(" ")[2:])
                    graph_map[graph_id].add_node(label)
                    node_map[node_id] = label
                elif line.startswith("u"):
                    start_node_id = line.split(" ")[1]
                    end_node_id = line.split(" ")[2]
                    label = None
                    if len(line.split(" ")) >= 3:
                        label = " ".join(line.split(" ")[3:])
                    graph_map[graph_id].add_edge(node_map[start_node_id], node_map[end_node_id], label=label)
                elif line.startswith("% => "):
                    line = re.sub("(% => \d{1,}\[)", "", line)
                    line = re.sub("\]$", "", line)
                    for index in line.split(","):
                        if index != "":
                            appears_in_id = graphs[int(index.strip())].graph['id']
                            graph_map[graph_id].graph['embeddings'].append(appears_in_id)

            for graph in graph_map:
                fg = FrequentGraph(graph_map[graph], graph_map[graph].graph['embeddings'])
                frequent_graphs.append(fg)

        return frequent_graphs


