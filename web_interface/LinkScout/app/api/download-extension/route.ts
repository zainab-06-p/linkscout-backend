import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:5000';

export async function GET(request: NextRequest) {
  try {
    console.log('📦 Requesting extension from backend...');
    
    // Forward request to Python backend
    const response = await fetch(`${BACKEND_URL}/download-extension`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status} ${response.statusText}`);
    }

    // Get the ZIP file from backend
    const buffer = await response.arrayBuffer();
    
    console.log(`✅ Extension received from backend (${buffer.byteLength} bytes)`);

    // Return the ZIP file
    return new NextResponse(buffer, {
      status: 200,
      headers: {
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename="LinkScout-Extension.zip"',
        'Content-Length': buffer.byteLength.toString(),
      },
    });

  } catch (error) {
    console.error('❌ Extension download error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to download extension',
        message: error instanceof Error ? error.message : 'Unknown error',
        hint: 'Please ensure the backend server is running on port 5000'
      },
      { status: 500 }
    );
  }
}
