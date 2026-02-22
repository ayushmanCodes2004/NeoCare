import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  [key: string]: any;
}

interface AuthContextType {
  token: string | null;
  role: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, role: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('anc_token'));
  const [role, setRole] = useState<string | null>(localStorage.getItem('anc_role'));
  const [user, setUser] = useState<User | null>(() => {
    const u = localStorage.getItem('anc_user');
    return u ? JSON.parse(u) : null;
  });

  const login = (token: string, role: string, user: User) => {
    localStorage.setItem('anc_token', token);
    localStorage.setItem('anc_role', role);
    localStorage.setItem('anc_user', JSON.stringify(user));
    setToken(token);
    setRole(role);
    setUser(user);
  };

  const logout = () => {
    localStorage.clear();
    setToken(null);
    setRole(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, role, user, isAuthenticated: !!token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
