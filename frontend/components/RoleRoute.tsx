import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

interface Props {
  allowedRoles: string[];
  children: React.ReactElement;
}

export const RoleRoute: React.FC<Props> = ({ allowedRoles, children }) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <div className="min-h-screen bg-cyber-dark flex items-center justify-center text-cyber-primary">Loading Sentry Core...</div>;
  if (!isAuthenticated || !user) return <Navigate to="/login" replace />;
  const hasRole = user.roles?.some((r) => allowedRoles.includes(r));
  if (!hasRole) return <Navigate to="/app" replace />;

  return children;
};

export default RoleRoute;
