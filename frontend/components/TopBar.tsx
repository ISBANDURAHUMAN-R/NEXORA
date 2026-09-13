"use client";

import { Menu } from "lucide-react";

export default function TopBar({
  title,
  subtitle,
  onMenu,
  right,
}: {
  title: string;
  subtitle?: string;
  onMenu: () => void;
  right?: React.ReactNode;
}) {
  return (
    <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-border-subtle bg-base/80 backdrop-blur-md px-4 md:px-8 py-4">
      <button
        onClick={onMenu}
        className="md:hidden text-ink-muted hover:text-ink focus-ring rounded"
        aria-label="Open navigation"
      >
        <Menu size={20} />
      </button>
      <div className="flex-1 min-w-0">
        <h1 className="text-[17px] font-semibold tracking-tight text-ink truncate">{title}</h1>
        {subtitle && <p className="text-xs text-ink-muted mt-0.5">{subtitle}</p>}
      </div>
      {right}
    </header>
  );
}
