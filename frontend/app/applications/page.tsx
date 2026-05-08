import { ClipboardList } from "lucide-react";
import Link from "next/link";
import Navigation from "../components/Navigation";
import JobCard from "../components/JobCard";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

async function getApplications() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/applications`, {
      next: { revalidate: 0 },
    });
    if (res.ok) {
      const data = await res.json();
      return data.items || [];
    }
    return [];
  } catch (e) {
    return [];
  }
}

async function getSavedIds() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/saved-jobs`, {
      next: { revalidate: 0 },
    });
    if (res.ok) {
      const data = await res.json();
      return (data.items || []).map((j: any) => j.job_external_id);
    }
    return [];
  } catch (e) {
    return [];
  }
}

export const dynamic = 'force-dynamic';

export default async function ApplicationsPage() {
  const [apps, savedIds] = await Promise.all([getApplications(), getSavedIds()]);

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

      <section className="dashboard-layout" style={{ gridTemplateColumns: '1fr' }}>
        <section style={{ maxWidth: '780px', margin: '0 auto', width: '100%' }}>
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
              {apps.map((app: any) => (
                <div key={app.job_external_id}>
                  <JobCard
                    job={{
                      external_id: app.job_external_id,
                      title: app.job_title,
                      company_name: app.company_name,
                      location: app.location || "Unknown",
                      source_name: app.source_name,
                      apply_url: app.apply_url,
                      skills: app.skills || []
                    }}
                    score_label={app.status.toUpperCase()}
                    final_score={100}
                    initialSaved={savedIds.includes(app.job_external_id)}
                    initialApplied={true}
                  />
                  <div className="app-footer">
                    <span>Applied on {new Date(app.applied_at).toLocaleDateString()}</span>
                    {app.notes && <span className="note">Note: {app.notes}</span>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
