import { useEffect } from 'react';
import { CheckCircle, XCircle, X } from 'lucide-react';

export default function Toast({ message, type = 'success', onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-slide-up">
      <div className={`flex items-center gap-3 px-4 py-3 rounded-2xl border shadow-2xl backdrop-blur ${
        type === 'success' 
          ? 'bg-teal-500/20 border-teal-500/40 text-teal-200'
          : 'bg-risk-critical/20 border-risk-critical/40 text-red-200'
      }`}>
        {type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
        <span className="text-sm font-medium">{message}</span>
        <button onClick={onClose} className="ml-2 opacity-60 hover:opacity-100">
          <X size={14} />
        </button>
      </div>
    </div>
  );
}
