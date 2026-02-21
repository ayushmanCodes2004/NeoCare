/**
 * Simple Input component for search and forms
 */
import { forwardRef } from 'react';

const Input = forwardRef(function Input(
  { className = '', ...props },
  ref
) {
  return (
    <input
      ref={ref}
      className={`w-full px-4 py-3 border border-gray-200 rounded-lg text-sm 
        focus:outline-none focus:ring-2 focus:ring-terra focus:border-transparent
        transition-all ${className}`}
      {...props}
    />
  );
});

export default Input;
