import {
  ArrowRight,
  Play,
  GraduationCap,
  FileText,
  Briefcase,
  ClipboardCheck,
} from "lucide-react";
import Navbar from "./components/Navbar";
import TerminalCard from "./components/home/TerminalCard";
import FeaturesSection from "./components/home/FeaturesSection";
import HowItWorksSection from "./components/home/HowItWorksSection";
import WorkflowSection from "./components/home/WorkflowSection";
import BenefitsSection from "./components/home/BenefitsSection";
import FAQSection from "./components/home/FAQsSection";
import Footer from "./components/Footer";
import { redirect } from "next/navigation";

type AgentCardProps = {
  icon: React.ReactNode;
  label: string;
  sub: string;
};

function AgentCard({ icon, label, sub }: AgentCardProps) {
  return (
    <div className="bg-gray-50 dark:bg-[#161822] border border-black/10 dark:border-white/8 p-3 flex items-center gap-3 hover:border-[#0C65D2]/40 transition-colors duration-500 cursor-default">
      <div className="w-8 h-8 bg-[#0C65D2]/10 border border-[#0C65D2]/20 flex items-center justify-center text-[#0C65D2] shrink-0 transition-all duration-500">
        {icon}
      </div>
      <div>
        <p className="font-mono text-[13px] text-gray-900 dark:text-[#F0F4FF] transition-all duration-500">
          {label}
        </p>
        <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
          {sub}
        </p>
      </div>
    </div>
  );
}

type StatProps = {
  value: string;
  label: string;
  last?: boolean;
};

function Stat({ value, label, last }: StatProps) {
  return (
    <div
      className={`py-4 sm:py-6 text-center ${!last ? "border-r border-black/10 dark:border-white/8" : ""}`}
    >
      <p className="font-syne text-xl sm:text-2xl lg:text-3xl font-extrabold">
        <span className="text-[#0C65D2]">{value}</span>
      </p>
      <p className="font-mono text-[10px] sm:text-[11px] text-gray-400 dark:text-[#6B7280] mt-1 px-1">
        {label}
      </p>
    </div>
  );
}

async function handleSignupRedirect() {
  "use server";
  redirect("/auth/signup");
}

export default function Home() {
  return (
    <div
      id="home"
      className="min-h-screen bg-white dark:bg-[#08090E] text-gray-900 dark:text-[#F0F4FF] transition-colors duration-500"
    >
      <Navbar />

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 pt-14 sm:pt-18 lg:pt-20 pb-12 sm:pb-14 lg:pb-16 grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-16 items-center">
        <div>
          <div className="inline-flex items-center gap-2 bg-[#0C65D2]/10 border border-[#0C65D2]/30 px-3 sm:px-3.5 py-1.5 font-mono text-[10px] sm:text-[11px] text-[#0C65D2] dark:text-[#6fa8f5] mb-5 sm:mb-6 tracking-widest">
            <span className="w-1.5 h-1.5 rounded-full bg-[#0C65D2] animate-pulse" />
            AGENTIC AI — CODEAMBLE 2026
          </div>

          <h1 className="font-syne text-3xl sm:text-4xl lg:text-[3.2rem] font-extrabold leading-[1.1] tracking-tight text-gray-900 dark:text-[#F0F4FF] mb-4 sm:mb-5 transition-all duration-500">
            Your entire academic
            <br />
            future, <span className="text-[#0C65D2]">co-piloted.</span>
          </h1>

          <p className="text-gray-500 dark:text-[#6B7280] text-sm sm:text-base leading-relaxed mb-6 sm:mb-8 max-w-xl transition-all duration-500">
            Scholarships, eligibility checks, document analysis, and career
            roadmaps — handled by a multi-agent AI system built for Indian
            students.
          </p>

          <div className="flex flex-wrap gap-3 mb-6 sm:mb-8">
            <form action={handleSignupRedirect}>
              <button className="flex items-center gap-2 px-5 sm:px-6 py-2.5 sm:py-3 bg-[#0C65D2] text-white font-mono text-xs sm:text-sm hover:bg-[#0a52b0] transition-colors duration-500 cursor-pointer group">
                Start for free
                <ArrowRight
                  size={15}
                  className="group-hover:translate-x-0.5 transition-transform duration-500"
                />
              </button>
            </form>
            <button className="flex items-center gap-2 px-5 sm:px-6 py-2.5 sm:py-3 bg-transparent border border-black/10 dark:border-white/8 text-gray-500 dark:text-[#6B7280] font-mono text-xs sm:text-sm hover:border-black/30 dark:hover:border-white/20 hover:text-gray-900 dark:hover:text-[#F0F4FF] transition-all duration-500 cursor-pointer">
              <Play size={14} />
              Watch demo
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {[
              "Scholarship discovery",
              "OCR analysis",
              "Eligibility check",
              "Career roadmap",
            ].map((f) => (
              <span
                key={f}
                className="font-mono text-[10px] sm:text-[11px] text-gray-400 dark:text-[#6B7280] border border-black/10 dark:border-white/8 px-2.5 sm:px-3 py-1"
              >
                {f}
              </span>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-3">
          <TerminalCard />
          <div className="grid grid-cols-2 gap-2">
            <AgentCard
              icon={<GraduationCap size={16} />}
              label="Scholarship agent"
              sub="847 sources indexed"
            />
            <AgentCard
              icon={<FileText size={16} />}
              label="OCR agent"
              sub="Documents + marksheets"
            />
            <AgentCard
              icon={<Briefcase size={16} />}
              label="Career agent"
              sub="Roadmaps + internships"
            />
            <AgentCard
              icon={<ClipboardCheck size={16} />}
              label="Eligibility agent"
              sub="Auto-verifies criteria"
            />
          </div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 border-t border-black/10 dark:border-white/8">
        <div className="grid grid-cols-3">
          <Stat value="847+" label="Scholarships indexed" />
          <Stat value="4 Agents" label="Working in parallel" />
          <Stat value="0 Manual" label="AI handles discovery" last />
        </div>
      </div>

      <FeaturesSection />
      <HowItWorksSection />
      <WorkflowSection />
      <BenefitsSection />
      <FAQSection />
      <Footer />
    </div>
  );
}
