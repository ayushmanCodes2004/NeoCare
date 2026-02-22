import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import '../styles/auth.css';

/**
 * Signup page — calls POST /api/auth/signup
 * Styled to match NeoSure landing page theme
 */
export default function SignupPage() {
  const { signup } = useAuth();
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
    try {
      await signup(data);
      navigate('/dashboard');
    } catch (err) {
      setApiError(
        err.response?.data?.message || 'Signup failed. Please try again.'
      );
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

      <div className="auth-card wide">
        {/* Header */}
        <div className="auth-header">
          <div className="auth-logo">
            <div className="auth-logo-mark">🌸</div>
            <span className="auth-logo-text">NeoSure</span>
          </div>
          <h1 className="auth-title">Join NeoSure</h1>
          <p className="auth-subtitle">Register as an ANC Health Worker</p>
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
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="auth-form grid">
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              placeholder="Anjali Devi"
              className={`form-input ${errors.fullName ? 'error' : ''}`}
              {...register('fullName', {
                required: 'Full name is required',
              })}
            />
            {errors.fullName && (
              <span className="form-error">
                ⚠ {errors.fullName.message}
              </span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Phone Number</label>
            <input
              type="tel"
              placeholder="9876543210"
              className={`form-input ${errors.phone ? 'error' : ''}`}
              {...register('phone', {
                required: 'Phone number is required',
                pattern: {
                  value: /^[6-9]\d{9}$/,
                  message: 'Enter a valid 10-digit mobile number',
                },
              })}
            />
            {errors.phone && (
              <span className="form-error">
                ⚠ {errors.phone.message}
              </span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              placeholder="anjali@phc.in"
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
                minLength: {
                  value: 8,
                  message: 'Password must be at least 8 characters',
                },
              })}
            />
            {errors.password && (
              <span className="form-error">
                ⚠ {errors.password.message}
              </span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Health Center</label>
            <input
              type="text"
              placeholder="PHC Angondhalli"
              className={`form-input ${errors.healthCenter ? 'error' : ''}`}
              {...register('healthCenter', {
                required: 'Health center is required',
              })}
            />
            {errors.healthCenter && (
              <span className="form-error">
                ⚠ {errors.healthCenter.message}
              </span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">District</label>
            <input
              type="text"
              placeholder="Bangalore Rural"
              className={`form-input ${errors.district ? 'error' : ''}`}
              {...register('district', {
                required: 'District is required',
              })}
            />
            {errors.district && (
              <span className="form-error">
                ⚠ {errors.district.message}
              </span>
            )}
          </div>

          <div className="form-group full-width">
            <button
              type="submit"
              disabled={loading}
              className={`auth-submit-btn ${loading ? 'loading' : ''}`}
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </div>
        </form>

        {/* Footer */}
        <div className="auth-footer">
          Already have an account?{' '}
          <Link to="/login">Sign in here</Link>
        </div>
      </div>
    </div>
  );
}
