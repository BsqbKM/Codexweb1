import { useCallback, useState } from "react";
import type { DragEvent } from "react";

type Props = {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
};

const ACCEPTED_TYPES = ["image/jpeg", "image/png"];

export function ImageDropzone({ onFileSelected, disabled }: Props) {
  const [isDragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      if (!files || files.length === 0) {
        return;
      }
      const file = files[0];
      if (!ACCEPTED_TYPES.includes(file.type)) {
        setError("Please upload a JPEG or PNG image");
        return;
      }
      setError(null);
      onFileSelected(file);
    },
    [onFileSelected]
  );

  const onDrop = useCallback(
    (event: DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      if (disabled) return;
      setDragOver(false);
      handleFiles(event.dataTransfer.files);
    },
    [disabled, handleFiles]
  );

  return (
    <div className="flex flex-col gap-3">
      <div
        onDragOver={(event) => {
          event.preventDefault();
          if (!disabled) setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        className={`flex h-56 w-full cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed transition ${
          isDragOver ? "border-rose-400 bg-rose-400/10" : "border-slate-700"
        } ${disabled ? "cursor-not-allowed opacity-60" : ""}`}
        onClick={() => {
          if (disabled) return;
          const input = document.createElement("input");
          input.type = "file";
          input.accept = ACCEPTED_TYPES.join(",");
          input.onchange = () => handleFiles(input.files);
          input.click();
        }}
      >
        <span className="text-sm text-slate-300">
          Drag & drop a wine label or click to browse
        </span>
      </div>
      {error && <p className="text-sm text-rose-400">{error}</p>}
    </div>
  );
}
