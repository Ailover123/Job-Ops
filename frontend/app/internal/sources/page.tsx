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
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full border border-gray-100">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Internal Access</h1>
          <p className="text-gray-600 mb-4 text-sm">Please enter the internal API key to access source management.</p>
          <div className="space-y-4">
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="X-Internal-API-Key"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              onKeyDown={(e) => e.key === "Enter" && handleSaveKey()}
            />
            <button
              onClick={handleSaveKey}
              className="w-full bg-blue-600 text-white font-semibold py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Authenticate
            </button>
            {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        
        <div className="flex justify-between items-center bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Job Sources</h1>
            <p className="text-gray-500 mt-1">Manage collector configurations</p>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => {
                sessionStorage.removeItem("internal_api_key");
                setHasKey(false);
              }}
              className="text-gray-500 hover:text-gray-700 text-sm font-medium"
            >
              Logout
            </button>
            <button
              onClick={handleCollectAll}
              disabled={isCollecting}
              className={`px-6 py-2 rounded-lg font-semibold text-white transition-colors ${
                isCollecting ? "bg-blue-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {isCollecting ? "Collecting..." : "Run Collect All"}
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">
            {error}
          </div>
        )}

        {collectResult && (
          <div className="bg-green-50 text-green-800 p-4 rounded-lg border border-green-200 text-sm">
            <strong>Collection Complete: </strong>
            Attempted: {collectResult.sources_attempted}, 
            Succeeded: {collectResult.sources_succeeded}, 
            Added: {collectResult.total_added}, 
            Updated: {collectResult.total_updated}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          <div className="lg:col-span-1">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 sticky top-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Add New Source</h2>
              <form onSubmit={handleAddSource} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
                  <input
                    type="text"
                    required
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
                    placeholder="e.g. OpenAI"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Source Type</label>
                  <select
                    value={sourceType}
                    onChange={(e) => setSourceType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 outline-none text-sm bg-white"
                  >
                    <option value="lever">Lever</option>
                    <option value="greenhouse">Greenhouse</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {sourceType === "greenhouse" ? "Board Token" : "Company ID"}
                  </label>
                  <input
                    type="text"
                    required
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
                    placeholder={`e.g. ${sourceType === "greenhouse" ? "openai" : "openai"}`}
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-gray-900 text-white font-medium py-2 rounded-md hover:bg-gray-800 transition-colors text-sm"
                >
                  Add Source
                </button>
              </form>
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-100 text-xs uppercase text-gray-500 font-semibold tracking-wider">
                      <th className="p-4">Company</th>
                      <th className="p-4">Type</th>
                      <th className="p-4">Identifier</th>
                      <th className="p-4">Status</th>
                      <th className="p-4">Last Run</th>
                      <th className="p-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 text-sm">
                    {sources.map(source => (
                      <tr key={source.id} className="hover:bg-gray-50 transition-colors">
                        <td className="p-4 font-medium text-gray-900">{source.company_name}</td>
                        <td className="p-4">
                          <span className={`px-2 py-1 rounded text-xs font-medium capitalize ${
                            source.source_type === 'greenhouse' ? 'bg-emerald-100 text-emerald-800' : 'bg-purple-100 text-purple-800'
                          }`}>
                            {source.source_type}
                          </span>
                        </td>
                        <td className="p-4 text-gray-600 font-mono text-xs">
                          {source.board_token || source.company_id}
                        </td>
                        <td className="p-4">
                          <button 
                            onClick={() => handleToggleEnabled(source)}
                            className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                              source.enabled ? 'bg-green-100 text-green-800 hover:bg-green-200' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                          >
                            {source.enabled ? 'Enabled' : 'Disabled'}
                          </button>
                        </td>
                        <td className="p-4">
                          {source.last_error ? (
                            <span className="text-red-600 text-xs" title={source.last_error}>Failed</span>
                          ) : source.last_success_at ? (
                            <span className="text-gray-500 text-xs">{new Date(source.last_success_at).toLocaleDateString()}</span>
                          ) : (
                            <span className="text-gray-400 text-xs">Never</span>
                          )}
                        </td>
                        <td className="p-4 text-right">
                          <button
                            onClick={() => handleDelete(source.id)}
                            disabled={!source.enabled}
                            className={`text-xs font-medium ${source.enabled ? 'text-red-600 hover:text-red-800' : 'text-gray-300 cursor-not-allowed'}`}
                          >
                            Disable
                          </button>
                        </td>
                      </tr>
                    ))}
                    {sources.length === 0 && (
                      <tr>
                        <td colSpan={6} className="p-8 text-center text-gray-500">
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
    </div>
  );
}
