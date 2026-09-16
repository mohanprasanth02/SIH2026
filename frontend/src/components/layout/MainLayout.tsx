import type { ReactNode } from 'react';
import { TopCommandBar } from './TopCommandBar';

interface Props {
  children: ReactNode;
}

export function MainLayout({ children }: Props) {
  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#F7F8F5] text-[#151918] relative">
      {/* ── Floating Top Navigation ── */}
      <TopCommandBar />

      {/* ── Main Viewport Container (Allows full vertical scrolling) ── */}
      <main className="flex-1 w-full h-full overflow-y-auto overflow-x-hidden relative">
        {children}
      </main>
    </div>
  );
}
