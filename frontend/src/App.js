import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Import auth pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import VerifyEmailPage from './pages/VerifyEmailPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';

// Import public pages
import PublicTicketFormPage from './pages/PublicTicketFormPage';
import PublicTicketViewPage from './pages/PublicTicketViewPage';

// Import components
import ProtectedRoute from './components/ProtectedRoute';

// Import pages (will be created later)
// import DashboardPage from './pages/DashboardPage';
// import BoardPage from './pages/BoardPage';

function App() {
  return (
    <div className="App">
      <Container>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />

          {/* Public board routes */}
          <Route path="/board/:uniqueName" element={<PublicTicketFormPage />} />
          <Route path="/ticket/:uuid" element={<PublicTicketViewPage />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <div><h1>Dashboard</h1><p>Coming soon...</p></div>
              </ProtectedRoute>
            }
          />

          {/* Protected manager routes (will be created later) */}
          {/* <Route
            path="/boards/:id"
            element={
              <ProtectedRoute>
                <BoardPage />
              </ProtectedRoute>
            }
          /> */}

          {/* 404 */}
          <Route path="*" element={<div><h1>404</h1><p>Page not found</p></div>} />
        </Routes>
      </Container>
    </div>
  );
}

export default App;
