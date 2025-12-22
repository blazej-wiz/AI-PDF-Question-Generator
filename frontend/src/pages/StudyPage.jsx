import { useLocation, useNavigate } from "react-router-dom";
import FlashcardDeck from "../components/FlashcardDeck";
import styles from "./StudyPage.module.css";

export default function StudyPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const cards = location.state?.cards ?? [];
  const questionType = location.state?.questionType ?? "mcq";

  if (!cards.length) {
    return (
      <div className={styles.shell}>
        <div className={styles.card}>
          <h2 className={styles.emptyTitle}>No cards found</h2>
          <p className={styles.emptyText}>
            Generate some questions first, then you’ll see them here.
          </p>
          <button
            className={styles.primaryButton}
            onClick={() => navigate("/")}
          >
            Back to Generator
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.shell}>
      <div className={styles.card}>
        {/* 👇 NEW: back button */}
        <button
          className={styles.backButton}
          onClick={() => navigate("/")}
        >
          ← Back to Generator
        </button>

        <FlashcardDeck cards={cards} questionType={questionType} />
      </div>
    </div>
  );
}
