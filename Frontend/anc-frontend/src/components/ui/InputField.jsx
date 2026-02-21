/**
 * Reusable form input — works with react-hook-form register().
 */
import { forwardRef } from 'react';

const InputField = forwardRef(function InputField(
  { label, error, type = 'text', className = '', ...props },
  ref
) {
  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <input
        ref={ref}
        type={type}
        className={`w-full px-3 py-2 border rounded-lg text-sm shadow-sm
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
          ${error ? 'border-red-400 bg-red-50' : 'border-gray-300 bg-white'}
          ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
    </div>
  );
});

export default InputField;
