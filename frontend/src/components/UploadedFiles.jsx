function UploadedFiles({ studyFiles, pyqFiles }) {
  return (
    <div className="uploaded-files">
      <h2>Uploaded Files</h2>

      <div>
        <h3>Study Material</h3>

        {studyFiles.length === 0 ? (
          <p>No study material uploaded</p>
        ) : (
          studyFiles.map((file) => (
            <p key={file}>{file}</p>
          ))
        )}
      </div>

      <div>
        <h3>Previous Year Papers</h3>

        {pyqFiles.length === 0 ? (
          <p>No PYQs uploaded</p>
        ) : (
          pyqFiles.map((file) => (
            <p key={file}>{file}</p>
          ))
        )}
      </div>
    </div>
  );
}

export default UploadedFiles;