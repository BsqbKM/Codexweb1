import { Candidate } from "../types";

type Props = {
  candidates: Candidate[];
  onSelect?: (candidate: Candidate) => void;
};

export function CandidateList({ candidates, onSelect }: Props) {
  if (!candidates.length) {
    return <p className="text-sm text-slate-400">No close matches found yet.</p>;
  }
  return (
    <div className="space-y-3">
      {candidates.map((candidate) => (
        <button
          key={candidate.wine_id}
          className="w-full rounded-lg border border-slate-800 bg-slate-900/70 p-4 text-left transition hover:border-rose-300"
          onClick={() => onSelect?.(candidate)}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-lg font-semibold text-rose-200">{candidate.name}</p>
              {candidate.producer && (
                <p className="text-sm text-slate-400">{candidate.producer}</p>
              )}
            </div>
            <div className="text-right text-sm text-slate-400">
              <div>Vintage: {candidate.vintage ?? "—"}</div>
              <div>Score: {(candidate.match_score * 100).toFixed(1)}%</div>
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}
