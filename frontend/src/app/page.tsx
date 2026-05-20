import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-4">
      <main className="flex max-w-2xl flex-col items-center gap-8 text-center">
        <h1 className="text-5xl font-bold tracking-tight">PET</h1>
        <p className="text-lg text-zinc-600">
          Prompt Engineering Tool — transform ideas into well-structured AI prompts.
        </p>
        <div className="flex gap-4">
          <Link
            href="/workspaces"
            className="rounded-lg bg-zinc-900 px-6 py-3 text-sm font-medium text-white hover:bg-zinc-700"
          >
            Get Started
          </Link>
          <Link
            href="/workspaces"
            className="rounded-lg border border-zinc-300 px-6 py-3 text-sm font-medium hover:bg-zinc-100"
          >
            Browse Workspaces
          </Link>
        </div>
      </main>
    </div>
  );
}
