"use client";

import { useEffect, useState } from "react";
import { getConsents, setConsent } from "@/app/lib/api";

const PURPOSE_LABELS: Record<string, string> = {
  aadhaar_verification: "Use my Aadhaar to auto-verify eligibility",
  income_certificate_processing: "Process income certificate in secure enclave",
  eligibility_auto_check: "Run automatic eligibility checks against schemes",
  document_ocr: "Extract data from uploaded documents via OCR",
  notification_email: "Send deadline reminders via email",
  notification_sms: "Send deadline reminders via SMS",
};

interface Props {
  userId: string;
  userEmail: string;
}

export default function ConsentManager({ userId, userEmail }: Props) {
  const [consents, setConsents] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getConsents(userId, userEmail)
      .then((records) => {
        const map: Record<string, boolean> = {};
        records.forEach((r) => { map[r.purpose] = r.granted; });
        setConsents(map);
      })
      .finally(() => setLoading(false));
  }, [userId, userEmail]);

  async function toggle(purpose: string, granted: boolean) {
    await setConsent(userId, purpose, granted, userEmail);
    setConsents((c) => ({ ...c, [purpose]: granted }));
  }

  if (loading) return <p className="font-mono text-[12px] text-gray-400">Loading consents…</p>;

  return (
    <div className="flex flex-col gap-4 max-w-xl">
      <div>
        <h1 className="font-syne text-xl font-bold">Consent Management</h1>
        <p className="font-mono text-[12px] text-gray-400 mt-1">
          DPDP Act compliant opt-in per data use case. All access is audit-logged.
        </p>
      </div>
      {Object.entries(PURPOSE_LABELS).map(([purpose, label]) => (
        <label
          key={purpose}
          className="flex items-start gap-3 border border-black/10 dark:border-white/8 p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-[#0F1117]"
        >
          <input
            type="checkbox"
            checked={consents[purpose] ?? false}
            onChange={(e) => toggle(purpose, e.target.checked)}
            className="mt-0.5"
          />
          <div>
            <p className="font-mono text-[13px] text-gray-900 dark:text-[#F0F4FF]">{label}</p>
            <p className="font-mono text-[10px] text-gray-400 mt-0.5">{purpose}</p>
          </div>
        </label>
      ))}
    </div>
  );
}
