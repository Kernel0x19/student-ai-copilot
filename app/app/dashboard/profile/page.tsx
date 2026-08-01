export const runtime = "edge";

import { createClient } from "@/app/lib/supabase/server";
import { redirect } from "next/navigation";
import ProfileForm from "@/app/components/dashboard/ProfileForm";
import { getProfile } from "@/app/lib/api";

export default async function ProfilePage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/auth/login");

  let profile = null;
  try {
    profile = await getProfile(user.id, user.email ?? "");
  } catch {
    profile = null;
  }

  return <ProfileForm initial={profile} userId={user.id} userEmail={user.email ?? ""} />;
}
