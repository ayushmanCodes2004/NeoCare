import { forwardRef } from 'react';
import { clsx } from 'clsx';

const Input = forwardRef(({ label, error, hint, className, type = 'text', ...rest }, ref) => (
  <div className="mb-4">
    {label && (
      <label className="block text-xs font-mono uppercase tracking-wider text-slate-400 mb-1.5">
        {label}
      </label>
    )}
    {type === 'textarea' ? (
      <textarea
        ref={ref}
        rows={3}
        className={clsx(
          'w-full px-4 py-2.5 rounded-xl bg-navy-800 border text-slate-100 text-sm',
          'placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-teal-500/50 resize-none',
          error ? 'border-risk-critical/60' : 'border-white/10 focus:border-teal-500/50',
          className
        )}
        {...rest}
      />
    ) : (
      <input
        ref={ref}
        type={type}
        className={clsx(
          'w-full px-4 py-2.5 rounded-xl bg-navy-800 border text-slate-100 text-sm',
          'placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-teal-500/50',
          error ? 'border-risk-critical/60' : 'border-white/10 focus:border-teal-500/50',
          className
        )}
        {...rest}
      />
    )}
    {error && <p className="mt-1 text-xs text-risk-critical">{error}</p>}
    {hint && !error && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
  </div>
));

Input.displayName = 'Input';
export default Input;
