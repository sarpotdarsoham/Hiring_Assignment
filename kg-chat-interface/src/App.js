import React, { useState } from 'react';
import './App.css';  // Import the new CSS file

function App() {
    const [query, setQuery] = useState("");
    const [response, setResponse] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        const res = await fetch('http://localhost:5001/query', {
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
        <div className="app-container">
            <h1>Knowledge Graph Chat Interface</h1>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask a question..."
                />
                <button type="submit">Submit</button>
            </form>
            <div className="response-container">
                <strong>Response:</strong>
                <p>{response}</p>
            </div>
        </div>
    );
}

export default App;
