import React from "react";

function Status({ status }) {
  return (
    <div className="flex items-center gap-4">
      <div className="relative flex items-center justify-center w-12 h-12 rounded-full bg-white/5 border border-white/10">
        {status === "completed" ? (
          <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
          </svg>
        ) : (
          <div className="w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
        )}
      </div>
      <div>
        <p className="text-xs text-slate-500 uppercase tracking-widest font-bold mb-1">Current State</p>
        <p className="text-lg font-semibold text-slate-200 capitalize">
          {status}
        </p>
      </div>
    </div>
  );
}

export default Status;