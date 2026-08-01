export const runtime = "edge";

import { createClient } from "@/app/lib/supabase/server";
import { redirect } from "next/navigation";
import { getNotifications } from "@/app/lib/api";
import { Bell } from "lucide-react";
import NotificationPrefs from "@/app/components/dashboard/NotificationPrefs";

export default async function NotificationsPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/auth/login");

  let notifications: Awaited<ReturnType<typeof getNotifications>> = [];
  try {
    notifications = await getNotifications(user.id, user.email ?? "");
  } catch {
    notifications = [];
  }

  return (
    <div className="flex flex-col gap-8 max-w-2xl">
      {/* Notifications List */}
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="font-syne text-xl font-bold">Notifications</h1>
          <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] mt-1">
            Deadline reminders and application updates
          </p>
        </div>

        {notifications.length === 0 ? (
          <div className="flex flex-col items-center py-16 gap-3 border border-black/10 dark:border-white/8">
            <Bell size={24} className="text-gray-300" />
            <p className="font-mono text-[12px] text-gray-400">No notifications yet</p>
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {notifications.map((n) => (
              <div
                key={n.id}
                className={`border border-black/10 dark:border-white/8 p-4 ${!n.read ? "bg-[#0C65D2]/5 border-[#0C65D2]/20" : "bg-gray-50 dark:bg-[#0F1117]"}`}
              >
                <p className="font-mono text-[13px] font-bold text-gray-900 dark:text-[#F0F4FF]">{n.title}</p>
                <p className="font-mono text-[12px] text-gray-500 mt-1">{n.body}</p>
                <p className="font-mono text-[10px] text-gray-400 mt-2">
                  {new Date(n.created_at).toLocaleString()} · {n.channel}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Preferences Section */}
      <div className="border-t border-black/10 dark:border-white/8 pt-6">
        <NotificationPrefs userId={user.id} userEmail={user.email ?? ""} />
      </div>
    </div>
  );
}
