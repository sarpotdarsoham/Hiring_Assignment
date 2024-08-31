import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import botAvatar from './bot-avatar.jpg';
import userAvatar from './user.png';

const ChatMessage = ({ message, isUser, isTyping }) => (
  <div className={`chat-message ${isUser ? 'user-message' : 'bot-message'}`}>
    <img 
      src={isUser ? userAvatar : botAvatar}
      alt={isUser ? 'User' : 'Bot'} 
      className="avatar"
    />
    <div className="message-content">
      <p>{message}</p>
      {isTyping && (
        <div className="typing-dots">
          <div></div>
          <div></div>
          <div></div>
        </div>
      )}
    </div>
  </div>
);

function App() {
  const [query, setQuery] = useState('');
  const [topic, setTopic] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isBuildingKG, setIsBuildingKG] = useState(false);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const handleTopicSubmit = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setIsLoading(true);
    setIsBuildingKG(true);
    setChatHistory(prev => [
      ...prev, 
      { message: `Building Knowledge Graph for "${topic}"`, isUser: false, isTyping: true }
    ]);

    try {
      const res = await fetch('http://localhost:5001/set_topic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      setChatHistory(prev => [
        ...prev.slice(0, -1),
        { message: `Knowledge Graph for "${topic}" built successfully! You can now start asking questions.`, isUser: false, isTyping: false }
      ]);
    } catch (error) {
      console.error('Error setting topic:', error);
      setChatHistory(prev => [
        ...prev.slice(0, -1),
        { message: `Error: ${error.message}. Please try again.`, isUser: false, isTyping: false }
      ]);
    } finally {
      setIsLoading(false);
      setIsBuildingKG(false);
    }
  };

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
        setChatHistory(prev => [...prev, { message: data.answer, isUser: false, isTyping: false }]);
      }, 500 + Math.random() * 1000);
    } catch (error) {
      console.error('Error fetching response:', error);
      setIsLoading(false);
      setChatHistory(prev => [
        ...prev, 
        { message: `Error: ${error.message}. Please try again.`, isUser: false, isTyping: false }
      ]);
    }
  };

  const handleDownload = async () => {
    try {
      const fileName = prompt("Enter the name for the downloaded file (without extension):", "chat_history");

      if (!fileName) return;

      const res = await fetch('http://localhost:5001/generate_document', {
        method: 'GET',
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${fileName}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (error) {
      console.error('Error generating document:', error);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AI Knowledge Graph Chat</h1>
      </header>
      <div className="chat-container" ref={chatContainerRef}>
        {chatHistory.map((chat, index) => (
          <ChatMessage 
            key={index} 
            message={chat.message} 
            isUser={chat.isUser} 
            isTyping={chat.isTyping}
          />
        ))}
      </div>
      <form onSubmit={handleTopicSubmit} className="chat-input-form">
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter a topic to build a Knowledge Graph..."
          className="chat-input"
          disabled={isLoading || isBuildingKG}
        />
        <button type="submit" className="send-button" disabled={isLoading || isBuildingKG}>
          Set Topic
        </button>
      </form>
      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask me anything..."
          className="chat-input"
          disabled={isLoading || isBuildingKG}
        />
        <button type="submit" className="send-button" disabled={isLoading || isBuildingKG}>
          Send
        </button>
      </form>
      <button onClick={handleDownload} className="send-button" style={{ marginTop: '20px' }}>
        Download Chat History
      </button>
    </div>
  );
}

export default App;
