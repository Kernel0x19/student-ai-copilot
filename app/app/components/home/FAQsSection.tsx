"use client";
import { useState } from "react";
import { Plus, Minus } from "lucide-react";

const FAQS = [
  {
    q: "Is EduPilot free to use?",
    a: "Yes — EduPilot is completely free during beta. Create your profile, upload documents, and get AI-powered scholarship and internship recommendations at no cost. We'll announce any pricing changes well in advance.",
  },
  {
    q: "How does the scholarship matching actually work?",
    a: "When you set up your profile, EduPilot stores your CGPA, stream, year, institution, category, and family income. The scholarship agent cross-references these against 847+ indexed scholarships in real time and surfaces only the ones you're actually eligible for — not a generic list.",
  },
  {
    q: "Is my data safe? Who can see my documents?",
    a: "Your documents are stored securely and are only accessible by you. EduPilot does not share your data with third parties. Document content is processed by the OCR agent solely to extract academic details and auto-fill your profile — nothing is stored beyond what you see in your dashboard.",
  },
  {
    q: "What types of documents can I upload?",
    a: "You can upload marksheets, bonafide certificates, income certificates, caste certificates, and offer letters. Supported formats are PDF, JPG, and PNG. The OCR agent handles scanned documents too, not just digital ones.",
  },
  {
    q: "Does EduPilot apply to scholarships on my behalf?",
    a: "Not yet — EduPilot finds, verifies, and tracks opportunities for you, but the actual application submission happens on the scholarship provider's portal. We pre-fill as much of the application data as possible using your stored profile to save you time.",
  },
  {
    q: "Which colleges and streams does EduPilot support?",
    a: "EduPilot works for students across all Indian colleges and streams — engineering, medicine, arts, commerce, and sciences. The scholarship database covers central government, state government, and private scholarships applicable across institutions.",
  },
  {
    q: "Can I use the AI chat assistant without filling my profile?",
    a: "You can, but the answers won't be personalized. The AI assistant is most powerful when it knows your profile — it can then tell you exactly which scholarships you qualify for, what your eligibility gaps are, and what your next steps should be.",
  },
];

export default function FAQSection() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section
      id="faq"
      className="border-t border-black/10 dark:border-white/8 py-16 sm:py-20 lg:py-24 transition-all duration-500"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
        <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] xl:grid-cols-[320px_1fr] gap-8 sm:gap-12 lg:gap-16">
          <div className="lg:sticky lg:top-28 lg:self-start">
            <div className="inline-flex items-center gap-2 bg-[#0C65D2]/10 border border-[#0C65D2]/30 px-3.5 py-1.5 font-mono text-[11px] text-[#0C65D2] dark:text-[#6fa8f5] mb-4 tracking-widest transition-all duration-500">
              <span className="w-1.5 h-1.5 rounded-full bg-[#0C65D2]" />
              FAQ
            </div>
            <h2 className="font-syne text-2xl sm:text-3xl lg:text-4xl font-extrabold text-gray-900 dark:text-[#F0F4FF] tracking-tight leading-[1.1] mb-4 transition-all duration-500">
              Questions students actually ask.
            </h2>
            <p className="font-mono text-sm text-gray-500 dark:text-[#6B7280] leading-relaxed transition-all duration-500">
              Can&apos;t find what you&apos;re looking for? Ask the AI assistant directly
              — it knows everything about EduPilot.
            </p>
          </div>

          <div className="flex flex-col">
            {FAQS.map((faq, i) => (
              <div
                key={i}
                className="border-b border-black/10 dark:border-white/8 first:border-t transition-all duration-500"
              >
                <button
                  onClick={() => setOpen(open === i ? null : i)}
                  className="w-full flex items-start justify-between gap-4 sm:gap-6 py-4 sm:py-5 text-left cursor-pointer group"
                >
                  <span
                    className={`font-syne font-bold text-sm sm:text-base transition-all duration-500 ${
                      open === i
                        ? "text-[#0C65D2]"
                        : "text-gray-900 dark:text-[#F0F4FF] group-hover:text-[#0C65D2]"
                    }`}
                  >
                    {faq.q}
                  </span>
                  <span
                    className={`shrink-0 mt-0.5 transition-all duration-500 ${
                      open === i
                        ? "text-[#0C65D2]"
                        : "text-gray-400 dark:text-[#6B7280]"
                    }`}
                  >
                    {open === i ? <Minus size={16} /> : <Plus size={16} />}
                  </span>
                </button>

                <div
                  className={`overflow-hidden transition-all duration-300 ${
                    open === i ? "max-h-64 pb-4 sm:pb-5" : "max-h-0"
                  }`}
                >
                  <p className="font-mono text-xs sm:text-sm text-gray-500 dark:text-[#6B7280] leading-relaxed transition-all duration-500">
                    {faq.a}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}