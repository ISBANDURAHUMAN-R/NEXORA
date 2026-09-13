"use client";

import { useEffect, useState } from "react";
import { Footprints, Flame, Brain, ArrowUpCircle, Award, Layers, Lock } from "lucide-react";
import clsx from "clsx";
import { api } from "@/lib/api";
import { Achievement } from "@/lib/types";
import { Card, Skeleton } from "@/components/ui";
import TopBar from "@/components/TopBar";
import { useMobileMenu } from "@/components/AppShell";

const ICONS: Record<string, any> = {
  footprints: Footprints,
  flame: Flame,
  brain: Brain,
  "arrow-up-circle": ArrowUpCircle,
  award: Award,
  layers: Layers,
};

export default function AchievementsPage() {
  const openMenu = useMobileMenu();
  const [achievements, setAchievements] = useState<Achievement[] | null>(null);

  useEffect(() => {
    api.get<Achievement[]>("/api/achievements").then(setAchievements);
  }, []);

  const unlockedCount = achievements?.filter((a) => a.unlocked).length ?? 0;

  return (
    <>
      <TopBar
        title="Achievements"
        subtitle={achievements ? `${unlockedCount} of ${achievements.length} unlocked` : undefined}
        onMenu={openMenu}
      />
      <main className="px-4 md:px-8 py-6 max-w-5xl mx-auto">
        {!achievements ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-28" />)}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {achievements.map((a) => {
              const Icon = ICONS[a.icon] ?? Award;
              return (
                <Card
                  key={a.code}
                  className={clsx(
                    "flex items-start gap-3.5 transition-all",
                    !a.unlocked && "opacity-50"
                  )}
                >
                  <div
                    className={clsx(
                      "h-10 w-10 rounded-xl flex items-center justify-center shrink-0",
                      a.unlocked ? "bg-accent-amber/10 text-accent-amber" : "bg-white/5 text-ink-faint"
                    )}
                  >
                    {a.unlocked ? <Icon size={18} /> : <Lock size={16} />}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-ink">{a.name}</p>
                    <p className="text-[11.5px] text-ink-muted mt-0.5 leading-relaxed">{a.description}</p>
                    {a.unlocked && a.unlocked_at && (
                      <p className="text-[10.5px] text-accent-teal mt-1.5 font-mono">Unlocked</p>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </main>
    </>
  );
}
