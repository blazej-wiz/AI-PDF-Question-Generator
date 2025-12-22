# 📘 AI PDF Question Generator & Study App

A full-stack web application that allows users to upload PDF lecture notes and automatically generate **AI-powered study questions** (MCQs or SAQs), then review them using an interactive **flashcard-based study interface**.

This project demonstrates clean UI design, robust AI integration, and real-world handling of inconsistent LLM outputs.

---

## ✨ Features

- 📄 Upload PDF lecture notes
- 🧠 Generate AI-based questions from content
- 📝 Supports **MCQ** and **SAQ** formats
- 🔀 Randomized MCQ options (no “always A” bias)
- 🃏 Flashcard-style study mode
- 🔁 Flip cards to reveal answers and explanations
- ⏮️ Navigate between questions
- 🎨 Minimal SaaS-style UI
- 🛡️ Defensive backend handling for unpredictable AI output

---

## 🧱 Tech Stack

**Frontend**
- React (Vite)
- React Router
- CSS Modules

**Backend**
- FastAPI
- OpenAI API
- PyPDF

---

## 🚀 Run Locally (Full Setup)

Follow the steps below to run the project locally.

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-pdf-question-generator.git
cd ai-pdf-question-generator

# 2. Create and activate a virtual environment (backend)
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Set your OpenAI API key
# macOS / Linux
export OPENAI_API_KEY=your_api_key_here

# Windows PowerShell
setx OPENAI_API_KEY "your_api_key_here"

# (Restart terminal after setting the key on Windows)

# 5. Start the backend
uvicorn main:app --reload

#Open new terminal for frontend

# 6. Install frontend dependencies
npm install

# 7. Start the frontend
npm run dev

## 🧠 How It Works

1. The user uploads a PDF document.
2. The backend extracts text from the PDF.
3. OpenAI generates study questions based on the extracted content.
4. The backend normalizes the AI output into a stable, predictable schema.
5. The frontend renders the questions as interactive flashcards.
6. Users flip flashcards to reveal answers and explanations.

---

## 🛡️ Backend Robustness

The backend includes defensive logic to handle common AI output issues, including:

- MCQ options returned as lists **or** dictionaries
- Incorrect or inconsistent option counts
- Invalid correct answer indices
- Malformed or partially invalid AI responses

This ensures the frontend always receives reliable and predictable data, preventing UI crashes.

---

## 🔮 Future Improvements

- Answer selection and scoring
- Question amount flexibility
- Potential AI chatbot to explain further
- Difficulty levels
- Progress tracking per PDF
