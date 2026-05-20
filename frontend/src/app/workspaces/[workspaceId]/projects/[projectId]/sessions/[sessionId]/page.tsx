'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { api, Prompt, FileInfo } from '@/lib/api';

const PATTERN_OPTIONS = ['persona', 'cot', 'few_shot', 'template'];

function PromptList({
  workspaceId,
  projectId,
  sessionId,
}: {
  workspaceId: string;
  projectId: string;
  sessionId: string;
}) {
  const [session, setSession] = useState<{ id: string; name: string } | null>(null);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [userPrompt, setUserPrompt] = useState('');
  const [pattern, setPattern] = useState('');
  const [variablesJson, setVariablesJson] = useState('');

  const [filesError, setFilesError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let ignore = false;
    (async () => {
      try {
        const [sess, pList] = await Promise.all([
          api.getSession(projectId, sessionId),
          api.listPrompts(sessionId),
        ]);
        if (!ignore) {
          setSession(sess);
          setPrompts(pList);
        }
      } catch (err) {
        if (!ignore) setError(err instanceof Error ? err.message : 'Failed to load');
      } finally {
        if (!ignore) setLoading(false);
      }
      try {
        const fList = await api.listFiles(sessionId);
        if (!ignore) setFiles(fList.sort((a, b) => b.created_at.localeCompare(a.created_at)));
      } catch {
        // silently fail for files
      }
    })();
    return () => { ignore = true; };
  }, [projectId, sessionId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    let variables: { name: string; type: string }[] | null = null;
    if (variablesJson.trim()) {
      try {
        variables = JSON.parse(variablesJson.trim());
        if (!Array.isArray(variables)) throw new Error('Must be an array');
      } catch {
        setError('Variables must be valid JSON array of {name, type} objects');
        return;
      }
    }

    try {
      await api.createPrompt(sessionId, {
        name,
        system_prompt: systemPrompt || null,
        user_prompt: userPrompt || null,
        prompt_pattern: pattern || null,
        variables,
      });
      setName('');
      setSystemPrompt('');
      setUserPrompt('');
      setPattern('');
      setVariablesJson('');

      const [sess, pList] = await Promise.all([
        api.getSession(projectId, sessionId),
        api.listPrompts(sessionId),
      ]);
      setSession(sess);
      setPrompts(pList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create prompt');
    }
  };

  const handleDelete = async (id: string) => {
    setError(null);
    try {
      await api.deletePrompt(sessionId, id);
      const [sess, pList] = await Promise.all([
        api.getSession(projectId, sessionId),
        api.listPrompts(sessionId),
      ]);
      setSession(sess);
      setPrompts(pList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete prompt');
    }
  };

  const handleUpload = async (file: File) => {
    setFilesError(null);
    setUploading(true);
    try {
      await api.uploadFile(sessionId, file);
      const fList = await api.listFiles(sessionId);
      setFiles(fList.sort((a, b) => b.created_at.localeCompare(a.created_at)));
    } catch (err) {
      setFilesError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteFile = async (fileId: string) => {
    setFilesError(null);
    try {
      await api.deleteFile(sessionId, fileId);
      const fList = await api.listFiles(sessionId);
      setFiles(fList.sort((a, b) => b.created_at.localeCompare(a.created_at)));
    } catch (err) {
      setFilesError(err instanceof Error ? err.message : 'Delete failed');
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  const formatSize = (bytes: number | null): string => {
    if (bytes === null) return '\u2014';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const fileIcon = (mime: string | null): string => {
    if (!mime) return '\u{1F4C4}';
    if (mime.startsWith('image/')) return '\u{1F5BC}\u{FE0F}';
    if (mime.startsWith('text/')) return '\u{1F4DD}';
    if (mime.includes('pdf')) return '\u{1F4D5}';
    if (mime.includes('json')) return '\u{1F4CB}';
    return '\u{1F4C4}';
  };

  if (loading || !session) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8">
        <div className="py-12 text-center text-zinc-400">Loading prompts...</div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <Link
        href={`/workspaces/${workspaceId}/projects/${projectId}`}
        className="mb-4 inline-block text-sm text-zinc-500 hover:text-zinc-900"
      >
        &larr; Back to Sessions
      </Link>

      <h1 className="mb-6 text-3xl font-bold tracking-tight">{session.name}</h1>

      {error && (
        <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <h2 className="mb-4 text-xl font-semibold">Prompts</h2>

      <form
        onSubmit={handleCreate}
        className="mb-8 space-y-3 rounded-lg border border-zinc-200 p-4"
      >
        <div>
          <label className="mb-1 block text-xs font-medium text-zinc-500">Name</label>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
            placeholder="Prompt name"
          />
        </div>
        <div className="flex gap-3">
          <div className="flex-1">
            <label className="mb-1 block text-xs font-medium text-zinc-500">System Prompt</label>
            <textarea
              rows={3}
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
              placeholder="You are a helpful assistant..."
            />
          </div>
          <div className="flex-1">
            <label className="mb-1 block text-xs font-medium text-zinc-500">User Prompt</label>
            <textarea
              rows={3}
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
              placeholder="Tell me about {{topic}}"
            />
          </div>
        </div>
        <div className="flex gap-3">
          <div className="flex-1">
            <label className="mb-1 block text-xs font-medium text-zinc-500">Pattern</label>
            <select
              value={pattern}
              onChange={(e) => setPattern(e.target.value)}
              className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
            >
              <option value="">None</option>
              {PATTERN_OPTIONS.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-[2]">
            <label className="mb-1 block text-xs font-medium text-zinc-500">
              Variables <span className="font-normal text-zinc-400">(JSON array)</span>
            </label>
            <input
              value={variablesJson}
              onChange={(e) => setVariablesJson(e.target.value)}
              className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
              placeholder='[{"name": "topic", "type": "string"}]'
            />
          </div>
        </div>
        <button
          type="submit"
          className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700"
        >
          Create Prompt
        </button>
      </form>

      {prompts.length === 0 ? (
        <p className="py-12 text-center text-zinc-400">No prompts yet. Create one above.</p>
      ) : (
        <div className="overflow-hidden rounded-lg border border-zinc-200">
          <table className="w-full text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">Name</th>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">Version</th>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">Pattern</th>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">System Prompt</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200">
              {prompts.map((p) => (
                <tr key={p.id} className="group hover:bg-zinc-50">
                  <td className="px-4 py-3">
                    <Link
                      href={`/workspaces/${workspaceId}/projects/${projectId}/sessions/${sessionId}/prompts/${p.id}`}
                      className="font-medium text-zinc-900 hover:underline"
                    >
                      {p.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-zinc-500">v{p.version}</td>
                  <td className="px-4 py-3 text-zinc-500">
                    {p.prompt_pattern ?? <span className="italic text-zinc-300">—</span>}
                  </td>
                  <td className="max-w-xs truncate px-4 py-3 text-zinc-500">
                    {p.system_prompt ?? <span className="italic text-zinc-300">—</span>}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(p.id)}
                      className="text-sm text-red-500 opacity-0 hover:text-red-700 group-hover:opacity-100"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <h2 className="mb-4 mt-10 text-xl font-semibold">Files</h2>

      {filesError && (
        <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {filesError}
        </div>
      )}

      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        className={`mb-6 cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
          dragOver
            ? 'border-zinc-900 bg-zinc-50'
            : 'border-zinc-300 hover:border-zinc-400'
        }`}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleUpload(file);
          }}
        />
        {uploading ? (
          <p className="text-sm text-zinc-500">Uploading...</p>
        ) : (
          <p className="text-sm text-zinc-500">
            Drop a file here or click to browse
          </p>
        )}
      </div>

      {files.length === 0 ? (
        <p className="py-6 text-center text-sm text-zinc-400">No files uploaded yet.</p>
      ) : (
        <div className="overflow-hidden rounded-lg border border-zinc-200">
          <table className="w-full text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">Name</th>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">Type</th>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">Size</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200">
              {files.map((f) => (
                <tr key={f.id} className="group hover:bg-zinc-50">
                  <td className="px-4 py-3">
                    <a
                      href={api.downloadFileUrl(sessionId, f.id)}
                      className="flex items-center gap-2 font-medium text-zinc-900 hover:underline"
                    >
                      <span className="text-sm">{fileIcon(f.mime_type)}</span>
                      {f.original_name}
                    </a>
                  </td>
                  <td className="px-4 py-3 text-zinc-500">{f.mime_type ?? '\u2014'}</td>
                  <td className="px-4 py-3 text-zinc-500">{formatSize(f.size_bytes)}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDeleteFile(f.id)}
                      className="text-sm text-red-500 opacity-0 hover:text-red-700 group-hover:opacity-100"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function Page({
  params,
}: {
  params: Promise<{ workspaceId: string; projectId: string; sessionId: string }>;
}) {
  const [ids, setIds] = useState<{
    workspaceId: string;
    projectId: string;
    sessionId: string;
  } | null>(null);
  useEffect(() => {
    params.then((p) => setIds(p));
  }, [params]);
  if (!ids) return <div className="p-8 text-center text-zinc-400">Loading...</div>;
  return (
    <PromptList
      workspaceId={ids.workspaceId}
      projectId={ids.projectId}
      sessionId={ids.sessionId}
    />
  );
}