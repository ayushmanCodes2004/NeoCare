/**
 * Renders the detectedRisks[] array from FastAPI response.
 */
export default function DetectedRisksList({ risks = [] }) {
  if (!risks.length) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
      <h3 className="font-semibold text-gray-800 mb-3">
        Detected Risk Factors ({risks.length})
      </h3>
      <ul className="space-y-2">
        {risks.map((risk, i) => (
          <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
            <span className="h-2 w-2 rounded-full bg-red-500 flex-shrink-0" />
            {risk}
          </li>
        ))}
      </ul>
    </div>
  );
}
