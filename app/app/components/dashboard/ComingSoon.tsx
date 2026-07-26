import { Construction } from "lucide-react";
import Link from "next/link";

interface Props {
  title: string;
  description: string;
  backHref?: string;
}

export default function ComingSoon({ title, description, backHref = "/dashboard" }: Props) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
      <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-10 flex flex-col items-center gap-5 max-w-md w-full">
        <div className="w-full border border-black/10 dark:border-white/8 overflow-hidden">
          <div className="bg-gray-100 dark:bg-[#161822] px-4 py-2 flex items-center gap-2 border-b border-black/10 dark:border-white/8">
            <span className="w-2 h-2 rounded-full bg-[#ff5f57]" />
            <span className="w-2 h-2 rounded-full bg-[#febc2e]" />
            <span className="w-2 h-2 rounded-full bg-[#28c840]" />
            <span className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280] ml-auto">
              edupilot — {title.toLowerCase()}
            </span>
          </div>
          <div className="p-4 font-mono text-[12px]">
            <div className="flex gap-2">
              <span className="text-[#0C65D2]">›</span>
              <span className="text-blue-600 dark:text-[#a8c7fa]">Loading {title.toLowerCase()} module...</span>
            </div>
            <div className="flex gap-2 mt-1">
              <span className="text-[#0C65D2]">›</span>
              <span className="text-yellow-600 dark:text-yellow-400">⚠ Under construction by AI team</span>
            </div>
            <div className="flex gap-2 mt-1">
              <span className="text-[#0C65D2]">›</span>
              <span className="text-gray-400 dark:text-[#6B7280]">ETA: coming soon</span>
            </div>
          </div>
        </div>

        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <Construction size={16} className="text-[#0C65D2]" />
            <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-lg">{title}</p>
          </div>
          <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] leading-relaxed">
            {description}
          </p>
        </div>

        <Link
          href={backHref}
          className="flex items-center gap-2 px-5 py-2.5 border border-black/10 dark:border-white/8 font-mono text-sm text-gray-500 dark:text-[#6B7280] hover:border-[#0C65D2]/40 hover:text-[#0C65D2] transition-all duration-200"
        >
          ← Back to Dashboard
        </Link>
      </div>
    </div>
  );
}