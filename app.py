from flask import Flask, request, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase
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
    with driver.session() as session:
        result = session.run(
            "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) RETURN n.name",
            name=query
        )
        return [record["n.name"] for record in result]

def generate_gpt_response(query, kg_results):
    prompt = f"Query: {query}\nKnowledge Graph Results: {', '.join(kg_results)}\nPlease provide a comprehensive answer based on the query and the knowledge graph results:"
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Using GPT-4o mini instead of GPT-3.5 Turbo
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides information based on a knowledge graph about Altera FPGA and related topics."},
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
    query = data['query']

    kg_results = query_knowledge_graph(query)
    
    if kg_results:
        gpt_response = generate_gpt_response(query, kg_results)
        answer = f"Based on the knowledge graph and additional context: {gpt_response}"
    else:
        answer = "No relevant information found in the knowledge graph."

    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)