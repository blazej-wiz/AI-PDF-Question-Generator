import { useMemo, useState } from "react";
import Flashcard from "./Flashcard";
import styles from "./FlashcardDeck.module.css";
import { postProgress } from "../api";

export default function FlashcardDeck({ cards, questionType = "mcq" }) {
  const [index, setIndex] = useState(0);
  const [finished, setFinished] = useState(false);

  const prev = () => setIndex((i) => Math.max(i - 1, 0));
  const next = () => setIndex((i) => Math.min(i + 1, cards.length - 1));

  const current = useMemo(() => cards[index], [cards, index]);

  async function mark(correct) {
    const card = cards[index];

    // Last card: record progress (if possible) then show "Done"
    if (index === cards.length - 1) {
      if (card?.id) {
        try {
          await postProgress({ cardId: card.id, correct });
        } catch {
          // ignore for now
        }
      }
      setFinished(true);
      return;
    }

    // If not saved (no id), just move on
    if (!card?.id) {
      next();
      return;
    }

    try {
      await postProgress({ cardId: card.id, correct });
    } catch {
      // ignore for now
    } finally {
      next();
    }
  }

  // ✅ MUST be inside the component, before the main return
  if (finished) {
    return (
      <div className={styles.deck}>
        <div className={styles.topRow}>
          <div className={styles.titleWrap}>
            <div className={styles.title}>Done 🎉</div>
            <div className={styles.subtitle}>
              You’ve finished this set of questions.
            </div>
          </div>
        </div>

        <div className={styles.controls}>
          <button
            className={styles.secondaryButton}
            onClick={() => {
              setIndex(0);
              setFinished(false);
            }}
          >
            Restart
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.deck}>
      <div className={styles.topRow}>
        <div className={styles.titleWrap}>
          <div className={styles.title}>Study</div>
          <div className={styles.subtitle}>
            Click the card to reveal the answer.
          </div>
        </div>

        <div className={styles.pill}>
          {questionType.toUpperCase()} • {index + 1}/{cards.length}
        </div>
      </div>

      <Flashcard
  key={current?.id ?? index}
  card={current}
  questionType={questionType}
/>


      <div className={styles.controls}>
        <button
          className={styles.secondaryButton}
          onClick={prev}
          disabled={index === 0}
        >
          ← Prev
        </button>

        <div className={styles.gradeRow}>
          <button className={styles.badButton} onClick={() => mark(false)}>
            ✗ Incorrect
          </button>
          <button className={styles.goodButton} onClick={() => mark(true)}>
            ✓ Correct
          </button>
        </div>

        <button
          className={styles.secondaryButton}
          onClick={next}
          disabled={index === cards.length - 1}
        >
          Next →
        </button>
      </div>
    </div>
  );
}
