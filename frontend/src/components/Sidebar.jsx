import React from 'react';
import { 
  Shield, LayoutDashboard, ArrowLeftRight, Wallet, Users, 
  Wifi, ShieldAlert, Network, BarChart2, Cpu, GitFork, Settings 
} from 'lucide-react';

export default function Sidebar({ activeSection, setActiveSection, activeDataset = 'synthetic' }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'transactions', label: 'Transactions', icon: ArrowLeftRight },
    { id: 'addresses', label: 'Addresses', icon: Wallet },
    { id: 'entities', label: 'Entities', icon: Users },
    { id: 'network', label: 'Network Traffic', icon: Wifi },
    { id: 'alerts', label: 'Alerts', icon: ShieldAlert },
    { id: 'graph', label: 'Graph Explorer', icon: Network },
    { id: 'analytics', label: 'Analytics', icon: BarChart2 },
    { id: 'ml_models', label: 'ML Models', icon: Cpu },
    { id: 'lineage', label: 'Data Lineage', icon: GitFork },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const getModeBadge = () => {
    if (activeDataset === 'elliptic_v1') {
      return {
        title: 'ELLIPTIC V1 MODE',
        sub: 'Research Benchmark',
        color: 'text-[#22D3EE]',
        dot: 'bg-[#22D3EE]'
      };
    }
    if (activeDataset === 'elliptic_v2') {
      return {
        title: 'ELLIPTIC++ MODE',
        sub: 'Research Benchmark',
        color: 'text-[#A855F7]',
        dot: 'bg-[#A855F7]'
      };
    }
    return {
      title: 'OFFLINE MODE',
      sub: 'SIH Synthetic Investigation',
      color: 'text-[#22C55E]',
      dot: 'bg-[#22C55E]'
    };
  };

  const modeBadge = getModeBadge();

  return (
    <aside className="w-60 bg-[#08111F] border-r border-[#101C2E] flex flex-col justify-between h-screen sticky top-0 shrink-0 select-none z-30">
      
      {/* Top Section: Logo & Branding */}
      <div>
        <div className="h-16 flex items-center space-x-3 px-5 border-b border-[#101C2E] bg-[#050B14]">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-[#2196F3] to-[#8B5CF6] shadow-md shadow-[#2196F3]/20">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-sm text-white tracking-wider font-mono">NTRO SOC</h1>
            <p className="text-[10px] text-slate-400 font-mono">SIH26146 Platform</p>
          </div>
        </div>

        {/* Navigation List */}
        <nav className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)]">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-[#2196F3]/15 text-[#22D3EE] border border-[#2196F3]/40 shadow-sm shadow-[#2196F3]/20 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-[#101C2E]/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-[#22D3EE]' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Section: Offline Status Badge */}
      <div className="p-4 border-t border-[#101C2E] bg-[#050B14]/80">
        <div className="flex items-center space-x-2 px-3 py-2 rounded-xl bg-[#0B1626] border border-[#101C2E]">
          <span className={`w-2 h-2 rounded-full ${modeBadge.dot} animate-pulse`}></span>
          <div>
            <div className="text-[11px] font-mono font-bold text-slate-200 uppercase tracking-wider">{modeBadge.title}</div>
            <div className={`text-[10px] font-mono ${modeBadge.color}`}>{modeBadge.sub}</div>
          </div>
        </div>
      </div>

    </aside>
  );
}
