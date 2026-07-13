function UploadCard({ title, setFiles }) {
  const handleFileChange = (event) => {
    setFiles(Array.from(event.target.files));
  };

  return (
    <div className="upload-card">
      <h2>{title}</h2>

      <input
        type="file"
        accept=".pdf"
        multiple
        onChange={handleFileChange}
      />
    </div>
  );
}

export default UploadCard;