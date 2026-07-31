export const runtime = "edge";

import { createClient } from "@/app/lib/supabase/server";
import { redirect } from "next/navigation";
import ScholarshipsClient from "@/app/components/dashboard/ScholarshipsClient";
import { getRecommendations, type MatchResult } from "@/app/lib/api";

export default async function ScholarshipsPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/auth/login");

  let matches: MatchResult[] = [];
  try {
    const rec = await getRecommendations(user.id, user.email ?? "");
    matches = rec.matches;
  } catch {
    matches = [];
  }

  return (
    <ScholarshipsClient
      initialMatches={matches}
      userId={user.id}
      userEmail={user.email ?? ""}
    />
  );
}
