"use client";

import React, { useState, useEffect } from "react";
import Navigation from "../components/Navigation";
import Link from "next/link";
import { 
  Milestone, 
  Sparkles, 
  BookOpen, 
  Code, 
  CheckCircle2, 
  ArrowRight, 
  Search, 
  Check, 
  HelpCircle,
  Briefcase,
  AlertCircle
} from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

interface RoadmapData {
  desired_role: string;
  existing_skills: string[];
  missing_skills: string[];
  recommended_learning_order: string[];
  suggested_project_ideas: string[];
  matching_jobs_used_count: number;
  explanation: string;
}

export default function RoadmapPage() {
  const [desiredRole, setDesiredRole] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [roadmap, setRoadmap] = useState<RoadmapData | null>(null);
  const [profileRoles, setProfileRoles] = useState<string[]>([]);
  const [fetchingProfile, setFetchingProfile] = useState(true);

  // Suggested starter roles
  const SUGGESTED_ROLES = [
    "AI Engineer Intern",
    "Backend Developer",
    "Frontend Developer",
    "Data Scientist",
    "Software Engineer"
  ];

  // Fetch the latest profile suggest_roles on load
  useEffect(() => {
    async function fetchProfile() {
      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/profile/latest`);
        if (res.ok) {
          const profile = await res.json();
          if (profile && profile.suggested_roles && profile.suggested_roles.length > 0) {
            setProfileRoles(profile.suggested_roles);
            // Default to the first suggested role
            const firstRole = profile.suggested_roles[0];
            setDesiredRole(firstRole);
            generateRoadmap(firstRole);
          } else {
            // Fallback default role
            setDesiredRole("AI Engineer Intern");
            generateRoadmap("AI Engineer Intern");
          }
        } else {
          // Fallback default role
          setDesiredRole("AI Engineer Intern");
          generateRoadmap("AI Engineer Intern");
        }
      } catch (e) {
        setDesiredRole("AI Engineer Intern");
        generateRoadmap("AI Engineer Intern");
      } finally {
        setFetchingProfile(false);
      }
    }
    fetchProfile();
  }, []);

  const generateRoadmap = async (roleToQuery: string) => {
    const queryRole = roleToQuery || desiredRole;
    if (!queryRole.trim()) {
      setError("Please enter or select a desired role.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/roadmap/skill-gap`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ desired_role: queryRole })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to generate roadmap");
      }

      const data = await res.json();
      setRoadmap(data);
    } catch (e: any) {
      setError(e.message || "Something went wrong. Please check your backend connection.");
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestClick = (role: string) => {
    setDesiredRole(role);
    generateRoadmap(role);
  };

  return (
    <main className="page-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="topbar-left">
            <div>
              <p className="brand">Job-Ops</p>
              <h1>Skill Gap Roadmap</h1>
            </div>
            <Navigation />
          </div>
        </div>
      </header>

      <section className="dashboard-layout" style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '24px', alignItems: 'start' }}>
        {/* Left Control Panel */}
        <aside className="profile-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#0f172a', marginBottom: '8px' }}>Select Target Role</h2>
            <p style={{ fontSize: '0.85rem', color: '#64748b', lineHeight: '1.4' }}>
              Analyze matching industry seed jobs and construct a clear learning path based on your current skills.
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label htmlFor="desired-role-input" style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#64748b', letterSpacing: '0.05em' }}>
              Target Job Role
            </label>
            <div style={{ position: 'relative' }}>
              <input
                id="desired-role-input"
                type="text"
                value={desiredRole}
                onChange={(e) => setDesiredRole(e.target.value)}
                placeholder="e.g. AI Engineer Intern"
                style={{
                  width: '100%',
                  padding: '10px 36px 10px 12px',
                  borderRadius: '8px',
                  border: '1px solid #cbd5e1',
                  fontSize: '0.9rem',
                  outline: 'none',
                  transition: 'border-color 0.2s',
                  color: '#0f172a'
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") generateRoadmap(desiredRole);
                }}
              />
              <Search size={16} style={{ position: 'absolute', right: '12px', top: '12px', color: '#94a3b8' }} />
            </div>
          </div>

          <button
            onClick={() => generateRoadmap(desiredRole)}
            disabled={loading}
            style={{
              width: '100%',
              padding: '12px',
              borderRadius: '8px',
              border: 'none',
              background: 'linear-gradient(135deg, #0f766e 0%, #0d9488 100%)',
              color: '#ffffff',
              fontWeight: 600,
              fontSize: '0.9rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              boxShadow: '0 4px 6px -1px rgba(13, 148, 136, 0.2)',
              opacity: loading ? 0.7 : 1
            }}
          >
            {loading ? (
              <>
                <div className="spinner" style={{ width: '16px', height: '16px', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 0.6s linear infinite' }} />
                Analyzing Gap...
              </>
            ) : (
              <>
                <Milestone size={16} />
                Generate Roadmap
              </>
            )}
          </button>

          {/* Preset Roles / Suggested From Profile */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', paddingTop: '16px', borderTop: '1px solid #e2e8f0' }}>
            <p style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: '#64748b', letterSpacing: '0.05em' }}>
              {profileRoles.length > 0 ? "Suggested From Profile" : "Popular Roles"}
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {(profileRoles.length > 0 ? profileRoles : SUGGESTED_ROLES).map((role) => (
                <button
                  key={role}
                  onClick={() => handleSuggestClick(role)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '20px',
                    border: '1px solid #e2e8f0',
                    background: desiredRole.toLowerCase() === role.toLowerCase() ? '#f0fdfa' : '#ffffff',
                    color: desiredRole.toLowerCase() === role.toLowerCase() ? '#0f766e' : '#475569',
                    borderColor: desiredRole.toLowerCase() === role.toLowerCase() ? '#99f6e4' : '#e2e8f0',
                    fontSize: '0.75rem',
                    fontWeight: 500,
                    cursor: 'pointer',
                    transition: 'all 0.15s'
                  }}
                >
                  {role}
                </button>
              ))}
            </div>
          </div>
        </aside>

        {/* Right Output Panel */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {error && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '16px', borderRadius: '12px', background: '#fef2f2', border: '1px solid #fee2e2', color: '#991b1b' }}>
              <AlertCircle size={20} />
              <p style={{ fontSize: '0.9rem', fontWeight: 500 }}>{error}</p>
            </div>
          )}

          {loading ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 24px', background: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0', gap: '16px' }}>
              <div className="spinner" style={{ width: '40px', height: '40px', border: '3px solid #f3f4f6', borderTopColor: '#0f766e', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
              <div style={{ textAlign: 'center' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0f172a', marginBottom: '4px' }}>Mapping Your Learning Path</h3>
                <p style={{ fontSize: '0.85rem', color: '#64748b' }}>Scanning local industry seed jobs to locate key skill gaps...</p>
              </div>
            </div>
          ) : roadmap ? (
            <>
              {/* Overview Header */}
              <div style={{ padding: '24px', background: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', gap: '16px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)' }}>
                <div style={{ display: 'flex', justifyContent: 'between', alignItems: 'start', flexWrap: 'wrap', gap: '12px' }}>
                  <div>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 10px', borderRadius: '20px', background: '#f0fdfa', color: '#0f766e', fontSize: '0.75rem', fontWeight: 600, marginBottom: '8px' }}>
                      <Sparkles size={12} />
                      AI & Rule-Based Skill Graph
                    </span>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>{roadmap.desired_role}</h2>
                    <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '4px' }}>
                      Roadmap generated from <span style={{ fontWeight: 600, color: '#0f172a' }}>{roadmap.matching_jobs_used_count} matching seed jobs</span> in our local pool.
                    </p>
                  </div>
                </div>

                <div style={{ padding: '16px', background: '#f8fafc', borderRadius: '12px', borderLeft: '4px solid #0d9488', fontSize: '0.9rem', lineHeight: '1.6', color: '#334155' }}>
                  {roadmap.explanation}
                </div>
              </div>

              {/* Skills Grid: Mastering vs Prep */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                {/* Mastered Skills */}
                <div style={{ padding: '20px', background: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0' }}>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#0f172a', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={18} style={{ color: '#10b981' }} />
                    Skills You Already Master ({roadmap.existing_skills.length})
                  </h3>
                  {roadmap.existing_skills.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {roadmap.existing_skills.map((skill) => (
                        <span
                          key={skill}
                          style={{
                            padding: '6px 12px',
                            borderRadius: '8px',
                            background: '#f0fdf4',
                            color: '#166534',
                            border: '1px solid #dcfce7',
                            fontSize: '0.85rem',
                            fontWeight: 500,
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px'
                          }}
                        >
                          <Check size={12} />
                          {skill}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p style={{ fontSize: '0.85rem', color: '#64748b', fontStyle: 'italic' }}>
                      None of the target skills matched your profile yet. Try updating your resume.
                    </p>
                  )}
                </div>

                {/* Skills to Learn */}
                <div style={{ padding: '20px', background: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0' }}>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#0f172a', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <BookOpen size={18} style={{ color: '#f59e0b' }} />
                    Skills to Learn/Refine ({roadmap.missing_skills.length})
                  </h3>
                  {roadmap.missing_skills.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {roadmap.missing_skills.map((skill) => (
                        <span
                          key={skill}
                          style={{
                            padding: '6px 12px',
                            borderRadius: '8px',
                            background: '#fffbeb',
                            color: '#92400e',
                            border: '1px solid #fef3c7',
                            fontSize: '0.85rem',
                            fontWeight: 500
                          }}
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p style={{ fontSize: '0.85rem', color: '#166534', fontWeight: 600 }}>
                      Amazing! You have 100% of the common skills required for this role!
                    </p>
                  )}
                </div>
              </div>

              {/* Recommended Learning Roadmap */}
              {roadmap.recommended_learning_order.length > 0 && (
                <div style={{ padding: '24px', background: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0f172a', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Milestone size={18} style={{ color: '#0f766e' }} />
                    Step-by-Step Learning Timeline
                  </h3>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', position: 'relative', paddingLeft: '24px' }}>
                    {/* Vertical Line */}
                    <div style={{ position: 'absolute', left: '7px', top: '8px', bottom: '8px', width: '2px', background: '#e2e8f0' }} />

                    {roadmap.recommended_learning_order.map((skill, index) => (
                      <div key={skill} style={{ position: 'relative', display: 'flex', gap: '12px', alignItems: 'start' }}>
                        {/* Circle bullet */}
                        <div
                          style={{
                            position: 'absolute',
                            left: '-24px',
                            top: '4px',
                            width: '16px',
                            height: '16px',
                            borderRadius: '50%',
                            background: index === 0 ? '#0f766e' : '#ffffff',
                            border: '3px solid #0f766e',
                            zIndex: 10
                          }}
                        />
                        <div>
                          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#0f172a' }}>
                            Step {index + 1}: Master {skill}
                          </h4>
                          <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '2px' }}>
                            {index === 0 
                              ? "Foundational priority. Acquire standard competency first to unlock later development."
                              : index === 1 
                                ? "Primary engineering component. Deepen hands-on proficiency."
                                : "Refinement & specialization. Integrate with other components inside full applications."}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Hands-on Project Ideas */}
              {roadmap.suggested_project_ideas.length > 0 && (
                <div style={{ padding: '24px', background: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0f172a', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Code size={18} style={{ color: '#0f766e' }} />
                    Hands-On Project Portfolio Ideas
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px' }}>
                    {roadmap.suggested_project_ideas.map((idea, idx) => (
                      <div
                        key={idx}
                        style={{
                          padding: '16px',
                          borderRadius: '12px',
                          border: '1px solid #f1f5f9',
                          background: '#f8fafc',
                          display: 'flex',
                          gap: '12px',
                          alignItems: 'start'
                        }}
                      >
                        <div style={{ padding: '6px', background: '#e0f2fe', color: '#0369a1', borderRadius: '8px', fontSize: '0.85rem', fontWeight: 700 }}>
                          P{idx + 1}
                        </div>
                        <div>
                          <p style={{ fontSize: '0.875rem', fontWeight: 500, color: '#1e293b', lineHeight: '1.5' }}>
                            {idea}
                          </p>
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: '#0284c7', marginTop: '6px', fontWeight: 600 }}>
                            Build to show on resume <ArrowRight size={12} />
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div style={{ padding: '60px 24px', background: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0', textAlign: 'center' }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>🗺️</div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0f172a', marginBottom: '8px' }}>No Roadmap Generated</h3>
              <p style={{ fontSize: '0.85rem', color: '#64748b', maxWidth: '400px', margin: '0 auto 16px' }}>
                Enter your desired role in the left sidebar to generate a fully customized visual gap analysis.
              </p>
            </div>
          )}
        </section>
      </section>

      {/* Global CSS for spinner animation */}
      <style jsx global>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </main>
  );
}
