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

async function getJobs() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/recommendations`, {
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
      next: { revalidate: 0 }, // Disable cache for dev
    });

    if (!res.ok) {
      console.warn("Backend API returned an error, using mock data.");
      return MOCK_RECOMMENDATIONS;
    }
    return res.json();
  } catch (e) {
    console.error("Failed to fetch jobs from backend, using mock data:", e);
    return MOCK_RECOMMENDATIONS;
  }
}

export default async function Home() {
  const recommendations = await getJobs();
  const isDemoMode = recommendations === MOCK_RECOMMENDATIONS;
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
        </aside>

        <section>
          <div className="section-heading">
            <div>
              <h2>Recommended Jobs</h2>
              <p>
                {isDemoMode 
                  ? "Showing preview data (Backend offline)." 
                  : "Seed data preview from live local backend."}
              </p>
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
