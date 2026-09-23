import type { MatchBreakdown } from "./types";

const STOPWORDS = new Set([
  "the", "and", "for", "with", "a", "an", "of", "to", "in", "on", "or",
  "is", "are", "as", "at", "by", "be", "this", "that", "will", "you",
  "we", "our", "have", "has", "years", "year", "experience", "strong",
  "knowledge", "ability", "working", "skills",
]);

export function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9+#.\s]/g, " ")
    .split(/\s+/)
    .map((w) => w.replace(/\.+$/, ""))
    .filter((w) => w.length > 1 && !STOPWORDS.has(w));
}

/** Naive "AI resume parsing": pull a candidate skill list out of free text
 * by matching against a reference vocabulary plus generic capitalised/tech
 * looking tokens. Mirrors Datacruit's automated CV-parsing feature. */
export function extractSkills(resumeText: string, vocabulary: string[]): string[] {
  const tokens = new Set(tokenize(resumeText));
  const found = new Set<string>();

  for (const skill of vocabulary) {
    const skillTokens = tokenize(skill);
    const allPresent = skillTokens.every((t) => tokens.has(t));
    if (allPresent) found.add(skill);
  }

  return Array.from(found);
}

function skillPresent(skill: string, haystackTokens: Set<string>): boolean {
  const skillTokens = tokenize(skill);
  return skillTokens.every((t) => haystackTokens.has(t));
}

/** "AI Match Score": weighted keyword overlap between a candidate's resume
 * and a job's must-have / nice-to-have requirements, with an explainable
 * breakdown of matched and missing requirements. */
export function scoreCandidate(
  resumeText: string,
  skills: string[],
  mustHave: string[],
  niceToHave: string[]
): MatchBreakdown {
  const haystack = new Set([
    ...tokenize(resumeText),
    ...skills.flatMap((s) => tokenize(s)),
  ]);

  const matchedMustHave = mustHave.filter((s) => skillPresent(s, haystack));
  const missingMustHave = mustHave.filter((s) => !skillPresent(s, haystack));
  const matchedNiceToHave = niceToHave.filter((s) => skillPresent(s, haystack));

  const mustHaveWeight = 0.75;
  const niceToHaveWeight = 0.25;

  const mustHaveScore =
    mustHave.length === 0 ? 1 : matchedMustHave.length / mustHave.length;
  const niceToHaveScore =
    niceToHave.length === 0 ? 1 : matchedNiceToHave.length / niceToHave.length;

  const rawScore =
    mustHaveScore * mustHaveWeight + niceToHaveScore * niceToHaveWeight;
  const score = Math.round(rawScore * 100);

  let summary: string;
  if (score >= 85) {
    summary = "Excellent match — covers nearly all requirements.";
  } else if (score >= 65) {
    summary = "Strong match — meets most must-have requirements.";
  } else if (score >= 40) {
    summary = "Partial match — some key requirements are missing.";
  } else {
    summary = "Weak match — resume covers few of the job's requirements.";
  }

  return {
    score,
    matchedMustHave,
    missingMustHave,
    matchedNiceToHave,
    summary,
  };
}
