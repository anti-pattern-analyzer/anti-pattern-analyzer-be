import networkx as nx
from networkx.readwrite import json_graph
from app.core.database import db_manager


def generate_weighted_graph_from_traces(traces):
    """
    Generate a weighted dependency graph from new traces, including enhanced metrics for analysis.
    """
    graph = nx.DiGraph()

    if not isinstance(traces, list):
        raise ValueError("Expected 'traces' to be a list of trace objects.")

    for trace in traces:
        processes = trace.get("processes", {})
        spans = trace.get("spans", [])

        # Validate processes and spans
        if not isinstance(processes, dict):
            raise ValueError(f"Invalid processes structure: {processes}")
        if not isinstance(spans, list):
            raise ValueError(f"Invalid spans structure: {spans}")

        # Map process IDs to service names
        process_to_service = {
            pid: details.get("serviceName", f"unknown-{pid}")
            for pid, details in processes.items()
            if isinstance(details, dict)
        }

        # Process spans to build relationships
        for span in spans:
            process_id = span.get("processID")
            if not process_id or process_id not in process_to_service:
                continue  # Skip spans with missing or invalid process IDs

            parent_span_id = None
            for ref in span.get("references", []):
                if ref.get("refType") == "CHILD_OF":
                    parent_span_id = ref.get("spanID")
                    break

            if parent_span_id:
                child_service = process_to_service[process_id]
                parent_span = next((s for s in spans if s.get("spanID") == parent_span_id), None)
                if parent_span:
                    parent_process_id = parent_span.get("processID")
                    parent_service = process_to_service.get(parent_process_id)
                    if parent_service and parent_service != child_service:
                        # Extract latency and error information
                        latency = span.get("duration", 0)  # Default duration to 0 if missing
                        error = any(tag.get("key") == "error" and tag.get("value") for tag in span.get("tags", []))

                        # Update graph with enhanced metadata
                        if graph.has_edge(parent_service, child_service):
                            graph[parent_service][child_service]["weight"] += 1
                            graph[parent_service][child_service]["latency_sum"] += latency
                            graph[parent_service][child_service]["error_count"] += 1 if error else 0
                        else:
                            graph.add_edge(
                                parent_service,
                                child_service,
                                weight=1,
                                latency_sum=latency,
                                error_count=1 if error else 0,
                            )

    # Add degree metrics to nodes
    for node in graph.nodes:
        graph.nodes[node]["in_degree"] = graph.in_degree(node)
        graph.nodes[node]["out_degree"] = graph.out_degree(node)

    return graph


def update_graph_in_neo4j(graph):
    """
    Update the dependency graph in Neo4j using the provided NetworkX graph.
    """
    with db_manager.neo4j_driver.session() as session:
        for edge in graph.edges(data=True):
            parent, child, attributes = edge
            weight = attributes.get("weight", 1)
            latency_sum = attributes.get("latency_sum", 0)
            error_count = attributes.get("error_count", 0)

            # Create or update nodes and relationships in Neo4j
            session.run("""
                MERGE (a:Service {name: $parent})
                MERGE (b:Service {name: $child})
                MERGE (a)-[r:CALLS]->(b)
                ON CREATE SET 
                    r.weight = $weight, 
                    r.latency_sum = $latency_sum, 
                    r.error_count = $error_count,
                    r.avg_latency = CASE WHEN $weight > 0 THEN $latency_sum / $weight ELSE 0 END
                ON MATCH SET 
                    r.weight = r.weight + $weight, 
                    r.latency_sum = r.latency_sum + $latency_sum, 
                    r.error_count = r.error_count + $error_count,
                    r.avg_latency = CASE WHEN (r.weight + $weight) > 0 THEN (r.latency_sum + $latency_sum) / (r.weight + $weight) ELSE 0 END
            """, parent=parent, child=child, weight=weight, latency_sum=latency_sum, error_count=error_count)


