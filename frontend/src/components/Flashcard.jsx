import { useMemo, useState } from "react";
import styles from "./Flashcard.module.css";

export default function Flashcard({ card, questionType = "mcq" }) {
  const [flipped, setFlipped] = useState(false);

  const isMCQ = questionType === "mcq";

  const options = Array.isArray(card.options) ? card.options : [];

  const resolvedAnswer = useMemo(() => {
  if (isMCQ) {
    const letter = card.correct_answer;
    if (
      typeof letter === "string" &&
      letter.length === 1 &&
      letter >= "A" &&
      letter <= "Z"
    ) {
      const index = letter.charCodeAt(0) - 65;
      const optionText = options[index];
      const cleaned = optionText?.replace(/^\s*[A-D]\s*[\)\.\:\-]\s*/i, "");
return cleaned ? `${letter}. ${cleaned}` : "No answer provided.";

    }
    return "No answer provided.";
  }

  // SAQ
  return (
  card.answer ||
  card.model_answer ||
  card.correct_answer ||
  card.response ||
  "No answer provided."
);

}, [card, isMCQ, options]);


return (
  <div className={styles.scene}>
    <div
      className={styles.card}
      role="button"
      tabIndex={0}
      onClick={() => setFlipped((v) => !v)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          setFlipped((v) => !v);
        }
      }}
    >
      <div
        className={`${styles.inner} ${
          flipped ? styles.innerFlipped : ""
        }`}
      >
        {/* Front face */}
        <div className={`${styles.face}`}>
          <div className={styles.content}>
            <div className={styles.kicker}>Question</div>
            <div className={styles.question}>{card.question}</div>

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

        {/* Back face */}
        <div className={`${styles.face} ${styles.back}`}>
          <div className={styles.content}>
            <div className={styles.kicker}>Answer</div>
            <div className={styles.answer}>{resolvedAnswer}</div>

            {card.explanation && (
              <div className={styles.explanation}>
                <div className={styles.explanationTitle}>
                  Explanation
                </div>
                <div className={styles.explanationText}>
                  {card.explanation}
                </div>
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
