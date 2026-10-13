import type { ReactNode } from "react";

export function Panel({ title, note, children }: { title: string; note?: string; children: ReactNode }) {
  return (
    <section className="rounded-md border border-border bg-surface p-5">
      <h2 className="text-base font-semibold">{title}</h2>
      {note && <p className="mt-1 text-sm text-muted">{note}</p>}
      <div className="mt-4">{children}</div>
    </section>
  );
}

export function Notice({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-md border border-border bg-surface p-5">
      <h2 className="font-semibold">{title}</h2>
      <div className="mt-2 text-sm text-muted">{children}</div>
    </div>
  );
}

export function FindingsBadge({ total, high }: { total: number; high: number }) {
  if (total === 0) {
    return <span className="rounded border border-border px-2 py-0.5 text-xs text-muted">No findings</span>;
  }
  return (
    <span className="flex items-center gap-1.5 text-xs">
      {high > 0 && <span className="rounded bg-high/15 px-2 py-0.5 font-medium text-high">{high} high</span>}
      <span className="rounded border border-border px-2 py-0.5 text-muted">
        {total} finding{total !== 1 ? "s" : ""}
      </span>
    </span>
  );
}