"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { getDb, nextId, updateDb } from "./store";
import { scoreCandidate } from "./matching";
import type { Stage } from "./types";

export async function applyToJob(formData: FormData) {
  const jobId = String(formData.get("jobId") ?? "");
  const name = String(formData.get("name") ?? "").trim();
  const email = String(formData.get("email") ?? "").trim();
  const phone = String(formData.get("phone") ?? "").trim();
  const source = String(formData.get("source") ?? "Career Site") as any;
  const experienceYears = Number(formData.get("experienceYears") ?? 0);
  const resumeText = String(formData.get("resumeText") ?? "").trim();

  if (!jobId || !name || !email || !resumeText) {
    throw new Error("Missing required application fields.");
  }

  const db = getDb();
  const job = db.jobs.find((j) => j.id === jobId);
  if (!job) throw new Error("Job not found.");

  const match = scoreCandidate(resumeText, [], job.mustHave, job.niceToHave);
  const skills = [...match.matchedMustHave, ...match.matchedNiceToHave];
  const id = nextId("cand");
  const createdAt = new Date().toISOString();

  updateDb((d) => {
    d.candidates.push({
      id,
      jobId,
      name,
      email,
      phone,
      source,
      resumeText,
      skills,
      experienceYears,
      stage: "applied",
      match,
      createdAt,
      stageHistory: [{ stage: "applied", at: createdAt }],
    });
  });

  revalidatePath("/jobs");
  revalidatePath(`/jobs/${jobId}`);
  revalidatePath("/");
  redirect(`/candidates/${id}?applied=1`);
}

export async function moveCandidateStage(
  candidateId: string,
  stage: Stage,
  jobId: string
) {
  updateDb((d) => {
    const cand = d.candidates.find((c) => c.id === candidateId);
    if (!cand) return;
    cand.stage = stage;
    cand.stageHistory.push({ stage, at: new Date().toISOString() });
  });
  revalidatePath(`/jobs/${jobId}`);
  revalidatePath(`/candidates/${candidateId}`);
  revalidatePath("/");
}

export async function scheduleInterview(formData: FormData) {
  const candidateId = String(formData.get("candidateId") ?? "");
  const jobId = String(formData.get("jobId") ?? "");
  const scheduledAt = String(formData.get("scheduledAt") ?? "");
  const interviewer = String(formData.get("interviewer") ?? "").trim();
  const type = String(formData.get("type") ?? "Video") as any;
  const notes = String(formData.get("notes") ?? "").trim();

  if (!candidateId || !jobId || !scheduledAt || !interviewer) {
    throw new Error("Missing required interview fields.");
  }

  const id = nextId("int");
  updateDb((d) => {
    d.interviews.push({
      id,
      candidateId,
      jobId,
      scheduledAt: new Date(scheduledAt).toISOString(),
      interviewer,
      type,
      status: "scheduled",
      notes,
    });
    const cand = d.candidates.find((c) => c.id === candidateId);
    if (cand && cand.stage === "applied") {
      cand.stage = "screening";
      cand.stageHistory.push({ stage: "screening", at: new Date().toISOString() });
    }
  });

  revalidatePath(`/candidates/${candidateId}`);
  revalidatePath(`/jobs/${jobId}`);
  revalidatePath("/");
}

export async function submitEvaluation(formData: FormData) {
  const candidateId = String(formData.get("candidateId") ?? "");
  const evaluatorName = String(formData.get("evaluatorName") ?? "").trim();
  const rating = Number(formData.get("rating") ?? 3);
  const recommendation = String(formData.get("recommendation") ?? "maybe") as any;
  const comments = String(formData.get("comments") ?? "").trim();

  if (!candidateId || !evaluatorName) {
    throw new Error("Missing required evaluation fields.");
  }

  const id = nextId("eval");
  updateDb((d) => {
    d.evaluations.push({
      id,
      candidateId,
      evaluatorName,
      rating: rating as any,
      recommendation,
      comments,
      createdAt: new Date().toISOString(),
    });
  });

  revalidatePath(`/candidates/${candidateId}`);
}

export async function createJob(formData: FormData) {
  const title = String(formData.get("title") ?? "").trim();
  const department = String(formData.get("department") ?? "").trim();
  const location = String(formData.get("location") ?? "").trim();
  const employmentType = String(formData.get("employmentType") ?? "Full-time") as any;
  const description = String(formData.get("description") ?? "").trim();
  const mustHave = String(formData.get("mustHave") ?? "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  const niceToHave = String(formData.get("niceToHave") ?? "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  if (!title || !department || !location) {
    throw new Error("Missing required job fields.");
  }

  const id = nextId("job");
  updateDb((d) => {
    d.jobs.push({
      id,
      title,
      department,
      location,
      employmentType,
      status: "open",
      description,
      mustHave,
      niceToHave,
      createdAt: new Date().toISOString(),
    });
  });

  revalidatePath("/jobs");
  redirect(`/jobs/${id}`);
}
