import { ArrowLeft, CheckCircle2 } from "lucide-react";
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
          <div style={{ display: 'flex', alignItems: 'center', gap: '40px' }}>
            <div>
              <p className="brand">Job-Ops</p>
              <h1>Applications</h1>
            </div>
            <Navigation />
          </div>
          <Link href="/" className="filter-button">
            <ArrowLeft size={16} />
            Back to Dashboard
          </Link>
        </div>
      </header>

      <section className="dashboard-layout" style={{ gridTemplateColumns: '1fr' }}>
        <section style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
          <div className="section-heading">
            <div>
              <h2>Tracked Applications</h2>
              <p>Monitor the status of your job hunt.</p>
            </div>
            <strong>{apps.length} applications</strong>
          </div>

          {apps.length === 0 ? (
            <div className="empty-state">
              <h3>No applications recorded</h3>
              <p>Apply to jobs from your recommendations or saved list and mark them as applied.</p>
              <Link href="/" className="button-primary" style={{ display: 'inline-flex', alignItems: 'center', height: '40px', textDecoration: 'none' }}>
                View Recommendations
              </Link>
            </div>
          ) : (
            <div className="job-list">
              {apps.map((app: any) => (
                <div key={app.job_external_id} style={{ position: 'relative' }}>
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
                  <div style={{ padding: '0 16px 16px', background: '#ffffff', border: '1px solid #e2e8f0', borderTop: 'none', borderRadius: '0 0 8px 8px', marginTop: '-8px', fontSize: '13px', color: '#64748b', display: 'flex', justifyContent: 'space-between' }}>
                    <span>Applied on: {new Date(app.applied_at).toLocaleDateString()}</span>
                    {app.notes && <span style={{ fontStyle: 'italic' }}>Note: {app.notes}</span>}
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
