import React, { useState } from "react";

function Upload({ onSuccess }) {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) return alert("Select a file");

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://127.0.0.1:8000/process/", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    onSuccess(data.job_id);
  };

  return (
    <div>
      <input
        type="file"
        accept="audio/*"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
}

export default Upload;