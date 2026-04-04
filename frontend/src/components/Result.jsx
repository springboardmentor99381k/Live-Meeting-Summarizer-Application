import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
function Result({ result, jobId }) {
  const [email, setEmail] = useState("");
  const [sending, setSending] = useState(false);

  const handleSendEmail = async () => {
    if (!email) return alert("Enter Email");

    setSending(true);
    const res = await fetch(`http://localhost:8000/send-email/${jobId}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
        }),
      });

    const data = await res.json();

    alert(data.message);
    setSending(false);
  };

  return (
    <div className="mt-8 bg-white shadow-xl rounded-2xl p-6 space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-2">Transcript</h2>
        <div className="bg-gray-100 p-4 rounded-lg max-h-60 overflow-y-auto text-sm">
          {result.transcript_lines?.map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-2">Summary</h2>
        {/* <p className="bg-gray-50 p-4 rounded-lg">
          {result.summary}
          </p> */}

        <div className="bg-gray-50 p-4 rounded-lg">

          <ReactMarkdown >
            {result.summary}
          </ReactMarkdown>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium mb-2">Send to Email</h3>
        <div className="flex gap-2">
          <input
            type="email"
            placeholder="Enter Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <button
            onClick={handleSendEmail}
            disabled={sending}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition"
          >
            {sending ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Result;