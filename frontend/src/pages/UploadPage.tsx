import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { inferWine } from "../api/client";
import { ErrorToast } from "../components/ErrorToast";
import { ImageDropzone } from "../components/ImageDropzone";
import { useHistory } from "../hooks/useHistory";

function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [storeImage, setStoreImage] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { addEntry } = useHistory();

  const onFileSelected = (selected: File) => {
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
  };

  const onSubmit = async () => {
    if (!file) {
      setError("Please select an image first");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const response = await inferWine(file, storeImage);
      const entry = await addEntry(response);
      navigate("/result", { state: { response, historyId: entry.id, preview } });
    } catch (err) {
      console.error(err);
      setError("Failed to run inference. Ensure the backend is available.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <section className="grid gap-6 md:grid-cols-2">
        <div className="space-y-4">
          <h1 className="text-3xl font-semibold text-rose-200">Recognize your wine</h1>
          <p className="text-sm text-slate-300">
            Upload a photo of a wine label to identify the bottle, review quality insights, and compare top matches.
          </p>
          <label className="flex items-center gap-3 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={storeImage}
              onChange={(event) => setStoreImage(event.target.checked)}
            />
            Save this photo to improve WineLens (opt-in)
          </label>
          <button
            onClick={onSubmit}
            disabled={loading}
            className="rounded-full bg-rose-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-rose-400 disabled:opacity-60"
          >
            {loading ? "Analyzing..." : "Analyze label"}
          </button>
        </div>
        <div className="space-y-4">
          <ImageDropzone onFileSelected={onFileSelected} disabled={loading} />
          {preview && (
            <img src={preview} alt="Preview" className="w-full rounded-lg border border-slate-800" />
          )}
        </div>
      </section>
      <ErrorToast message={error} onClose={() => setError(null)} />
    </div>
  );
}

export default UploadPage;
