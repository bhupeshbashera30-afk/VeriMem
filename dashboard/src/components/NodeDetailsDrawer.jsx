import React, { useState } from 'react';
import { X, Code, CheckCircle, AlertTriangle, XCircle, Info, ArrowRight } from 'lucide-react';

export default function NodeDetailsDrawer({ node, onClose }) {
  const [viewMode, setViewMode] = useState('summary'); // 'summary' | 'json'

  if (!node) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      width: '460px',
      height: '100vh',
      background: '#0a0d14',
      borderLeft: '1px solid #1e293b',
      boxShadow: '-15px 0 40px rgba(0, 0, 0, 0.7)',
      zIndex: 200,
      display: 'flex',
      flexDirection: 'column',
      animation: 'slideIn 0.25s ease'
    }}>
      {/* Header */}
      <div style={{
        padding: '20px 24px',
        borderBottom: '1px solid #1e293b',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'rgba(15, 23, 42, 0.6)'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-cyan">{node.type}</span>
            <span className={`badge badge-${node.status === 'success' ? 'emerald' : node.status === 'warning' ? 'amber' : 'rose'}`}>
              {node.status}
            </span>
          </div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>{node.label}</h3>
        </div>
        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: '4px',
            borderRadius: '6px'
          }}
        >
          <X size={20} />
        </button>
      </div>

      {/* Mode Switcher Tabs */}
      <div style={{
        display: 'flex',
        borderBottom: '1px solid #1e293b',
        padding: '0 24px',
        background: '#07090e'
      }}>
        <button
          onClick={() => setViewMode('summary')}
          style={{
            padding: '10px 16px',
            background: 'transparent',
            border: 'none',
            borderBottom: viewMode === 'summary' ? '2px solid #38bdf8' : '2px solid transparent',
            color: viewMode === 'summary' ? '#38bdf8' : 'var(--text-muted)',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer'
          }}
        >
          Pipeline Analysis
        </button>
        <button
          onClick={() => setViewMode('json')}
          style={{
            padding: '10px 16px',
            background: 'transparent',
            border: 'none',
            borderBottom: viewMode === 'json' ? '2px solid #38bdf8' : '2px solid transparent',
            color: viewMode === 'json' ? '#38bdf8' : 'var(--text-muted)',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <Code size={14} />
          Raw JSON Payload
        </button>
      </div>

      {/* Body Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
        {viewMode === 'summary' ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Input Details */}
            {node.details?.text && (
              <div className="glass-panel" style={{ padding: '16px' }}>
                <h4 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Input Statement
                </h4>
                <p style={{ fontSize: '0.92rem', color: '#f8fafc', lineHeight: 1.5 }}>
                  "{node.details.text}"
                </p>
              </div>
            )}

            {/* Extracted Candidates */}
            {node.details?.candidates && (
              <div>
                <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '10px', textTransform: 'uppercase' }}>
                  Extracted Candidates ({node.details.candidates.length})
                </h4>
                {node.details.candidates.map((c, i) => (
                  <div key={i} className="glass-panel" style={{ padding: '14px', marginBottom: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span className="badge badge-purple">{c.category}</span>
                      <span style={{ fontSize: '0.75rem', color: '#34d399' }}>Conf: {(c.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <p style={{ fontSize: '0.88rem', color: '#e2e8f0' }}>{c.text}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Decomposed Atomic Facts */}
            {node.details?.facts && (
              <div>
                <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '10px', textTransform: 'uppercase' }}>
                  Decomposed Atomic Facts ({node.details.facts.length})
                </h4>
                {node.details.facts.map((f, i) => (
                  <div key={i} className="glass-panel" style={{ padding: '12px', marginBottom: '8px', display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                    <span style={{ color: '#38bdf8', marginTop: '2px' }}>•</span>
                    <div>
                      <p style={{ fontSize: '0.88rem', color: '#e2e8f0', fontWeight: 500 }}>{f.text || f.fact_text}</p>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Entity: {f.subject || 'User'} | Prop: {f.predicate || 'has_preference'}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Evidence Verification Details */}
            {node.details?.verifications && (
              <div>
                <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '10px', textTransform: 'uppercase' }}>
                  Evidence Grounding Results
                </h4>
                {node.details.verifications.map((v, i) => (
                  <div key={i} className="glass-panel" style={{ padding: '14px', marginBottom: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span className={`badge badge-${v.grounding_label === 'supported' || v.grounding_label === 'directly_supported' ? 'emerald' : v.grounding_label === 'assistant_originated' ? 'rose' : 'amber'}`}>
                        {v.grounding_label}
                      </span>
                      <span style={{ fontSize: '0.78rem', color: '#38bdf8' }}>Confidence: {(v.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', marginBottom: '6px' }}>{v.reason}</p>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                      Verified Turn Evidence: {v.evidence_turns?.length ? v.evidence_turns.join(', ') : 'None'}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Conflict & Update Detector Details */}
            {node.details?.conflicts && (
              <div>
                <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '10px', textTransform: 'uppercase' }}>
                  Conflict & Update Detector Results
                </h4>
                {node.details.conflicts.map((c, i) => (
                  <div key={i} className="glass-panel" style={{ padding: '14px', marginBottom: '10px', borderLeft: c.status === 'update_required' ? '3px solid #38bdf8' : '3px solid #34d399' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span className={`badge badge-${c.status === 'update_required' ? 'cyan' : 'emerald'}`}>
                        {c.status}
                      </span>
                      <span className="badge badge-purple">{c.action}</span>
                    </div>
                    <p style={{ fontSize: '0.86rem', color: '#e2e8f0', marginBottom: '6px' }}>{c.reason}</p>
                    {c.related_memories && c.related_memories.length > 0 && (
                      <div style={{ fontSize: '0.75rem', color: '#38bdf8' }}>
                        Related Prior Memories to Retire: {c.related_memories.join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Policy Engine Details */}
            {node.details?.evaluations && (
              <div>
                <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '10px', textTransform: 'uppercase' }}>
                  Policy Engine Evaluations
                </h4>
                {node.details.evaluations.map((ev, i) => (
                  <div key={i} className="glass-panel" style={{ padding: '12px', marginBottom: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Candidate ID: {ev.candidate_id}</span>
                    <span className="badge badge-emerald">{ev.action}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Committed DB Operations */}
            {node.details?.committed_operations && (
              <div>
                <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '10px', textTransform: 'uppercase' }}>
                  Database Committed Write Decisions
                </h4>
                {node.details.committed_operations.map((op, i) => (
                  <div key={i} className="glass-panel" style={{ padding: '14px', marginBottom: '10px', borderLeft: '3px solid #34d399' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span className="badge badge-emerald">{op.decision}</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>ID: {op.committed_memory_id}</span>
                    </div>
                    <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)' }}>{op.reason}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Hybrid Retrieval Results */}
            {node.details?.results && (
              <div>
                <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '10px', textTransform: 'uppercase' }}>
                  Multi-Signal Score Breakdown
                </h4>
                {node.details.results.map((r, i) => (
                  <div key={i} className="glass-panel" style={{ padding: '14px', marginBottom: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.88rem', color: '#f8fafc' }}>Rank #{i+1}</span>
                      <span className="badge badge-cyan">Score: {r.combined_score}</span>
                    </div>
                    <p style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '10px' }}>"{r.text}"</p>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', fontSize: '0.75rem' }}>
                      <div style={{ background: 'rgba(255,255,255,0.03)', padding: '6px 8px', borderRadius: '4px' }}>
                        Semantic: <strong style={{ color: '#38bdf8' }}>{r.signals.semantic}</strong>
                      </div>
                      <div style={{ background: 'rgba(255,255,255,0.03)', padding: '6px 8px', borderRadius: '4px' }}>
                        Keyword: <strong style={{ color: '#c084fc' }}>{r.signals.keyword}</strong>
                      </div>
                      <div style={{ background: 'rgba(255,255,255,0.03)', padding: '6px 8px', borderRadius: '4px' }}>
                        Recency: <strong style={{ color: '#34d399' }}>{r.signals.recency}</strong>
                      </div>
                      <div style={{ background: 'rgba(255,255,255,0.03)', padding: '6px 8px', borderRadius: '4px' }}>
                        Confidence: <strong style={{ color: '#fbbf24' }}>{r.signals.confidence}</strong>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Grounded Answer Agent */}
            {node.details?.answer && (
              <div className="glass-panel" style={{ padding: '16px', borderLeft: '4px solid #34d399' }}>
                <h4 style={{ fontSize: '0.8rem', color: '#34d399', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Grounded Output Response
                </h4>
                <p style={{ fontSize: '0.95rem', color: '#f8fafc', lineHeight: 1.6 }}>
                  {node.details.answer}
                </p>
              </div>
            )}
          </div>
        ) : (
          <pre style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.78rem',
            color: '#38bdf8',
            background: '#07090e',
            padding: '16px',
            borderRadius: '8px',
            border: '1px solid #1e293b',
            overflowX: 'auto',
            whiteSpace: 'pre-wrap'
          }}>
            {JSON.stringify(node, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
