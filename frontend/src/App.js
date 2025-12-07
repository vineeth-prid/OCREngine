import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import FormBuilder from './pages/FormBuilder';
import Documents from './pages/Documents';
import AdminPanel from './pages/AdminPanel';
import { authAPI, userAPI } from './services/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [userRoles, setUserRoles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      Promise.all([
        authAPI.getCurrentUser(),
        userAPI.getRoles(JSON.parse(localStorage.getItem('user') || '{}').id || 1)
      ])
        .then(([userResponse, rolesResponse]) => {
          setUser(userResponse.data);
          setUserRoles(rolesResponse.data || []);
          setIsAuthenticated(true);
        })
        .catch((err) => {
          console.error('Auth error:', err);
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogin = (token, userData) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App min-h-screen bg-gray-50">
        <Routes>
          <Route path="/login" element={
            !isAuthenticated ? <Login onLogin={handleLogin} /> : <Navigate to="/dashboard" />
          } />
          <Route path="/register" element={
            !isAuthenticated ? <Register onLogin={handleLogin} /> : <Navigate to="/dashboard" />
          } />
          <Route path="/dashboard" element={
            isAuthenticated ? <Dashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" />
          } />
          <Route path="/schemas" element={
            isAuthenticated ? <Schemas user={user} onLogout={handleLogout} /> : <Navigate to="/login" />
          } />
          <Route path="/documents" element={
            isAuthenticated ? <Documents user={user} onLogout={handleLogout} /> : <Navigate to="/login" />
          } />
          <Route path="/admin" element={
            isAuthenticated ? <AdminPanel user={user} onLogout={handleLogout} /> : <Navigate to="/login" />
          } />
          <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
