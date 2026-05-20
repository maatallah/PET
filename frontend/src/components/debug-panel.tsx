/* eslint-disable */
'use client';

import { useEffect, useRef, useState } from 'react';

interface DebugEntry {
  id: number;
  timestamp: string;
  method: string;
  url: string;
  status: number | null;
  duration: number;
  error: string | null;
  size: string;
}

let logId = 0;

function patchFetch(addEntry: (entry: DebugEntry) => void): () => void {
  const originalFetch = (globalThis as any).fetch;
  let active = true;

  (globalThis as any).fetch = async function (...args: any[]) {
    if (!active) return originalFetch(...args);

    const id = ++logId;
    const started = performance.now();
    const method: string = (args[1] && (args[1] as any).method) || 'GET';
    const url: string = (args[0] as string).split('?')[0];
    const entry: DebugEntry = {
      id,
      timestamp: new Date().toLocaleTimeString(),
      method,
      url,
      status: null,
      duration: 0,
      error: null,
      size: '—',
    };

    try {
      const res: Response = await originalFetch(...args);
      entry.status = res.status;
      const body: string = await res.clone().text();
      entry.size = body.length > 1024
        ? `${(body.length / 1024).toFixed(1)} KB`
        : `${body.length} B`;
      return new Response(body, {
        status: res.status,
        statusText: res.statusText,
        headers: res.headers,
      });
    } catch (e: any) {
      entry.error = e.message || 'Network error';
      entry.status = 0;
    } finally {
      entry.duration = Math.round(performance.now() - started);
      addEntry(entry);
    }

    if (entry.error) throw new Error(entry.error);
    return undefined as any;
  };

  return () => {
    active = false;
    (globalThis as any).fetch = originalFetch;
  };
}

interface Props {
  visible: boolean;
  onToggle: () => void;
}

export default function DebugPanel({ visible, onToggle }: Props) {
  const [entries, setEntries] = useState<DebugEntry[]>([]);
  const [filter, setFilter] = useState('');
  const [paused, setPaused] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!visible || paused) return;
    const cleanup = patchFetch((entry) => {
      setEntries((prev) => [...prev.slice(-200), entry]);
    });
    return cleanup;
  }, [visible, paused]);

  useEffect(() => {
    if (!visible) return;
    const handle = setInterval(() => {
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
    }, 100);
    return () => clearInterval(handle);
  }, [visible]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        onToggle();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onToggle]);

  const filtered = entries.filter(
    (e) =>
      !filter ||
      e.url.toLowerCase().includes(filter.toLowerCase()) ||
      e.method.toLowerCase().includes(filter.toLowerCase()),
  );

  const ok = filtered.filter(
    (e) => e.status && e.status >= 200 && e.status < 400,
  ).length;
  const err = filtered.filter(
    (e) => e && e.status && e.status >= 400,
  ).length;
  const net = filtered.filter((e) => e.error).length;

  return (
    <div
      style={{
        position: 'fixed',
        bottom: visible ? 16 : -400,
        right: 16,
        width: 480,
        maxHeight: 400,
        zIndex: 99999,
        background: '#1a1a2e',
        border: '1px solid #333',
        borderRadius: 8,
        boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
        color: '#ddd',
        fontFamily: 'monospace',
        fontSize: 11,
        display: 'flex',
        flexDirection: 'column',
        transition: 'bottom 0.2s',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '6px 10px',
          background: '#16213e',
          borderBottom: '1px solid #333',
          borderRadius: '8px 8px 0 0',
        }}
      >
        <span style={{ fontWeight: 'bold', color: '#0ff' }}>
          PET Debug [{entries.length}]
        </span>
        <span style={{ fontSize: 10, color: '#888' }}>
          {ok}OK {err}ERR {net}NET
        </span>
        <div style={{ display: 'flex', gap: 6 }}>
          <label style={{ fontSize: 10, color: '#aaa', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={paused}
              onChange={(e) => setPaused(e.target.checked)}
              style={{ marginRight: 4 }}
            />
            Pause
          </label>
          <button
            onClick={() => setEntries([])}
            style={{
              background: 'none',
              border: 'none',
              color: '#f55',
              cursor: 'pointer',
              fontSize: 12,
            }}
          >
            Clear
          </button>
          <button
            onClick={onToggle}
            style={{
              background: 'none',
              border: 'none',
              color: '#ff0',
              cursor: 'pointer',
              fontSize: 14,
            }}
          >
            X
          </button>
        </div>
      </div>

      <input
        type="text"
        placeholder="Filter by URL or method..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        style={{
          padding: 4,
          margin: 4,
          background: '#0f0f23',
          border: '1px solid #333',
          borderRadius: 4,
          color: '#ccc',
          fontSize: 10,
        }}
      />

      <div
        ref={scrollRef}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '0 6px 6px',
        }}
      >
        {filtered.map((e) => (
          <div
            key={e.id}
            style={{
              padding: '3px 4px',
              borderBottom: '1px solid #1a1a2e',
              color: e.error
                ? '#f44'
                : e.status && e.status >= 400
                ? '#fa0'
                : e.status && e.status >= 300
                ? '#ff0'
                : '#0f0',
              display: 'flex',
              justifyContent: 'space-between',
              gap: 4,
            }}
          >
            <span>
              {e.method.toUpperCase()} {e.url.slice(0, 40)}
              {e.url.length > 40 ? '...' : ''}
              {e.error ? ` [${e.error}]` : ` [${e.status}]`}
            </span>
            <span style={{ color: '#888' }}>
              {e.duration}ms {e.size}
            </span>
          </div>
        ))}
        {entries.length === 0 && (
          <div style={{ padding: 16, textAlign: 'center', color: '#555' }}>
            Ctrl+Shift+D to toggle - No requests captured yet
          </div>
        )}
      </div>
    </div>
  );
}