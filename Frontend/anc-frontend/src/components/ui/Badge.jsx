/**
 * Risk level badge — maps riskLevel to colour.
 */
export default function Badge({ riskLevel, className = '' }) {
  const styles = {
    CRITICAL: 'bg-red-100 text-red-800 border-red-300',
    HIGH:     'bg-orange-100 text-orange-800 border-orange-300',
    MEDIUM:   'bg-yellow-100 text-yellow-800 border-yellow-300',
    LOW:      'bg-green-100 text-green-800 border-green-300',
  };

  const style = styles[riskLevel] || 'bg-gray-100 text-gray-600 border-gray-300';

  return (
    <span className={`inline-block px-2.5 py-0.5 text-xs font-semibold rounded-full border ${style} ${className}`}>
      {riskLevel || 'UNKNOWN'}
    </span>
  );
}
