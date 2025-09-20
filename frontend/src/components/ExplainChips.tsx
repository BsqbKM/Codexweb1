import { Explanation } from "../types";

type Props = {
  explanation: Explanation | null;
};

export function ExplainChips({ explanation }: Props) {
  if (!explanation) return null;
  return (
    <div className="space-y-4">
      <section>
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">OCR tokens</h3>
        <div className="mt-2 flex flex-wrap gap-2">
          {explanation.ocr_tokens.map((token) => (
            <span key={token.text} className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-200">
              {token.text} · {Math.round(token.weight * 100)}%
            </span>
          ))}
        </div>
      </section>
      <section>
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Nearest neighbours</h3>
        <div className="mt-2 space-y-1 text-sm text-slate-300">
          {explanation.image_neighbors.map((item) => (
            <div key={item.wine_id} className="rounded-lg bg-slate-900/60 px-3 py-2">
              ID #{item.wine_id} · similarity {(item.sim * 100).toFixed(1)}%
            </div>
          ))}
        </div>
      </section>
      <section>
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Key features</h3>
        <div className="mt-2 flex flex-wrap gap-2">
          {explanation.features.map((feature) => (
            <span key={feature.name} className="rounded border border-rose-300/50 px-3 py-1 text-xs text-rose-100">
              {feature.name} · {feature.gain.toFixed(2)}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
}
