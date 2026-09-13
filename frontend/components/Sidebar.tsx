"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  GitBranch,
  ListTree,
  BookOpen,
  BarChart3,
  Target,
  Trophy,
  Settings,
  Sparkles,
  X,
} from "lucide-react";
import clsx from "clsx";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/skill-tree", label: "Skill Tree", icon: GitBranch },
  { href: "/skills", label: "Skills", icon: ListTree },
  { href: "/learning", label: "Learning", icon: BookOpen },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/goals", label: "Goals", icon: Target },
  { href: "/achievements", label: "Achievements", icon: Trophy },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar({
  mobileOpen,
  onClose,
}: {
  mobileOpen: boolean;
  onClose: () => void;
}) {
  const pathname = usePathname();

  const content = (
    <>
      <div className="flex items-center justify-between px-5 pt-6 pb-8">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-accent to-accent-teal flex items-center justify-center shadow-glow">
            <Sparkles size={16} className="text-base" strokeWidth={2.5} />
          </div>
          <span className="font-semibold tracking-tight text-[15px]">SkillTree</span>
        </div>
        <button
          onClick={onClose}
          className="md:hidden text-ink-muted hover:text-ink"
          aria-label="Close navigation"
        >
          <X size={18} />
        </button>
      </div>
      <nav className="flex-1 px-3 space-y-0.5">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              onClick={onClose}
              className={clsx(
                "group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors focus-ring",
                active
                  ? "bg-white/[0.06] text-ink"
                  : "text-ink-muted hover:text-ink hover:bg-white/[0.03]"
              )}
            >
              <Icon
                size={17}
                strokeWidth={2}
                className={active ? "text-accent" : "text-ink-faint group-hover:text-ink-muted"}
              />
              <span>{label}</span>
              {active && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-accent" />}
            </Link>
          );
        })}
      </nav>
      <div className="px-5 py-5 mt-auto">
        <div className="glass rounded-xl p-3.5">
          <p className="text-xs text-ink-muted leading-relaxed">
            Demo data active. Progress resets from Settings.
          </p>
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden md:flex md:flex-col md:w-64 md:shrink-0 border-r border-border-subtle bg-base-panel/60">
        {content}
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={onClose} />
          <aside className="absolute left-0 top-0 bottom-0 w-72 flex flex-col bg-base-panel border-r border-border-subtle animate-fade-up">
            {content}
          </aside>
        </div>
      )}
    </>
  );
}
