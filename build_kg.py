import spacy
import re
import logging
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

uri = "bolt://localhost:7687"
username = "neo4j"
password = "Soham@1142000"
driver = GraphDatabase.driver(uri, auth=(username, password))

nlp = spacy.load("en_core_web_trf")

def clean_entity_name(name):
    name = re.sub(r"[^\w\s,.-]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name.lower()

def create_node(tx, label, name, properties=None):
    if properties is None:
        properties = {}
    properties['name'] = name
    query = f"MERGE (a:{label} {{name: $name}}) SET a += $properties"
    tx.run(query, name=name, properties=properties)
    logger.info(f"Node created: ({label}: {name})")

def create_relationship(tx, source_label, source_name, target_label, target_name, relationship_type):
    source_name = source_name.strip().lower()
    target_name = target_name.strip().lower()
    source_label = source_label.strip().capitalize()
    target_label = target_label.strip().capitalize()

    # Check if both nodes exist
    check_query = f"""
    MATCH (a:{source_label} {{name: $source_name}})
    MATCH (b:{target_label} {{name: $target_name}})
    RETURN a, b
    """
    result = tx.run(check_query, source_name=source_name, target_name=target_name).single()

    if result:
        query = f"""
        MATCH (a:{source_label} {{name: $source_name}})
        MATCH (b:{target_label} {{name: $target_name}})
        MERGE (a)-[r:{relationship_type}]->(b)
        RETURN r
        """
        tx.run(query, source_name=source_name, target_name=target_name)
        logger.info(f"Relationship created: ({source_label}: '{source_name}') -[{relationship_type}]-> ({target_label}: '{target_name}')")
    else:
        logger.warning(f"Nodes not found: {source_label} '{source_name}' or {target_label} '{target_name}'. Relationship '{relationship_type}' not created.")

def determine_relationship(token):
    if token.dep_ == "nsubj" and token.head.lemma_ in {"manufacture", "produce", "create", "develop"}:
        return "MANUFACTURES"
    elif token.dep_ == "dobj" and token.head.lemma_ in {"create", "develop", "invent", "design"}:
        return "CREATES"
    elif token.dep_ == "pobj" and token.head.lemma_ in {"in", "located", "based"}:
        return "LOCATED_IN"
    elif token.dep_ == "prep" and token.head.lemma_ in {"with", "using"}:
        return "USES"
    elif token.dep_ == "agent" and token.head.lemma_ in {"lead", "head"}:
        return "LEADS"
    elif token.dep_ == "pobj" and token.head.lemma_ in {"part", "include", "feature"}:
        return "INCLUDES"
    return "RELATED_TO"

def extract_entities_and_relationships(text):
    doc = nlp(text)
    entities = []
    relationships = []

    for ent in doc.ents:
        if ent.label_ in {"ORG", "PRODUCT", "PERSON", "GPE", "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE"}:
            clean_name = clean_entity_name(ent.text)
            if len(clean_name) > 2:
                label = ent.label_.capitalize()
                entities.append((clean_name, label))

    for token in doc:
        if token.dep_ in ("nsubj", "dobj", "pobj", "prep"):
            subject = token.head
            if subject.ent_type_ and token.ent_type_:
                relationship_type = determine_relationship(token)
                relationships.append((subject.text, subject.ent_type_, token.text, token.ent_type_, relationship_type))

    logger.info(f"Entities extracted: {entities}")
    logger.info(f"Relationships extracted: {relationships}")
    
    return list(set(entities)), list(set(relationships))


def build_knowledge_graph_in_batches(file_path, batch_size=100):
    with driver.session() as session:
        with open(file_path, "r") as file:
            entities_batch = []
            relationships_batch = []
            for chunk in iter(lambda: file.read(4096), ''):
                entities, relationships = extract_entities_and_relationships(chunk)
                entities_batch.extend(entities)
                relationships_batch.extend(relationships)
                
                if len(entities_batch) >= batch_size:
                    session.write_transaction(lambda tx: batch_create_nodes(tx, entities_batch))
                    entities_batch = []

                if len(relationships_batch) >= batch_size:
                    session.write_transaction(lambda tx: batch_create_relationships(tx, relationships_batch))
                    relationships_batch = []

            if entities_batch:
                session.write_transaction(lambda tx: batch_create_nodes(tx, entities_batch))
            if relationships_batch:
                session.write_transaction(lambda tx: batch_create_relationships(tx, relationships_batch))

def batch_create_nodes(tx, entities):
    for entity, label in entities:
        create_node(tx, label, entity)

def batch_create_relationships(tx, relationships):
    for entity1, label1, entity2, label2, rel_type in relationships:
        if entity1 != entity2:
            create_relationship(tx, label1, entity1, label2, entity2, rel_type)

def clear_graph():
    with driver.session() as session:
        session.write_transaction(lambda tx: tx.run("MATCH (n) DETACH DELETE n"))
        logger.info("Existing graph cleared.")

if __name__ == "__main__":
    data_file = "extracted_data.txt"
    
    clear_graph()

    build_knowledge_graph_in_batches(data_file, batch_size=50)

    logger.info("Knowledge graph built and analyzed successfully!")
