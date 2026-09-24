import Link from "next/link";
import { getDb } from "@/lib/store";
import { STAGES, STAGE_LABELS } from "@/lib/types";
import StatCard from "@/components/StatCard";
import StageBadge from "@/components/StageBadge";
import MatchBadge from "@/components/MatchBadge";
import { FunnelChart, SourcePieChart } from "@/components/Charts";

export const dynamic = "force-dynamic";

function formatDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function DashboardPage() {
  const db = getDb();
  const { jobs, candidates, interviews } = db;

  const openJobs = jobs.filter((j) => j.status === "open");
  const totalCandidates = candidates.length;
  const offersOut = candidates.filter(
    (c) => c.stage === "offer" || c.stage === "hired"
  ).length;

  const hired = candidates.filter((c) => c.stage === "hired");
  const timeToHireDays = hired.map((c) => {
    const applied = c.stageHistory.find((h) => h.stage === "applied");
    const hiredAt = c.stageHistory.find((h) => h.stage === "hired");
    if (!applied || !hiredAt) return null;
    const ms = new Date(hiredAt.at).getTime() - new Date(applied.at).getTime();
    return Math.max(1, Math.round(ms / (1000 * 60 * 60 * 24)));
  }).filter((n): n is number => n !== null);
  const avgTimeToHire =
    timeToHireDays.length > 0
      ? Math.round(
          timeToHireDays.reduce((a, b) => a + b, 0) / timeToHireDays.length
        )
      : null;

  const funnelData = STAGES.filter((s) => s !== "rejected").map((stage) => ({
    stage: STAGE_LABELS[stage],
    count: candidates.filter((c) => c.stage === stage).length,
  }));

  const sourceCounts = candidates.reduce<Record<string, number>>((acc, c) => {
    acc[c.source] = (acc[c.source] ?? 0) + 1;
    return acc;
  }, {});
  const sourceData = Object.entries(sourceCounts).map(([name, value]) => ({
    name,
    value,
  }));

  const upcoming = interviews
    .filter((i) => i.status === "scheduled")
    .sort(
      (a, b) => new Date(a.scheduledAt).getTime() - new Date(b.scheduledAt).getTime()
    );

  const avgMatch =
    candidates.length > 0
      ? Math.round(
          candidates.reduce((a, c) => a + c.match.score, 0) / candidates.length
        )
      : 0;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">
          Recruiting dashboard
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Live snapshot of open roles, AI-matched candidates and hiring
          performance — in the spirit of Datacruit&apos;s ATS reporting.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        <StatCard label="Open jobs" value={String(openJobs.length)} />
        <StatCard label="Total candidates" value={String(totalCandidates)} />
        <StatCard label="Offers extended" value={String(offersOut)} />
        <StatCard
          label="Avg. time to hire"
          value={avgTimeToHire !== null ? `${avgTimeToHire}d` : "—"}
          hint={hired.length === 0 ? "No hires yet" : `${hired.length} hires`}
        />
        <StatCard label="Avg. AI match score" value={`${avgMatch}%`} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card p-5">
          <h2 className="text-sm font-semibold text-slate-700">
            Pipeline funnel
          </h2>
          <p className="mb-2 text-xs text-slate-400">
            Candidates currently in each stage across all jobs
          </p>
          <FunnelChart data={funnelData} />
        </div>
        <div className="card p-5">
          <h2 className="text-sm font-semibold text-slate-700">
            Candidate sources
          </h2>
          <p className="mb-2 text-xs text-slate-400">
            Where applicants are coming from
          </p>
          <SourcePieChart data={sourceData} />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card p-5">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-700">
              Upcoming interviews
            </h2>
            <span className="text-xs text-slate-400">{upcoming.length} scheduled</span>
          </div>
          <ul className="divide-y divide-slate-100">
            {upcoming.length === 0 && (
              <li className="py-3 text-sm text-slate-400">No interviews scheduled.</li>
            )}
            {upcoming.map((i) => {
              const cand = candidates.find((c) => c.id === i.candidateId);
              const job = jobs.find((j) => j.id === i.jobId);
              return (
                <li key={i.id} className="flex items-center justify-between py-3">
                  <div>
                    <Link
                      href={`/candidates/${i.candidateId}`}
                      className="text-sm font-medium text-slate-900 hover:text-brand-600"
                    >
                      {cand?.name ?? "Unknown"}
                    </Link>
                    <p className="text-xs text-slate-400">
                      {job?.title} · {i.type} · {i.interviewer}
                    </p>
                  </div>
                  <span className="text-xs font-medium text-slate-500">
                    {formatDate(i.scheduledAt)}
                  </span>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="card p-5">
          <h2 className="mb-3 text-sm font-semibold text-slate-700">
            Open roles
          </h2>
          <ul className="divide-y divide-slate-100">
            {openJobs.map((j) => {
              const jobCandidates = candidates.filter((c) => c.jobId === j.id);
              const top = [...jobCandidates].sort(
                (a, b) => b.match.score - a.match.score
              )[0];
              return (
                <li key={j.id} className="py-3">
                  <div className="flex items-center justify-between">
                    <Link
                      href={`/jobs/${j.id}`}
                      className="text-sm font-medium text-slate-900 hover:text-brand-600"
                    >
                      {j.title}
                    </Link>
                    <span className="text-xs text-slate-400">
                      {jobCandidates.length} candidates
                    </span>
                  </div>
                  <div className="mt-1 flex items-center justify-between">
                    <p className="text-xs text-slate-400">{j.location}</p>
                    {top && (
                      <div className="flex items-center gap-2">
                        <StageBadge stage={top.stage} />
                        <MatchBadge score={top.match.score} />
                      </div>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    </div>
  );
}
