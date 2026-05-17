"use client";

import { useState, useRef } from "react";
import { FileText, Upload, X, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import Link from "next/link";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export default function ResumeUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [textPreview, setTextPreview] = useState("");
  const [textLength, setTextLength] = useState(0);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) processFile(selectedFile);
  };

  const processFile = (selectedFile: File) => {
    if (selectedFile.type !== "application/pdf") {
      setErrorMessage("Only PDF files are allowed.");
      setStatus("error");
      setFile(null);
      return;
    }
    setFile(selectedFile);
    setStatus("idle");
    setErrorMessage("");
    setTextPreview("");
    setTextLength(0);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) processFile(droppedFile);
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
      localStorage.setItem("extracted_resume_text", data.extracted_text);
      setTextPreview(data.text_preview);
      setTextLength(data.text_length);
      setStatus("success");
    } catch (err: any) {
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
    <main className="centered-page">
      <div className="card" style={{ maxWidth: '440px', width: '100%', textAlign: 'center' }}>
        <p className="brand">Step 1 of 3</p>
        <h1 style={{ marginBottom: '8px' }}>Upload your resume</h1>
        <p style={{ color: '#64748b', marginBottom: '28px', fontSize: '13px' }}>
          We'll extract your skills and experience to find the best fresher roles.
        </p>

        {!file ? (
          <div
            className={`upload-zone ${dragOver ? "dragover" : ""}`}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') fileInputRef.current?.click(); }}
          >
            <Upload size={36} color="#94a3b8" style={{ marginBottom: '12px' }} />
            <p style={{ fontWeight: 600, marginBottom: '2px', fontSize: '14px' }}>Click or drag to upload</p>
            <p style={{ color: '#94a3b8', fontSize: '12px' }}>PDF only · max 5 MB</p>
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
            <FileText size={28} color="#0f766e" />
            <div style={{ flex: 1, textAlign: 'left', minWidth: 0 }}>
              <p style={{ fontWeight: 600, fontSize: '13px', marginBottom: '1px', wordBreak: 'break-all' }}>{file.name}</p>
              <p style={{ color: '#94a3b8', fontSize: '11px', margin: 0 }}>{formatSize(file.size)}</p>
            </div>
            {status !== "uploading" && status !== "success" && (
              <button onClick={clearFile} style={{ border: 'none', background: 'none', color: '#94a3b8', cursor: 'pointer' }} title="Remove file">
                <X size={18} />
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
          <div className="error-text">
            <AlertCircle size={14} />
            {errorMessage}
          </div>
        )}

        {status === "success" && (
          <div className="success-text">
            <CheckCircle size={14} />
            Resume uploaded successfully!
          </div>
        )}

        {status === "success" && textPreview && (
          <div style={{ marginTop: '20px', textAlign: 'left' }}>
            <p className="input-label">
              Extracted Content ({textLength} chars)
            </p>
            <div className="preview-box">
              {textPreview}
              {textLength > textPreview.length && "..."}
            </div>
          </div>
        )}

        <div style={{ marginTop: '24px', display: 'flex', gap: '10px', flexDirection: 'column' }}>
          {status === "success" ? (
            <Link href="/onboarding/profile" className="button-primary">
              Continue to Profile
            </Link>
          ) : (
            <button
              className="button-primary"
              onClick={handleUpload}
              disabled={!file || status === "uploading"}
            >
              {status === "uploading" && <Loader2 size={16} className="animate-spin" />}
              {status === "uploading" ? "Uploading..." : "Upload & Analyze"}
            </button>
          )}

          <Link href="/" className="skip-onboarding-link">
            Skip for now
          </Link>
        </div>
      </div>
    </main>
  );
}
