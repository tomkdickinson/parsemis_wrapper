import unittest

import networkx as nx

from parsemis.parsemis_wrapper import ParsemisMiner, FrequentGraph


class TestParsemisWrapperMethods(unittest.TestCase):

    classUnderTest: ParsemisMiner

    def test_digraph_is_subgraph_with_labels(self):
        G = nx.DiGraph()
        G.add_edges_from(
            [
                (1, 2, {'label': 'a'}),
                (2, 3, {'label': 'c'}),
                (3, 4, {'label': 'd'}),
                (2, 4, {'label': 'b'})
            ]
        )

        valid_subgraph_a = nx.DiGraph()
        valid_subgraph_a.add_edge(1, 2, label='a')

        valid_subgraph_b = nx.DiGraph()
        valid_subgraph_b.add_edge(3, 4, label='d')

        invalid_subgraph_a = nx.DiGraph()
        invalid_subgraph_a.add_edge(1, 2, label='b')

        invalid_subgraph_b = nx.DiGraph()
        invalid_subgraph_b.add_edge(2, 1, label='a')

        invalid_subgraph_c = nx.DiGraph()
        invalid_subgraph_c.add_edge(1, 4, label='a')

        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_a))
        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_b))

        self.assertFalse(ParsemisMiner.is_subgraph(G, invalid_subgraph_a))
        self.assertFalse(ParsemisMiner.is_subgraph(G, invalid_subgraph_b))
        self.assertFalse(ParsemisMiner.is_subgraph(G, invalid_subgraph_c))

    def test_multidigraph_is_subgraph_with_labels(self):
        G = nx.MultiDiGraph()
        G.add_edges_from(
            [
                (1, 2, {'label': 'a'}),
                (1, 2, {'label': 'f'}),
                (2, 3, {'label': 'c'}),
                (3, 4, {'label': 'd'}),
                (2, 4, {'label': 'b'})
            ]
        )

        valid_subgraph_a = nx.MultiDiGraph()
        valid_subgraph_a.add_edge(1, 2, label='a')

        valid_subgraph_b = nx.MultiDiGraph()
        valid_subgraph_b.add_edge(1, 2, label='f')

        valid_subgraph_c = nx.MultiDiGraph()
        valid_subgraph_c.add_edge(3, 4, label='d')

        invalid_subgraph_a = nx.MultiDiGraph()
        invalid_subgraph_a.add_edge(1, 2, label='b')

        invalid_subgraph_b = nx.MultiDiGraph()
        invalid_subgraph_b.add_edge(2, 1, label='a')

        invalid_subgraph_c = nx.MultiDiGraph()
        invalid_subgraph_c.add_edge(1, 4, label='a')

        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_a))
        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_b))
        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_c))

        self.assertFalse(ParsemisMiner.is_subgraph(G, invalid_subgraph_a))
        self.assertFalse(ParsemisMiner.is_subgraph(G, invalid_subgraph_b))
        self.assertFalse(ParsemisMiner.is_subgraph(G, invalid_subgraph_c))

    def test_graph_is_subgraph_with_labels(self):
        G = nx.Graph()
        G.add_edges_from(
            [
                (1, 2, {'label': 'a'}),
                (2, 3, {'label': 'c'}),
                (3, 4, {'label': 'd'}),
                (2, 4, {'label': 'b'})
            ]
        )

        valid_subgraph_a = nx.Graph()
        valid_subgraph_a.add_edge(1, 2, label='a')

        valid_subgraph_b = nx.Graph()
        valid_subgraph_b.add_edge(3, 4, label='d')

        valid_subgraph_c = nx.Graph()
        valid_subgraph_c.add_edge(2, 1, label='a')

        invalid_subgraph_a = nx.Graph()
        invalid_subgraph_a.add_edge(1, 2, label='b')

        invalid_subgraph_b = nx.Graph()
        invalid_subgraph_b.add_edge(1, 4, label='a')

        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_a))
        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_b))
        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_c))

        self.assertFalse(ParsemisMiner.is_subgraph(G, invalid_subgraph_a))
        self.assertFalse(ParsemisMiner.is_subgraph(G, invalid_subgraph_b))

    def test_digraph_is_subgraph_without_labels(self):
        G = nx.DiGraph()
        G.add_edges_from(
            [
                (1, 2),
                (2, 3),
                (3, 4),
                (2, 4)
            ]
        )

        valid_subgraph_a = nx.DiGraph()
        valid_subgraph_a.add_edge(1, 2)

        valid_subgraph_b = nx.DiGraph()
        valid_subgraph_b.add_edge(3, 4)

        invalid_subgraph_a = nx.DiGraph()
        invalid_subgraph_a.add_edge(1, 4)

        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_a))
        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_b))

        self.assertFalse(ParsemisMiner.is_subgraph(G, invalid_subgraph_a))

    def test_multidigraph_is_subgraph_without_labels(self):
        G = nx.MultiDiGraph()
        G.add_edges_from(
            [
                (1, 2),
                (2, 3),
                (3, 4),
                (2, 4)
            ]
        )

        valid_subgraph_a = nx.MultiDiGraph()
        valid_subgraph_a.add_edge(1, 2)

        valid_subgraph_b = nx.MultiDiGraph()
        valid_subgraph_b.add_edge(3, 4)

        invalid_subgraph_a = nx.MultiDiGraph()
        invalid_subgraph_a.add_edge(1, 4)

        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_a))
        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_b))

        self.assertFalse(ParsemisMiner.is_subgraph(G, invalid_subgraph_a))

    def test_graph_is_subgraph_without_labels(self):
        G = nx.Graph()
        G.add_edges_from(
            [
                (1, 2),
                (2, 3),
                (3, 4),
                (2, 4)
            ]
        )

        valid_subgraph_a = nx.Graph()
        valid_subgraph_a.add_edge(1, 2)

        valid_subgraph_b = nx.Graph()
        valid_subgraph_b.add_edge(3, 4)

        valid_subgraph_c = nx.Graph()
        valid_subgraph_c.add_edge(4, 3)

        invalid_subgraph_b = nx.Graph()
        invalid_subgraph_b.add_edge(1, 4)

        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_a))
        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_b))
        self.assertTrue(ParsemisMiner.is_subgraph(G, valid_subgraph_c))

        self.assertFalse(ParsemisMiner.is_subgraph(G, invalid_subgraph_b))

    def test_frequent_graph(self):
        G = nx.MultiDiGraph()
        G.add_edge(1, 2, label='a')
        G.add_edge(1, 2, label='b')

        fg = FrequentGraph(G, [])
        print("Name: %s" % fg.to_string())

    def test_similarity_when_same(self):
        super_graph = nx.Graph()
        super_graph.add_edge(1, 2, label='a')
        super_graph.add_edge(2, 3, label='b')

        sub_graph = super_graph.copy()

        self.assertEqual(ParsemisMiner.calculate_dot_product_similarity(super_graph, sub_graph), 1, 'Dot Product')
        self.assertEqual(ParsemisMiner.calculate_jaccard_similarity(super_graph, sub_graph), 1, 'Jaccard Similarity')

    def test_similarity_when_different(self):
        super_graph = nx.Graph()
        super_graph.add_edge(1, 2, label='a')
        super_graph.add_edge(2, 3, label='b')

        sub_graph = nx.Graph()
        sub_graph.add_edge(4, 5, label='c')
        sub_graph.add_edge(5, 6, label='d')

        self.assertEqual(ParsemisMiner.calculate_dot_product_similarity(super_graph, sub_graph), 0, 'Dot Product')
        self.assertEqual(ParsemisMiner.calculate_jaccard_similarity(super_graph, sub_graph), 0, 'Jaccard Similarity')

    def test_similairity_when_similiar(self):
        super_graph = nx.Graph()
        super_graph.add_edge(1, 2, label='a')
        super_graph.add_edge(2, 3, label='b')
        super_graph.add_edge(3, 4, label='c')

        sub_graph = nx.Graph()
        sub_graph.add_edge(2, 3, label='b')
        sub_graph.add_edge(2, 5, label='d')

        self.assertEqual(ParsemisMiner.calculate_dot_product_similarity(sub_graph, super_graph), 0.6, 'Dot Product')
        self.assertEqual(ParsemisMiner.calculate_jaccard_similarity(sub_graph, super_graph), 0.6, 'Jaccard Similarity')

    # def jaccard_similarity_is_one_when_same(self):
