import Link from "next/link";
import RepoFilter from "../components/RepoFilter";
import { FindingsBadge, Notice } from "../components/ui";
import { analytics, formatTime, type Recent, type Repo } from "../lib/analytics";

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<{ repo?: string }>;
}) {
  const { repo } = await searchParams;

  let reviews: Recent[];
  let repos: Repo[];
  try {
    [repos, reviews] = await Promise.all([
      analytics<Repo[]>("repositories"),
      analytics<Recent[]>("recent", repo, { limit: 100 }),
    ]);
  } catch (e) {
    return (
      <main className="mx-auto max-w-3xl p-8">
        <Notice title="Couldn't load reviews">
          The backend didn&apos;t respond correctly ({(e as Error).message}). If it was idle, wait a
          minute and refresh.
        </Notice>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl p-8">
      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Pull request reviews</h1>
          <p className="mt-1 text-sm text-muted">Latest review for each pull request.</p>
        </div>
        <RepoFilter repos={repos.map((r) => r.repository)} value={repo} />
      </div>

      {reviews.length === 0 ? (
        <Notice title="No reviews yet">
          Open a pull request in a repository that sends webhooks to PRISM and its review will
          show up here.
        </Notice>
      ) : (
        <ul className="space-y-3">
          {reviews.map((r) => (
            <li key={r.id}>
              <Link
                href={`/reviews/${r.id}`}
                className="block rounded-md border border-border bg-surface p-4 transition-colors hover:border-accent"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <p className="truncate font-medium">{r.pr_title || "Untitled PR"}</p>
                    <p className="text-sm text-muted">
                      {r.repository}, PR #{r.pr_number}
                    </p>
                  </div>
                  <FindingsBadge total={r.finding_count} high={r.high_count} />
                </div>
                <p className="mt-2 text-xs text-muted">
                  <time dateTime={r.created_at}>{formatTime(r.created_at)}</time>
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}