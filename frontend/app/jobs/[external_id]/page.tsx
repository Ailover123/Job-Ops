"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  Bookmark,
  CheckCircle2,
  MapPin,
  BriefcaseBusiness,
  ExternalLink,
  Loader2,
  Award,
  AlertCircle
} from "lucide-react";
import Link from "next/link";
import Navigation from "../../components/Navigation";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

interface Job {
  external_id: string;
  title: string;
  company_name: string;
  location: string;
  source_name: string;
  apply_url: string;
  skills: string[];
  description: string;
}

interface MatchDetails {
  job: Job;
  has_profile: boolean;
  match_score?: number;
  match_label?: string;
  match_explanation?: string;
  skill_score?: number;
  fresher_score?: number;
  location_score?: number;
  experience_score?: number;
}

export default function JobDetailPage() {
  const params = useParams();
  const external_id = params?.external_id as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [data, setData] = useState<MatchDetails | null>(null);

  // Saved / Applied Actions State
  const [isSaved, setIsSaved] = useState(false);
  const [isApplied, setIsApplied] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (!external_id) return;

    const fetchJobDetailsAndStates = async () => {
      try {
        setLoading(true);
        setError("");

        // 1. Fetch job details & matchmaking math
        const detailRes = await fetch(`${API_BASE_URL}/api/v1/jobs/${external_id}`);
        if (!detailRes.ok) {
          if (detailRes.status === 404) {
            throw new Error("Job not found.");
          }
          throw new Error("Failed to fetch job details.");
        }
        const detailData = await detailRes.json();
        setData(detailData);

        // 2. Fetch saved/applied status lists in parallel to sync toggle state
        const [savedRes, appliedRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/v1/saved-jobs`),
          fetch(`${API_BASE_URL}/api/v1/applications`)
        ]);

        if (savedRes.ok) {
          const savedData = await savedRes.json();
          const savedList = savedData.items || [];
          setIsSaved(savedList.some((item: any) => item.job_external_id === external_id));
        }

        if (appliedRes.ok) {
          const appliedData = await appliedRes.json();
          const appliedList = appliedData.items || [];
          setIsApplied(appliedList.some((item: any) => item.job_external_id === external_id));
        }

      } catch (err: any) {
        setError(err.message || "An unexpected error occurred.");
      } finally {
        setLoading(false);
      }
    };

    fetchJobDetailsAndStates();
  }, [external_id]);

  const toggleSave = async () => {
    if (!data?.job || actionLoading) return;
    setActionLoading(true);
    try {
      if (isSaved) {
        const res = await fetch(`${API_BASE_URL}/api/v1/saved-jobs/${external_id}`, {
          method: "DELETE",
        });
        if (res.ok) setIsSaved(false);
        else throw new Error("Failed to unsave job");
      } else {
        const res = await fetch(`${API_BASE_URL}/api/v1/saved-jobs`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            job_external_id: data.job.external_id,
            job_title: data.job.title,
            company_name: data.job.company_name,
            location: data.job.location,
            source_name: data.job.source_name,
            apply_url: data.job.apply_url,
            skills: data.job.skills,
          }),
        });
        if (res.ok) setIsSaved(true);
        else throw new Error("Failed to save job");
      }
    } catch (err: any) {
      alert(err.message || "Action failed");
    } finally {
      setActionLoading(false);
    }
  };

  const markApplied = async () => {
    if (!data?.job || actionLoading || isApplied) return;
    setActionLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/applications`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_external_id: data.job.external_id,
          job_title: data.job.title,
          company_name: data.job.company_name,
          location: data.job.location,
          source_name: data.job.source_name,
          apply_url: data.job.apply_url,
          skills: data.job.skills,
        }),
      });
      if (res.ok) setIsApplied(true);
      else throw new Error("Failed to mark as applied");
    } catch (err: any) {
      alert(err.message || "Action failed");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <main className="centered-page" style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#f8fafc" }}>
        <div style={{ textAlign: "center" }}>
          <Loader2 size={40} className="animate-spin" style={{ color: "#0f766e", marginBottom: "12px" }} />
          <h2 style={{ fontSize: "18px", fontWeight: 600, color: "#1e293b" }}>Loading job details...</h2>
          <p style={{ color: "#94a3b8", fontSize: "13px" }}>Analyzing compatibility score and match details.</p>
        </div>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="page-shell" style={{ background: "#f8fafc", padding: "28px 16px", minHeight: "100vh" }}>
        <div style={{ maxWidth: "800px", margin: "0 auto", textAlign: "center", padding: "60px 0" }}>
          <AlertCircle size={48} style={{ color: "#b91c1c", margin: "0 auto 16px auto" }} />
          <h2 style={{ fontSize: "20px", fontWeight: 700, color: "#0f172a", marginBottom: "8px" }}>Failed to Load Opportunity</h2>
          <p style={{ color: "#64748b", fontSize: "14px", marginBottom: "24px" }}>{error || "We couldn't retrieve the details for this job."}</p>
          <Link href="/" className="detail-button-primary">
            <ArrowLeft size={16} /> Back to Dashboard
          </Link>
        </div>
      </main>
    );
  }

  const {
    job,
    has_profile,
    match_score = 0,
    match_label = "Unrated Match",
    match_explanation = "",
    skill_score = 0,
    fresher_score = 0,
    location_score = 0,
    experience_score = 0
  } = data;

  return (
    <main className="page-shell" style={{ background: "#f8fafc", minHeight: "100vh" }}>
      <header className="topbar">
        <div className="topbar-inner">
          <div className="topbar-left">
            <div>
              <p className="brand">Job-Ops</p>
              <h1>Job Detail</h1>
            </div>
            <Navigation />
          </div>
        </div>
      </header>

      <section style={{ maxWidth: "880px", margin: "32px auto", padding: "0 16px" }}>
        {/* Breadcrumb Navigation */}
        <nav className="breadcrumb-nav">
          <Link href="/">Dashboard</Link>
          <span>/</span>
          <span>Jobs</span>
          <span>/</span>
          <span style={{ color: "#0f172a" }}>{job.external_id}</span>
        </nav>

        {/* Compatibility Score Widget Banner */}
        {has_profile ? (
          <div className="compatibility-banner">
            <div className="compat-score-circle">
              <span className="number">{match_score}</span>
              <span className="percent">Score</span>
            </div>
            <div className="compat-details">
              <h2>
                <Award size={18} style={{ color: "#0f766e" }} />
                <span>{match_label}</span>
              </h2>
              <p>{match_explanation}</p>
              
              {/* Score breakdown metrics grid */}
              <div className="compat-breakdown-grid">
                <div className="compat-breakdown-card">
                  <strong>{Math.round(skill_score * 100)}%</strong>
                  <span>Skill Match</span>
                </div>
                <div className="compat-breakdown-card">
                  <strong>{Math.round(location_score * 100)}%</strong>
                  <span>Location Match</span>
                </div>
                <div className="compat-breakdown-card">
                  <strong>{Math.round(fresher_score * 100)}%</strong>
                  <span>Fresher Fit</span>
                </div>
                <div className="compat-breakdown-card">
                  <strong>{Math.round(experience_score * 100)}%</strong>
                  <span>Exp Fit</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="compat-onboarding-banner">
            <h3>Personalize Compatibility Score</h3>
            <p>
              Upload your resume or set refined match preferences to immediately calculate your personalized fit percentage and match explanation for this job.
            </p>
            <div style={{ display: "flex", justifyContent: "center", gap: "12px", flexWrap: "wrap" }}>
              <Link href="/onboarding/resume" className="detail-button-primary" style={{ padding: "8px 16px", fontSize: "13px" }}>
                Upload Resume
              </Link>
              <Link href="/preferences" className="detail-button-secondary" style={{ padding: "8px 16px", fontSize: "13px" }}>
                Refine Preferences
              </Link>
            </div>
          </div>
        )}

        {/* Job Detail Card Container */}
        <div className="job-detail-container">
          <header className="job-detail-header">
            <h1 id="job-title-heading">{job.title}</h1>
            <p className="company">{job.company_name}</p>
            
            <div className="meta-row" style={{ marginTop: "16px", fontSize: "14px" }}>
              <span style={{ display: "inline-flex", alignItems: "center", gap: "6px", color: "#475569" }}>
                <MapPin size={16} />
                {job.location}
              </span>
              <span style={{ display: "inline-flex", alignItems: "center", gap: "6px", color: "#475569" }}>
                <BriefcaseBusiness size={16} />
                Source: {job.source_name}
              </span>
            </div>

            <div className="detail-tags">
              {job.skills.map((skill: string) => (
                <span key={skill}>{skill}</span>
              ))}
            </div>
          </header>

          <div className="job-detail-body">
            <div className="job-detail-section">
              <h2>Job Description</h2>
              <p style={{ whiteSpace: "pre-line", color: "#334155", fontSize: "15px", lineHeight: "1.7" }}>
                {job.description || "No description provided by source."}
              </p>
            </div>

            {/* Action buttons footer tray */}
            <div className="detail-actions-panel">
              <a
                href={job.apply_url}
                target="_blank"
                rel="noopener noreferrer"
                className="detail-button-primary"
              >
                Apply Now <ExternalLink size={16} />
              </a>

              <button
                onClick={toggleSave}
                disabled={actionLoading}
                className={`detail-button-secondary ${isSaved ? "active" : ""}`}
                title={isSaved ? "Saved Job" : "Save Job"}
              >
                <Bookmark size={16} fill={isSaved ? "currentColor" : "none"} />
                {isSaved ? "Saved" : "Save for Later"}
              </button>

              <button
                onClick={markApplied}
                disabled={actionLoading || isApplied}
                className={`detail-button-secondary ${isApplied ? "active" : ""}`}
                style={{ cursor: isApplied ? "default" : "pointer" }}
                title={isApplied ? "Applied" : "Mark as Applied"}
              >
                <CheckCircle2 size={16} fill={isApplied ? "currentColor" : "none"} />
                {isApplied ? "Applied Successfully" : "Mark as Applied"}
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
