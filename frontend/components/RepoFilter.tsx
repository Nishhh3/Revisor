"use client";

import { usePathname, useRouter } from "next/navigation";

export default function RepoFilter({ repos, value }: { repos: string[]; value?: string }) {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <label className="flex items-center gap-2 text-sm text-muted">
      Repository
      <select
        value={value ?? ""}
        onChange={(e) =>
          router.push(e.target.value ? `${pathname}?repo=${encodeURIComponent(e.target.value)}` : pathname)
        }
        className="rounded border border-border bg-surface px-2 py-1 text-foreground"
      >
        <option value="">All repositories</option>
        {repos.map((r) => (
          <option key={r} value={r}>
            {r}
          </option>
        ))}
      </select>
    </label>
  );
}