import { createBrowserRouter } from "react-router-dom";

import App from "./App";
import HistoryPage from "./pages/HistoryPage";
import ResultPage from "./pages/ResultPage";
import UploadPage from "./pages/UploadPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        index: true,
        element: <UploadPage />
      },
      {
        path: "result",
        element: <ResultPage />
      },
      {
        path: "history",
        element: <HistoryPage />
      }
    ]
  }
]);
