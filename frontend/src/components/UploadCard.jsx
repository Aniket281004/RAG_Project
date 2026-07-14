import { useRef, useState } from "react";

function UploadCard({ title, setFiles }) {
  const inputRef = useRef(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = (files) => {
    const pdfFiles = Array.from(files).filter((file) =>
      file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")
    );

    setFiles(pdfFiles);
    setSelectedFiles(pdfFiles.map((file) => file.name));
  };

  const handleFileChange = (event) => {
    handleFiles(event.target.files || []);
    event.target.value = "";
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    handleFiles(event.dataTransfer.files || []);
  };

  const openPicker = () => {
    inputRef.current?.click();
  };

  return (
    <div className="upload-card">
      <h2>{title}</h2>

      <div
        className={`dropzone ${isDragging ? "dragging" : ""}`}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={openPicker}
        role="button"
        tabIndex={0}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            openPicker();
          }
        }}
      >
        <p className="dropzone-title">Drop PDF files here</p>
        <p className="dropzone-text">or click to browse</p>

        {selectedFiles.length > 0 && (
          <p className="dropzone-files">{selectedFiles.length} file(s) selected</p>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        multiple
        onChange={handleFileChange}
        className="visually-hidden"
      />
    </div>
  );
}

export default UploadCard;