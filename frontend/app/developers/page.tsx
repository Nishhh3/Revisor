import RepoFilter from "../../components/RepoFilter";
import { Notice, Panel } from "../../components/ui";
import { analytics, type Developer, type Repo } from "../../lib/analytics";

export default async function DevelopersPage({
  searchParams,
}: {
  searchParams: Promise<{ repo?: string }>;
}) {
  const { repo } = await searchParams;

  try {
    const [repos, devs] = await Promise.all([
      analytics<Repo[]>("repositories"),
      analytics<Developer[]>("developers", repo),
    ]);
    const maxRate = Math.max(1, ...devs.map((d) => Number(d.findings_per_pr)));

    return (
      <main className="mx-auto max-w-4xl space-y-6 p-8">
        <header className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold">Developers</h1>
            <p className="mt-1 text-sm text-muted">
              Authors are shown as anonymised IDs. Reviews from before author tracking was added
              aren&apos;t included.
            </p>
          </div>
          <RepoFilter repos={repos.map((r) => r.repository)} value={repo} />
        </header>

        <Panel title="Findings per pull request" note="A higher rate means more issues caught per PR.">
          {devs.length === 0 ? (
            <Notice title="No author data yet">
              New pull requests record a hashed author. Open one and it will appear here.
            </Notice>
          ) : (
            <table className="w-full text-sm">
              <thead className="text-left text-muted">
                <tr>
                  <th className="pb-2 font-medium">Developer</th>
                  <th className="pb-2 text-right font-medium">PRs</th>
                  <th className="pb-2 text-right font-medium">Findings</th>
                  <th className="pb-2 text-right font-medium">High</th>
                  <th className="w-40 pb-2 pl-6 font-medium">Per PR</th>
                </tr>
              </thead>
              <tbody>
                {devs.map((d) => (
                  <tr key={d.developer} className="border-t border-border">
                    <td className="py-2.5 font-mono text-xs">{d.developer.slice(0, 8)}</td>
                    <td className="py-2.5 text-right tabular-nums">{d.prs}</td>
                    <td className="py-2.5 text-right tabular-nums">{d.findings}</td>
                    <td className="py-2.5 text-right tabular-nums">{d.high}</td>
                    <td className="py-2.5 pl-6">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 flex-1 rounded bg-border">
                          <div
                            className="h-1.5 rounded bg-accent"
                            style={{ width: `${(Number(d.findings_per_pr) / maxRate) * 100}%` }}
                          />
                        </div>
                        <span className="w-8 text-right tabular-nums">{d.findings_per_pr}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Panel>
      </main>
    );
  } catch (e) {
    return (
      <main className="mx-auto max-w-3xl p-8">
        <Notice title="Couldn't load developers">
          The backend didn&apos;t respond correctly ({(e as Error).message}).
        </Notice>
      </main>
    );
  }
}