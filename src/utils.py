import json
def export_chunks_to_json(chunks, filename):
    """
    Export retrieved chunks to JSON.
    """

    data = []

    for i, chunk in enumerate(chunks):
        data.append({
            "chunk_id": i,
            "content": chunk.page_content,
            "metadata": chunk.metadata
        })

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(chunks)} chunks to {filename}")