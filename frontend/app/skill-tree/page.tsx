"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { SkillTree, RecommendedSkill } from "@/lib/types";
import TopBar from "@/components/TopBar";
import { useMobileMenu } from "@/components/AppShell";
import SkillTreeCanvas from "@/components/SkillTreeCanvas";
import SkillDetailPanel from "@/components/SkillDetailPanel";
import { Skeleton } from "@/components/ui";

export default function SkillTreePage() {
  const openMenu = useMobileMenu();
  const [tree, setTree] = useState<SkillTree | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [recommended, setRecommended] = useState<RecommendedSkill[]>([]);

  useEffect(() => {
    api.get<SkillTree>("/api/skill-tree").then(setTree);
    api.get<{ recommended: RecommendedSkill[] }>("/api/dashboard").then((d: any) => setRecommended(d.recommended));
  }, []);

  const selected = tree?.nodes.find((n) => n.id === selectedId) ?? null;
  const recNext = selected
    ? recommended.find((r) => r.skill_id !== selected.id) ?? null
    : null;

  return (
    <>
      <TopBar title="Skill Tree" subtitle="Drag to pan, scroll to zoom, click a node for details" onMenu={openMenu} />
      <main className="px-4 md:px-8 py-6 max-w-7xl mx-auto">
        {!tree ? (
          <Skeleton className="h-[600px]" />
        ) : (
          <div className="h-[calc(100vh-180px)] min-h-[480px]">
            <SkillTreeCanvas
              nodes={tree.nodes}
              edges={tree.edges}
              selectedId={selectedId}
              onSelect={setSelectedId}
            />
          </div>
        )}
      </main>

      {selected && (
        <SkillDetailPanel skill={selected} onClose={() => setSelectedId(null)} recommendedNext={recNext} />
      )}
    </>
  );
}
