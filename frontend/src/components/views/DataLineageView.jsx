import React from 'react';
import { GitFork, ShieldAlert, Cpu, Layers, Database, Wifi } from 'lucide-react';

export default function DataLineageView() {
  return (
    <div className="p-6 space-y-6 max-w-[1400px] mx-auto font-mono">
      <div className="bg-[#0B1626] border border-[#101C2E] p-4 rounded-xl">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
          <GitFork className="w-4 h-4 text-[#8B5CF6]" />
          <span>Evidence & Data Lineage Traceability</span>
        </h2>
        <p className="text-[11px] text-slate-400">End-to-end evidence tree from synthetic P2P observation to risk score</p>
      </div>

      {/* Timeline Tree */}
      <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-6 shadow-md space-y-6">
        
        {/* Step 1: Alert */}
        <div className="flex items-start space-x-4 border-l-2 border-[#EF4444] pl-4">
          <div className="p-2 bg-rose-950/60 rounded-xl border border-rose-800 text-rose-400">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-bold text-white uppercase">Step 1: Alert Generated</div>
            <div className="text-xs text-rose-400 font-bold">ALT-1acd2b04 (Peeling Chain Funnel - Risk: 92.4 / 100)</div>
          </div>
        </div>

        {/* Step 2: ML Model */}
        <div className="flex items-start space-x-4 border-l-2 border-[#F59E0B] pl-4">
          <div className="p-2 bg-amber-950/60 rounded-xl border border-amber-800 text-amber-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-bold text-white uppercase">Step 2: Detection Model Inference</div>
            <div className="text-xs text-amber-300">Peeling-chain structural analysis + IsolationForest (Anomaly Score: -0.74)</div>
          </div>
        </div>

        {/* Step 3: Features */}
        <div className="flex items-start space-x-4 border-l-2 border-[#2196F3] pl-4">
          <div className="p-2 bg-blue-950/60 rounded-xl border border-blue-800 text-[#2196F3]">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-bold text-white uppercase">Step 3: Extracted Feature Vector</div>
            <div className="text-xs text-cyan-300">tx_velocity: 14, turnover_ratio: 0.998, peeling_hops: 5</div>
          </div>
        </div>

        {/* Step 4: Supporting Observations */}
        <div className="flex items-start space-x-4 border-l-2 border-[#22C55E] pl-4">
          <div className="p-2 bg-emerald-950/60 rounded-xl border border-emerald-800 text-[#22C55E]">
            <Wifi className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-bold text-white uppercase">Step 4: Synthetic P2P Network Observations</div>
            <div className="text-xs text-slate-300">P2P IP: 192.168.1.45 (US, AS15169) | Relay Delta: 0.12s | Timestamp: 2026-10-02 00:42:10</div>
          </div>
        </div>

      </div>
    </div>
  );
}
