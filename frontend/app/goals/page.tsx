"use client";

import { useEffect, useState } from "react";
import { Plus, X, Target } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { Goal, Skill } from "@/lib/types";
import { Card, ProgressBar, Button, EmptyState, Skeleton } from "@/components/ui";
import TopBar from "@/components/TopBar";
import { useMobileMenu } from "@/components/AppShell";
import { useToast } from "@/hooks/useToast";

function CreateGoalModal({
  skills,
  onClose,
  onCreated,
}: {
  skills: Skill[];
  onClose: () => void;
  onCreated: (g: Goal) => void;
}) {
  const [title, setTitle] = useState("");
  const [skillId, setSkillId] = useState<number | "">("");
  const [targetLevel, setTargetLevel] = useState(10);
  const [deadlineDays, setDeadlineDays] = useState(90);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const submit = async () => {
    if (!title.trim()) {
      setError("Give your goal a title.");
      return;
    }
    setSubmitting(true);
    try {
      const goal = await api.post<Goal>("/api/goals", {
        title: title.trim(),
        skill_id: skillId === "" ? null : skillId,
        target_level: targetLevel,
        deadline_days: deadlineDays,
      });
      onCreated(goal);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to create goal.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div className="relative w-full max-w-md glass rounded-2xl p-6 animate-pop">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-base font-semibold text-ink">New Goal</h2>
          <button onClick={onClose} className="text-ink-muted hover:text-ink"><X size={18} /></button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-xs text-ink-faint uppercase tracking-wider mb-1.5">Goal</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Master Machine Learning" className="input" />
          </div>
          <div>
            <label className="block text-xs text-ink-faint uppercase tracking-wider mb-1.5">Linked Skill (optional)</label>
            <select value={skillId} onChange={(e) => setSkillId(e.target.value ? Number(e.target.value) : "")} className="input">
              <option value="">None</option>
              {skills.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-ink-faint uppercase tracking-wider mb-1.5">Target Level</label>
              <input type="number" min={1} max={100} value={targetLevel} onChange={(e) => setTargetLevel(Number(e.target.value))} className="input" />
            </div>
            <div>
              <label className="block text-xs text-ink-faint uppercase tracking-wider mb-1.5">Deadline (days)</label>
              <input type="number" min={1} max={365} value={deadlineDays} onChange={(e) => setDeadlineDays(Number(e.target.value))} className="input" />
            </div>
          </div>
          {error && <p className="text-xs text-accent-rose">{error}</p>}
          <div className="flex gap-3 pt-2">
            <Button variant="secondary" className="flex-1" onClick={onClose}>Cancel</Button>
            <Button variant="primary" className="flex-1" onClick={submit} disabled={submitting}>
              {submitting ? "Creating..." : "Create Goal"}
            </Button>
          </div>
        </div>
      </div>
      <style jsx global>{`
        .input { width: 100%; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
          border-radius: 0.5rem; padding: 0.55rem 0.75rem; font-size: 0.875rem; color: #E9EAEE; outline: none; }
        .input:focus { border-color: #7C9CFF; }
      `}</style>
    </div>
  );
}

export default function GoalsPage() {
  const openMenu = useMobileMenu();
  const { push } = useToast();
  const [goals, setGoals] = useState<Goal[] | null>(null);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [showCreate, setShowCreate] = useState(false);

  const load = () => api.get<Goal[]>("/api/goals").then(setGoals);

  useEffect(() => {
    load();
    api.get<Skill[]>("/api/skills").then(setSkills);
  }, []);

  const remove = async (id: number, title: string) => {
    if (!confirm(`Delete goal "${title}"?`)) return;
    await api.del(`/api/goals/${id}`);
    push({ title: "Goal removed", lines: [title] });
    load();
  };

  return (
    <>
      <TopBar
        title="Goals"
        subtitle="Targets that connect to your learning activity"
        onMenu={openMenu}
        right={<Button variant="primary" onClick={() => setShowCreate(true)}><Plus size={15} /> New Goal</Button>}
      />
      <main className="px-4 md:px-8 py-6 max-w-4xl mx-auto">
        {!goals ? (
          <div className="space-y-3">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-24" />)}</div>
        ) : goals.length === 0 ? (
          <EmptyState title="No goals set" body="Create a goal to track long-term progress toward mastering a skill." />
        ) : (
          <div className="space-y-3">
            {goals.map((g) => (
              <Card key={g.id} className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-xl bg-accent/10 flex items-center justify-center shrink-0">
                  <Target size={18} className="text-accent" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1.5">
                    <p className="text-sm text-ink truncate">{g.title}</p>
                    <span className="text-[11px] text-ink-faint shrink-0 ml-2">{g.deadline_days}-day target</span>
                  </div>
                  <ProgressBar pct={g.progress_pct} color="teal" height="h-1.5" />
                  <p className="text-[11px] text-ink-muted mt-1.5">
                    {g.skill_name ? `${g.skill_name} · ` : ""}Level {g.current_level} of {g.target_level}
                  </p>
                </div>
                <button onClick={() => remove(g.id, g.title)} className="text-ink-faint hover:text-accent-rose shrink-0">
                  <X size={16} />
                </button>
              </Card>
            ))}
          </div>
        )}
      </main>

      {showCreate && (
        <CreateGoalModal
          skills={skills}
          onClose={() => setShowCreate(false)}
          onCreated={(g) => {
            setShowCreate(false);
            push({ title: "Goal created", lines: [g.title] });
            load();
          }}
        />
      )}
    </>
  );
}
