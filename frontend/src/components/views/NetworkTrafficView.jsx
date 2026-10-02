import React, { useState } from 'react';
import { Wifi, Globe, Search, Filter } from 'lucide-react';

export default function NetworkTrafficView() {
  const [searchTerm, setSearchTerm] = useState('');

  const sampleNetworkEvents = [
    { src_ip: '192.168.1.45', dst_ip: '10.0.4.12', src_port: 8333, dst_port: 8333, txid: '1acd2b047946a9d5...', timestamp: '2026-10-02 00:42:10', geo_country: 'US', asn: 'AS15169', time_delta: 0.12, event_type: 'inv_relay' },
    { src_ip: '10.0.4.12', dst_ip: '172.16.0.8', src_port: 8333, dst_port: 8333, txid: '0f4c05bac9057140...', timestamp: '2026-10-02 00:35:05', geo_country: 'DE', asn: 'AS3320', time_delta: 0.08, event_type: 'tx_broadcast' },
    { src_ip: '192.168.1.100', dst_ip: '192.168.1.1', src_port: 8333, dst_port: 8333, txid: '3b89fa12e09418b7...', timestamp: '2026-10-02 00:20:00', geo_country: 'IN', asn: 'AS55836', time_delta: 0.45, event_type: 'addr_discovery' },
  ];

  const filtered = sampleNetworkEvents.filter(
    (item) => item.src_ip.includes(searchTerm) || item.geo_country.toLowerCase().includes(searchTerm.toLowerCase()) || item.txid.includes(searchTerm)
  );

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      <div className="bg-[#0B1626] border border-[#101C2E] p-4 rounded-xl flex items-center justify-between">
        <div>
          <h2 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <Wifi className="w-4 h-4 text-[#22D3EE]" />
            <span>P2P Network Observation Metadata (Correlated)</span>
          </h2>
          <p className="text-[11px] text-slate-400 font-mono">Cross-layered P2P node IP observations and relay deltas</p>
        </div>

        <div className="relative w-64">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search IP / Country / TXID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#050B14] text-xs font-mono text-cyan-300 placeholder-slate-500 pl-8 pr-3 py-1.5 rounded-xl border border-[#101C2E] focus:outline-none focus:border-[#22D3EE]"
          />
        </div>
      </div>

      <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl overflow-hidden shadow-md">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-[#050B14] text-slate-400 border-b border-[#101C2E] uppercase text-[10px]">
              <tr>
                <th className="py-3 px-4">Source IP : Port</th>
                <th className="py-3 px-4">Destination IP : Port</th>
                <th className="py-3 px-4">TXID</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Geo Country</th>
                <th className="py-3 px-4">ASN</th>
                <th className="py-3 px-4">Relay Delta (s)</th>
                <th className="py-3 px-4">Event Type</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#101C2E]">
              {filtered.map((item, idx) => (
                <tr key={idx} className="hover:bg-[#101C2E]/50 transition">
                  <td className="py-3 px-4 text-cyan-300 font-bold">{item.src_ip}:{item.src_port}</td>
                  <td className="py-3 px-4 text-slate-300">{item.dst_ip}:{item.dst_port}</td>
                  <td className="py-3 px-4 text-amber-400 break-all">{item.txid}</td>
                  <td className="py-3 px-4 text-slate-400 text-[11px]">{item.timestamp}</td>
                  <td className="py-3 px-4 text-emerald-400 font-bold">{item.geo_country}</td>
                  <td className="py-3 px-4 text-slate-300">{item.asn}</td>
                  <td className="py-3 px-4 text-slate-300">{item.time_delta}s</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] bg-[#050B14] border border-[#101C2E] text-slate-300">
                      {item.event_type}
                    </span>
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
