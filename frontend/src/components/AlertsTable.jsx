import React, { useState } from 'react';
import { ShieldAlert, Search, Filter, ChevronRight, Eye, AlertTriangle, Layers, Zap } from 'lucide-react';

export default function AlertsTable({ alerts, onSelectAlert }) {
  const [filterType, setFilterType] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredAlerts = alerts.filter(a => {
    const matchesType = filterType === 'ALL' || a.alert_type === filterType;
    const matchesQuery = searchQuery === '' || 
      a.alert_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.target_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesQuery;
  });

  const getRiskBadge = (score) => {
    if (score >= 70) {
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono font-bold bg-rose-950/80 text-rose-400 border border-rose-800/80 shadow-sm shadow-rose-900/40">
          <AlertTriangle className="w-3 h-3 mr-1 text-rose-400" />
          {score.toFixed(1)} / 100
        </span>
      );
    } else if (score >= 45) {
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono font-bold bg-amber-950/80 text-amber-400 border border-amber-800/80">
          {score.toFixed(1)} / 100
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono font-medium bg-cyan-950/80 text-cyan-400 border border-cyan-800/80">
        {score.toFixed(1)} / 100
      </span>
    );
  };

  const getAlertTypeBadge = (type) => {
    switch (type) {
      case 'PEELING_CHAIN':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-purple-950/60 text-purple-300 border border-purple-800/50">
            <Layers className="w-3 h-3 mr-1 text-purple-400" />
            Peeling Chain
          </span>
        );
      case 'MIXING_PATTERN':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-indigo-950/60 text-indigo-300 border border-indigo-800/50">
            <Zap className="w-3 h-3 mr-1 text-indigo-400" />
            Mixing Pattern
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-slate-800 text-slate-300 border border-slate-700">
            <ShieldAlert className="w-3 h-3 mr-1 text-slate-400" />
            {type}
          </span>
        );
    }
  };

  return (
    <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800">
      
      {/* Header & Filters */}
      <div className="p-4 sm:p-6 border-b border-slate-800/80 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            Investigative Leads & Alert Queue
          </h2>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Ranked by multi-component normalized risk score
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
          {/* Search Input */}
          <div className="relative flex-1 sm:w-64">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search TXID or Alert ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900/80 text-xs text-slate-200 placeholder-slate-500 pl-9 pr-3 py-2 rounded-xl border border-slate-800 focus:outline-none focus:border-cyan-500/50 transition"
            />
          </div>

          {/* Filter Dropdown */}
          <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
            {['ALL', 'PEELING_CHAIN', 'MIXING_PATTERN', 'ANOMALY_BURST'].map((t) => (
              <button
                key={t}
                onClick={() => setFilterType(t)}
                className={`px-2.5 py-1 rounded-lg text-xs font-mono transition ${
                  filterType === t
                    ? 'bg-cyan-500/20 text-cyan-400 font-semibold border border-cyan-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {t === 'ALL' ? 'All' : t.split('_')[0]}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/60 text-slate-400 font-mono uppercase tracking-wider border-b border-slate-800/80">
            <tr>
              <th className="py-3.5 px-4">Alert ID</th>
              <th className="py-3.5 px-4">Type</th>
              <th className="py-3.5 px-4">Target (TXID / IP)</th>
              <th className="py-3.5 px-4">Risk Score</th>
              <th className="py-3.5 px-4">Confidence</th>
              <th className="py-3.5 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {filteredAlerts.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-500 font-mono">
                  No investigative alerts match the current filter.
                </td>
              </tr>
            ) : (
              filteredAlerts.map((alt) => (
                <tr key={alt.alert_id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3 px-4 font-mono font-medium text-cyan-300">
                    {alt.alert_id}
                  </td>
                  <td className="py-3 px-4">
                    {getAlertTypeBadge(alt.alert_type)}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-300 max-w-[200px] truncate" title={alt.target_id}>
                    {alt.target_id}
                  </td>
                  <td className="py-3 px-4">
                    {getRiskBadge(alt.risk_score)}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-400">
                    {(alt.confidence * 100).toFixed(0)}%
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => onSelectAlert(alt)}
                      className="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-cyan-950/60 text-cyan-400 hover:bg-cyan-900/60 border border-cyan-800/60 transition"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Inspect</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
}
