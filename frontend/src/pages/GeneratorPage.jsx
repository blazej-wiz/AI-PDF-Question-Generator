import { useMemo, useRef, useState } from "react";
import styles from "./GeneratorPage.module.css";
import { generateQuestions } from "../api";
import { useNavigate } from "react-router-dom";

export default function GeneratorPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [questionType, setQuestionType] = useState("mcq");
  const [count, setCount] = useState(5)
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const fileLabel = useMemo(() => {
    if (!file) return "No file selected";
    return file.name.length > 32 ? file.name.slice(0, 32) + "…" : file.name;
  }, [file]);

  async function onGenerate() {
  setError("");

  if (!file) {
    setError("Please upload a PDF first.");
    return;
  }

  try {
    setLoading(true);

    const data = await generateQuestions({
  file,
  questionType,
  count
});


    const cards = (data.questions || []).map((q) => ({
      type: q.type,
      question: q.question,
      options: q.options || [],
      correct_answer: q.correct_answer,
      explanation: q.explanation || "",
      answer: q.answer || ""
    }));

    navigate("/study", {
      state: {
        cards,
        questionType
      }
    });
  } catch (e) {
    setError(e.message || "Something went wrong.");
  } finally {
    setLoading(false);
  }
}


  return (
  <div className={styles.shell}>
    <div className={styles.card}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Question Generator</h1>
          <p className={styles.subtitle}>
            Upload a PDF and instantly generate study questions.
          </p>
        </div>
      </div>

      <div className={styles.form}>
        {/* File picker */}
        <div className={styles.field}>
          <label className={styles.label}>PDF</label>
          <div className={styles.fileRow}>
            <input
              ref={fileInputRef}
              type="file"
              accept="application/pdf"
              className={styles.fileInput}
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
            <button
              type="button"
              className={styles.secondaryButton}
              onClick={() => fileInputRef.current?.click()}
            >
              Upload PDF
            </button>
            <div className={styles.fileName} title={file?.name || ""}>
              {fileLabel}
            </div>
          </div>
        </div>

        {/* Question type */}
        <div className={styles.field}>
          <label className={styles.label}>Type</label>
          <select
            className={styles.select}
            value={questionType}
            onChange={(e) => setQuestionType(e.target.value)}
          >
            <option value="mcq">MCQ</option>
            <option value="saq">SAQ</option>
          </select>
        </div>

        {/* Number of questions */}
        <div className={styles.field}>
          <label className={styles.label}>Count</label>
          <select
            className={styles.select}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={15}>15</option>
            <option value={20}>20</option>
          </select>
        </div>

        {/* Actions */}
        <button
          type="button"
          className={styles.primaryButton}
          onClick={onGenerate}
          disabled={loading}
        >
          {loading ? "Generating…" : "Generate Questions"}
        </button>

        {error && <div className={styles.error}>{error}</div>}
      </div>
    </div>
  </div>
);

}
