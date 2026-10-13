const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Finding {
  id: string;
  agent_type: string;
  severity: "high" | "medium" | "low";
  file_path: string | null;
  issue: string;
  recommendation: string | null;
  created_at: string;
}

export interface ReviewSummary {
  id: string;
  repository: string;
  pr_number: number;
  pr_title: string | null;
  finding_count: number;
  created_at: string;
}

export interface ReviewDetail extends ReviewSummary {
  findings: Finding[];
}

export async function getReviews(): Promise<ReviewSummary[]> {
  const res = await fetch(`${API_BASE_URL}/api/reviews`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch reviews");
  return res.json();
}

export async function getReview(id: string): Promise<ReviewDetail> {
  const res = await fetch(`${API_BASE_URL}/api/reviews/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch review");
  return res.json();
}