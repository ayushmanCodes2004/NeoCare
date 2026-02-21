import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import InputField from '../components/ui/InputField';
import Button from '../components/ui/Button';
import ErrorAlert from '../components/ui/ErrorAlert';

/**
 * Login page — calls POST /api/auth/login
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-lg w-full max-w-md p-8">

        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-4xl mb-3">🏥</div>
          <h1 className="text-2xl font-bold text-gray-900">ANC Portal</h1>
          <p className="text-gray-500 text-sm mt-1">Maternal Health Risk Assessment</p>
        </div>

        <ErrorAlert message={apiError} onDismiss={() => setApiError(null)} />

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <InputField
            label="Phone Number"
            type="tel"
            placeholder="9876543210"
            error={errors.phone?.message}
            {...register('phone', {
              required: 'Phone number is required',
              pattern: {
                value: /^[6-9]\d{9}$/,
                message: 'Enter a valid 10-digit mobile number',
              },
            })}
          />

          <InputField
            label="Password"
            type="password"
            placeholder="••••••••"
            error={errors.password?.message}
            {...register('password', {
              required: 'Password is required',
            })}
          />

          <Button
            type="submit"
            loading={loading}
            className="w-full mt-2"
          >
            Login
          </Button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600">
          Don't have an account?{' '}
          <Link to="/signup" className="text-blue-600 hover:text-blue-700 font-medium">
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
}
