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
    <div className="flex flex-col items-center justify-center p-6">
      <div className="relative group perspective">
        {!recording ? (
          <button  
            className="relative px-8 py-4 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 font-bold text-white shadow-xl shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:-translate-y-1 transition-all duration-300 text-lg flex items-center gap-3 w-full justify-center overflow-hidden" 
            onClick={startRecording}
          >
            <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            Start Analyzing
          </button>
        ) : (
          <button 
            onClick={stopRecording}
            className="relative px-8 py-4 rounded-full bg-gradient-to-r from-rose-500 to-red-600 font-bold text-white shadow-xl shadow-red-500/30 hover:shadow-red-500/50 hover:-translate-y-1 transition-all duration-300 text-lg flex items-center gap-3 w-full justify-center"
          >
            <span className="w-3 h-3 rounded-full bg-white animate-pulse"></span>
            Stop & Process
          </button>
        )}
      </div>
      {recording && (
        <div className="mt-6 flex gap-1 items-center h-8">
          {[1,2,3,4,5,6,7].map((i) => (
            <div key={i} className={`w-1.5 bg-indigo-400 rounded-full animate-[bounce_1s_infinite]`} style={{ animationDelay: `${i * 0.1}s`, height: `${Math.random() * 100 + 40}%` }}></div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Recorder;