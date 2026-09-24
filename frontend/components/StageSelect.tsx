"use client";

import { useTransition } from "react";
import { moveCandidateStage } from "@/lib/actions";
import { STAGES, STAGE_LABELS, type Stage } from "@/lib/types";

export default function StageSelect({
  candidateId,
  jobId,
  stage,
}: {
  candidateId: string;
  jobId: string;
  stage: Stage;
}) {
  const [isPending, startTransition] = useTransition();

  return (
    <select
      value={stage}
      disabled={isPending}
      onClick={(e) => e.preventDefault()}
      onChange={(e) => {
        const newStage = e.target.value as Stage;
        startTransition(() => {
          moveCandidateStage(candidateId, newStage, jobId);
        });
      }}
      className="w-full rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs font-medium text-slate-600 disabled:opacity-50"
    >
      {STAGES.map((s) => (
        <option key={s} value={s}>
          Move to {STAGE_LABELS[s]}
        </option>
      ))}
    </select>
  );
}
