import type { Stage } from "@/lib/types";
import { STAGE_LABELS } from "@/lib/types";

const COLORS: Record<Stage, string> = {
  applied: "bg-slate-100 text-slate-700",
  screening: "bg-sky-100 text-sky-700",
  interview: "bg-violet-100 text-violet-700",
  offer: "bg-amber-100 text-amber-700",
  hired: "bg-emerald-100 text-emerald-700",
  rejected: "bg-rose-100 text-rose-700",
};

export default function StageBadge({ stage }: { stage: Stage }) {
  return <span className={`badge ${COLORS[stage]}`}>{STAGE_LABELS[stage]}</span>;
}
