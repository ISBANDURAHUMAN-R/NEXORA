"use client";

import React, { createContext, useCallback, useContext, useState } from "react";

export interface ToastItem {
  id: number;
  title: string;
  lines?: string[];
  variant?: "xp" | "success" | "info" | "achievement";
}

interface ToastContextValue {
  push: (t: Omit<ToastItem, "id">) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const push = useCallback((t: Omit<ToastItem, "id">) => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { ...t, id }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((x) => x.id !== id));
    }, 4500);
  }, []);

  return (
    <ToastContext.Provider value={{ push }}>
      {children}
      <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-3 w-[320px]">
        {toasts.map((t) => (
          <div
            key={t.id}
            className="glass rounded-xl px-4 py-3 shadow-soft animate-fade-up"
          >
            <div className="flex items-center gap-2">
              <span
                className={
                  "h-1.5 w-1.5 rounded-full " +
                  (t.variant === "xp"
                    ? "bg-accent"
                    : t.variant === "achievement"
                    ? "bg-accent-amber"
                    : "bg-accent-teal")
                }
              />
              <p className="text-sm font-medium text-ink">{t.title}</p>
            </div>
            {t.lines?.map((l, i) => (
              <p key={i} className="text-xs text-ink-muted mt-1 pl-3.5">
                {l}
              </p>
            ))}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
