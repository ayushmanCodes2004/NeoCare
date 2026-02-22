export default function StatCard({ label, value, sub, icon: Icon, accent = 'teal' }) {
  const colors = {
    teal: 'text-teal-400 bg-teal-400/10 border-teal-400/20',
    critical: 'text-risk-critical bg-risk-critical/10 border-risk-critical/20',
    high: 'text-risk-high bg-risk-high/10 border-risk-high/20',
    low: 'text-risk-low bg-risk-low/10 border-risk-low/20',
    slate: 'text-slate-300 bg-white/5 border-white/10',
  };
  
  return (
    <div className="glass-card p-5 flex items-start gap-4 animate-fade-in">
      {Icon && (
        <div className={`p-2.5 rounded-xl border ${colors[accent]}`}>
          <Icon size={20} className={colors[accent].split(' ')[0]} />
        </div>
      )}
      <div>
        <p className="section-label">{label}</p>
        <p className="text-3xl font-display font-bold text-slate-100">{value ?? '—'}</p>
        {sub && <p className="text-xs text-slate-500 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}
