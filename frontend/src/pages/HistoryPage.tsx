import { useNavigate } from "react-router-dom";

import { useHistory } from "../hooks/useHistory";

function HistoryPage() {
  const { history, loading } = useHistory();
  const navigate = useNavigate();

  if (loading) {
    return <p className="text-sm text-slate-400">Loading history…</p>;
  }

  if (!history.length) {
    return <p className="text-sm text-slate-400">No past inferences yet.</p>;
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-rose-200">History</h1>
      <div className="space-y-3">
        {history.map((entry) => (
          <button
            key={entry.id}
            className="w-full rounded-xl border border-slate-800 bg-slate-900/60 p-4 text-left transition hover:border-rose-300"
            onClick={() => navigate("/result", { state: { response: entry.response } })}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-300">Quality {entry.response.final.pred_quality.toFixed(1)}</p>
                <p className="text-xs text-slate-500">
                  Stored at {new Date(entry.created_at).toLocaleString()}
                </p>
              </div>
              <span className="text-xs uppercase tracking-wide text-slate-400">
                {entry.response.candidates[0]?.name ?? "Unknown"}
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default HistoryPage;
