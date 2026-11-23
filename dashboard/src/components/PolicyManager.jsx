import React, { useState } from 'react';
import { FileText, Plus, ShieldAlert, Check } from 'lucide-react';

export default function PolicyManager({ policies = [], onCreatePolicy, isLoading }) {
  const [ruleText, setRuleText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!ruleText.trim() || isLoading) return;
    onCreatePolicy(ruleText);
    setRuleText('');
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '24px' }}>
      {/* Header */}
      <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 800 }}>Natural-Language Policy Engine</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '2px' }}>
          Define custom safety, privacy, or memory retention policies in plain English. The policy engine compiles rules into JSON policy schemas.
        </p>
      </div>

      {/* Add Policy Input Form */}
      <form onSubmit={handleSubmit} className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '10px' }}>Compile New Memory Policy</h3>
        <div style={{ display: 'flex', gap: '12px' }}>
          <input
            type="text"
            value={ruleText}
            onChange={(e) => setRuleText(e.target.value)}
            placeholder='e.g., "Do not store any health or medical records without explicit confirmation"'
            disabled={isLoading}
            style={{
              flex: 1,
              background: '#07090e',
              border: '1px solid #1e293b',
              borderRadius: '8px',
              padding: '12px 16px',
              color: '#f8fafc',
              fontSize: '0.9rem',
              outline: 'none'
            }}
          />
          <button type="submit" disabled={isLoading || !ruleText.trim()} className="btn-primary" style={{ borderRadius: '8px' }}>
            <Plus size={16} />
            <span>Compile Policy</span>
          </button>
        </div>
      </form>

      {/* Active Compiled Policies List */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px' }}>Active Compiled Policies ({policies.length})</h3>
        {policies.length === 0 ? (
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No policies registered for this user.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {policies.map((p) => (
              <div key={p.id} className="glass-panel" style={{ padding: '16px', borderLeft: '3px solid #c084fc' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span className="badge badge-purple">{p.id}</span>
                  <span className="badge badge-cyan">{p.action || 'ENFORCED'}</span>
                </div>
                <p style={{ fontSize: '0.9rem', color: '#f8fafc', fontWeight: 600 }}>"{p.natural_language_rule}"</p>
                {p.target_category && (
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>
                    Target Category: {p.target_category}
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
