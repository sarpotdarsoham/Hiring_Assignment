from flask import Flask, request, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase
from fuzzywuzzy import fuzz
import openai

app = Flask(__name__)
CORS(app)

uri = "bolt://localhost:7687"
username = "neo4j"
password = "Soham@1142000"
driver = GraphDatabase.driver(uri, auth=(username, password))

# Set up OpenAI API
openai.api_key = "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"

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
        print(f"Error querying knowledge graph: {e}")
        return []

def generate_gpt_response(query, kg_results):
    if kg_results:
        prompt = f"Query: {query}\nKnowledge Graph Results: {', '.join(kg_results)}\nPlease provide a comprehensive answer based on the query and the knowledge graph results:"
    else:
        prompt = f"Query: {query}\nNo relevant information was found in the knowledge graph. Please provide a comprehensive answer based on your knowledge:"

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides information based on a knowledge graph"},
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
    app.run(host='0.0.0.0', port=5001, debug=True)
