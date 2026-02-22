import { cn } from '@/lib/utils';

const riskStyles: Record<string, string> = {
  LOW: 'bg-risk-low text-primary-foreground',
  MEDIUM: 'bg-risk-medium text-warning-foreground',
  HIGH: 'bg-risk-high text-primary-foreground',
  CRITICAL: 'bg-risk-critical text-primary-foreground',
};

const RiskBadge = ({ level, className }: { level: string; className?: string }) => (
  <span className={cn('inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-semibold uppercase tracking-wide', riskStyles[level] || 'bg-muted text-muted-foreground', className)}>
    {level}
  </span>
);

export default RiskBadge;
