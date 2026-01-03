const API_BASE = "http://127.0.0.1:8000";

export async function generateQuestions({ file, questionType, count = 5 }) {
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
