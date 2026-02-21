import axiosInstance from './axiosInstance';

/**
 * Patient API — matches PatientController.java endpoints
 */

export const createPatient = async (data) => {
  const response = await axiosInstance.post('/api/patients', data);
  return response.data;
};

export const getMyPatients = async () => {
  const response = await axiosInstance.get('/api/patients');
  return response.data;
};

export const getPatientById = async (patientId) => {
  const response = await axiosInstance.get(`/api/patients/${patientId}`);
  return response.data;
};
