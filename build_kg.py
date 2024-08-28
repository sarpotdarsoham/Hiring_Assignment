from neo4j import GraphDatabase

# Update with your new Neo4j credentials
uri = "bolt://localhost:7687"
username = "neo4j"  # Default username is usually neo4j
password = "Soham@1142000"

# Create the driver with your credentials
driver = GraphDatabase.driver(uri, auth=(username, password))

def create_node(tx, label, name):
    tx.run("CREATE (a:"+label+" {name: $name})", name=name)

def create_relationship(tx, node1, rel, node2):
    tx.run("MATCH (a {name: $node1_name}), (b {name: $node2_name}) "
           "CREATE (a)-[:"+rel+"]->(b)",
           node1_name=node1, node2_name=node2)

def build_knowledge_graph(data_file):
    with driver.session() as session:
        # Creating nodes and relationships
        session.execute_write(create_node, "Company", "Altera")
        session.execute_write(create_node, "Company", "Intel")
        session.execute_write(create_node, "Product", "FPGA")
        session.execute_write(create_node, "Product", "System on a Chip")
        session.execute_write(create_node, "Industry", "Semiconductor")
        session.execute_write(create_node, "Industry", "Programmable Logic Devices")
        session.execute_write(create_node, "Event", "Acquisition by Intel")
        session.execute_write(create_node, "Event", "Initial Public Offering (IPO)")
        session.execute_write(create_node, "Event", "Spinoff of PSG")
        session.execute_write(create_node, "Event", "Reestablishment of Altera")
        session.execute_write(create_node, "Person", "Rodney Smith")
        session.execute_write(create_node, "Person", "Robert Hartmann")
        session.execute_write(create_node, "Person", "James Sansbury")
        session.execute_write(create_node, "Person", "Paul Newhagen")
        session.execute_write(create_relationship, "Altera", "PRODUCES", "FPGA")
        session.execute_write(create_relationship, "Altera", "PRODUCES", "System on a Chip")
        session.execute_write(create_relationship, "Altera", "BELONGS_TO", "Semiconductor")
        session.execute_write(create_relationship, "Altera", "FOCUSES_ON", "Programmable Logic Devices")
        session.execute_write(create_relationship, "Altera", "ACQUIRED_BY", "Intel")
        session.execute_write(create_relationship, "Altera", "FOUNDED_BY", "Rodney Smith")
        session.execute_write(create_relationship, "Altera", "FOUNDED_BY", "Robert Hartmann")
        session.execute_write(create_relationship, "Altera", "FOUNDED_BY", "James Sansbury")
        session.execute_write(create_relationship, "Altera", "FOUNDED_BY", "Paul Newhagen")
        session.execute_write(create_relationship, "Altera", "UNDERWENT", "Acquisition by Intel")
        session.execute_write(create_relationship, "Altera", "UNDERWENT", "Initial Public Offering (IPO)")
        session.execute_write(create_relationship, "Altera", "UNDERWENT", "Spinoff of PSG")
        session.execute_write(create_relationship, "Intel", "SPUN_OFF", "Spinoff of PSG")
        session.execute_write(create_relationship, "Intel", "REESTABLISHED", "Reestablishment of Altera")

if __name__ == "__main__":
    data_file = "extracted_data.txt"  # Your extracted data file (not used in this example, but available for extension)
    build_knowledge_graph(data_file)
