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
import numpy as np


class FrequentGraph:

    def __init__(self, graph, appears_in) -> None:
        super().__init__()
        self._graph = graph
        self._appears_in = appears_in
        self._support = len(self._appears_in)
        self.__rank = None

    def to_string(self):
        if len(self._graph.edges()) == 0:
            return  ",".join(self._graph.nodes())
        else:
            edge_strings = []
            for edge in self._graph.edges():
                labels = ParsemisMiner.get_label_from_edge(self._graph, edge)
                for label in labels:
                    if (nx.is_directed(self._graph)):
                        edge_strings.append("(%s)-[%s]->(%s)" % (edge[0], label, edge[1]))
                    else:
                        edge_strings.append("(%s)-[%s]-(%s)" % (edge[0], label, edge[1]))
            return ", ".join(list(set(edge_strings)))

    @property
    def graph(self):
        return self._graph

    @property
    def support(self):
        return self._support

    @property
    def appears_in(self):
        return self._appears_in

    @property
    def rank(self):
        return self.__rank

    def set_rank(self, rank):
        self.__rank = rank


class ParsemisMiner:
    """
    A basic wrapper for using ParSeMiS.

    The wrapper itself has one required argument, a location to store the input and output files for the graphs
    that are required for parsing.
    """

    def __init__(self, data_location, mine_undirected=True, debug=True):
        self.data_location = data_location

        self.parsemis_location = "%s/parsemis.jar" % os.path.dirname(os.path.realpath(__file__))
        os.makedirs(self.data_location, exist_ok=True)

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

    def mine_graphs(self, graphs, **kwargs):
        log.debug("Mining %i graphs" % len(graphs))
        self.write_graph(graphs)
        self.perform_mining(**kwargs)
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

    def perform_mining(self, **kwargs):
        commands = ['java', '-jar',
                    "-Xmx10g",
                    self.parsemis_location,
                    "--graphFile=%s" % self.input_file,
                    "--outputFile=%s" % self.output_file,
                    "--minimumFrequency=%s" % kwargs.get('minimum_frequency', '0.05'),
                    "--findPathsOnly=%s" % kwargs.get('find_paths_only', True),
                    "--findTreesOnly=%s" % kwargs.get('find_trees_only', True),
                    "--singleRooted=%s" % kwargs.get('single_rooter', True),
                    "--connectedFragments=%s" % kwargs.get('connectedFragments', True),
                    "--algorithm=%s" % kwargs.get('algorithm', 'gspan'),
                    "--closeGraph=%s" % kwargs.get('close_graph', False),
                    "--subdue=%s" % kwargs.get('subdue', False),
                    "--zaretsky=%s" % kwargs.get('zaretsky', False),
                    "--distribution=%s" % kwargs.get('distribution', 'threads'),
                    "--threads=%s" % kwargs.get('n_threads', 1),
                    "--storeEmbeddings=%s" % kwargs.get('store_embeddings', True)
                    ]
        if self.debug_statement is not None:
            commands.insert(2, self.debug_statement)

        if 'minimum_node_count' in kwargs:
            commands.append("--minimumNodeCount=%i" % kwargs.get('minimum_node_count'))
        if 'maximum_node_count' in kwargs:
            commands.append("--maximumNodeCount=%i" % kwargs.get('maximum_node_count'))
        if 'minimum_edge_count' in kwargs:
            commands.append("--minimumEdgeCount=%i" % kwargs.get('minimum_edge_count'))
        if 'maximum_edge_count' in kwargs:
            commands.append("--maximumEdgeCount=%i" % kwargs.get('maximum_edge_count'))
        if 'maximum_frequency' in kwargs:
            commands.append("--maximumFrequency=%i" % kwargs.get('maximum_frequency'))

        log.debug(commands)
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
                        if n == '':
                            n = '[EMPTY_NODE]'
                        node_dict[n] = n_id
                        f.write("v %i %s\n" % (node_dict[n], n))

                    for edge in graph.edges():
                        labels = self.get_label_from_edge(graph, edge)
                        for label in labels:
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
                        labels = self.get_label_from_edge(graph, edge)
                        for label in labels:
                            if label is not None:
                                f.write("u %i %i %s\n" % (node_dict[edge[0]], node_dict[edge[1]], label))
                            else:
                                f.write("u %i %i\n" % (node_dict[edge[0]], node_dict[edge[1]]))
                except Exception as e:
                    log.error(e)

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

    @staticmethod
    def get_label_from_edge(g, edge, attribute_name='label'):
        edge_attributes = g.get_edge_data(edge[0], edge[1])
        if edge_attributes is None and nx.is_directed(g):
            edge_attributes = g.get_edge_data(edge[1], edge[0])

        labels = []
        if type(g) == nx.MultiDiGraph or type(g) == nx.MultiGraph:
            for index in edge_attributes:
                if attribute_name in edge_attributes[index]:
                    labels.append(edge_attributes[index][attribute_name])
        else:
            if attribute_name in edge_attributes:
                labels.append(edge_attributes[attribute_name])

        return labels

    @staticmethod
    def is_subgraph(graph, subgraph):
        if not set(subgraph.nodes()).issubset(graph.nodes()):
            return False
        else:
            for edge in subgraph.edges():
                return ParsemisMiner.graph_has_edge(graph, subgraph, edge)
        return True

    @staticmethod
    def graph_has_edge(graph, subgraph, edge):
        if graph.has_edge(edge[0], edge[1]) or (not nx.is_directed(graph) and graph.has_edge(edge[1], edge[0])):
            subgraph_edge_labels = ParsemisMiner.get_label_from_edge(subgraph, edge)
            supergraph_edge_labels = ParsemisMiner.get_label_from_edge(graph, edge)
            if ParsemisMiner.shares_edge_label(subgraph_edge_labels, supergraph_edge_labels) \
                    or (len(subgraph_edge_labels) == 0 and len(supergraph_edge_labels) == 0):
                return True
            else:
                return False

    @staticmethod
    def shares_edge_label(list_a, list_b):
        return len(set(list_a).intersection(set(list_b))) > 0

    @staticmethod
    def calculate_dot_product_similarity(sub_graph: nx.Graph, super_graph: nx.Graph):
        a_values = np.ones(len(sub_graph.nodes()) + len(sub_graph.edges()))
        b_values = np.zeros(len(a_values))
        for i, node in enumerate(sub_graph.nodes()):
            if node in super_graph.nodes():
                b_values[i] = 1
        for i, edge in enumerate(sub_graph.edges()):
            if ParsemisMiner.graph_has_edge(super_graph, sub_graph, edge):
                b_values[i + len(sub_graph.nodes())] = 1

        return np.prod(np.column_stack((a_values, b_values)), axis=1).sum() / len(a_values)


    @staticmethod
    def calculate_jaccard_similarity(sub_graph: nx.Graph, super_graph: nx.Graph):
        """
                Calculates the similiarity between a subgraph and a parent
                :param sub_graph:
                :param parent_graph:
                :return:
                """

        set_a = set(sub_graph.nodes()).union(sub_graph.edges())
        set_b = ParsemisMiner._calcuate_set_b(sub_graph, super_graph)

        result = len(set_a.intersection(set_b)) / len(set_a.union(set_b))
        return result

    @staticmethod
    def _calcuate_set_b(sub_graph: nx.Graph, super_graph: nx.Graph):
        set_b = set()
        for node in sub_graph.nodes():
            if node in super_graph.nodes():
                set_b.add(node)
        for edge in sub_graph.edges():
            if ParsemisMiner.graph_has_edge(super_graph, sub_graph, edge):
                set_b.add(edge)
        return set_b