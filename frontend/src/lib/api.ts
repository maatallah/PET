const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as T;
}

function buildQuery(params: Record<string, string | number | undefined>): string {
  const entries = Object.entries(params).filter(([, v]) => v !== undefined);
  if (entries.length === 0) return '';
  return '?' + new URLSearchParams(entries.map(([k, v]) => [k, String(v)])).toString();
}

export interface Workspace {
  id: string;
  name: string;
  description: string | null;
  owner_id: string | null;
  created_at: string;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  icon: string | null;
  archived: boolean;
  workspace_id: string;
  created_at: string;
}

export interface Session {
  id: string;
  name: string;
  description: string | null;
  tags: string[] | null;
  project_id: string;
  created_at: string;
}

export interface Prompt {
  id: string;
  version: number;
  name: string;
  system_prompt: string | null;
  user_prompt: string | null;
  variables: { name: string; type: string }[] | null;
  prompt_pattern: string | null;
  model_id: string | null;
  model_params: Record<string, unknown> | null;
  tokens_input: number | null;
  tokens_output: number | null;
  cost_estimate: number | null;
  tags: string[] | null;
  session_id: string;
  parent_version_id: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface ExecuteResult {
  resolved_prompt: string;
  tokens_input: number | null;
  tokens_output: number | null;
  cost_estimate: number | null;
  response?: string;
}

export const api = {
  // Workspaces
  listWorkspaces: (skip = 0, limit = 100) =>
    request<Workspace[]>(`/workspaces${buildQuery({ skip, limit })}`),

  getWorkspace: (id: string) => request<Workspace>(`/workspaces/${id}`),

  createWorkspace: (data: { name: string; description?: string | null }) =>
    request<Workspace>('/workspaces', { method: 'POST', body: JSON.stringify(data) }),

  updateWorkspace: (id: string, data: { name?: string; description?: string | null }) =>
    request<Workspace>(`/workspaces/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),

  deleteWorkspace: (id: string) => request<void>(`/workspaces/${id}`, { method: 'DELETE' }),

  // Projects
  listProjects: (workspaceId: string, skip = 0, limit = 100) =>
    request<Project[]>(`/workspaces/${workspaceId}/projects${buildQuery({ skip, limit })}`),

  createProject: (
    workspaceId: string,
    data: { name: string; description?: string | null; icon?: string | null },
  ) =>
    request<Project>(`/workspaces/${workspaceId}/projects`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Sessions
  listSessions: (projectId: string, skip = 0, limit = 100) =>
    request<Session[]>(`/projects/${projectId}/sessions${buildQuery({ skip, limit })}`),

  createSession: (
    projectId: string,
    data: { name: string; description?: string | null; tags?: string[] | null },
  ) =>
    request<Session>(`/projects/${projectId}/sessions`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Prompts
  listPrompts: (sessionId: string, skip = 0, limit = 100) =>
    request<Prompt[]>(`/sessions/${sessionId}/prompts${buildQuery({ skip, limit })}`),

  createPrompt: (
    sessionId: string,
    data: {
      name: string;
      system_prompt?: string | null;
      user_prompt?: string | null;
      variables?: { name: string; type: string }[] | null;
      prompt_pattern?: string | null;
      model_id?: string | null;
      model_params?: Record<string, unknown> | null;
    },
  ) =>
    request<Prompt>(`/sessions/${sessionId}/prompts`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

// Single GET
   getProject: (workspaceId: string, id: string) =>
     request<Project>(`/workspaces/${workspaceId}/projects/${id}`),
   getSession: (projectId: string, id: string) =>
     request<Session>(`/projects/${projectId}/sessions/${id}`),
   getPrompt: (sessionId: string, id: string) =>
     request<Prompt>(`/sessions/${sessionId}/prompts/${id}`),

   // Deletes
   deleteProject: (workspaceId: string, id: string) =>
     request<void>(`/workspaces/${workspaceId}/projects/${id}`, { method: 'DELETE' }),
   deleteSession: (projectId: string, id: string) =>
     request<void>(`/projects/${projectId}/sessions/${id}`, { method: 'DELETE' }),
   deletePrompt: (sessionId: string, id: string) =>
     request<void>(`/sessions/${sessionId}/prompts/${id}`, { method: 'DELETE' }),

  // Execute
  executePrompt: (
    sessionId: string,
    promptId: string,
    data: { variables?: Record<string, string>; dry_run?: boolean; provider?: string },
  ) =>
    request<ExecuteResult>(`/sessions/${sessionId}/prompts/${promptId}/execute`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Files
  listFiles: (sessionId: string) => request<FileInfo[]>(`/sessions/${sessionId}/files`),

  uploadFile: async (sessionId: string, file: File) => {
    const form = new FormData();
    form.append('upload', file);
    const res = await fetch(`${BASE_URL}/sessions/${sessionId}/files`, {
      method: 'POST',
      body: form,
    });
    if (!res.ok) {
      const body = await res.text();
      throw new Error(`${res.status} ${res.statusText}: ${body}`);
    }
    return res.json() as Promise<FileInfo>;
  },

  deleteFile: (sessionId: string, fileId: string) =>
    request<void>(`/sessions/${sessionId}/files/${fileId}`, { method: 'DELETE' }),

  getFile: (sessionId: string, fileId: string) =>
    request<FileInfo>(`/sessions/${sessionId}/files/${fileId}`),

  downloadFileUrl: (sessionId: string, fileId: string) =>
    `${BASE_URL}/sessions/${sessionId}/files/${fileId}/download`,

  // Health
  health: () => request<{ status: string }>('/health'),
};

export interface FileInfo {
  id: string;
  filename: string;
  original_name: string;
  mime_type: string | null;
  size_bytes: number | null;
  content_text: string | null;
  file_metadata: Record<string, unknown> | null;
  session_id: string;
  created_at: string;
}

type LoadResult<T> = { data: T; error: null } | { data: null; error: string };

export async function loadData<T>(fn: () => Promise<T>): Promise<LoadResult<T>> {
  try {
    const data = await fn();
    return { data, error: null };
  } catch (e) {
    return { data: null, error: (e as Error).message };
  }
}
