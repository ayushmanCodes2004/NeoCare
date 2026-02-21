import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import axios from 'axios';
import '../styles/auth.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

/**
 * Doctor Login page — calls POST /api/auth/doctor/login
 * Styled to match NeoSure landing page theme
 */
export default function DoctorLoginPage() {
  const navigate = useNavigate();
  const [apiError, setApiError] = useState(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    setApiError(null);
    setLoading(true);
    
    console.log('Attempting doctor login with email:', data.email);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/doctor/login`, {
        phone: data.email, // Send email in phone field for doctor login
        password: data.password,
      });
      
      console.log('Login response:', response.data);
      
      // Store token first
      const token = response.data.token;
      localStorage.setItem('token', token);
      localStorage.setItem('userRole', 'DOCTOR');
      localStorage.setItem('doctorId', response.data.workerId);
      
      // Fetch full doctor profile to get specialization
      try {
        const profileResponse = await axios.get(`${API_BASE_URL}/api/auth/doctor/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        console.log('Profile response:', profileResponse.data);
        
        localStorage.setItem('doctorInfo', JSON.stringify({
          fullName: profileResponse.data.fullName,
          email: profileResponse.data.email,
          phone: profileResponse.data.phone,
          specialization: profileResponse.data.specialization,
          hospital: profileResponse.data.hospital,
          district: profileResponse.data.district
        }));
      } catch (profileErr) {
        console.error('Profile fetch error:', profileErr);
        // Fallback if profile fetch fails
        localStorage.setItem('doctorInfo', JSON.stringify({
          fullName: response.data.fullName,
          email: response.data.email,
          phone: response.data.phone,
          hospital: response.data.healthCenter,
          district: response.data.district
        }));
      }
      console.log('Login successful! Redirecting to doctor dashboard...');
      console.log('Stored data:', {
        token: !!token,
        userRole: localStorage.getItem('userRole'),
        doctorId: localStorage.getItem('doctorId'),
        doctorInfo: localStorage.getItem('doctorInfo')
      });
      
      // Force navigation to doctor dashboard
      window.location.href = '/doctor/dashboard';
    } catch (err) {
      console.error('Login error:', err);
      console.error('Error response:', err.response?.data);
      
      let errorMessage = 'Login failed. Please check your credentials.';
      
      if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.response?.status === 401) {
        errorMessage = 'Invalid email or password';
      } else if (err.response?.status === 403) {
        errorMessage = 'Access denied. Please check your credentials.';
      } else if (err.message === 'Network Error') {
        errorMessage = 'Cannot connect to server. Please ensure backend is running on port 8080.';
      }
      
      setApiError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-dots-tl"></div>
      <div className="auth-dots-br"></div>

      <Link to="/" className="auth-back-link">
        ← Back to Home
      </Link>

      <div className="auth-card">
        {/* Header */}
        <div className="auth-header">
          <div className="auth-logo">
            <div className="auth-logo-mark">🌸</div>
            <span className="auth-logo-text">NeoSure</span>
          </div>
          <h1 className="auth-title">Doctor Portal</h1>
          <p className="auth-subtitle">Sign in to access consultations</p>
        </div>

        {/* Error Alert */}
        {apiError && (
          <div className="auth-alert error">
            <span className="auth-alert-icon">⚠️</span>
            <span>{apiError}</span>
            <button 
              className="auth-alert-close" 
              onClick={() => setApiError(null)}
              aria-label="Close"
            >
              ×
            </button>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="auth-form">
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              placeholder="doctor@hospital.com"
              className={`form-input ${errors.email ? 'error' : ''}`}
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                  message: 'Enter a valid email address',
                },
              })}
            />
            {errors.email && (
              <span className="form-error">
                ⚠ {errors.email.message}
              </span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              placeholder="••••••••"
              className={`form-input ${errors.password ? 'error' : ''}`}
              {...register('password', {
                required: 'Password is required',
              })}
            />
            {errors.password && (
              <span className="form-error">
                ⚠ {errors.password.message}
              </span>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`auth-submit-btn ${loading ? 'loading' : ''}`}
          >
            {!loading && 'Sign In'}
          </button>
        </form>

        {/* Footer */}
        <div className="auth-footer">
          Don't have an account?{' '}
          <Link to="/doctor/signup">Register as Doctor</Link>
        </div>
      </div>
    </div>
  );
}
