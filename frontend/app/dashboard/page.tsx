import Link from "next/link";
import { ActivityChart, AgentBars, PatternBars, SeverityDonut } from "../../components/Charts";
import RepoFilter from "../../components/RepoFilter";
import { FindingsBadge, Notice, Panel } from "../../components/ui";
import {
  analytics, type AgentRow, type Day, type Hotspot, type Pattern,
  type Recent, type Repo, type Severity, type Summary,
} from "../../lib/analytics";

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ repo?: string }>;
}) {
  const { repo } = await searchParams;

  try {
    const [repos, summary, severity, agents, timeline, hotspots, patterns, recent] = await Promise.all([
      analytics<Repo[]>("repositories"),
      analytics<Summary>("summary", repo),
      analytics<Severity[]>("severity", repo),
      analytics<AgentRow[]>("agents", repo),
      analytics<Day[]>("timeline", repo, { days: 90 }),
      analytics<Hotspot[]>("hotspots", repo),
      analytics<Pattern[]>("recurring", repo),
      analytics<Recent[]>("recent", repo, { limit: 8 }),
    ]);

    const stats = [
      { label: "Pull requests reviewed", value: summary.total_reviews },
      { label: "Findings raised", value: summary.total_findings, hint: `${summary.avg_findings_per_review} per PR` },
      { label: "High severity", value: summary.high_severity_findings },
      { label: "PRs with no findings", value: `${summary.clean_rate}%` },
    ];

    return (
      <main className="mx-auto max-w-6xl space-y-6 p-8">
        <header className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold">Review analytics</h1>
            <p className="mt-1 text-sm text-muted">
              What the agents are finding. Each pull request is counted once, using its latest review.
            </p>
          </div>
          <RepoFilter repos={repos.map((r) => r.repository)} value={repo} />
        </header>

        <dl className="grid grid-cols-2 divide-border rounded-md border border-border bg-surface md:grid-cols-4 md:divide-x">
          {stats.map((s) => (
            <div key={s.label} className="p-5">
              <dt className="text-sm text-muted">{s.label}</dt>
              <dd className="mt-1 text-3xl font-semibold tabular-nums">{s.value}</dd>
              {s.hint && <p className="mt-1 text-xs text-muted">{s.hint}</p>}
            </div>
          ))}
        </dl>

        <div className="grid gap-6 md:grid-cols-3">
          <div className="md:col-span-2">
            <Panel title="Activity over time" note="Daily reviews and findings, last 90 days.">
              <ActivityChart data={timeline} />
            </Panel>
          </div>
          <Panel title="Severity mix">
            <SeverityDonut data={severity} />
          </Panel>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Panel title="Recurring issues" note="Most common problem types across reviews.">
            <PatternBars data={patterns} />
          </Panel>
          <Panel title="Findings by agent" note="Split by severity.">
            <AgentBars data={agents} />
          </Panel>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Panel title="File hotspots" note="Files that attract the most findings.">
            {hotspots.length === 0 ? (
              <p className="text-sm text-muted">No findings yet.</p>
            ) : (
              <table className="w-full text-sm">
                <thead className="text-left text-muted">
                  <tr>
                    <th className="pb-2 font-medium">File</th>
                    <th className="pb-2 text-right font-medium">Findings</th>
                    <th className="pb-2 text-right font-medium">High</th>
                    <th className="pb-2 text-right font-medium">PRs</th>
                  </tr>
                </thead>
                <tbody>
                  {hotspots.map((h) => (
                    <tr key={h.file_path} className="border-t border-border">
                      <td className="py-2 pr-2">{h.file_path}</td>
                      <td className="py-2 text-right tabular-nums">{h.findings}</td>
                      <td className="py-2 text-right tabular-nums">{h.high}</td>
                      <td className="py-2 text-right tabular-nums">{h.reviews}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Panel>

          <Panel title="Recent reviews">
            <ul className="divide-y divide-border text-sm">
              {recent.map((r) => (
                <li key={r.id} className="flex items-center justify-between gap-3 py-2.5">
                  <Link href={`/reviews/${r.id}`} className="min-w-0 truncate text-accent hover:underline">
                    {r.repository} #{r.pr_number}
                  </Link>
                  <FindingsBadge total={r.finding_count} high={r.high_count} />
                </li>
              ))}
            </ul>
          </Panel>
        </div>
      </main>
    );
  } catch (e) {
    return (
      <main className="mx-auto max-w-3xl p-8">
        <Notice title="Couldn't load analytics">
          The backend didn&apos;t respond correctly ({(e as Error).message}). Check that it&apos;s
          running, that <code>NEXT_PUBLIC_API_URL</code> points to it, and that the analytics router
          is registered in <code>main.py</code>.
        </Notice>
      </main>
    );
  }
}