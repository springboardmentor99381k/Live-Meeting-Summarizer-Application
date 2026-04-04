import { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import Dashboard from './Dashboard';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('userId'));

  return (
    <Routes>
      {/* If not logged in, show Login on "/", otherwise redirect to "/dashboard" */}
      <Route 
        path="/" 
        element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login setAuth={setIsAuthenticated} />} 
      />
      
      {/* If logged in, show Dashboard on "/dashboard", otherwise redirect to "/" */}
      <Route 
        path="/dashboard" 
        element={isAuthenticated ? <Dashboard logout={() => { localStorage.removeItem('userId'); setIsAuthenticated(false); }} /> : <Navigate to="/" />} 
      />

      {/* Catch-all unmatched routes and redirect to home */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;
