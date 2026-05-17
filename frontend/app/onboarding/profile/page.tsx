"use client";

import { useState, useEffect } from "react";
import {
  User, Mail, Phone, MapPin,
  BookOpen, Briefcase, Award,
  Save, AlertCircle, Loader2,
  CheckCircle2, Plus, X
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

interface ProfileData {
  full_name: string;
  email: string;
  phone: string;
  location: { city: string; state: string; country: string };
  education: Array<{ degree: string; institution: string; year: string; score: string }>;
  skills: Array<{ name: string; type: string; confidence: number }>;
  projects: Array<{ title: string; description: string; tech_stack: string[]; url: string }>;
  certifications: string[];
  suggested_roles: string[];
  preferred_domains: string[];
}

export default function ProfileReview() {
  const router = useRouter();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [extracting, setExtracting] = useState(false);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    const resumeText = localStorage.getItem("extracted_resume_text");
    if (!resumeText) {
      router.push("/onboarding/resume");
      return;
    }

    const fetchProfile = async () => {
      setExtracting(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/profile/extract`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ resume_text: resumeText }),
        });

        if (!response.ok) {
          let errorMsg = "Failed to extract profile structured data.";
          try {
            const errData = await response.json();
            if (errData && errData.detail) {
              errorMsg = typeof errData.detail === "string" ? errData.detail : JSON.stringify(errData.detail);
            }
          } catch (_) {}
          throw new Error(errorMsg);
        }

        const data = await response.json();
        setProfile(data.profile);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setExtracting(false);
        setLoading(false);
      }
    };

    fetchProfile();
  }, [router]);

  const handleSave = async () => {
    if (!profile) return;
    setSaving(true);
    setSaveSuccess(false);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profile),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to save profile.");
      }

      setSaveSuccess(true);
      setTimeout(() => {
        router.push("/");
      }, 1500);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading || extracting) {
    return (
      <main className="centered-page">
        <div style={{ textAlign: 'center' }}>
          <Loader2 size={40} className="animate-spin" style={{ color: '#0f766e', marginBottom: '12px' }} />
          <h2 style={{ fontSize: '18px', fontWeight: 600 }}>Analyzing your profile...</h2>
          <p style={{ color: '#94a3b8', fontSize: '13px' }}>Our AI is structuring your experience.</p>
        </div>
      </main>
    );
  }

  if (error || !profile) {
    return (
      <main className="centered-page">
        <div className="card" style={{ maxWidth: '380px', textAlign: 'center' }}>
          <AlertCircle size={40} color="#ef4444" style={{ marginBottom: '12px' }} />
          <h2 style={{ fontSize: '16px' }}>Something went wrong</h2>
          <p style={{ color: '#94a3b8', marginBottom: '20px', fontSize: '13px' }}>{error || "Could not load profile data."}</p>
          <Link href="/onboarding/resume" className="button-primary">Try Uploading Again</Link>
        </div>
      </main>
    );
  }

  return (
    <main className="page-shell" style={{ background: '#f8fafc', padding: '28px 16px' }}>
      <div style={{ maxWidth: '760px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <p className="brand">Step 2 of 3</p>
            <h1>Review your profile</h1>
            <p style={{ color: '#94a3b8', fontSize: '13px', margin: 0 }}>Verify and edit the details extracted from your resume.</p>
          </div>
          <button
            className="button-primary"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
            {saving ? "Saving..." : "Save Profile"}
          </button>
        </div>

        {saveSuccess && (
          <div className="success-banner">
            <CheckCircle2 size={16} />
            Profile saved! Redirecting to dashboard...
          </div>
        )}

        <div style={{ display: 'grid', gap: '16px' }}>
          {/* Personal Info */}
          <section className="card" style={{ textAlign: 'left' }}>
            <h3 className="card-header">
              <User size={18} /> Personal Details
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
              <div className="input-group">
                <label className="input-label">Full Name</label>
                <input
                  type="text"
                  value={profile.full_name}
                  onChange={(e) => setProfile({...profile, full_name: e.target.value})}
                  className="input-field"
                />
              </div>
              <div className="input-group">
                <label className="input-label">Email</label>
                <div className="input-icon-wrap">
                  <Mail size={14} />
                  <input
                    type="email"
                    value={profile.email}
                    onChange={(e) => setProfile({...profile, email: e.target.value})}
                    className="input-field"
                  />
                </div>
              </div>
              <div className="input-group">
                <label className="input-label">Phone</label>
                <div className="input-icon-wrap">
                  <Phone size={14} />
                  <input
                    type="text"
                    value={profile.phone}
                    onChange={(e) => setProfile({...profile, phone: e.target.value})}
                    className="input-field"
                  />
                </div>
              </div>
              <div className="input-group">
                <label className="input-label">Location</label>
                <div className="input-icon-wrap">
                  <MapPin size={14} />
                  <input
                    type="text"
                    value={`${profile.location.city}, ${profile.location.country}`}
                    className="input-field"
                    readOnly
                  />
                </div>
              </div>
            </div>
          </section>

          {/* Education */}
          <section className="card" style={{ textAlign: 'left' }}>
            <h3 className="card-header">
              <BookOpen size={18} /> Education
            </h3>
            {profile.education.map((edu, idx) => (
              <div key={idx} className="edu-card">
                <div className="edu-card-grid">
                  <div>
                    <p style={{ fontWeight: 600, fontSize: '13px', marginBottom: '2px' }}>{edu.degree || "Degree"}</p>
                    <p style={{ color: '#64748b', fontSize: '12px', margin: 0 }}>{edu.institution || "Institution"}</p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <p style={{ fontWeight: 600, fontSize: '13px', marginBottom: '2px' }}>{edu.year || "Year"}</p>
                    <p style={{ color: '#0f766e', fontSize: '12px', fontWeight: 500, margin: 0 }}>{edu.score || "N/A"}</p>
                  </div>
                </div>
              </div>
            ))}
            <button className="button-secondary" style={{ width: '100%' }}>
              <Plus size={14} /> Add Education
            </button>
          </section>

          {/* Skills */}
          <section className="card" style={{ textAlign: 'left' }}>
            <h3 className="card-header">
              <Award size={18} /> Skills & Expertise
            </h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {profile.skills.map((skill, idx) => (
                <div key={idx} className={`skill-pill ${skill.type === "technical" ? "technical" : "soft"}`}>
                  {skill.name}
                  <button title={`Remove ${skill.name}`}>
                    <X size={12} />
                  </button>
                </div>
              ))}
            </div>
          </section>

          {/* Suggested Roles */}
          <section className="card" style={{ textAlign: 'left' }}>
            <h3 className="card-header">
              <Briefcase size={18} /> Career Focus
            </h3>
            <p className="input-label">Suggested Roles</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {profile.suggested_roles.map((role, idx) => (
                <span key={idx} className="role-tag">{role}</span>
              ))}
            </div>
          </section>
        </div>

        <div style={{ marginTop: '28px', textAlign: 'center' }}>
          <Link href="/" className="button-primary" style={{ padding: '0 32px' }}>
            Go to Dashboard
          </Link>
        </div>
      </div>
    </main>
  );
}
