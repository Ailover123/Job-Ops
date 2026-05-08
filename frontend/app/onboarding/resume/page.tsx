"use client";

import { useState, useRef } from "react";
import { FileText, Upload, X, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import Link from "next/link";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export default function ResumeUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type !== "application/pdf") {
        setErrorMessage("Only PDF files are allowed.");
        setStatus("error");
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setStatus("idle");
      setErrorMessage("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setStatus("uploading");
    setErrorMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/onboarding/resume`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Upload failed");
      }

      const data = await response.json();
      console.log("Upload success:", data);
      setStatus("success");
    } catch (err: any) {
      console.error("Upload error:", err);
      setErrorMessage(err.message || "Could not connect to backend.");
      setStatus("error");
    }
  };

  const clearFile = () => {
    setFile(null);
    setStatus("idle");
    setErrorMessage("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <main className="page-shell" style={{ display: 'grid', placeItems: 'center', background: '#f1f5f9' }}>
      <div className="card" style={{ maxWidth: '480px', width: '90%', textAlign: 'center' }}>
        <p className="brand">Step 1 of 3</p>
        <h1 style={{ marginBottom: '12px' }}>Upload your resume</h1>
        <p style={{ color: '#64748b', marginBottom: '32px' }}>
          We'll extract your skills and experience to find the best fresher roles.
        </p>

        {!file ? (
          <div 
            className="upload-zone"
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={48} color="#94a3b8" style={{ marginBottom: '16px' }} />
            <p style={{ fontWeight: 600, marginBottom: '4px' }}>Click to upload or drag and drop</p>
            <p style={{ color: '#64748b', fontSize: '14px' }}>PDF only (max 5MB)</p>
            <input 
              type="file" 
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf,application/pdf"
              style={{ display: 'none' }}
            />
          </div>
        ) : (
          <div className="file-info">
            <FileText size={32} color="#0f766e" />
            <div style={{ flex: 1, textAlign: 'left' }}>
              <p style={{ fontWeight: 600, fontSize: '14px', marginBottom: '2px', wordBreak: 'break-all' }}>{file.name}</p>
              <p style={{ color: '#64748b', fontSize: '12px' }}>{formatSize(file.size)}</p>
            </div>
            {status !== "uploading" && status !== "success" && (
              <button onClick={clearFile} style={{ border: 'none', background: 'none', color: '#94a3b8' }}>
                <X size={20} />
              </button>
            )}
          </div>
        )}

        {status === "uploading" && (
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: '60%' }}></div>
          </div>
        )}

        {status === "error" && (
          <div className="error-text" style={{ display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'center' }}>
            <AlertCircle size={16} />
            {errorMessage}
          </div>
        )}

        {status === "success" && (
          <div className="success-text" style={{ display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'center' }}>
            <CheckCircle size={16} />
            Resume uploaded successfully!
          </div>
        )}

        <div style={{ marginTop: '32px', display: 'flex', gap: '12px', flexDirection: 'column' }}>
          {status === "success" ? (
            <Link href="/onboarding/profile" className="button-primary" style={{ display: 'grid', placeItems: 'center', textDecoration: 'none' }}>
              Continue to Profile
            </Link>
          ) : (
            <button 
              className="button-primary" 
              onClick={handleUpload}
              disabled={!file || status === "uploading"}
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
            >
              {status === "uploading" && <Loader2 size={18} className="animate-spin" />}
              {status === "uploading" ? "Uploading..." : "Upload & Analyze"}
            </button>
          )}
          
          <Link href="/" style={{ color: '#64748b', fontSize: '14px', textDecoration: 'none' }}>
            Skip for now
          </Link>
        </div>
      </div>
    </main>
  );
}
