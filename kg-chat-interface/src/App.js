import React, { useState } from 'react';

function App() {
    const [query, setQuery] = useState("");
    const [response, setResponse] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        const res = await fetch('http://localhost:5001/query', {  // Update to port 5001
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });
        const data = await res.json();
        setResponse(data.answer);
    };

    return (
        <div style={{ padding: "20px" }}>
            <h1>Knowledge Graph Chat Interface</h1>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask a question..."
                    style={{ width: "300px", padding: "10px" }}
                />
                <button type="submit" style={{ padding: "10px", marginLeft: "10px" }}>Submit</button>
            </form>
            <div style={{ marginTop: "20px", padding: "10px", border: "1px solid #ccc", width: "320px" }}>
                <strong>Response:</strong>
                <p>{response}</p>
            </div>
        </div>
    );
}

export default App;
