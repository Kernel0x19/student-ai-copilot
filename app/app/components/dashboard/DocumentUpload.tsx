"use client";

import { useState, useRef, useCallback } from "react";
import {
  FileText,
  Upload,
  CheckCircle2,
  AlertTriangle,
  Clock,
  XCircle,
  Loader2,
  RefreshCw,
  Shield,
} from "lucide-react";
import type { DocumentStatus } from "@/app/lib/api";
import { uploadDocument } from "@/app/lib/api";

const DOC_TYPES = [
  { value: "aadhaar", label: "Aadhaar Card" },
  { value: "income_certificate", label: "Income Certificate" },
  { value: "caste_certificate", label: "Caste Certificate" },
  { value: "marksheet", label: "Marksheet / Transcript" },
  { value: "bonafide", label: "Bonafide Certificate" },
];

const STATUS_CONFIG: Record<
  string,
  { icon: React.ReactNode; color: string; label: string }
> = {
  auto_approved: {
    icon: <CheckCircle2 size={16} />,
    color: "text-green-500",
    label: "Auto-Approved",
  },
  verified: {
    icon: <CheckCircle2 size={16} />,
    color: "text-green-500",
    label: "Verified",
  },
  needs_review: {
    icon: <AlertTriangle size={16} />,
    color: "text-amber-500",
    label: "Needs Review",
  },
  processing: {
    icon: <Loader2 size={16} className="animate-spin" />,
    color: "text-[#0C65D2]",
    label: "Processing",
  },
  pending: {
    icon: <Clock size={16} />,
    color: "text-gray-400",
    label: "Pending",
  },
  rejected: {
    icon: <XCircle size={16} />,
    color: "text-red-500",
    label: "Rejected",
  },
};

interface Props {
  userId: string;
}

export default function DocumentUpload({ userId }: Props) {
  const [docType, setDocType] = useState(DOC_TYPES[0].value);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState<DocumentStatus[]>([]);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = useCallback(async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const result = await uploadDocument(userId, docType, file);
      setUploaded((prev) => [result, ...prev]);
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }, [file, docType, userId]);

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      {/* Header */}
      <div>
        <h1 className="font-syne text-xl font-bold flex items-center gap-2">
          <Shield size={20} className="text-[#0C65D2]" />
          Document Vault
        </h1>
        <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] mt-1">
          Upload and verify documents — AES-256 encrypted, TEE-secured
          processing
        </p>
      </div>

      {/* Upload Form */}
      <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-6 flex flex-col gap-4">
        <p className="font-mono text-[13px] font-bold text-gray-900 dark:text-[#F0F4FF]">
          Upload Document
        </p>

        {/* Document Type Selector */}
        <div className="flex flex-col gap-1.5">
          <label
            htmlFor="doc-type-select"
            className="font-mono text-[11px] text-gray-500"
          >
            Document Type
          </label>
          <select
            id="doc-type-select"
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="px-3 py-2 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] font-mono text-[13px] outline-none focus:border-[#0C65D2]/40"
          >
            {DOC_TYPES.map((dt) => (
              <option key={dt.value} value={dt.value}>
                {dt.label}
              </option>
            ))}
          </select>
        </div>

        {/* File Picker */}
        <div className="flex flex-col gap-1.5">
          <label
            htmlFor="doc-file-input"
            className="font-mono text-[11px] text-gray-500"
          >
            File (PDF, PNG, JPG)
          </label>
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-black/10 dark:border-white/8 p-8 flex flex-col items-center justify-center gap-2 cursor-pointer hover:border-[#0C65D2]/30 transition-all"
          >
            <Upload size={24} className="text-gray-300 dark:text-[#3B3F51]" />
            <p className="font-mono text-[12px] text-gray-400">
              {file ? file.name : "Click to select file"}
            </p>
            {file && (
              <p className="font-mono text-[10px] text-gray-400">
                {(file.size / 1024).toFixed(1)} KB
              </p>
            )}
          </div>
          <input
            id="doc-file-input"
            ref={fileInputRef}
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </div>

        {error && (
          <div className="flex items-center gap-2 text-red-500 font-mono text-[12px]">
            <XCircle size={14} /> {error}
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="flex items-center justify-center gap-2 px-4 py-2.5 bg-[#0C65D2] hover:bg-[#0B5ABD] disabled:opacity-50 text-white font-mono text-[12px] transition-all"
        >
          {uploading ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <Upload size={14} />
          )}
          {uploading ? "Encrypting & Verifying…" : "Upload & Verify"}
        </button>
      </div>

      {/* Uploaded Documents */}
      {uploaded.length > 0 && (
        <div className="flex flex-col gap-3">
          <p className="font-mono text-[13px] font-bold text-gray-900 dark:text-[#F0F4FF]">
            Verification Results
          </p>
          {uploaded.map((doc) => (
            <DocumentCard key={doc.document_id} doc={doc} />
          ))}
        </div>
      )}
    </div>
  );
}

function DocumentCard({ doc }: { doc: DocumentStatus }) {
  const status = STATUS_CONFIG[doc.verification_status] || STATUS_CONFIG.pending;
  const fields = doc.extracted_fields
    ? Object.entries(doc.extracted_fields)
    : [];

  return (
    <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileText size={16} className="text-[#0C65D2]" />
          <div>
            <p className="font-mono text-[13px] font-bold text-gray-900 dark:text-[#F0F4FF] uppercase">
              {doc.document_type.replace("_", " ")}
            </p>
            <p className="font-mono text-[10px] text-gray-400">
              {doc.document_id}
            </p>
          </div>
        </div>
        <div className={`flex items-center gap-1.5 ${status.color}`}>
          {status.icon}
          <span className="font-mono text-[11px] font-bold">{status.label}</span>
        </div>
      </div>

      {/* Confidence Bar */}
      <div className="flex items-center gap-3">
        <span className="font-mono text-[11px] text-gray-500 shrink-0">
          Confidence
        </span>
        <div className="flex-1 h-2 bg-gray-200 dark:bg-[#1C1F2E] rounded-full overflow-hidden">
          <div
            className="h-full bg-[#0C65D2] transition-all duration-700"
            style={{ width: `${Math.round(doc.confidence_score * 100)}%` }}
          />
        </div>
        <span className="font-mono text-[12px] font-bold text-[#0C65D2] shrink-0">
          {Math.round(doc.confidence_score * 100)}%
        </span>
      </div>

      {/* Extracted Fields */}
      {fields.length > 0 && (
        <div className="grid grid-cols-2 gap-2">
          {fields.slice(0, 8).map(([key, value]) => (
            <div
              key={key}
              className="border border-black/5 dark:border-white/5 p-2"
            >
              <p className="font-mono text-[10px] text-gray-400 uppercase">
                {key.replace(/_/g, " ")}
              </p>
              <p className="font-mono text-[12px] text-gray-800 dark:text-[#F0F4FF] truncate">
                {String(value)}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Re-upload for rejected */}
      {doc.verification_status === "rejected" && (
        <button className="flex items-center gap-1.5 px-3 py-1.5 border border-red-500/30 text-red-500 font-mono text-[11px] hover:bg-red-500/5 w-fit transition-all">
          <RefreshCw size={12} /> Re-upload Document
        </button>
      )}
    </div>
  );
}
