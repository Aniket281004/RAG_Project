import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'
import Navbar from "./components/Navbar";
import UploadCard from "./components/UploadCard";
import IngestPanel from "./components/BuildButton";
import QueryBox from "./components/QueryBox";
import AnswerBox from "./components/AnswerBox";

function App() {

    return (
        <>
            <Navbar />

            <div className="upload-section">

                <UploadCard
                    title="Study Material"
                    endpoint="/upload/study-material"
                />

                <UploadCard
                    title="Previous Year Questions"
                    endpoint="/upload/pyqs"
                />

            </div>

            <IngestPanel />

            <QueryBox />

            <AnswerBox />

        </>
    );
}

export default App
