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
  const [{ items: recommendations, status }, { savedIds, appliedIds }] = await Promise.all([
    getRecommendations(),
    getUserJobStats()
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
          {status !== "personalized" && (
            <div className="profile-tip">
              <Link href="/onboarding/resume">Upload your resume</Link> to get personalized matches.
            </div>
          )}
          {status === "personalized" && (
            <div className="profile-tip" style={{ borderColor: '#ccfbf1', background: '#f0fdfa' }}>
              ✓ Matched to your profile. <Link href="/onboarding/resume">Update resume</Link>
            </div>
          )}
        </aside>

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
