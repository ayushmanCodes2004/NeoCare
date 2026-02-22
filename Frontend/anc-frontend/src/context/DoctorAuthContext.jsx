import { createContext, useState, useEffect, useCallback } from 'react';
import { doctorLogin, doctorSignup } from '../api/doctorApi';

export const DoctorAuthContext = createContext(null);

export function DoctorAuthProvider({ children }) {
  const [doctor, setDoctor] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('anc_token');
    const stored = localStorage.getItem('anc_user');
    const role = localStorage.getItem('anc_role');
    
    if (token && stored && role === 'DOCTOR') {
      try {
        setDoctor(JSON.parse(stored));
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
    localStorage.setItem('anc_role', 'DOCTOR');
    setDoctor(info);
  };

  const login = useCallback(async (phone, password) => {
    const result = await doctorLogin({ phone, password });
    persist(result);
    return result;
  }, []);

  const signup = useCallback(async (data) => {
    const result = await doctorSignup(data);
    persist(result);
    return result;
  }, []);

  const logout = useCallback(() => {
    localStorage.clear();
    setDoctor(null);
    window.location.href = '/doctor/login';
  }, []);

  return (
    <DoctorAuthContext.Provider value={{ doctor, ready, isAuth: !!doctor, login, signup, logout }}>
      {children}
    </DoctorAuthContext.Provider>
  );
}
