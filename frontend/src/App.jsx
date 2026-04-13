import React, { useState } from "react";
import Recorder from "./components/Recorder.jsx";
import Status from "./components/Status.jsx";
import Result from "./components/Result.jsx";
import SendEmail from "./components/SendEmail.jsx";
import './App.css';

function App() {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);

  const handleUploadSuccess = (jobId) => {
    setJobId(jobId);
    setStatus("processing")

    const eventSource = new EventSource(
      `http://127.0.0.1:8000/stream/${jobId}`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStatus(data.status);
      if (data.status === "completed") {
        setResult(data.result);
        eventSource.close();
      }
    }
  }

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-200 font-['Outfit'] relative overflow-hidden">
      {/* Background Orbs */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-900/40 blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-purple-900/30 blur-[120px] pointer-events-none"></div>
      
      {/* Top Nav */}
      <nav className="w-full border-b border-white/10 bg-white/5 backdrop-blur-xl px-8 py-5 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold tracking-wide text-white">
            Meeting<span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">AI</span>
          </h1>
        </div>
        <div className="hidden md:flex items-center gap-4">
          <div className="text-xs font-semibold px-4 py-2 bg-white/5 border border-white/10 text-indigo-300 rounded-full shadow-inner">
            {jobId ? `SESSION ID: ${jobId.substring(0, 8)}` : "SYSTEM READY"}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 p-6 lg:p-12 relative z-10">
        
        {/* Left Column */}
        <div className="lg:col-span-4 space-y-8">
          <div className="bg-white/5 backdrop-blur-md rounded-3xl border border-white/10 p-8 shadow-2xl relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            
            <div className="flex items-center gap-3 mb-8 relative z-10">
              <h2 className="text-sm font-bold text-indigo-300 uppercase tracking-[0.2em]">Input Hub</h2>
              <div className="h-px flex-1 bg-gradient-to-r from-indigo-500/40 to-transparent"></div>
            </div>
            
            <div className="relative z-10">
              <Recorder onSuccess={handleUploadSuccess} />
            </div>

            <div className="mt-8 space-y-4">
              <p className="text-sm text-slate-400 text-center flex items-center justify-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                Secure Local Processing
              </p>
            </div>
          </div>

          {status && (
            <div className="bg-gradient-to-br from-[#131624] className to-[#0f1118] rounded-3xl shadow-2xl border border-indigo-500/20 p-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
               <div className="flex items-center justify-between mb-6">
                  <h3 className="text-sm font-bold text-slate-300 tracking-wide uppercase">Live Analysis</h3>
                  {status === "processing" && (
                    <div className="w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
                  )}
               </div>
               <div className="p-6 bg-white/5 rounded-2xl border border-white/5 backdrop-blur-sm">
                  <Status status={status} />
               </div>
            </div>
          )}

          <div className="p-8 border border-white/5 bg-white/5 backdrop-blur-sm rounded-3xl hidden md:block">
            <h4 className="text-sm font-bold text-slate-300 mb-4 tracking-wide uppercase">AI Pipeline</h4>
            <ul className="text-sm text-slate-400 space-y-4">
              <li className="flex gap-3 items-center"><div className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs">1</div> High-fidelity recording</li>
              <li className="flex gap-3 items-center"><div className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs">2</div> Pyannote Diarization</li>
              <li className="flex gap-3 items-center"><div className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs">3</div> Whisper Transcription</li>
              <li className="flex gap-3 items-center"><div className="w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center text-xs">4</div> LLM Extraction</li>
            </ul>
          </div>
        </div>

        {/* Right Column */}
        <div className="lg:col-span-8">
          {!result && !status && (
            <div className="h-[600px] flex flex-col items-center justify-center bg-white/5 backdrop-blur-sm rounded-3xl border border-white/5 text-slate-400 p-12 text-center shadow-xl">
              <div className="w-24 h-24 bg-white/5 rounded-full flex items-center justify-center mb-8 relative">
                <div className="absolute inset-0 rounded-full border border-indigo-500/30 animate-ping opacity-20"></div>
                <svg className="w-12 h-12 text-indigo-400/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-2xl font-semibold text-slate-200 mb-3 tracking-wide">Awaiting Transmission</h3>
              <p className="max-w-md text-slate-500 leading-relaxed">Initiate recording to generate an AI-powered meeting synthesis. Insights will manifest here in real-time.</p>
            </div>
          )}

          {(status || result) && (
            <div className="space-y-6 animate-in slide-in-from-bottom-8 duration-700">
              <div className="bg-[#11141e]/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-indigo-500/20 overflow-hidden relative">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>
                <div className="border-b border-white/5 px-10 py-6 flex justify-between items-center bg-white/5">
                  <div className="flex items-center gap-4">
                    <span className={`relative flex h-4 w-4`}>
                      {status !== 'completed' && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>}
                      <span className={`relative inline-flex rounded-full h-4 w-4 ${status === 'completed' ? 'bg-green-400' : 'bg-indigo-500'}`}></span>
                    </span>
                    <h3 className="font-semibold text-lg text-slate-200 tracking-wide">
                      {status === 'completed' ? 'Intelligence Report' : 'Synthesizing Data...'}
                    </h3>
                  </div>
                </div>
                
                <div className="p-10 min-h-[500px]">
                  {result ? (
                    <div className="prose prose-invert prose-indigo max-w-none prose-headings:font-bold prose-headings:tracking-tight hover:prose-a:text-indigo-400">
                      <Result result={result} jobId={jobId} />
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full py-32 text-slate-400 gap-8">
                      <div className="w-20 h-20 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin shadow-xl shadow-indigo-500/10"></div>
                      <p className="animate-pulse font-medium tracking-wide text-indigo-300">Extracting Insights from Audio Stream...</p>
                    </div>
                  )}
                </div>
              </div>

              {result && (
                <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-3xl p-10 text-white shadow-2xl shadow-purple-500/20 transform transition-all hover:scale-[1.01] relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-12 opacity-10 pointer-events-none">
                    <svg className="w-48 h-48" fill="currentColor" viewBox="0 0 24 24"><path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/><path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/></svg>
                  </div>
                  <div className="flex flex-col md:flex-row items-center justify-between gap-10 relative z-10">
                    <div className="text-center md:text-left">
                      <h3 className="text-3xl font-bold mb-3 tracking-tight">Distribute Findings</h3>
                      <p className="text-indigo-100/90 text-lg">Send this synthesized intelligence report to key stakeholders.</p>
                    </div>
                    <div className="w-full md:w-auto bg-white/10 p-2 rounded-2xl backdrop-blur-md border border-white/20">
                      <SendEmail jobId={jobId} />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <footer className="py-12 border-t border-white/5 mt-12 bg-[#090b10]">
        <p className="text-center text-slate-500 text-sm tracking-widest uppercase">
          &copy; {new Date().getFullYear()} MeetingAI • Encrypted & Secure
        </p>
      </footer>
    </div>
  );
}

export default App;