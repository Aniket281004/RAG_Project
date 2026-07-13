const BASE_URL = "http://127.0.0.1:8000";

const uploadFile = async (file, endpoint) => {
  const formData = new FormData();

  formData.append("files", file);

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error);
  }

  return response.json();
};

export const uploadStudyMaterial = (file) => {
  return uploadFile(file, "/upload/study-material");
};

export const uploadPyqs = (file) => {
  return uploadFile(file, "/upload/pyqs");
};

export const getUploadedFiles = async () => {
  const response = await fetch(`${BASE_URL}/files`);

  if (!response.ok) {
    throw new Error("Failed to fetch uploaded files");
  }

  return response.json();
};

export const generateAnswer = async (query) => {
  const response = await fetch(
    `${BASE_URL}/ask?query=${encodeURIComponent(query)}`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error);
  }

  return response.json();
};

export const ingestFiles = async () => {
  const response = await fetch(`${BASE_URL}/ingest`, {
    method: "POST",
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error);
  }

  return response.json();
};