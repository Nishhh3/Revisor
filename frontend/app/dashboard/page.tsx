"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const SEVERITY_COLORS: Record<string, string> = {
  high: "#b42318",
  medium: "#c77700",
  low: "#5b6b7a",
};

type Summary = {
  total_reviews: number;
  total_findings: number;
  avg_findings_per_review: number;
  clean_rate: number;
  high_severity_findings: number;
  repositories: number;
};
type Severity = { severity: string; count: number };
type AgentRow = { agent_type: string; high: number; medium: number; low: number; total: number };
type Day = { day: string; reviews: number; findings: number };
type Hotspot = { file_path: string; findings: number; high: number; reviews: number };
type Pattern = { pattern: string; count: number; reviews: number };
type Recent = {
  id: string;
  repository: string;
  pr_number: number;
  pr_title: string;
  finding_count: number;
  high_count: number;
  created_at: string;
};

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API}/api/analytics/${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`${path}: ${res.status}`);
  return res.json();
}

function Panel({ title, note, children }: { title: string; note?: string; children: React.ReactNode }) {
  return (
    <section className="rounded border border-neutral-200 bg-white p-5">
      <h2 className="text-base font-semibold text-neutral-900">{title}</h2>
      {note && <p className="mt-1 text-sm text-neutral-500">{note}</p>}
      <div className="mt-4">{children}</div>
    </section>
  );
}

function Stat({ label, value, hint }: { label: string; value: string | number; hint?: string }) {
  return (
    <div className="rounded border border-neutral-200 bg-white p-5">
      <p className="text-sm text-neutral-500">{label}</p>
      <p className="mt-1 text-3xl font-semibold tabular-nums text-neutral-900">{value}</p>
      {hint && <p className="mt-1 text-xs text-neutral-400">{hint}</p>}
    </div>
  );
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [severity, setSeverity] = useState<Severity[]>([]);
  const [agents, setAgents] = useState<AgentRow[]>([]);
  const [timeline, setTimeline] = useState<Day[]>([]);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [recent, setRecent] = useState<Recent[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      get<Summary>("summary"),
      get<Severity[]>("severity"),
      get<AgentRow[]>("agents"),
      get<Day[]>("timeline?days=90"),
      get<Hotspot[]>("hotspots"),
      get<Pattern[]>("recurring"),
      get<Recent[]>("recent"),
    ])
      .then(([s, sev, a, t, h, p, r]) => {
        setSummary(s);
        setSeverity(sev);
        setAgents(a);
        setTimeline(t);
        setHotspots(h);
        setPatterns(p);
        setRecent(r);
      })
      .catch((e) => setError(e.message));
  }, []);

  if (error)
    return (
      <main className="mx-auto max-w-5xl p-8">
        <h1 className="text-xl font-semibold">Couldn't load analytics</h1>
        <p className="mt-2 text-neutral-600">
          The backend at {API} didn't respond correctly ({error}). Check that it's running and that CORS allows this
          origin.
        </p>
      </main>
    );

  if (!summary) return <main className="p-8 text-neutral-500">Loading analytics…</main>;

  return (
    <main className="mx-auto max-w-6xl space-y-6 bg-neutral-50 p-8">
      <header>
        <h1 className="text-2xl font-semibold text-neutral-900">Review analytics</h1>
        <p className="text-sm text-neutral-500">What the agents are finding across your pull requests.</p>
      </header>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Stat label="Pull requests reviewed" value={summary.total_reviews} hint={`${summary.repositories} repositories`} />
        <Stat label="Findings raised" value={summary.total_findings} hint={`${summary.avg_findings_per_review} per PR`} />
        <Stat label="High severity" value={summary.high_severity_findings} />
        <Stat label="PRs with no findings" value={`${summary.clean_rate}%`} />
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2">
          <Panel title="Activity over time" note="Daily reviews and findings.">
            <div className="h-64">
              <ResponsiveContainer>
                <LineChart data={timeline}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                  <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="reviews" stroke="#1f4e79" strokeWidth={2} dot />
                  <Line type="monotone" dataKey="findings" stroke="#b42318" strokeWidth={2} dot />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Panel>
        </div>
        <Panel title="Severity mix">
          <div className="h-64">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={severity} dataKey="count" nameKey="severity" innerRadius={50} outerRadius={85} paddingAngle={2}>
                  {severity.map((s) => (
                    <Cell key={s.severity} fill={SEVERITY_COLORS[s.severity] ?? "#999"} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Panel title="Recurring issues" note="Most common problem types across all reviews.">
          <div className="h-72">
            <ResponsiveContainer>
              <BarChart data={patterns} layout="vertical" margin={{ left: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="pattern" width={180} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#1f4e79" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Findings by agent" note="Split by severity.">
          <div className="h-72">
            <ResponsiveContainer>
              <BarChart data={agents}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                <XAxis dataKey="agent_type" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="high" stackId="a" fill={SEVERITY_COLORS.high} />
                <Bar dataKey="medium" stackId="a" fill={SEVERITY_COLORS.medium} />
                <Bar dataKey="low" stackId="a" fill={SEVERITY_COLORS.low} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Panel title="File hotspots" note="Files that attract the most findings.">
          <table className="w-full text-sm">
            <thead className="text-left text-neutral-500">
              <tr>
                <th className="pb-2 font-medium">File</th>
                <th className="pb-2 text-right font-medium">Findings</th>
                <th className="pb-2 text-right font-medium">High</th>
                <th className="pb-2 text-right font-medium">PRs</th>
              </tr>
            </thead>
            <tbody>
              {hotspots.map((h) => (
                <tr key={h.file_path} className="border-t border-neutral-100">
                  <td className="py-2">{h.file_path}</td>
                  <td className="py-2 text-right tabular-nums">{h.findings}</td>
                  <td className="py-2 text-right tabular-nums">{h.high}</td>
                  <td className="py-2 text-right tabular-nums">{h.reviews}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
        <Panel title="Recent reviews">
          <ul className="divide-y divide-neutral-100 text-sm">
            {recent.map((r) => (
              <li key={r.id} className="flex items-center justify-between gap-3 py-2">
                <Link href={`/reviews/${r.id}`} className="min-w-0 truncate text-[#1f4e79] hover:underline">
                  {r.repository} #{r.pr_number}
                </Link>
                <span className="shrink-0 text-neutral-500">
                  {r.finding_count} findings{r.high_count > 0 && `, ${r.high_count} high`}
                </span>
              </li>
            ))}
          </ul>
        </Panel>
      </div>
    </main>
  );
}