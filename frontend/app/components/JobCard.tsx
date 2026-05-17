"use client";

import { useState } from "react";
import { Bookmark, BriefcaseBusiness, CheckCircle2, MapPin, ExternalLink } from "lucide-react";
import Link from "next/link";

import { API_BASE_URL } from "../lib/api";

interface Job {
  external_id: string;
  title: string;
  company_name: string;
  location: string;
  source_name: string;
  apply_url: string;
  skills: string[];
}

interface JobCardProps {
  job: Job;
  score_label: string;
  final_score: number;
  initialSaved?: boolean;
  initialApplied?: boolean;
  onActionError?: (msg: string) => void;
}

export default function JobCard({
  job,
  score_label,
  final_score,
  initialSaved = false,
  initialApplied = false,
  onActionError,
}: JobCardProps) {
  const [isSaved, setIsSaved] = useState(initialSaved);
  const [isApplied, setIsApplied] = useState(initialApplied);
  const [loading, setLoading] = useState(false);

  const toggleSave = async () => {
    if (loading) return;
    setLoading(true);
    try {
      if (isSaved) {
        const res = await fetch(`${API_BASE_URL}/api/v1/saved-jobs/${job.external_id}`, {
          method: "DELETE",
        });
        if (res.ok) setIsSaved(false);
        else throw new Error("Failed to unsave");
      } else {
        const res = await fetch(`${API_BASE_URL}/api/v1/saved-jobs`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            job_external_id: job.external_id,
            job_title: job.title,
            company_name: job.company_name,
            location: job.location,
            source_name: job.source_name,
            apply_url: job.apply_url,
            skills: job.skills,
          }),
        });
        if (res.ok) setIsSaved(true);
        else throw new Error("Failed to save");
      }
    } catch (err) {
      onActionError?.(err instanceof Error ? err.message : "Action failed");
    } finally {
      setLoading(false);
    }
  };

  const markApplied = async () => {
    if (loading || isApplied) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/applications`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_external_id: job.external_id,
          job_title: job.title,
          company_name: job.company_name,
          location: job.location,
          source_name: job.source_name,
          apply_url: job.apply_url,
          skills: job.skills,
        }),
      });
      if (res.ok) setIsApplied(true);
      else throw new Error("Failed to mark as applied");
    } catch (err) {
      onActionError?.(err instanceof Error ? err.message : "Action failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <article className="job-card">
      <div className="job-main">
        <div className="job-content">
          <div className="title-row">
            <h3>
              <Link href={`/jobs/${job.external_id}`} className="job-title-link">
                {job.title}
              </Link>
            </h3>
            <span className={`match-label ${score_label.toLowerCase().replace(/\s+/g, "-")}`}>{score_label}</span>
          </div>
          <p className="company">{job.company_name}</p>
          <div className="meta-row">
            <span>
              <MapPin size={14} />
              {job.location}
            </span>
            <span>
              <BriefcaseBusiness size={14} />
              {job.source_name}
            </span>
          </div>
          <div className="tag-row">
            {job.skills.map((tag: string) => (
              <span key={tag}>{tag}</span>
            ))}
          </div>
          <a
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="apply-link"
          >
            View on {job.source_name} <ExternalLink size={13} />
          </a>
        </div>

        <div className="action-column">
          <div className="score-badge">{final_score}</div>
          <div className="icon-actions">
            <button
              title={isSaved ? "Unsave job" : "Save job"}
              aria-label={isSaved ? "Unsave job" : "Save job"}
              className={isSaved ? "active" : ""}
              onClick={toggleSave}
              disabled={loading}
            >
              <Bookmark size={15} fill={isSaved ? "currentColor" : "none"} />
            </button>
            <button
              title={isApplied ? "Applied" : "Mark as applied"}
              aria-label={isApplied ? "Applied" : "Mark applied"}
              className={isApplied ? "applied" : ""}
              onClick={markApplied}
              disabled={loading || isApplied}
            >
              <CheckCircle2 size={15} fill={isApplied ? "currentColor" : "none"} />
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}
