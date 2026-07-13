function QueryBox({
  query,
  setQuery,
  onGenerate,
  loading,
}) {
  return (
    <div className="query-box">
      <h2>Generate Question Paper</h2>

      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Example: Generate a 60 mark question paper covering all units..."
      />

      <button
        onClick={onGenerate}
        disabled={loading || !query.trim()}
      >
        {loading ? "Generating..." : "Generate Paper"}
      </button>
    </div>
  );
}

export default QueryBox;