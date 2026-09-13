"use client";

import { useEffect, useState } from "react";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid,
  BarChart, Bar, PieChart, Pie, Cell,
} from "recharts";
import { api } from "@/lib/api";
import { Analytics } from "@/lib/types";
import { formatDate } from "@/lib/format";
import { Card, Skeleton } from "@/components/ui";
import TopBar from "@/components/TopBar";
import { useMobileMenu } from "@/components/AppShell";
import clsx from "clsx";

const RANGES = [
  { key: "7d", label: "7 Days" },
  { key: "30d", label: "30 Days" },
  { key: "90d", label: "90 Days" },
  { key: "all", label: "All Time" },
];

const PIE_COLORS = ["#7C9CFF", "#35D0BA", "#F0A64B", "#F0637C", "#A9BEFF", "#5B616E", "#9098A8", "#3D4250"];

const tooltipStyle = {
  background: "#15181F",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: 10,
  fontSize: 12,
  color: "#E9EAEE",
};

export default function AnalyticsPage() {
  const openMenu = useMobileMenu();
  const [range, setRange] = useState("30d");
  const [data, setData] = useState<Analytics | null>(null);

  useEffect(() => {
    setData(null);
    api.get<Analytics>(`/api/analytics?range=${range}`).then(setData);
  }, [range]);

  return (
    <>
      <TopBar
        title="Analytics"
        subtitle="Trends across your learning activity"
        onMenu={openMenu}
        right={
          <div className="flex gap-1 glass rounded-lg p-1">
            {RANGES.map((r) => (
              <button
                key={r.key}
                onClick={() => setRange(r.key)}
                className={clsx(
                  "text-xs px-2.5 py-1.5 rounded-md transition-colors",
                  range === r.key ? "bg-accent text-[#0A0B0F]" : "text-ink-muted hover:text-ink"
                )}
              >
                {r.label}
              </button>
            ))}
          </div>
        }
      />
      <main className="px-4 md:px-8 py-6 max-w-7xl mx-auto space-y-4">
        {!data ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-72" />)}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <h2 className="text-sm font-medium text-ink mb-4">XP Over Time</h2>
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={data.xp_over_time}>
                  <defs>
                    <linearGradient id="xpGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#7C9CFF" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="#7C9CFF" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="date" tickFormatter={formatDate} tick={{ fill: "#5B616E", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#5B616E", fontSize: 11 }} axisLine={false} tickLine={false} width={30} />
                  <Tooltip contentStyle={tooltipStyle} labelFormatter={formatDate} />
                  <Area type="monotone" dataKey="xp" stroke="#7C9CFF" fill="url(#xpGrad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </Card>

            <Card>
              <h2 className="text-sm font-medium text-ink mb-4">Learning Hours</h2>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={data.learning_hours}>
                  <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="date" tickFormatter={formatDate} tick={{ fill: "#5B616E", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#5B616E", fontSize: 11 }} axisLine={false} tickLine={false} width={30} />
                  <Tooltip contentStyle={tooltipStyle} labelFormatter={formatDate} />
                  <Bar dataKey="hours" fill="#35D0BA" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card>
              <h2 className="text-sm font-medium text-ink mb-4">Category Distribution</h2>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={data.category_distribution}
                    dataKey="minutes"
                    nameKey="category"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={2}
                  >
                    {data.category_distribution.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} stroke="none" />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex flex-wrap gap-x-4 gap-y-1.5 justify-center mt-2">
                {data.category_distribution.map((c, i) => (
                  <div key={c.category} className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full" style={{ background: PIE_COLORS[i % PIE_COLORS.length] }} />
                    <span className="text-[11px] text-ink-muted">{c.category}</span>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <h2 className="text-sm font-medium text-ink mb-4">Most Practiced Skills</h2>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={data.most_practiced} layout="vertical" margin={{ left: 10 }}>
                  <CartesianGrid stroke="rgba(255,255,255,0.05)" horizontal={false} />
                  <XAxis type="number" tick={{ fill: "#5B616E", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis dataKey="skill" type="category" tick={{ fill: "#9098A8", fontSize: 11 }} axisLine={false} tickLine={false} width={110} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar dataKey="minutes" fill="#7C9CFF" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card className="lg:col-span-2">
              <h2 className="text-sm font-medium text-ink mb-4">Weekly Consistency</h2>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={data.weekly_consistency}>
                  <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="day" tick={{ fill: "#5B616E", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#5B616E", fontSize: 11 }} axisLine={false} tickLine={false} width={30} allowDecimals={false} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar dataKey="sessions" fill="#F0A64B" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </div>
        )}
      </main>
    </>
  );
}
