export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function analytics<T>(
  path: string,
  repo?: string,
  extra: Record<string, string | number> = {},
): Promise<T> {
  const qs = new URLSearchParams();
  if (repo) qs.set("repository", repo);
  for (const [k, v] of Object.entries(extra)) qs.set(k, String(v));
  const q = qs.toString();
  const res = await fetch(`${API}/api/analytics/${path}${q ? `?${q}` : ""}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`${path} returned ${res.status}`);
  return res.json();
}

export type Repo = { repository: string; prs: number; findings: number };
export type Summary = {
  total_reviews: number;
  total_findings: number;
  avg_findings_per_review: number;
  clean_rate: number;
  high_severity_findings: number;
  repositories: number;
};
export type Severity = { severity: string; count: number };
export type AgentRow = { agent_type: string; high: number; medium: number; low: number; total: number };
export type Day = { day: string; reviews: number; findings: number };
export type Hotspot = { file_path: string; findings: number; high: number; reviews: number };
export type Pattern = { pattern: string; count: number; reviews: number };
export type Developer = { developer: string; prs: number; findings: number; high: number; findings_per_pr: number };
export type Recent = {
  id: string;
  repository: string;
  pr_number: number;
  pr_title: string | null;
  finding_count: number;
  high_count: number;
  created_at: string;
};

export function formatTime(iso: string): string {
  // Server-rendered, so state the zone explicitly instead of guessing the viewer's.
  const d = new Date(iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z");
  return (
    d.toLocaleString("en-GB", { dateStyle: "medium", timeStyle: "short", timeZone: "UTC" }) + " UTC"
  );
}