"use client";
import Navbar from "@/app/components/Navbar";
import TerminalCard from "@/app/components/TerminalCard";
import { ArrowUpRight, MoveRight } from "lucide-react";
import Image from "next/image";
import { redirect } from "next/navigation";

const page = () => {
  return (
    <div className="min-h-screen bg-white dark:bg-[#08090E] text-gray-900 dark:text-[#F0F4FF] transition-colors duration-500">
      <Navbar isAuth={true} />
      <section className="max-w-300 mx-auto px-10 pt-15 pb-16 grid grid-cols-1 lg:grid-cols-2 gap-25 items-center">
        <div className="flex flex-col gap-3">
          <h1 className="font-syne text-5xl lg:text-[3.2rem] font-extrabold leading-[1.1] tracking-tight text-gray-900 dark:text-[#F0F4FF] mb-5 transition-all duration-500">
            Your entire academic
            <br />
            future, <span className="text-[#0C65D2]">co-piloted.</span>
          </h1>
          <p className="text-gray-500 dark:text-[#6B7280] text-base leading-relaxed mb-8 max-w-120 transition-all duration-500">
            Scholarships, eligibility checks, document analysis, and career
            roadmaps — handled by a multi-agent AI system built for Indian
            students.
          </p>
          <TerminalCard />
        </div>
        <div className="flex flex-col gap-5 p-8 shadow-xl border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] overflow-hidden transition-all duration-500">
          <div className="flex flex-col gap-2">
            <h1 className="text-2xl font-bold">
              Create your <span className="text-[#0C65D2]">Account</span>
            </h1>
          </div>
          <div className="flex gap-4">
            <div className="flex flex-col gap-1.5 flex-1">
              <label className="text-base text-black/50 dark:text-white/50 font-semibold uppercase tracking-wide transition-colors duration-500">
                First Name
              </label>
              <input
                type="text"
                placeholder="Prathamesh"
                className="px-3.5 py-2.5 w-full rounded-lg text-sm border outline-none transition-colors duration-500 bg-black/8 border-black/15 text-black placeholder-black/35 focus:border-black/25 focus:bg-black/10 dark:bg-white/12 dark:border-white/20 dark:text-white dark:placeholder-white/30 dark:focus:border-white/40 dark:focus:bg-white/15"
              />
            </div>
            <div className="flex flex-col gap-1.5 flex-1">
              <label className="text-base text-black/50 dark:text-white/50 font-semibold uppercase tracking-wide transition-colors duration-500">
                Last Name
              </label>
              <input
                type="text"
                placeholder="Kulkarni"
                className="px-3.5 py-2.5 w-full rounded-lg text-sm border outline-none transition-colors duration-500 bg-black/8 border-black/15 text-black placeholder-black/35 focus:border-black/25 focus:bg-black/10 dark:bg-white/12 dark:border-white/20 dark:text-white dark:placeholder-white/30 dark:focus:border-white/40 dark:focus:bg-white/15"
              />
            </div>
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-base text-black/50 dark:text-white/50 font-semibold uppercase tracking-wide transition-colors duration-500">
              Email
            </label>
            <input
              type="email"
              placeholder="you@example.com"
              className="px-3.5 py-2.5 w-full rounded-lg text-sm border outline-none transition-colors duration-500 bg-black/8 border-black/15 text-black placeholder-black/35 focus:border-black/25 focus:bg-black/10 dark:bg-white/12 dark:border-white/20 dark:text-white dark:placeholder-white/30 dark:focus:border-white/40 dark:focus:bg-white/15"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-base text-black/50 dark:text-white/50 font-semibold uppercase tracking-wide transition-colors duration-500">
              Password
            </label>
            <input
              type="password"
              placeholder="Min. 8 characters"
              className="px-3.5 py-2.5 w-full rounded-lg text-sm border outline-none transition-colors duration-500 bg-black/8 border-black/15 text-black placeholder-black/35 focus:border-black/25 focus:bg-black/10 dark:bg-white/12 dark:border-white/20 dark:text-white dark:placeholder-white/30 dark:focus:border-white/40 dark:focus:bg-white/15"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-base text-black/50 dark:text-white/50 font-semibold uppercase tracking-wide transition-colors duration-500">
              College / University
            </label>
            <input
              type="text"
              placeholder="Vishwakarma Institute of Technology, Pune"
              className="px-3.5 py-2.5 w-full rounded-lg text-sm border outline-none transition-colors duration-500 bg-black/8 border-black/15 text-black placeholder-black/35 focus:border-black/25 focus:bg-black/10 dark:bg-white/12 dark:border-white/20 dark:text-white dark:placeholder-white/30 dark:focus:border-white/40 dark:focus:bg-white/15"
            />
          </div>
          <div className="flex gap-4">
            <div className="flex flex-col gap-1.5 flex-1">
              <label className="text-base text-black/50 dark:text-white/50 font-semibold uppercase tracking-wide transition-colors duration-500">
                Stream
              </label>
              <select className="px-3.5 py-2.5 w-full rounded-lg text-sm border outline-none transition-colors duration-500 bg-black/8 border-black/15 text-black/70 focus:border-black/25 focus:bg-black/10 dark:bg-white/12 dark:border-white/20 dark:text-white/70 dark:focus:border-white/40 dark:focus:bg-white/15 appearance-none cursor-pointer">
                <option defaultValue="Select Stream">Select stream</option>
                <option>Computer Science (AI)</option>
                <option>Computer Science</option>
                <option>Electronics & TC</option>
                <option>Data Science</option>
                <option>Mechanical</option>
                <option>Civil</option>
                <option>Other</option>
              </select>
            </div>
            <div className="flex flex-col gap-1.5 flex-1">
              <label className="text-base text-black/50 dark:text-white/50 font-semibold uppercase tracking-wide transition-colors duration-500">
                Year
              </label>
              <select className="px-3.5 py-2.5 w-full rounded-lg text-sm border outline-none transition-colors duration-500 bg-black/8 border-black/15 text-black/70 focus:border-black/25 focus:bg-black/10 dark:bg-white/12 dark:border-white/20 dark:text-white/70 dark:focus:border-white/40 dark:focus:bg-white/15 appearance-none cursor-pointer">
                <option defaultValue={"Select Year"}>Select year</option>
                <option value={"1st Year"}>1st year</option>
                <option value={"2nd Year"}>2nd year</option>
                <option value={"3rd Year"}>3rd year</option>
                <option value={"4th Year"}>4th year</option>
              </select>
            </div>
          </div>
          <div className="w-full flex items-center justify-center">
            <button className="px-5 py-3 bg-[#0C65D2] text-white font-mono text-sm hover:bg-[#0a52b0] hover:rounded-lg transition-all duration-500 cursor-pointer flex items-center gap-2 group">
              Create Account
              <MoveRight
                size={15}
                className="group-hover:translate-x-0.5 transition-transform duration-500"
              />
            </button>
          </div>

          <div className="flex items-center gap-2.5">
            <div className="flex-1 h-px bg-black/8 dark:bg-white/7" />
            <span className="text-[11px] uppercase tracking-wider text-black/30 dark:text-white/25">
              or
            </span>
            <div className="flex-1 h-px bg-black/8 dark:bg-white/7" />
          </div>

          <div className="w-full flex items-center justify-center gap-10">
            <button className="px-5 py-3 bg-[#0C65D2] text-white font-mono text-sm hover:bg-[#0a52b0] hover:rounded-lg transition-all duration-500 cursor-pointer flex items-center gap-2 group">
              <Image
                src={"/GoogleLogo.svg"}
                width={20}
                height={20}
                loading="eager"
                alt="Google Logo"
              />
              Google
              <MoveRight
                size={15}
                className="group-hover:translate-x-0.5 transition-transform duration-500"
              />
            </button>
            <button className="px-5 py-3 bg-[#0d1117] text-white font-mono text-sm hover:bg-[#161b22] hover:rounded-lg transition-all duration-500 cursor-pointer flex items-center gap-2 group border border-[#30363d]">
              <Image
                src={"/GithubLogo-dark.svg"}
                width={20}
                height={20}
                loading="eager"
                alt="Github Logo"
              />
              Github
              <MoveRight
                size={15}
                className="group-hover:translate-x-0.5 transition-transform duration-500"
              />
            </button>
          </div>

          <div className="w-full flex items-center justify-center-safe">
            <h1 className="text-sm text-black/50 dark:text-white/50 font-semibold tracking-wide transition-colors duration-500 flex items-center gap-2">
              Already have an account?{" "}
              <span>
                <a
                  className="text-sm text-profit flex items-center gap-0.5 hover:underline cursor-pointer group transition-colors duration-500 text-[#0C65D2]"
                  onClick={() => redirect("/auth/login")}
                >
                  Log In
                  <ArrowUpRight
                    size={12}
                    className="group-hover:-translate-y-0.5 transition-transform duration-300"
                  />
                </a>
              </span>
            </h1>
          </div>
        </div>
      </section>
    </div>
  );
};

export default page;
