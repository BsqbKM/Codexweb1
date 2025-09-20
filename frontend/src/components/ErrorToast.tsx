type Props = {
  message: string | null;
  onClose?: () => void;
};

export function ErrorToast({ message, onClose }: Props) {
  if (!message) return null;
  return (
    <div className="fixed bottom-6 right-6 flex max-w-sm items-center gap-3 rounded-lg border border-rose-500 bg-slate-900 px-4 py-3 text-sm text-rose-100 shadow-lg">
      <span>{message}</span>
      <button className="text-xs uppercase text-rose-300" onClick={onClose}>
        Close
      </button>
    </div>
  );
}
