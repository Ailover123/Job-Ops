"use client";

import { useEffect, useState } from "react";
import { ClipboardList, Calendar, Edit3, Check, X, Loader2 } from "lucide-react";
import Link from "next/link";
import Navigation from "../components/Navigation";
import JobCard from "../components/JobCard";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export default function ApplicationsPage() {
  const [apps, setApps] = useState<any[]>([]);
  const [savedIds, setSavedIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Note-editing state
  const [editingAppId, setEditingAppId] = useState<string | null>(null);
  const [editingNoteText, setEditingNoteText] = useState("");
  const [savingNoteId, setSavingNoteId] = useState<string | null>(null);

  // Status-updating state
  const [updatingStatusId, setUpdatingStatusId] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [appsRes, savedRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/applications`),
        fetch(`${API_BASE_URL}/api/v1/saved-jobs`),
      ]);

      if (!appsRes.ok) throw new Error("Failed to fetch applications");
      if (!savedRes.ok) throw new Error("Failed to fetch saved jobs");

      const appsData = await appsRes.json();
      const savedData = await savedRes.json();

      setApps(appsData.items || []);
      setSavedIds((savedData.items || []).map((j: any) => j.job_external_id));
    } catch (e) {
      console.error(e);
      setError("Could not load applications. Please ensure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleUpdateStatus = async (jobId: string, newStatus: string) => {
    setUpdatingStatusId(jobId);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/applications/${jobId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!res.ok) throw new Error("Failed to update status");

      const data = await res.json();
      const updatedApp = data.item;

      // Update local state
      setApps((prevApps) =>
        prevApps.map((app) =>
          app.job_external_id === jobId ? { ...app, status: updatedApp.status } : app
        )
      );
    } catch (e) {
      console.error(e);
      alert("Error updating status. Please try again.");
    } finally {
      setUpdatingStatusId(null);
    }
  };

  const handleSaveNote = async (jobId: string) => {
    setSavingNoteId(jobId);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/applications/${jobId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ notes: editingNoteText }),
      });

      if (!res.ok) throw new Error("Failed to save note");

      const data = await res.json();
      const updatedApp = data.item;

      // Update local state
      setApps((prevApps) =>
        prevApps.map((app) =>
          app.job_external_id === jobId ? { ...app, notes: updatedApp.notes } : app
        )
      );

      // Exit edit mode
      setEditingAppId(null);
      setEditingNoteText("");
    } catch (e) {
      console.error(e);
      alert("Error saving note. Please try again.");
    } finally {
      setSavingNoteId(null);
    }
  };

  const startEditing = (jobId: string, currentNotes: string) => {
    setEditingAppId(jobId);
    setEditingNoteText(currentNotes || "");
  };

  const cancelEditing = () => {
    setEditingAppId(null);
    setEditingNoteText("");
  };

  if (loading) {
    return (
      <main className="page-shell">
        <header className="topbar">
          <div className="topbar-inner">
            <div className="topbar-left">
              <div>
                <p className="brand">Job-Ops</p>
                <h1>Applications</h1>
              </div>
              <Navigation />
            </div>
          </div>
        </header>
        <section className="dashboard-layout" style={{ gridTemplateColumns: "1fr" }}>
          <section style={{ maxWidth: "780px", margin: "0 auto", width: "100%", padding: "24px" }}>
            <div style={{ textAlign: "center", padding: "48px 0", color: "#64748b" }}>
              <Loader2 className="spinner" size={32} style={{ margin: "0 auto 16px" }} />
              <p>Loading your tracked applications...</p>
            </div>
          </section>
        </section>
      </main>
    );
  }

  if (error) {
    return (
      <main className="page-shell">
        <header className="topbar">
          <div className="topbar-inner">
            <div className="topbar-left">
              <div>
                <p className="brand">Job-Ops</p>
                <h1>Applications</h1>
              </div>
              <Navigation />
            </div>
          </div>
        </header>
        <section className="dashboard-layout" style={{ gridTemplateColumns: "1fr" }}>
          <section style={{ maxWidth: "780px", margin: "0 auto", width: "100%", padding: "24px" }}>
            <div className="empty-state" style={{ borderColor: "#fca5a5", background: "#fff5f5" }}>
              <h3 style={{ color: "#c5221f" }}>Failed to load applications</h3>
              <p>{error}</p>
              <button onClick={fetchData} className="button-primary" style={{ marginTop: "12px" }}>
                Retry Connection
              </button>
            </div>
          </section>
        </section>
      </main>
    );
  }

  return (
    <main className="page-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="topbar-left">
            <div>
              <p className="brand">Job-Ops</p>
              <h1>Applications</h1>
            </div>
            <Navigation />
          </div>
        </div>
      </header>

      <section className="dashboard-layout" style={{ gridTemplateColumns: "1fr" }}>
        <section style={{ maxWidth: "780px", margin: "0 auto", width: "100%" }}>
          <div className="section-heading">
            <div>
              <h2>Tracked Applications</h2>
              <p>Jobs you've marked as applied.</p>
            </div>
            <strong>{apps.length} applied</strong>
          </div>

          {apps.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">
                <ClipboardList size={40} />
              </div>
              <h3>No applications recorded</h3>
              <p>Apply to jobs from your recommendations and mark them as applied to track here.</p>
              <Link href="/" className="button-primary">
                View Recommendations
              </Link>
            </div>
          ) : (
            <div className="job-list">
              {apps.map((app: any) => {
                const isEditing = editingAppId === app.job_external_id;
                const isSavingNote = savingNoteId === app.job_external_id;
                const isUpdatingStatus = updatingStatusId === app.job_external_id;

                return (
                  <div key={app.job_external_id} className="app-card-wrapper" style={{ marginBottom: "24px" }}>
                    <JobCard
                      job={{
                        external_id: app.job_external_id,
                        title: app.job_title,
                        company_name: app.company_name,
                        location: app.location || "Unknown",
                        source_name: app.source_name,
                        apply_url: app.apply_url,
                        skills: app.skills || [],
                      }}
                      score_label={app.status.toUpperCase()}
                      final_score={100}
                      initialSaved={savedIds.includes(app.job_external_id)}
                      initialApplied={true}
                    />

                    <div
                      className="app-footer"
                      style={{
                        borderTop: "1px solid #e2e8f0",
                        background: "#f8fafc",
                        padding: "10px 16px",
                        display: "flex",
                        flexWrap: "wrap",
                        justifyContent: "space-between",
                        alignItems: "center",
                        gap: "16px",
                      }}
                    >
                      {/* Left: Status & Applied Date */}
                      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "4px",
                            color: "#64748b",
                            fontSize: "12px",
                          }}
                        >
                          <Calendar size={13} />
                          {new Date(app.applied_at).toLocaleDateString()}
                        </span>

                        <div style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
                          <label htmlFor={`status-select-${app.job_external_id}`} className="visually-hidden">
                            Status
                          </label>
                          <select
                            id={`status-select-${app.job_external_id}`}
                            value={app.status}
                            disabled={isUpdatingStatus}
                            onChange={(e) => handleUpdateStatus(app.job_external_id, e.target.value)}
                            className="status-dropdown"
                            style={{
                              background: "#ffffff",
                              border: "1px solid #cbd5e1",
                              borderRadius: "6px",
                              color: "#334155",
                              fontSize: "11px",
                              fontWeight: 600,
                              padding: "4px 8px",
                              cursor: "pointer",
                              outline: "none",
                              boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
                            }}
                          >
                            <option value="applied">Applied</option>
                            <option value="interviewing">Interviewing</option>
                            <option value="offer">Offer Received</option>
                            <option value="rejected">Rejected</option>
                            <option value="withdrawn">Withdrawn</option>
                          </select>
                          {isUpdatingStatus && (
                            <Loader2 className="spinner" size={12} style={{ color: "#0f766e" }} />
                          )}
                        </div>
                      </div>

                      {/* Right: Notes Management */}
                      <div
                        style={{
                          flex: 1,
                          minWidth: "240px",
                          display: "flex",
                          justifyContent: "flex-end",
                          alignItems: "center",
                        }}
                      >
                        {isEditing ? (
                          <div style={{ display: "flex", width: "100%", gap: "8px", alignItems: "center" }}>
                            <label htmlFor={`notes-input-${app.job_external_id}`} className="visually-hidden">
                              Edit Notes
                            </label>
                            <input
                              id={`notes-input-${app.job_external_id}`}
                              type="text"
                              value={editingNoteText}
                              onChange={(e) => setEditingNoteText(e.target.value)}
                              placeholder="Add custom application notes..."
                              disabled={isSavingNote}
                              style={{
                                flex: 1,
                                padding: "4px 8px",
                                fontSize: "12px",
                                border: "1px solid #cbd5e1",
                                borderRadius: "6px",
                                outline: "none",
                                background: "#ffffff",
                              }}
                            />
                            <button
                              onClick={() => handleSaveNote(app.job_external_id)}
                              disabled={isSavingNote}
                              title="Save Notes"
                              aria-label="Save Notes"
                              style={{
                                background: "#0f766e",
                                color: "#ffffff",
                                border: "none",
                                borderRadius: "6px",
                                width: "26px",
                                height: "26px",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                cursor: "pointer",
                              }}
                            >
                              {isSavingNote ? <Loader2 className="spinner" size={13} /> : <Check size={13} />}
                            </button>
                            <button
                              onClick={cancelEditing}
                              disabled={isSavingNote}
                              title="Cancel Editing"
                              aria-label="Cancel Editing"
                              style={{
                                background: "#f1f5f9",
                                color: "#475569",
                                border: "1px solid #cbd5e1",
                                borderRadius: "6px",
                                width: "26px",
                                height: "26px",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                cursor: "pointer",
                              }}
                            >
                              <X size={13} />
                            </button>
                          </div>
                        ) : (
                          <div
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: "8px",
                              width: "100%",
                              justifyContent: "flex-end",
                            }}
                          >
                            {app.notes ? (
                              <span
                                style={{
                                  fontSize: "12px",
                                  color: "#475569",
                                  fontStyle: "italic",
                                  overflow: "hidden",
                                  textOverflow: "ellipsis",
                                  whiteSpace: "nowrap",
                                  maxWidth: "300px",
                                }}
                              >
                                Note: {app.notes}
                              </span>
                            ) : (
                              <span style={{ fontSize: "11px", color: "#94a3b8" }}>No notes added</span>
                            )}
                            <button
                              onClick={() => startEditing(app.job_external_id, app.notes)}
                              style={{
                                background: "transparent",
                                border: "none",
                                color: "#0f766e",
                                fontSize: "11px",
                                fontWeight: 600,
                                display: "inline-flex",
                                alignItems: "center",
                                gap: "3px",
                                padding: "2px 6px",
                                borderRadius: "4px",
                                cursor: "pointer",
                              }}
                            >
                              <Edit3 size={11} />
                              {app.notes ? "Edit" : "+ Add note"}
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
