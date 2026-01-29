// src/routes/ProtectedRoute.tsx
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

const ProtectedRoute = () => {
  const { isAuthenticated, loading } = useAuth();

  // While checking session (/auth/me, refresh, etc.)
  if (loading) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        Initializing session…
      </div>
    );
  }

  // Not logged in → send to login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Auth OK → render child routes
  return <Outlet />;
};

export default ProtectedRoute;
