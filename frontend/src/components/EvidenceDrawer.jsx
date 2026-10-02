import React, { useState } from 'react';
import { X, ShieldAlert, Cpu, Network, Layers, Code, FileText, CheckCircle2 } from 'lucide-react';

export default function EvidenceDrawer({ alert, onClose, onSelectTxid }) {
  const [showRawJson, setShowRawJson] = useState(false);

  if (!alert) return null;

  const ev = alert.evidence || {};
  const components = ev.risk_components || {};

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm transition-opacity">
      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-xl glass-panel bg-[#0b101d] border-l border-slate-800 shadow-2xl flex flex-col">
          
          {/* Header */}
          <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
            <div>
              <div className="flex items-center space-x-2">
                <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-rose-950 text-rose-400 border border-rose-800">
                  {alert.alert_type}
                </span>
                <span className="text-xs font-mono text-slate-400">{alert.alert_id}</span>
              </div>
              <h2 className="text-lg font-bold text-white mt-1">Investigative Evidence Pack</h2>
            </div>
            
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Drawer Body Scrollable */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            
            {/* Target & Scores Summary */}
            <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <div>
                <span className="text-xs font-mono text-slate-400 uppercase">Target ID</span>
                <p 
                  className="font-mono text-xs font-semibold text-cyan-300 truncate mt-0.5 cursor-pointer hover:underline"
                  onClick={() => onSelectTxid && onSelectTxid(alert.target_id)}
                  title="Click to view in Transaction Inspector"
                >
                  {alert.target_id}
                </p>
              </div>

              <div>
                <span className="text-xs font-mono text-slate-400 uppercase">Risk Score</span>
                <p className="font-mono text-lg font-bold text-rose-400 mt-0.5">
                  {alert.risk_score} / 100
                </p>
              </div>

              <div>
                <span className="text-xs font-mono text-slate-400 uppercase">Confidence</span>
                <p className="font-mono text-sm font-semibold text-slate-200 mt-0.5">
                  {(alert.confidence * 100).toFixed(0)}%
                </p>
              </div>

              <div>
                <span className="text-xs font-mono text-slate-400 uppercase">Timestamp</span>
                <p className="font-mono text-xs text-slate-300 mt-0.5">
                  {ev.time_range || 'N/A'}
                </p>
              </div>
            </div>

            {/* Risk Component Score Decomposition */}
            <div>
              <h3 className="text-xs font-mono uppercase text-slate-400 mb-3 flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-cyan-400" />
                Risk Component Decomposition
              </h3>
              <div className="space-y-2.5 p-4 rounded-xl bg-slate-900/40 border border-slate-800/80">
                {Object.entries(components).map(([key, score]) => (
                  <div key={key}>
                    <div className="flex justify-between text-xs font-mono mb-1">
                      <span className="capitalize text-slate-300">{key.replace('_', ' ')}</span>
                      <span className="text-cyan-400 font-bold">{(score * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                      <div
                        className={`h-1.5 rounded-full ${
                          score > 0.6 ? 'bg-rose-500' : score > 0.3 ? 'bg-amber-500' : 'bg-cyan-500'
                        }`}
                        style={{ width: `${Math.min(100, score * 100)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Narrative Reasoning */}
            <div>
              <h3 className="text-xs font-mono uppercase text-slate-400 mb-2 flex items-center gap-1.5">
                <FileText className="w-4 h-4 text-purple-400" />
                Model Explanation & Narrative
              </h3>
              <div className="p-3.5 rounded-xl bg-purple-950/20 border border-purple-900/50 text-xs text-purple-200 space-y-2">
                {(ev.contributing_features || []).map((reason, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
                    <span>{reason}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Supporting Lineage (TXIDs & IPs) */}
            <div className="space-y-4">
              <div>
                <h4 className="text-xs font-mono text-slate-400 uppercase mb-1.5">Supporting Blockchain TXIDs</h4>
                <div className="flex flex-wrap gap-1.5">
                  {(ev.supporting_txids || []).map((txid, idx) => (
                    <button
                      key={idx}
                      onClick={() => onSelectTxid && onSelectTxid(txid)}
                      className="font-mono text-[11px] px-2 py-1 rounded bg-slate-800 hover:bg-cyan-950 hover:text-cyan-300 text-slate-300 border border-slate-700 transition"
                    >
                      {txid}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-xs font-mono text-slate-400 uppercase mb-1.5">Correlated P2P Network Observations</h4>
                <div className="flex flex-wrap gap-1.5">
                  {(ev.supporting_ip_obs || []).map((obsId, idx) => (
                    <span key={idx} className="font-mono text-[11px] px-2 py-1 rounded bg-indigo-950/50 text-indigo-300 border border-indigo-800/40">
                      {obsId}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Raw JSON Toggle */}
            <div className="pt-4 border-t border-slate-800">
              <button
                onClick={() => setShowRawJson(!showRawJson)}
                className="flex items-center space-x-1.5 text-xs font-mono text-slate-400 hover:text-slate-200 transition"
              >
                <Code className="w-3.5 h-3.5" />
                <span>{showRawJson ? 'Hide Raw Evidence JSON' : 'Inspect Raw Evidence JSON'}</span>
              </button>

              {showRawJson && (
                <pre className="mt-3 p-4 rounded-xl bg-slate-950 border border-slate-800 text-[11px] text-cyan-400 font-mono overflow-x-auto max-h-64">
                  {JSON.stringify(alert, null, 2)}
                </pre>
              )}
            </div>

          </div>

        </div>
      </div>
    </div>
  );
}
