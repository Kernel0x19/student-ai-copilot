"use client";
import Navbar from "@/app/components/Navbar";
import TerminalCard from "@/app/components/home/TerminalCard";
import { ArrowUpRight, MoveRight } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { signup, signInWithOAuth } from "@/app/auth/actions";

const Page = () => {
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState<"google" | "github" | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    college: "",
    stream: "",
    year: "",
  });

  const update = (k: string, v: string) => setForm((p) => ({ ...p, [k]: v }));

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const fd = new FormData();
    fd.append("full_name", `${form.first_name} ${form.last_name}`.trim());
    fd.append("email", form.email);
    fd.append("password", form.password);
    fd.append("college", form.college);
    fd.append("stream", form.stream);
    fd.append("year", form.year);
    const result = await signup(fd);
    if (result?.error) {
      setError(result.error);
      setLoading(false);
    }
    localStorage.setItem('session_login_time', Date.now().toString())
  };

  const handleOAuth = async (provider: "google" | "github") => {
    setOauthLoading(provider);
    setError(null);
    const result = await signInWithOAuth(provider);
    if (result?.error) {
      setError(result.error);
      setOauthLoading(null);
    }
    localStorage.setItem('session_login_time', Date.now().toString())
  };

  return (
    <div className="min-h-screen bg-white dark:bg-[#08090E] text-gray-900 dark:text-[#F0F4FF] transition-colors duration-500">
      <Navbar isAuth={true} />
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 pt-10 sm:pt-12 lg:pt-15 pb-12 sm:pb-14 lg:pb-16 grid grid-cols-1 lg:grid-cols-2 gap-10 sm:gap-14 lg:gap-20 xl:gap-25 items-center">
        <div className="flex flex-col gap-3">
          <h1 className="font-syne text-3xl sm:text-4xl lg:text-5xl xl:text-[3.2rem] font-extrabold leading-[1.1] tracking-tight text-gray-900 dark:text-[#F0F4FF] mb-3 sm:mb-5 transition-all duration-500">
            Your entire academic
            <br />
            future, <span className="text-[#0C65D2]">co-piloted.</span>
          </h1>
          <p className="text-gray-500 dark:text-[#6B7280] text-sm sm:text-base leading-relaxed mb-6 sm:mb-8 max-w-xl transition-all duration-500">
            Scholarships, eligibility checks, document analysis, and career
            roadmaps — handled by a multi-agent AI system built for Indian
            students.
          </p>
          <TerminalCard />
        </div>

        <form
          onSubmit={handleSignup}
          className="flex flex-col gap-4 sm:gap-5 p-5 sm:p-6 lg:p-8 shadow-xl border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] overflow-hidden transition-all duration-500"
        >
          <div className="flex flex-col gap-2">
            <h1 className="text-xl sm:text-2xl font-bold">
              Create your <span className="text-[#0C65D2]">Account</span>
            </h1>
          </div>

          {error && (
            <div className="px-4 py-3 border border-red-500/30 bg-red-500/10 font-mono text-[12px] text-red-500 rounded-lg">
              {error}
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
            <div className="flex flex-col gap-1.5 flex-1">
              <label className="text-sm sm:text-base text-black/50 dark:text-white/50 font-semibold uppercase tracking-wide transition-colors duration-500">
                First Name
              </label>
              <input
                type="text"
                value={form.first_name}
                onChange={(e) => update("first_name", e.target.value)}
                placeholder="Prathamesh"
                required
                className="px-3.5 py-2.5 w-full rounded-lg text-sm border outline-none transition-colors duration-500 bg-black/8 border-black/15 text-black placeholder-black/35 focus:border-black/25 focus:bg-black/10 dark:bg-white/12 dark:border-white/20 dark:text-white dark:placeholder-white/30 dark:focus:border-white/40 dark:focus:bg-white/15"
              />
            </div>
            <div className="flex flex-col gap-1.5 flex-1">
              <label className="text-sm sm:text-base text-black/50 dark:text-white/50 font-semibold uppercase tracking-wide transition-colors duration-500">
                Last Name
              </label>
              <input
                type="text"
                value={form.last_name}
                onChange={(e) => update("last_name", e.target.value)}
                placeholder="Kulkarni"
                required
                className="px-3.5 py-2.5 w-full rounded-lg text-sm border outline-none transition-colors duration-500 bg-black/8 border-black/15 text-black placeholder-black/35 focus:border-black/25 focus:bg-black/10 dark:bg-white/12 dark:border-white/20 dark:text-white dark:placeholder-white/30 dark:focus:border-white/40 dark:focus:bg-white/15"
              />
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-sm sm:text-base text-black/50 dark:text-white/50 font-semibold uppercase tracking-wide transition-colors duration-500">
              Email
            </label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => update("email", e.target.value)}
              placeholder="you@example.com"
              required
              className="px-3.5 py-2.5 w-full rounded-lg text-sm border outline-none transition-colors duration-500 bg-black/8 border-black/15 text-black placeholder-black/35 focus:border-black/25 focus:bg-black/10 dark:bg-white/12 dark:border-white/20 dark:text-white dark:placeholder-white/30 dark:focus:border-white/40 dark:focus:bg-white/15"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-sm sm:text-base text-black/50 dark:text-white/50 font-semibold uppercase tracking-wide transition-colors duration-500">
              Password
            </label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => update("password", e.target.value)}
              placeholder="Min. 8 characters"
              required
              minLength={8}
              className="px-3.5 py-2.5 w-full rounded-lg text-sm border outline-none transition-colors duration-500 bg-black/8 border-black/15 text-black placeholder-black/35 focus:border-black/25 focus:bg-black/10 dark:bg-white/12 dark:border-white/20 dark:text-white dark:placeholder-white/30 dark:focus:border-white/40 dark:focus:bg-white/15"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-sm sm:text-base text-black/50 dark:text-white/50 font-semibold uppercase tracking-wide transition-colors duration-500">
              College / University
            </label>
            <input
              type="text"
              value={form.college}
              onChange={(e) => update("college", e.target.value)}
              placeholder="Vishwakarma Institute of Technology, Pune"
              className="px-3.5 py-2.5 w-full rounded-lg text-sm border outline-none transition-colors duration-500 bg-black/8 border-black/15 text-black placeholder-black/35 focus:border-black/25 focus:bg-black/10 dark:bg-white/12 dark:border-white/20 dark:text-white dark:placeholder-white/30 dark:focus:border-white/40 dark:focus:bg-white/15"
            />
          </div>

          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
            <div className="flex flex-col gap-1.5 flex-1">
              <label className="text-sm sm:text-base text-black/50 dark:text-white/50 font-semibold uppercase tracking-wide transition-colors duration-500">
                Stream
              </label>
              <select
                value={form.stream}
                onChange={(e) => update("stream", e.target.value)}
                className="px-3.5 py-2.5 w-full rounded-lg text-sm border outline-none transition-colors duration-500 bg-black/8 border-black/15 text-black/70 focus:border-black/25 focus:bg-black/10 dark:bg-white/12 dark:border-white/20 dark:text-white/70 dark:focus:border-white/40 dark:focus:bg-white/15 appearance-none cursor-pointer"
              >
                <option value="">Select stream</option>
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
              <label className="text-sm sm:text-base text-black/50 dark:text-white/50 font-semibold uppercase tracking-wide transition-colors duration-500">
                Year
              </label>
              <select
                value={form.year}
                onChange={(e) => update("year", e.target.value)}
                className="px-3.5 py-2.5 w-full rounded-lg text-sm border outline-none transition-colors duration-500 bg-black/8 border-black/15 text-black/70 focus:border-black/25 focus:bg-black/10 dark:bg-white/12 dark:border-white/20 dark:text-white/70 dark:focus:border-white/40 dark:focus:bg-white/15 appearance-none cursor-pointer"
              >
                <option value="">Select year</option>
                <option value="1st Year">1st year</option>
                <option value="2nd Year">2nd year</option>
                <option value="3rd Year">3rd year</option>
                <option value="4th Year">4th year</option>
              </select>
            </div>
          </div>

          <div className="w-full flex items-center justify-center">
            <button
              type="submit"
              disabled={loading || !!oauthLoading}
              className="w-full sm:w-auto px-5 py-3 bg-[#0C65D2] text-white font-mono text-sm hover:bg-[#0a52b0] hover:rounded-lg transition-all duration-500 cursor-pointer flex items-center justify-center gap-2 group disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? (
                <Spinner />
              ) : (
                <>
                  Create Account
                  <MoveRight
                    size={15}
                    className="group-hover:translate-x-0.5 transition-transform duration-500"
                  />
                </>
              )}
            </button>
          </div>

          <div className="flex items-center gap-2.5">
            <div className="flex-1 h-px bg-black/8 dark:bg-white/7" />
            <span className="text-[11px] uppercase tracking-wider text-black/30 dark:text-white/25">
              or
            </span>
            <div className="flex-1 h-px bg-black/8 dark:bg-white/7" />
          </div>

          <div className="w-full flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-10">
            <button
              type="button"
              onClick={() => handleOAuth("google")}
              disabled={!!oauthLoading || loading}
              className="w-full sm:w-auto px-5 py-3 bg-[#0C65D2] text-white font-mono text-sm hover:bg-[#0a52b0] hover:rounded-lg transition-all duration-500 cursor-pointer flex items-center justify-center gap-2 group disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {oauthLoading === "google" ? (
                <Spinner />
              ) : (
                <Image
                  src="/GoogleLogo.svg"
                  width={20}
                  height={20}
                  loading="eager"
                  alt="Google Logo"
                />
              )}
              Google
              <MoveRight
                size={15}
                className="group-hover:translate-x-0.5 transition-transform duration-500"
              />
            </button>
            <button
              type="button"
              onClick={() => handleOAuth("github")}
              disabled={!!oauthLoading || loading}
              className="w-full sm:w-auto px-5 py-3 bg-[#0d1117] text-white font-mono text-sm hover:bg-[#161b22] hover:rounded-lg transition-all duration-500 cursor-pointer flex items-center justify-center gap-2 group border border-[#30363d] disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {oauthLoading === "github" ? (
                <Spinner />
              ) : (
                <Image
                  src="/GithubLogo-dark.svg"
                  width={20}
                  height={20}
                  loading="eager"
                  alt="Github Logo"
                />
              )}
              Github
              <MoveRight
                size={15}
                className="group-hover:translate-x-0.5 transition-transform duration-500"
              />
            </button>
          </div>

          <div className="w-full flex items-center justify-center">
            <p className="text-xs sm:text-sm text-black/50 dark:text-white/50 font-semibold tracking-wide transition-colors duration-500 flex items-center gap-2">
              Already have an account?{" "}
              <Link
                href="/auth/login"
                className="text-xs sm:text-sm text-[#0C65D2] flex items-center gap-0.5 hover:underline cursor-pointer group transition-colors duration-500"
              >
                Log In
                <ArrowUpRight
                  size={12}
                  className="group-hover:-translate-y-0.5 transition-transform duration-300"
                />
              </Link>
            </p>
          </div>
        </form>
      </section>
    </div>
  );
};

export default Page;

function Spinner() {
  return (
    <svg
      className="animate-spin h-4 w-4 text-white"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v8z"
      />
    </svg>
  );
}
