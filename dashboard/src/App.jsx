import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import N8nPipeline from './components/N8nPipeline';
import ChatPlayground from './components/ChatPlayground';
import MemoryBank from './components/MemoryBank';
import PolicyManager from './components/PolicyManager';
import AuditLog from './components/AuditLog';
import { 
  fetchUserMemories, 
  fetchUserPolicies, 
  createPolicy, 
  traceIngestTurn, 
  traceRecallQuery,
  fetchAuditLogs
} from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('playground');
  const [userId] = useState('user_default');
  const [memories, setMemories] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [messages, setMessages] = useState([]);
  const [traceData, setTraceData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const loadData = async () => {
    const mems = await fetchUserMemories(userId);
    const pols = await fetchUserPolicies(userId);
    const logs = await fetchAuditLogs(userId);
    setMemories(mems);
    setPolicies(pols);
    setAuditLogs(logs);
  };

  useEffect(() => {
    loadData();
  }, [userId]);

  const handleSendTurn = async (text) => {
    setIsLoading(true);
    setMessages((prev) => [...prev, { sender: 'user', text, type: 'turn' }]);

    try {
      const traceRes = await traceIngestTurn(userId, text);
      setTraceData(traceRes);
      
      if (traceRes.is_question && traceRes.answer) {
        const answerObj = traceRes.answer || {};
        setMessages((prev) => [...prev, {
          sender: 'bot',
          text: answerObj.answer || 'I do not have enough verified memory to answer this question.',
          citations: answerObj.citations || [],
          type: 'recall',
          hasTrace: true
        }]);
      } else if (traceRes.processed_candidates && traceRes.processed_candidates.length > 0) {
        const c = traceRes.processed_candidates[0];
        botResponse = `Verified & Stored Memory: "${c.candidate.memory_text}" [Status: ${c.decision.decision}]`;
        setMessages((prev) => [...prev, { 
          sender: 'bot', 
          text: botResponse, 
          type: 'ingest',
          hasTrace: true 
        }]);
      } else {
        botResponse = 'Fact processed. Evidence verified against conversation history.';
        setMessages((prev) => [...prev, { 
          sender: 'bot', 
          text: botResponse, 
          type: 'ingest',
          hasTrace: true 
        }]);
      }
      await loadData();
    } catch (err) {
      console.error('Failed turn ingest trace:', err);
      setMessages((prev) => [...prev, { sender: 'bot', text: 'Error processing memory turn.', type: 'error' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendRecall = async (question) => {
    setIsLoading(true);
    setMessages((prev) => [...prev, { sender: 'user', text: question, type: 'question' }]);

    try {
      const traceRes = await traceRecallQuery(userId, question);
      setTraceData(traceRes);
      
      const answerObj = traceRes.answer || {};
      setMessages((prev) => [...prev, {
        sender: 'bot',
        text: answerObj.answer || 'I do not have enough verified memory to answer this question.',
        citations: answerObj.citations || [],
        type: 'recall',
        hasTrace: true
      }]);

      await loadData();
    } catch (err) {
      console.error('Failed recall query trace:', err);
      setMessages((prev) => [...prev, { sender: 'bot', text: 'Error querying verified memory bank.', type: 'error' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunTestScenario = async (type, text) => {
    if (type === 'ingest' || type === 'ingest_assistant') {
      const speaker = type === 'ingest_assistant' ? 'assistant' : 'user';
      setIsLoading(true);
      try {
        const traceRes = await traceIngestTurn(userId, text, speaker);
        setTraceData(traceRes);
        await loadData();
        setActiveTab('pipeline');
      } catch (err) {
        console.error('Scenario run error:', err);
      } finally {
        setIsLoading(false);
      }
    } else if (type === 'recall') {
      await handleSendRecall(text);
      setActiveTab('pipeline');
    }
  };

  const handleCreatePolicy = async (ruleText) => {
    setIsLoading(true);
    try {
      await createPolicy(userId, ruleText);
      await loadData();
    } catch (err) {
      console.error('Failed creating policy:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        activeMemoriesCount={memories.filter((m) => m.status === 'active').length}
      />

      <main style={{ flex: 1 }}>
        {activeTab === 'playground' && (
          <ChatPlayground
            messages={messages}
            isLoading={isLoading}
            onSendTurn={handleSendTurn}
            onSendRecall={handleSendRecall}
            onNavigateToPipeline={() => setActiveTab('pipeline')}
          />
        )}

        {activeTab === 'pipeline' && (
          <N8nPipeline
            traceData={traceData}
            isLoading={isLoading}
            onRunTestScenario={handleRunTestScenario}
          />
        )}

        {activeTab === 'memories' && (
          <MemoryBank
            memories={memories}
            onRefresh={loadData}
          />
        )}

        {activeTab === 'policies' && (
          <PolicyManager
            policies={policies}
            isLoading={isLoading}
            onCreatePolicy={handleCreatePolicy}
          />
        )}

        {activeTab === 'audit' && (
          <AuditLog
            auditLogs={auditLogs}
          />
        )}
      </main>
    </div>
  );
}
