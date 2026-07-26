"use client";
import { useEffect, useRef, useState } from "react";

type TermLine = {
  text: string;
  type: "command" | "success" | "muted";
};

type VisibleLine = {
  text: string;
  full: string;
  type: string;
};

const LINES: TermLine[] = [
  { text: "Connecting to student profile....", type: "command" },
  { text: "Loading CGPA 8.4 · CSE · 3rd year · VIT Pune ", type: "command" },
  {
    text: "Scanning 847 scholarships against your profile....",
    type: "command",
  },
  { text: "✓ 18 scholarships matched  ", type: "success" },
  { text: "✓ Eligibility verified for 12 of 18  ", type: "success" },
  { text: "✓ Career roadmap generated — ML Engineer track  ", type: "success" },
  { text: "Ready. Ask EduPilot anything.  ", type: "muted" },
];

const TYPE_SPEED = 28;
const LINE_DELAY = 320;
const CHAR_DELAY = 380;

export default function TerminalCard() {
  const [visibleLines, setVisibleLines] = useState<VisibleLine[]>([]);
  const [currentTyping, setCurrentTyping] = useState<number>(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let lineIndex = 0;
    let charIndex = 0;

    const startLine = () => {
      if (lineIndex >= LINES.length) return;
      const line = LINES[lineIndex];
      charIndex = 0;

      setVisibleLines((prev: VisibleLine[]) => [
        ...prev,
        { text: "", full: line.text, type: line.type },
      ]);

      intervalRef.current = setInterval(() => {
        charIndex++;
        const sliced = line.text.slice(0, charIndex);

        setVisibleLines((prev: VisibleLine[]) =>
          prev.map((l: VisibleLine, i: number) =>
            i === lineIndex ? { ...l, text: sliced } : l,
          ),
        );
        setCurrentTyping(lineIndex);

        if (charIndex >= line.text.length) {
          clearInterval(intervalRef.current!);
          lineIndex++;
          setTimeout(startLine, LINE_DELAY);
        }
      }, TYPE_SPEED);
    };

    const initial = setTimeout(startLine, CHAR_DELAY);
    return () => {
      clearTimeout(initial);
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const colorClass = (type: string) => {
    if (type === "success") return "text-green-500 dark:text-green-400";
    if (type === "muted") return "text-gray-400 dark:text-[#6B7280]";
    return "text-blue-600 dark:text-[#a8c7fa]";
  };

  return (
    <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] overflow-hidden transition-all duration-500 w-full">
      <div className="bg-gray-100 dark:bg-[#161822] px-3 sm:px-4 py-2.5 flex items-center gap-2 border-b border-black/10 dark:border-white/8 transition-all duration-500">
        <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f57] shrink-0" />
        <span className="w-2.5 h-2.5 rounded-full bg-[#febc2e] shrink-0" />
        <span className="w-2.5 h-2.5 rounded-full bg-[#28c840] shrink-0" />
        <span className="font-mono text-[10px] sm:text-[11px] text-gray-400 dark:text-[#6B7280] ml-auto truncate">
          edupilot — agent runtime
        </span>
      </div>
      <div className="p-3 sm:p-5 font-mono text-[11px] sm:text-[13px] leading-loose min-h-48 sm:min-h-55 overflow-x-auto">
        {visibleLines.map((line: VisibleLine, i: number) => (
          <div key={i} className="flex items-baseline gap-1.5 sm:gap-2 min-w-0">
            <span className="text-[#0C65D2] select-none shrink-0">›</span>
            <span
              className={`${colorClass(line.type)} wrap-break-word min-w-0`}
            >
              {line.text}
              {i === currentTyping && line.text !== line.full && (
                <span className="inline-block w-1.5 sm:w-2 h-3 sm:h-3.5 bg-[#0C65D2] ml-0.5 align-middle animate-[blink_1s_infinite]" />
              )}
            </span>
          </div>
        ))}
        {visibleLines.length === 0 && (
          <span className="inline-block w-1.5 sm:w-2 h-3 sm:h-3.5 bg-[#0C65D2] animate-[blink_1s_infinite]" />
        )}
      </div>
    </div>
  );
}