def fetch_graph_from_neo4j():
    """
    Fetch the dependency graph from Neo4j and return it as a NetworkX graph object with enhanced metrics.
    """
    graph = nx.DiGraph()

    try:
        with db_manager.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (a:Service)-[r:CALLS]->(b:Service)
                RETURN 
                    a.name AS parent, 
                    b.name AS child, 
                    r.weight AS weight, 
                    r.latency_sum AS latency_sum, 
                    r.error_count AS error_count, 
                    r.avg_latency AS avg_latency
            """)

            for record in result:
                parent = record["parent"]
                child = record["child"]
                weight = record["weight"]
                latency_sum = record.get("latency_sum", 0)
                error_count = record.get("error_count", 0)
                avg_latency = record.get("avg_latency", 0)

                # Add the edge with the fetched attributes
                graph.add_edge(
                    parent,
                    child,
                    weight=weight,
                    latency_sum=latency_sum,
                    error_count=error_count,
                    avg_latency=avg_latency
                )

    except Exception as e:
        print(f"Error fetching graph from Neo4j: {e}")

    return graph


def get_graph_data_as_json():
    """
    Retrieve the dependency graph as JSON-compatible data for API or frontend consumption.
    """
    graph = fetch_graph_from_neo4j()
    return json_graph.node_link_data(graph)


def get_anti_patterns_using_graph_data(graph_data):
    """
    Analyze the graph data to identify anti-patterns.
    Returns a list of detected anti-patterns with details.
    """
    anti_patterns = []

    # Reconstruct the graph using networkx
    graph = json_graph.node_link_graph(graph_data)

    # Calculate in-degree and out-degree for each node
    for node in graph.nodes:
        graph.nodes[node]["in_degree"] = graph.in_degree(node)
        graph.nodes[node]["out_degree"] = graph.out_degree(node)

    # 1. Detect Cyclic Dependencies
    try:
        cycles = list(nx.simple_cycles(graph))
        if cycles:
            anti_patterns.append({
                "type": "Cyclic Dependency",
                "severity": "High",
                "details": [{"cycle": cycle} for cycle in cycles],
                "recommendations": [
                    "Refactor cyclic dependencies by introducing intermediary services.",
                    "Consider using a message broker to decouple direct service calls.",
                    "Perform architectural reviews to identify and prevent future cyclic dependencies."
                ]
            })
    except Exception as e:
        print(f"Error detecting cycles: {e}")

    # 2. Detect High Fan-Out
    high_fan_out_services = [
        {"service": node, "out_degree": graph.nodes[node]["out_degree"]}
        for node in graph.nodes
        if graph.nodes[node]["out_degree"] > 5  # Threshold for high fan-out
    ]

    if high_fan_out_services:
        anti_patterns.append({
            "type": "High Fan-Out",
            "severity": "Medium",
            "details": high_fan_out_services,
            "recommendations": [
                "Reduce the number of downstream dependencies by merging or eliminating unnecessary calls.",
                "Implement caching or data aggregation to reduce direct dependency on downstream services.",
                "Introduce a dedicated service to handle common requests from multiple services."
            ]
        })

    # 3. Detect Excessive Dependencies
    excessive_dependency_services = [
        {"service": node, "in_degree": graph.nodes[node]["in_degree"]}
        for node in graph.nodes
        if graph.nodes[node]["in_degree"] > 5  # Threshold for excessive dependencies
    ]

    if excessive_dependency_services:
        anti_patterns.append({
            "type": "Excessive Dependency",
            "severity": "Medium",
            "details": excessive_dependency_services,
            "recommendations": [
                "Identify critical dependencies and evaluate if they can be reduced.",
                "Introduce service abstractions or APIs to consolidate dependencies.",
                "Regularly review service dependencies to avoid unnecessary complexity."
            ]
        })

    # 4. Detect Service Bottlenecks
    bottleneck_services = [
        {"source": edge[0], "target": edge[1], "request_rate": edge[2]["weight"], "avg_latency": edge[2]["latency_sum"] / edge[2]["weight"]}
        for edge in graph.edges(data=True)
        if edge[2]["weight"] > 50 or edge[2]["latency_sum"] / edge[2]["weight"] > 1000  # Example thresholds
    ]

    if bottleneck_services:
        anti_patterns.append({
            "type": "Service Bottleneck",
            "severity": "High",
            "details": bottleneck_services,
            "recommendations": [
                "Scale the bottleneck service horizontally or vertically to meet demand.",
                "Optimize resource usage through performance tuning and profiling.",
                "Distribute requests using load balancers to reduce the load on a single service."
            ]
        })

    return anti_patterns
