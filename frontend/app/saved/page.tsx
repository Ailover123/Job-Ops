import { SlidersHorizontal, ArrowLeft } from "lucide-react";
import Link from "next/link";
import Navigation from "../components/Navigation";
import JobCard from "../components/JobCard";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

async function getSavedJobs() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/saved-jobs`, {
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

async function getAppliedIds() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/applications`, {
      next: { revalidate: 0 },
    });
    if (res.ok) {
      const data = await res.json();
      return (data.items || []).map((a: any) => a.job_external_id);
    }
    return [];
  } catch (e) {
    return [];
  }
}

export const dynamic = 'force-dynamic';

export default async function SavedPage() {
  const [jobs, appliedIds] = await Promise.all([getSavedJobs(), getAppliedIds()]);

  return (
    <main className="page-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <div style={{ display: 'flex', alignItems: 'center', gap: '40px' }}>
            <div>
              <p className="brand">Job-Ops</p>
              <h1>Saved Jobs</h1>
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
              <h2>Your Bookmarks</h2>
              <p>Keep track of jobs you're interested in.</p>
            </div>
            <strong>{jobs.length} jobs saved</strong>
          </div>

          {jobs.length === 0 ? (
            <div className="empty-state">
              <h3>No saved jobs yet</h3>
              <p>Start browsing recommendations and bookmark jobs you like.</p>
              <Link href="/" className="button-primary" style={{ display: 'inline-flex', alignItems: 'center', height: '40px', textDecoration: 'none' }}>
                Browse Jobs
              </Link>
            </div>
          ) : (
            <div className="job-list">
              {jobs.map((job: any) => (
                <JobCard 
                  key={job.job_external_id} 
                  job={{
                    external_id: job.job_external_id,
                    title: job.job_title,
                    company_name: job.company_name,
                    location: job.location,
                    source_name: job.source_name,
                    apply_url: job.apply_url,
                    skills: job.skills || []
                  }} 
                  score_label="Saved"
                  final_score={100}
                  initialSaved={true}
                  initialApplied={appliedIds.includes(job.job_external_id)}
                />
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
