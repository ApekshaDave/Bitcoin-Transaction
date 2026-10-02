import React from 'react';
import { Database, Wifi, Users, AlertTriangle, Gauge } from 'lucide-react';

export default function KPICards({ kpis }) {
  const cards = [
    {
      title: "Total Transactions",
      value: kpis?.total_transactions || 0,
      icon: Database,
      color: "from-blue-500/20 to-cyan-500/20 border-blue-500/30 text-cyan-400",
      sub: "Blockchain Layer"
    },
    {
      title: "P2P Observations",
      value: kpis?.total_network_observations || 0,
      icon: Wifi,
      color: "from-indigo-500/20 to-purple-500/20 border-indigo-500/30 text-indigo-400",
      sub: "Network Layer Correlated"
    },
    {
      title: "Inferred Entities",
      value: kpis?.total_entities_clustered || 0,
      icon: Users,
      color: "from-purple-500/20 to-fuchsia-500/20 border-purple-500/30 text-fuchsia-400",
      sub: "DBSCAN Multi-Input Clusters"
    },
    {
      title: "High Risk Alerts",
      value: kpis?.high_risk_alerts_count || 0,
      icon: AlertTriangle,
      color: "from-rose-500/20 to-red-500/20 border-rose-500/30 text-rose-400",
      sub: "Investigative Leads"
    },
    {
      title: "Avg Risk Score",
      value: `${kpis?.avg_risk_score || 0}/100`,
      icon: Gauge,
      color: "from-amber-500/20 to-orange-500/20 border-amber-500/30 text-amber-400",
      sub: "System-Wide Normalized"
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
      {cards.map((c, i) => {
        const IconComponent = c.icon;
        return (
          <div key={i} className={`p-4 rounded-xl glass-panel bg-gradient-to-br ${c.color} transition hover:scale-[1.02]`}>
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{c.title}</span>
              <IconComponent className="w-5 h-5 opacity-80" />
            </div>
            <div className="mt-2 flex items-baseline">
              <span className="text-2xl font-bold font-mono text-white tracking-tight">{c.value}</span>
            </div>
            <p className="mt-1 text-[11px] text-slate-400 font-mono">{c.sub}</p>
          </div>
        );
      })}
    </div>
  );
}
