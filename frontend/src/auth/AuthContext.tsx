import React, {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import { authApi } from "../../services/authService";

/* =======================
   Types
======================= */

export type User = {
  id: string;
  email: string;
  roles: string[];
  scopes: string[];
};

type AuthContextType = {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  isLoading: boolean; // alias to satisfy older components
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
  hasRole: (role: string) => boolean;
  hasScope: (scope: string) => boolean;
};

/* =======================
   Context
======================= */

export const AuthContext = createContext<AuthContextType | null>(null);

/* =======================
   Provider
======================= */

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const isAuthenticated = !!user;

  /* =======================
     Helpers
  ======================= */

  const hasRole = useCallback(
    (role: string) => user?.roles.includes(role) ?? false,
    [user]
  );

  const hasScope = useCallback(
    (scope: string) => user?.scopes.includes(scope) ?? false,
    [user]
  );

  /* =======================
     API Calls
  ======================= */

  const login = async (email: string, password: string): Promise<boolean> => {
    setLoading(true);
    try {
      const { user, access_token } = await authApi.login(email, password);
      authApi.setAccessToken(access_token);
      setUser(user);
      return true;
    } catch (err) {
      console.error("login failed", err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await authApi.logout();
    } finally {
      authApi.clearAccessToken();
      setUser(null);
      setLoading(false);
    }
  };

  const refresh = async () => {
    try {
      const token = await authApi.refresh();
      authApi.setAccessToken(token);
      // Optionally fetch user to resync
      const me = await authApi.me();
      setUser(me);
    } catch {
      authApi.clearAccessToken();
      setUser(null);
    }
  };

  /* =======================
     Session Restore
  ======================= */

  useEffect(() => {
    const restoreSession = async () => {
      try {
        const me = await authApi.me();
        setUser(me);
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    restoreSession();
  }, []);

  /* =======================
     Axios Interceptor
  ======================= */

  const value = useMemo(
    () => ({
      user,
      isAuthenticated,
      loading,
      isLoading: loading,
      login,
      logout,
      refresh,
      hasRole,
      hasScope,
    }),
    [user, isAuthenticated, loading, hasRole, hasScope]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
