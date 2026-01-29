// src/routes/RoleRoute.tsx
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

type RoleRouteProps = {
  allowedRoles: string[];
  redirectTo?: string;
};

const RoleRoute = ({
  allowedRoles,
  redirectTo = "/app",
}: RoleRouteProps) => {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        Checking permissions…
      </div>
    );
  }

  // Not logged in → login
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  const hasAccess = user.roles.some((role) =>
    allowedRoles.includes(role)
  );

  // Logged in but forbidden
  if (!hasAccess) {
    return <Navigate to={redirectTo} replace />;
  }

  return <Outlet />;
};

export default RoleRoute;
