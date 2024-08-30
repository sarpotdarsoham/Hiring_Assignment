import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase
from fuzzywuzzy import fuzz
import openai
import subprocess
import logging

app = Flask(__name__)
CORS(app)

uri = "bolt://localhost:7687"
username = "neo4j"
password = "Soham@1142000"
driver = GraphDatabase.driver(uri, auth=(username, password))
openai.api_key = "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"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_graph():
    with driver.session() as session:
        session.execute_write(lambda tx: tx.run("MATCH (n) DETACH DELETE n"))
        logger.info("\n--- Existing graph cleared ---\n")


def trigger_data_scraping(topic):
    try:
        logger.info(f"\n--- Starting data scraping process for topic: {topic} ---\n")
        result = subprocess.run(['python3', 'scrape_data.py', topic], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"\n--- Data scraping process for topic '{topic}' completed successfully ---\n")
            logger.info(result.stdout)
        else:
            logger.error(f"\n--- Error in data scraping for topic '{topic}' ---\n{result.stderr}")
    except Exception as e:
        logger.error(f"\n--- Failed to trigger data scraping for topic '{topic}' ---\n{str(e)}")


def trigger_kg_build():
    try:
        logger.info("\n--- Starting Knowledge Graph build process ---\n")
        result = subprocess.run(['python3', 'build_kg.py'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("\n--- Knowledge Graph build process completed successfully ---\n")
            logger.info(result.stdout)
        else:
            logger.error(f"\n--- Error in building Knowledge Graph ---\n{result.stderr}")
    except Exception as e:
        logger.error(f"\n--- Failed to trigger Knowledge Graph build ---\n{str(e)}")


def query_knowledge_graph(query):
    try:
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN n.name")
            all_names = [record["n.name"] for record in result]

            close_matches = []
            for name in all_names:
                ratio = fuzz.ratio(query.lower(), name.lower())
                if ratio > 20:
                    close_matches.append(name)

            if not close_matches:
                result = session.run(
                    "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) RETURN n.name",
                    name=query
                )
                return [record["n.name"] for record in result]
            else:
                return close_matches
    except Exception as e:
        logger.error(f"\n--- Error querying knowledge graph: {e} ---\n")
        return []

def generate_gpt_response(query, kg_results):
    if kg_results:
        prompt = f"Query: {query}\nKnowledge Graph Results: {', '.join(kg_results)}\nPlease provide a comprehensive answer based on the query and the knowledge graph results:"
    else:
        prompt = f"Query: {query}\nNo relevant information was found in the knowledge graph. Please provide a comprehensive answer based on your knowledge:"

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides information based on a knowledge graph about the queried topic."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    
    return response.choices[0].message['content'].strip()

@app.route('/query', methods=['POST'])
def query_kg():
    data = request.json
    query = data.get('query', "").strip()

    if not query:
        return jsonify({'answer': 'Query cannot be empty'}), 400

    kg_results = query_knowledge_graph(query)
    
    if kg_results:
        gpt_response = generate_gpt_response(query, kg_results)
        answer = f"Based on the knowledge graph: {gpt_response}"
    else:
        gpt_response = generate_gpt_response(query, [])
        answer = f"No relevant information found in the knowledge graph. However, here's what I found: {gpt_response}"

    return jsonify({'answer': answer})

if __name__ == '__main__':
    if len(sys.argv) > 1:
        topic = sys.argv[1]
        trigger_data_scraping(topic)
        clear_graph()
        trigger_kg_build()
    
    app.run(host='0.0.0.0', port=5001, debug=True)
