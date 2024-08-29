from flask import Flask, request, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase

app = Flask(__name__)
CORS(app)

uri = "bolt://localhost:7687"
username = "neo4j"
password = "Soham@1142000"
driver = GraphDatabase.driver(uri, auth=(username, password))

@app.route('/query', methods=['POST'])
def query_kg():
    data = request.json
    query = data['query']

    with driver.session() as session:
        result = session.run(
            "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) RETURN n.name",
            name=query
        )
        answer = [record["n.name"] for record in result]

    return jsonify({'answer': ', '.join(answer)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)