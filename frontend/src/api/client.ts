import axios from "axios";

import { InferenceResponse } from "../types";

export async function inferWine(file: File, storeImage: boolean) {
  const formData = new FormData();
  formData.append("image", file);
  const response = await axios.post<InferenceResponse>(
    `/api/v1/infer?store_image=${storeImage}`,
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" }
    }
  );
  return response.data;
}
