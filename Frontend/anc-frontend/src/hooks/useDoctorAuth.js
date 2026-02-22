import { useContext } from 'react';
import { DoctorAuthContext } from '../context/DoctorAuthContext';

export const useDoctorAuth = () => useContext(DoctorAuthContext);
