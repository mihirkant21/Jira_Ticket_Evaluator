import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // We use process.env.NEXT_PUBLIC_API_URL or a dedicated server env variable for the backend
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // Forward the request to the python backend
    const response = await fetch(`${API_BASE_URL}/api/evaluate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'bypass-tunnel-reminder': 'true', // Needed if using localtunnel (loca.lt)
        'ngrok-skip-browser-warning': 'true' // Needed if using ngrok
      },
      body: JSON.stringify(body),
      cache: 'no-store'
    });

    const text = await response.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch (e) {
      console.error('Failed to parse backend response as JSON:', text.substring(0, 500));
      return NextResponse.json(
        { detail: `Backend returned non-JSON response: ${text.substring(0, 100)}...` },
        { status: response.status || 502 }
      );
    }

    if (!response.ok) {
      return NextResponse.json(
        { detail: data.detail || 'Evaluation failed on backend' },
        { status: response.status }
      );
    }

    return NextResponse.json(data);
  } catch (error: any) {
    console.error('API Route Error:', error);
    return NextResponse.json(
      { detail: error.message || 'Internal Server Error proxying to backend' },
      { status: 500 }
    );
  }
}
