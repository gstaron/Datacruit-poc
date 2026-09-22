import Link from "next/link";
import { notFound } from "next/navigation";
import { getDb } from "@/lib/store";
import KanbanBoard from "@/components/KanbanBoard";

export const dynamic = "force-dynamic";

export default function JobDetailPage({ params }: { params: { id: string } }) {
  const db = getDb();
  const job = db.jobs.find((j) => j.id === params.id);
  if (!job) notFound();

  const candidates = db.candidates.filter((c) => c.jobId === job.id);

  return (
    <div className="space-y-6">
      <div>
        <Link href="/jobs" className="text-sm text-slate-400 hover:text-slate-600">
          ← All jobs
        </Link>
        <div className="mt-2 flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">{job.title}</h1>
            <p className="text-sm text-slate-500">
              {job.department} · {job.location} · {job.employmentType}
            </p>
          </div>
          <Link
            href={`/apply/${job.id}`}
            className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
          >
            + Add candidate
          </Link>
        </div>
        <p className="mt-3 max-w-3xl text-sm text-slate-600">{job.description}</p>
        <div className="mt-3 flex flex-wrap gap-4 text-xs">
          <div>
            <span className="font-semibold text-slate-500">Must-have: </span>
            {job.mustHave.map((s) => (
              <span key={s} className="badge mr-1 bg-slate-100 text-slate-600">
                {s}
              </span>
            ))}
          </div>
          <div>
            <span className="font-semibold text-slate-500">Nice-to-have: </span>
            {job.niceToHave.map((s) => (
              <span key={s} className="badge mr-1 bg-brand-50 text-brand-600">
                {s}
              </span>
            ))}
          </div>
        </div>
      </div>

      <KanbanBoard jobId={job.id} candidates={candidates} />
    </div>
  );
}
