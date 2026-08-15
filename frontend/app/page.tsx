import Link from "next/link";
import { getReviews } from "../lib/api";

export default async function HomePage() {
  const reviews = await getReviews();

  return (
    <main className="max-w-3xl mx-auto p-8">
      <h1 className="text-2xl font-semibold mb-6">PRISM Reviews</h1>

      {reviews.length === 0 ? (
        <p className="text-gray-500">No reviews yet.</p>
      ) : (
        <div className="space-y-3">
          {reviews.map((review) => (
            <Link
              key={review.id}
              href={`/reviews/${review.id}`}
              className="block border rounded-lg p-4 hover:bg-gray-50 transition"
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium">{review.pr_title || "Untitled PR"}</p>
                  <p className="text-sm text-gray-500">
                    {review.repository} · PR #{review.pr_number}
                  </p>
                </div>
                <span className="text-sm bg-gray-100 rounded-full px-3 py-1">
                  {review.finding_count} finding{review.finding_count !== 1 ? "s" : ""}
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                {new Date(review.created_at).toLocaleString()}
              </p>
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}