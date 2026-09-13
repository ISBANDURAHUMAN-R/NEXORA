"use client";

import clsx from "clsx";
import { STATUS_COLORS, STATUS_LABELS } from "@/lib/format";

export function Card({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={clsx("glass rounded-2xl p-5", className)}>{children}</div>
  );
}

export function StatCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: React.ReactNode;
  sub?: React.ReactNode;
  accent?: "default" | "teal" | "amber" | "rose";
}) {
  const accentClass =
    accent === "teal"
      ? "text-accent-teal"
      : accent === "amber"
      ? "text-accent-amber"
      : accent === "rose"
      ? "text-accent-rose"
      : "text-ink";
  return (
    <Card className="flex flex-col gap-1.5">
      <span className="text-[11px] uppercase tracking-wider text-ink-faint font-medium">
        {label}
      </span>
      <span className={clsx("text-2xl font-semibold font-mono tabular-nums", accentClass)}>
        {value}
      </span>
      {sub && <span className="text-xs text-ink-muted">{sub}</span>}
    </Card>
  );
}

export function ProgressBar({
  pct,
  color = "accent",
  height = "h-2",
}: {
  pct: number;
  color?: "accent" | "teal" | "amber";
  height?: string;
}) {
  const barColor =
    color === "teal" ? "bg-accent-teal" : color === "amber" ? "bg-accent-amber" : "bg-accent";
  return (
    <div className={clsx("w-full rounded-full bg-white/[0.06] overflow-hidden", height)}>
      <div
        className={clsx(barColor, "h-full rounded-full transition-all duration-700 ease-out")}
        style={{ width: `${Math.min(100, Math.max(0, pct))}%` }}
      />
    </div>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const c = STATUS_COLORS[status] ?? STATUS_COLORS.locked;
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-medium",
        c.text,
        c.bg,
        c.border
      )}
    >
      <span className={clsx("h-1.5 w-1.5 rounded-full", c.dot)} />
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}

export function Button({
  variant = "primary",
  className,
  children,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "ghost" }) {
  return (
    <button
      className={clsx(
        "inline-flex items-center justify-center gap-2 rounded-lg text-sm font-medium px-4 py-2.5 transition-all focus-ring disabled:opacity-40 disabled:cursor-not-allowed",
        variant === "primary" &&
          "bg-accent text-[#0A0B0F] hover:bg-accent-soft active:scale-[0.98]",
        variant === "secondary" &&
          "bg-white/[0.06] text-ink hover:bg-white/[0.1] border border-border-subtle",
        variant === "ghost" && "text-ink-muted hover:text-ink hover:bg-white/[0.04]",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={clsx("animate-pulse rounded-lg bg-white/[0.05]", className)} />;
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <Card className="text-center py-12">
      <p className="text-sm font-medium text-ink">{title}</p>
      <p className="text-xs text-ink-muted mt-1.5 max-w-sm mx-auto">{body}</p>
    </Card>
  );
}
