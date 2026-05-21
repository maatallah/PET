'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState, useEffect, useRef } from 'react';

interface SearchHit {
  type: string;
  id: string;
  name: string;
  breadcrumb: string;
  match: string;
}

export default function Header() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchHit[]>([]);
  const [open, setOpen] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleSearch = (value: string) => {
    setQuery(value);
    if (timer.current) clearTimeout(timer.current);
    if (!value.trim()) {
      setResults([]);
      setOpen(false);
      return;
    }
    timer.current = setTimeout(async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/search?q=${encodeURIComponent(value)}`);
        if (res.ok) {
          const data: SearchHit[] = await res.json();
          setResults(data);
          setOpen(data.length > 0);
        }
      } catch {
        // ignore
      }
    }, 300);
  };

  const navigate = (hit: SearchHit) => {
    setOpen(false);
    setQuery('');
    setResults([]);
    if (hit.type === 'workspace') router.push(`/workspaces/${hit.id}`);
    else if (hit.type === 'project') router.push(`/workspaces/_/projects/${hit.id}`);
  };

  return (
    <header className="border-b border-zinc-200">
      <nav className="mx-auto flex h-14 max-w-5xl items-center gap-6 px-4">
        <Link href="/" className="text-lg font-bold tracking-tight">
          PET
        </Link>
        <Link href="/workspaces" className="text-sm text-zinc-600 hover:text-zinc-900">
          Workspaces
        </Link>
        <Link href="/analytics" className="text-sm text-zinc-600 hover:text-zinc-900">
          Analytics
        </Link>

        <div ref={ref} className="relative ml-auto">
          <input
            type="text"
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search..."
            className="w-56 rounded-md border border-zinc-300 px-3 py-1.5 text-sm focus:border-zinc-500 focus:outline-none"
          />
          {open && results.length > 0 && (
            <div className="absolute right-0 top-full mt-1 w-80 rounded-md border border-zinc-200 bg-white shadow-lg">
              {results.map((hit, i) => (
                <button
                  key={`${hit.type}-${hit.id}-${i}`}
                  onClick={() => navigate(hit)}
                  className="w-full px-4 py-2 text-left text-sm hover:bg-zinc-50"
                >
                  <span className="text-xs font-medium uppercase text-zinc-400">{hit.type}</span>
                  <p className="truncate font-medium text-zinc-900">{hit.name}</p>
                  <p className="truncate text-xs text-zinc-500">{hit.breadcrumb}</p>
                </button>
              ))}
            </div>
          )}
        </div>
      </nav>
    </header>
  );
}
