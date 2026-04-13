import React, { useState } from "react";

function SendEmail({ jobId }) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("idle");

  const sendEmail = () => {
    if (!email) return;
    setStatus("sending");
    fetch(`http://127.0.0.1:8000/email/${jobId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email })
    }).then(res => res.json())
      .then(data => {
        setStatus("success");
      })
      .catch(err => {
        console.error(err);
        setStatus("error");
      });
  };

  return (
    <div className="flex gap-3 items-center w-full max-w-md relative">
      <div className="relative flex-1">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <svg className="w-5 h-5 text-indigo-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <input 
          type="email" 
          placeholder="colleague@company.com" 
          value={email}
          onChange={e => setEmail(e.target.value)}
          className="w-full pl-12 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-indigo-200/60 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all font-medium"
        />
      </div>
      <button 
        onClick={sendEmail}
        disabled={status === "sending" || !email}
        className={`px-8 py-3 rounded-xl font-bold transition-all duration-300 flex items-center gap-2 ${status === 'success' ? 'bg-green-500 text-white' : 'bg-white text-indigo-600 hover:bg-slate-100 disabled:opacity-50'}`}
      >
        {status === "sending" && <div className="w-4 h-4 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>}
        {status === "sending" ? "Sending" : status === "success" ? "Sent!" : "Send"}
      </button>
    </div>
  );
}

export default SendEmail;
