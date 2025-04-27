import React from "react";
import { Routes, Route } from "react-router-dom";
import UploadCard from "./Components/UploadCard";
import CaptureFace from "./Components/CaptureFace";
import ViewResult from "./Components/ViewResult"; 

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<UploadCard />} />
        <Route path="/capture-face" element={<CaptureFace />} />
        <Route path="/view-result" element={<ViewResult />} />
      </Routes>
    </div>
  );
}

export default App;