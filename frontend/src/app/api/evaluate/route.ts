import { NextResponse } from 'next/server';

export const maxDuration = 60; // Max allowed duration for Vercel Hobby
export const dynamic = 'force-dynamic'; // Prevent static caching

export async function POST(request: Request) {
  const requestId = Math.random().toString(36).substring(7);
  console.log(`[${requestId}] API Route: Received evaluation request`);

  try {
    const body = await request.json();
    console.log(`[${requestId}] API Route: Request body:`, JSON.stringify(body));
    
    // We use process.env.NEXT_PUBLIC_API_URL or a dedicated server env variable for the backend
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    console.log(`[${requestId}] API Route: Using API_BASE_URL: ${API_BASE_URL}`);

    if (!API_BASE_URL.startsWith('http')) {
      console.error(`[${requestId}] API Route: Invalid API_BASE_URL!`);
    }
    
    console.log(`[${requestId}] API Route: Fetching from ${API_BASE_URL}/api/evaluate...`);

    // Forward the request to the python backend
    let response;
    try {
      response = await fetch(`${API_BASE_URL}/api/evaluate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'bypass-tunnel-reminder': 'true', // Needed if using localtunnel (loca.lt)
          'ngrok-skip-browser-warning': 'true' // Needed if using ngrok
        },
        body: JSON.stringify(body),
        cache: 'no-store'
      });
    } catch (fetchError: any) {
      console.error(`[${requestId}] API Route: Fetch failed!`, fetchError);
      return NextResponse.json(
        { detail: `Failed to connect to backend: ${fetchError.message}` },
        { status: 503 }
      );
    }

    console.log(`[${requestId}] API Route: Backend responded with status: ${response.status}`);

    const text = await response.text();
    console.log(`[${requestId}] API Route: Raw backend response (first 200 chars): ${text.substring(0, 200)}`);

    let data;
    try {
      data = JSON.parse(text);
    } catch (e) {
      console.error(`[${requestId}] API Route: Failed to parse backend response as JSON:`, text.substring(0, 500));
      return NextResponse.json(
        { detail: `Backend returned non-JSON response: ${text.substring(0, 100)}...` },
        { status: response.status || 502 }
      );
    }

    if (!response.ok) {
      console.warn(`[${requestId}] API Route: Backend returned error status`, response.status);
      return NextResponse.json(
        { detail: data.detail || 'Evaluation failed on backend' },
        { status: response.status }
      );
    }

    console.log(`[${requestId}] API Route: Successfully processed evaluation`);
    return NextResponse.json(data);
  } catch (error: any) {
    console.error(`[${requestId}] API Route Error:`, error);
    return NextResponse.json(
      { detail: error.message || 'Internal Server Error proxying to backend' },
      { status: 500 }
    );
  }
}
