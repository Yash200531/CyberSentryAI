import React from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import RoleRoute from './components/RoleRoute';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ScanPage from './pages/ScanPage';
import HistoryPage from './pages/HistoryPage';
import ReportPage from './pages/ReportPage';
import ProfilePage from './pages/ProfilePage';
import AboutPage from './pages/AboutPage';
import InfoPage from './pages/InfoPage';
import FraudRecoveryPage from './pages/FraudRecoveryPage';

const App: React.FC = () => {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        
        {/* Protected Routes */}
        <Route path="/app" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Navigate to="/app/scan" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="scan" element={<ScanPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="report/:id" element={<ReportPage />} />
          <Route path="recovery" element={<FraudRecoveryPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="about" element={<AboutPage />} />
          <Route path="info" element={<InfoPage />} />
          <Route path="admin" element={<RoleRoute allowedRoles={["admin"]}><DashboardPage /></RoleRoute>} />
        </Route>
      </Routes>
    </HashRouter>
  );
};

export default App;