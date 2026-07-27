import { getServerApiBase } from '../../../../lib/api';

export async function POST(request: Request) {
  try {
    const upstream = await fetch(`${getServerApiBase()}/newsletter/subscribe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: await request.text(),
      cache: 'no-store',
    });

    return new Response(await upstream.text(), {
      status: upstream.status,
      headers: {
        'Content-Type': upstream.headers.get('content-type') || 'application/json',
      },
    });
  } catch {
    return Response.json(
      { detail: 'API temporariamente indisponível.' },
      { status: 502 },
    );
  }
}
