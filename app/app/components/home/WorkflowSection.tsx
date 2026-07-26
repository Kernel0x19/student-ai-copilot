"use client";
import { useEffect, useState } from "react";

const AGENTS = [
  {
    id: "scholarship",
    label: "Scholarship",
    sub: "847 sources",
    color: "#0C65D2",
  },
  { id: "ocr", label: "OCR", sub: "Document parser", color: "#0C65D2" },
  {
    id: "eligibility",
    label: "Eligibility",
    sub: "Criteria checker",
    color: "#0C65D2",
  },
  { id: "career", label: "Career", sub: "Roadmap builder", color: "#0C65D2" },
];

const PIPELINE_STEPS = [
  "Student query received",
  "Orchestrator routes to agents",
  "Agents run in parallel",
  "Results aggregated",
  "Personalized output delivered",
];

export default function WorkflowSection() {
  const [activeStep, setActiveStep] = useState(0);
  const [activeAgent, setActiveAgent] = useState<number | null>(null);
  const [running, setRunning] = useState(false);

  const startAnimation = () => {
    if (running) return;
    setRunning(true);
    setActiveStep(0);
    setActiveAgent(null);

    setTimeout(() => setActiveStep(1), 600);
    setTimeout(() => setActiveStep(2), 1200);
    setTimeout(() => {
      setActiveStep(2);
      setActiveAgent(0);
    }, 1600);
    setTimeout(() => setActiveAgent(1), 2000);
    setTimeout(() => setActiveAgent(2), 2400);
    setTimeout(() => setActiveAgent(3), 2800);
    setTimeout(() => {
      setActiveStep(3);
      setActiveAgent(null);
    }, 3400);
    setTimeout(() => setActiveStep(4), 4200);
    setTimeout(() => setActiveStep(5), 4800);
    setTimeout(() => setRunning(false), 5000);
  };

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) startAnimation();
      },
      { threshold: 0.3 },
    );
    const el = document.getElementById("workflow-section");
    if (el) observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      id="workflow"
      className="border-t border-black/10 dark:border-white/8 py-14 sm:py-20 lg:py-24 transition-all duration-500"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
        <div className="mb-10 sm:mb-14 lg:mb-16">
          <div className="inline-flex items-center gap-2 bg-[#0C65D2]/10 border border-[#0C65D2]/30 px-3.5 py-1.5 font-mono text-[11px] text-[#0C65D2] dark:text-[#6fa8f5] mb-4 tracking-widest transition-all duration-500">
            <span className="w-1.5 h-1.5 rounded-full bg-[#0C65D2]" />
            WORKFLOW
          </div>
          <div className="flex items-end justify-between gap-4">
            <div>
              <h2 className="font-syne text-2xl sm:text-3xl lg:text-4xl font-extrabold text-gray-900 dark:text-[#F0F4FF] tracking-tight transition-all duration-500">
                How the agents
                <span className="text-[#0C65D2]"> work together.</span>
              </h2>
              <p className="mt-3 text-gray-500 dark:text-[#6B7280] font-mono text-xs sm:text-sm max-w-lg transition-all duration-500">
                Every query is routed by an orchestrator that decides which
                agents to activate and in what order.
              </p>
            </div>
            <button
              onClick={startAnimation}
              disabled={running}
              className="hidden lg:flex items-center gap-2 px-4 py-2 border border-black/10 dark:border-white/8 font-mono text-xs text-gray-500 dark:text-[#6B7280] hover:border-[#0C65D2]/40 hover:text-[#0C65D2] disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-all duration-500"
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${running ? "bg-green-500 animate-pulse" : "bg-gray-400 dark:bg-[#6B7280]"} transition-all duration-500`}
              />
              {running ? "Running..." : "Re-run pipeline"}
            </button>
          </div>
          <button
            onClick={startAnimation}
            disabled={running}
            className="mt-4 lg:hidden flex items-center gap-2 px-4 py-2 border border-black/10 dark:border-white/8 font-mono text-xs text-gray-500 dark:text-[#6B7280] hover:border-[#0C65D2]/40 hover:text-[#0C65D2] disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-all duration-500"
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${running ? "bg-green-500 animate-pulse" : "bg-gray-400 dark:bg-[#6B7280]"} transition-all duration-500`}
            />
            {running ? "Running..." : "Re-run pipeline"}
          </button>
        </div>

        <div
          id="workflow-section"
          className="flex flex-col lg:grid lg:grid-cols-[1fr_auto_1fr_auto_1fr] gap-4 lg:gap-0 items-stretch lg:items-center"
        >
          <PipelineNode
            active={activeStep >= 0}
            label="Student"
            sub="Asks a question"
            tag="INPUT"
            accent
          />
          <PipelineArrow active={activeStep >= 1} />
          <PipelineNode
            active={activeStep >= 1}
            label="Orchestrator"
            sub="Routes and coordinates"
            tag="LangGraph"
            highlight
          />
          <PipelineArrow active={activeStep >= 2} />
          <div className="flex flex-col gap-3">
            {AGENTS.map((agent, i) => (
              <AgentNode
                key={agent.id}
                label={agent.label}
                sub={agent.sub}
                active={
                  activeAgent !== null && activeAgent >= i && activeStep >= 2
                }
                firing={activeAgent === i}
              />
            ))}
          </div>
        </div>

        <div className="mt-4 lg:mt-6 flex flex-col lg:grid lg:grid-cols-[1fr_auto_1fr_auto_1fr] gap-0 items-center">
          <div />
          <div />
          <PipelineArrow active={activeStep >= 3} vertical />
          <div />
          <div />
        </div>

        <div className="flex flex-col lg:grid lg:grid-cols-[1fr_auto_1fr_auto_1fr] gap-4 lg:gap-0 items-stretch lg:items-center">
          <div className="hidden lg:block" />
          <div className="hidden lg:block" />
          <PipelineNode
            active={activeStep >= 3}
            label="Aggregator"
            sub="Merges agent results"
            tag="FastAPI"
          />
          <PipelineArrow active={activeStep >= 4} />
          <PipelineNode
            active={activeStep >= 4}
            label="Dashboard"
            sub="Personalized output"
            tag="OUTPUT"
            accent
          />
        </div>

        <div className="mt-10 sm:mt-14 lg:mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {PIPELINE_STEPS.map((step, i) => (
            <div
              key={i}
              className={`border px-4 py-3 transition-all duration-500 ${
                activeStep > i
                  ? "border-[#0C65D2]/40 bg-[#0C65D2]/8 dark:bg-[#0C65D2]/10"
                  : "border-black/10 dark:border-white/8 bg-transparent"
              }`}
            >
              <p
                className={`font-mono text-[10px] tracking-widest mb-1 ${activeStep > i ? "text-[#0C65D2]" : "text-gray-400 dark:text-[#6B7280]"} transition-all duration-500`}
              >
                STEP {String(i + 1).padStart(2, "0")}
              </p>
              <p
                className={`font-mono text-[11px] ${activeStep > i ? "text-gray-900 dark:text-[#F0F4FF]" : "text-gray-400 dark:text-[#6B7280]"} transition-all duration-500`}
              >
                {step}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function PipelineNode({
  active,
  label,
  sub,
  tag,
  highlight,
  accent,
}: {
  active: boolean;
  label: string;
  sub: string;
  tag: string;
  highlight?: boolean;
  accent?: boolean;
}) {
  return (
    <div
      className={`border p-4 sm:p-5 transition-all duration-500 ${
        active
          ? highlight
            ? "border-[#0C65D2] bg-[#0C65D2]/8 dark:bg-[#0C65D2]/10"
            : accent
              ? "border-[#0C65D2]/60 bg-white dark:bg-[#0F1117]"
              : "border-black/20 dark:border-white/20 bg-white dark:bg-[#0F1117]"
          : "border-black/10 dark:border-white/8 bg-transparent"
      }`}
    >
      <div className="flex items-center justify-between mb-2 transition-all duration-500">
        <span
          className={`font-mono text-[10px] tracking-widest px-2 py-0.5 border ${
            active
              ? "border-[#0C65D2]/30 bg-[#0C65D2]/10 text-[#0C65D2] dark:text-[#6fa8f5]"
              : "border-black/10 dark:border-white/8 text-gray-400 dark:text-[#6B7280]"
          }`}
        >
          {tag}
        </span>
        <span
          className={`w-2 h-2 rounded-full transition-all duration-500 ${
            active
              ? "bg-[#0C65D2] animate-pulse"
              : "bg-gray-300 dark:bg-white/10"
          }`}
        />
      </div>
      <p
        className={`font-syne font-bold text-sm sm:text-base transition-colors duration-500 ${active ? "text-gray-900 dark:text-[#F0F4FF]" : "text-gray-400 dark:text-[#6B7280]"}`}
      >
        {label}
      </p>
      <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] mt-0.5">
        {sub}
      </p>
    </div>
  );
}

