"use client";

import { X, CheckCircle2, XCircle, ArrowRight } from "lucide-react";
import { Skill, RecommendedSkill } from "@/lib/types";
import { ProgressBar, StatusBadge, Button } from "@/components/ui";
import { formatXP } from "@/lib/format";
import Link from "next/link";

export default function SkillDetailPanel({
  skill,
  onClose,
  recommendedNext,
}: {
  skill: Skill;
  onClose: () => void;
  recommendedNext?: RecommendedSkill | null;
}) {
  return (
    <div className="fixed inset-0 z-40 flex justify-end">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <aside className="relative w-full sm:w-[400px] h-full bg-base-panel border-l border-border-subtle overflow-y-auto animate-fade-up">
        <div className="sticky top-0 bg-base-panel/95 backdrop-blur px-5 py-4 border-b border-border-subtle flex items-start justify-between">
          <div>
            <p className="text-[11px] text-ink-faint uppercase tracking-wider mb-1">{skill.category}</p>
            <h2 className="text-lg font-semibold text-ink">{skill.name}</h2>
          </div>
          <button onClick={onClose} className="text-ink-muted hover:text-ink focus-ring rounded" aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <div className="p-5 space-y-6">
          <StatusBadge status={skill.status} />

          {skill.description && (
            <p className="text-sm text-ink-muted leading-relaxed">{skill.description}</p>
          )}

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-ink-faint uppercase tracking-wider">Level</span>
              <span className="font-mono text-sm text-ink">{skill.level} <span className="text-ink-faint">/ {skill.target_level}</span></span>
            </div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-ink-faint uppercase tracking-wider">XP</span>
              <span className="font-mono text-sm text-ink">
                {formatXP(skill.xp_into_level)} / {formatXP(skill.xp_for_next)}
              </span>
            </div>
            <ProgressBar
              pct={skill.progress_pct}
              color={skill.status === "mastered" ? "teal" : skill.status === "in_progress" ? "amber" : "accent"}
            />
            <p className="text-right text-[11px] text-ink-faint mt-1">{skill.progress_pct}%</p>
          </div>

          {skill.prerequisites.length > 0 && (
            <div>
              <p className="text-xs text-ink-faint uppercase tracking-wider mb-2.5">Prerequisites</p>
              <ul className="space-y-2">
                {skill.prerequisites.map((p) => (
                  <li key={p.id} className="flex items-center gap-2 text-sm">
                    {p.met ? (
                      <CheckCircle2 size={15} className="text-accent-teal shrink-0" />
                    ) : (
                      <XCircle size={15} className="text-ink-faint shrink-0" />
                    )}
                    <span className={p.met ? "text-ink" : "text-ink-muted"}>
                      {p.name} <span className="text-ink-faint">(needs Lv{p.required_level})</span>
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {recommendedNext && (
            <div>
              <p className="text-xs text-ink-faint uppercase tracking-wider mb-2.5">Recommended Next</p>
              <div className="glass rounded-xl p-3.5 flex items-center justify-between">
                <div>
                  <p className="text-sm text-ink">{recommendedNext.name}</p>
                  <p className="text-[11px] text-ink-muted mt-0.5">{recommendedNext.reason}</p>
                </div>
                <ArrowRight size={15} className="text-accent shrink-0 ml-2" />
              </div>
            </div>
          )}

          <Link href={`/learning?skill=${skill.id}`}>
            <Button variant="primary" className="w-full">
              Log a Learning Session
            </Button>
          </Link>
        </div>
      </aside>
    </div>
  );
}
