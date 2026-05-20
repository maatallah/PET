import Link from 'next/link';

export default function Header() {
  return (
    <header className="border-b border-zinc-200">
      <nav className="mx-auto flex h-14 max-w-5xl items-center gap-6 px-4">
        <Link href="/" className="text-lg font-bold tracking-tight">
          PET
        </Link>
        <Link href="/workspaces" className="text-sm text-zinc-600 hover:text-zinc-900">
          Workspaces
        </Link>
      </nav>
    </header>
  );
}
