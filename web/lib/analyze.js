export const MAX_BYTES = 256 * 1024;

export const demos = {
  quick: `Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for demo-server (192.0.2.10)
Host is up (0.0021s latency).
Not shown: 96 closed tcp ports (conn-refused)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
3306/tcp open  mysql
Nmap done: 1 IP address (1 host up) scanned in 1.42 seconds`,
  service: `Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for demo-server (192.0.2.10)
Host is up (0.0021s latency).
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.6
80/tcp   open  http    nginx 1.24.0
443/tcp  open  https   nginx 1.24.0
3306/tcp open  mysql   MySQL 8.0.36
Service detection performed.
Nmap done: 1 IP address (1 host up) scanned in 6.84 seconds`,
  sweep: `Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for gateway (192.0.2.1)
Host is up (0.0010s latency).
Nmap scan report for demo-server (192.0.2.10)
Host is up (0.0021s latency).
Nmap scan report for workstation (192.0.2.24)
Host is up (0.0032s latency).
Nmap done: 256 IP addresses (3 hosts up) scanned in 2.10 seconds`,
};

const guidance = {
  ssh: ['Remote access', 'SSH provides encrypted remote access. Prefer key-based authentication and restrict access to trusted networks.'],
  http: ['Unencrypted web traffic', 'HTTP does not encrypt traffic. Redirect sensitive pages to HTTPS and check that credentials are never sent over HTTP.'],
  https: ['Encrypted web traffic', 'HTTPS encrypts web traffic. Keep certificates current and review TLS configuration.'],
  mysql: ['Database access', 'MySQL is reachable on this scanned interface. Confirm whether this is intended and restrict access to application hosts.'],
  postgresql: ['Database access', 'PostgreSQL is reachable. Review network restrictions, authentication, and access roles.'],
  telnet: ['Unencrypted remote access', 'Telnet sends traffic without encryption. Replace it with SSH where possible.'],
  ftp: ['File transfer', 'FTP may send credentials without encryption. Prefer SFTP or a securely configured encrypted alternative.'],
  'ms-wbt-server': ['Remote desktop', 'Remote Desktop is reachable. Restrict access and require strong authentication.'],
};

export function analyze(raw) {
  if (typeof raw !== 'string' || !raw.trim()) throw new Error('Paste or upload Nmap normal text output first.');
  if (Buffer.byteLength(raw, 'utf8') > MAX_BYTES) throw new Error('Scan output must be 256 KB or smaller.');
  if (!/^Nmap scan report for .+/m.test(raw)) throw new Error('No Nmap hosts found. Use normal text output generated with nmap -oN scan.txt <target>. XML and grepable formats are not supported.');
  const hosts = [];
  let host;
  for (const line of raw.split(/\r?\n/)) {
    const heading = line.match(/^Nmap scan report for (.+)$/);
    if (heading) {
      const named = heading[1].match(/^(.*?) \(([^)]+)\)$/);
      host = { name: named ? named[1] : heading[1], address: named ? named[2] : heading[1], status: 'unknown', ports: [] };
      hosts.push(host);
    } else if (host) {
      if (/^Host is up/.test(line)) host.status = 'up';
      if (/^Host seems down/.test(line)) host.status = 'down';
      const port = line.trim().match(/^(\d{1,5})\/(tcp|udp)\s+(open|closed|filtered|unfiltered|open\|filtered|closed\|filtered)\s+(\S+)(?:\s+(.*))?$/);
      if (port && Number(port[1]) <= 65535) host.ports.push({ port: Number(port[1]), protocol: port[2], state: port[3], service: port[4], version: port[5] || '' });
    }
  }
  const ports = hosts.flatMap(h => h.ports.map(p => ({ ...p, host: h.address })));
  const open = ports.filter(p => p.state === 'open');
  const insights = open.map(p => {
    const [title, detail] = guidance[p.service] || ['Review exposed service', `Confirm that ${p.service} is intended to be reachable and keep its software maintained.`];
    return { ...p, title, detail, attention: ['mysql', 'postgresql', 'telnet', 'ftp', 'ms-wbt-server'].includes(p.service) };
  });
  const duration = raw.match(/scanned in ([\d.]+) seconds/);
  const result = { hosts, ports, insights, summary: { hosts: hosts.length, open: open.length, services: new Set(open.map(p => p.service)).size, review: insights.filter(i => i.attention).length, duration: duration ? `${duration[1]}s` : '—' } };
  result.report = report(result);
  return result;
}

function report(result) {
  const clean = value => String(value).replace(/[|\r\n`<>]/g, ' ');
  return `# EasyNmap scan review\n\n${result.summary.hosts} hosts · ${result.summary.open} explicitly open ports · ${result.summary.review} services to review\n\n## Ports\n\n| Host | Port | State | Service | Version |\n| --- | --- | --- | --- | --- |\n${result.ports.map(p => `| ${clean(p.host)} | ${p.port}/${p.protocol} | ${p.state} | ${clean(p.service)} | ${clean(p.version)} |`).join('\n')}\n\n## Guidance\n\n${result.insights.map(i => `- ${clean(i.host)}:${i.port} — ${clean(i.title)}. ${clean(i.detail)}`).join('\n')}\n\nRule-based guidance, not a vulnerability assessment. An open port alone does not establish a vulnerability. Counts include explicit port rows only; aggregated “not shown” ports are excluded.\n`;
}
