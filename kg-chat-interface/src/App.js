import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import botAvatar from './bot-avatar.jpg';
import userAvatar from './user.png';

const ChatMessage = ({ message, isUser }) => (
  <div className={`chat-message ${isUser ? 'user-message' : 'bot-message'}`}>
    <img 
      src={isUser ? userAvatar : botAvatar}
      alt={isUser ? 'User' : 'Bot'} 
      className="avatar"
    />
    <div className="message-content">
      <p>{message}</p>
    </div>
  </div>
);

const TypingIndicator = () => (
  <div className="typing-indicator">
    <img src={botAvatar} alt="Bot" className="avatar" />
    <div className="typing-dots">
      <div></div>
      <div></div>
      <div></div>
    </div>
  </div>
);

function App() {
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setChatHistory(prev => [...prev, { message: query, isUser: true }]);
    setQuery('');
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:5001/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      
      setTimeout(() => {
        setIsLoading(false);
        setChatHistory(prev => [...prev, { message: data.answer, isUser: false }]);
      }, 500 + Math.random() * 1000); // Simulate varying response times
    } catch (error) {
      console.error('Error fetching response:', error);
      setIsLoading(false);
      setChatHistory(prev => [...prev, { message: `Error: ${error.message}. Please try again.`, isUser: false }]);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AI Knowledge Graph Chat</h1>
      </header>
      <div className="chat-container" ref={chatContainerRef}>
        {chatHistory.map((chat, index) => (
          <ChatMessage key={index} message={chat.message} isUser={chat.isUser} />
        ))}
        {isLoading && <TypingIndicator />}
      </div>
      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask me anything..."
          className="chat-input"
        />
        <button type="submit" className="send-button" disabled={isLoading}>
          Send
        </button>
      </form>
    </div>
  );
}

export default App;