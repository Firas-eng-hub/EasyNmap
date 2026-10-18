import { analyze, demos } from '../../../lib/analyze.js';

export const dynamic = 'force-dynamic';

export async function GET(request) {
  const profile = new URL(request.url).searchParams.get('profile') || 'quick';
  if (!Object.hasOwn(demos, profile)) return Response.json({ error: 'Choose quick, service, or sweep.' }, { status: 400 });
  const raw = demos[profile];
  return Response.json({ raw, ...analyze(raw), source: 'demo' }, { headers: { 'Cache-Control': 'no-store' } });
}
