export type Candidate = {
  wine_id: number;
  name: string;
  producer?: string | null;
  vintage?: number | null;
  match_score: number;
};

export type Explanation = {
  ocr_tokens: { text: string; weight: number }[];
  image_neighbors: { wine_id: number; sim: number }[];
  features: { name: string; gain: number }[];
};

export type InferenceFinal = {
  wine_id: number | null;
  pred_quality: number;
  conf_interval: [number, number];
  explain: Explanation;
};

export type InferenceResponse = {
  candidates: Candidate[];
  final: InferenceFinal;
  debug: {
    model_versions: Record<string, string>;
    latency_ms: number;
  };
};

export type StoredHistory = {
  id: string;
  response: InferenceResponse;
  created_at: number;
};
