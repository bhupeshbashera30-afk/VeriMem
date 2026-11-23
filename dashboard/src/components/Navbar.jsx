import React from 'react';
import { 
  ShieldCheck, 
  Workflow, 
  MessageSquare, 
  Database, 
  FileText, 
  Activity,
  Sparkles
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, activeMemoriesCount = 0 }) {
  const navItems = [
    { id: 'playground', label: 'Playground', icon: MessageSquare },
    { id: 'pipeline', label: 'n8n Visual Inspector', icon: Workflow, badge: 'LIVE' },
    { id: 'memories', label: 'Memory Bank', icon: Database, count: activeMemoriesCount },
    { id: 'policies', label: 'Policies', icon: FileText },
    { id: 'audit', label: 'Audit Trail', icon: Activity }
  ];

  return (
    <header style={{
      borderBottom: '1px solid var(--border-dim)',
      background: 'rgba(7, 9, 14, 0.85)',
      backdropFilter: 'blur(16px)',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'var(--primary-gradient)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(56, 189, 248, 0.4)'
          }}>
            <ShieldCheck size={24} color="#07090e" strokeWidth={2.5} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontWeight: 800, fontSize: '1.2rem', letterSpacing: '-0.02em' }}>VeriMem</span>
              <span className="badge badge-cyan">v0.1.0</span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Hallucination-Aware Memory Architecture
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  background: isActive ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                  color: isActive ? '#38bdf8' : 'var(--text-muted)',
                  border: isActive ? '1px solid rgba(56, 189, 248, 0.3)' : '1px solid transparent',
                  padding: '8px 16px',
                  borderRadius: '8px',
                  fontWeight: 600,
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  transition: 'all 0.2s ease'
                }}
              >
                <Icon size={16} />
                <span>{item.label}</span>
                {item.badge && (
                  <span className="badge badge-purple" style={{ fontSize: '0.65rem', padding: '1px 6px' }}>
                    {item.badge}
                  </span>
                )}
                {item.count !== undefined && (
                  <span style={{
                    background: 'rgba(255, 255, 255, 0.1)',
                    padding: '2px 7px',
                    borderRadius: '99px',
                    fontSize: '0.7rem'
                  }}>
                    {item.count}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* System Beacon */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.25)',
            padding: '6px 12px',
            borderRadius: '20px',
            fontSize: '0.78rem',
            color: '#34d399'
          }}>
            <span className="pulse-dot" style={{ background: '#34d399' }}></span>
            <span>FastAPI Core Online</span>
          </div>
        </div>
      </div>
    </header>
  );
}
