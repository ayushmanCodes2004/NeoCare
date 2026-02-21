import axiosInstance from './axiosInstance';

/**
 * Auth API — matches AuthController.java endpoints
 */

export const signup = async (data) => {
  const response = await axiosInstance.post('/api/auth/signup', data);
  return response.data;
};

export const login = async (data) => {
  const response = await axiosInstance.post('/api/auth/login', data);
  return response.data;
};

export const getMe = async () => {
  const response = await axiosInstance.get('/api/auth/me');
  return response.data;
};
