import { analyze, MAX_BYTES } from '../../../lib/analyze.js';

export const runtime = 'nodejs';

export async function POST(request) {
  try {
    // Bound the streamed body, including requests without Content-Length.
    const reader = request.body?.getReader();
    if (!reader) return Response.json({ error: 'A scan is required.' }, { status: 400 });
    const chunks = [];
    let size = 0;
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > MAX_BYTES * 2) {
        await reader.cancel();
        return Response.json({ error: 'Request too large. Use a scan under 256 KB.' }, { status: 413 });
      }
      chunks.push(value);
    }
    const body = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    return Response.json(analyze(body.raw), { headers: { 'Cache-Control': 'no-store' } });
  } catch (error) {
    return Response.json({ error: error instanceof SyntaxError ? 'Invalid JSON request.' : error.message }, { status: 400 });
  }
}
