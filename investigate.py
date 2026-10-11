
import os
from neo4j import GraphDatabase

from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

if not all([URI, USERNAME, PASSWORD]):
    raise SystemExit(
        "Missing Aura credentials. Set NEO4J_URI, "
        "NEO4J_USERNAME, and NEO4J_PASSWORD first."
    )

DATABASE = "neo4j"
MAX_PATH_LENGTH = 6

CHECK_REPORTS_QUERY = """
MATCH (r:Report)
WHERE r.id IN $ids
RETURN collect(r.id) AS found
"""

INVESTIGATION_QUERY = """
MATCH (a:Report {id: $start_id})
MATCH (b:Report {id: $target_id})
MATCH path = shortestPath((a)-[*..6]-(b))
RETURN
    [
        n IN nodes(path) |
        {
            labels: labels(n),
            identifier: coalesce(n.id, n.value, n.domain, n.address),
            category: n.category,
            reported_at: n.reported_at,
            summary: n.summary
        }
    ] AS evidence_nodes,
    [rel IN relationships(path) | type(rel)] AS relationship_types,
    length(path) AS path_length
LIMIT 1
"""


def investigate(session, start_id, target_id):
    # Check that both report IDs exist.
    check = session.run(
        CHECK_REPORTS_QUERY,
        ids=[start_id, target_id]
    ).single()

    found = set(check["found"])

    if start_id not in found:
        print(f"Report not found: {start_id}")
        return

    if target_id not in found:
        print(f"Report not found: {target_id}")
        return

    if start_id == target_id:
        print("Both IDs refer to the same report.")
        return

    # Search for the shortest connection path.
    result = session.run(
        INVESTIGATION_QUERY,
        start_id=start_id,
        target_id=target_id
    ).single()

    if result is None:
        print(
            f"No connection found between {start_id} and {target_id} "
            f"within {MAX_PATH_LENGTH} relationships."
        )
        return

    nodes = result["evidence_nodes"]
    relationship_types = result["relationship_types"]

    print("\n" + "=" * 55)
    print("TRUSTTRACE — INVESTIGATION RESULTS")
    print("=" * 55)
    print(f"Start report: {start_id}")
    print(f"Target report: {target_id}")
    print(f"Path length: {result['path_length']} relationships")
    print("\nEVIDENCE TRAIL")
    print("-" * 55)

    for index, node in enumerate(nodes):
        labels = node["labels"]
        identifier = node["identifier"]

        if "Report" in labels:
            print(f"\nREPORT: {identifier}")
            print(f"  Category: {node.get('category')}")
            print(f"  Date: {node.get('reported_at')}")
            print(f"  Summary: {node.get('summary')}")
        else:
            entity_type = ", ".join(labels)
            print(f"\nSHARED IDENTIFIER: {entity_type} = {identifier}")

        if index < len(relationship_types):
            rel_type = relationship_types[index]
            print(f"  --[{rel_type}]--")

    print("\n" + "=" * 55)
    print("Interpretation: this is a graph connection, not proof of wrongdoing.")
    print("=" * 55)


def main():
    start_id = input("Enter starting report ID (e.g. R0001): ").strip().upper()
    target_id = input("Enter target report ID (e.g. R0004): ").strip().upper()

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:
        driver.verify_connectivity()
        print("\nConnected to Neo4j Aura.")

        with driver.session(database=DATABASE) as session:
            investigate(session, start_id, target_id)

    except Exception as error:
        print("\nSomething went wrong while connecting or querying Neo4j.")
        print(f"Error: {error}")
        print("Check your Aura credentials, network connection, and database status.")

    finally:
        driver.close()


if __name__ == "__main__":
    main()
