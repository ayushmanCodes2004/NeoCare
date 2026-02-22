import { clsx } from 'clsx';

const config = {
  CRITICAL: { cls: 'risk-critical', dot: 'bg-risk-critical animate-pulse', label: 'CRITICAL' },
  HIGH: { cls: 'risk-high', dot: 'bg-risk-high', label: 'HIGH' },
  MEDIUM: { cls: 'risk-medium', dot: 'bg-risk-medium', label: 'MEDIUM' },
  LOW: { cls: 'risk-low', dot: 'bg-risk-low', label: 'LOW' },
};

export default function RiskBadge({ level, large }) {
  const cfg = config[level] || { 
    cls: 'text-slate-400 bg-white/10 border-white/20', 
    dot: 'bg-slate-500', 
    label: level || '—' 
  };
  
  return (
    <span className={clsx(
      'inline-flex items-center gap-1.5 rounded-full border font-mono font-semibold uppercase tracking-wide',
      large ? 'px-4 py-1.5 text-sm' : 'px-2.5 py-0.5 text-xs',
      cfg.cls
    )}>
      <span className={clsx('rounded-full', large ? 'h-2.5 w-2.5' : 'h-1.5 w-1.5', cfg.dot)} />
      {cfg.label}
    </span>
  );
}
