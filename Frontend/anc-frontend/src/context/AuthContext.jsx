import { createContext, useState, useEffect, useCallback } from 'react';
import { workerLogin, workerSignup } from '../api/authApi';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('anc_token');
    const stored = localStorage.getItem('anc_user');
    const role = localStorage.getItem('anc_role');
    
    if (token && stored && role === 'WORKER') {
      try {
        setUser(JSON.parse(stored));
      } catch {
        localStorage.clear();
      }
    }
    setReady(true);
  }, []);

  const persist = (data) => {
    const { token, ...info } = data;
    localStorage.setItem('anc_token', token);
    localStorage.setItem('anc_user', JSON.stringify(info));
    localStorage.setItem('anc_role', 'WORKER');
    setUser(info);
  };

  const login = useCallback(async (phone, password) => {
    const result = await workerLogin({ phone, password });
    persist(result);
    return result;
  }, []);

  const signup = useCallback(async (data) => {
    const result = await workerSignup(data);
    persist(result);
    return result;
  }, []);

  const logout = useCallback(() => {
    localStorage.clear();
    setUser(null);
    window.location.href = '/login';
  }, []);

  return (
    <AuthContext.Provider value={{ user, ready, isAuth: !!user, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
