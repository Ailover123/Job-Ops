"use client";

import { useState, useEffect } from "react";
import { API_BASE_URL } from "../../lib/api";

type CollectorSource = {
  id: number;
  company_name: string;
  source_type: string;
  board_token: string | null;
  company_id: string | null;
  enabled: boolean;
  last_run_at: string | null;
  last_success_at: string | null;
  last_error: string | null;
};

export default function InternalSourcesPage() {
  const [apiKey, setApiKey] = useState("");
  const [hasKey, setHasKey] = useState(false);
  const [sources, setSources] = useState<CollectorSource[]>([]);
  const [error, setError] = useState<string | null>(null);

  // New source form state
  const [companyName, setCompanyName] = useState("");
  const [sourceType, setSourceType] = useState("lever");
  const [identifier, setIdentifier] = useState("");

  const [isCollecting, setIsCollecting] = useState(false);
  const [collectResult, setCollectResult] = useState<any>(null);

  useEffect(() => {
    const savedKey = sessionStorage.getItem("internal_api_key");
    if (savedKey) {
      setApiKey(savedKey);
      setHasKey(true);
      fetchSources(savedKey);
    }
  }, []);

  const handleSaveKey = () => {
    if (apiKey.trim()) {
      sessionStorage.setItem("internal_api_key", apiKey.trim());
      setHasKey(true);
      fetchSources(apiKey.trim());
    }
  };

  const fetchSources = async (key: string) => {
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/internal/sources`, {
        headers: { "X-Internal-API-Key": key }
      });
      if (!res.ok) {
        if (res.status === 403) throw new Error("Invalid API Key");
        throw new Error("Failed to fetch sources");
      }
      const data = await res.json();
      setSources(data);
    } catch (err: any) {
      setError(err.message);
      if (err.message === "Invalid API Key") {
        setHasKey(false);
        sessionStorage.removeItem("internal_api_key");
      }
    }
  };

  const handleAddSource = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const body = {
        company_name: companyName,
        source_type: sourceType,
        board_token: sourceType === "greenhouse" ? identifier : null,
        company_id: sourceType === "lever" ? identifier : null
      };

      const res = await fetch(`${API_BASE_URL}/api/v1/internal/sources`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Internal-API-Key": apiKey
        },
        body: JSON.stringify(body)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to add source");
      }

      setCompanyName("");
      setIdentifier("");
      fetchSources(apiKey);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleToggleEnabled = async (source: CollectorSource) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/internal/sources/${source.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Internal-API-Key": apiKey
        },
        body: JSON.stringify({ enabled: !source.enabled })
      });
      if (!res.ok) throw new Error("Failed to toggle source");
      fetchSources(apiKey);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to disable this source?")) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/internal/sources/${id}`, {
        method: "DELETE",
        headers: { "X-Internal-API-Key": apiKey }
      });
      if (!res.ok) throw new Error("Failed to disable source");
      fetchSources(apiKey);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleCollectAll = async () => {
    setIsCollecting(true);
    setError(null);
    setCollectResult(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/internal/collect/all`, {
        method: "POST",
        headers: { "X-Internal-API-Key": apiKey }
      });
      if (!res.ok) throw new Error("Failed to run collection");
      const data = await res.json();
      setCollectResult(data);
      fetchSources(apiKey); // refresh status
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsCollecting(false);
    }
  };

  if (!hasKey) {
    return (
      <div className="centered-page">
        <div className="card" style={{ maxWidth: '400px', width: '100%' }}>
          <h1 style={{ marginBottom: '16px' }}>Internal Access</h1>
          <p style={{ color: '#64748b', fontSize: '13px', marginBottom: '24px' }}>Please enter the internal API key to access source management.</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="X-Internal-API-Key"
              className="input-field"
              onKeyDown={(e) => e.key === "Enter" && handleSaveKey()}
            />
            <button
              onClick={handleSaveKey}
              className="button-primary"
              style={{ width: '100%' }}
            >
              Authenticate
            </button>
            {error && <p className="error-text">{error}</p>}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-shell" style={{ padding: '32px' }}>
      <div style={{ maxWidth: '1120px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        
        <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ marginBottom: '4px' }}>Job Sources</h1>
            <p style={{ color: '#64748b', fontSize: '13px', margin: 0 }}>Manage collector configurations</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button
              onClick={() => {
                sessionStorage.removeItem("internal_api_key");
                setHasKey(false);
              }}
              style={{ background: 'none', border: 'none', color: '#64748b', fontSize: '13px', fontWeight: 500, cursor: 'pointer' }}
            >
              Logout
            </button>
            <button
              onClick={() => fetchSources(apiKey)}
              disabled={isCollecting}
              className="button-secondary"
            >
              Refresh
            </button>
            <button
              onClick={handleCollectAll}
              disabled={isCollecting}
              className="button-primary"
            >
              {isCollecting ? "Collecting..." : "Run Collect All"}
            </button>
          </div>
        </div>

        {error && (
          <div className="error-text" style={{ padding: '12px 16px', background: '#fef2f2', border: '1px solid #fee2e2', borderRadius: '6px' }}>
            {error}
          </div>
        )}

        {collectResult && (
          <div className="success-banner">
            <strong>Collection Complete: </strong>
            Attempted: {collectResult.sources_attempted}, 
            Succeeded: {collectResult.sources_succeeded}, 
            Added: {collectResult.total_added}, 
            Updated: {collectResult.total_updated}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px', alignItems: 'start' }}>
          
          <div className="card">
            <h2 style={{ marginBottom: '16px', fontSize: '16px' }}>Add New Source</h2>
            <form onSubmit={handleAddSource} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label className="input-label">Company Name</label>
                <input
                  type="text"
                  required
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="input-field"
                  placeholder="e.g. OpenAI"
                />
              </div>
              <div>
                <label className="input-label">Source Type</label>
                <select
                  value={sourceType}
                  onChange={(e) => setSourceType(e.target.value)}
                  className="input-field"
                >
                  <option value="lever">Lever</option>
                  <option value="greenhouse">Greenhouse</option>
                </select>
              </div>
              <div>
                <label className="input-label">
                  {sourceType === "greenhouse" ? "Board Token" : "Company ID"}
                </label>
                <input
                  type="text"
                  required
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  className="input-field"
                  placeholder={`e.g. ${sourceType === "greenhouse" ? "openai" : "openai"}`}
                />
              </div>
              <button
                type="submit"
                className="button-primary"
                style={{ marginTop: '8px' }}
              >
                Add Source
              </button>
            </form>
          </div>

          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                    <th style={{ padding: '12px 16px', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.03em' }}>Company</th>
                    <th style={{ padding: '12px 16px', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.03em' }}>Type</th>
                    <th style={{ padding: '12px 16px', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.03em' }}>Identifier</th>
                    <th style={{ padding: '12px 16px', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.03em' }}>Status</th>
                    <th style={{ padding: '12px 16px', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.03em' }}>Last Run</th>
                    <th style={{ padding: '12px 16px', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.03em', textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody style={{ fontSize: '13px' }}>
                  {sources.map((source, i) => (
                    <tr key={source.id} style={{ borderBottom: i === sources.length - 1 ? 'none' : '1px solid #f1f5f9' }}>
                      <td style={{ padding: '14px 16px', fontWeight: 500 }}>{source.company_name}</td>
                      <td style={{ padding: '14px 16px' }}>
                        <span className={`match-label ${source.source_type === 'greenhouse' ? 'applied' : 'interviewing'}`} style={{ textTransform: 'capitalize' }}>
                          {source.source_type}
                        </span>
                      </td>
                      <td style={{ padding: '14px 16px', fontFamily: 'monospace', color: '#64748b' }}>
                        {source.board_token || source.company_id}
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <button 
                          onClick={() => handleToggleEnabled(source)}
                          style={{
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '11px',
                            fontWeight: 600,
                            border: 'none',
                            cursor: 'pointer',
                            background: source.enabled ? '#ecfdf5' : '#f1f5f9',
                            color: source.enabled ? '#059669' : '#64748b'
                          }}
                        >
                          {source.enabled ? 'Enabled' : 'Disabled'}
                        </button>
                      </td>
                      <td style={{ padding: '14px 16px', color: '#64748b', fontSize: '12px' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                          {source.last_run_at ? (
                            <span>Run: {new Date(source.last_run_at).toLocaleString()}</span>
                          ) : (
                            <span>Never run</span>
                          )}
                          {source.last_error ? (
                            <span style={{ color: '#dc2626' }} title={source.last_error}>Failed</span>
                          ) : source.last_success_at ? (
                            <span style={{ color: '#059669' }}>Success</span>
                          ) : null}
                        </div>
                      </td>
                      <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                        <button
                          onClick={() => handleDelete(source.id)}
                          disabled={!source.enabled}
                          style={{
                            background: 'none',
                            border: 'none',
                            fontSize: '12px',
                            fontWeight: 600,
                            color: source.enabled ? '#dc2626' : '#cbd5e1',
                            cursor: source.enabled ? 'pointer' : 'not-allowed'
                          }}
                        >
                          Disable
                        </button>
                      </td>
                    </tr>
                  ))}
                  {sources.length === 0 && (
                    <tr>
                      <td colSpan={6} style={{ padding: '32px 16px', textAlign: 'center', color: '#94a3b8' }}>
                        No sources configured yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
