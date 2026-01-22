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

// Import protected pages
import DashboardPage from './pages/DashboardPage';
import BoardListPage from './pages/BoardListPage';
import BoardDetailPage from './pages/BoardDetailPage';
import BoardFormPage from './pages/BoardFormPage';
import TicketListPage from './pages/TicketListPage';
import TicketDetailPage from './pages/TicketDetailPage';
import StandbyQueuePage from './pages/StandbyQueuePage';
import StandbyQueueItemPage from './pages/StandbyQueueItemPage';
import ProfileSettingsPage from './pages/ProfileSettingsPage';
import SecuritySettingsPage from './pages/SecuritySettingsPage';
import InboxListPage from './pages/InboxListPage';
import InboxFormPage from './pages/InboxFormPage';

// Import components
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/common/ErrorBoundary';
import { ToastProvider } from './contexts/ToastContext';

function App() {
  return (
    <ErrorBoundary level="app">
      <ToastProvider>
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
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          {/* Board routes */}
          <Route
            path="/boards"
            element={
              <ProtectedRoute>
                <BoardListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/boards/new"
            element={
              <ProtectedRoute>
                <BoardFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/boards/:id"
            element={
              <ProtectedRoute>
                <BoardDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/boards/:id/edit"
            element={
              <ProtectedRoute>
                <BoardFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/boards/:boardId/tickets/:ticketId"
            element={
              <ProtectedRoute>
                <TicketDetailPage />
              </ProtectedRoute>
            }
          />

          {/* Ticket routes */}
          <Route
            path="/tickets"
            element={
              <ProtectedRoute>
                <TicketListPage />
              </ProtectedRoute>
            }
          />

          {/* Standby queue routes */}
          <Route
            path="/standby-queue"
            element={
              <ProtectedRoute>
                <StandbyQueuePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/standby-queue/:id"
            element={
              <ProtectedRoute>
                <StandbyQueueItemPage />
              </ProtectedRoute>
            }
          />

          {/* Settings routes */}
          <Route
            path="/settings/profile"
            element={
              <ProtectedRoute>
                <ProfileSettingsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/security"
            element={
              <ProtectedRoute>
                <SecuritySettingsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/inboxes"
            element={
              <ProtectedRoute>
                <InboxListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/inboxes/new"
            element={
              <ProtectedRoute>
                <InboxFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/inboxes/:inboxId/edit"
            element={
              <ProtectedRoute>
                <InboxFormPage />
              </ProtectedRoute>
            }
          />

          {/* 404 */}
          <Route path="*" element={<div><h1>404</h1><p>Page not found</p></div>} />
        </Routes>
      </Container>
    </div>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
