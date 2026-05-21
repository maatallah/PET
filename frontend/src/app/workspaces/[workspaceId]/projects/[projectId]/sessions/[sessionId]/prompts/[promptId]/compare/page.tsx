'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, Prompt, ExecuteResult } from '@/lib/api';

type Variant = {
  label: string;
  provider: string;
  model: string;
  result: ExecuteResult | null;
  error: string | null;
  executing: boolean;
};

function CompareView({
  workspaceId,
  projectId,
  sessionId,
  promptId,
}: {
  workspaceId: string;
  projectId: string;
  sessionId: string;
  promptId: string;
}) {
  const [prompt, setPrompt] = useState<Prompt | null>(null);
  const [providers, setProviders] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [variants, setVariants] = useState<Variant[]>([
    { label: 'A', provider: 'openai', model: 'gpt-4o-mini', result: null, error: null, executing: false },
    { label: 'B', provider: 'openrouter', model: 'openai/gpt-4o-mini', result: null, error: null, executing: false },
  ]);

  useEffect(() => {
    let ignore = false;
    (async () => {
      try {
        const [p, provs] = await Promise.all([
          api.getPrompt(sessionId, promptId),
          fetch('http://127.0.0.1:8000/providers').then(r => r.json()),
        ]);
        if (!ignore) {
          setPrompt(p);
          setProviders(provs);
        }
      } catch (err) {
        if (!ignore) setError(err instanceof Error ? err.message : 'Failed to load');
      } finally {
        if (!ignore) setLoading(false);
      }
    })();
    return () => { ignore = true; };
  }, [sessionId, promptId]);

  const updateVariant = (index: number, patch: Partial<Variant>) => {
    setVariants((prev) => prev.map((v, i) => (i === index ? { ...v, ...patch } : v)));
  };

  const runCompare = async () => {
    setVariants((prev) => prev.map((v) => ({ ...v, result: null, error: null, executing: true })));

    await Promise.all(
      variants.map(async (v, i) => {
        try {
          const res = await api.executePrompt(sessionId, promptId, {
            dry_run: false,
            provider: v.provider,
            model: v.model,
          });
          updateVariant(i, { result: res, error: null, executing: false });
        } catch (err) {
          updateVariant(i, { error: err instanceof Error ? err.message : 'Execution failed', executing: false });
        }
      }),
    );
  };

  if (loading) {
    return <div className="mx-auto max-w-7xl px-4 py-8 text-center text-zinc-400">Loading...</div>;
  }

  if (error || !prompt) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8">
        <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error ?? 'Prompt not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <Link
        href={`/workspaces/${workspaceId}/projects/${projectId}/sessions/${sessionId}/prompts/${promptId}`}
        className="mb-4 inline-block text-sm text-zinc-500 hover:text-zinc-900"
      >
        &larr; Back to Prompt
      </Link>

      <h1 className="mb-2 text-2xl font-bold">A/B Compare: {prompt.name}</h1>
      <p className="mb-6 text-sm text-zinc-500">Run the same prompt with different providers or settings side by side.</p>

      <div className="mb-6 grid grid-cols-2 gap-6">
        {variants.map((v, i) => (
          <div key={v.label} className="rounded-lg border border-zinc-200 p-4">
            <h3 className="mb-3 text-lg font-semibold">Variant {v.label}</h3>

            <div className="mb-3 space-y-2">
              <div>
                <label className="mb-1 block text-xs font-medium text-zinc-500">Provider</label>
                <select
                  value={v.provider}
                  onChange={(e) => updateVariant(i, { provider: e.target.value })}
                  className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
                >
                  {providers.length === 0 ? (
                    <option value="openai">OpenAI</option>
                  ) : (
                    providers.map((p) => (
                      <option key={p} value={p}>
                        {p === 'openai' ? 'OpenAI' : p === 'google' ? 'Google Gemini' : p === 'ollama' ? 'Ollama' : p === 'openrouter' ? 'OpenRouter' : p}
                      </option>
                    ))
                  )}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-zinc-500">Model</label>
                <input
                  value={v.model}
                  onChange={(e) => updateVariant(i, { model: e.target.value })}
                  className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
                  placeholder="e.g. gpt-4o-mini"
                />
              </div>
            </div>

            {v.executing && <p className="text-sm text-zinc-400">Executing...</p>}

            {v.error && (
              <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                {v.error}
              </div>
            )}

            {v.result && (
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-xs font-medium text-zinc-400">Response</span>
                  <pre className="mt-1 max-h-60 overflow-auto whitespace-pre-wrap rounded-md bg-green-50 p-3 text-xs">
                    {v.result.response ?? v.result.model_response ?? '(empty)'}
                  </pre>
                </div>
                <div className="flex gap-4 text-xs text-zinc-500">
                  {v.result.tokens_input !== null && <span>In: {v.result.tokens_input}</span>}
                  {v.result.tokens_output !== null && <span>Out: {v.result.tokens_output}</span>}
                  {v.result.cost_estimate !== null && <span>Cost: ${v.result.cost_estimate.toFixed(6)}</span>}
                  {v.result.latency_ms !== null && <span>Latency: {v.result.latency_ms}ms</span>}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <button
        onClick={runCompare}
        disabled={variants.some((v) => v.executing)}
        className="rounded-md bg-zinc-900 px-6 py-2.5 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
      >
        {variants.some((v) => v.executing) ? 'Running...' : 'Run Both'}
      </button>

      {variants.every((v) => v.result) && (
        <div className="mt-6 rounded-lg border border-zinc-200 p-4">
          <h3 className="mb-2 text-sm font-semibold">Summary</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            {variants.map((v) => (
              <div key={v.label}>
                <p className="font-medium text-zinc-700">
                  {v.label}: {v.provider}/{v.model}
                </p>
                <ul className="mt-1 space-y-0.5 text-xs text-zinc-500">
                  <li>Tokens: {v.result?.tokens_input ?? '?'} in / {v.result?.tokens_output ?? '?'} out</li>
                  <li>Cost: ${v.result?.cost_estimate?.toFixed(6) ?? '?'}</li>
                  <li>Latency: {v.result?.latency_ms ?? '?'}ms</li>
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function Page({
  params,
}: {
  params: Promise<{
    workspaceId: string;
    projectId: string;
    sessionId: string;
    promptId: string;
  }>;
}) {
  const [ids, setIds] = useState<{
    workspaceId: string;
    projectId: string;
    sessionId: string;
    promptId: string;
  } | null>(null);
  useEffect(() => {
    params.then((p) => setIds(p));
  }, [params]);
  if (!ids) return <div className="p-8 text-center text-zinc-400">Loading...</div>;
  return (
    <CompareView
      workspaceId={ids.workspaceId}
      projectId={ids.projectId}
      sessionId={ids.sessionId}
      promptId={ids.promptId}
    />
  );
}
