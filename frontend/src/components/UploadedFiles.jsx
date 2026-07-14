function UploadedFiles({ studyFiles, pyqFiles }) {
  return (
    <div className="uploaded-files">
      <h2>Uploaded Files</h2>

      <div className="sidebar-section">
        <h3>Study Material</h3>

        {studyFiles.length === 0 ? (
          <p className="empty-state">No study material uploaded</p>
        ) : (
          studyFiles.map((file) => (
            <div className="file-row" key={file}>{file}</div>
          ))
        )}
      </div>

      <div className="sidebar-section">
        <h3>Previous Year Papers</h3>

        {pyqFiles.length === 0 ? (
          <p className="empty-state">No PYQs uploaded</p>
        ) : (
          pyqFiles.map((file) => (
            <div className="file-row" key={file}>{file}</div>
          ))
        )}
      </div>
    </div>
  );
}

export default UploadedFiles;