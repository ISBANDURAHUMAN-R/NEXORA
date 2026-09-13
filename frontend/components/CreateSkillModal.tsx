"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { Skill } from "@/lib/types";
import { CATEGORIES } from "@/lib/format";
import { Button } from "@/components/ui";

export default function CreateSkillModal({
  skills,
  onClose,
  onCreated,
}: {
  skills: Skill[];
  onClose: () => void;
  onCreated: (s: Skill) => void;
}) {
  const [name, setName] = useState("");
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [description, setDescription] = useState("");
  const [currentLevel, setCurrentLevel] = useState(1);
  const [targetLevel, setTargetLevel] = useState(10);
  const [prereqIds, setPrereqIds] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const togglePrereq = (id: number) => {
    setPrereqIds((prev) => (prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]));
  };

  const submit = async () => {
    if (!name.trim()) {
      setError("Skill name is required.");
      return;
    }
    if (targetLevel < currentLevel) {
      setError("Target level must be greater than or equal to current level.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const skill = await api.post<Skill>("/api/skills", {
        name: name.trim(),
        category,
        description,
        current_level: currentLevel,
        target_level: targetLevel,
        prerequisites: prereqIds.map((id) => ({ prerequisite_id: id, required_level: 3 })),
        pos_x: 40 + Math.random() * 600,
        pos_y: 40 + Math.random() * 400,
      });
      onCreated(skill);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to create skill.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60" onClick={onClose} />
      <div className="relative w-full max-w-md glass rounded-2xl p-6 animate-pop max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-base font-semibold text-ink">New Skill</h2>
          <button onClick={onClose} className="text-ink-muted hover:text-ink" aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <div className="space-y-4">
          <Field label="Skill Name">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Reinforcement Learning"
              className="input"
            />
          </Field>

          <Field label="Category">
            <select value={category} onChange={(e) => setCategory(e.target.value)} className="input">
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </Field>

          <Field label="Description">
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What does mastering this skill look like?"
              rows={2}
              className="input resize-none"
            />
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Current Level">
              <input
                type="number" min={1} max={100} value={currentLevel}
                onChange={(e) => setCurrentLevel(Number(e.target.value))}
                className="input"
              />
            </Field>
            <Field label="Target Level">
              <input
                type="number" min={1} max={100} value={targetLevel}
                onChange={(e) => setTargetLevel(Number(e.target.value))}
                className="input"
              />
            </Field>
          </div>

          {skills.length > 0 && (
            <Field label="Prerequisites (optional)">
              <div className="max-h-32 overflow-y-auto space-y-1.5 pr-1">
                {skills.map((s) => (
                  <label key={s.id} className="flex items-center gap-2 text-sm text-ink-muted cursor-pointer">
                    <input
                      type="checkbox"
                      checked={prereqIds.includes(s.id)}
                      onChange={() => togglePrereq(s.id)}
                      className="accent-accent"
                    />
                    {s.name}
                  </label>
                ))}
              </div>
            </Field>
          )}

          {error && <p className="text-xs text-accent-rose">{error}</p>}

          <div className="flex gap-3 pt-2">
            <Button variant="secondary" className="flex-1" onClick={onClose}>Cancel</Button>
            <Button variant="primary" className="flex-1" onClick={submit} disabled={submitting}>
              {submitting ? "Creating..." : "Create Skill"}
            </Button>
          </div>
        </div>
      </div>

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
        .input:focus {
          border-color: #7C9CFF;
        }
      `}</style>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs text-ink-faint uppercase tracking-wider mb-1.5">{label}</label>
      {children}
    </div>
  );
}
