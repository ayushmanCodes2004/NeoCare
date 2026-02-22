import { CheckCircle } from 'lucide-react';
import { clsx } from 'clsx';

export default function StepWizard({ steps, current }) {
  return (
    <div className="flex items-center gap-0 mb-8">
      {steps.map((label, i) => {
        const done = i < current;
        const active = i === current;
        
        return (
          <div key={i} className="flex items-center flex-1 last:flex-none">
            <div className="flex flex-col items-center">
              <div className={clsx(
                'h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all duration-300',
                done 
                  ? 'bg-teal-500 border-teal-500 text-navy-950'
                  : active 
                    ? 'bg-transparent border-teal-400 text-teal-400 shadow-lg shadow-teal-500/30'
                    : 'bg-transparent border-white/20 text-slate-500'
              )}>
                {done ? <CheckCircle size={14} /> : i + 1}
              </div>
              <span className={clsx(
                'text-xs mt-1.5 text-center font-medium whitespace-nowrap',
                active ? 'text-teal-400' : done ? 'text-slate-400' : 'text-slate-600'
              )}>
                {label}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div className={clsx(
                'flex-1 h-0.5 mx-2 mb-5 transition-colors duration-300',
                done ? 'bg-teal-500' : 'bg-white/10'
              )} />
            )}
          </div>
        );
      })}
    </div>
  );
}
