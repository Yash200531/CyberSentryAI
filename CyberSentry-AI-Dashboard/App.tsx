import React from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { StoreProvider, useStore } from './contexts/StoreContext';
import { Layout } from './components/Layout';
import { Auth } from './pages/Auth';
import { Scanner } from './pages/Scanner';
import { HistoryPage } from './pages/History';
import { Profile } from './pages/Profile';

const AppRoutes = () => {
  const { user } = useStore();

  if (!user) {
    return <Auth />;
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Scanner />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
};

const App: React.FC = () => {
  return (
    <StoreProvider>
      <HashRouter>
        <AppRoutes />
      </HashRouter>
    </StoreProvider>
  );
};

export default App;