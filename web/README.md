# EasyNmap web playground

A Next.js app for Vercel with an interactive terminal demo and real server-side analysis of uploaded Nmap normal text output. The Python app stays in the repository root; the web app lives in `web/`.

**Live app: [easynmap-showcase-f8ebc9.vercel.app](https://easynmap-showcase-f8ebc9.vercel.app)**

## Develop

Requires Node.js 20.9+ (Node 24 is verified).

```bash
cd web
npm ci
npm run dev
```

If the machine's default npm cache is not writable, add `--cache /workspace/.npm-cache` to `npm ci`.

```bash
npm test
npm run build
npm start
```

## Deploy on Vercel

1. Push the `web/` directory and its lockfile to your GitHub repository.
2. Import `Firas-eng-hub/EasyNmap` as a Vercel project.
3. Set **Root Directory** to **`web`** and **Framework Preset** to **Next.js**.
4. Keep the default build command (`npm run build`), installation command (`npm install`), and output directory. Deploy.

No environment variables, database, API key, or separate server are required. Next.js route handlers deploy as Vercel functions. Do not enable static export: `/api/analyze` must execute on the server.

Alternatively, from `web/`, use an authenticated Vercel CLI:

```bash
npx vercel
# After reviewing the preview deployment:
npx vercel --prod
```

## What actually runs

- `GET /api/demo?profile=quick|service|sweep` parses a bundled sample on the server. The interface clearly labels these results as samples. Terminal commands demonstrate the Python app; they never start scans or execute shell commands.
- `POST /api/analyze` accepts JSON `{ "raw": "Nmap scan report for ..." }`. It parses each host, TCP/UDP port, state, service, and version, and returns counts, rule-based service guidance, and a Markdown report.
- Import normal text output generated using `nmap -oN scan.txt <target>`. Maximum scan size: 256 KB UTF-8. XML and grepable formats are not supported. Requests are streamed with a separate 512 KB body cap to allow JSON encoding overhead.
- Counts include explicit port rows only. Aggregated “not shown” ports do not count. Open/filtered ports are not treated as confirmed open. Guidance does not infer vulnerabilities from an open port or version number.
- Uploaded output is processed in memory for each request; this app does not persist scan contents or log them. Hosting infrastructure may retain request metadata under its own policies. Do not upload sensitive results to an instance you do not trust.
- Markdown export is generated from the analysis and downloaded in the browser.

Vercel does not run Nmap or the interactive Python TUI. Actual live scanning requires a separate runner with appropriate permissions and network access. The web app deliberately accepts scan output rather than arbitrary scan targets.

The original Python project's AI integration uses OpenRouter. This showcase uses deterministic service guidance and does not make AI calls.
