import { createClient } from "@/app/lib/supabase/server";
import { redirect } from "next/navigation";
import Sidebar from "@/app/components/dashboard/Sidebar";
import DashboardHeader from "@/app/components/dashboard/DashboardHeader";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) redirect("/auth/login");

  const { data: profile } = await supabase
    .from("profiles")
    .select("full_name, college, stream, year_of_study, cgpa, is_admin")
    .eq("id", user.id)
    .single();

  const firstName = profile?.full_name?.split(" ")[0] ?? "Student";

  return (
    <div className="min-h-screen bg-white dark:bg-[#08090E] transition-all duration-500 text-gray-900 dark:text-[#F0F4FF] flex">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 pl-60">
        <DashboardHeader userName={firstName} />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}