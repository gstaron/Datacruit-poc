import Link from "next/link";
import { getDb } from "@/lib/store";
import { createJob } from "@/lib/actions";

export const dynamic = "force-dynamic";

export default function JobsPage() {
  const db = getDb();

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Jobs & pipelines</h1>
          <p className="mt-1 text-sm text-slate-500">
            Manage open roles and track every candidate through the hiring pipeline.
          </p>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {db.jobs.map((job) => {
          const candidates = db.candidates.filter((c) => c.jobId === job.id);
          const active = candidates.filter(
            (c) => c.stage !== "rejected" && c.stage !== "hired"
          ).length;
          return (
            <Link
              key={job.id}
              href={`/jobs/${job.id}`}
              className="card block p-5 transition hover:border-brand-300 hover:shadow-md"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="font-semibold text-slate-900">{job.title}</h2>
                  <p className="text-sm text-slate-500">
                    {job.department} · {job.location}
                  </p>
                </div>
                <span
                  className={`badge ${
                    job.status === "open"
                      ? "bg-emerald-100 text-emerald-700"
                      : "bg-slate-100 text-slate-500"
                  }`}
                >
                  {job.status === "open" ? "Open" : "Closed"}
                </span>
              </div>
              <p className="mt-3 line-clamp-2 text-sm text-slate-500">
                {job.description}
              </p>
              <div className="mt-4 flex flex-wrap gap-1.5">
                {job.mustHave.slice(0, 5).map((s) => (
                  <span key={s} className="badge bg-slate-100 text-slate-600">
                    {s}
                  </span>
                ))}
              </div>
              <div className="mt-4 flex items-center justify-between text-xs text-slate-400">
                <span>{candidates.length} candidates · {active} active</span>
                <span>{job.employmentType}</span>
              </div>
            </Link>
          );
        })}
      </div>

      <details className="card p-5">
        <summary className="cursor-pointer text-sm font-semibold text-slate-700">
          + Post a new job
        </summary>
        <form action={createJob} className="mt-4 grid gap-3 sm:grid-cols-2">
          <input
            name="title"
            placeholder="Job title"
            required
            className="rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <input
            name="department"
            placeholder="Department"
            required
            className="rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <input
            name="location"
            placeholder="Location"
            required
            className="rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <select
            name="employmentType"
            className="rounded-md border border-slate-300 px-3 py-2 text-sm"
            defaultValue="Full-time"
          >
            <option>Full-time</option>
            <option>Part-time</option>
            <option>Contract</option>
          </select>
          <textarea
            name="description"
            placeholder="Job description"
            className="sm:col-span-2 rounded-md border border-slate-300 px-3 py-2 text-sm"
            rows={3}
          />
          <input
            name="mustHave"
            placeholder="Must-have skills, comma separated (e.g. React, TypeScript, Git)"
            className="sm:col-span-2 rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <input
            name="niceToHave"
            placeholder="Nice-to-have skills, comma separated"
            className="sm:col-span-2 rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <button
            type="submit"
            className="sm:col-span-2 rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
          >
            Publish job
          </button>
        </form>
      </details>
    </div>
  );
}
