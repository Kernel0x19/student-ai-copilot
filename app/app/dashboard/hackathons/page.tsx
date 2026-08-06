import { createClient } from "@/app/lib/supabase/server";
import { redirect } from "next/navigation";
import HackathonsClient from "@/app/components/dashboard/HackathonsClient";

export const dynamic = "force-dynamic";

export default async function HackathonsPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/auth/login");

  // Pass only auth identifiers — the client fetches its own data on mount
  // so results are always fresh and never served from a stale server cache.
  return <HackathonsClient userId={user.id} userEmail={user.email ?? ""} />;
}
