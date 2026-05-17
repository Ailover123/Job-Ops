import { SlidersHorizontal } from "lucide-react";
import Navigation from "./components/Navigation";
import JobCard from "./components/JobCard";
import Link from "next/link";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

const MOCK_RECOMMENDATIONS = [
  {
    job: {
      external_id: "seed-1",
      title: "Python Developer Intern",
      company_name: "NovaSkill Labs",
      location: "Bangalore",
      source_name: "Direct",
      apply_url: "https://example.com",
      skills: ["Python", "APIs", "SQL"]
    },
    score_label: "Strong Match",
    final_score: 92
  },
  {
    job: {
      external_id: "seed-2",
      title: "Junior AI Engineer",
      company_name: "VectorBridge AI",
      location: "Remote",
      source_name: "LinkedIn",
      apply_url: "https://example.com",
      skills: ["Python", "RAG", "LLMs"]
    },
    score_label: "Good Match",
    final_score: 85
  }
];

async function getRecommendations() {
  try {
    const personalizedRes = await fetch(`${API_BASE_URL}/api/v1/recommendations/latest-profile`, {
      next: { revalidate: 0 },
    });

    if (personalizedRes.ok) {
      const data = await personalizedRes.json();
      if (data.status === "personalized") {
        return { items: data.items, status: "personalized" };
      }
    }

    const demoRes = await fetch(`${API_BASE_URL}/api/v1/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        preferred_roles: ["Python Developer", "AI Intern", "Data Analyst"],
        skills: ["Python", "MySQL", "RAG", "APIs"],
        preferred_locations: ["Bangalore", "Remote"],
        remote_preference: "remote_or_hybrid",
        job_types: ["internship", "full_time"],
        experience_level: "fresher",
      }),
      next: { revalidate: 0 },
    });

    if (demoRes.ok) {
      const items = await demoRes.json();
      return { items: items, status: "demo" };
    }

    return { items: MOCK_RECOMMENDATIONS, status: "offline" };
  } catch (e) {
    return { items: MOCK_RECOMMENDATIONS, status: "offline" };
  }
}

async function getLatestProfile() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/profile/latest`, {
      next: { revalidate: 0 },
    });
    if (res.ok) {
      const data = await res.json();
      if (data && data.status !== "error") {
        return data;
      }
    }
    return null;
  } catch (e) {
    return null;
  }
}

async function getUserJobStats() {
  try {
    const [savedRes, appliedRes] = await Promise.all([
      fetch(`${API_BASE_URL}/api/v1/saved-jobs`, { next: { revalidate: 0 } }),
      fetch(`${API_BASE_URL}/api/v1/applications`, { next: { revalidate: 0 } })
    ]);

    const saved = savedRes.ok ? (await savedRes.json()).items : [];
    const applied = appliedRes.ok ? (await appliedRes.json()).items : [];

    return {
      savedIds: saved.map((j: any) => j.job_external_id),
      appliedIds: applied.map((a: any) => a.job_external_id)
    };
  } catch (e) {
    return { savedIds: [], appliedIds: [] };
  }
}

export const dynamic = 'force-dynamic';

