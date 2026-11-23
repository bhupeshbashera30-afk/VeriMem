import React from 'react';
import { Activity, ShieldCheck, AlertCircle, FileText } from 'lucide-react';

export default function AuditLog({ auditLogs = [] }) {
  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '24px' }}>
      {/* Header */}
      <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 800 }}>Operation-Level Audit Trail</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '2px' }}>
          Complete audit history of memory candidate extractions, evidence grounding decisions, policy checks, and database modifications.
        </p>
      </div>

      <div className="glass-panel" style={{ padding: '24px' }}>
        {auditLogs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            <Activity size={32} color="#38bdf8" style={{ opacity: 0.5, marginBottom: '8px' }} />
            <p style={{ fontSize: '0.88rem' }}>No audit operations logged yet. Run a scenario or interact in the playground to generate logs.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {auditLogs.map((log, idx) => (
              <div key={idx} className="glass-panel" style={{ padding: '14px 18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span className="badge badge-emerald">{log.operation_type || 'STORE_WRITE'}</span>
                    <span style={{ fontSize: '0.85rem', color: '#f8fafc', fontWeight: 600 }}>Memory ID: {log.memory_id}</span>
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{log.details || log.explanation || 'Evidence grounded memory write'}</p>
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : 'Just now'}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
