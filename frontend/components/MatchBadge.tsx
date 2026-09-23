function colorFor(score: number) {
  if (score >= 85) return "bg-emerald-100 text-emerald-700";
  if (score >= 65) return "bg-brand-100 text-brand-700";
  if (score >= 40) return "bg-amber-100 text-amber-700";
  return "bg-rose-100 text-rose-700";
}

export default function MatchBadge({ score }: { score: number }) {
  return (
    <span className={`badge ${colorFor(score)}`}>
      <span className="mr-1">⚡</span>
      {score}% AI match
    </span>
  );
}
