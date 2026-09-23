export type Stage =
  | "applied"
  | "screening"
  | "interview"
  | "offer"
  | "hired"
  | "rejected";

export const STAGES: Stage[] = [
  "applied",
  "screening",
  "interview",
  "offer",
  "hired",
  "rejected",
];

export const STAGE_LABELS: Record<Stage, string> = {
  applied: "Applied",
  screening: "Screening",
  interview: "Interview",
  offer: "Offer",
  hired: "Hired",
  rejected: "Rejected",
};

export type Job = {
  id: string;
  title: string;
  department: string;
  location: string;
  employmentType: "Full-time" | "Part-time" | "Contract";
  status: "open" | "closed";
  description: string;
  mustHave: string[];
  niceToHave: string[];
  createdAt: string;
};

export type MatchBreakdown = {
  score: number;
  matchedMustHave: string[];
  missingMustHave: string[];
  matchedNiceToHave: string[];
  summary: string;
};

export type Candidate = {
  id: string;
  jobId: string;
  name: string;
  email: string;
  phone: string;
  source: "LinkedIn" | "Job Board" | "Referral" | "Career Site" | "Agency";
  resumeText: string;
  skills: string[];
  experienceYears: number;
  stage: Stage;
  match: MatchBreakdown;
  createdAt: string;
  stageHistory: { stage: Stage; at: string }[];
};

export type Interview = {
  id: string;
  candidateId: string;
  jobId: string;
  scheduledAt: string;
  interviewer: string;
  type: "Phone" | "Video" | "Onsite";
  status: "scheduled" | "completed" | "cancelled";
  notes: string;
};

export type Evaluation = {
  id: string;
  candidateId: string;
  evaluatorName: string;
  rating: 1 | 2 | 3 | 4 | 5;
  recommendation: "hire" | "no-hire" | "maybe";
  comments: string;
  createdAt: string;
};

export type Database = {
  jobs: Job[];
  candidates: Candidate[];
  interviews: Interview[];
  evaluations: Evaluation[];
};
