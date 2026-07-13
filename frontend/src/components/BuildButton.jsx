import { useState } from "react";

import {
  uploadStudyMaterial,
  ingestFiles,
  uploadPyqs,
} from "../services/api";

function IngestButton() {
  const [loading, setLoading] = useState(false);

  const handleIngest = async () => {
    try {
      setLoading(true);

      await ingestFiles();

      alert("Ingestion completed");
    } catch (error) {
      console.error("INGESTION ERROR:", error);
      alert("Ingestion failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <button onClick={handleIngest} disabled={loading}>
      {loading ? "Ingesting..." : "Build Knowledge Base"}
    </button>
  );
}

export default IngestButton;
function BuildButton({ studyFiles, pyqFiles }) {
  const [loading, setLoading] = useState(false);
  const [uploaded, setUploaded] = useState(0);

  const totalFiles = studyFiles.length + pyqFiles.length;

  const handleBuild = async () => {
    try {
      setLoading(true);
      setUploaded(0);

      for (const file of studyFiles) {
        await uploadStudyMaterial(file);
        setUploaded((count) => count + 1);
      }

      for (const file of pyqFiles) {
        await uploadPyqs(file);
        setUploaded((count) => count + 1);
      }
    } catch (error) {
      console.error("UPLOAD ERROR:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button
        onClick={handleBuild}
        disabled={loading || totalFiles === 0}
      >
        {loading ? "Uploading..." : "Build Knowledge Base"}
      </button>

      {loading && (
        <p>
          Uploaded {uploaded} / {totalFiles} files
        </p>
      )}
    </div>
  );
}

export default BuildButton;