"use client";

import { useEffect, useMemo, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Skill } from "@/lib/types";
import { CATEGORIES } from "@/lib/format";
import { Card, ProgressBar, StatusBadge, Button, Skeleton, EmptyState } from "@/components/ui";
import TopBar from "@/components/TopBar";
import { useMobileMenu } from "@/components/AppShell";
import CreateSkillModal from "@/components/CreateSkillModal";
import { useToast } from "@/hooks/useToast";

export default function SkillsPage() {
  const openMenu = useMobileMenu();
  const { push } = useToast();
  const [skills, setSkills] = useState<Skill[] | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>("All");
  const [showCreate, setShowCreate] = useState(false);

  const load = () => api.get<Skill[]>("/api/skills").then(setSkills);

  useEffect(() => {
    load();
  }, []);

  const filtered = useMemo(() => {
    if (!skills) return [];
    return categoryFilter === "All" ? skills : skills.filter((s) => s.category === categoryFilter);
  }, [skills, categoryFilter]);

  const remove = async (id: number, name: string) => {
    if (!confirm(`Delete "${name}"? This cannot be undone.`)) return;
    await api.del(`/api/skills/${id}`);
    push({ title: "Skill deleted", lines: [name] });
    load();
  };

  return (
    <>
      <TopBar
        title="Skills"
        subtitle="All tracked skills and their progress"
        onMenu={openMenu}
        right={
          <Button variant="primary" onClick={() => setShowCreate(true)}>
            <Plus size={15} /> New Skill
          </Button>
        }
      />
      <main className="px-4 md:px-8 py-6 max-w-7xl mx-auto">
        <div className="flex flex-wrap gap-2 mb-5">
          {["All", ...CATEGORIES].map((c) => (
            <button
              key={c}
              onClick={() => setCategoryFilter(c)}
              className={
                "text-xs px-3 py-1.5 rounded-full border transition-colors " +
                (categoryFilter === c
                  ? "border-accent/40 bg-accent/10 text-accent-soft"
                  : "border-border-subtle text-ink-muted hover:text-ink")
              }
            >
              {c}
            </button>
          ))}
        </div>

        {!skills ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-40" />)}
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState title="No skills here yet" body="Create a skill to start tracking progress toward it." />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((s) => (
              <Card key={s.id} className="flex flex-col gap-3 group">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-[11px] text-ink-faint uppercase tracking-wider">{s.category}</p>
                    <h3 className="text-sm font-medium text-ink mt-0.5">{s.name}</h3>
                  </div>
                  <button
                    onClick={() => remove(s.id, s.name)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity text-ink-faint hover:text-accent-rose"
                    aria-label={`Delete ${s.name}`}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>

                <StatusBadge status={s.status} />

                <div>
                  <div className="flex items-center justify-between text-[11px] text-ink-muted mb-1">
                    <span>Level {s.level} / {s.target_level}</span>
                    <span className="font-mono">{s.progress_pct}%</span>
                  </div>
                  <ProgressBar
                    pct={s.progress_pct}
                    color={s.status === "mastered" ? "teal" : s.status === "in_progress" ? "amber" : "accent"}
                    height="h-1.5"
                  />
                </div>

                <Link href={`/learning?skill=${s.id}`} className="mt-auto">
                  <Button variant="secondary" className="w-full text-xs py-2">Log Session</Button>
                </Link>
              </Card>
            ))}
          </div>
        )}
      </main>

      {showCreate && (
        <CreateSkillModal
          skills={skills ?? []}
          onClose={() => setShowCreate(false)}
          onCreated={(s) => {
            setShowCreate(false);
            push({ title: "Skill created", lines: [s.name] });
            load();
          }}
        />
      )}
    </>
  );
}
