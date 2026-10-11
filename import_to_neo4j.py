
import csv
import os
from pathlib import Path
from neo4j import GraphDatabase

from dotenv import load_dotenv

load_dotenv()

# Read credentials from environment variables.
URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

if not all([URI, USERNAME, PASSWORD]):
    raise SystemExit(
        "Missing Aura credentials. Set NEO4J_URI, "
        "NEO4J_USERNAME and NEO4J_PASSWORD first."
    )

CSV_FILE = Path("data/reports.csv")
DATABASE = "neo4j"
BATCH_SIZE = 100

if not CSV_FILE.exists():
    raise SystemExit(
        f"Dataset not found: {CSV_FILE}. "
        "Run generate_dataset.py first."
    )

# Each identifier has a uniqueness constraint.
CONSTRAINTS = [
    """
    CREATE CONSTRAINT report_id_unique IF NOT EXISTS
    FOR (r:Report) REQUIRE r.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT phone_value_unique IF NOT EXISTS
    FOR (p:PhoneNumber) REQUIRE p.value IS UNIQUE
    """,
    """
    CREATE CONSTRAINT website_domain_unique IF NOT EXISTS
    FOR (w:Website) REQUIRE w.domain IS UNIQUE
    """,
    """
    CREATE CONSTRAINT email_address_unique IF NOT EXISTS
    FOR (e:Email) REQUIRE e.address IS UNIQUE
    """,
]

IMPORT_QUERY = """
UNWIND $rows AS row

MERGE (r:Report {id: row.report_id})
SET r.reported_at = row.reported_at,
    r.category = row.category,
    r.summary = row.summary

MERGE (p:PhoneNumber {value: row.phone_id})
MERGE (w:Website {domain: row.website_domain})
MERGE (e:Email {address: row.email_id})

MERGE (r)-[:MENTIONS_PHONE]->(p)
MERGE (r)-[:MENTIONS_WEBSITE]->(w)
MERGE (r)-[:MENTIONS_EMAIL]->(e)
"""

def read_csv_batches():
    """Yield CSV rows in manageable batches."""
    with CSV_FILE.open(
        "r", encoding="utf-8", newline=""
    ) as file:
        reader = csv.DictReader(file)
        required = {
            "report_id",
            "reported_at",
            "category",
            "summary",
            "phone_id",
            "website_domain",
            "email_id",
        }

        if not required.issubset(reader.fieldnames or []):
            raise ValueError(
                "CSV is missing required columns."
            )

        batch = []
        for row in reader:
            batch.append({
                key: row[key]
                for key in required
            })

            if len(batch) >= BATCH_SIZE:
                yield batch
                batch = []

        if batch:
            yield batch

def main():
    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:
        driver.verify_connectivity()
        print("Connected to Neo4j Aura.")

        with driver.session(database=DATABASE) as session:
            # Create constraints before importing.
            for statement in CONSTRAINTS:
                session.run(statement).consume()

            print("Uniqueness constraints are ready.")

            total = 0

            for batch in read_csv_batches():
                session.execute_write(
                    lambda tx, rows: tx.run(
                        IMPORT_QUERY,
                        rows=rows
                    ).consume(),
                    batch
                )
                total += len(batch)
                print(f"Imported {total} reports...")

            print(f"\nImport complete: {total} CSV rows processed.")

            result = session.run("""
                MATCH (r:Report)
                RETURN count(r) AS total
            """).single()

            print(
                "Total Report nodes in Aura:",
                result["total"]
            )

    finally:
        driver.close()

if __name__ == "__main__":
    main()
