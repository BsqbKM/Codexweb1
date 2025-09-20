import { useLocation, useNavigate } from "react-router-dom";

import { CandidateList } from "../components/CandidateList";
import { ExplainChips } from "../components/ExplainChips";
import { ProgressBar } from "../components/ProgressBar";
import { InferenceResponse } from "../types";

function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as { response: InferenceResponse; preview?: string } | undefined;

  if (!state) {
    return (
      <div className="space-y-4 text-sm text-slate-300">
        <p>No inference data found. Please upload a wine label first.</p>
        <button className="text-rose-300" onClick={() => navigate("/")}>
          Go to upload
        </button>
      </div>
    );
  }

  const { response, preview } = state;
  const quality = Math.round(response.final.pred_quality);

  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-[2fr,1fr]">
        <section className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold text-rose-200">Quality estimate</h2>
            <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
              latency {response.debug.latency_ms} ms
            </span>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-5xl font-bold text-rose-300">{quality}</div>
            <div className="flex-1">
              <ProgressBar value={response.final.pred_quality} />
              <p className="mt-2 text-xs text-slate-400">
                Confidence interval {response.final.conf_interval[0].toFixed(1)} – {" "}
                {response.final.conf_interval[1].toFixed(1)}
              </p>
            </div>
          </div>
        </section>
        <section className="space-y-3 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Preview</h3>
          {preview ? (
            <img src={preview} alt="Preview" className="w-full rounded-lg border border-slate-800" />
          ) : (
            <p className="text-sm text-slate-400">No preview available.</p>
          )}
        </section>
      </div>

      <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-lg font-semibold text-slate-200">Top candidates</h2>
        <CandidateList candidates={response.candidates} />
      </section>

      <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-lg font-semibold text-slate-200">Why this result?</h2>
        <ExplainChips explanation={response.final.explain} />
      </section>
    </div>
  );
}

export default ResultPage;
