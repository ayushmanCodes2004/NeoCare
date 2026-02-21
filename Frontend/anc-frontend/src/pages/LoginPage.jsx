import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import '../styles/auth.css';

/**
 * Login page — calls POST /api/auth/login
 * Styled to match NeoSure landing page theme
 */
export default function LoginPage() {
  const { login } = useAuth();
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
      await login(data.phone, data.password);
      navigate('/dashboard');
    } catch (err) {
      setApiError(
        err.response?.data?.message || 'Login failed. Please check your credentials.'
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

      <div className="auth-card">
        {/* Header */}
        <div className="auth-header">
          <div className="auth-logo">
            <div className="auth-logo-mark">🌸</div>
            <span className="auth-logo-text">NeoSure</span>
          </div>
          <h1 className="auth-title">Welcome Back</h1>
          <p className="auth-subtitle">Sign in to continue helping mothers</p>
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
          <Link to="/signup">Create one now</Link>
        </div>
      </div>
    </div>
  );
}
