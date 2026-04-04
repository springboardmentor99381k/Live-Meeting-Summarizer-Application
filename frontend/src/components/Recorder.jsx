import React, { useState, useRef } from "react";

function Recorder({ onSuccess }) {
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunks = useRef([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;

    chunks.current = [];

    mediaRecorder.ondataavailable = (e) => {
      chunks.current.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunks.current, { type: "audio/webm" });

      const formData = new FormData();
      formData.append("file", blob, "recording.webm");

      const res = await fetch("http://localhost:8000/process/", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      onSuccess(data.job_id);
    };

    mediaRecorder.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setRecording(false);
  };

  return (
    <div  className="flex justify-center mt-6">
      {!recording ? (
        <button  
        className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-3 rounded-full shadow-lg transition-all duration-300 text-lg" 
        onClick={startRecording}>
          Start Recording</button>
      ) : (
        <button 
        onClick={stopRecording}
        className="bg-gray-800 hover:bg-gray-900 text-white px-8 py-3 rounded-full shadow-lg transition-all duration-300 text-lg">
          Stop Recording</button>
      )}
    </div>
  );
}

export default Recorder;