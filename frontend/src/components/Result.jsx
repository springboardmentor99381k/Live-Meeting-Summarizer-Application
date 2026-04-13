import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from 'remark-gfm';

function Result({ result, jobId }) {
  if (!result) return null;

  return (
    <div className="space-y-8">
      
      {/* Transcript Section */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
        <h2 className="text-sm font-bold text-indigo-300 uppercase tracking-widest mb-4 flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
          Raw Transcript
        </h2>
        <div className="bg-[#0b0c10] border border-white/5 p-5 rounded-xl h-48 overflow-y-auto text-sm space-y-2 custom-scrollbar">
          {result.transcript_lines?.map((line, i) => (
            <div key={i} className="text-slate-300 leading-relaxed group hover:bg-white/5 px-2 py-1 rounded transition-colors">
              {line}
            </div>
          ))}
        </div>
      </div>

      {/* Summary Section */}
      <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 rounded-2xl p-8 backdrop-blur-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/20 rounded-full blur-3xl"></div>
        <h2 className="text-sm font-bold text-indigo-300 uppercase tracking-widest mb-6 flex items-center gap-2 relative z-10">
          <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          AI Synthesized Summary
        </h2>
        
        <div className="relative z-10 text-slate-200 text-lg leading-relaxed font-light">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {result.summary}
          </ReactMarkdown>
        </div>
      </div>

    </div>
  );
}

export default Result;