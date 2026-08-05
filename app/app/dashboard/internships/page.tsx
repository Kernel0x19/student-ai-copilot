import { createClient } from "@/app/lib/supabase/server";
import { redirect } from "next/navigation";
import InternshipsClient from "@/app/components/dashboard/InternshipsClient";

export const dynamic = "force-dynamic";

export default async function InternshipsPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/auth/login");

  // Pass only auth identifiers — the client fetches its own data on mount
  // so results are always fresh and never served from a stale server cache.
  return (
    <InternshipsClient
      userId={user.id}
      userEmail={user.email ?? ""}
    />
  );
}
