import { HashRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";

import ProtectedRoute from "./routes/ProtectedRoute";
import RoleRoute from "./routes/RoleRoute";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import AdminPanel from "./pages/AdminPanel";

function App() {
  return (
    <AuthProvider>
      <HashRouter>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<Login />} />

          {/* Protected */}
          <Route element={<ProtectedRoute />}>
            <Route path="/app" element={<Dashboard />} />

            {/* Admin only */}
            <Route
              element={
                <RoleRoute
                  allowedRoles={["admin"]}
                  redirectTo="/app"
                />
              }
            >
              <Route path="/admin" element={<AdminPanel />} />
            </Route>
          </Route>

          {/* Default */}
          <Route path="*" element={<Navigate to="/app" replace />} />
        </Routes>
      </HashRouter>
    </AuthProvider>
  );
}

export default App;
