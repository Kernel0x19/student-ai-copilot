"use client";

import { useState, useCallback } from "react";
import {
  ThumbsUp,
  ThumbsDown,
  AlertCircle,
  Send,
  Loader2,
  Check,
  X,
  MessageSquare,
} from "lucide-react";
import { submitFeedback } from "@/app/lib/api";
import type { FeedbackPayload } from "@/app/lib/api";

type FeedbackType = FeedbackPayload["feedback_type"];

const FEEDBACK_OPTIONS: { type: FeedbackType; icon: React.ReactNode; label: string; color: string }[] = [
  { type: "relevant", icon: <ThumbsUp size={14} />, label: "Relevant", color: "text-green-500 border-green-500/30 hover:bg-green-500/5" },
  { type: "not_relevant", icon: <ThumbsDown size={14} />, label: "Not Relevant", color: "text-amber-500 border-amber-500/30 hover:bg-amber-500/5" },
  { type: "ineligible", icon: <AlertCircle size={14} />, label: "Ineligible", color: "text-red-500 border-red-500/30 hover:bg-red-500/5" },
];

interface Props {
  opportunityId: string;
  userId: string;
  userEmail: string;
}

export default function FeedbackWidget({ opportunityId, userId, userEmail }: Props) {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<FeedbackType | null>(null);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = useCallback(async () => {
    if (!selected) return;
    setSubmitting(true);
    try {
      await submitFeedback(userId, {
        opportunity_id: opportunityId,
        feedback_type: selected,
        comment: comment.trim() || undefined,
      }, userEmail);
      setSubmitted(true);
      setTimeout(() => setOpen(false), 1500);
    } catch {
      // silent
    } finally {
      setSubmitting(false);
    }
  }, [selected, comment, userId, userEmail, opportunityId]);

  if (submitted) {
    return (
      <span className="flex items-center gap-1.5 font-mono text-[11px] text-green-500">
        <Check size={12} /> Feedback sent
      </span>
    );
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-1.5 px-2 py-1 border border-black/10 dark:border-white/8 font-mono text-[11px] text-gray-400 hover:text-[#0C65D2] transition-all"
      >
        <MessageSquare size={12} /> Rate
      </button>
    );
  }

  return (
    <div className="border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] p-3 flex flex-col gap-2 animate-in fade-in">
      <div className="flex items-center justify-between">
        <p className="font-mono text-[11px] text-gray-500">Rate this match</p>
        <button onClick={() => setOpen(false)} className="text-gray-400 hover:text-gray-600">
          <X size={12} />
        </button>
      </div>

      <div className="flex gap-2">
        {FEEDBACK_OPTIONS.map((opt) => (
          <button
            key={opt.type}
            onClick={() => setSelected(opt.type)}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 border font-mono text-[11px] transition-all ${
              selected === opt.type
                ? `${opt.color} bg-opacity-10`
                : "border-black/10 dark:border-white/8 text-gray-400"
            }`}
          >
            {opt.icon} {opt.label}
          </button>
        ))}
      </div>

      <input
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Optional comment…"
        className="w-full px-3 py-1.5 border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] font-mono text-[11px] outline-none"
      />

      <button
        onClick={handleSubmit}
        disabled={!selected || submitting}
        className="flex items-center justify-center gap-1.5 px-3 py-1.5 bg-[#0C65D2] text-white font-mono text-[11px] disabled:opacity-50 transition-all"
      >
        {submitting ? <Loader2 size={12} className="animate-spin" /> : <Send size={12} />}
        Submit
      </button>
    </div>
  );
}
