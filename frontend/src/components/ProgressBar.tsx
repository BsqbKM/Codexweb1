type Props = {
  value: number;
  max?: number;
};

export function ProgressBar({ value, max = 100 }: Props) {
  const percent = Math.min(100, Math.max(0, (value / max) * 100));
  return (
    <div className="h-3 w-full rounded-full bg-slate-800">
      <div
        className="h-3 rounded-full bg-gradient-to-r from-rose-400 to-amber-300 transition-all"
        style={{ width: `${percent}%` }}
      />
    </div>
  );
}
