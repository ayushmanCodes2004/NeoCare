/**
 * Step progress bar for the ANC visit form.
 */
export default function VisitStepIndicator({ currentStep, steps }) {
  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-2">
        {steps.map((label, i) => {
          const step = i + 1;
          const done    = step < currentStep;
          const active  = step === currentStep;
          return (
            <div key={i} className="flex flex-col items-center flex-1 relative">
              <div className={`h-8 w-8 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-colors z-10
                ${done   ? 'bg-blue-600 border-blue-600 text-white'
                : active ? 'border-blue-600 text-blue-600 bg-white'
                :          'border-gray-300 text-gray-400 bg-white'}`}>
                {done ? '✓' : step}
              </div>
              <span className={`text-xs mt-1 text-center hidden sm:block
                ${active ? 'text-blue-600 font-medium' : 'text-gray-400'}`}>
                {label}
              </span>
              {i < steps.length - 1 && (
                <div className={`absolute h-0.5 w-full top-4 left-1/2 -z-0
                  ${done ? 'bg-blue-600' : 'bg-gray-200'}`} />
              )}
            </div>
          );
        })}
      </div>
      <div className="w-full bg-gray-200 rounded-full h-1.5">
        <div
          className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
          style={{ width: `${((currentStep - 1) / (steps.length - 1)) * 100}%` }}
        />
      </div>
      <p className="text-sm text-gray-500 mt-1">
        Step {currentStep} of {steps.length}: <span className="font-medium text-gray-700">{steps[currentStep - 1]}</span>
      </p>
    </div>
  );
}
