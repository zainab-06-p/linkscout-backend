import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:5000';

export async function GET(request: NextRequest) {
  try {
    const response = await fetch(`${BACKEND_URL}/health`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Backend unhealthy: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json({
      ...data,
      web_interface: 'healthy',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    return NextResponse.json(
      { 
        status: 'unhealthy',
        web_interface: 'healthy',
        backend: 'offline',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      },
      { status: 503 }
    );
  }
}
