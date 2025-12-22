import { Routes, Route } from "react-router-dom";
import GeneratorPage from "./pages/GeneratorPage";
import StudyPage from "./pages/StudyPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<GeneratorPage />} />
      <Route path="/study" element={<StudyPage />} />
    </Routes>
  );
}
