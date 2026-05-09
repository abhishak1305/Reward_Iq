import React, { useState, useEffect, useRef } from 'react';
import { FiMessageCircle, FiX, FiSend, FiZap } from 'react-icons/fi';
import './Chatbot.css';
import { apiFetch } from '../lib/api';

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! I am your AI HR Coach. I can analyze your 360-degree feedback, provide performance insights, or answer HR questions. How can I help?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const role = localStorage.getItem('userRole') || 'admin';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // if (role === 'admin') return null; // Chatbot specifically for employees

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsTyping(true);

    let isAnalyzeAction = userMsg.toLowerCase().includes('feedback') || userMsg.toLowerCase().includes('insight');
    let aiResponse = "";
    let actualFeedback = [];

    try {
      if (isAnalyzeAction) {
        // Fetch real feedback from backend before analyzing
        try {
          actualFeedback = await apiFetch('/feedback'); 
          // Note: If logged in as admin, this gets all. If employee, it's filtered.
        } catch (e) {
          console.warn("Could not fetch feedback for analysis", e);
        }
      }

      // Fixed 5.1: Use centralized apiFetch instead of hardcoded URL
      const data = await apiFetch('/ai/chat', {
        method: 'POST',
        body: JSON.stringify({
          message: userMsg,
          action: isAnalyzeAction ? 'analyze' : 'chat',
          user: localStorage.getItem('userName') || 'Employee User',
          feedback: isAnalyzeAction ? actualFeedback : null
        })
      });

      aiResponse = data.response;

    } catch (error) {
      // Fallback if backend is not running or no API key
      const constructives = actualFeedback.filter(f => f.sentiment_label === 'constructive').length;
      const positives = actualFeedback.filter(f => f.sentiment_label === 'positive').length;
      
      if (isAnalyzeAction) {
        if (actualFeedback.length === 0) {
          aiResponse = "I've checked the database, but you don't have any recent peer feedback yet. Encourage your team to use the Peer Feedback tool on the dashboard!";
        } else {
          aiResponse = `**AI Analysis (Simulated Fallback):**\nI analyzed ${actualFeedback.length} recent feedback entries.\n\n` +
          `**Strengths:** You have ${positives} highly positive remarks.\n` +
          `**Hidden Insight:** However, ${constructives} entries suggest areas for improvement.\n\n` + 
          `**Suggested Action:** Focus on team communication and daily organization. (Note: Backend AI service call failed. Showing local summary.)`;
        }
      } else {
        aiResponse = "I'm sorry, I couldn't reach the backend AI server. Please ensure the FastAPI server is running.";
      }
    }

    setMessages(prev => [...prev, { role: 'ai', content: aiResponse }]);
    setIsTyping(false);
  };

  const requestInsights = () => {
    setInput('Can you analyze my recent feedback and provide insights?');
  };

  return (
    <>
      <button 
        className={`chatbot-trigger ${isOpen ? 'hidden' : ''}`}
        onClick={() => setIsOpen(true)}
      >
        <FiMessageCircle size={24} />
      </button>

      <div className={`chatbot-window glass-panel ${isOpen ? 'open' : ''}`}>
        <div className="chatbot-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div className="avatar small" style={{ background: '#10b981' }}><FiZap color="white" /></div>
            <div>
              <h4 style={{ margin: 0 }}>HR AI Coach</h4>
              <span style={{ fontSize: '0.75rem', color: '#10b981' }}>Powered by OpenRouter AI</span>
            </div>
          </div>
          <button className="icon-btn small" onClick={() => setIsOpen(false)}>
            <FiX />
          </button>
        </div>

        <div className="chatbot-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.role}`}>
              <div className="chat-bubble">
                {msg.content.split('\n').map((line, i) => <span key={i}>{line}<br/></span>)}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="chat-message ai">
              <div className="chat-bubble typing">
                <span className="dot"></span><span className="dot"></span><span className="dot"></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chatbot-suggestions">
          <button className="suggestion-btn" onClick={requestInsights}>
            ✨ Analyze my recent feedback
          </button>
        </div>

        <form className="chatbot-input" onSubmit={handleSend}>
          <input 
            type="text" 
            placeholder="Ask your AI Coach..." 
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" className="icon-btn" disabled={!input.trim()}>
            <FiSend color={input.trim() ? '#6366f1' : '#94a3b8'} />
          </button>
        </form>
      </div>
    </>
  );
};

export default Chatbot;
