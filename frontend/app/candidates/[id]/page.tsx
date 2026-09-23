import Link from "next/link";
import { notFound } from "next/navigation";
import { getDb } from "@/lib/store";
import { scheduleInterview, submitEvaluation } from "@/lib/actions";
import MatchBadge from "@/components/MatchBadge";
import StageBadge from "@/components/StageBadge";
import StageSelect from "@/components/StageSelect";

export const dynamic = "force-dynamic";

function formatDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

const STARS = [1, 2, 3, 4, 5] as const;

export default function CandidateProfilePage({
  params,
  searchParams,
}: {
  params: { id: string };
  searchParams: { applied?: string };
}) {
  const db = getDb();
  const candidate = db.candidates.find((c) => c.id === params.id);
  if (!candidate) notFound();

  const job = db.jobs.find((j) => j.id === candidate.jobId);
  const interviews = db.interviews
    .filter((i) => i.candidateId === candidate.id)
    .sort((a, b) => new Date(a.scheduledAt).getTime() - new Date(b.scheduledAt).getTime());
  const evaluations = db.evaluations
    .filter((e) => e.candidateId === candidate.id)
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

  const { match } = candidate;

  return (
    <div className="space-y-6">
      <Link
        href={job ? `/jobs/${job.id}` : "/jobs"}
        className="text-sm text-slate-400 hover:text-slate-600"
      >
        ← Back to {job?.title ?? "pipeline"}
      </Link>

      {searchParams.applied === "1" && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          ✓ Application received. AI parsing extracted {candidate.skills.length} skills
          and scored this candidate a {match.score}% match automatically.
        </div>
      )}

      <div className="card p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">{candidate.name}</h1>
            <p className="text-sm text-slate-500">
              Applying for{" "}
              <Link href={`/jobs/${candidate.jobId}`} className="text-brand-600 hover:underline">
                {job?.title}
              </Link>
            </p>
            <p className="mt-1 text-xs text-slate-400">
              {candidate.email} · {candidate.phone} · {candidate.source} ·{" "}
              {candidate.experienceYears} yrs experience
            </p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <MatchBadge score={match.score} />
            <StageBadge stage={candidate.stage} />
          </div>
        </div>

        <div className="mt-4 max-w-xs">
          <StageSelect candidateId={candidate.id} jobId={candidate.jobId} stage={candidate.stage} />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card p-6">
          <h2 className="text-sm font-semibold text-slate-700">AI match breakdown</h2>
          <p className="mt-1 text-sm text-slate-500">{match.summary}</p>

          <div className="mt-4 space-y-3 text-sm">
            <div>
              <p className="mb-1 font-medium text-slate-600">
                Must-have — matched ({match.matchedMustHave.length}/
                {match.matchedMustHave.length + match.missingMustHave.length})
              </p>
              <div className="flex flex-wrap gap-1.5">
                {match.matchedMustHave.map((s) => (
                  <span key={s} className="badge bg-emerald-100 text-emerald-700">
                    ✓ {s}
                  </span>
                ))}
                {match.missingMustHave.map((s) => (
                  <span key={s} className="badge bg-rose-100 text-rose-700">
                    ✗ {s}
                  </span>
                ))}
              </div>
            </div>
            {match.matchedNiceToHave.length > 0 && (
              <div>
                <p className="mb-1 font-medium text-slate-600">Nice-to-have — matched</p>
                <div className="flex flex-wrap gap-1.5">
                  {match.matchedNiceToHave.map((s) => (
                    <span key={s} className="badge bg-brand-100 text-brand-700">
                      ✓ {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-sm font-semibold text-slate-700">Resume</h2>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-slate-600">
            {candidate.resumeText}
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card p-6">
          <h2 className="text-sm font-semibold text-slate-700">Interviews</h2>
          <ul className="mt-3 space-y-2">
            {interviews.length === 0 && (
              <p className="text-sm text-slate-400">No interviews scheduled yet.</p>
            )}
            {interviews.map((i) => (
              <li key={i.id} className="rounded-md bg-slate-50 p-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-slate-800">{i.type} interview</span>
                  <span className="badge bg-slate-200 text-slate-600">{i.status}</span>
                </div>
                <p className="text-xs text-slate-500">
                  {formatDate(i.scheduledAt)} · with {i.interviewer}
                </p>
                {i.notes && <p className="mt-1 text-xs text-slate-500">{i.notes}</p>}
              </li>
            ))}
          </ul>

          <form action={scheduleInterview} className="mt-4 space-y-2 border-t border-slate-100 pt-4">
            <input type="hidden" name="candidateId" value={candidate.id} />
            <input type="hidden" name="jobId" value={candidate.jobId} />
            <p className="text-xs font-medium text-slate-500">Schedule a new interview</p>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="datetime-local"
                name="scheduledAt"
                required
                className="rounded-md border border-slate-300 px-2 py-1.5 text-sm"
              />
              <select
                name="type"
                className="rounded-md border border-slate-300 px-2 py-1.5 text-sm"
                defaultValue="Video"
              >
                <option>Video</option>
                <option>Phone</option>
                <option>Onsite</option>
              </select>
            </div>
            <input
              name="interviewer"
              placeholder="Interviewer name"
              required
              className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
            />
            <textarea
              name="notes"
              placeholder="Notes (optional)"
              rows={2}
              className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
            />
            <button
              type="submit"
              className="w-full rounded-md bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700"
            >
              Schedule interview
            </button>
          </form>
        </div>

        <div className="card p-6">
          <h2 className="text-sm font-semibold text-slate-700">
            Manager feedback & evaluations
          </h2>
          <ul className="mt-3 space-y-2">
            {evaluations.length === 0 && (
              <p className="text-sm text-slate-400">No evaluations submitted yet.</p>
            )}
            {evaluations.map((e) => (
              <li key={e.id} className="rounded-md bg-slate-50 p-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-slate-800">{e.evaluatorName}</span>
                  <span
                    className={`badge ${
                      e.recommendation === "hire"
                        ? "bg-emerald-100 text-emerald-700"
                        : e.recommendation === "no-hire"
                        ? "bg-rose-100 text-rose-700"
                        : "bg-amber-100 text-amber-700"
                    }`}
                  >
                    {e.recommendation}
                  </span>
                </div>
                <p className="text-xs text-slate-500">
                  {"★".repeat(e.rating)}
                  {"☆".repeat(5 - e.rating)} · {formatDate(e.createdAt)}
                </p>
                {e.comments && <p className="mt-1 text-xs text-slate-500">{e.comments}</p>}
              </li>
            ))}
          </ul>

          <form action={submitEvaluation} className="mt-4 space-y-2 border-t border-slate-100 pt-4">
            <input type="hidden" name="candidateId" value={candidate.id} />
            <p className="text-xs font-medium text-slate-500">Submit evaluation</p>
            <input
              name="evaluatorName"
              placeholder="Your name"
              required
              className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
            />
            <div className="grid grid-cols-2 gap-2">
              <select
                name="rating"
                className="rounded-md border border-slate-300 px-2 py-1.5 text-sm"
                defaultValue={4}
              >
                {STARS.map((n) => (
                  <option key={n} value={n}>
                    {n} star{n > 1 ? "s" : ""}
                  </option>
                ))}
              </select>
              <select
                name="recommendation"
                className="rounded-md border border-slate-300 px-2 py-1.5 text-sm"
                defaultValue="maybe"
              >
                <option value="hire">Hire</option>
                <option value="maybe">Maybe</option>
                <option value="no-hire">No hire</option>
              </select>
            </div>
            <textarea
              name="comments"
              placeholder="Feedback comments"
              rows={2}
              className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
            />
            <button
              type="submit"
              className="w-full rounded-md bg-slate-800 px-3 py-2 text-sm font-medium text-white hover:bg-slate-900"
            >
              Submit evaluation
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
