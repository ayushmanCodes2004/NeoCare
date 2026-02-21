import Badge from '../ui/Badge';

/**
 * Big alert banner shown at the top of the VisitResultPage.
 */
export default function RiskBanner({ isHighRisk, riskLevel, recommendation }) {
  const bgStyles = {
    CRITICAL: 'bg-red-600 text-white',
    HIGH:     'bg-orange-500 text-white',
    MEDIUM:   'bg-yellow-400 text-gray-900',
    LOW:      'bg-green-500 text-white',
  };

  const bg = bgStyles[riskLevel] || 'bg-gray-400 text-white';

  return (
    <div className={`rounded-xl p-5 mb-6 ${bg}`}>
      <div className="flex items-center gap-3 mb-2">
        {isHighRisk && (
          <span className="text-2xl">🚨</span>
        )}
        <h2 className="text-xl font-bold">
          Risk Level: {riskLevel}
        </h2>
        <Badge riskLevel={riskLevel} className="ml-auto" />
      </div>
      {recommendation && (
        <p className="text-sm font-medium mt-1 opacity-90">{recommendation}</p>
      )}
    </div>
  );
}