export default async function Home() {
  const [
    { items: recommendations, status },
    { savedIds, appliedIds },
    profile
  ] = await Promise.all([
    getRecommendations(),
    getUserJobStats(),
    getLatestProfile()
  ]);
  
  const statusMessage = status === "personalized" 
    ? "Ranked by your saved profile."
    : status === "demo"
      ? "Showing preview data."
      : "Preview mode (backend offline).";

  return (
    <main className="page-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="topbar-left">
            <div>
              <p className="brand">Job-Ops</p>
              <h1>Dashboard</h1>
            </div>
            <Navigation />
          </div>
          <button className="filter-button">
            <SlidersHorizontal size={14} />
            Filters
          </button>
        </div>
      </header>

      <section className="dashboard-layout">
        {profile ? (
          <aside className="profile-panel">
            <h2>Profile Snapshot</h2>
            <div className="profile-info-header" style={{ marginBottom: '16px', paddingBottom: '12px', borderBottom: '1px solid #f1f5f9' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0f172a' }}>{profile.full_name}</h3>
              {profile.email && <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '2px' }}>{profile.email}</p>}
            </div>
            <div className="profile-stack">
              <div>
                <p className="eyebrow">Target roles</p>
                <p>{profile.suggested_roles && profile.suggested_roles.length > 0 ? profile.suggested_roles.join(", ") : "Not Specified"}</p>
              </div>
              <div>
                <p className="eyebrow">Skills</p>
                <p>{profile.skills && profile.skills.length > 0 ? profile.skills.map((s: any) => s.name).join(", ") : "Not Specified"}</p>
              </div>
              <div>
                <p className="eyebrow">Location</p>
                <p>
                  {[profile.location?.city, profile.location?.country].filter(Boolean).join(", ") || "Not Specified"}
                </p>
              </div>
            </div>
            <div className="profile-tip" style={{ borderColor: '#ccfbf1', background: '#f0fdfa', marginTop: '16px' }}>
              ✓ Matched to your profile. <Link href="/onboarding/resume">Update resume</Link>
            </div>
            <div style={{ marginTop: '12px' }}>
              <Link 
                href="/preferences" 
                className="filter-button" 
                style={{ 
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '100%', 
                  background: '#ffffff', 
                  color: '#0f766e', 
                  borderColor: '#0f766e', 
                  fontWeight: 600,
                  fontSize: '0.85rem',
                  gap: '6px'
                }}
              >
                <SlidersHorizontal size={14} />
                Refine Matches
              </Link>
            </div>
          </aside>
        ) : status === "offline" ? (
          <aside className="profile-panel">
            <h2>Profile Snapshot</h2>
            <div className="profile-stack">
              <div>
                <p className="eyebrow">Target roles</p>
                <p>Python Developer, AI Intern, Data Analyst</p>
              </div>
              <div>
                <p className="eyebrow">Skills</p>
                <p>Python, MySQL, RAG, APIs</p>
              </div>
              <div>
                <p className="eyebrow">Preference</p>
                <p>Remote / Bangalore</p>
              </div>
            </div>
            <div className="profile-tip" style={{ borderColor: '#fee2e2', background: '#fef2f2', marginTop: '16px', color: '#991b1b' }}>
              Preview mode (backend offline). <Link href="/onboarding/resume">Try Onboarding</Link>
            </div>
            <div style={{ marginTop: '12px' }}>
              <Link 
                href="/preferences" 
                className="filter-button" 
                style={{ 
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '100%', 
                  background: '#ffffff', 
                  color: '#0f766e', 
                  borderColor: '#0f766e', 
                  fontWeight: 600,
                  fontSize: '0.85rem',
                  gap: '6px'
                }}
              >
                <SlidersHorizontal size={14} />
                Refine Matches
              </Link>
            </div>
          </aside>
        ) : (
          <aside className="profile-panel">
            <h2>Profile Snapshot</h2>
            <div style={{ textAlign: 'center', padding: '24px 16px', background: '#f8fafc', borderRadius: '12px', border: '1px dashed #cbd5e1', marginTop: '16px' }}>
              <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🚀</div>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#1e293b', marginBottom: '8px' }}>Personalize Your Feed</h3>
              <p style={{ fontSize: '0.85rem', color: '#64748b', lineHeight: '1.4', marginBottom: '16px' }}>
                Upload your resume to get highly relevant, AI-personalized matches tailored to your top skills.
              </p>
              <Link 
                href="/onboarding/resume" 
                style={{ 
                  display: 'block', 
                  width: '100%', 
                  textDecoration: 'none', 
                  padding: '10px', 
                  borderRadius: '8px', 
                  fontSize: '0.9rem', 
                  fontWeight: 500, 
                  background: '#2563eb', 
                  color: '#ffffff', 
                  textAlign: 'center' 
                }}
              >
                Upload Resume
              </Link>
            </div>
            <div className="profile-tip" style={{ marginTop: '16px' }}>
              <Link href="/onboarding/resume">Get started</Link> in under 60 seconds!
            </div>
          </aside>
        )}

        <section>
          <div className="section-heading">
            <div>
              <h2>Recommended Jobs</h2>
              <p>{statusMessage}</p>
            </div>
            <strong>{recommendations.length} matches</strong>
          </div>

          <div className="job-list">
            {recommendations.map((rec: any) => (
              <JobCard 
                key={rec.job.external_id} 
                job={rec.job} 
                score_label={rec.score_label}
                final_score={rec.final_score}
                initialSaved={savedIds.includes(rec.job.external_id)}
                initialApplied={appliedIds.includes(rec.job.external_id)}
              />
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}
