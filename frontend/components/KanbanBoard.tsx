import Link from "next/link";
import type { Candidate } from "@/lib/types";
import { STAGES, STAGE_LABELS } from "@/lib/types";
import MatchBadge from "./MatchBadge";
import StageSelect from "./StageSelect";

export default function KanbanBoard({
  jobId,
  candidates,
}: {
  jobId: string;
  candidates: Candidate[];
}) {
  return (
    <div className="grid grid-flow-col auto-cols-[260px] gap-4 overflow-x-auto pb-2">
      {STAGES.map((stage) => {
        const inStage = candidates
          .filter((c) => c.stage === stage)
          .sort((a, b) => b.match.score - a.match.score);
        return (
          <div key={stage} className="flex flex-col">
            <div className="mb-2 flex items-center justify-between px-1">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                {STAGE_LABELS[stage]}
              </h3>
              <span className="text-xs text-slate-400">{inStage.length}</span>
            </div>
            <div className="flex flex-1 flex-col gap-2 rounded-lg bg-slate-100/70 p-2">
              {inStage.length === 0 && (
                <p className="px-1 py-2 text-xs text-slate-400">No candidates</p>
              )}
              {inStage.map((c) => (
                <div key={c.id} className="card space-y-2 p-3">
                  <Link
                    href={`/candidates/${c.id}`}
                    className="block text-sm font-medium text-slate-900 hover:text-brand-600"
                  >
                    {c.name}
                  </Link>
                  <p className="text-xs text-slate-400">
                    {c.experienceYears} yrs · {c.source}
                  </p>
                  <MatchBadge score={c.match.score} />
                  <StageSelect candidateId={c.id} jobId={jobId} stage={c.stage} />
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
