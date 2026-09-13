export function formatXP(xp: number): string {
  return Math.round(xp).toLocaleString("en-US");
}

export function formatDate(iso: string): string {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export const STATUS_COLORS: Record<string, { text: string; bg: string; border: string; dot: string }> = {
  locked: { text: "text-ink-faint", bg: "bg-white/[0.02]", border: "border-white/[0.06]", dot: "bg-ink-faint" },
  available: { text: "text-accent-soft", bg: "bg-accent/[0.06]", border: "border-accent/30", dot: "bg-accent" },
  in_progress: { text: "text-accent-amber", bg: "bg-accent-amber/[0.08]", border: "border-accent-amber/30", dot: "bg-accent-amber" },
  mastered: { text: "text-accent-teal", bg: "bg-accent-teal/[0.08]", border: "border-accent-teal/30", dot: "bg-accent-teal" },
};

export const STATUS_LABELS: Record<string, string> = {
  locked: "Locked",
  available: "Available",
  in_progress: "In Progress",
  mastered: "Mastered",
};

export const CATEGORIES = [
  "Programming",
  "AI/ML",
  "Data Science",
  "Cybersecurity",
  "Design",
  "Communication",
  "Mathematics",
  "Business",
  "Custom",
];
