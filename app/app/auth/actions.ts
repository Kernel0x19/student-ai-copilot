"use server";

import { createClient } from "@/app/lib/supabase/client"; 

export async function login(formData: FormData) {
  const supabase = await createClient();

  const email = formData.get("email") as string;
  const password = formData.get("password") as string;
  const remember = formData.get("remember") === "true";

  const { error } = await supabase.auth.signInWithPassword({ email, password });

  if (error) {
    return { error: error.message };
  }

  if (!remember) {
    const { cookies } = await import("next/headers");
    const cookieStore = await cookies();
    cookieStore.set("session_expiry", Date.now().toString(), {
      maxAge: 60 * 60 * 24,
      httpOnly: true,
      path: "/",
    });
  }

  return { redirectTo: "/dashboard" };
}

export async function signup(formData: FormData) {
  const supabase = await createClient();

  const email = formData.get("email") as string;
  const password = formData.get("password") as string;
  const full_name = formData.get("full_name") as string;

  const { data: existing } = await supabase
    .from("profiles")
    .select("id")
    .eq("email", email)
    .single();

  if (existing) {
    return {
      error: "An account with this email already exists. Please log in instead.",
    };
  }

  const { error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        full_name,
        college: formData.get("college"),
        stream: formData.get("stream"),
        year_of_study: formData.get("year"),
        cgpa: formData.get("cgpa"),
        phone: formData.get("phone"),
      },
    },
  });

  if (error) {
    return { error: error.message };
  }

  return { redirectTo: "/dashboard" };
}

export async function logout() {
  const supabase = await createClient();
  await supabase.auth.signOut();
  return { redirectTo: "/auth/login" };
}

export async function signInWithOAuth(provider: "google" | "github") {
  const supabase = await createClient();

  const { data, error } = await supabase.auth.signInWithOAuth({
    provider,
    options: {
      redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/auth/callback`,
    },
  });

  if (error) {
    return { error: error.message };
  }

  return { redirectTo: data.url };
}