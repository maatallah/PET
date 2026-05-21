'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, Prompt, ExecuteResult, FileInfo, TokenEstimate } from '@/lib/api';

function PromptDetail({
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
  const router = useRouter();
  const [prompt, setPrompt] = useState<Prompt | null>(null);
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState<ExecuteResult | null>(null);
  const [formValues, setFormValues] = useState<Record<string, string>>({});
  const [provider, setProvider] = useState('openai');
  const [filesError, setFilesError] = useState<string | null>(null);
  const [previewFileId, setPreviewFileId] = useState<string | null>(null);
  const [previewText, setPreviewText] = useState<string | null>(null);
  const [tokenEstimate, setTokenEstimate] = useState<TokenEstimate | null>(null);
  const [providers, setProviders] = useState<string[]>([]);
  const estimateTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let ignore = false;
    (async () => {
      try {
        const [p, f, provs] = await Promise.all([
          api.getPrompt(sessionId, promptId),
          api.listFiles(sessionId),
          fetch('http://127.0.0.1:8000/providers').then(r => r.json()),
        ]);
        if (!ignore) {
          setPrompt(p);
          setProviders(provs);
          setFiles(f.sort((a, b) => b.created_at.localeCompare(a.created_at)));
        }
      } catch (err) {
        if (!ignore) setError(err instanceof Error ? err.message : 'Failed to load');
      } finally {
        if (!ignore) setLoading(false);
      }
    })();
    return () => { ignore = true; };
  }, [sessionId, promptId]);

  const updateEstimate = useCallback(async () => {
    if (!prompt) return;
    let text = `${prompt.system_prompt ?? ''}\n${prompt.user_prompt ?? ''}`;
    if (prompt.variables) {
      for (const v of prompt.variables) {
        text = text.replaceAll(`{${v.name}}`, formValues[v.name] ?? `{${v.name}}`);
      }
    }
    try {
      const est = await api.estimateTokens(text);
      setTokenEstimate(est);
    } catch {
      // ignore estimate errors
    }
  }, [prompt, formValues]);

  useEffect(() => {
    if (!prompt) return;
    if (estimateTimer.current) clearTimeout(estimateTimer.current);
    estimateTimer.current = setTimeout(updateEstimate, 300);
    return () => {
      if (estimateTimer.current) clearTimeout(estimateTimer.current);
    };
  }, [formValues, prompt, updateEstimate]);

  const handleDelete = async () => {
    setError(null);
    try {
      await api.deletePrompt(sessionId, promptId);
      router.push(`/workspaces/${workspaceId}/projects/${projectId}/sessions/${sessionId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete prompt');
    }
  };

  const handleExecute = async (dryRun: boolean) => {
    setError(null);
    setResult(null);
    setExecuting(true);
    try {
      const variables = prompt!.variables && prompt!.variables.length > 0 ? formValues : undefined;
      const res = await api.executePrompt(sessionId, promptId, {
        variables,
        dry_run: dryRun,
        provider,
      });
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Execution failed');
    } finally {
      setExecuting(false);
    }
  };

  const handleVarChange = (name: string, value: string) => {
    setFormValues((prev) => ({ ...prev, [name]: value }));
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8">
        <div className="py-12 text-center text-zinc-400">Loading prompt...</div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <Link
        href={`/workspaces/${workspaceId}/projects/${projectId}/sessions/${sessionId}`}
        className="mb-4 inline-block text-sm text-zinc-500 hover:text-zinc-900"
      >
        &larr; Back to Prompts
      </Link>

      {error && prompt === null && (
        <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {prompt && (
        <>
          <div className="mb-6 flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">{prompt.name}</h1>
              <p className="mt-1 text-sm text-zinc-500">v{prompt.version}</p>
            </div>
            <button
              onClick={handleDelete}
              className="rounded-md border border-red-300 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50"
            >
              Delete
            </button>
          </div>

          {error && (
            <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="mb-6 space-y-4">
            <div>
              <h3 className="mb-1 text-xs font-medium uppercase tracking-wide text-zinc-400">Pattern</h3>
              <p className="text-sm">
                {prompt.prompt_pattern ?? <span className="italic text-zinc-300">None</span>}
              </p>
            </div>

            <div>
              <h3 className="mb-1 text-xs font-medium uppercase tracking-wide text-zinc-400">
                System Prompt
              </h3>
              <pre className="whitespace-pre-wrap rounded-md bg-zinc-50 p-3 text-sm">
                {prompt.system_prompt ?? <span className="italic text-zinc-300">None</span>}
              </pre>
            </div>

            <div>
              <h3 className="mb-1 text-xs font-medium uppercase tracking-wide text-zinc-400">
                User Prompt
              </h3>
              <pre className="whitespace-pre-wrap rounded-md bg-zinc-50 p-3 text-sm">
                {prompt.user_prompt ?? <span className="italic text-zinc-300">None</span>}
              </pre>
            </div>

            {prompt.model_id && (
              <div>
                <h3 className="mb-1 text-xs font-medium uppercase tracking-wide text-zinc-400">Model</h3>
                <p className="text-sm">{prompt.model_id}</p>
              </div>
            )}

            {prompt.variables && prompt.variables.length > 0 && (
              <div>
                <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-zinc-400">
                  Variables
                </h3>
                <div className="space-y-2">
                  {prompt.variables.map((v) => (
                    <div key={v.name}>
                      <label className="mb-1 block text-xs font-medium text-zinc-500">
                        {v.name} <span className="text-zinc-400">({v.type})</span>
                      </label>
                      <input
                        value={formValues[v.name] ?? ''}
                        onChange={(e) => handleVarChange(v.name, e.target.value)}
                        className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
                        placeholder={`Enter ${v.name}...`}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex flex-wrap items-center gap-3">
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  className="rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
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
                <span className="text-xs text-zinc-400">
                  {tokenEstimate ? `~${tokenEstimate.tokens} tokens · ~$${tokenEstimate.cost.toFixed(6)}` : ''}
                </span>
                <button
                  onClick={() => handleExecute(true)}
                  disabled={executing}
                  className="rounded-md border border-zinc-300 px-4 py-2 text-sm font-medium hover:bg-zinc-100 disabled:opacity-50"
                >
                  {executing ? 'Executing...' : 'Preview'}
                </button>
                <button
                  onClick={() => handleExecute(false)}
                  disabled={executing}
                  className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
                >
                  {executing ? 'Executing...' : 'Run'}
                </button>
                <a
                  href={api.exportPromptUrl(sessionId, promptId, 'markdown')}
                  download
                  className="rounded-md border border-zinc-300 px-3 py-2 text-sm text-zinc-600 hover:bg-zinc-50"
                >
                  .md
                </a>
                <a
                  href={api.exportPromptUrl(sessionId, promptId, 'json')}
                  download
                  className="rounded-md border border-zinc-300 px-3 py-2 text-sm text-zinc-600 hover:bg-zinc-50"
                >
                  .json
                </a>
                <Link
                  href={`/workspaces/${workspaceId}/projects/${projectId}/sessions/${sessionId}/prompts/${promptId}/compare`}
                  className="rounded-md border border-zinc-300 px-3 py-2 text-sm text-zinc-600 hover:bg-zinc-50"
                >
                  A/B Compare
                </Link>
            </div>
        </div>
        </>
      )}

      {result && (
        <div className="space-y-4 rounded-lg border border-zinc-200 p-4">
          {result.resolved_prompt && (
            <div>
              <h3 className="mb-1 text-xs font-medium uppercase tracking-wide text-zinc-400">
                Resolved Prompt
              </h3>
              <pre className="whitespace-pre-wrap rounded-md bg-zinc-50 p-3 text-sm">
                {result.resolved_prompt}
              </pre>
            </div>
          )}

          {result.response && (
            <div>
              <h3 className="mb-1 text-xs font-medium uppercase tracking-wide text-zinc-400">
                Response
              </h3>
              <pre className="whitespace-pre-wrap rounded-md bg-green-50 p-3 text-sm">
                {result.response}
              </pre>
            </div>
          )}

          <div className="flex gap-6 text-sm text-zinc-500">
            {result.tokens_input !== null && <span>Input tokens: {result.tokens_input}</span>}
            {result.tokens_output !== null && <span>Output tokens: {result.tokens_output}</span>}
            {result.cost_estimate !== null && <span>Cost: ${result.cost_estimate.toFixed(6)}</span>}
          </div>
        </div>
      )}

      <h2 className="mb-4 mt-10 text-xl font-semibold">Session Files</h2>

      {filesError && (
        <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {filesError}
        </div>
      )}

      {files.length === 0 ? (
        <p className="py-6 text-center text-sm text-zinc-400">No files in this session.</p>
      ) : (
        <div className="space-y-3">
          {files.map((f) => (
            <div key={f.id}>
              <button
                onClick={async () => {
                  if (previewFileId === f.id) {
                    setPreviewFileId(null);
                    return;
                  }
                  setPreviewFileId(f.id);
                  setPreviewText(null);
                  if (
                    f.content_text ||
                    f.mime_type?.startsWith('text/') ||
                    f.mime_type?.includes('json')
                  ) {
                    if (f.content_text) {
                      setPreviewText(f.content_text);
                    } else {
                      try {
                        const res = await fetch(api.downloadFileUrl(sessionId, f.id));
                        setPreviewText(await res.text());
                      } catch {
                        setPreviewText('[Failed to load preview]');
                      }
                    }
                  }
                }}
                className="flex w-full items-center gap-3 rounded-lg border border-zinc-200 px-4 py-3 text-left text-sm hover:bg-zinc-50"
              >
                <span className="text-lg">
                  {f.mime_type?.startsWith('image/')
                    ? '\u{1F5BC}\u{FE0F}'
                    : f.mime_type?.startsWith('text/') || f.mime_type?.includes('json')
                      ? '\u{1F4DD}'
                      : '\u{1F4C4}'}
                </span>
                <span className="flex-1 font-medium text-zinc-900">{f.original_name}</span>
                <span className="text-zinc-400">
                  {f.size_bytes !== null
                    ? f.size_bytes < 1024
                      ? `${f.size_bytes} B`
                      : `${(f.size_bytes / 1024).toFixed(1)} KB`
                    : '\u2014'}
                </span>
                <a
                  href={api.downloadFileUrl(sessionId, f.id)}
                  onClick={(e) => e.stopPropagation()}
                  className="rounded px-2 py-1 text-zinc-500 hover:text-zinc-900"
                >
                  Download
                </a>
              </button>

              {previewFileId === f.id && (
                <div className="mt-2 rounded-lg border border-zinc-200 p-4">
                  {f.mime_type?.startsWith('image/') ? (
                    <img
                      src={api.downloadFileUrl(sessionId, f.id)}
                      alt={f.original_name}
                      className="max-h-96 rounded object-contain"
                    />
                  ) : (
                    <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded bg-zinc-50 p-3 text-xs">
                      {previewText === null ? 'Loading...' : previewText}
                    </pre>
                  )}
                </div>
              )}
            </div>
          ))}
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
  if (!ids)
    return <div className="p-8 text-center text-zinc-400">Loading...</div>;
  return (
    <PromptDetail
      workspaceId={ids.workspaceId}
      projectId={ids.projectId}
      sessionId={ids.sessionId}
      promptId={ids.promptId}
    />
  );
}