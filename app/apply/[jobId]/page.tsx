import Link from "next/link";
import { notFound } from "next/navigation";
import { getDb } from "@/lib/store";
import { applyToJob } from "@/lib/actions";

export const dynamic = "force-dynamic";

export default function ApplyPage({ params }: { params: { jobId: string } }) {
  const db = getDb();
  const job = db.jobs.find((j) => j.id === params.jobId);
  if (!job) notFound();

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <Link
          href={`/jobs/${job.id}`}
          className="text-sm text-slate-400 hover:text-slate-600"
        >
          ← Back to {job.title}
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">
          Apply for {job.title}
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Paste a resume below — our AI parser will extract skills and score
          the candidate against this role&apos;s requirements automatically,
          the way Datacruit&apos;s CV analysis works.
        </p>
      </div>

      <form action={applyToJob} className="card space-y-4 p-6">
        <input type="hidden" name="jobId" value={job.id} />
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="text-xs font-medium text-slate-500">Full name</label>
            <input
              name="name"
              required
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-500">Email</label>
            <input
              type="email"
              name="email"
              required
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-500">Phone</label>
            <input
              name="phone"
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-500">
              Years of experience
            </label>
            <input
              type="number"
              name="experienceYears"
              min={0}
              defaultValue={2}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <div className="sm:col-span-2">
            <label className="text-xs font-medium text-slate-500">Source</label>
            <select
              name="source"
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              defaultValue="Career Site"
            >
              <option>Career Site</option>
              <option>LinkedIn</option>
              <option>Job Board</option>
              <option>Referral</option>
              <option>Agency</option>
            </select>
          </div>
        </div>
        <div>
          <label className="text-xs font-medium text-slate-500">
            Resume text (paste instead of uploading a file for this PoC)
          </label>
          <textarea
            name="resumeText"
            required
            rows={8}
            placeholder="Paste the candidate's resume or a summary of their experience..."
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <button
          type="submit"
          className="w-full rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          Submit application & run AI matching
        </button>
      </form>
    </div>
  );
}
