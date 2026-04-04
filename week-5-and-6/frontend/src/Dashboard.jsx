import React, { useState, useEffect, useRef } from 'react';
import { Mic, Square, RotateCcw, CheckCircle2, Circle, Lightbulb, CheckSquare, Trash2, Download, FileText } from 'lucide-react';
import jsPDF from 'jspdf';
import './Dashboard.css';

const STEPS = ["Recording", "Transcribing", "Diarizing", "Summarizing", "Done"];

export default function Dashboard({ logout }) {
  const userId = localStorage.getItem('userId');
  
  const [isRecording, setIsRecording] = useState(false);
  const [currentStep, setCurrentStep] = useState("Idle");
  const fileInputRef = useRef(null);
  
  const [liveTranscript, setLiveTranscript] = useState('');
  const [transcriptTurns, setTranscriptTurns] = useState([]);
  const [analytics, setAnalytics] = useState([]);
  const [summaryData, setSummaryData] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recognitionRef = useRef(null);
  
  // Session Metadata
  const [durationMinutes, setDurationMinutes] = useState(0);
  const [showSaveBar, setShowSaveBar] = useState(false);
  const [sessionName, setSessionName] = useState('');

  const [pastSessions, setPastSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [sessionToDelete, setSessionToDelete] = useState(null);

  const liveTranscriptRef = useRef(null);
  
  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    if (liveTranscriptRef.current) {
      if (activeSessionId) {
        liveTranscriptRef.current.scrollTop = 0;
      } else {
        liveTranscriptRef.current.scrollTop = liveTranscriptRef.current.scrollHeight;
      }
    }
  }, [liveTranscript, transcriptTurns, activeSessionId]);

  const fetchSessions = async () => {
    try {
      const res = await fetch(`https://aashikaarun123-live-meeting-summarizer.hf.space/api/sessions?user_id=${userId}`);
      const data = await res.json();
      setPastSessions(data);
    } catch (e) { console.error("Could not fetch sessions", e); }
  };

  const exportMD = () => {
    if (!summaryData) return;
    let md = `# Meeting Summary\n\n## Summary\n${summaryData.summary}\n\n`;
    md += `## Action Items\n${(summaryData.action_items || []).map(i => `- ${i}`).join('\n')}\n\n`;
    md += `## Key Decisions\n${(summaryData.decisions || []).map(i => `- ${i}`).join('\n')}\n\n`;
    md += `## Transcript\n${transcriptTurns.map(t => `**${t.speaker}** [${t.time}]: ${t.text}`).join('\n\n')}`;
    
    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `meeting_summary_${activeSessionId || 'export'}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportPDF = () => {
    if (!summaryData) return;
    const doc = new jsPDF();
    let y = 20;
    
    const printText = (text, isHeader = false) => {
      doc.setFontSize(isHeader ? 16 : 12);
      doc.setFont('helvetica', isHeader ? 'bold' : 'normal');
      const lines = doc.splitTextToSize(text || '', 170);
      lines.forEach(line => {
        if (y > 280) { doc.addPage(); y = 20; }
        doc.text(line, 20, y);
        y += isHeader ? 10 : 7;
      });
      y += isHeader ? 2 : 5;
    };

    printText("Meeting Summary", true);
    printText("Summary", true);
    printText(summaryData.summary);
    
    printText("Action Items", true);
    (summaryData.action_items || []).forEach(item => printText(`- ${item}`));
    
    printText("Key Decisions", true);
    (summaryData.decisions || []).forEach(item => printText(`- ${item}`));

    doc.save(`meeting_summary_${activeSessionId || 'export'}.pdf`);
  };

  const startRecording = async () => {
    resetUI();
    setIsRecording(true);
    setCurrentStep("Recording");
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.start();

      let persistentFinal = '';
      
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        
        recognition.onresult = (event) => {
          let interim = '';
          for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
              persistentFinal += event.results[i][0].transcript;
            } else {
              interim += event.results[i][0].transcript;
            }
          }
          setLiveTranscript(persistentFinal + ' ' + interim);
        };
        
        recognition.onerror = () => {};
        recognition.start();
        recognitionRef.current = recognition;
      } else {
        setLiveTranscript("Live transcript not supported in this browser. Audio is being recorded...");
      }
    } catch (e) {
      alert("Microphone access denied or error occurred.");
      setIsRecording(false);
      setCurrentStep("Idle");
    }
  };

  const uploadAudio = async (e) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    
    resetUI();
    setCurrentStep("Transcribing");
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      await fetch('https://aashikaarun123-live-meeting-summarizer.hf.space/api/upload', {
        method: 'POST',
        body: formData
      });
    } catch (err) {
      alert("Upload failed.");
      setCurrentStep("Idle");
    }
    
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const stopRecording = () => {
    if (!isRecording) return;
    setIsRecording(false);
    
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const file = new File([audioBlob], "recording.webm", { type: 'audio/webm' });
        
        setCurrentStep("Transcribing");
        const formData = new FormData();
        formData.append('file', file);
        
        try {
          await fetch('https://aashikaarun123-live-meeting-summarizer.hf.space/api/upload', {
            method: 'POST',
            body: formData
          });
        } catch (err) {
          alert("Upload failed.");
          setCurrentStep("Idle");
        }
        
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      };
      mediaRecorderRef.current.stop();
    }
  };

  const resetUI = () => {
    setLiveTranscript('');
    setTranscriptTurns([]);
    setAnalytics([]);
    setSummaryData(null);
    setCurrentStep("Idle");
    setShowSaveBar(false);
    setActiveSessionId(null);
  };

  const saveSessionToDb = async () => {
    if (!sessionName.trim()) return alert("Provide a name!");
    try {
      await fetch('https://aashikaarun123-live-meeting-summarizer.hf.space/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          name: sessionName,
          duration_minutes: durationMinutes,
          transcript: transcriptTurns,
          analytics: analytics,
          summary: summaryData
        })
      });
      setShowSaveBar(false);
      setSessionName('');
      fetchSessions();
    } catch (e) {
      alert("Failed to save.");
    }
  };

  const loadPastSession = (session) => {
    resetUI();
    setActiveSessionId(session._id);
    setTranscriptTurns(session.transcript || []);
    setAnalytics(session.analytics || []);
    setSummaryData(session.summary || null);
    setCurrentStep("Done");
  };

  const deleteSession = async (e, sessionId) => {
    e.stopPropagation();
    setSessionToDelete(sessionId);
  };

  const confirmDeleteSession = async () => {
    if (!sessionToDelete) return;
    try {
      await fetch(`https://aashikaarun123-live-meeting-summarizer.hf.space/api/sessions/${sessionToDelete}`, {
        method: 'DELETE'
      });
      if (activeSessionId === sessionToDelete) resetUI();
      fetchSessions();
    } catch (err) {
      alert("Failed to delete session.");
    } finally {
      setSessionToDelete(null);
    }
  };

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (showSaveBar || isRecording) return;
      
      if (activeSessionId !== null) {
        const isInteractiveBox = e.target.closest('.card') || 
                                 e.target.closest('.sessions-list li') || 
                                 e.target.closest('.sidebar-section') || 
                                 e.target.closest('.stepper-header') || 
                                 e.target.closest('.sidebar-bottom');
        if (!isInteractiveBox) {
          resetUI();
        }
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [activeSessionId, showSaveBar, isRecording]);

  useEffect(() => {
    let eventSource;
    const connectSSE = () => {
      eventSource = new EventSource('https://aashikaarun123-live-meeting-summarizer.hf.space/api/stream');
      
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'live_transcript') {
             setLiveTranscript(prev => prev + " " + data.text);
          } else if (data.type === 'status') {
             if (data.step) setCurrentStep(data.step);
             if (data.transcript) setTranscriptTurns(data.transcript);
             if (data.analytics) setAnalytics(data.analytics);
             if (data.summary) setSummaryData(data.summary);
          } else if (data.type === 'done') {
             setCurrentStep("Done");
             setDurationMinutes(data.duration_minutes || 0);
             setShowSaveBar(true);
          }
        } catch (e) {}
      };

      eventSource.onerror = () => {
        eventSource.close();
        setTimeout(connectSSE, 3000); // Implement SSE reconnection mechanism
      };
    };

    connectSSE();
    return () => eventSource?.close();
  }, []);

  const getStepStatus = (stepName) => {
     const iStep = STEPS.indexOf(stepName);
     const iCurrent = STEPS.indexOf(currentStep);
     if (currentStep === "Idle") return 'pending';
     if (iStep < iCurrent || currentStep === "Done") return 'completed';
     if (iStep === iCurrent) return 'active';
     return 'pending';
  };

  return (
    <div className="dashboard-layout">
      {/* Application Navigation Console */}
      <aside className="sidebar">
        <div className="app-logo sidebar-logo">
           <div className="logo-icon"><Mic size={20} color="#fff"/></div>
           <div className="logo-text"><b>MeetingAI</b><br/><span>Summarizer</span></div>
        </div>
        
        <div className="sidebar-section">
          <h5>CONTROLS</h5>
          <div className="btn-group">
            <button className="btn-control start" onClick={startRecording} disabled={isRecording || currentStep !== "Idle"}>
               ▶ Start
            </button>
            <button className="btn-control stop" onClick={stopRecording} disabled={!isRecording && currentStep !== "Idle"}>
               ⏹ Stop
            </button>
          </div>
          <div style={{ textAlign: 'center', margin: '0.5rem 0', color: '#64748b', fontSize: '0.8rem', fontWeight: 600 }}>OR</div>
          <input type="file" accept="audio/*" ref={fileInputRef} onChange={uploadAudio} style={{ display: 'none' }} />
          <button className="btn-upload" onClick={() => fileInputRef.current.click()} disabled={isRecording || currentStep !== "Idle"}>
             Upload Audio File
          </button>
          <button className="btn-reset" onClick={resetUI}>
             <RotateCcw size={14}/> Reset
          </button>
        </div>

        <div className="sidebar-section">
          <h5>STATUS</h5>
          <div className="status-indicator">
             <span className={`dot ${currentStep !== 'Idle' ? 'active' : ''}`}></span>
             {currentStep !== 'Idle' ? currentStep : 'Standing By'}
          </div>
        </div>

        <div className="sidebar-section scrollable">
          <h5>PAST SESSIONS</h5>
          <ul className="sessions-list">
            {pastSessions.map(sess => (
              <li key={sess._id} className={activeSessionId === sess._id ? 'active' : ''} onClick={() => loadPastSession(sess)} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                 <div style={{ flex: 1, overflow: 'hidden' }}>
                    <span className="sess-title" style={{ display: 'block', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>{sess.name}</span>
                    <span className="sess-meta">{new Date(sess.date).toLocaleDateString()} &bull; {sess.duration_minutes || 0} min</span>
                 </div>
                 <button className="btn-delete-session" onClick={(e) => deleteSession(e, sess._id)} title="Delete session">
                   <Trash2 size={16} />
                 </button>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="sidebar-bottom">
           <button className="btn-logout" onClick={logout}>Log Out</button>
        </div>
      </aside>

      {/* Primary Presentation View */}
      <main className="main-content">
        
        {/* Process Lifecycle Indicator */}
        <header className="stepper-header">
           <div className="stepper">
              {STEPS.map((step, idx) => {
                 const status = getStepStatus(step);
                 return (
                   <React.Fragment key={step}>
                     <div className={`step ${status}`}>
                       {status === 'completed' ? <CheckCircle2 size={24} className="icon-done" /> : 
                        status === 'active' ? <div className="icon-active"><Circle size={10} fill="currentColor"/></div> :
                        <div className="icon-pending">{idx+1}</div>}
                       <span className="step-label">{step}</span>
                     </div>
                     {idx < STEPS.length - 1 && <div className={`line ${status === 'completed' ? 'done' : ''}`} />}
                   </React.Fragment>
                 )
              })}
           </div>
        </header>

        {/* Session Metadata Input Interface */}
        {showSaveBar && (
          <div className="save-bar">
             <p>Session processing complete. Save to history?</p>
             <div className="save-inputs">
               <input value={sessionName} onChange={e=>setSessionName(e.target.value)} placeholder="Enter meeting name..." autoFocus/>
               <button className="btn-delete" onClick={() => setShowSaveBar(false)}>Don't Save</button>
               <button onClick={saveSessionToDb}>Save Session</button>
             </div>
          </div>
        )}

        {/* Multi-Dimensional Analytics Grid */}
        <div className="panels-grid">
           
           {/* Transcription Stream Component */}
           <div className="card transcript-card">
              <div className="card-header">
                 <h3>Live Transcript</h3>
                 <span>{transcriptTurns.length > 0 ? `${transcriptTurns.length} turns` : 'Listening...'}</span>
              </div>
              <div className="card-body" ref={liveTranscriptRef}>
                 {transcriptTurns.length > 0 ? (
                    transcriptTurns.map((turn, idx) => (
                      <div className="message" key={idx}>
                         <div className="avatar" style={{backgroundColor: getAvatarColor(turn.speaker)}}>{turn.speaker.charAt(0)}</div>
                         <div className="msg-content">
                            <div className="msg-meta">
                               <span className="spk-name" style={{color: getAvatarColor(turn.speaker)}}>{turn.speaker}</span>
                               <span className="spk-time">{turn.time}</span>
                            </div>
                            <div className="msg-text">{turn.text}</div>
                         </div>
                      </div>
                    ))
                 ) : (
                    <div className="live-preview">{liveTranscript || 'Start recording right away...'}</div>
                 )}
              </div>
           </div>

           {/* Diarization Distribution Component */}
           <div className="card analytics-card">
              <div className="card-header">
                 <h3>Speaker Analytics</h3>
                 <span>{analytics.length} participants</span>
              </div>
              <div className="card-body">
                 {analytics.length > 0 ? (
                   <>
                     {/* Activity Distribution Chart */}
                     <div className="chart-container">
                        <div className="css-donut" style={{background: buildConicGradient(analytics)}}>
                          <div className="donut-hole"></div>
                        </div>
                     </div>
                     
                     <div className="speakers-list">
                        {analytics.map((spk, idx) => (
                          <div className="spk-row" key={idx}>
                             <div className="spk-row-head">
                                <div className="spk-label">
                                   <span className="dot" style={{backgroundColor: getAvatarColor(spk.speaker)}}></span>
                                   {spk.speaker}
                                </div>
                                <span className="turns">{spk.turns} turns</span>
                             </div>
                             <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <div className="progress-bar" style={{ flex: 1 }}>
                                   <div className="fill" style={{width: `${spk.percent}%`, backgroundColor: getAvatarColor(spk.speaker)}}></div>
                                </div>
                                <span className="percent-label">{spk.percent}%</span>
                             </div>
                          </div>
                        ))}
                     </div>
                   </>
                 ) : (
                   <div style={{color:'#94a3b8', textAlign:'center', marginTop:'2rem'}}>No analytics available until diarization.</div>
                 )}
              </div>
           </div>

           {/* AI Telemetry and Artifact Extraction */}
           <div className="card summary-card">
              <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                 <div>
                   <h3>Summary & Actions</h3>
                   <span>AI-generated insights</span>
                 </div>
                 {summaryData && (
                   <div style={{ display: 'flex', gap: '8px' }}>
                     <button onClick={exportMD} title="Download Markdown" style={{ display:'flex', alignItems:'center', gap:'4px', padding:'4px 8px', background:'transparent', border:'1px solid #cbd5e1', borderRadius:'4px', cursor:'pointer' }}>
                       <FileText size={14} /> MD
                     </button>
                     <button onClick={exportPDF} title="Download PDF" style={{ display:'flex', alignItems:'center', gap:'4px', padding:'4px 8px', background:'transparent', border:'1px solid #cbd5e1', borderRadius:'4px', cursor:'pointer' }}>
                       <Download size={14} /> PDF
                     </button>
                   </div>
                 )}
              </div>
              <div className="card-body">
                 {summaryData ? (
                   <div className="insights-view">
                      <h4 className="insight-title"><Lightbulb size={16}/> SUMMARY</h4>
                      <p className="summary-text">{summaryData.summary}</p>
                      
                      <h4 className="insight-title mt-4"><CheckSquare size={16}/> ACTION ITEMS</h4>
                      <ol className="action-items">
                         {summaryData.action_items?.map((item, i) => (
                           <li key={i}>{item}</li>
                         ))}
                      </ol>

                      <h4 className="insight-title mt-4"><CheckCircle2 size={16} color="#10b981"/> KEY DECISIONS</h4>
                      <ul className="decisions">
                         {summaryData.decisions?.map((item, i) => (
                           <li key={i}>{item}</li>
                         ))}
                      </ul>
                   </div>
                 ) : (
                   <div style={{color:'#94a3b8', textAlign:'center', marginTop:'2rem'}}>Insights are prepared in the summarization phase.</div>
                 )}
              </div>
           </div>

        </div>
      </main>

      {/* Critical Action Confirmation Dialog */}
      {sessionToDelete && (
        <div className="modal-overlay">
          <div className="modal-content">
             <h3>Delete Session</h3>
             <p>Are you sure you want to permanently delete this session? This action cannot be undone.</p>
             <div className="modal-actions">
               <button onClick={() => setSessionToDelete(null)} className="btn-cancel">Cancel</button>
               <button onClick={confirmDeleteSession} className="btn-delete">Delete</button>
             </div>
          </div>
        </div>
      )}
    </div>
  );
}

// UI Rendering Utilities
function getAvatarColor(speakerName) {
   let hash = 0;
   for (let i = 0; i < speakerName.length; i++) {
     hash = speakerName.charCodeAt(i) + ((hash << 5) - hash);
   }
   const hue = Math.abs(hash * 137.5) % 360;
   return `hsl(${hue}, 75%, 50%)`;
}

function buildConicGradient(analytics) {
  let gradientStr = [];
  let currentAngle = 0;
  analytics.forEach(spk => {
     let angle = (spk.percent / 100) * 360;
     let color = getAvatarColor(spk.speaker);
     gradientStr.push(`${color} ${currentAngle}deg ${currentAngle + angle}deg`);
     currentAngle += angle;
  });
  return `conic-gradient(${gradientStr.join(', ')})`;
}
