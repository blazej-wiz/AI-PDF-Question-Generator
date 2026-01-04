const API_BASE = "http://127.0.0.1:8000";

export async function generateQuestions({ file, questionType, count }) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("question_type", questionType);
  formData.append("count", String(count));

  const res = await fetch(`${API_BASE}/generate-questions`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Request failed");
  }

  return res.json();
}

// ✅ NEW: create a saved deck/document
export async function createDocument({ title }) {
  const res = await fetch(`${API_BASE}/documents`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Create document failed");
  }

  return res.json();
}

// ✅ NEW: save cards to a document
export async function addCardsToDocument({ documentId, cards }) {
  const res = await fetch(`${API_BASE}/documents/${documentId}/cards`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cards }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Save cards failed");
  }

  return res.json();
}

// ✅ NEW: list documents (library)
export async function listDocuments() {
  const res = await fetch(`${API_BASE}/documents`, { method: "GET" });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "List documents failed");
  }

  return res.json();
}

// ✅ NEW: load cards for a document
export async function getCardsForDocument({ documentId }) {
  const res = await fetch(`${API_BASE}/documents/${documentId}/cards`, {
    method: "GET",
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Get cards failed");
  }

  return res.json();
}

// ✅ NEW: record progress
export async function postProgress({ cardId, correct }) {
  const res = await fetch(`${API_BASE}/progress`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ card_id: cardId, correct }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Post progress failed");
  }

  return res.json();
}
