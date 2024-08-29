import spacy
import re
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "Soham@1142000"
driver = GraphDatabase.driver(uri, auth=(username, password))

nlp = spacy.load("en_core_web_trf")

def create_node(tx, label, name, properties=None):
    if properties is None:
        properties = {}
    properties['name'] = name
    query = f"MERGE (a:{label} {{name: $name}}) SET a += $properties"
    tx.run(query, name=name, properties=properties)
    print(f"Node created: ({label}: {name})")

def create_relationship(tx, source_label, source_name, target_label, target_name, relationship_type):
    source_name = source_name.strip().lower()
    target_name = target_name.strip().lower()
    print(f"Attempting to create relationship: ({source_label}: '{source_name}') -[{relationship_type}]-> ({target_label}: '{target_name}')")
    query = f"""
    MATCH (a:{source_label} {{name: $source_name}})
    MATCH (b:{target_label} {{name: $target_name}})
    MERGE (a)-[r:{relationship_type}]->(b)
    RETURN r
    """
    result = tx.run(query, source_name=source_name, target_name=target_name)
    print(f"Relationship creation result: {result.consume().counters}")


def clean_entity_name(name):
    name = re.sub(r"[^\w\s,.-]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name

def extract_entities_and_relationships(text):
    doc = nlp(text)
    entities = []
    relationships = []

    for ent in doc.ents:
        if ent.label_ in {"ORG", "PRODUCT", "PERSON", "GPE", "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE"}:
            clean_name = clean_entity_name(ent.text)
            if len(clean_name) > 2:
                entities.append((clean_name, ent.label_))

    for token in doc:
        if token.dep_ in ("nsubj", "dobj", "pobj"):
            subject = token.head
            if subject.ent_type_ and token.ent_type_:
                relationship_type = determine_relationship(subject.ent_type_, token.ent_type_)
                relationships.append((subject.text, subject.ent_type_, token.text, token.ent_type_, relationship_type))

    print(f"Entities extracted: {len(entities)}")
    print(f"Relationships extracted: {len(relationships)}")
    
    return list(set(entities)), list(set(relationships))

def determine_relationship(ent1_label, ent2_label):
    if ent1_label == "PERSON" and ent2_label == "PRODUCT":
        return "CREATED"
    elif ent1_label == "ORG" and ent2_label == "PRODUCT":
        return "MANUFACTURES"
    elif ent1_label == "GPE" and ent2_label == "ORG":
        return "LOCATED_IN"
    elif ent1_label == "PRODUCT" and ent2_label == "PRODUCT":
        return "COMPATIBLE_WITH"
    return "RELATED_TO"

def build_knowledge_graph_in_chunks(file_path, chunk_size=1024):
    with driver.session() as session:
        with open(file_path, "r") as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                entities, relationships = extract_entities_and_relationships(chunk)
                
                for entity, label in entities:
                    session.execute_write(create_node, label, entity)
                
                for entity1, label1, entity2, label2, rel_type in relationships:
                    if entity1 != entity2:
                        session.execute_write(create_relationship, label1, entity1, label2, entity2, rel_type)

def clear_graph():
    with driver.session() as session:
        session.execute_write(lambda tx: tx.run("MATCH (n) DETACH DELETE n"))
        print("Existing graph cleared.")

if __name__ == "__main__":
    data_file = "extended_extracted_data.txt"
    
    clear_graph()

    build_knowledge_graph_in_chunks(data_file, chunk_size=4096)

    print("Knowledge graph built and analyzed successfully!")
