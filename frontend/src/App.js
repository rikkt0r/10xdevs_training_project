import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Import pages (will be created later)
// import HomePage from './pages/HomePage';
// import LoginPage from './pages/LoginPage';
// import RegisterPage from './pages/RegisterPage';
// import DashboardPage from './pages/DashboardPage';
// import BoardPage from './pages/BoardPage';
// import PublicTicketFormPage from './pages/PublicTicketFormPage';
// import PublicTicketViewPage from './pages/PublicTicketViewPage';

function App() {
  return (
    <div className="App">
      <Container>
        <Routes>
          <Route path="/" element={<div><h1>Simple Issue Tracker</h1><p>Coming soon...</p></div>} />
          {/* <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/boards/:id" element={<BoardPage />} />
          <Route path="/board/:uniqueName" element={<PublicTicketFormPage />} />
          <Route path="/ticket/:uuid" element={<PublicTicketViewPage />} /> */}
        </Routes>
      </Container>
    </div>
  );
}

export default App;
