import fs from "fs";
import path from "path";
import type {
  Candidate,
  Database,
  Evaluation,
  Interview,
  Job,
  Stage,
} from "./types";
import { scoreCandidate } from "./matching";

const DB_PATH = path.join(process.cwd(), "data", "db.json");

let cache: Database | null = null;

function nowIso(daysAgo = 0) {
  const d = new Date();
  d.setDate(d.getDate() - daysAgo);
  return d.toISOString();
}

function id(prefix: string, n: number) {
  return `${prefix}_${n}`;
}

const PIPELINE_ORDER: Stage[] = [
  "applied",
  "screening",
  "interview",
  "offer",
  "hired",
];

/** Builds a plausible stage-by-stage history from application day to the
 * candidate's current stage, so time-in-pipeline metrics have real data. */
function buildStageHistory(finalStage: Stage, appliedDaysAgo: number) {
  const steps: Stage[] =
    finalStage === "rejected"
      ? ["applied", "screening", "rejected"]
      : PIPELINE_ORDER.slice(0, PIPELINE_ORDER.indexOf(finalStage) + 1);

  return steps.map((stage, i) => {
    const daysAgo =
      steps.length === 1
        ? appliedDaysAgo
        : Math.round(appliedDaysAgo * (1 - i / (steps.length - 1)));
    return { stage, at: nowIso(daysAgo) };
  });
}

