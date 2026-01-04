import { useMemo, useState } from "react";
import styles from "./Flashcard.module.css";

export default function Flashcard({ card, questionType = "mcq" }) {
  const [flipped, setFlipped] = useState(false);

  const isMCQ = questionType === "mcq";
  const options = Array.isArray(card?.options) ? card.options : [];

  const resolvedAnswer = useMemo(() => {
    if (!card) return "No answer provided.";

    if (isMCQ) {
      const letter = card.correct_answer;
      if (
        typeof letter === "string" &&
        letter.length === 1 &&
        letter >= "A" &&
        letter <= "Z"
      ) {
        const idx = letter.charCodeAt(0) - 65;
        const text = options[idx] ?? "No answer provided.";
        return `${letter}. ${text}`;
      }
      return "No answer provided.";
    }

    return card.answer || "No answer provided.";
  }, [card, isMCQ, options]);

  return (
    <div className={styles.scene}>
      <div className={[styles.inner, flipped ? styles.innerFlipped : ""].join(" ")}>
        {/* FRONT */}
        <div className={`${styles.face} ${styles.front}`}>
          <div
            className={styles.card}
            role="button"
            tabIndex={0}
            onClick={() => setFlipped((v) => !v)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") setFlipped((v) => !v);
            }}
          >
            <div className={styles.content}>
              <div className={styles.kicker}>Question</div>
              <div className={styles.question}>{card?.question}</div>

              {isMCQ && options.length > 0 && (
                <ul className={styles.choices}>
                  {options.map((opt, i) => (
                    <li key={i} className={styles.choice}>
                      <span className={styles.choiceKey}>
                        {String.fromCharCode(65 + i)}
                      </span>
                      <span className={styles.choiceText}>{opt}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className={styles.hint}>Click to flip</div>
          </div>
        </div>

        {/* BACK */}
        <div className={`${styles.face} ${styles.back}`}>
          <div
            className={styles.card}
            role="button"
            tabIndex={0}
            onClick={() => setFlipped((v) => !v)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") setFlipped((v) => !v);
            }}
          >
            <div className={styles.content}>
              <div className={styles.kicker}>Answer</div>
              <div className={styles.answer}>{resolvedAnswer}</div>

              {card?.explanation && (
                <div className={styles.explanation}>
                  <div className={styles.explanationTitle}>Explanation</div>
                  <div className={styles.explanationText}>{card.explanation}</div>
                </div>
              )}
            </div>
            <div className={styles.hint}>Click to flip</div>
          </div>
        </div>
      </div>
    </div>
  );
}
