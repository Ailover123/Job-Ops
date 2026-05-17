"use client";

import { useState, useEffect } from "react";
import {
  SlidersHorizontal, ArrowLeft, Loader2, Save,
  Plus, X, Briefcase, MapPin, Laptop, BadgeCheck, HelpCircle
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

interface PreferenceData {
  preferred_roles: string[];
  preferred_locations: string[];
  remote_preference: string;
  job_types: string[];
  preferred_tech_stack: string[];
  willing_to_relocate: boolean;
}

export default function PreferencesPage() {
  const router = useRouter();
  
  // Form State
  const [roles, setRoles] = useState<string[]>([]);
  const [locations, setLocations] = useState<string[]>([]);
  const [remotePref, setRemotePref] = useState<string>("remote_or_hybrid");
  const [jobTypes, setJobTypes] = useState<string[]>([]);
  const [techStack, setTechStack] = useState<string[]>([]);
  const [willingToRelocate, setWillingToRelocate] = useState<boolean>(false);

  // Input states for tag builders
  const [roleInput, setRoleInput] = useState("");
  const [locationInput, setLocationInput] = useState("");
  const [techInput, setTechInput] = useState("");

  // UI state
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        // Parallel load latest preferences and profile to pre-fill smart defaults
        const [prefRes, profileRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/v1/preferences/latest`),
          fetch(`${API_BASE_URL}/api/v1/profile/latest`)
        ]);

        let hasPrefs = false;
        if (prefRes.ok) {
          const prefData = await prefRes.json();
          if (prefData && !prefData.error) {
            setRoles(prefData.preferred_roles || []);
            setLocations(prefData.preferred_locations || []);
            setRemotePref(prefData.remote_preference || "remote_or_hybrid");
            setJobTypes(prefData.job_types || []);
            setTechStack(prefData.preferred_tech_stack || []);
            setWillingToRelocate(prefData.willing_to_relocate || false);
            hasPrefs = true;
          }
        }

        // If no preferences are set yet, pre-populate using latest saved profile (if any)
        if (!hasPrefs && profileRes.ok) {
          const profileData = await profileRes.json();
          if (profileData && !profileData.error) {
            setRoles(profileData.suggested_roles || []);
            if (profileData.location?.city) {
              setLocations([profileData.location.city]);
            }
            if (profileData.skills) {
              setTechStack(profileData.skills.map((s: any) => s.name) || []);
            }
            // Smart defaults
            setJobTypes(["full_time", "internship"]);
            setRemotePref("remote_or_hybrid");
          }
        }
      } catch (err) {
        console.error("Failed to load initial data", err);
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, []);

  const handleAddRole = (e: React.KeyboardEvent | React.MouseEvent) => {
    if ('key' in e && e.key !== 'Enter') return;
    e.preventDefault();
    const clean = roleInput.trim();
    if (clean && !roles.includes(clean)) {
      setRoles([...roles, clean]);
      setRoleInput("");
    }
  };

  const handleRemoveRole = (roleToRemove: string) => {
    setRoles(roles.filter(r => r !== roleToRemove));
  };

  const handleAddLocation = (e: React.KeyboardEvent | React.MouseEvent) => {
    if ('key' in e && e.key !== 'Enter') return;
    e.preventDefault();
    const clean = locationInput.trim();
    if (clean && !locations.includes(clean)) {
      setLocations([...locations, clean]);
      setLocationInput("");
    }
  };

  const handleRemoveLocation = (locToRemove: string) => {
    setLocations(locations.filter(l => l !== locToRemove));
  };

  const handleAddTech = (e: React.KeyboardEvent | React.MouseEvent) => {
    if ('key' in e && e.key !== 'Enter') return;
    e.preventDefault();
    const clean = techInput.trim();
    if (clean && !techStack.includes(clean)) {
      setTechStack([...techStack, clean]);
      setTechInput("");
    }
  };

  const handleRemoveTech = (techToRemove: string) => {
    setTechStack(techStack.filter(t => t !== techToRemove));
  };

  const toggleJobType = (type: string) => {
    if (jobTypes.includes(type)) {
      setJobTypes(jobTypes.filter(t => t !== type));
    } else {
      setJobTypes([...jobTypes, type]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccess(false);
    setError("");

    const payload: PreferenceData = {
      preferred_roles: roles,
      preferred_locations: locations,
      remote_preference: remotePref,
      job_types: jobTypes,
      preferred_tech_stack: techStack,
      willing_to_relocate: willingToRelocate,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/preferences`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to save match preferences.");
      }

      setSuccess(true);
      setTimeout(() => {
        router.push("/");
      }, 1500);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <main className="centered-page" style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#f8fafc" }}>
        <div style={{ textAlign: "center" }}>
          <Loader2 size={40} className="animate-spin" style={{ color: "#0f766e", marginBottom: "12px" }} />
          <h2 style={{ fontSize: "18px", fontWeight: 600, color: "#1e293b" }}>Loading preferences...</h2>
          <p style={{ color: "#94a3b8", fontSize: "13px" }}>Preparing personalized matching knobs.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="page-shell" style={{ background: "#f8fafc", padding: "28px 16px", minHeight: "100vh" }}>
      <div style={{ maxWidth: "720px", margin: "0 auto" }}>
        {/* Navigation & Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "28px" }}>
          <div>
            <Link href="/" style={{ display: "inline-flex", alignItems: "center", gap: "6px", color: "#64748b", textDecoration: "none", fontSize: "13px", fontWeight: 500, marginBottom: "8px" }} className="hover-teal">
              <ArrowLeft size={14} /> Back to Dashboard
            </Link>
            <h1 style={{ display: "flex", alignItems: "center", gap: "10px", fontSize: "24px", fontWeight: 700, color: "#0f172a" }}>
              <SlidersHorizontal size={24} style={{ color: "#0f766e" }} /> Refine Match Preferences
            </h1>
            <p style={{ color: "#64748b", fontSize: "13.5px", marginTop: "4px", marginBottom: 0 }}>
              Fine-tune the recommendation filters without updating your resume to get exactly the jobs you want.
            </p>
          </div>
        </div>

        {/* Error / Success Notifications */}
        {error && (
          <div style={{ background: "#fef2f2", border: "1px solid #fee2e2", color: "#b91c1c", padding: "12px 16px", borderRadius: "8px", fontSize: "13px", marginBottom: "20px" }}>
            ⚠️ {error}
          </div>
        )}
        
        {success && (
          <div style={{ background: "#ecfdf5", border: "1px solid #d1fae5", color: "#065f46", padding: "12px 16px", borderRadius: "8px", fontSize: "13px", display: "flex", alignItems: "center", gap: "8px", marginBottom: "20px" }}>
            <BadgeCheck size={16} /> Saved successfully! Recalculating personalized dashboard job matches...
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "grid", gap: "20px" }}>
          
          {/* Section: Roles & Titles */}
          <section className="card" style={{ padding: "20px", borderRadius: "10px", background: "#ffffff", border: "1px solid #e2e8f0" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "15px", fontWeight: 600, color: "#0f172a", borderBottom: "1px solid #f1f5f9", paddingBottom: "10px", marginBottom: "16px" }}>
              <Briefcase size={18} style={{ color: "#0f766e" }} /> Target Job Roles
            </h3>
            <div className="input-group">
              <label className="input-label" style={{ fontWeight: 500, color: "#475569" }}>Preferred Roles / Titles</label>
              <div style={{ display: "flex", gap: "8px", marginBottom: "10px" }}>
                <input
                  type="text"
                  placeholder="e.g. Software Engineer, Backend Intern, Data Analyst"
                  value={roleInput}
                  onChange={(e) => setRoleInput(e.target.value)}
                  onKeyDown={handleAddRole}
                  className="input-field"
                  style={{ flex: 1 }}
                />
                <button type="button" onClick={handleAddRole} className="button-secondary" style={{ padding: "0 14px", height: "38px" }}>
                  <Plus size={16} /> Add
                </button>
              </div>
              <p style={{ color: "#94a3b8", fontSize: "12px", marginBottom: "12px" }}>Press Enter or click Add to append multiple roles.</p>
              
              {/* Tag Container */}
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {roles.length === 0 ? (
                  <span style={{ fontSize: "12px", color: "#94a3b8", fontStyle: "italic" }}>No roles added yet (uses resume profile titles)</span>
                ) : (
                  roles.map((role, idx) => (
                    <span key={idx} style={{ display: "inline-flex", alignItems: "center", gap: "4px", background: "#f0fdfa", color: "#0f766e", border: "1px solid #ccfbf1", borderRadius: "6px", padding: "4px 8px", fontSize: "12px", fontWeight: 500 }}>
                      {role}
                      <button type="button" onClick={() => handleRemoveRole(role)} style={{ border: "none", background: "none", padding: 0, display: "flex", alignItems: "center", color: "#0d9488", cursor: "pointer" }}>
                        <X size={12} />
                      </button>
                    </span>
                  ))
                )}
              </div>
            </div>
          </section>

          {/* Section: Tech Stack & Skills */}
          <section className="card" style={{ padding: "20px", borderRadius: "10px", background: "#ffffff", border: "1px solid #e2e8f0" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "15px", fontWeight: 600, color: "#0f172a", borderBottom: "1px solid #f1f5f9", paddingBottom: "10px", marginBottom: "16px" }}>
              <Laptop size={18} style={{ color: "#0f766e" }} /> Key Tech Stack & Skills
            </h3>
            <div className="input-group">
              <label className="input-label" style={{ fontWeight: 500, color: "#475569" }}>Skills to Prioritize</label>
              <div style={{ display: "flex", gap: "8px", marginBottom: "10px" }}>
                <input
                  type="text"
                  placeholder="e.g. React, Node.js, Python, PostgreSQL, AWS"
                  value={techInput}
                  onChange={(e) => setTechInput(e.target.value)}
                  onKeyDown={handleAddTech}
                  className="input-field"
                  style={{ flex: 1 }}
                />
                <button type="button" onClick={handleAddTech} className="button-secondary" style={{ padding: "0 14px", height: "38px" }}>
                  <Plus size={16} /> Add
                </button>
              </div>
              <p style={{ color: "#94a3b8", fontSize: "12px", marginBottom: "12px" }}>These will be appended to your extracted resume skills for scoring matching roles.</p>
              
              {/* Tag Container */}
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {techStack.length === 0 ? (
                  <span style={{ fontSize: "12px", color: "#94a3b8", fontStyle: "italic" }}>No skills added yet (uses resume profile skills)</span>
                ) : (
                  techStack.map((tech, idx) => (
                    <span key={idx} style={{ display: "inline-flex", alignItems: "center", gap: "4px", background: "#eff6ff", color: "#1d4ed8", border: "1px solid #dbeafe", borderRadius: "6px", padding: "4px 8px", fontSize: "12px", fontWeight: 500 }}>
                      {tech}
                      <button type="button" onClick={() => handleRemoveTech(tech)} style={{ border: "none", background: "none", padding: 0, display: "flex", alignItems: "center", color: "#2563eb", cursor: "pointer" }}>
                        <X size={12} />
                      </button>
                    </span>
                  ))
                )}
              </div>
            </div>
          </section>

          {/* Section: Locations & Relocation */}
          <section className="card" style={{ padding: "20px", borderRadius: "10px", background: "#ffffff", border: "1px solid #e2e8f0" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "15px", fontWeight: 600, color: "#0f172a", borderBottom: "1px solid #f1f5f9", paddingBottom: "10px", marginBottom: "16px" }}>
              <MapPin size={18} style={{ color: "#0f766e" }} /> Target Locations
            </h3>
            
            <div className="input-group" style={{ marginBottom: "16px" }}>
              <label className="input-label" style={{ fontWeight: 500, color: "#475569" }}>Preferred Cities / States / Countries</label>
              <div style={{ display: "flex", gap: "8px", marginBottom: "10px" }}>
                <input
                  type="text"
                  placeholder="e.g. Bangalore, Remote, San Francisco, Munich"
                  value={locationInput}
                  onChange={(e) => setLocationInput(e.target.value)}
                  onKeyDown={handleAddLocation}
                  className="input-field"
                  style={{ flex: 1 }}
                />
                <button type="button" onClick={handleAddLocation} className="button-secondary" style={{ padding: "0 14px", height: "38px" }}>
                  <Plus size={16} /> Add
                </button>
              </div>
              
              {/* Tag Container */}
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "16px" }}>
                {locations.length === 0 ? (
                  <span style={{ fontSize: "12px", color: "#94a3b8", fontStyle: "italic" }}>No locations added yet (matches globally)</span>
                ) : (
                  locations.map((loc, idx) => (
                    <span key={idx} style={{ display: "inline-flex", alignItems: "center", gap: "4px", background: "#faf5ff", color: "#7e22ce", border: "1px solid #f3e8ff", borderRadius: "6px", padding: "4px 8px", fontSize: "12px", fontWeight: 500 }}>
                      {loc}
                      <button type="button" onClick={() => handleRemoveLocation(loc)} style={{ border: "none", background: "none", padding: 0, display: "flex", alignItems: "center", color: "#9333ea", cursor: "pointer" }}>
                        <X size={12} />
                      </button>
                    </span>
                  ))
                )}
              </div>
            </div>

            {/* Willing to Relocate Toggle */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px", background: "#f8fafc", borderRadius: "8px", border: "1px solid #f1f5f9" }}>
              <div>
                <span style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#1e293b" }}>Open to Relocation</span>
                <span style={{ display: "block", fontSize: "12px", color: "#64748b", marginTop: "2px" }}>Bypass hard location mismatch filters for matching high-value opportunities globally.</span>
              </div>
              <label style={{ position: "relative", display: "inline-block", width: "44px", height: "24px", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={willingToRelocate}
                  onChange={(e) => setWillingToRelocate(e.target.checked)}
                  style={{ opacity: 0, width: 0, height: 0 }}
                />
                <span style={{
                  position: "absolute",
                  top: 0, left: 0, right: 0, bottom: 0,
                  backgroundColor: willingToRelocate ? "#0f766e" : "#cbd5e1",
                  borderRadius: "24px",
                  transition: "0.2s",
                }}>
                  <span style={{
                    position: "absolute",
                    content: '""',
                    height: "18px", width: "18px",
                    left: willingToRelocate ? "22px" : "3px",
                    bottom: "3px",
                    backgroundColor: "white",
                    borderRadius: "50%",
                    transition: "0.2s",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.15)"
                  }} />
                </span>
              </label>
            </div>
          </section>

          {/* Section: Remote Prefs & Job Types */}
          <section className="card" style={{ padding: "20px", borderRadius: "10px", background: "#ffffff", border: "1px solid #e2e8f0" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "15px", fontWeight: 600, color: "#0f172a", borderBottom: "1px solid #f1f5f9", paddingBottom: "10px", marginBottom: "16px" }}>
              <Laptop size={18} style={{ color: "#0f766e" }} /> Work Mode & Job Type
            </h3>

            {/* Remote Pref */}
            <div className="input-group" style={{ marginBottom: "20px" }}>
              <label className="input-label" style={{ fontWeight: 500, color: "#475569", marginBottom: "8px" }}>Remote Policy Preferences</label>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: "10px" }}>
                {[
                  { value: "remote", label: "Fully Remote" },
                  { value: "onsite", label: "Onsite" },
                  { value: "hybrid", label: "Hybrid" },
                  { value: "remote_or_hybrid", label: "Remote or Hybrid" }
                ].map(opt => {
                  const active = remotePref === opt.value;
                  return (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => setRemotePref(opt.value)}
                      style={{
                        padding: "10px",
                        fontSize: "12.5px",
                        fontWeight: 500,
                        borderRadius: "8px",
                        border: active ? "2px solid #0f766e" : "1px solid #e2e8f0",
                        background: active ? "#f0fdfa" : "#ffffff",
                        color: active ? "#0f766e" : "#475569",
                        textAlign: "center",
                        transition: "all 0.15s"
                      }}
                    >
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Job Types */}
            <div className="input-group" style={{ marginBottom: 0 }}>
              <label className="input-label" style={{ fontWeight: 500, color: "#475569", marginBottom: "8px" }}>Job Types</label>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
                {[
                  { value: "full_time", label: "Full Time" },
                  { value: "part_time", label: "Part Time" },
                  { value: "internship", label: "Internship / Co-op" },
                  { value: "contract", label: "Contract" }
                ].map(opt => {
                  const checked = jobTypes.includes(opt.value);
                  return (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => toggleJobType(opt.value)}
                      style={{
                        padding: "8px 14px",
                        fontSize: "12px",
                        fontWeight: 500,
                        borderRadius: "20px",
                        border: checked ? "1px solid #0f766e" : "1px solid #e2e8f0",
                        background: checked ? "#0f766e" : "#ffffff",
                        color: checked ? "#ffffff" : "#475569",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "6px",
                        transition: "all 0.15s"
                      }}
                    >
                      {checked && <span style={{ fontSize: "10px" }}>✓</span>}
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </section>

          {/* Save Action Row */}
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px", marginTop: "10px" }}>
            <Link href="/" className="button-secondary" style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", padding: "10px 20px", textDecoration: "none", fontSize: "14px", fontWeight: 500, borderRadius: "8px", height: "42px" }}>
              Cancel
            </Link>
            <button
              type="submit"
              className="button-primary"
              disabled={saving}
              style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", gap: "8px", padding: "10px 24px", fontSize: "14px", fontWeight: 600, borderRadius: "8px", background: "#0f766e", color: "#ffffff", border: "none", height: "42px", cursor: "pointer" }}
            >
              {saving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
              {saving ? "Refining matches..." : "Apply & Refine Matches"}
            </button>
          </div>

        </form>
      </div>
    </main>
  );
}
