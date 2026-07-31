export const runtime = "edge";

import { createClient } from "@/app/lib/supabase/server";
import { redirect } from "next/navigation";
import DocumentUpload from "@/app/components/dashboard/DocumentUpload";

export default async function DocumentsPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/auth/login");

  return <DocumentUpload userId={user.id} />;
}
