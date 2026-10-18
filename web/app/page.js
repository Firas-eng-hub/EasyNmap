'use client';

import { useEffect, useRef, useState } from 'react';
import { ArrowDownToLine, ArrowRight, ArrowUpRight, Check, CheckCheck, ChevronRight, CircleHelp, Code2, Copy, FileText, Github, Globe2, Layers, LoaderCircle, Network, Play, Plus, Radar, ShieldCheck, Terminal, Upload, X } from 'lucide-react';

const repository = 'https://github.com/Firas-eng-hub/EasyNmap';
const profiles = [
  { id: 'quick', name: 'Quick scan', flag: '-T4 -F', description: 'The essentials. Top 100 ports.', command: '/scan quick' },
  { id: 'service', name: 'Service detection', flag: '-sV', description: 'See what’s behind each port.', command: '/scan service' },
  { id: 'sweep', name: 'Host discovery', flag: '-sn', description: 'Find the hosts on a network.', command: '/sweep' },
];

export default function Home() {
  const [profile, setProfile] = useState('quick');
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [tab, setTab] = useState('ports');
  const [command, setCommand] = useState('');
  const [lines, setLines] = useState([{ kind: 'muted', text: 'EasyNmap v1.0 · interactive demo' }, { kind: 'muted', text: 'Type /help to explore, or run a scan below.' }]);
  const [upload, setUpload] = useState(false);
  const [raw, setRaw] = useState('');
  const [copied, setCopied] = useState(false);
  const [source, setSource] = useState('demo');
  const [guide, setGuide] = useState(false);
  const terminalEnd = useRef(null);
  const input = useRef(null);
  useEffect(() => {
    const body = terminalEnd.current?.parentElement;
    if (body) body.scrollTop = body.scrollHeight;
  }, [lines]);
  useEffect(() => {
    const close = e => { if (e.key === 'Escape') { setUpload(false); setGuide(false); } };
    document.addEventListener('keydown', close);
    return () => document.removeEventListener('keydown', close);
  }, []);

  async function run(id = profile) {
    if (busy) return;
    setBusy(true); setError(''); setProfile(id);
    const selected = profiles.find(p => p.id === id);
    setLines(prev => [...prev, { kind: 'command', text: selected.command + ' 192.0.2.10' }, { kind: 'muted', text: 'Loading sample output · no network scan is performed…' }]);
    try {
      const response = await fetch(`/api/demo?profile=${id}`, { cache: 'no-store' });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Could not load demo.');
      setResult(data); setSource('demo'); setTab(id === 'sweep' ? 'hosts' : 'ports');
      setLines(prev => [...prev, { kind: 'output', text: data.raw }, { kind: 'success', text: `✓ Complete. ${data.summary.hosts} host(s), ${data.summary.open} explicitly open port(s).` }]);
    } catch (e) { setError(e.message); setLines(prev => [...prev, { kind: 'error', text: e.message }]); }
    finally { setBusy(false); }
  }

  function submit(e) {
    e.preventDefault();
    const cmd = command.trim(); setCommand('');
    if (!cmd || busy) return;
    if (cmd === '/clear') { setLines([]); return; }
    const id = cmd.startsWith('/scan service') ? 'service' : cmd.startsWith('/scan quick') ? 'quick' : cmd === '/sweep' ? 'sweep' : null;
    if (id) { run(id); return; }
    setLines(prev => [...prev, { kind: 'command', text: cmd }, { kind: 'muted', text: cmd === '/help' ? 'Available: /scan quick · /scan service · /sweep · /clear · /help\nDemo mode uses sample results. Use Import scan to analyze your own Nmap output.' : 'Unknown command. Type /help for supported demo commands.' }]);
  }

  async function analyzeUpload(e) {
    e.preventDefault(); setBusy(true); setError('');
    try {
      const response = await fetch('/api/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ raw }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Analysis failed.');
      setResult(data); setSource('upload'); setTab('ports'); setUpload(false);
      setLines(prev => [...prev, { kind: 'success', text: `✓ Imported scan analyzed on the server. ${data.summary.hosts} host(s), ${data.summary.open} open port(s).` }]);
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }

  async function fileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 262144) { setError('Choose a text file under 256 KB.'); return; }
    try { setRaw(await file.text()); setError(''); } catch { setError('Could not read this file. Try pasting its contents.'); }
  }

  function download() {
    const url = URL.createObjectURL(new Blob([result.report], { type: 'text/markdown' }));
    const a = document.createElement('a'); a.href = url; a.download = 'easynmap-report.md'; a.click(); URL.revokeObjectURL(url);
  }

  return <div className="app-shell">
    <aside className="sidebar">
      <a className="brand" href="/" aria-label="EasyNmap home"><span className="brand-icon"><Radar size={22}/></span>easy<span>nmap</span><span className="brand-dot">®</span></a>
      <div className="workspace-label">THE WORKSPACE <span>01</span></div>
      <nav aria-label="Main navigation">
        <button className="nav-item selected" onClick={() => document.getElementById('playground').scrollIntoView({ behavior: 'smooth' })}><Terminal size={17}/> Playground <span className="nav-count">01</span></button>
        <button className="nav-item" onClick={() => { setUpload(true); setError(''); }}><Upload size={17}/> Analyze a scan <Plus size={14} className="nav-end"/></button>
        <button className="nav-item" onClick={() => setGuide(true)}><FileText size={17}/> Getting started <ArrowUpRight size={14} className="nav-end"/></button>
      </nav>
      <div className="sidebar-note"><div className="mini-radar"><Radar size={27}/></div><h3>A little clarity.<br/>A lot of possibility.</h3><p>Network exploration,<br/>without the learning curve.</p><a href={repository} target="_blank" rel="noreferrer">Meet the project <ArrowUpRight size={14}/></a></div>
      <div className="sidebar-bottom"><span className="status-dot"/> Open source. Always.<a href={repository} target="_blank" rel="noreferrer" aria-label="GitHub repository"><Github size={17}/></a></div>
    </aside>

    <main>
      <header className="topbar"><div><span className="breadcrumb">Workspace</span><ChevronRight size={13}/><span>Playground</span></div><a href={repository} target="_blank" rel="noreferrer"><Github size={16}/> Star on GitHub <ArrowUpRight size={13}/></a></header>
      <div className="content">
        <section className="hero"><div className="eyebrow"><span className="tiny-square"/> LESS GUESSWORK. MORE UNDERSTANDING.</div><div className="hero-title"><h1>Your network.<br/><span>A little less mysterious.</span></h1><div className="hero-art" aria-hidden="true"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="orbit orbit-three"/><span className="orbit-center"><Radar size={33}/></span><i className="satellite one"/><i className="satellite two"/><span className="orbit-tag">hello, network.</span></div></div><p>Meet the friendlier side of Nmap. Explore a scan, understand the<br className="desktop-break"/> results, and find your footing. All from one terminal.</p><div className="hero-meta"><span><CheckCheck size={15}/> Beginner friendly</span><span><Code2 size={15}/> Built with Python</span><span><Globe2 size={15}/> Open source</span></div></section>

        <section id="playground" className="playground-section"><div className="section-heading"><div><h2>Take it for a spin <span className="pill">LIVE PLAYGROUND</span></h2><p>A real feel for the tool. A safe place to explore.</p></div><button className="button secondary" onClick={() => { setUpload(true); setError(''); }}><Upload size={15}/> Import scan</button></div>
          <div className="playground-grid"><div className="scan-controls"><div className="label-row"><span>01</span> CHOOSE YOUR SCAN</div><div className="scan-options">{profiles.map(p => <button key={p.id} className={`scan-option ${profile === p.id ? 'active' : ''}`} onClick={() => setProfile(p.id)} disabled={busy}><div className="scan-option-top"><span className="radio">{profile === p.id && <span/>}</span><strong>{p.name}</strong><code>{p.flag}</code></div><p>{p.description}</p></button>)}</div><div className="target-label"><span>TARGET</span><span className="demo-badge">DEMO HOST</span></div><div className="target-input"><Globe2 size={15}/><code>192.0.2.10</code><ShieldCheck size={15}/></div><button className="button primary run-button" disabled={busy} onClick={() => run()}>{busy ? <LoaderCircle size={16} className="spin"/> : <Play size={15} fill="currentColor"/>}{busy ? 'Processing…' : 'Run demo scan'}<ArrowRight size={16}/></button><p className="safe-note"><ShieldCheck size={12}/> Sample data. No external scans.</p></div>
            <div className="terminal"><div className="terminal-bar"><div className="window-dots"><i/><i/><i/></div><span>easynmap — playground</span><span className="terminal-live"><span/> DEMO</span></div><div className="terminal-body" aria-live="polite" aria-label="Terminal output">{lines.map((line, i) => <div key={i} className={`terminal-line ${line.kind}`}>{line.kind === 'command' && <span className="prompt">❯ </span>}{line.text}</div>)}{!result && lines.length === 2 && <div className="terminal-welcome"><span className="ascii">{'  ┌─ easy ──────────────────┐\n  │  n m a p   /  made easy │\n  └────────────────────────┘'}</span><p>Your first discovery starts here.</p><span>Choose a scan and hit run. We’ll take it from there.</span></div>}<div ref={terminalEnd}/></div><form className="terminal-input" onSubmit={submit}><span>❯</span><input ref={input} value={command} onChange={e => setCommand(e.target.value)} placeholder="Type /help for commands" aria-label="Terminal command" disabled={busy} autoComplete="off" spellCheck="false"/><button type="submit" aria-label="Run command" disabled={busy}><CornerEnter/></button></form><div className="terminal-footer"><span><span className="status-dot"/> {busy ? 'Processing' : 'Ready to explore'}</span><span>Sample output <span className="terminal-divider">/</span> v1.0.0</span></div></div>
          </div>
          {error && !upload && <div className="error-message" role="alert">{error}</div>}
        </section>

        <section className="results-section" aria-label="Scan results"><div className="section-heading"><div><h2>A clearer picture <span className="result-source">{result ? source === 'demo' ? 'SAMPLE RESULTS' : 'IMPORTED RESULTS' : 'YOUR RESULTS'}</span></h2><p>{result ? 'The details, translated into something useful.' : 'Run a demo or import a scan to see what’s out there.'}</p></div><button className="button text-button" disabled={!result} onClick={download}><ArrowDownToLine size={15}/> Export report</button></div><div className="stats-grid">{[{ label: 'HOSTS FOUND', value: result?.summary.hosts, icon: Network }, { label: 'OPEN PORTS', value: result?.summary.open, icon: Layers }, { label: 'SERVICES', value: result?.summary.services, icon: Globe2 }, { label: 'TO REVIEW', value: result?.summary.review, icon: ShieldCheck }].map(({ label, value, icon: Icon }) => <div className="stat" key={label}><div><span>{label}</span><Icon size={16}/></div><strong>{value ?? '—'}</strong><small>{label === 'TO REVIEW' ? 'Configuration guidance' : label === 'OPEN PORTS' ? 'Explicit open port rows' : label === 'HOSTS FOUND' ? 'In the scan output' : 'Unique open services'}</small></div>)}</div>
          <div className="results-panel"><div className="results-tabs" role="tablist" aria-label="Result views">{['ports', 'hosts', 'insights'].map(t => <button key={t} role="tab" aria-selected={tab === t} className={tab === t ? 'active' : ''} onClick={() => setTab(t)}>{t === 'ports' ? 'Port overview' : t === 'hosts' ? 'Discovered hosts' : 'What it means'}{t === 'ports' && result && <span>{result.ports.length}</span>}</button>)}<span className="results-time">{result ? `Scan time ${result.summary.duration}` : 'Awaiting your first scan'}</span></div>
          {!result ? <div className="empty-results"><Radar size={26}/><span>A little curiosity goes a long way.</span><p>Your scan results will appear here.</p></div> : tab === 'ports' ? result.ports.length ? <div className="table-scroll"><table><thead><tr><th>PORT / PROTOCOL</th><th>STATE</th><th>SERVICE</th><th>HOST</th><th>VERSION</th></tr></thead><tbody>{result.ports.map((p, i) => <tr key={i}><td className="port-number">{p.port}<span>/{p.protocol}</span></td><td><span className={`state ${p.state === 'open' ? 'open' : ''}`}><i/>{p.state}</span></td><td>{p.service}</td><td className="mono muted">{p.host}</td><td className="muted">{p.version || 'Not detected'}</td></tr>)}</tbody></table></div> : <div className="empty-results"><Network size={24}/><span>No explicit port rows in this scan.</span><p>Host discovery results are available in Discovered hosts.</p></div> : tab === 'hosts' ? <div className="host-list">{result.hosts.map((h, i) => <div key={i}><span className="host-icon"><Network size={18}/></span><div><strong>{h.name}</strong><p>{h.address}</p></div><span className="host-status">{h.status}</span></div>)}</div> : <div className="insights"><p className="insight-disclaimer">Rule-based guidance · An open port alone does not establish a vulnerability.</p>{result.insights.length ? result.insights.map((item, i) => <article key={i}><span className={item.attention ? 'insight-symbol attention' : 'insight-symbol'}><ShieldCheck size={18}/></span><div><h3>{item.title}<code>{item.host}:{item.port}</code></h3><p>{item.detail}</p></div></article>) : <p>No open services to review in this output.</p>}</div>}</div>
          <p className="results-footnote"><CircleHelp size={12}/> Counts reflect explicit port rows. Imported output is processed for this request and is not saved by the app.</p>
        </section>

        <section className="install-banner"><span className="install-icon"><Terminal size={23}/></span><div><h3>Like the view? Take the wheel.</h3><p>The full EasyNmap experience lives in your terminal.</p></div><button onClick={async () => { try { await navigator.clipboard.writeText('git clone https://github.com/Firas-eng-hub/EasyNmap.git'); setCopied(true); setTimeout(() => setCopied(false), 2000); } catch { setGuide(true); } }}><code>git clone …/EasyNmap.git</code>{copied ? <Check size={15}/> : <Copy size={15}/>}</button><a href={repository + '#installation'} target="_blank" rel="noreferrer">Get started <ArrowUpRight size={15}/></a></section>
        <footer><span><Radar size={14}/> Built for the curious. Made with EasyNmap.</span><span>Explore responsibly. Scan with permission. <a href={repository} target="_blank" rel="noreferrer">GitHub <ArrowUpRight size={12}/></a></span></footer>
      </div>
    </main>

    {(upload || guide) && <div className="modal-backdrop" onClick={() => { setUpload(false); setGuide(false); }}><section className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" onClick={e => e.stopPropagation()}><button className="close-modal" aria-label="Close dialog" onClick={() => { setUpload(false); setGuide(false); }}><X size={20}/></button>{upload ? <form onSubmit={analyzeUpload}><span className="eyebrow">BRING YOUR OWN DISCOVERY</span><h2 id="modal-title">Make sense of a scan.</h2><p>Upload or paste normal Nmap text output. Analysis runs on the server; no network scan is started.</p><label className="file-picker"><Upload size={19}/><span>Choose a .txt or .nmap file <small>Up to 256 KB · normal text format</small></span><input type="file" accept=".txt,.nmap,text/plain" onChange={fileChange}/></label><label className="textarea-label" htmlFor="scan-output">Or paste your output</label><textarea autoFocus id="scan-output" value={raw} onChange={e => setRaw(e.target.value)} placeholder={'Nmap scan report for 192.0.2.10\nHost is up…\nPORT   STATE SERVICE\n22/tcp open  ssh'} required/><p className="format-help">Generate compatible output: <code>nmap -oN scan.txt &lt;target&gt;</code>. Only upload results you’re comfortable sending to this app.</p>{error && <div className="error-message" role="alert">{error}</div>}<button className="button primary" disabled={busy || !raw.trim()}>{busy ? <LoaderCircle className="spin" size={16}/> : <ArrowRight size={16}/>} Analyze scan</button></form> : <div><span className="eyebrow">FROM PLAYGROUND TO TERMINAL</span><h2 id="modal-title">Your next discovery.</h2><p>EasyNmap is a Python terminal app that wraps Nmap. The web playground demonstrates its workflow with sample scans and analyzes your uploaded text output.</p><ol className="guide-steps"><li><strong>Get the source</strong><code>git clone {repository}.git</code></li><li><strong>Install on Linux with Python 3.10+ and Nmap</strong><code>cd EasyNmap<br/>python3 -m venv venv<br/>source venv/bin/activate<br/>pip install -r requirements.txt<br/>pip install -e .</code></li><li><strong>Start exploring offline</strong><code>python -m easynmap.app --no-ai</code></li></ol><p>AI features in the Python app require an OpenRouter key. This web app provides rule-based explanations without an API key.</p><a className="button primary" href={repository} target="_blank" rel="noreferrer">Read the documentation <ArrowUpRight size={15}/></a></div>}</section></div>}
  </div>;
}

function CornerEnter() { return <span className="enter-key">↵</span>; }
