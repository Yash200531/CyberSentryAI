import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AnalysisResult, AppState } from '../types';

interface StoreContextProps extends AppState {
  login: (username: string, email: string) => void;
  logout: () => void;
  toggleTheme: () => void;
  addHistoryItem: (item: AnalysisResult) => void;
  clearHistory: () => void;
  updateUser: (updates: Partial<User>) => void;
}

const StoreContext = createContext<StoreContextProps | undefined>(undefined);

export const StoreProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Theme State
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  
  // User State
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('cyberSentry_user');
    return stored ? JSON.parse(stored) : null;
  });

  // History State
  const [history, setHistory] = useState<AnalysisResult[]>(() => {
    const stored = localStorage.getItem('cyberSentry_history');
    return stored ? JSON.parse(stored) : [];
  });

  // Effects
  useEffect(() => {
    const root = window.document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  useEffect(() => {
    localStorage.setItem('cyberSentry_history', JSON.stringify(history));
  }, [history]);

  useEffect(() => {
    if (user) {
      localStorage.setItem('cyberSentry_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('cyberSentry_user');
    }
  }, [user]);

  // Actions
  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  const login = (username: string, email: string) => {
    const newUser: User = {
      id: crypto.randomUUID(),
      username,
      email,
      joinedDate: new Date().toISOString(),
      avatarUrl: `https://api.dicebear.com/7.x/avataaars/svg?seed=${username}`
    };
    setUser(newUser);
  };

  const logout = () => {
    setUser(null);
  };

  const updateUser = (updates: Partial<User>) => {
    if (!user) return;
    setUser(prev => prev ? { ...prev, ...updates } : null);
  };

  const addHistoryItem = (item: AnalysisResult) => {
    setHistory(prev => [item, ...prev]);
  };

  const clearHistory = () => {
    setHistory([]);
  };

  return (
    <StoreContext.Provider value={{
      user,
      history,
      theme,
      login,
      logout,
      toggleTheme,
      addHistoryItem,
      clearHistory,
      updateUser
    }}>
      {children}
    </StoreContext.Provider>
  );
};

export const useStore = () => {
  const context = useContext(StoreContext);
  if (context === undefined) {
    throw new Error('useStore must be used within a StoreProvider');
  }
  return context;
};