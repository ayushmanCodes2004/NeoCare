import RiskBadge from '../ui/RiskBadge';
import ConfidenceBar from './ConfidenceBar';
import { AlertTriangle, Stethoscope, Brain, ClipboardList } from 'lucide-react';

export default function RiskReport({ risk }) {
  if (!risk) return null;
  
  const bannerColor = {
    CRITICAL: 'from-risk-critical/20 to-transparent border-risk-critical/40',
    HIGH: 'from-risk-high/20 to-transparent border-risk-high/40',
    MEDIUM: 'from-risk-medium/20 to-transparent border-risk-medium/40',
    LOW: 'from-risk-low/20 to-transparent border-risk-low/40',
  }[risk.riskLevel] || 'from-white/5 to-transparent border-white/10';

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Risk level banner */}
      <div className={`p-5 rounded-2xl border bg-gradient-to-br ${bannerColor}`}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            {risk.isHighRisk && <AlertTriangle size={22} className="text-risk-critical" />}
            <span className="font-display text-xl font-bold text-slate-100">Risk Assessment</span>
          </div>
          <RiskBadge level={risk.riskLevel} large />
        </div>
        <ConfidenceBar value={risk.confidence} />
      </div>

      {/* Detected risks */}
      {risk.detectedRisks?.length > 0 && (
        <div className="glass-card p-5">
          <div className="flex items-center gap-2 section-label mb-3">
            <AlertTriangle size={14} /> Detected Risk Factors ({risk.detectedRisks.length})
          </div>
          <div className="flex flex-wrap gap-2">
            {risk.detectedRisks.map((r, i) => (
              <span 
                key={i} 
                className="text-xs px-3 py-1 rounded-full bg-risk-critical/10 text-risk-critical border border-risk-critical/20 font-medium"
              >
                {r}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Explanation */}
      {risk.explanation && (
        <div className="glass-card p-5">
          <div className="flex items-center gap-2 section-label mb-2">
            <Brain size={14} /> AI Analysis
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">{risk.explanation}</p>
        </div>
      )}

      {/* Recommendation */}
      {risk.recommendation && (
        <div className="glass-card p-5">
          <div className="flex items-center gap-2 section-label mb-2">
            <ClipboardList size={14} /> Recommended Action
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">{risk.recommendation}</p>
        </div>
      )}
    </div>
  );
}
