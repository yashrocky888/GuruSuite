import { NextResponse } from "next/server";

/**
 * Location Search Proxy Route
 * 
 * This route enforces the architectural law:
 * Browser → Next.js API Route → Guru API → Nominatim
 * 
 * No direct browser calls to Guru API or external services are allowed.
 */
export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const q = searchParams.get("q");
  const startedAt = Date.now();

  if (!q || q.length < 3) {
    // MANDATORY: Always return JSON array, never empty object
    return NextResponse.json([], { status: 200 });
  }

  try {
    const guruApiUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.replace('/api/v1', '') || 
                      process.env.NEXT_PUBLIC_GURU_API_URL || 
                      process.env.NEXT_PUBLIC_API_URL || 
                      'https://guru-api-660206747784.asia-south1.run.app';
    
    const provider = "guru-api:/api/v1/location/search";

    const response = await fetch(
      `${guruApiUrl}/api/v1/location/search?q=${encodeURIComponent(q)}`,
      {
        cache: "no-store",
        headers: {
          'Accept': 'application/json',
        },
        signal: AbortSignal.timeout(15000), // 15 second timeout
      }
    );

    if (!response.ok) {
      // MANDATORY: Always return JSON array on error (empty array for UX)
      // Log error but don't expose it to user
      const durationMs = Date.now() - startedAt;
      console.warn("⚠️ Location search API non-OK response", {
        provider,
        query: q,
        status: response.status,
        statusText: response.statusText,
        durationMs,
      });
      return NextResponse.json([], { status: 200 });
    }

    // MANDATORY: Normalize response - ensure it's JSON
    const contentType = response.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
      console.error("❌ Location search: Invalid content-type:", contentType);
      return NextResponse.json([], { status: 200 });
    }

    const data = await response.json();
    
    // MANDATORY: Ensure data is an array
    if (!Array.isArray(data)) {
      console.error("❌ Location search: Response is not an array:", typeof data);
      return NextResponse.json([], { status: 200 });
    }
    
    // Return normalized array (empty array is valid - no results found)
    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    // MANDATORY: Always return JSON array, never throw or return empty object
    const errorMessage = error?.message || String(error) || 'Unknown error';
    const durationMs = Date.now() - startedAt;
    const provider = "guru-api:/api/v1/location/search";
    const isTimeout =
      error?.name === "TimeoutError" ||
      error?.code === "ETIMEDOUT" ||
      /timeout/i.test(errorMessage || "");

    console.warn("⚠️ Guru Web Location Proxy Warning:", {
      message: errorMessage,
      name: error?.name || 'Unknown',
      type: typeof error,
      provider,
      query: q,
      durationMs,
      isTimeout,
    });
    // Return empty array for graceful UX (no results found)
    return NextResponse.json([], { status: 200 });
  }
}

