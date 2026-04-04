import React, { useState } from 'react';
import { Mic } from 'lucide-react';
import './Login.css';

export default function Login({ setAuth }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleAuth = async (e) => {
    e.preventDefault();
    const endpoint = isRegister ? '/api/register' : '/api/login';
    try {
      const res = await fetch(`https://aashikaarun123-live-meeting-summarizer.hf.space${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        localStorage.setItem('userId', data.user_id);
        setAuth(true);
      }
    } catch {
      setError("Server connection failed. Make sure FastAPI and MongoDB are running.");
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
           <div className="app-logo">
             <div className="logo-icon"><Mic size={24} color="#fff"/></div>
             <div className="logo-text">
               <b>MeetingAI</b><br/><span>Summarizer</span>
             </div>
           </div>
           <h2 style={{marginTop: '2rem'}}>{isRegister ? 'Create Account' : 'Welcome Back'}</h2>
        </div>
        <form onSubmit={handleAuth} className="login-form">
           {error && <div className="error-box">{error}</div>}
           <div className="input-group">
             <label>Username</label>
             <input type="text" value={username} onChange={e => setUsername(e.target.value)} required />
           </div>
           <div className="input-group">
             <label>Password</label>
             <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
           </div>
           <button type="submit" className="btn-primary" style={{marginTop:'10px'}}>{isRegister ? 'Sign Up' : 'Log In'}</button>
        </form>
        <p className="toggle-auth">
          {isRegister ? 'Already have an account? ' : "Don't have an account? "}
          <span onClick={() => setIsRegister(!isRegister)}>{isRegister ? 'Log In' : 'Sign Up'}</span>
        </p>
      </div>
    </div>
  );
}
