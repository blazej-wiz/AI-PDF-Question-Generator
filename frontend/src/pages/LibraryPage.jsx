import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listDocuments, getCardsForDocument } from "../api";
import styles from "./LibraryPage.module.css";

export default function LibraryPage() {
  const navigate = useNavigate();
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        setError("");
        setLoading(true);
        const data = await listDocuments();
        setDocs(data || []);
      } catch (e) {
        setError(e.message || "Failed to load library.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function onStudy(doc) {
    try {
      setError("");
      const cards = await getCardsForDocument({ documentId: doc.id });

      navigate("/study", {
        state: {
          cards,
          questionType: (cards?.[0]?.type || "mcq"), // best guess
          documentId: doc.id,
          documentTitle: doc.title,
          fromLibrary: true,
        },
      });
    } catch (e) {
      setError(e.message || "Failed to load deck.");
    }
  }

  return (
    <div className={styles.shell}>
      <div className={styles.card}>
        <div className={styles.topRow}>
          <div>
            <h1 className={styles.title}>Library</h1>
            <p className={styles.subtitle}>Saved decks you can revisit anytime.</p>
          </div>

          <button className={styles.secondaryButton} onClick={() => navigate("/")}>
            + New Generation
          </button>
        </div>

        {loading && <div className={styles.muted}>Loading…</div>}
        {error && <div className={styles.error}>{error}</div>}

        {!loading && !docs.length && (
          <div className={styles.muted}>
            No saved decks yet. Generate questions and save them to your library.
          </div>
        )}

        <div className={styles.list}>
          {docs.map((d) => (
            <div key={d.id} className={styles.row}>
              <div className={styles.rowLeft}>
                <div className={styles.docTitle}>{d.title}</div>
                <div className={styles.docMeta}>Deck ID: {d.id}</div>
              </div>
              <button className={styles.primaryButton} onClick={() => onStudy(d)}>
                Study
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
