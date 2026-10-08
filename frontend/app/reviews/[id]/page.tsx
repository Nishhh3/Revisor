import Link from "next/link";
import { getReview } from "../../../lib/api";

const SEVERITY_STYLES: Record<string, string> = {
  high: "bg-red-950/40 text-red-300 border-red-800",
  medium: "bg-yellow-950/40 text-yellow-300 border-yellow-800",
  low: "bg-green-950/40 text-green-300 border-green-800",
};

export default async function ReviewDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const review = await getReview(id);

  return (
    <main className="max-w-3xl mx-auto p-8">
      <Link href="/" className="text-sm text-gray-400 hover:underline">
        ← Back to reviews
      </Link>

      <h1 className="text-2xl font-semibold mt-4">{review.pr_title || "Untitled PR"}</h1>
      <p className="text-sm text-gray-400 mb-6">
        {review.repository} · PR #{review.pr_number}
      </p>

      {review.findings.length === 0 ? (
        <p className="text-gray-400">No issues found in this PR. ✅</p>
      ) : (
        <div className="space-y-4">
          {review.findings.map((finding) => (
            <div
              key={finding.id}
              className={`border rounded-lg p-4 ${SEVERITY_STYLES[finding.severity] || "bg-gray-800 border-gray-700"}`}
            >
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-semibold uppercase">{finding.severity}</span>
                {finding.file_path && (
                  <code className="text-xs bg-black/30 text-gray-200 px-2 py-1 rounded">
                    {finding.file_path}
                  </code>
                )}
              </div>
              <p className="text-sm">{finding.issue}</p>
              {finding.recommendation && (
                <p className="text-sm mt-2 text-gray-300">
                  <strong>Suggested fix:</strong> {finding.recommendation}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </main>
  );
}