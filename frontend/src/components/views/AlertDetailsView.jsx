import React from 'react';
import { ShieldAlert, ArrowLeft, GitFork, CheckCircle, AlertTriangle } from 'lucide-react';

export default function AlertDetailsView({ alert, onBack }) {
  const currentAlert = alert || {
    alert_id: 'ALT-1acd2b04',
    alert_type: 'Peeling Chain Funnel',
    target: '1acd2b047946a9d529e40b799d51fd88dc3c482e7d91af960bfccfed5c4551ea',
    risk_score: 92.4,
    confidence: 0.88,
    created_at: '2026-10-02 00:42:15',
    evidence: {
      reasons: [
        { feature: 'unusual_tx_velocity', value: '14 tx/min', baseline: '0.5 tx/min', contribution: 0.35 },
        { feature: 'high_address_turnover', value: '0.998 turnover ratio', baseline: '0.150 turnover', contribution: 0.28 },
        { feature: 'multiple_ip_observations', value: '2 unique IPs (US, DE)', baseline: '1 IP', contribution: 0.20 },
        { feature: 'peeling_chain_length', value: '5 consecutive hops', baseline: '1 hop', contribution: 0.17 },
      ],
    },
  };

  return (
    <div className="p-6 space-y-6 max-w-[1400px] mx-auto font-mono">
      
      {/* Top Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={onBack}
          className="p-2 bg-[#0B1626] border border-[#101C2E] text-slate-300 hover:text-white rounded-xl transition"
        >
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div>
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-[#EF4444]" />
            <span>Alert Investigation & Explainable Evidence</span>
          </h2>
          <p className="text-[11px] text-slate-400">ID: {currentAlert.alert_id}</p>
        </div>
      </div>

      {/* Alert Summary Card */}
      <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-5 shadow-md grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <span className="text-[10px] text-slate-400">Alert Classification:</span>
          <div className="text-sm font-bold text-amber-400 mt-0.5">{currentAlert.alert_type}</div>
        </div>
        <div>
          <span className="text-[10px] text-slate-400">Target Identifier:</span>
          <div className="text-xs font-bold text-cyan-300 break-all mt-0.5">{currentAlert.target}</div>
        </div>
        <div>
          <span className="text-[10px] text-slate-400">Normalized Risk Score:</span>
          <div className="text-base font-bold text-rose-400 mt-0.5">{currentAlert.risk_score} / 100</div>
        </div>
        <div>
          <span className="text-[10px] text-slate-400">System Confidence:</span>
          <div className="text-base font-bold text-emerald-400 mt-0.5">{((currentAlert.confidence || 0.85) * 100).toFixed(0)}%</div>
        </div>
      </div>

      {/* Why Was This Flagged Panel */}
      <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-5 shadow-md space-y-4">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          <span>Why Was This Flagged? (Model Evidence Lineage)</span>
        </h3>

        <div className="space-y-3">
          {currentAlert.evidence.reasons.map((reason, idx) => (
            <div key={idx} className="bg-[#050B14] p-3 rounded-xl border border-[#101C2E] flex flex-col md:flex-row md:items-center justify-between gap-2">
              <div>
                <div className="text-xs font-bold text-cyan-300 capitalize">{reason.feature.replace(/_/g, ' ')}</div>
                <div className="text-[11px] text-slate-400 mt-0.5">
                  Observed: <span className="text-white font-bold">{reason.value}</span> | Baseline: <span className="text-slate-400">{reason.baseline}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-[10px] text-slate-400">Contribution:</span>
                <span className="px-2 py-0.5 rounded bg-rose-950/60 text-rose-400 border border-rose-800 text-xs font-bold">
                  +{(reason.contribution * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
