import React, { useState } from 'react';
import { Send, User, Bot, Sparkles, Workflow, ArrowRight } from 'lucide-react';

export default function ChatPlayground({ 
  onSendTurn, 
  onSendRecall, 
  messages, 
  isLoading,
  onNavigateToPipeline 
}) {
  const [inputText, setInputText] = useState('');
  const [mode, setMode] = useState('ingest'); // 'ingest' | 'recall'

  const handleSubmit = (e) => {
    e.preventDefault();
    const text = inputText.trim();
    if (!text || isLoading) return;

    // Smart auto-detection for questions and recall queries
    const questionRegex = /\b(what|where|who|whom|whose|how|why|which|when|do i|did i|should i|can i|could i|would i|is my|are my|am i|what do|what is|what are|what was|what were|what did|which do|which one|do you know|tell me|so now what|coffee or tea|prefer coffee or tea|do i prefer)\b/i;
    const isQuestion = text.endsWith('?') || questionRegex.test(text) || /\b(asked|asking|inquiring|wondering|question)\b/i.test(text);

    if (mode === 'recall' || isQuestion) {
      onSendRecall(text);
    } else {
      onSendTurn(text);
    }
    setInputText('');
  };

  const samplePrompts = [
    { label: '📥 Add Fact: "I love Earl Grey tea in the morning"', action: () => onSendTurn('I love drinking Earl Grey tea in the morning') },
    { label: '🔄 Update Preference: "Actually I prefer Coffee over Tea"', action: () => onSendTurn('Actually I now prefer Coffee over Tea') },
    { label: '🔍 Ask Question: "What is my favorite morning drink?"', action: () => onSendRecall('What is my favorite morning drink?') }
  ];

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '24px' }}>
      {/* Playground Header & Mode Selector */}
      <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 800 }}>VeriMem Agent Playground</h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              Send user statements to extract verified memories or ask questions to receive grounded answers.
            </p>
          </div>
          
          <div style={{ display: 'flex', background: '#07090e', border: '1px solid #1e293b', borderRadius: '8px', padding: '3px' }}>
            <button
              onClick={() => setMode('ingest')}
              style={{
                padding: '6px 14px',
                borderRadius: '6px',
                border: 'none',
                background: mode === 'ingest' ? 'rgba(56, 189, 248, 0.15)' : 'transparent',
                color: mode === 'ingest' ? '#38bdf8' : 'var(--text-muted)',
                fontWeight: 600,
                fontSize: '0.8rem',
                cursor: 'pointer'
              }}
            >
              📥 Ingest & Store Fact
            </button>
            <button
              onClick={() => setMode('recall')}
              style={{
                padding: '6px 14px',
                borderRadius: '6px',
                border: 'none',
                background: mode === 'recall' ? 'rgba(168, 85, 247, 0.15)' : 'transparent',
                color: mode === 'recall' ? '#c084fc' : 'var(--text-muted)',
                fontWeight: 600,
                fontSize: '0.8rem',
                cursor: 'pointer'
              }}
            >
              🔍 Grounded Question (Recall)
            </button>
          </div>
        </div>

        {/* Quick Sample Action Bar */}
        <div style={{ display: 'flex', gap: '8px', marginTop: '14px', flexWrap: 'wrap' }}>
          {samplePrompts.map((sp, i) => (
            <button
              key={i}
              onClick={sp.action}
              disabled={isLoading}
              className="btn-secondary"
              style={{ fontSize: '0.76rem', padding: '6px 12px' }}
            >
              {sp.label}
            </button>
          ))}
        </div>
      </div>

      {/* Messages List */}
      <div className="glass-panel" style={{ minHeight: '400px', padding: '24px', marginBottom: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {messages.length === 0 ? (
          <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--text-muted)' }}>
            <Sparkles size={36} color="#38bdf8" style={{ marginBottom: '12px' }} />
            <h3 style={{ color: '#f8fafc', fontSize: '1rem', marginBottom: '6px' }}>Start a Conversation</h3>
            <p style={{ fontSize: '0.85rem' }}>Use the quick buttons above or type any statement / question below.</p>
          </div>
        ) : (
          messages.map((m, idx) => (
            <div key={idx} style={{
              alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '85%',
              background: m.sender === 'user' ? 'rgba(56, 189, 248, 0.12)' : '#0f172a',
              border: m.sender === 'user' ? '1px solid rgba(56, 189, 248, 0.3)' : '1px solid #1e293b',
              padding: '14px 18px',
              borderRadius: m.sender === 'user' ? '16px 16px 2px 16px' : '16px 16px 16px 2px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                {m.sender === 'user' ? (
                  <User size={14} color="#38bdf8" />
                ) : (
                  <Bot size={14} color="#34d399" />
                )}
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: m.sender === 'user' ? '#38bdf8' : '#34d399' }}>
                  {m.sender === 'user' ? 'User' : 'VeriMem Core Engine'}
                </span>
                {m.type === 'recall' && (
                  <span className="badge badge-purple" style={{ fontSize: '0.62rem' }}>GROUNDED ANSWER</span>
                )}
                {m.type === 'ingest' && (
                  <span className="badge badge-emerald" style={{ fontSize: '0.62rem' }}>MEMORY VERIFIED</span>
                )}
              </div>
              
              <p style={{ fontSize: '0.92rem', color: '#f8fafc', lineHeight: 1.5 }}>
                {m.text}
              </p>

              {m.citations && m.citations.length > 0 && (
                <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #1e293b', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Evidence Citations: {m.citations.map(c => typeof c === 'object' ? (c.memory_id || JSON.stringify(c)) : String(c)).join(', ')}
                </div>
              )}

              {/* Trace Navigation Button inside Bot Response */}
              {m.sender === 'bot' && m.hasTrace && (
                <button
                  onClick={onNavigateToPipeline}
                  style={{
                    marginTop: '10px',
                    background: 'rgba(56, 189, 248, 0.1)',
                    border: '1px solid rgba(56, 189, 248, 0.25)',
                    color: '#38bdf8',
                    padding: '4px 10px',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  <Workflow size={12} />
                  <span>Inspect n8n Visual Execution Pipeline →</span>
                </button>
              )}
            </div>
          ))
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px' }}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={mode === 'ingest' ? 'Enter a statement (e.g., "I love drinking Earl Grey tea in the morning")' : 'Ask a question (e.g., "What is my favorite morning drink?")'}
          disabled={isLoading}
          style={{
            flex: 1,
            background: '#07090e',
            border: '1px solid #1e293b',
            borderRadius: '10px',
            padding: '14px 18px',
            color: '#f8fafc',
            fontSize: '0.92rem',
            outline: 'none'
          }}
        />
        <button
          type="submit"
          disabled={isLoading || !inputText.trim()}
          className="btn-primary"
          style={{ borderRadius: '10px', padding: '0 24px' }}
        >
          <span>Send</span>
          <Send size={16} />
        </button>
      </form>
    </div>
  );
}
