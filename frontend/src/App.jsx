import React, { useState } from "react";
import ReactLoading from 'react-loading';
import ReactMarkdown from "react-markdown";
import Upload from "./components/Upload.jsx";
import Status from "./components/Status.jsx";
import Result from "./components/Result.jsx";
import SendEmail from "./components/SendEmail.jsx";
import Recorder from "./components/Recorder.jsx";
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
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans">
      {/* Top Navigation Bar */}
      <nav className="w-full bg-white border-b border-slate-200 px-6 py-4 flex justify-between items-center sticky top-0 z-20 shadow-sm">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center shadow-indigo-200 shadow-lg">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </div>
          <h1 className="text-xl font-bold tracking-tight">Live-Meeting-Summarizer<span className="text-indigo-600">AI</span></h1>
        </div>
        <div className="hidden md:flex items-center gap-4">
          <div className="text-xs font-medium px-3 py-1 bg-slate-100 text-slate-500 rounded-full">
            {jobId ? `JOB: ${jobId.substring(0, 8)}` : "System Ready"}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 p-6 lg:p-10">
        
        {/* Left Column: Controls (4 Units wide) */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center gap-3 mb-6">
              <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Input Source</h2>
              <div className="h-px flex-1 bg-slate-100"></div>
            </div>
            
            <div className="bg-slate-50 rounded-xl border-2 border-dashed border-slate-200 p-4 transition-all hover:border-indigo-300">
              <Recorder onSuccess={handleUploadSuccess} />
            </div>

            <div className="mt-6 space-y-3">
              <p className="text-xs text-slate-400 text-center italic">Supported: MP3, WAV, M4A</p>
            </div>
          </div>

          {/* Dynamic Status Dashboard Card */}
          {status && (
            <div className="bg-white rounded-2xl shadow-lg border border-indigo-100 p-6 animate-in fade-in zoom-in duration-300">
               <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-bold text-slate-700">Live Status</h3>
                  {status === "processing" && (
                    <ReactLoading type="bars" color="#4F46E5" height={20} width={20} />
                  )}
               </div>
               <div className="p-4 bg-indigo-50 rounded-xl border border-indigo-100">
                  <Status status={status} />
               </div>
            </div>
          )}

          {/* Dashboard Helper Line */}
          <div className="p-6 border border-slate-200 rounded-2xl border-dashed">
            <h4 className="text-sm font-semibold text-slate-600 mb-2">How it works</h4>
            <ul className="text-xs text-slate-500 space-y-2">
              <li className="flex gap-2"><span>1.</span> Record or upload meeting audio.</li>
              <li className="flex gap-2"><span>2.</span> AI transcribes and identifies speakers.</li>
              <li className="flex gap-2"><span>3.</span> Receive a summarized markdown report.</li>
            </ul>
          </div>
        </div>

        {/* Right Column: Results Stage (8 Units wide) */}
        <div className="lg:col-span-8">
          {!result && !status && (
            <div className="h-full min-h-[500px] flex flex-col items-center justify-center bg-white rounded-3xl border border-slate-200 border-dashed text-slate-400 p-12 text-center">
              <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-6">
                <svg className="w-10 h-10 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-600">No Analysis Yet</h3>
              <p className="max-w-xs mt-2">Start recording to see your meeting summary and actionable items appear here.</p>
            </div>
          )}

          {(status || result) && (
            <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
              <div className="bg-white rounded-3xl shadow-xl shadow-slate-200/60 border border-slate-200 overflow-hidden">
                <div className="bg-slate-50 border-b border-slate-200 px-8 py-5 flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <span className={`w-3 h-3 rounded-full ${status === 'completed' ? 'bg-green-500' : 'bg-amber-400 animate-pulse'}`}></span>
                    <h3 className="font-bold text-slate-700 tracking-tight">
                      {status === 'completed' ? 'Meeting Intelligence Report' : 'AI Analysis in Progress...'}
                    </h3>
                  </div>
                </div>
                
                <div className="p-8 min-h-[400px]">
                  {result ? (
                    <div className="prose prose-indigo max-w-none">
                      <Result result={result} jobId={jobId} />
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full py-20 text-slate-400">
                      <ReactLoading type="bubbles" color="#cbd5e1" height={100} width={100} />
                      <p className="mt-4 animate-pulse font-medium">Crunching your audio data...</p>
                    </div>
                  )}
                </div>
              </div>

              {result && (
                <div className="bg-indigo-600 rounded-3xl p-8 text-white shadow-xl shadow-indigo-200 transition-all hover:scale-[1.01]">
                  <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                    <div className="text-center md:text-left">
                      <h3 className="text-2xl font-bold mb-2">Share Summary</h3>
                      <p className="text-indigo-100 opacity-90">Ready to send the insights to your team via email?</p>
                    </div>
                    <div className="w-full md:w-auto">
                      <SendEmail jobId={jobId} />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <footer className="py-10 text-center">
        <p className="text-slate-400 text-sm">
          &copy; {new Date().getFullYear()} MeetingAI Dashboard • All data encrypted and secure.
        </p>
      </footer>
    </div>
  );
}

export default App;
// import React, { useState } from "react";
// import ReactLoading from 'react-loading';
// import ReactMarkdown from "react-markdown";
// import Upload from "./components/Upload.jsx";
// import Status from "./components/Status.jsx";
// import Result from "./components/Result.jsx";
// import SendEmail from "./components/SendEmail.jsx";
// import Recorder from "./components/Recorder.jsx";
// import './App.css';
// function App() {

//   const [jobId, setJobId] = useState(null);
//   const [status, setStatus] = useState(null);
//   const [result, setResult] = useState(null);

//   const handleUploadSuccess = (jobId) => {
//     setJobId(jobId);
//     setStatus("processing")

//     const eventSource = new EventSource(
//       `http://127.0.0.1:8000/stream/${jobId}`
//     );

//     eventSource.onmessage = (event) => {
//       const data = JSON.parse(event.data);

//       setStatus(data.status);
//       if (data.status === "completed") {
//         setResult(data.result);
//         eventSource.close();
//       }
//     }

//   }



//   return (
//     <div className="min-h-screen bg-gray-100 flex flex-col items-center px-4 py-10">

//       <div className="w-full max-w-2xl bg-white shadow-2xl rounded-2xl p-6">

//         <h1 className="text-3xl font-bold text-center mb-6">
//           Meeting Summarizer
//         </h1>

//         {/* test */}
//         {/* <div
//         className="bg-gray-50 p-4 rounded-lg">
//           <ReactMarkdown
//             remarkPlugins={[remarkGfm]}
            
//           >
//             {`**Key Discussion Points**
//               * The participants discussed the global rise and popularity of K-Pop.
//               * There is a consensus that K-Pop is currently "making waves" internationally and is being recognized for its high-quality music production.`}
//           </ReactMarkdown>

//         </div> */}

//         <Recorder onSuccess={handleUploadSuccess} />

//         {status && <Status status={status} />}

//         {result && <Result result={result} jobId={jobId} />}

//       </div>
//     </div>
//   );
// }

// export default App;