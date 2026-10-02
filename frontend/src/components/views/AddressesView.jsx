import React from 'react';
import { Wallet, ShieldAlert, Users, Network } from 'lucide-react';

export default function AddressesView({ onViewGraphTarget }) {
  const sampleAddresses = [
    { address: '1InputAddr_bc1q9x29a40b799d51fd88dc3c482e7d91af960b', entity_id: 'ENTITY_C12', tx_count: 14, total_received: 42.85, total_sent: 42.80, turnover: 0.998, degree: 18, risk_score: 85.0, confidence: 0.88 },
    { address: '3OutputAddr_bc1q7y0124510258102451025810245102581024', entity_id: 'ENTITY_C12', tx_count: 2, total_received: 0.05, total_sent: 0.00, turnover: 0.000, degree: 3, risk_score: 20.0, confidence: 0.95 },
    { address: 'bc1qpeeling_change_addr_90124510258102451025810245', entity_id: 'ENTITY_C08', tx_count: 9, total_received: 18.50, total_sent: 18.10, turnover: 0.978, degree: 12, risk_score: 91.2, confidence: 0.89 },
    { address: 'bc1qnormal_user_addr_402151528419a421bc08912e76f4', entity_id: 'Unclustered', tx_count: 3, total_received: 1.20, total_sent: 0.50, turnover: 0.416, degree: 4, risk_score: 12.0, confidence: 0.92 },
  ];

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      <div className="bg-[#0B1626] border border-[#101C2E] p-4 rounded-xl flex items-center justify-between">
        <div>
          <h2 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <Wallet className="w-4 h-4 text-[#8B5CF6]" />
            <span>Bitcoin Address Ledger & Clustering</span>
          </h2>
          <p className="text-[11px] text-slate-400 font-mono">Address turnover rates and entity mappings</p>
        </div>
      </div>

      <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl overflow-hidden shadow-md">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-[#050B14] text-slate-400 border-b border-[#101C2E] uppercase text-[10px]">
              <tr>
                <th className="py-3 px-4">Address</th>
                <th className="py-3 px-4">Inferred Entity ID</th>
                <th className="py-3 px-4">TX Count</th>
                <th className="py-3 px-4">Received / Sent (BTC)</th>
                <th className="py-3 px-4">Turnover Ratio</th>
                <th className="py-3 px-4">Graph Degree</th>
                <th className="py-3 px-4">Risk Score</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#101C2E]">
              {sampleAddresses.map((addr) => (
                <tr key={addr.address} className="hover:bg-[#101C2E]/50 transition">
                  <td className="py-3 px-4 text-cyan-300 font-bold break-all max-w-xs">{addr.address}</td>
                  <td className="py-3 px-4 text-emerald-400 font-semibold">{addr.entity_id}</td>
                  <td className="py-3 px-4 text-slate-300">{addr.tx_count}</td>
                  <td className="py-3 px-4 text-white font-bold">{addr.total_received} / {addr.total_sent}</td>
                  <td className="py-3 px-4 text-slate-300">{addr.turnover.toFixed(3)}</td>
                  <td className="py-3 px-4 text-slate-300">{addr.degree}</td>
                  <td className="py-3 px-4">
                    <span className={`font-bold ${addr.risk_score >= 75 ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {addr.risk_score.toFixed(1)} / 100
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => onViewGraphTarget && onViewGraphTarget(addr.address)}
                      className="px-2.5 py-1 bg-[#2196F3]/20 text-[#22D3EE] hover:bg-[#2196F3] hover:text-white rounded-lg border border-[#2196F3]/40 text-[10px] transition"
                    >
                      Graph Subgraph
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
