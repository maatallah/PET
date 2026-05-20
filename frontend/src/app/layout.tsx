import type { Metadata } from 'next';
import './globals.css';
import Header from '@/components/header';
import DebugWrapper from '@/components/debug-wrapper';

export const metadata: Metadata = {
  title: 'PET — Prompt Engineering Tool',
  description: 'Transform ideas into well-structured AI prompts',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="flex min-h-full flex-col">
        <Header />
        <main className="flex flex-1 flex-col">{children}</main>
        <DebugWrapper />
      </body>
    </html>
  );
}