"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { api, ApiError } from "@/lib/api";
import { Skill, LearningSession } from "@/lib/types";
import { formatXP, formatDate } from "@/lib/format";
import { Card, Button, EmptyState, Skeleton } from "@/components/ui";
import TopBar from "@/components/TopBar";
import { useMobileMenu } from "@/components/AppShell";
import { useToast } from "@/hooks/useToast";

function LearningForm({
  skills,
  onLogged,
}: {
  skills: Skill[];
  onLogged: (s: LearningSession) => void;
}) {
  const searchParams = useSearchParams();
  const preselect = searchParams.get("skill");
  const { push } = useToast();

  const [skillId, setSkillId] = useState<number | "">(preselect ? Number(preselect) : "");
  const [duration, setDuration] = useState(30);
  const [activity, setActivity] = useState("");
  const [difficulty, setDifficulty] = useState<"Easy" | "Medium" | "Hard">("Medium");
  const [notes, setNotes] = useState("");
  const [deepWork, setDeepWork] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (skills.length > 0 && skillId === "") setSkillId(skills[0].id);
  }, [skills]); // eslint-disable-line

  const submit = async () => {
    if (skillId === "") {
      setError("Choose a skill.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const session = await api.post<LearningSession>("/api/learning", {
        skill_id: skillId,
        duration_minutes: duration,
        activity,
        difficulty,
        notes,
        deep_work: deepWork,
      });
      push({
        title: `+${formatXP(session.xp_awarded)} XP — ${session.skill_name}`,
        lines: session.xp_breakdown.map((b) => `+${formatXP(b.amount)} XP — ${b.reason}`),
        variant: "xp",
      });
      setActivity("");
      setNotes("");
      onLogged(session);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to log session.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card className="space-y-4">
      <h2 className="text-sm font-medium text-ink">Log a Session</h2>

      <div>
        <label className="block text-xs text-ink-faint uppercase tracking-wider mb-1.5">Skill</label>
        <select
          value={skillId}
          onChange={(e) => setSkillId(Number(e.target.value))}
          className="input"
        >
          {skills.map((s) => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs text-ink-faint uppercase tracking-wider mb-1.5">Duration (min)</label>
          <input type="number" min={1} max={600} value={duration} onChange={(e) => setDuration(Number(e.target.value))} className="input" />
        </div>
        <div>
          <label className="block text-xs text-ink-faint uppercase tracking-wider mb-1.5">Difficulty</label>
          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value as any)} className="input">
            <option>Easy</option>
            <option>Medium</option>
            <option>Hard</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-xs text-ink-faint uppercase tracking-wider mb-1.5">Activity</label>
        <input value={activity} onChange={(e) => setActivity(e.target.value)} placeholder="e.g. FastAPI practice" className="input" />
      </div>

      <div>
        <label className="block text-xs text-ink-faint uppercase tracking-wider mb-1.5">Notes</label>
        <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} placeholder="Built REST API" className="input resize-none" />
      </div>

      <label className="flex items-center gap-2 text-sm text-ink-muted cursor-pointer">
        <input type="checkbox" checked={deepWork} onChange={(e) => setDeepWork(e.target.checked)} className="accent-accent" />
        Deep work session (+10% XP)
      </label>

      {error && <p className="text-xs text-accent-rose">{error}</p>}

      <Button variant="primary" className="w-full" onClick={submit} disabled={submitting || skills.length === 0}>
        {submitting ? "Saving..." : "Save Session"}
      </Button>

      <style jsx global>{`
        .input {
          width: 100%;
          background: rgba(255,255,255,0.04);
          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 0.5rem;
          padding: 0.55rem 0.75rem;
          font-size: 0.875rem;
          color: #E9EAEE;
          outline: none;
        }
        .input:focus { border-color: #7C9CFF; }
      `}</style>
    </Card>
  );
}

function LearningPageInner() {
  const openMenu = useMobileMenu();
  const [skills, setSkills] = useState<Skill[]>([]);
  const [sessions, setSessions] = useState<LearningSession[] | null>(null);

  const loadSessions = () => api.get<LearningSession[]>("/api/learning").then(setSessions);

  useEffect(() => {
    api.get<Skill[]>("/api/skills").then(setSkills);
    loadSessions();
  }, []);

  return (
    <>
      <TopBar title="Learning" subtitle="Record sessions and review your history" onMenu={openMenu} />
      <main className="px-4 md:px-8 py-6 max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-[380px_1fr] gap-6">
        {skills.length === 0 ? (
          <EmptyState title="No skills yet" body="Create a skill first before logging a session." />
        ) : (
          <LearningForm skills={skills} onLogged={loadSessions} />
        )}

        <div>
          <h2 className="text-sm font-medium text-ink mb-3">History</h2>
          {!sessions ? (
            <div className="space-y-3">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-16" />)}</div>
          ) : sessions.length === 0 ? (
            <EmptyState title="No sessions logged" body="Your learning history will show up here." />
          ) : (
            <div className="space-y-2.5">
              {sessions.map((s) => (
                <Card key={s.id} className="flex items-center justify-between py-3.5">
                  <div className="min-w-0">
                    <p className="text-sm text-ink truncate">{s.skill_name}</p>
                    <p className="text-[11px] text-ink-muted mt-0.5">
                      {s.duration_minutes} min · {s.difficulty} · {formatDate(s.session_date)}
                      {s.activity ? ` · ${s.activity}` : ""}
                    </p>
                  </div>
                  <span className="font-mono text-xs text-accent-teal shrink-0 ml-3">+{formatXP(s.xp_awarded)} XP</span>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  );
}

export default function LearningPage() {
  return (
    <Suspense fallback={null}>
      <LearningPageInner />
    </Suspense>
  );
}
