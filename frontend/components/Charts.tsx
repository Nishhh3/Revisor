"use client";

import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart,
  Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import type { AgentRow, Day, Pattern, Severity } from "../lib/analytics";

const tick = { fontSize: 11, fill: "var(--muted)" };
const grid = "var(--border)";
const tooltipStyle = {
  background: "var(--surface)",
  border: "1px solid var(--border)",
  borderRadius: 6,
  fontSize: 12,
  color: "var(--foreground)",
};
const legendStyle = { fontSize: 12, color: "var(--muted)" };
const SEVERITY: Record<string, string> = {
  high: "var(--high)",
  medium: "var(--medium)",
  low: "var(--low)",
};

function Empty() {
  return <p className="text-sm text-muted">Nothing to chart yet.</p>;
}

export function ActivityChart({ data }: { data: Day[] }) {
  if (!data.length) return <Empty />;
  return (
    <div className="h-64">
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke={grid} />
          <XAxis dataKey="day" tick={tick} />
          <YAxis allowDecimals={false} tick={tick} />
          <Tooltip contentStyle={tooltipStyle} />
          <Legend wrapperStyle={legendStyle} />
          <Line type="monotone" dataKey="reviews" name="PRs reviewed" stroke="var(--accent)" strokeWidth={2} />
          <Line type="monotone" dataKey="findings" stroke="var(--high)" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function SeverityDonut({ data }: { data: Severity[] }) {
  if (!data.length) return <Empty />;
  return (
    <div className="h-64">
      <ResponsiveContainer>
        <PieChart>
          <Pie data={data} dataKey="count" nameKey="severity" innerRadius={50} outerRadius={85} paddingAngle={2} stroke="none">
            {data.map((s) => (
              <Cell key={s.severity} fill={SEVERITY[s.severity] ?? "var(--muted)"} />
            ))}
          </Pie>
          <Tooltip contentStyle={tooltipStyle} />
          <Legend wrapperStyle={legendStyle} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export function PatternBars({ data }: { data: Pattern[] }) {
  if (!data.length) return <Empty />;
  return (
    <div className="h-72">
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={grid} />
          <XAxis type="number" allowDecimals={false} tick={tick} />
          <YAxis type="category" dataKey="pattern" width={190} tick={tick} />
          <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "var(--border)", opacity: 0.4 }} />
          <Bar dataKey="count" name="Findings" fill="var(--accent)" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function AgentBars({ data }: { data: AgentRow[] }) {
  if (!data.length) return <Empty />;
  return (
    <div className="h-72">
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke={grid} />
          <XAxis dataKey="agent_type" tick={tick} />
          <YAxis allowDecimals={false} tick={tick} />
          <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "var(--border)", opacity: 0.4 }} />
          <Legend wrapperStyle={legendStyle} />
          <Bar dataKey="high" stackId="a" fill={SEVERITY.high} />
          <Bar dataKey="medium" stackId="a" fill={SEVERITY.medium} />
          <Bar dataKey="low" stackId="a" fill={SEVERITY.low} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}