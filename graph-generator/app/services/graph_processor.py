import networkx as nx
from app.core.database import neo4j_driver


def generate_dependency_graph():
    graph = nx.DiGraph()
    graph.add_edge("service-a", "service-b", weight=3)
    graph.add_edge("service-b", "service-c", weight=2)
    return nx.node_link_data(graph)


def save_dependency_graph_to_neo4j(graph):
    with neo4j_driver.session() as session:
        for node in graph["nodes"]:
            session.run("MERGE (:Service {name: $name})", name=node["id"])
        for link in graph["links"]:
            session.run(
                """
                MATCH (a:Service {name: $source}), (b:Service {name: $target})
                MERGE (a)-[:CALLS {weight: $weight}]->(b)
                """,
                source=link["source"], target=link["target"], weight=link["value"]
            )
