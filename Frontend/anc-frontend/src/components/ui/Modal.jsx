import { X } from 'lucide-react';
import { useEffect } from 'react';

export default function Modal({ open, onClose, title, children, wide }) {
  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  if (!open) return null;
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />
      <div className={`relative glass-card p-6 w-full animate-slide-up ${wide ? 'max-w-2xl' : 'max-w-lg'}`}>
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-display text-lg font-semibold text-slate-100">{title}</h3>
          <button 
            onClick={onClose} 
            className="p-1 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-white/10"
          >
            <X size={18} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
