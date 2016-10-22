"""
This script is a wrapper script for ParSeMiS

For this example, our graphs are represented using NetworkX

https://www2.informatik.uni-erlangen.de/EN/research/zold/ParSeMiS/index.html
"""
import subprocess
import networkx as nx
import logging as log
import re


class ParsemisMiner:
    """
    A basic wrapper for using ParSeMiS.

    The wrapper itself has one required argument, a location to store the input and output files for the graphs
    that are required for parsing.
    """

    def __init__(self, data_location, parsemis_location="./parsemis.jar", minimum_frequency="5%", close_graph=False,
                 maximum_frequency=None, minimum_node_count=None, maximum_node_count=None, minimum_edge_count=None,
                 maximum_edge_count=None, find_paths_only=False, find_trees_only=False, single_rooted=False,
                 connected_fragments=False, algorithm="gspan", subdue=False, zaretsky=False, distribution="local",
                 threads=1):

        self.data_location = data_location
        self.parsemis_location = parsemis_location
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

    def mine_graphs(self, graphs):
        log.debug("Mining %i graphs" % len(graphs))

        # First write the graphs to the input location
        self.write_lg(graphs, "%s/input.lg" % self.data_location)

        # Then perform pattern mining on those graphs
        self.perform_mining()

        # Finally read the graphs from the output location
        return self.read_lg("%s/output.lg" % self.data_location)

    def perform_mining(self):
        commands = ['java', '-jar',
                    "-Xmx10g",
                    self.parsemis_location,
                    "--graphFile=%s/input.lg" % self.data_location,
                    "--outputFile=%s/output.lg" % self.data_location,
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
                    "--threads=%s" % int(self.threads)
                    ]

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

        subprocess.call(commands)

    @staticmethod
    def write_lg(graphs, file):
        log.debug("Writing graphs to %s" % file)
        with open(file, "w") as f:
            for g_id, graph in enumerate(graphs):
                try:
                    f.write("t # %s\n" % g_id)
                    node_dict = {}
                    for n_id, n in enumerate(graph.nodes()):
                        node_dict[n] = n_id
                        f.write("v %i \'%s\'\n" % (node_dict[n], n))
                    for start in graph.edge:
                        edges = graph.edge[start]
                        for e in edges:
                            f.write("e %i %i \'%s\'\n" % (node_dict[start], node_dict[e], edges[e]['label']))
                except Exception as e:
                    print(e)
            f.close()

    @staticmethod
    def read_lg(file):
        """
        Reads an LineGraph file and converts it to a list of NetworkX Graph Objects
        :param file: LineGraph file to read
        :return: A list of LineGraph objects
        """
        log.debug("Reading graphs from %s" % file)
        graphs = []

        with open(file, "r") as f:
            graph_map = {}
            node_map = {}
            graph_id = 1
            for line in f.readlines():
                line = line.strip()
                if line.startswith("t #"):
                    node_map = {}
                    graph_id = re.findall("\d+$", line)[0]
                    graph = nx.Graph(id=graph_id)
                    graph_map[graph_id] = graph
                elif line.startswith("v"):
                    parts = line.split(" ")
                    graph_map[graph_id].add_node(parts[2].strip('\''))
                    node_map[parts[1]] = parts[2].strip('\'')
                elif line.startswith("e"):
                    parts = line.split(" ")
                    graph_map[graph_id].add_edge(node_map[parts[1]], node_map[parts[2]], label=parts[3].strip('\''))
            graphs += graph_map.values()
        return graphs
