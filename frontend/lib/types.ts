export type SkillStatus = "locked" | "available" | "in_progress" | "mastered";

export interface Prerequisite {
  id: number;
  name: string;
  required_level: number;
  met: boolean;
}

export interface Skill {
  id: number;
  name: string;
  category: string;
  description: string;
  level: number;
  xp: number;
  xp_for_next: number;
  xp_into_level: number;
  progress_pct: number;
  target_level: number;
  status: SkillStatus;
  pos_x: number;
  pos_y: number;
  prerequisites: Prerequisite[];
}

export interface TreeEdge {
  from: number;
  to: number;
  met: boolean;
}

export interface SkillTree {
  nodes: Skill[];
  edges: TreeEdge[];
}

export interface XPBreakdownItem {
  reason: string;
  amount: number;
}

export interface LearningSession {
  id: number;
  skill_id: number;
  skill_name: string;
  duration_minutes: number;
  activity: string;
  difficulty: "Easy" | "Medium" | "Hard";
  notes: string;
  xp_awarded: number;
  xp_breakdown: XPBreakdownItem[];
  deep_work: boolean;
  session_date: string;
}

export interface Goal {
  id: number;
  title: string;
  skill_id: number | null;
  skill_name: string | null;
  target_level: number;
  deadline_days: number;
  current_level: number;
  progress_pct: number;
  completed: boolean;
  created_at: string;
}

export interface Achievement {
  code: string;
  name: string;
  description: string;
  icon: string;
  unlocked: boolean;
  unlocked_at: string | null;
}

export interface RecommendedSkill {
  skill_id: number;
  name: string;
  category: string;
  level: number;
  status: SkillStatus;
  score: number;
  reason: string;
}

export interface DashboardData {
  level: number;
  xp: number;
  xp_for_next: number;
  xp_into_level: number;
  total_skills: number;
  mastered: number;
  in_progress: number;
  locked: number;
  available: number;
  current_streak: number;
  longest_streak: number;
  xp_this_week: number;
  weekly_hours: number;
  recently_improved: {
    skill_id: number;
    skill_name: string;
    xp_awarded: number;
    date: string;
  }[];
  recommended: RecommendedSkill[];
  active_goals: {
    id: number;
    title: string;
    target_level: number;
    current_level: number;
    progress_pct: number;
    deadline_days: number;
  }[];
}

export interface Analytics {
  xp_over_time: { date: string; xp: number }[];
  learning_hours: { date: string; hours: number }[];
  category_distribution: { category: string; minutes: number }[];
  most_practiced: { skill: string; minutes: number }[];
  skill_growth: { skill: string; level: number; category: string }[];
  weekly_consistency: { day: string; sessions: number }[];
}
