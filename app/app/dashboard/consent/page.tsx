export const runtime = "edge";

import { createClient } from "@/app/lib/supabase/server";
import { redirect } from "next/navigation";
import ConsentManager from "@/app/components/dashboard/ConsentManager";

export default async function ConsentPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/auth/login");

  return <ConsentManager userId={user.id} userEmail={user.email ?? ""} />;
}
