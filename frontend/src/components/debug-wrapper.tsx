'use client';

import { useState } from 'react';
import DebugPanel from './debug-panel';

export default function DebugWrapper() {
  const [showDebug, setShowDebug] = useState(false);

  return (
    <>
      {showDebug && <DebugPanel visible onToggle={() => setShowDebug(false)} />}
      <button
        onClick={() => setShowDebug(true)}
        className="fixed bottom-2 right-2 z-[99999] rounded border border-cyan-400 bg-slate-900 px-2.5 py-1 text-xs font-medium text-cyan-400 shadow-lg hover:bg-slate-800"
      >
        Debug
      </button>
    </>
  );
}