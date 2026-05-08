import { Bookmark, BriefcaseBusiness, CheckCircle2, MapPin, SlidersHorizontal } from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

const MOCK_RECOMMENDATIONS = [
  {
    job: {
      external_id: "seed-1",
      title: "Python Developer Intern",
      company_name: "NovaSkill Labs",
      location: "Bangalore",
      source_name: "Direct",
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
      skills: ["Python", "RAG", "LLMs"]
    },
    score_label: "Good Match",
    final_score: 85
  }
];

async function getRecommendations() {
  try {
    // 1. Try to get personalized recommendations from latest profile
    const personalizedRes = await fetch(`${API_BASE_URL}/api/v1/recommendations/latest-profile`, {
      next: { revalidate: 0 },
    });

    if (personalizedRes.ok) {
      const data = await personalizedRes.json();
      if (data.status === "personalized") {
        return {
          items: data.items,
          status: "personalized",
        };
      }
    }

    // 2. If no profile exists or that fails, try the demo POST endpoint
    const demoRes = await fetch(`${API_BASE_URL}/api/v1/recommendations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
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
      return {
        items: items,
        status: "demo",
      };
    }

    // 3. Absolute fallback to mock data
    return {
      items: MOCK_RECOMMENDATIONS,
      status: "offline",
    };
  } catch (e) {
    console.error("Failed to fetch jobs from backend, using mock data:", e);
    return {
      items: MOCK_RECOMMENDATIONS,
      status: "offline",
    };
  }
}

export const dynamic = 'force-dynamic';

export default async function Home() {
  const { items: recommendations, status } = await getRecommendations();
  
  const statusMessage = status === "personalized" 
    ? "Recommendations based on your saved profile."
    : status === "demo"
      ? "Showing preview data from live backend."
      : "Showing preview data (Backend offline).";

  return (
    <main className="page-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <div>
            <p className="brand">Job-Ops</p>
            <h1>AI Fresher Job Matcher</h1>
          </div>
          <button className="filter-button">
            <SlidersHorizontal size={16} />
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
              <p>Remote or Bangalore, internship/full-time</p>
            </div>
          </div>
          {status !== "personalized" && (
            <div style={{ marginTop: '20px', padding: '12px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', fontSize: '12px', border: '1px solid rgba(255,255,255,0.1)' }}>
              <p style={{ opacity: 0.7 }}>Tip: Complete onboarding to see personalized matches.</p>
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
              <article key={rec.job.external_id} className="job-card">
                <div className="job-main">
                  <div>
                    <div className="title-row">
                      <h3>{rec.job.title}</h3>
                      <span className="match-label">{rec.score_label}</span>
                    </div>
                    <p className="company">{rec.job.company_name}</p>
                    <div className="meta-row">
                      <span>
                        <MapPin size={15} />
                        {rec.job.location}
                      </span>
                      <span>
                        <BriefcaseBusiness size={15} />
                        {rec.job.source_name}
                      </span>
                    </div>
                    <div className="tag-row">
                      {rec.job.skills.map((tag: string) => (
                        <span key={tag}>{tag}</span>
                      ))}
                    </div>
                  </div>

                  <div className="action-column">
                    <div className="score-badge">{rec.final_score}</div>
                    <div className="icon-actions">
                      <button aria-label="Save job">
                        <Bookmark size={16} />
                      </button>
                      <button aria-label="Mark applied">
                        <CheckCircle2 size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}
