"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Flame, TrendingUp, Clock, ArrowUpRight, Target } from "lucide-react";
import { api } from "@/lib/api";
import { DashboardData } from "@/lib/types";
import { formatXP, formatDate } from "@/lib/format";
import { Card, StatCard, ProgressBar, Skeleton, Button } from "@/components/ui";
import TopBar from "@/components/TopBar";
import { useMobileMenu } from "@/components/AppShell";

export default function DashboardPage() {
  const openMenu = useMobileMenu();
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<DashboardData>("/api/dashboard")
      .then(setData)
      .catch((e) => setError(e.message || "Failed to load dashboard"));
  }, []);

  return (
    <>
      <TopBar
        title="Dashboard"
        subtitle="Your learning progress at a glance"
        onMenu={openMenu}
      />
      <main className="px-4 md:px-8 py-6 max-w-7xl mx-auto">
        {error && (
          <Card className="mb-6 border-accent-rose/30">
            <p className="text-sm text-accent-rose">
              Could not reach the backend at the configured API URL. {error}
            </p>
          </Card>
        )}

        {!data && !error && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} className="h-28" />
            ))}
          </div>
        )}

        {data && (
          <div className="space-y-6 animate-fade-up">
            {/* Level + XP hero */}
            <Card className="flex flex-col md:flex-row md:items-center gap-6 md:gap-10 bg-gradient-to-br from-white/[0.03] to-transparent">
              <div className="flex items-center gap-5">
                <div className="relative h-20 w-20 shrink-0">
                  <svg viewBox="0 0 80 80" className="h-20 w-20 -rotate-90">
                    <circle cx="40" cy="40" r="34" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="6" />
                    <circle
                      cx="40" cy="40" r="34" fill="none" stroke="#7C9CFF" strokeWidth="6"
                      strokeLinecap="round"
                      strokeDasharray={`${2 * Math.PI * 34}`}
                      strokeDashoffset={`${2 * Math.PI * 34 * (1 - (data.xp_into_level / Math.max(1, data.xp_for_next)))}`}
                      className="transition-all duration-1000 ease-out"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-[10px] text-ink-faint uppercase tracking-wider">Lvl</span>
                    <span className="text-xl font-semibold font-mono">{data.level}</span>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-ink-faint uppercase tracking-wider mb-1">Experience</p>
                  <p className="font-mono text-lg text-ink">
                    {formatXP(data.xp_into_level)} <span className="text-ink-faint">/</span>{" "}
                    {formatXP(data.xp_for_next)} XP
                  </p>
                  <div className="w-56 mt-2">
                    <ProgressBar pct={(data.xp_into_level / Math.max(1, data.xp_for_next)) * 100} />
                  </div>
                </div>
              </div>

              <div className="hidden md:block h-14 w-px bg-border-subtle" />

              <div className="grid grid-cols-3 gap-6 flex-1">
                <div className="flex items-center gap-2.5">
                  <Flame size={18} className="text-accent-amber" />
                  <div>
                    <p className="font-mono text-lg leading-none">{data.current_streak}</p>
                    <p className="text-[11px] text-ink-muted mt-1">day streak</p>
                  </div>
                </div>
                <div className="flex items-center gap-2.5">
                  <TrendingUp size={18} className="text-accent-teal" />
                  <div>
                    <p className="font-mono text-lg leading-none">{formatXP(data.xp_this_week)}</p>
                    <p className="text-[11px] text-ink-muted mt-1">XP this week</p>
                  </div>
                </div>
                <div className="flex items-center gap-2.5">
                  <Clock size={18} className="text-accent" />
                  <div>
                    <p className="font-mono text-lg leading-none">{data.weekly_hours}h</p>
                    <p className="text-[11px] text-ink-muted mt-1">hours this week</p>
                  </div>
                </div>
              </div>
            </Card>

            {/* Skill counts */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard label="Total Skills" value={data.total_skills} />
              <StatCard label="Mastered" value={data.mastered} accent="teal" />
              <StatCard label="In Progress" value={data.in_progress} accent="amber" />
              <StatCard label="Locked" value={data.locked} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Recently improved */}
              <Card className="lg:col-span-1">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-medium text-ink">Recently Improved</h2>
                  <Link href="/learning" className="text-xs text-accent hover:text-accent-soft flex items-center gap-1">
                    View log <ArrowUpRight size={12} />
                  </Link>
                </div>
                {data.recently_improved.length === 0 ? (
                  <p className="text-xs text-ink-muted">No sessions logged yet.</p>
                ) : (
                  <ul className="space-y-3">
                    {data.recently_improved.map((r, i) => (
                      <li key={i} className="flex items-center justify-between text-sm">
                        <div>
                          <p className="text-ink">{r.skill_name}</p>
                          <p className="text-[11px] text-ink-faint">{formatDate(r.date)}</p>
                        </div>
                        <span className="font-mono text-xs text-accent-teal">+{formatXP(r.xp_awarded)} XP</span>
                      </li>
                    ))}
                  </ul>
                )}
              </Card>

              {/* Recommended */}
              <Card className="lg:col-span-1">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-medium text-ink">Recommended Next</h2>
                  <Link href="/skill-tree" className="text-xs text-accent hover:text-accent-soft flex items-center gap-1">
                    Skill tree <ArrowUpRight size={12} />
                  </Link>
                </div>
                {data.recommended.length === 0 ? (
                  <p className="text-xs text-ink-muted">Add skills to get recommendations.</p>
                ) : (
                  <ul className="space-y-3.5">
                    {data.recommended.map((r) => (
                      <li key={r.skill_id}>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-ink">{r.name}</span>
                          <span className="text-[11px] text-ink-faint">{r.category}</span>
                        </div>
                        <p className="text-[11px] text-ink-muted mt-0.5 leading-snug">{r.reason}</p>
                      </li>
                    ))}
                  </ul>
                )}
              </Card>

              {/* Goals */}
              <Card className="lg:col-span-1">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-medium text-ink">Current Goals</h2>
                  <Link href="/goals" className="text-xs text-accent hover:text-accent-soft flex items-center gap-1">
                    All goals <ArrowUpRight size={12} />
                  </Link>
                </div>
                {data.active_goals.length === 0 ? (
                  <div className="text-center py-2">
                    <Target size={20} className="text-ink-faint mx-auto mb-2" />
                    <p className="text-xs text-ink-muted">No active goals yet.</p>
                  </div>
                ) : (
                  <ul className="space-y-4">
                    {data.active_goals.map((g) => (
                      <li key={g.id}>
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-sm text-ink truncate pr-2">{g.title}</span>
                          <span className="text-[11px] font-mono text-ink-muted shrink-0">
                            L{g.current_level}/{g.target_level}
                          </span>
                        </div>
                        <ProgressBar pct={g.progress_pct} color="teal" height="h-1.5" />
                      </li>
                    ))}
                  </ul>
                )}
              </Card>
            </div>
          </div>
        )}
      </main>
    </>
  );
}
