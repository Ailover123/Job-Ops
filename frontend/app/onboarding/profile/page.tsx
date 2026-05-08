"use client";

import { useState, useEffect } from "react";
import { 
  User, Mail, Phone, MapPin, 
  BookOpen, Briefcase, Award, 
  Save, AlertCircle, Loader2,
  CheckCircle2, Plus, Trash2, X
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

        if (!response.ok) throw new Error("Failed to extract profile structured data.");
        
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
    setSaving(true);
    // Simulate API call for now since we don't have DB storage implemented yet
    await new Promise(resolve => setTimeout(resolve, 1000));
    setSaving(false);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  if (loading || extracting) {
    return (
      <main className="page-shell" style={{ display: 'grid', placeItems: 'center', background: '#f8fafc' }}>
        <div style={{ textAlign: 'center' }}>
          <Loader2 size={48} className="animate-spin" style={{ color: '#0f766e', marginBottom: '16px' }} />
          <h2 style={{ fontSize: '20px', fontWeight: 600 }}>Analyzing your profile...</h2>
          <p style={{ color: '#64748b' }}>Our AI is structuring your experience.</p>
        </div>
      </main>
    );
  }

  if (error || !profile) {
    return (
      <main className="page-shell" style={{ display: 'grid', placeItems: 'center', background: '#f8fafc' }}>
        <div className="card" style={{ maxWidth: '400px', textAlign: 'center' }}>
          <AlertCircle size={48} color="#ef4444" style={{ marginBottom: '16px' }} />
          <h2>Something went wrong</h2>
          <p style={{ color: '#64748b', marginBottom: '24px' }}>{error || "Could not load profile data."}</p>
          <Link href="/onboarding/resume" className="button-primary">Try Uploading Again</Link>
        </div>
      </main>
    );
  }

  return (
    <main className="page-shell" style={{ background: '#f8fafc', padding: '40px 20px' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
          <div>
            <p className="brand">Step 2 of 3</p>
            <h1 style={{ fontSize: '28px' }}>Review your profile</h1>
            <p style={{ color: '#64748b' }}>Verify and edit the details extracted from your resume.</p>
          </div>
          <button 
            className="button-primary" 
            onClick={handleSave}
            disabled={saving}
            style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            {saving ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} />}
            {saving ? "Saving..." : "Save Profile"}
          </button>
        </div>

        {saveSuccess && (
          <div style={{ 
            background: '#ecfdf5', 
            border: '1px solid #10b981', 
            color: '#065f46', 
            padding: '12px 16px', 
            borderRadius: '8px',
            marginBottom: '24px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <CheckCircle2 size={18} />
            Profile updated successfully! Continue to the next step.
          </div>
        )}

        <div style={{ display: 'grid', gap: '24px' }}>
          {/* Personal Info */}
          <section className="card" style={{ textAlign: 'left' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px', borderBottom: '1px solid #f1f5f9', paddingBottom: '12px' }}>
              <User size={20} color="#0f766e" /> Personal Details
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
              <div className="input-group">
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#64748b', marginBottom: '4px' }}>Full Name</label>
                <input 
                  type="text" 
                  value={profile.full_name} 
                  onChange={(e) => setProfile({...profile, full_name: e.target.value})}
                  className="input-field" 
                />
              </div>
              <div className="input-group">
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#64748b', marginBottom: '4px' }}>Email</label>
                <div style={{ position: 'relative' }}>
                  <Mail size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
                  <input 
                    type="email" 
                    value={profile.email} 
                    onChange={(e) => setProfile({...profile, email: e.target.value})}
                    className="input-field" 
                    style={{ paddingLeft: '40px' }}
                  />
                </div>
              </div>
              <div className="input-group">
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#64748b', marginBottom: '4px' }}>Phone</label>
                <div style={{ position: 'relative' }}>
                  <Phone size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
                  <input 
                    type="text" 
                    value={profile.phone} 
                    onChange={(e) => setProfile({...profile, phone: e.target.value})}
                    className="input-field" 
                    style={{ paddingLeft: '40px' }}
                  />
                </div>
              </div>
              <div className="input-group">
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#64748b', marginBottom: '4px' }}>Location</label>
                <div style={{ position: 'relative' }}>
                  <MapPin size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
                  <input 
                    type="text" 
                    value={`${profile.location.city}, ${profile.location.country}`} 
                    className="input-field" 
                    style={{ paddingLeft: '40px' }}
                    readOnly
                  />
                </div>
              </div>
            </div>
          </section>

          {/* Education */}
          <section className="card" style={{ textAlign: 'left' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px', borderBottom: '1px solid #f1f5f9', paddingBottom: '12px' }}>
              <BookOpen size={20} color="#0f766e" /> Education
            </h3>
            {profile.education.map((edu, idx) => (
              <div key={idx} style={{ padding: '16px', background: '#f8fafc', borderRadius: '8px', marginBottom: '12px', position: 'relative' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div>
                    <p style={{ fontWeight: 600, fontSize: '14px' }}>{edu.degree || "Degree"}</p>
                    <p style={{ color: '#64748b', fontSize: '13px' }}>{edu.institution || "Institution"}</p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <p style={{ fontWeight: 600, fontSize: '14px' }}>{edu.year || "Year"}</p>
                    <p style={{ color: '#0f766e', fontSize: '13px', fontWeight: 500 }}>{edu.score || "N/A"}</p>
                  </div>
                </div>
              </div>
            ))}
            <button className="button-secondary" style={{ width: '100%', fontSize: '13px' }}>
              <Plus size={14} /> Add Education
            </button>
          </section>

          {/* Skills */}
          <section className="card" style={{ textAlign: 'left' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px', borderBottom: '1px solid #f1f5f9', paddingBottom: '12px' }}>
              <Award size={20} color="#0f766e" /> Skills & Expertise
            </h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {profile.skills.map((skill, idx) => (
                <div key={idx} style={{ 
                  background: skill.type === "technical" ? "#f0f9ff" : "#f0fdf4", 
                  color: skill.type === "technical" ? "#0369a1" : "#166534",
                  border: `1px solid ${skill.type === "technical" ? "#bae6fd" : "#bbf7d0"}`,
                  padding: '6px 12px',
                  borderRadius: '20px',
                  fontSize: '13px',
                  fontWeight: 500,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  {skill.name}
                  <X size={14} style={{ cursor: 'pointer', opacity: 0.5 }} />
                </div>
              ))}
            </div>
          </section>

          {/* Suggested Roles */}
          <section className="card" style={{ textAlign: 'left' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px', borderBottom: '1px solid #f1f5f9', paddingBottom: '12px' }}>
              <Briefcase size={20} color="#0f766e" /> Career Focus
            </h3>
            <p style={{ fontSize: '12px', fontWeight: 600, color: '#64748b', marginBottom: '8px' }}>SUGGESTED ROLES</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
              {profile.suggested_roles.map((role, idx) => (
                <span key={idx} style={{ background: '#f1f5f9', padding: '4px 10px', borderRadius: '4px', fontSize: '13px' }}>{role}</span>
              ))}
            </div>
          </section>
        </div>

        <div style={{ marginTop: '40px', textAlign: 'center' }}>
          <Link href="/dashboard" className="button-primary" style={{ padding: '12px 40px', textDecoration: 'none', display: 'inline-block' }}>
            Go to Dashboard
          </Link>
        </div>
      </div>
    </main>
  );
}
