import axiosInstance from './axiosInstance';

/**
 * ANC Visit API — matches AncVisitController.java endpoints
 */

export const registerVisit = async (data) => {
  const response = await axiosInstance.post('/api/anc/register-visit', data);
  return response.data;
};

export const getPatientVisits = async (patientId) => {
  const response = await axiosInstance.get(`/api/anc/patients/${patientId}/visits`);
  return response.data;
};

export const getVisitById = async (visitId) => {
  const response = await axiosInstance.get(`/api/anc/visits/${visitId}`);
  return response.data;
};

export const getHighRiskVisits = async () => {
  const response = await axiosInstance.get('/api/anc/visits/high-risk');
  return response.data;
};

export const getCriticalVisits = async () => {
  const response = await axiosInstance.get('/api/anc/visits/critical');
  return response.data;
};
