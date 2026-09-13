"use client";

import { useRef, useState, useCallback, WheelEvent, MouseEvent } from "react";
import { Lock, CheckCircle2, Loader2, Circle, ZoomIn, ZoomOut, Maximize2 } from "lucide-react";
import clsx from "clsx";
import { Skill, TreeEdge } from "@/lib/types";

const NODE_W = 168;
const NODE_H = 64;

const STATUS_STYLE: Record<string, { border: string; glow: string; text: string; icon: JSX.Element }> = {
  locked: {
    border: "stroke-white/10",
    glow: "",
    text: "fill-ink-faint",
    icon: <Lock size={13} />,
  },
  available: {
    border: "stroke-accent/70",
    glow: "drop-shadow-[0_0_10px_rgba(124,156,255,0.35)]",
    text: "fill-accent-soft",
    icon: <Circle size={13} />,
  },
  in_progress: {
    border: "stroke-accent-amber/70",
    glow: "drop-shadow-[0_0_10px_rgba(240,166,75,0.3)]",
    text: "fill-accent-amber",
    icon: <Loader2 size={13} />,
  },
  mastered: {
    border: "stroke-accent-teal/80",
    glow: "drop-shadow-[0_0_12px_rgba(53,208,186,0.4)]",
    text: "fill-accent-teal",
    icon: <CheckCircle2 size={13} />,
  },
};

