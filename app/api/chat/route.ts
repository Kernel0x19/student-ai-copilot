import { NextResponse } from "next/server";

/**
 * Compatibility proxy for chat clients that use the Next.js endpoint.
 * The FastAPI service owns profile lookup, eligibility-aware RAG, and secure
 * document processing, so this route deliberately contains no parallel logic.
 */
export async function POST(request: Request) {
  const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const contentType = request.headers.get("content-type") || "application/json";
  const isUpload = contentType.startsWith("multipart/form-data");
  const backendResponse = await fetch(
    `${apiBase}/api/v1/chat/${isUpload ? "upload" : ""}`,
    {
      method: "POST",
      headers: {
        "Content-Type": contentType,
        "X-User-Id": request.headers.get("x-user-id") || "",
        "X-User-Email": request.headers.get("x-user-email") || "",
        ...(request.headers.get("authorization")
          ? { Authorization: request.headers.get("authorization")! }
          : {}),
      },
      body: await request.arrayBuffer(),
    }
  );
  const payload = await backendResponse.json();
  return NextResponse.json(payload, { status: backendResponse.status });
}
