import axios from "axios";

const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
    headers: {
        "Content-Type": "application/json",
    },
});

export default api;

/* ---------------- Upload APIs ---------------- */

export const uploadStudyMaterial = async (files) => {

    const formData = new FormData();

    Array.from(files).forEach((file) => {
        formData.append("files", file);
    });

    const response = await api.post(
        "/upload/study-material",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
};

export const uploadPYQs = async (files) => {

    const formData = new FormData();

    Array.from(files).forEach((file) => {
        formData.append("files", file);
    });

    const response = await api.post(
        "/upload/pyqs",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
};

/* ---------------- Ingestion API ---------------- */

export const buildKnowledgeBase = async () => {

    const response = await api.post("/ingest");

    return response.data;
};

/* ---------------- RAG API ---------------- */

export const askQuestion = async (query) => {

    const response = await api.post("/ask", {
        query: query,
    });

    return response.data;
};