import React, { useState, useEffect } from 'react';
import { Wifi, Globe, Search, Filter, AlertCircle, Info, Shield } from 'lucide-react';

export default function NetworkTrafficView({ activeDataset = 'synthetic' }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [observations, setObservations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [meta, setMeta] = useState({});

  useEffect(() => {
    fetchNetworkObservations();
  }, [activeDataset]);

  const fetchNetworkObservations = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/network/observations?dataset=${activeDataset || 'synthetic'}&limit=100`);
      if (res.ok) {
        const data = await res.json();
        setMeta(data);
        const obsList = data.observations || [];
        if (obsList.length > 0) {
          setObservations(obsList);
        } else {
          setObservations(getFallbackEvents(activeDataset));
        }
      } else {
        setObservations(getFallbackEvents(activeDataset));
      }
    } catch (e) {
      console.error('Failed to fetch network observations:', e);
      setObservations(getFallbackEvents(activeDataset));
    } finally {
      setLoading(false);
    }
  };

  const getFallbackEvents = (ds) => [
    { obs_id: 'obs_01', src_ip: '192.168.1.45', dst_ip: '10.0.4.12', src_port: 54321, dst_port: 8333, txid: '1acd2b047946a9d5c8e2...', timestamp: '2026-10-02 00:42:10', geo_country: 'US', asn: 'AS15169', time_delta: 0.12, network_event_type: 'inv_relay', network_data_provenance: 'project_generated' },
    { obs_id: 'obs_02', src_ip: '10.0.4.12', dst_ip: '172.16.0.8', src_port: 49152, dst_port: 8333, txid: '0f4c05bac9057140a12f...', timestamp: '2026-10-02 00:35:05', geo_country: 'DE', asn: 'AS3320', time_delta: 0.08, network_event_type: 'tx_broadcast', network_data_provenance: 'project_generated' },
    { obs_id: 'obs_03', src_ip: '172.16.0.8', dst_ip: '192.168.1.100', src_port: 61000, dst_port: 8333, txid: '3b89fa12e09418b7d91e...', timestamp: '2026-10-02 00:20:00', geo_country: 'IN', asn: 'AS55836', time_delta: 0.45, network_event_type: 'addr_discovery', network_data_provenance: 'project_generated' },
  ];

  const getSubtitle = () => {
    if (activeDataset === 'elliptic_v1') {
      return "Synthetic P2P observations correlated with Elliptic v1 blockchain transactions";
    }
    if (activeDataset === 'elliptic_v2') {
      return "Synthetic P2P observations correlated with Elliptic++ blockchain transactions";
    }
    return "Cross-layered synthetic P2P observations and relay metadata";
  };

  const getBadgeText = () => {
    if (activeDataset === 'elliptic_v1' || activeDataset === 'elliptic_v2') {
      return "🟣 SYNTHETIC NETWORK SIMULATION";
    }
    return "🟣 SYNTHETIC NETWORK DATA";
  };

  const getExplanatoryText = () => {
    if (activeDataset === 'elliptic_v1') {
      return "IP/port/relay observations are project-generated synthetic data. They are not part of the original Elliptic dataset.";
    }
    if (activeDataset === 'elliptic_v2') {
      return "IP/port/relay observations are project-generated synthetic data. They are not part of the original Elliptic++ dataset.";
    }
    return "Synthetic IP/port/relay telemetry generated to simulate P2P network layer observations.";
  };

  const filtered = observations.filter((item) => {
    const s = searchTerm.toLowerCase();
    const srcIp = item.src_ip || '';
    const dstIp = item.dst_ip || '';
    const country = item.geo_country || '';
    const txid = item.txid || '';
    return srcIp.toLowerCase().includes(s) || dstIp.toLowerCase().includes(s) || country.toLowerCase().includes(s) || txid.toLowerCase().includes(s);
  });

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      
      {/* Header Bar */}
      <div className="bg-[#0B1626] border border-[#101C2E] p-5 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h2 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center space-x-2">
              <Wifi className="w-4 h-4 text-[#22D3EE]" />
              <span>P2P NETWORK OBSERVATION METADATA (CORRELATED)</span>
            </h2>
            <span className="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40">
              {getBadgeText()}
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-mono mt-1">{getSubtitle()}</p>
        </div>

        <div className="relative w-72">
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

      {/* Explanatory Callout Banner */}
      <div className="bg-[#050B14] border border-purple-500/30 rounded-xl p-4 flex items-start space-x-3 text-xs font-mono">
        <Info className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-bold text-purple-300">Data Lineage & Provenance Notice</div>
          <p className="text-slate-300 leading-relaxed">
            {getExplanatoryText()}
          </p>
        </div>
      </div>

      {/* Observation Table */}
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
                <th className="py-3 px-4">Provenance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#101C2E]">
              {filtered.map((item, idx) => (
                <tr key={item.obs_id || idx} className="hover:bg-[#101C2E]/50 transition">
                  <td className="py-3 px-4 text-cyan-300 font-bold">{item.src_ip}:{item.src_port || 8333}</td>
                  <td className="py-3 px-4 text-slate-300">{item.dst_ip}:{item.dst_port || 8333}</td>
                  <td className="py-3 px-4 text-amber-400 break-all max-w-xs">{item.txid}</td>
                  <td className="py-3 px-4 text-slate-400 text-[11px]">{item.timestamp}</td>
                  <td className="py-3 px-4 text-emerald-400 font-bold">{item.geo_country}</td>
                  <td className="py-3 px-4 text-slate-300">{item.asn}</td>
                  <td className="py-3 px-4 text-slate-300">{item.time_delta}s</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] bg-[#050B14] border border-[#101C2E] text-slate-300">
                      {item.network_event_type || item.event_type || 'tx_relay'}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-purple-500/10 text-purple-300 border border-purple-500/30">
                      Synthetic Simulation
                    </span>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan="9" className="py-8 text-center text-slate-500">
                    {loading ? 'Loading network observations...' : 'No network observations found.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
