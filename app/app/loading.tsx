export default function Loading() {
  return (
    <div className="fixed inset-0 z-9999 flex flex-col items-center justify-center bg-white dark:bg-[#08090E]">
      <div className="flex items-center gap-2 mb-10">
        <div className="w-8 h-8 bg-[#0C65D2] flex items-center justify-center font-mono text-sm font-bold text-white">
          EP
        </div>
        <span className="font-syne text-2xl font-bold text-gray-900 dark:text-[#F0F4FF]">
          Edu<span className="text-[#0C65D2]">Pilot</span>
        </span>
      </div>
      <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] w-72">
        <div className="bg-gray-100 dark:bg-[#161822] px-4 py-2 flex items-center gap-2 border-b border-black/10 dark:border-white/8">
          <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f57]" />
          <span className="w-2.5 h-2.5 rounded-full bg-[#febc2e]" />
          <span className="w-2.5 h-2.5 rounded-full bg-[#28c840]" />
          <span className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280] ml-auto">
            edupilot — loading
          </span>
        </div>
        <div className="p-4 font-mono text-[12px] flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <span className="text-[#0C65D2]">›</span>
            <span className="text-blue-600 dark:text-[#a8c7fa]">
              Initialising agents
            </span>
            <span className="flex gap-0.5 ml-auto">
              <span className="w-1 h-1 rounded-full bg-[#0C65D2] animate-bounce [animation-delay:0ms]" />
              <span className="w-1 h-1 rounded-full bg-[#0C65D2] animate-bounce [animation-delay:150ms]" />
              <span className="w-1 h-1 rounded-full bg-[#0C65D2] animate-bounce [animation-delay:300ms]" />
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[#0C65D2]">›</span>
            <span className="text-gray-400 dark:text-[#6B7280]">
              Loading your profile
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[#0C65D2]">›</span>
            <span className="text-gray-400 dark:text-[#6B7280]">
              Fetching opportunities
            </span>
          </div>
        </div>
        <div className="h-0.5 bg-black/8 dark:bg-white/8">
          <div className="h-full bg-[#0C65D2] animate-[loading-bar_1.5s_ease-in-out_infinite]" />
        </div>
      </div>
    </div>
  );
}
