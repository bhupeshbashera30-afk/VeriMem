import React, { useState } from 'react';
import { 
  MessageSquare, 
  Filter, 
  Split, 
  ShieldCheck, 
  Zap, 
  FileText, 
  Database, 
  HelpCircle, 
  Cpu, 
  Sparkles,
  Play,
  RotateCcw,
  Info,
  ChevronRight
} from 'lucide-react';
import NodeDetailsDrawer from './NodeDetailsDrawer';

const ICON_MAP = {
  MessageSquare,
  Filter,
  Split,
  ShieldCheck,
  Zap,
  FileText,
  Database,
  HelpCircle,
  Cpu,
  Sparkles
};

export default function N8nPipeline({ 
  traceData, 
  onRunTestScenario, 
  isLoading 
}) {
  const [selectedNode, setSelectedNode] = useState(null);

  const nodes = traceData?.nodes || [];
  const edges = traceData?.edges || [];
  const mode = traceData?.mode || 'ingest';

  // Preset Scenario Handlers
  const scenarios = [
    {
      id: 'ingest_tea',
      title: '1. Ingest Fact',
      desc: '"I love drinking Earl Grey tea every morning."',
      action: () => onRunTestScenario('ingest', 'I love drinking Earl Grey tea every morning.')
    },
    {
      id: 'update_coffee',
      title: '2. Update Preference Conflict',
      desc: '"Actually, I switched from tea to cold brew coffee."',
      action: () => onRunTestScenario('ingest', 'Actually, I switched from tea to cold brew coffee.')
    },
    {
      id: 'recall_drink',
      title: '3. Grounded Recall Query',
      desc: '"What is my preferred morning drink?"',
      action: () => onRunTestScenario('recall', 'What is my preferred morning drink?')
    },
    {
      id: 'reject_hallucination',
      title: '4. Test Assistant Hallucination',
      desc: 'Assistant asserts "User lives in Tokyo" without user evidence',
      action: () => onRunTestScenario('ingest_assistant', 'User lives in Tokyo, Japan.')
    }
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header Bar & Test Scenario Controls */}
      <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800 }}>n8n Visual Backend Inspector</h2>
              <span className="badge badge-purple">{mode.toUpperCase()} FLOW</span>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Live operation-level memory execution pipeline. Select any node to inspect atomic facts, evidence verification, and scoring matrix.
            </p>
          </div>
          {isLoading && (
            <div className="badge badge-cyan pulse" style={{ padding: '6px 14px' }}>
              ⚡ Executing Pipeline...
            </div>
          )}
        </div>

        {/* Scenario Quick Buttons */}
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          {scenarios.map((sc) => (
            <button
              key={sc.id}
              onClick={sc.action}
              disabled={isLoading}
              className="btn-secondary"
              style={{
                fontSize: '0.8rem',
                flex: 1,
                minWidth: '220px',
                justifyContent: 'space-between',
                textAlign: 'left'
              }}
            >
              <div>
                <strong style={{ display: 'block', color: '#f8fafc', fontSize: '0.82rem' }}>{sc.title}</strong>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{sc.desc}</span>
              </div>
              <Play size={14} color="#38bdf8" style={{ flexShrink: 0 }} />
            </button>
          ))}
        </div>
      </div>

      {/* n8n Node Canvas Container */}
      <div className="glass-panel n8n-canvas-grid" style={{
        minHeight: '480px',
        padding: '40px 24px',
        position: 'relative',
        overflowX: 'auto',
        borderRadius: '16px',
        border: '1px solid #1e293b'
      }}>
        {nodes.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '80px 20px',
            color: 'var(--text-muted)'
          }}>
            <Play size={48} color="#38bdf8" style={{ opacity: 0.5, marginBottom: '16px' }} />
            <h3 style={{ color: '#f8fafc', marginBottom: '8px' }}>No Active Pipeline Run</h3>
            <p style={{ fontSize: '0.9rem' }}>Click one of the test scenarios above or type a turn in the Playground to trigger node visual execution.</p>
          </div>
        ) : (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-start',
            gap: '36px',
            minWidth: 'max-content',
            padding: '20px 10px'
          }}>
            {nodes.map((node, index) => {
              const IconComponent = ICON_MAP[node.icon] || MessageSquare;
              const isSelected = selectedNode?.id === node.id;
              const hasNext = index < nodes.length - 1;

              return (
                <React.Fragment key={node.id}>
                  {/* Node Card */}
                  <div
                    className={`n8n-node ${isSelected ? 'active-node' : ''}`}
                    onClick={() => setSelectedNode(node)}
                  >
                    <div className="n8n-node-header">
                      <div className="n8n-node-title">
                        <div style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '8px',
                          background: 'rgba(56, 189, 248, 0.12)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#38bdf8'
                        }}>
                          <IconComponent size={18} />
                        </div>
                        <span style={{ fontSize: '0.88rem', color: '#f8fafc' }}>{node.label}</span>
                      </div>
                      <span className={`pulse-dot`} style={{
                        background: node.status === 'success' ? '#34d399' : node.status === 'warning' ? '#fbbf24' : '#fb7185'
                      }}></span>
                    </div>

                    {/* Node Quick Specs */}
                    <div style={{
                      fontSize: '0.76rem',
                      color: 'var(--text-muted)',
                      borderTop: '1px dashed #1e293b',
                      paddingTop: '10px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}>
                      <span>Step #{index + 1}</span>
                      <span style={{ color: '#38bdf8', fontWeight: 600 }}>Inspect Payload →</span>
                    </div>
                  </div>

                  {/* Flow Arrow Connection Cable */}
                  {hasNext && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#38bdf8' }}>
                      <svg width="40" height="24" viewBox="0 0 40 24">
                        <path
                          d="M0,12 L40,12"
                          stroke="#38bdf8"
                          strokeWidth="2.5"
                          className="animated-cable"
                        />
                        <polygon points="34,6 40,12 34,18" fill="#38bdf8" />
                      </svg>
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        )}
      </div>

      {/* Node Inspector Drawer */}
      <NodeDetailsDrawer
        node={selectedNode}
        onClose={() => setSelectedNode(null)}
      />
    </div>
  );
}
