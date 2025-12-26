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

  if (!q || q.length < 3) {
    // MANDATORY: Always return JSON array, never empty object
    return NextResponse.json([], { status: 200 });
  }

  try {
    const guruApiUrl = process.env.NEXT_PUBLIC_GURU_API_URL || 
                      process.env.NEXT_PUBLIC_API_URL || 
                      'https://guru-api-660206747784.asia-south1.run.app';
    
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
      console.error(`❌ Location search API error: ${response.status} ${response.statusText}`);
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
    console.error("❌ Guru Web Location Proxy Error:", {
      message: errorMessage,
      name: error?.name || 'Unknown',
      type: typeof error,
    });
    // Return empty array for graceful UX (no results found)
    return NextResponse.json([], { status: 200 });
  }
}

