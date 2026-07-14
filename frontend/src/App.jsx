import { useEffect, useState } from "react";
import "./index.css";
import "./App.css";
import Navbar from "./components/Navbar";
import UploadCard from "./components/UploadCard";
import UploadedFiles from "./components/UploadedFiles";
import QueryBox from "./components/QueryBox";
import AnswerBox from "./components/AnswerBox";
import Button from "./components/Button";

import {
  getUploadedFiles,
  generateAnswer,
  uploadStudyMaterial,
  uploadPyqs,
  ingestFiles,
} from "./services/api";

function App() {
  const [studyFiles, setStudyFiles] = useState([]);
  const [pyqFiles, setPyqFiles] = useState([]);

  const [uploadedStudyFiles, setUploadedStudyFiles] = useState([]);
  const [uploadedPyqFiles, setUploadedPyqFiles] = useState([]);

  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");

  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(0);

  const [ingesting, setIngesting] = useState(false);
  const [generating, setGenerating] = useState(false);

  const totalFiles = studyFiles.length + pyqFiles.length;

  const fetchUploadedFiles = async () => {
    try {
      const data = await getUploadedFiles();

      setUploadedStudyFiles(data.study_files);
      setUploadedPyqFiles(data.pyq_files);
    } catch (error) {
      console.error("FETCH FILES ERROR:", error);
    }
  };

  useEffect(() => {
    fetchUploadedFiles();
  }, []);

  const handleUpload = async () => {
    try {
      setUploading(true);
      setUploaded(0);

      for (const file of studyFiles) {
        await uploadStudyMaterial(file);
        setUploaded((prev) => prev + 1);
      }

      for (const file of pyqFiles) {
        await uploadPyqs(file);
        setUploaded((prev) => prev + 1);
      }

      await fetchUploadedFiles();

      setStudyFiles([]);
      setPyqFiles([]);
    } catch (error) {
      console.error("UPLOAD ERROR:", error);
    } finally {
      setUploading(false);
    }
  };

  const handleIngest = async () => {
    try {
      setIngesting(true);

      await ingestFiles();

      alert("Knowledge base built successfully");
    } catch (error) {
      console.error("INGESTION ERROR:", error);
    } finally {
      setIngesting(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setGenerating(true);

      const data = await generateAnswer(query);

      setAnswer(data.answer);
    } catch (error) {
      console.error("GENERATION ERROR:", error);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="app-container">
      <aside className="left-sidebar">
        <div className="upload-container">
          <UploadCard
            title="Study Material"
            setFiles={setStudyFiles}
          />

          <UploadCard
            title="Previous Year Papers"
            setFiles={setPyqFiles}
          />
        </div>

        <div className="action-buttons">
          <Button
            onClick={handleUpload}
            disabled={uploading || totalFiles === 0}
          >
            {uploading ? "Uploading..." : "Upload Files"}
          </Button>

          <Button
            onClick={handleIngest}
            disabled={ingesting}
            className="secondary"
          >
            {ingesting ? "Ingesting..." : "Ingest"}
          </Button>
        </div>

        {uploading && (
          <p>
            Uploaded {uploaded} / {totalFiles}
          </p>
        )}
      </aside>

      <main className="main-content">
        <section className="hero-card">
          <p className="eyebrow">AI Study Assistant</p>
          <h1>Turn your notes into polished question papers.</h1>
          <p>Upload study material and previous papers, then generate a clear paper in seconds.</p>
        </section>

        <QueryBox
          query={query}
          setQuery={setQuery}
          onGenerate={handleGenerate}
          loading={generating}
        />

        <AnswerBox answer={answer} />
      </main>

      <aside className="right-sidebar">
        <UploadedFiles
          studyFiles={uploadedStudyFiles}
          pyqFiles={uploadedPyqFiles}
        />
      </aside>
    </div>
  );
}

export default App;