import { useNavigate } from 'react-router-dom';

/**
 * Card shown in the patient list.
 */
export default function PatientCard({ patientId, fullName, phone, age, village, district, lmpDate }) {
  const navigate = useNavigate();

  return (
    <div
      className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md hover:border-blue-300 cursor-pointer transition-all"
      onClick={() => navigate(`/patients/${patientId}`)}
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-gray-900">{fullName}</h3>
          <p className="text-sm text-gray-500 mt-0.5">
            {phone} {age ? `• Age ${age}` : ''} {village ? `• ${village}` : ''}
          </p>
          {district && <p className="text-xs text-gray-400">{district}</p>}
        </div>
        <div className="text-right text-xs text-gray-400">
          {lmpDate && (
            <p>LMP: {new Date(lmpDate).toLocaleDateString('en-IN')}</p>
          )}
          <span className="text-blue-500 font-medium">View →</span>
        </div>
      </div>
    </div>
  );
}
