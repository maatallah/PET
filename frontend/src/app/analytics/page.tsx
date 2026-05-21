'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, AnalyticsData } from '@/lib/api';

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;
    (async () => {
      try {
        const d = await api.getAnalytics();
        if (!ignore) setData(d);
      } catch (err) {
        if (!ignore) setError(err instanceof Error ? err.message : 'Failed to load');
      } finally {
        if (!ignore) setLoading(false);
      }
    })();
    return () => { ignore = true; };
  }, []);

  if (loading) return <div className="mx-auto max-w-5xl px-4 py-8 text-center text-zinc-400">Loading...</div>;

  if (error) return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
    </div>
  );

  if (!data || data.total_runs === 0) return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <Link href="/workspaces" className="mb-4 inline-block text-sm text-zinc-500 hover:text-zinc-900">&larr; Back</Link>
      <h1 className="mb-2 text-2xl font-bold">Analytics</h1>
      <p className="py-12 text-center text-zinc-400">No execution data yet. Run some prompts first.</p>
    </div>
  );

  const cards = [
    { label: 'Total Runs', value: data.total_runs },
    { label: 'Total Tokens In', value: data.total_tokens_input.toLocaleString() },
    { label: 'Total Tokens Out', value: data.total_tokens_output.toLocaleString() },
    { label: 'Total Cost', value: `$${data.total_cost.toFixed(6)}` },
    { label: 'Avg Latency', value: `${data.avg_latency_ms}ms` },
    { label: 'Avg Tokens / Run', value: `${data.avg_tokens_input} in / ${data.avg_tokens_output} out` },
    { label: 'Avg Cost / Run', value: `$${data.avg_cost.toFixed(8)}` },
  ];

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <Link href="/workspaces" className="mb-4 inline-block text-sm text-zinc-500 hover:text-zinc-900">&larr; Back</Link>
      <h1 className="mb-6 text-2xl font-bold">Analytics</h1>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {cards.map((card) => (
          <div key={card.label} className="rounded-lg border border-zinc-200 p-4">
            <p className="text-xs font-medium uppercase tracking-wide text-zinc-400">{card.label}</p>
            <p className="mt-1 text-xl font-semibold">{card.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
