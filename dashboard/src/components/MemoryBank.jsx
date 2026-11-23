import React, { useState } from 'react';
import { Database, Search, RefreshCw } from 'lucide-react';

export default function MemoryBank({ memories = [], onRefresh }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  const filtered = (memories || []).filter((m) => {
    const statement = (m.memory_text || m.statement || '').toLowerCase();
    const category = (m.type || m.category || '').toLowerCase();
    const query = (searchQuery || '').toLowerCase();

    const matchesSearch = statement.includes(query) || category.includes(query);
    const matchesStatus = filterStatus === 'all' || m.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      {/* Header */}
      <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800 }}>Verified Memory Bank</h2>
              <span className="badge badge-cyan">{(memories || []).length} STORED</span>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              Operational SQLite hybrid store containing evidence-grounded active memories, policy checks, and temporal updates.
            </p>
          </div>
          <button onClick={onRefresh} className="btn-secondary" style={{ padding: '8px 14px', fontSize: '0.8rem' }}>
            <RefreshCw size={14} />
            <span>Refresh Store</span>
          </button>
        </div>

        {/* Filters & Search */}
        <div style={{ display: 'flex', gap: '12px', marginTop: '16px', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
            <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search memory statements or categories..."
              style={{
                width: '100%',
                background: '#07090e',
                border: '1px solid #1e293b',
                borderRadius: '8px',
                padding: '8px 12px 8px 36px',
                color: '#f8fafc',
                fontSize: '0.85rem',
                outline: 'none'
              }}
            />
          </div>

          <div style={{ display: 'flex', gap: '6px' }}>
            {['all', 'active', 'updated', 'uncertain', 'rejected', 'retired'].map((st) => (
              <button
                key={st}
                onClick={() => setFilterStatus(st)}
                style={{
                  padding: '6px 12px',
                  borderRadius: '6px',
                  border: filterStatus === st ? '1px solid #38bdf8' : '1px solid #1e293b',
                  background: filterStatus === st ? 'rgba(56, 189, 248, 0.12)' : '#07090e',
                  color: filterStatus === st ? '#38bdf8' : 'var(--text-muted)',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  textTransform: 'capitalize'
                }}
              >
                {st}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Memory Table / Cards Grid */}
      {filtered.length === 0 ? (
        <div className="glass-panel" style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
          <Database size={40} color="#38bdf8" style={{ opacity: 0.5, marginBottom: '12px' }} />
          <h3>No Memories Found</h3>
          <p style={{ fontSize: '0.85rem' }}>No memories match the current filter or search criteria.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '16px' }}>
          {filtered.map((m) => {
            const statement = m.memory_text || m.statement || '';
            const category = m.type || m.category || 'preference';
            return (
              <div key={m.id} className="glass-panel" style={{ padding: '18px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <span className="badge badge-purple">{category}</span>
                    <span className={`badge badge-${m.status === 'active' ? 'emerald' : m.status === 'updated' ? 'cyan' : 'amber'}`}>
                      {m.status} (v{m.version || 1})
                    </span>
                  </div>
                  <p style={{ fontSize: '0.92rem', color: '#f8fafc', fontWeight: 600, lineHeight: 1.5, marginBottom: '12px' }}>
                    "{statement}"
                  </p>
                </div>

                <div style={{ borderTop: '1px solid #1e293b', paddingTop: '10px', fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
                  <span>ID: {m.id}</span>
                  <span>Confidence: {((m.confidence || 0.95) * 100).toFixed(0)}%</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
