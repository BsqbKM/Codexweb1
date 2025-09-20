import { useCallback, useEffect, useState } from "react";

import { InferenceResponse, StoredHistory } from "../types";

const DB_NAME = "winelens";
const STORE_NAME = "history";
const DB_VERSION = 1;

async function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: "id" });
      }
    };
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
}

async function getAllHistory(): Promise<StoredHistory[]> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(STORE_NAME, "readonly");
    const store = transaction.objectStore(STORE_NAME);
    const request = store.getAll();
    request.onerror = () => reject(request.error);
    request.onsuccess = () => {
      resolve((request.result as StoredHistory[]).sort((a, b) => b.created_at - a.created_at));
    };
  });
}

async function addHistoryEntry(entry: StoredHistory): Promise<void> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(STORE_NAME, "readwrite");
    const store = transaction.objectStore(STORE_NAME);
    const request = store.put(entry);
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve();
  });
}

export function useHistory() {
  const [history, setHistory] = useState<StoredHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAllHistory()
      .then((entries) => setHistory(entries))
      .finally(() => setLoading(false));
  }, []);

  const addEntry = useCallback(async (response: InferenceResponse) => {
    const entry: StoredHistory = {
      id: crypto.randomUUID(),
      response,
      created_at: Date.now()
    };
    await addHistoryEntry(entry);
    setHistory((prev) => [entry, ...prev]);
    return entry;
  }, []);

  return { history, loading, addEntry };
}
