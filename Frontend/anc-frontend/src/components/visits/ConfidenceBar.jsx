export default function ConfidenceBar({ value }) {
  const pct = Math.round((value || 0) * 100);
  const color = pct >= 70 ? 'bg-teal-500' : pct >= 50 ? 'bg-risk-medium' : 'bg-risk-high';
  
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span className="font-mono uppercase tracking-wider">AI Confidence</span>
        <span className="font-mono font-semibold text-slate-200">{pct}%</span>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <div 
          className={`h-full rounded-full transition-all duration-1000 ${color}`}
          style={{ width: `${pct}%` }} 
        />
      </div>
    </div>
  );
}
