import React from 'react';
import { TrendingUp, BarChart2, ShieldAlert, Activity, Globe, Layers, Server } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';

export default function AnalyticsView({ kpiData, transactions = [], activeDataset = 'synthetic' }) {
  // Activity / Volume Trends
  const activityData = [
    { time: '00:00', totalTx: 120, anomalousTx: 15, volume: 14.2 },
    { time: '04:00', totalTx: 95, anomalousTx: 8, volume: 11.0 },
    { time: '08:00', totalTx: 210, anomalousTx: 42, volume: 29.8 },
    { time: '12:00', totalTx: 340, anomalousTx: 85, volume: 48.0 },
    { time: '16:00', totalTx: 280, anomalousTx: 60, volume: 38.0 },
    { time: '20:00', totalTx: 190, anomalousTx: 30, volume: 21.0 },
    { time: '23:59', totalTx: 140, anomalousTx: 18, volume: 17.5 },
  ];

  // Risk Distribution Donut Data
  const riskDonutData = [
    { name: 'Low Risk (0-25)', value: 65, color: '#22C55E' },
    { name: 'Medium Risk (26-50)', value: 20, color: '#F59E0B' },
    { name: 'High Risk (51-75)', value: 10, color: '#F97316' },
    { name: 'Critical Risk (76-100)', value: 5, color: '#EF4444' },
  ];

  // Dataset Benchmark Comparisons
  const datasetComparisonData = [
    { dataset: 'Synthetic (SIH)', totalTxs: 81, features: 18, networkObs: 81, groundTruth: 'Scenario-based' },
    { dataset: 'Elliptic v1', totalTxs: 203769, features: 167, networkObs: 0, groundTruth: 'Class 1/2/3' },
    { dataset: 'Elliptic v2', totalTxs: 1268260, features: 184, networkObs: 0, groundTruth: 'Heterogeneous Wallet' },
  ];

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono">
      
      {/* Header Banner */}
      <div className="bg-[#0B1626] border border-[#101C2E] p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" />
            <span>Bitcoin Traffic & Anomaly Analytics</span>
          </h2>
          <p className="text-[11px] text-slate-400">
            Temporal patterns, risk scoring distributions, network observations & benchmark comparisons
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400">Active Analytics Scope:</span>
          <span className="px-2.5 py-1 rounded bg-[#2196F3]/20 text-[#2196F3] border border-[#2196F3]/40 font-bold uppercase">
            {activeDataset}
          </span>
        </div>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-4">
          <div className="text-[10px] text-slate-400 uppercase">Avg Risk Score</div>
          <div className="text-2xl font-bold text-cyan-400 mt-1">{kpiData?.avg_risk_score || '7.5'} / 100</div>
          <div className="text-[10px] text-slate-500 mt-1">Isolation Forest & DBSCAN</div>
        </div>

        <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-4">
          <div className="text-[10px] text-slate-400 uppercase">Total Entities Clustered</div>
          <div className="text-2xl font-bold text-purple-400 mt-1">{kpiData?.total_entities_clustered || 0}</div>
          <div className="text-[10px] text-slate-500 mt-1">Union-Find / DBSCAN</div>
        </div>

        <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-4">
          <div className="text-[10px] text-slate-400 uppercase">Network Observations</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">{kpiData?.total_network_observations || 0}</div>
          <div className="text-[10px] text-slate-500 mt-1">IP / Port / Geo correlation</div>
        </div>

        <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-4">
          <div className="text-[10px] text-slate-400 uppercase">High Risk Alerts</div>
          <div className="text-2xl font-bold text-rose-400 mt-1">{kpiData?.high_risk_alerts_count || 0}</div>
          <div className="text-[10px] text-slate-500 mt-1">Prioritization score &gt; 75</div>
        </div>
      </div>

      {/* Temporal Volume & Anomaly Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <div className="lg:col-span-2 bg-[#0B1626] border border-[#101C2E] rounded-xl p-5 shadow-md space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              <span>Temporal Volume & Anomaly Trend</span>
            </h3>
            <span className="text-[10px] text-slate-400">24-Hour Time Step Aggregate</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={activityData}>
                <defs>
                  <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2196F3" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#2196F3" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorAnomalous" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#64748B" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={10} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#050B14', borderColor: '#101C2E', fontSize: '11px', color: '#fff' }} />
                <Area type="monotone" dataKey="totalTx" stroke="#2196F3" fillOpacity={1} fill="url(#colorTotal)" name="Total Txs" />
                <Area type="monotone" dataKey="anomalousTx" stroke="#EF4444" fillOpacity={1} fill="url(#colorAnomalous)" name="Anomalous Txs" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Distribution Donut */}
        <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-5 shadow-md space-y-3 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              <span>Risk Score Breakdown</span>
            </h3>
            <p className="text-[11px] text-slate-400 mt-1">Multi-factor Isolation Forest & Network score</p>

            <div className="h-48 relative flex items-center justify-center mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskDonutData}
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {riskDonutData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-1.5 text-xs pt-3 border-t border-[#101C2E]">
            {riskDonutData.map((item) => (
              <div key={item.name} className="flex justify-between items-center">
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                  <span className="text-slate-300">{item.name}</span>
                </div>
                <span className="font-bold text-white">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Dataset Benchmark Comparison Table */}
      <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-5 shadow-md space-y-3">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
          <Layers className="w-4 h-4 text-purple-400" />
          <span>Multi-Dataset Architectural Comparison</span>
        </h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#050B14] text-slate-400 border-b border-[#101C2E] uppercase text-[10px]">
              <tr>
                <th className="py-2.5 px-4">Dataset</th>
                <th className="py-2.5 px-4">Transactions</th>
                <th className="py-2.5 px-4">Features</th>
                <th className="py-2.5 px-4">Network Observations</th>
                <th className="py-2.5 px-4">Ground Truth Scheme</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#101C2E]">
              {datasetComparisonData.map((d) => (
                <tr key={d.dataset} className="hover:bg-[#101C2E]/40">
                  <td className="py-3 px-4 font-bold text-cyan-300">{d.dataset}</td>
                  <td className="py-3 px-4 text-slate-200">{d.totalTxs.toLocaleString()}</td>
                  <td className="py-3 px-4 text-slate-400">{d.features}</td>
                  <td className="py-3 px-4 text-emerald-400">{d.networkObs > 0 ? `${d.networkObs} (Cross-layer)` : '0 (On-chain only)'}</td>
                  <td className="py-3 px-4 text-slate-300">{d.groundTruth}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
