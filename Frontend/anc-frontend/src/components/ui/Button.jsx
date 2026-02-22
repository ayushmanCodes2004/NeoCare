import { clsx } from 'clsx';
import Spinner from './Spinner';

const variants = {
  primary: 'bg-teal-500 hover:bg-teal-400 text-navy-950 font-semibold shadow-lg shadow-teal-500/20',
  secondary: 'bg-white/10 hover:bg-white/15 text-slate-200 border border-white/20',
  danger: 'bg-risk-critical/20 hover:bg-risk-critical/30 text-risk-critical border border-risk-critical/30',
  ghost: 'text-slate-400 hover:text-slate-200 hover:bg-white/5',
  outline: 'border border-teal-500/50 text-teal-400 hover:bg-teal-500/10',
};

export default function Button({
  children,
  variant = 'primary',
  loading,
  disabled,
  className,
  type = 'button',
  size = 'md',
  ...rest
}) {
  const sizeClass = size === 'sm' ? 'px-3 py-1.5 text-xs' : size === 'lg' ? 'px-6 py-3 text-base' : 'px-4 py-2 text-sm';
  
  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={clsx(
        'inline-flex items-center justify-center gap-2 rounded-xl transition-all duration-200',
        'disabled:opacity-40 disabled:cursor-not-allowed',
        variants[variant],
        sizeClass,
        className
      )}
      {...rest}
    >
      {loading && <Spinner />}
      {children}
    </button>
  );
}
