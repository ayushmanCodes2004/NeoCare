import { createContext, useState, useEffect, useCallback } from 'react';
import { login as apiLogin, signup as apiSignup } from '../api/authApi';

/**
 * AuthContext — global authentication state.
 *
 * Provides:
 *   user, token, isLoading, userRole, login(), signup(), logout()
 *   Supports both ANC workers and doctors
 */

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [userRole, setUserRole] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Restore session from localStorage on app load
  useEffect(() => {
    // Check for new format (doctor/worker)
    const storedToken = localStorage.getItem('token');
    const storedRole = localStorage.getItem('userRole');
    
    if (storedToken && storedRole) {
      setToken(storedToken);
      setUserRole(storedRole);
      
      if (storedRole === 'DOCTOR') {
        const doctorInfo = localStorage.getItem('doctorInfo');
        if (doctorInfo) {
          try {
            setUser(JSON.parse(doctorInfo));
          } catch {
            localStorage.clear();
          }
        }
      } else {
        // Try old format for workers
        const storedWorker = localStorage.getItem('anc_worker');
        if (storedWorker) {
          try {
            setUser(JSON.parse(storedWorker));
          } catch {
            localStorage.clear();
          }
        }
      }
    } else {
      // Fallback to old format
      const oldToken = localStorage.getItem('anc_token');
      const oldWorker = localStorage.getItem('anc_worker');
      
      if (oldToken && oldWorker) {
        try {
          setToken(oldToken);
          setUser(JSON.parse(oldWorker));
          setUserRole('WORKER');
        } catch {
          localStorage.clear();
        }
      }
    }
    
    setIsLoading(false);
  }, []);

  // Persist auth data to localStorage
  const persistAuth = (authResponse) => {
    const { token, ...userInfo } = authResponse;
    localStorage.setItem('token', token);
    localStorage.setItem('anc_token', token); // Keep old format for compatibility
    localStorage.setItem('anc_worker', JSON.stringify(userInfo));
    localStorage.setItem('userRole', 'WORKER');
    setToken(token);
    setUser(userInfo);
    setUserRole('WORKER');
  };

  // Login
  const login = useCallback(async (phone, password) => {
    const authResponse = await apiLogin({ phone, password });
    persistAuth(authResponse);
    return authResponse;
  }, []);

  // Signup
  const signup = useCallback(async (formData) => {
    const authResponse = await apiSignup(formData);
    persistAuth(authResponse);
    return authResponse;
  }, []);

  // Logout
  const logout = useCallback(() => {
    localStorage.clear();
    setToken(null);
    setUser(null);
    setUserRole(null);
    window.location.href = '/';
  }, []);

  const value = {
    worker: user, // Keep 'worker' for backward compatibility
    user,
    token,
    userRole,
    isLoading,
    isAuthenticated: !!token,
    login,
    signup,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
