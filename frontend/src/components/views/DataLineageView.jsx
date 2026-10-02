import React from 'react';
import { GitFork, ShieldAlert, Cpu, Layers, Database, Wifi, Info } from 'lucide-react';

export default function DataLineageView({ activeDataset = 'synthetic' }) {
  const isEllipticV1 = activeDataset === 'elliptic_v1';
  const isEllipticV2 = activeDataset === 'elliptic_v2';
  const isBenchmark = isEllipticV1 || isEllipticV2;

  const getDatasetLabel = () => {
    if (isEllipticV1) return "Elliptic v1 Benchmark Dataset";
    if (isEllipticV2) return "Elliptic++ v2 Benchmark Dataset";
    return "SIH Synthetic Multi-Layer Dataset";
  };

  return (
    <div className="p-6 space-y-6 max-w-[1400px] mx-auto font-mono">
      <div className="bg-[#0B1626] border border-[#101C2E] p-5 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <GitFork className="w-4 h-4 text-[#8B5CF6]" />
            <span>Evidence & Data Lineage Traceability</span>
          </h2>
          <p className="text-[11px] text-slate-400 mt-0.5">End-to-end evidence pipeline from raw data sources to ML risk scores</p>
        </div>
        <span className="px-3 py-1 rounded text-xs font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40">
          Scope: {getDatasetLabel()}
        </span>
      </div>

      {isBenchmark && (
        <div className="bg-[#050B14] border border-purple-500/30 rounded-xl p-4 flex items-start space-x-3 text-xs">
          <Info className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="font-bold text-purple-300">Data Lineage Provenance Notice</div>
            <p className="text-slate-300 leading-relaxed">
              {isEllipticV1 ? (
                "Elliptic v1 provides real public transaction data. Network P2P observations are project-generated synthetic simulation correlated with Elliptic transaction IDs for SIH investigation architecture demonstration."
              ) : (
                "Elliptic++ v2 provides real public transaction & wallet ground-truth data. Network P2P observations are project-generated synthetic simulation correlated with Elliptic++ transaction IDs for SIH investigation architecture demonstration."
              )}
            </p>
          </div>
        </div>
      )}

      {/* Timeline Tree */}
      <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-6 shadow-md space-y-6">
        
        {/* Step 1: Data Origin */}
        <div className="flex items-start space-x-4 border-l-2 border-[#8B5CF6] pl-4">
          <div className="p-2 bg-purple-950/60 rounded-xl border border-purple-800 text-purple-400">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-bold text-white uppercase">Step 1: Blockchain Data Layer</div>
            <div className="text-xs text-purple-300">
              {isBenchmark ? `${getDatasetLabel()} (Public Ground-Truth Benchmark)` : "Synthetic Bitcoin Blockchain Transactions (Data Generator)"}
            </div>
          </div>
        </div>

        {/* Step 2: Network Layer */}
        <div className="flex items-start space-x-4 border-l-2 border-[#22C55E] pl-4">
          <div className="p-2 bg-emerald-950/60 rounded-xl border border-emerald-800 text-[#22C55E]">
            <Wifi className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-bold text-white uppercase">Step 2: Network Observation Telemetry</div>
            <div className="text-xs text-slate-300">
              {isBenchmark ? (
                "Project-Generated Synthetic Network Simulation (Correlated with Benchmark TXIDs)"
              ) : (
                "Synthetic P2P Observations (IP: 192.168.1.45, US, AS15169 | Relay Delta: 0.12s)"
              )}
            </div>
          </div>
        </div>

        {/* Step 3: Feature Extraction */}
        <div className="flex items-start space-x-4 border-l-2 border-[#2196F3] pl-4">
          <div className="p-2 bg-blue-950/60 rounded-xl border border-blue-800 text-[#2196F3]">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-bold text-white uppercase">Step 3: Cross-Layer Feature Engineering</div>
            <div className="text-xs text-cyan-300">
              Cross-layer correlation (IP ↔ TXID ↔ Address ↔ Entity) + 166 transaction/graph features
            </div>
          </div>
        </div>

        {/* Step 4: ML Inference */}
        <div className="flex items-start space-x-4 border-l-2 border-[#F59E0B] pl-4">
          <div className="p-2 bg-amber-950/60 rounded-xl border border-amber-800 text-amber-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-bold text-white uppercase">Step 4: AI/ML Detection Engine</div>
            <div className="text-xs text-amber-300">
              Isolation Forest Anomaly Scoring + DBSCAN Entity Clustering + Supervised Benchmarks
            </div>
          </div>
        </div>

        {/* Step 5: Risk & Alert */}
        <div className="flex items-start space-x-4 border-l-2 border-[#EF4444] pl-4">
          <div className="p-2 bg-rose-950/60 rounded-xl border border-rose-800 text-rose-400">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-bold text-white uppercase">Step 5: Alert Lead & SOC Investigation</div>
            <div className="text-xs text-rose-400 font-bold">
              Investigation Lead Generation (Heuristic Multi-Factor Risk Score ≥ 30.0)
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