function AgentNode({
  label,
  sub,
  active,
  firing,
}: {
  label: string;
  sub: string;
  active: boolean;
  firing: boolean;
}) {
  return (
    <div
      className={`border px-4 py-2.5 flex items-center gap-3 transition-all duration-300 ${
        firing
          ? "border-[#0C65D2] bg-[#0C65D2]/10 dark:bg-[#0C65D2]/15"
          : active
            ? "border-black/20 dark:border-white/20 bg-white dark:bg-[#0F1117]"
            : "border-black/10 dark:border-white/8 bg-transparent"
      }`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full shrink-0 transition-all duration-300 ${
          firing
            ? "bg-[#0C65D2] animate-ping"
            : active
              ? "bg-green-500"
              : "bg-gray-300 dark:bg-white/10"
        }`}
      />
      <div>
        <p
          className={`font-mono text-[12px] transition-colors duration-300 ${active ? "text-gray-900 dark:text-[#F0F4FF]" : "text-gray-400 dark:text-[#6B7280]"}`}
        >
          {label} agent
        </p>
        <p className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280]">
          {sub}
        </p>
      </div>
    </div>
  );
}

function PipelineArrow({
  active,
  vertical,
}: {
  active: boolean;
  vertical?: boolean;
}) {
  if (vertical) {
    return (
      <div className="flex justify-center py-2">
        <div
          className={`w-px h-8 transition-all duration-500 ${active ? "bg-[#0C65D2]" : "bg-black/10 dark:bg-white/8"}`}
        />
      </div>
    );
  }
  return (
    <div className="flex items-center justify-center px-2 py-2 lg:py-0">
      <div className="flex items-center gap-0 transition-all duration-500">
        <div
          className={`h-px w-8 transition-all duration-500 ${active ? "bg-[#0C65D2]" : "bg-black/10 dark:bg-white/8"}`}
        />
        <div
          className={`w-0 h-0 border-t-4 border-b-4 border-l-6 border-t-transparent border-b-transparent transition-all duration-500 ${active ? "border-l-[#0C65D2]" : "border-l-black/10 dark:border-l-white/8"}`}
        />
      </div>
    </div>
  );
}