function buildSeed(): Database {
  const jobs: Job[] = [
    {
      id: "job_1",
      title: "Senior Frontend Engineer",
      department: "Engineering",
      location: "Amsterdam, NL (Hybrid)",
      employmentType: "Full-time",
      status: "open",
      description:
        "Own the candidate-facing web app experience: build fast, accessible interfaces and collaborate closely with design and product.",
      mustHave: ["React", "TypeScript", "CSS", "REST APIs", "Git"],
      niceToHave: ["Next.js", "GraphQL", "Testing", "Tailwind CSS"],
      createdAt: nowIso(21),
    },
    {
      id: "job_2",
      title: "Backend Engineer (Node.js)",
      department: "Engineering",
      location: "Remote (EU)",
      employmentType: "Full-time",
      status: "open",
      description:
        "Design and scale the services powering our matching engine, integrations and automation pipelines.",
      mustHave: ["Node.js", "TypeScript", "PostgreSQL", "REST APIs", "Git"],
      niceToHave: ["Docker", "AWS", "Kubernetes", "Redis"],
      createdAt: nowIso(18),
    },
    {
      id: "job_3",
      title: "Recruitment Consultant",
      department: "Talent Acquisition",
      location: "Prague, CZ (Hybrid)",
      employmentType: "Full-time",
      status: "open",
      description:
        "Partner with clients to source, screen and place candidates across tech and commercial roles using our ATS.",
      mustHave: ["Recruiting", "Communication", "Sourcing", "CRM"],
      niceToHave: ["LinkedIn Recruiter", "Negotiation", "ATS"],
      createdAt: nowIso(30),
    },
    {
      id: "job_4",
      title: "Data Analyst",
      department: "Operations",
      location: "Remote",
      employmentType: "Contract",
      status: "open",
      description:
        "Turn hiring funnel and product usage data into recommendations for the leadership team.",
      mustHave: ["SQL", "Python", "Excel", "Data Visualization"],
      niceToHave: ["Power BI", "Tableau", "Statistics"],
      createdAt: nowIso(10),
    },
  ];

  const rawCandidates: Array<{
    job: Job;
    name: string;
    email: string;
    phone: string;
    source: Candidate["source"];
    resumeText: string;
    experienceYears: number;
    stage: Stage;
    daysAgo: number;
  }> = [
    {
      job: jobs[0],
      name: "Elena Novak",
      email: "elena.novak@example.com",
      phone: "+420 601 234 111",
      source: "LinkedIn",
      resumeText:
        "Senior frontend engineer with 6 years building React and TypeScript applications. Deep experience with REST APIs, Git workflows, CSS and design systems. Recently shipped a Next.js migration and set up automated Testing with Tailwind CSS.",
      experienceYears: 6,
      stage: "interview",
      daysAgo: 9,
    },
    {
      job: jobs[0],
      name: "Marcus Feldt",
      email: "marcus.feldt@example.com",
      phone: "+49 151 555 2233",
      source: "Career Site",
      resumeText:
        "Frontend developer with 3 years of experience in React and CSS. Comfortable with Git and REST APIs. Currently learning TypeScript and exploring GraphQL on side projects.",
      experienceYears: 3,
      stage: "screening",
      daysAgo: 5,
    },
    {
      job: jobs[0],
      name: "Priya Shah",
      email: "priya.shah@example.com",
      phone: "+31 6 1234 5678",
      source: "Referral",
      resumeText:
        "Full-stack engineer focused mostly on backend Python services, with some CSS and basic Git usage day to day.",
      experienceYears: 4,
      stage: "applied",
      daysAgo: 2,
    },
    {
      job: jobs[1],
      name: "Tomas Dvorak",
      email: "tomas.dvorak@example.com",
      phone: "+420 602 987 111",
      source: "LinkedIn",
      resumeText:
        "Backend engineer with 7 years in Node.js and TypeScript, running production PostgreSQL databases and REST APIs. Strong Git practices, containerised services with Docker and deployed on AWS and Kubernetes.",
      experienceYears: 7,
      stage: "offer",
      daysAgo: 15,
    },
    {
      job: jobs[1],
      name: "Sara Lindqvist",
      email: "sara.lindqvist@example.com",
      phone: "+46 70 555 1122",
      source: "Job Board",
      resumeText:
        "Node.js developer with 2 years of experience, working with REST APIs and Git. Familiar with PostgreSQL basics and eager to grow into a stronger backend role.",
      experienceYears: 2,
      stage: "applied",
      daysAgo: 3,
    },
    {
      job: jobs[1],
      name: "Igor Petrov",
      email: "igor.petrov@example.com",
      phone: "+420 603 444 555",
      source: "Agency",
      resumeText:
        "Java backend developer with 5 years of experience building services on Oracle databases and internal enterprise tooling.",
      experienceYears: 5,
      stage: "rejected",
      daysAgo: 12,
    },
    {
      job: jobs[2],
      name: "Nikola Horakova",
      email: "nikola.horakova@example.com",
      phone: "+420 604 222 333",
      source: "Referral",
      resumeText:
        "Recruitment consultant with 5 years of full-cycle recruiting, sourcing and candidate communication. Power user of LinkedIn Recruiter and ATS platforms, strong negotiation and CRM skills.",
      experienceYears: 5,
      stage: "hired",
      daysAgo: 25,
    },
    {
      job: jobs[2],
      name: "David Kral",
      email: "david.kral@example.com",
      phone: "+420 605 666 777",
      source: "Career Site",
      resumeText:
        "Junior talent sourcer with 1 year of experience helping identify and reach out to candidates for open roles. Comfortable with day-to-day communication, still building hands-on experience with dedicated recruiting tools.",
      experienceYears: 1,
      stage: "screening",
      daysAgo: 6,
    },
    {
      job: jobs[2],
      name: "Anna Svobodova",
      email: "anna.svobodova@example.com",
      phone: "+420 606 888 999",
      source: "LinkedIn",
      resumeText:
        "HR generalist with strong communication skills and some early experience helping source candidates for internal openings.",
      experienceYears: 3,
      stage: "applied",
      daysAgo: 1,
    },
    {
      job: jobs[3],
      name: "Lukas Bauer",
      email: "lukas.bauer@example.com",
      phone: "+43 660 111 222",
      source: "Job Board",
      resumeText:
        "Data analyst with 4 years of experience writing SQL and Python for reporting, building Excel models and Data Visualization dashboards in Power BI and Tableau, plus applied statistics coursework.",
      experienceYears: 4,
      stage: "interview",
      daysAgo: 8,
    },
    {
      job: jobs[3],
      name: "Katerina Novotna",
      email: "katerina.novotna@example.com",
      phone: "+420 607 333 444",
      source: "Career Site",
      resumeText:
        "Business analyst comfortable with Excel and writing basic SQL queries for ad hoc reporting requests.",
      experienceYears: 2,
      stage: "applied",
      daysAgo: 4,
    },
    {
      job: jobs[3],
      name: "Jonas Weber",
      email: "jonas.weber@example.com",
      phone: "+49 152 777 888",
      source: "Referral",
      resumeText:
        "Analytics engineer with 6 years across SQL, Python, Excel automation and Data Visualization using Power BI and Tableau. Also trained in statistics for A/B testing.",
      experienceYears: 6,
      stage: "offer",
      daysAgo: 11,
    },
  ];

  const candidates: Candidate[] = rawCandidates.map((c, i) => {
    const match = scoreCandidate(
      c.resumeText,
      [],
      c.job.mustHave,
      c.job.niceToHave
    );
    const skills = [...match.matchedMustHave, ...match.matchedNiceToHave];
    const stageHistory = buildStageHistory(c.stage, c.daysAgo);
    const createdAt = stageHistory[0].at;
    return {
      id: id("cand", i + 1),
      jobId: c.job.id,
      name: c.name,
      email: c.email,
      phone: c.phone,
      source: c.source,
      resumeText: c.resumeText,
      skills,
      experienceYears: c.experienceYears,
      stage: c.stage,
      match,
      createdAt,
      stageHistory,
    };
  });

  const interviews: Interview[] = [
    {
      id: "int_1",
      candidateId: "cand_1",
      jobId: "job_1",
      scheduledAt: nowIso(-2),
      interviewer: "Hana Kucerova (Eng Manager)",
      type: "Video",
      status: "scheduled",
      notes: "Focus on component architecture and design system experience.",
    },
    {
      id: "int_2",
      candidateId: "cand_10",
      jobId: "job_4",
      scheduledAt: nowIso(-1),
      interviewer: "Ben Ostrava (Head of Ops)",
      type: "Video",
      status: "scheduled",
      notes: "Walk through a past dashboard project end to end.",
    },
    {
      id: "int_3",
      candidateId: "cand_4",
      jobId: "job_2",
      scheduledAt: nowIso(4),
      interviewer: "Petr Malek (Staff Engineer)",
      type: "Onsite",
      status: "completed",
      notes: "Strong system design round, moving to offer stage.",
    },
  ];

  const evaluations: Evaluation[] = [
    {
      id: "eval_1",
      candidateId: "cand_4",
      evaluatorName: "Petr Malek",
      rating: 5,
      recommendation: "hire",
      comments:
        "Excellent grasp of distributed systems trade-offs, very clean take-home submission.",
      createdAt: nowIso(4),
    },
    {
      id: "eval_2",
      candidateId: "cand_7",
      evaluatorName: "Klara Dolezalova",
      rating: 5,
      recommendation: "hire",
      comments: "Great client references, hit every sourcing benchmark in the case study.",
      createdAt: nowIso(20),
    },
    {
      id: "eval_3",
      candidateId: "cand_6",
      evaluatorName: "Petr Malek",
      rating: 2,
      recommendation: "no-hire",
      comments: "Database experience doesn't transfer well to our PostgreSQL-heavy stack.",
      createdAt: nowIso(10),
    },
  ];

  return { jobs, candidates, interviews, evaluations };
}

function readDb(): Database {
  if (cache) return cache;
  if (fs.existsSync(DB_PATH)) {
    const raw = fs.readFileSync(DB_PATH, "utf-8");
    cache = JSON.parse(raw) as Database;
    return cache;
  }
  const seeded = buildSeed();
  writeDb(seeded);
  return seeded;
}

function writeDb(db: Database) {
  cache = db;
  fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });
  fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2), "utf-8");
}

export function getDb(): Database {
  return readDb();
}

export function updateDb(mutator: (db: Database) => void) {
  const db = readDb();
  mutator(db);
  writeDb(db);
}

export function resetDb() {
  writeDb(buildSeed());
}

export function nextId(prefix: string) {
  const db = readDb();
  const all = [
    ...db.jobs.map((j) => j.id),
    ...db.candidates.map((c) => c.id),
    ...db.interviews.map((i) => i.id),
    ...db.evaluations.map((e) => e.id),
  ];
  let n = 1;
  while (all.includes(`${prefix}_${n}`)) n++;
  return `${prefix}_${n}`;
}
