import { useMemo, useState } from "react";
import Flashcard from "./Flashcard";
import styles from "./FlashcardDeck.module.css";

export default function FlashcardDeck({ cards, questionType = "mcq" }) {
  const [index, setIndex] = useState(0);

  const prev = () => setIndex((i) => Math.max(i - 1, 0));
  const next = () => setIndex((i) => Math.min(i + 1, cards.length - 1));

  const current = useMemo(() => cards[index], [cards, index]);

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
  key={index}
  card={current}
  questionType={questionType}
/>


      <div className={styles.controls}>
        <button className={styles.secondaryButton} onClick={prev} disabled={index === 0}>
          ← Prev
        </button>

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
