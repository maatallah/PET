'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';

function WorkspacesList() {
  const [workspaces, setWorkspaces] = useState<{ id: string; name: string; description: string | null; created_at: string }[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');

  useEffect(() => {
    let ignore = false;
    (async () => {
      try {
        const data = await api.listWorkspaces();
        if (!ignore) setWorkspaces(data);
      } catch (err) {
        if (!ignore) setError(err instanceof Error ? err.message : 'Failed to load');
      } finally {
        if (!ignore) setLoading(false);
      }
    })();
    return () => { ignore = true; };
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await api.createWorkspace({ name, description: desc || null });
      setName('');
      setDesc('');
      const data = await api.listWorkspaces();
      setWorkspaces(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create workspace');
    }
  };

  const handleDelete = async (id: string) => {
    setError(null);
    try {
      await api.deleteWorkspace(id);
      const data = await api.listWorkspaces();
      setWorkspaces(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete workspace');
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8">
        <div className="py-12 text-center text-zinc-400">Loading workspaces...</div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-6 text-3xl font-bold tracking-tight">Workspaces</h1>

      {error && (
        <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleCreate} className="mb-8 flex flex-wrap items-end gap-3">
        <div className="flex-1">
          <label className="mb-1 block text-xs font-medium text-zinc-500">Name</label>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
            placeholder="My Workspace"
          />
        </div>
        <div className="flex-[2]">
          <label className="mb-1 block text-xs font-medium text-zinc-500">Description</label>
          <input
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
            className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
            placeholder="Optional description"
          />
        </div>
        <button
          type="submit"
          className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700"
        >
          Create
        </button>
      </form>

      {workspaces.length === 0 ? (
        <p className="py-12 text-center text-zinc-400">No workspaces yet. Create one above.</p>
      ) : (
        <div className="overflow-hidden rounded-lg border border-zinc-200">
          <table className="w-full text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">Name</th>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">Description</th>
                <th className="px-4 py-3 text-left font-medium text-zinc-500">Created</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200">
              {workspaces.map((ws) => (
                <tr key={ws.id} className="group hover:bg-zinc-50">
                  <td className="px-4 py-3">
                    <Link
                      href={`/workspaces/${ws.id}`}
                      className="font-medium text-zinc-900 hover:underline"
                    >
                      {ws.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-zinc-500">
                    {ws.description ?? <span className="italic text-zinc-300">—</span>}
                  </td>
                  <td className="px-4 py-3 text-zinc-500">
                    {new Date(ws.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(ws.id)}
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

export default function WorkspacesPage() {
  return <WorkspacesList />;
}