export default function SkillTreeCanvas({
  nodes,
  edges,
  selectedId,
  onSelect,
}: {
  nodes: Skill[];
  edges: TreeEdge[];
  selectedId: number | null;
  onSelect: (id: number) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [transform, setTransform] = useState({ x: 60, y: 40, scale: 0.85 });
  const dragState = useRef<{ dragging: boolean; startX: number; startY: number; origX: number; origY: number }>({
    dragging: false, startX: 0, startY: 0, origX: 0, origY: 0,
  });

  const nodeById = new Map(nodes.map((n) => [n.id, n]));

  const clampScale = (s: number) => Math.min(2, Math.max(0.35, s));

  const onWheel = useCallback((e: WheelEvent) => {
    e.preventDefault();
    const delta = -e.deltaY * 0.0015;
    setTransform((t) => ({ ...t, scale: clampScale(t.scale + delta) }));
  }, []);

  const onMouseDown = (e: MouseEvent) => {
    dragState.current = {
      dragging: true,
      startX: e.clientX,
      startY: e.clientY,
      origX: transform.x,
      origY: transform.y,
    };
  };
  const onMouseMove = (e: MouseEvent) => {
    if (!dragState.current.dragging) return;
    const dx = e.clientX - dragState.current.startX;
    const dy = e.clientY - dragState.current.startY;
    setTransform((t) => ({ ...t, x: dragState.current.origX + dx, y: dragState.current.origY + dy }));
  };
  const endDrag = () => {
    dragState.current.dragging = false;
  };

  const zoom = (dir: 1 | -1) => setTransform((t) => ({ ...t, scale: clampScale(t.scale + dir * 0.15) }));
  const reset = () => setTransform({ x: 60, y: 40, scale: 0.85 });

  return (
    <div
      ref={containerRef}
      className="relative h-full w-full overflow-hidden rounded-2xl border border-border-subtle bg-[#0B0C11] cursor-grab active:cursor-grabbing"
      onWheel={onWheel}
      onMouseDown={onMouseDown}
      onMouseMove={onMouseMove}
      onMouseUp={endDrag}
      onMouseLeave={endDrag}
    >
      <div
        className="absolute inset-0"
        style={{
          backgroundImage:
            "radial-gradient(rgba(255,255,255,0.05) 1px, transparent 1px)",
          backgroundSize: "26px 26px",
        }}
      />

      <svg
        className="absolute inset-0 h-full w-full select-none"
        style={{ touchAction: "none" }}
      >
        <g transform={`translate(${transform.x} ${transform.y}) scale(${transform.scale})`}>
          {/* edges */}
          {edges.map((e, i) => {
            const from = nodeById.get(e.from);
            const to = nodeById.get(e.to);
            if (!from || !to) return null;
            const x1 = from.pos_x + NODE_W / 2;
            const y1 = from.pos_y + NODE_H;
            const x2 = to.pos_x + NODE_W / 2;
            const y2 = to.pos_y;
            const midY = (y1 + y2) / 2;
            return (
              <path
                key={i}
                d={`M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`}
                fill="none"
                stroke={e.met ? "rgba(124,156,255,0.45)" : "rgba(255,255,255,0.08)"}
                strokeWidth={1.5}
              />
            );
          })}

          {/* nodes */}
          {nodes.map((n) => {
            const style = STATUS_STYLE[n.status] ?? STATUS_STYLE.locked;
            const selected = n.id === selectedId;
            return (
              <g
                key={n.id}
                transform={`translate(${n.pos_x} ${n.pos_y})`}
                className="cursor-pointer"
                onClick={(ev) => {
                  ev.stopPropagation();
                  onSelect(n.id);
                }}
              >
                <rect
                  width={NODE_W}
                  height={NODE_H}
                  rx={14}
                  className={clsx(
                    "fill-[#14161D] transition-all",
                    style.border,
                    style.glow,
                    selected && "stroke-2"
                  )}
                  strokeWidth={selected ? 2 : 1.3}
                  style={{
                    stroke: selected ? "#7C9CFF" : undefined,
                  }}
                />
                <foreignObject x={0} y={0} width={NODE_W} height={NODE_H}>
                  <div className="h-full w-full flex flex-col justify-center px-3.5 py-1.5 pointer-events-none">
                    <div className="flex items-center justify-between">
                      <span className="text-[12.5px] font-medium text-ink truncate max-w-[105px]">
                        {n.name}
                      </span>
                      <span className={clsx("shrink-0", style.text.replace("fill-", "text-"))}>
                        {style.icon}
                      </span>
                    </div>
                    <div className="mt-1.5 flex items-center gap-1.5">
                      <div className="h-1 flex-1 rounded-full bg-white/[0.08] overflow-hidden">
                        <div
                          className={clsx(
                            "h-full rounded-full",
                            n.status === "mastered" ? "bg-accent-teal" :
                            n.status === "in_progress" ? "bg-accent-amber" :
                            n.status === "available" ? "bg-accent" : "bg-white/20"
                          )}
                          style={{ width: `${n.status === "locked" ? 0 : n.progress_pct}%` }}
                        />
                      </div>
                      <span className="text-[10px] font-mono text-ink-faint shrink-0">Lv{n.level}</span>
                    </div>
                  </div>
                </foreignObject>
              </g>
            );
          })}
        </g>
      </svg>

      <div className="absolute bottom-4 right-4 flex flex-col gap-1.5">
        <button onClick={() => zoom(1)} className="glass h-8 w-8 rounded-lg flex items-center justify-center text-ink-muted hover:text-ink" aria-label="Zoom in">
          <ZoomIn size={15} />
        </button>
        <button onClick={() => zoom(-1)} className="glass h-8 w-8 rounded-lg flex items-center justify-center text-ink-muted hover:text-ink" aria-label="Zoom out">
          <ZoomOut size={15} />
        </button>
        <button onClick={reset} className="glass h-8 w-8 rounded-lg flex items-center justify-center text-ink-muted hover:text-ink" aria-label="Reset view">
          <Maximize2 size={13} />
        </button>
      </div>

      <div className="absolute top-4 left-4 flex flex-wrap gap-3 glass rounded-lg px-3 py-2">
        {Object.entries({ locked: "Locked", available: "Available", in_progress: "In Progress", mastered: "Mastered" }).map(
          ([key, label]) => (
            <div key={key} className="flex items-center gap-1.5">
              <span
                className={clsx(
                  "h-1.5 w-1.5 rounded-full",
                  key === "locked" && "bg-white/20",
                  key === "available" && "bg-accent",
                  key === "in_progress" && "bg-accent-amber",
                  key === "mastered" && "bg-accent-teal"
                )}
              />
              <span className="text-[10.5px] text-ink-muted">{label}</span>
            </div>
          )
        )}
      </div>
    </div>
  );
}
