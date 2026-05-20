'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, Project, Session } from '@/lib/api';

function SessionList({ workspaceId, projectId }: { workspaceId: string; projectId: string }) {
  const [project, setProject] = useState<Project | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');

  useEffect(() => {
    let ignore = false;
    (async () => {
      try {
        const [proj, sess] = await Promise.all([
          api.getProject(workspaceId, projectId),
          api.listSessions(projectId),
        ]);
        if (!ignore) {
          setProject(proj);
          setSessions(sess);
        }
      } catch (err) {
        if (!ignore) setError(err instanceof Error ? err.message : 'Failed to load');
      } finally {
        if (!ignore) setLoading(false);
      }
    })();
    return () => { ignore = true; };
  }, [workspaceId, projectId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await api.createSession(projectId, { name, description: desc || null });
      setName('');
      setDesc('');
      const [proj, sess] = await Promise.all([
        api.getProject(workspaceId, projectId),
        api.listSessions(projectId),
      ]);
      setProject(proj);
      setSessions(sess);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create session');
    }
  };

  const handleDelete = async (id: string) => {
    setError(null);
    try {
      await api.deleteSession(projectId, id);
      const [proj, sess] = await Promise.all([
        api.getProject(workspaceId, projectId),
        api.listSessions(projectId),
      ]);
      setProject(proj);
      setSessions(sess);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete session');
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8">
        <div className="py-12 text-center text-zinc-400">Loading sessions...</div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <Link
        href={`/workspaces/${workspaceId}`}
        className="mb-4 inline-block text-sm text-zinc-500 hover:text-zinc-900"
      >
        &larr; Back to Projects
      </Link>

      {error && project === null ? (
        <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Failed to load: {error}
        </div>
      ) : null}

      {project && (
        <>
          <h1 className="mb-1 text-3xl font-bold tracking-tight">{project.name}</h1>
          {project.description && <p className="mb-6 text-zinc-500">{project.description}</p>}
        </>
      )}

      {error && project !== null && (
        <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <h2 className="mb-4 text-xl font-semibold">Sessions</h2>

      <form onSubmit={handleCreate} className="mb-8 flex flex-wrap items-end gap-3">
        <div className="flex-1">
          <label className="mb-1 block text-xs font-medium text-zinc-500">Name</label>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-500 focus:outline-none"
            placeholder="My Session"
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

      {sessions.length === 0 ? (
        <p className="py-12 text-center text-zinc-400">No sessions yet. Create one above.</p>
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
              {sessions.map((sess) => (
                <tr key={sess.id} className="group hover:bg-zinc-50">
                  <td className="px-4 py-3">
                    <Link
                      href={`/workspaces/${workspaceId}/projects/${projectId}/sessions/${sess.id}`}
                      className="font-medium text-zinc-900 hover:underline"
                    >
                      {sess.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-zinc-500">
                    {sess.description ?? <span className="italic text-zinc-300">—</span>}
                  </td>
                  <td className="px-4 py-3 text-zinc-500">
                    {new Date(sess.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(sess.id)}
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
  params: Promise<{ workspaceId: string; projectId: string }>;
}) {
  const [ids, setIds] = useState<{ workspaceId: string; projectId: string } | null>(null);
  useEffect(() => {
    params.then((p) => setIds(p));
  }, [params]);
  if (!ids) return <div className="p-8 text-center text-zinc-400">Loading...</div>;
  return <SessionList workspaceId={ids.workspaceId} projectId={ids.projectId} />;
}