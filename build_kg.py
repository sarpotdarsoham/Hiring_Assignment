import spacy
import re
from neo4j import GraphDatabase
import networkx as nx
from collections import defaultdict

# Neo4j connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "Soham@1142000"
driver = GraphDatabase.driver(uri, auth=(username, password))

# Load the SpaCy model for NER
nlp = spacy.load("en_core_web_sm")

def create_node(tx, label, name, properties=None):
    if properties is None:
        properties = {}
    properties['name'] = name
    query = f"MERGE (a:{label} {{name: $name}}) SET a += $properties"
    tx.run(query, name=name, properties=properties)

def create_relationship(tx, source_label, source_name, target_label, target_name, relationship_type):
    query = f"""
    MATCH (a:{source_label} {{name: $source_name}})
    MATCH (b:{target_label} {{name: $target_name}})
    MERGE (a)-[r:{relationship_type}]->(b)
    """
    tx.run(query, source_name=source_name, target_name=target_name)

def clean_entity_name(name):
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name

def extract_entities(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        if ent.label_ in {"ORG", "PRODUCT", "PERSON", "GPE", "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE"}:
            clean_name = clean_entity_name(ent.text)
            if len(clean_name) > 2:
                entities.append((clean_name, ent.label_))
    return list(set(entities))  # Remove duplicates

def build_knowledge_graph(data_file):
    with driver.session() as session:
        with open(data_file, "r") as file:
            text = file.read()
            entities = extract_entities(text)
            
            # Create nodes
            for entity, label in entities:
                session.execute_write(create_node, label, entity)
            
            # Create relationships
            for i, (entity1, label1) in enumerate(entities):
                for entity2, label2 in entities[i+1:]:
                    if entity1 != entity2:
                        session.execute_write(create_relationship, label1, entity1, label2, entity2, "RELATED_TO")

def clear_graph(tx):
    tx.run("MATCH (n) DETACH DELETE n")

def get_graph_data(tx):
    result = tx.run("""
    MATCH (n)-[r]->(m)
    RETURN n.name AS source, m.name AS target, type(r) AS relationship
    """)
    return [(record["source"], record["target"], record["relationship"]) for record in result]

def build_networkx_graph(graph_data):
    G = nx.Graph()
    for source, target, relationship in graph_data:
        G.add_edge(source, target, relationship=relationship)
    return G

def calculate_pagerank(G):
    return nx.pagerank(G)

def detect_communities(G):
    return nx.community.louvain_communities(G)

def update_node_properties(tx, node_name, pagerank, community):
    query = """
    MATCH (n {name: $name})
    SET n.pagerank = $pagerank, n.community = $community
    """
    tx.run(query, name=node_name, pagerank=pagerank, community=community)

if __name__ == "__main__":
    data_file = "extended_extracted_data.txt"
    
    with driver.session() as session:
        # Clear existing graph
        session.execute_write(clear_graph)
        
        # Build new graph
        build_knowledge_graph(data_file)
        
        # Get graph data for NetworkX
        graph_data = session.execute_read(get_graph_data)
        
        # Build NetworkX graph
        G = build_networkx_graph(graph_data)
        
        # Calculate PageRank
        pagerank = calculate_pagerank(G)
        
        # Detect communities
        communities = detect_communities(G)
        
        # Create a mapping of nodes to their community
        node_community = {}
        for i, community in enumerate(communities):
            for node in community:
                node_community[node] = i
        
        # Update Neo4j with PageRank and community information
        for node, pr in pagerank.items():
            community = node_community.get(node, -1)  # -1 if node is not in any community
            session.execute_write(update_node_properties, node, pr, community)

print("Knowledge graph built and analyzed successfully!")