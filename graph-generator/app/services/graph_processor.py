import networkx as nx


def generate_dependency_graph():
    graph = nx.DiGraph()
    graph.add_edge("service-a", "service-b", weight=3)
    graph.add_edge("service-b", "service-c", weight=2)
    return nx.node_link_data(graph)
