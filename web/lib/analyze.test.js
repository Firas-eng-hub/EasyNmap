import { test } from 'node:test';
import assert from 'node:assert/strict';
import { analyze, demos, MAX_BYTES } from './analyze.js';

test('service demo returns ports, versions, guidance and report', () => {
  const r = analyze(demos.service);
  assert.equal(r.summary.open, 4);
  assert.equal(r.summary.review, 1);
  assert.equal(r.ports[0].version, 'OpenSSH 9.6');
  assert.match(r.report, /192.0.2.10/);
});
test('sweep preserves distinct hosts without inventing ports', () => {
  const r = analyze(demos.sweep);
  assert.equal(r.hosts.length, 3);
  assert.equal(r.summary.open, 0);
});
test('closed and uncertain ports are not counted as open', () => {
  const r = analyze('Nmap scan report for 127.0.0.1\r\nHost is up.\r\n53/udp open|filtered domain\r\n22/tcp closed ssh\r\n443/tcp open https');
  assert.equal(r.ports.length, 3);
  assert.equal(r.summary.open, 1);
});
test('rejects invalid output and oversized data', () => {
  for (const input of ['', null, 'hello', 'x'.repeat(MAX_BYTES + 1)]) assert.throws(() => analyze(input));
});
test('report escapes host and service table delimiters', () => {
  const r = analyze('Nmap scan report for <host|name>\n80/tcp open http');
  assert.ok(!r.report.includes('<host|name>'));
});
