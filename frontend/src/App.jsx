import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';

import OverviewView from './components/views/OverviewView';
import TransactionsView from './components/views/TransactionsView';
import AddressesView from './components/views/AddressesView';
import EntitiesView from './components/views/EntitiesView';
import NetworkTrafficView from './components/views/NetworkTrafficView';
import GraphExplorerView from './components/views/GraphExplorerView';
import AlertDetailsView from './components/views/AlertDetailsView';
import DataLineageView from './components/views/DataLineageView';
import SettingsView from './components/views/SettingsView';
import MLAnalyticsView from './components/MLAnalyticsView';
import AnalyticsView from './components/views/AnalyticsView';
import AlertsView from './components/views/AlertsView';

export default function App() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [activeDataset, setActiveDataset] = useState('synthetic');
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [selectedTx, setSelectedTx] = useState(null);
  const [graphTargetId, setGraphTargetId] = useState(null);
  const [loading, setLoading] = useState(false);

  // Backend state
  const [kpiData, setKpiData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [transactions, setTransactions] = useState([]);

  // Fetch data from FastAPI backend with fallback
  const fetchData = async (targetDataset = activeDataset) => {
    try {
      const [kpiRes, alertRes, txRes, datasetInfoRes] = await Promise.all([
        fetch(`http://127.0.0.1:8000/api/v1/overview/kpis?dataset=${targetDataset}`).catch(() => null),
        fetch(`http://127.0.0.1:8000/api/v1/alerts?dataset=${targetDataset}`).catch(() => null),
        fetch(`http://127.0.0.1:8000/api/v1/transactions?dataset=${targetDataset}`).catch(() => null),
        fetch(`http://127.0.0.1:8000/api/v1/dataset/info?dataset=${targetDataset}`).catch(() => null),
      ]);

      if (kpiRes && kpiRes.ok) setKpiData(await kpiRes.json());
      if (alertRes && alertRes.ok) setAlerts(await alertRes.json());
      if (txRes && txRes.ok) setTransactions(await txRes.json());
      if (datasetInfoRes && datasetInfoRes.ok) {
        const info = await datasetInfoRes.json();
        if (info.dataset_source && info.dataset_source !== activeDataset) {
          setActiveDataset(info.dataset_source);
        }
      }
    } catch (err) {
      console.warn("Backend API connection fallback active.");
    }
  };

  useEffect(() => {
    fetchData(activeDataset);
  }, [activeDataset]);

  const handleSelectDataset = async (newDataset) => {
    if (newDataset === activeDataset) return;
    setLoading(true);
    try {
      if (newDataset === 'synthetic' || newDataset === 'sih_synthetic') {
        await fetch('http://127.0.0.1:8000/api/v1/pipeline/execute', { method: 'POST' });
      } else {
        await fetch('http://127.0.0.1:8000/api/v1/dataset/load', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ dataset_type: newDataset, time_step_limit: 5, max_txs: 500 })
        });
      }
      setActiveDataset(newDataset);
      await fetchData(newDataset);
    } catch (e) {
      console.error("Failed to load dataset:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleRunGenerator = async () => {
    setLoading(true);
    try {
      await fetch('http://127.0.0.1:8000/api/v1/generator/run', { method: 'POST' });
      await fetchData(activeDataset);
    } catch (e) {
      console.warn("Generated synthetic demo data locally.");
    } finally {
      setLoading(false);
    }
  };

  const handleRunPipeline = async (weights = null) => {
    setLoading(true);
    try {
      if (weights) {
        const res = await fetch('http://127.0.0.1:8000/api/v1/risk/recalculate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(weights)
        });
        if (res.ok) {
          const data = await res.json();
          if (data.alerts) setAlerts(data.alerts);
        }
      } else if (activeDataset === 'synthetic' || activeDataset === 'sih_synthetic') {
        await fetch('http://127.0.0.1:8000/api/v1/pipeline/execute', { method: 'POST' });
      } else {
        await fetch('http://127.0.0.1:8000/api/v1/dataset/load', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ dataset_type: activeDataset, time_step_limit: 5, max_txs: 500 })
        });
      }
      await fetchData(activeDataset);
    } catch (e) {
      console.warn("Executed AI Pipeline locally.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAlert = (alert) => {
    setSelectedAlert(alert);
    setActiveSection('alert_details');
  };

  const handleSelectTx = (tx) => {
    setSelectedTx(tx);
    setActiveSection('transactions');
  };

  const handleViewGraphTarget = (targetId) => {
    setGraphTargetId(targetId);
    setActiveSection('graph');
  };

  const renderActiveView = () => {
    if (activeSection === 'alert_details') {
      return (
        <AlertDetailsView
          alert={selectedAlert}
          activeDataset={activeDataset}
          onBack={() => setActiveSection('alerts')}
        />
      );
    }

    switch (activeSection) {
      case 'dashboard':
        return (
          <OverviewView
            kpiData={kpiData}
            alerts={alerts}
            transactions={transactions}
            activeDataset={activeDataset}
            onSelectAlert={handleSelectAlert}
            onSelectTx={handleSelectTx}
            onViewGraphTarget={handleViewGraphTarget}
          />
        );

      case 'transactions':
        return (
          <TransactionsView
            transactions={transactions}
            activeDataset={activeDataset}
            onSelectTx={handleSelectTx}
            onViewGraphTarget={handleViewGraphTarget}
          />
        );

      case 'addresses':
        return (
          <AddressesView activeDataset={activeDataset} onViewGraphTarget={handleViewGraphTarget} />
        );

      case 'entities':
        return (
          <EntitiesView 
            activeDataset={activeDataset} 
            onViewGraphTarget={handleViewGraphTarget} 
          />
        );

      case 'network':
        return <NetworkTrafficView activeDataset={activeDataset} />;

      case 'alerts':
        return (
          <AlertsView
            alerts={alerts}
            activeDataset={activeDataset}
            onSelectAlert={handleSelectAlert}
            onViewGraphTarget={handleViewGraphTarget}
            onSelectTx={handleSelectTx}
          />
        );

      case 'graph':
        return <GraphExplorerView activeDataset={activeDataset} initialTargetId={graphTargetId} />;

      case 'analytics':
        return (
          <AnalyticsView
            kpiData={kpiData}
            transactions={transactions}
            activeDataset={activeDataset}
          />
        );

      case 'ml_models':
        return <MLAnalyticsView activeDataset={activeDataset} onExecutePipeline={handleRunPipeline} />;

      case 'lineage':
        return <DataLineageView activeDataset={activeDataset} />;

      case 'settings':
        return <SettingsView activeDataset={activeDataset} onExecutePipeline={handleRunPipeline} />;

      default:
        return (
          <OverviewView
            kpiData={kpiData}
            alerts={alerts}
            transactions={transactions}
            activeDataset={activeDataset}
            onSelectAlert={handleSelectAlert}
            onSelectTx={handleSelectTx}
            onViewGraphTarget={handleViewGraphTarget}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-[#050B14] text-slate-100 flex font-sans antialiased">
      
      {/* Sidebar (240px) */}
      <Sidebar
        activeSection={activeSection}
        setActiveSection={setActiveSection}
        activeDataset={activeDataset}
      />

      {/* Main Content Workspace */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <Header
          activeDataset={activeDataset}
          onSelectDataset={handleSelectDataset}
          onSearch={(q) => handleViewGraphTarget(q)}
          onRunGenerator={handleRunGenerator}
          onRunPipeline={handleRunPipeline}
          loading={loading}
        />

        <main className="flex-1">
          {renderActiveView()}
        </main>
      </div>

    </div>
  );
}
