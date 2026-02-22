import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { registerVisit } from '../../api/visitApi';
import StepWizard from '../../components/visits/StepWizard';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { AlertCircle, ChevronLeft, ChevronRight, Zap } from 'lucide-react';

const STEPS = ['Patient Info', 'Vitals', 'Lab Reports', 'Medical History', 'Obstetric History', 'Pregnancy', 'Symptoms'];

function CheckRow({ label, name, register }) {
  return (
    <label className="flex items-center gap-3 p-3 rounded-xl border border-white/10 hover:border-teal-500/30 hover:bg-teal-500/5 cursor-pointer transition-all group">
      <input type="checkbox" className="h-4 w-4 rounded border-slate-600 bg-navy-800 text-teal-500 focus:ring-teal-500/30"
        {...register(name)} />
      <span className="text-sm text-slate-300 group-hover:text-slate-100">{label}</span>
    </label>
  );
}

export default function VisitFormPage() {
  const { patientId } = useParams();
  const navigate      = useNavigate();
  const [step, setStep]       = useState(0);
  const [saved, setSaved]     = useState({});
  const [err,   setErr]       = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  const saveAndNext = (data) => {
    setSaved(prev => ({ ...prev, ...data }));
    if (step < 6) { setStep(s => s + 1); reset(); }
  };

  const submitAll = async (data) => {
    setErr(''); setSubmitting(true);
    const all = { ...saved, ...data };

    const payload = {
      patientId,
      structured_data: {
        patient_info:      { age: Number(all.age) || null, gestationalWeeks: Number(all.gestationalWeeks) || null },
        vitals:            { heightCm: Number(all.heightCm)||null, bmi: Number(all.bmi)||null, bpSystolic: Number(all.bpSystolic)||null, bpDiastolic: Number(all.bpDiastolic)||null },
        lab_reports:       { hemoglobin: Number(all.hemoglobin)||null, rhNegative: !!all.rhNegative, hivPositive: !!all.hivPositive, syphilisPositive: !!all.syphilisPositive, urineProtein: !!all.urineProtein, urineSugar: !!all.urineSugar },
        medical_history:   { previousLSCS: !!all.previousLSCS, badObstetricHistory: !!all.badObstetricHistory, previousStillbirth: !!all.previousStillbirth, previousPretermDelivery: !!all.previousPretermDelivery, previousAbortion: !!all.previousAbortion, chronicHypertension: !!all.chronicHypertension, diabetes: !!all.diabetes, thyroidDisorder: !!all.thyroidDisorder, smoking: !!all.smoking, tobaccoUse: !!all.tobaccoUse, alcoholUse: !!all.alcoholUse, systemicIllness: all.systemicIllness || 'None' },
        obstetric_history: { birthOrder: Number(all.birthOrder)||null, interPregnancyInterval: Number(all.interPregnancyInterval)||null, stillbirthCount: Number(all.stillbirthCount)||0, abortionCount: Number(all.abortionCount)||0, pretermHistory: !!all.pretermHistory },
        pregnancy_details: { twinPregnancy: !!all.twinPregnancy, malpresentation: !!all.malpresentation, placentaPrevia: !!all.placentaPrevia, reducedFetalMovement: !!all.reducedFetalMovement, amnioticFluidNormal: all.amnioticFluidNormal !== false, umbilicalDopplerAbnormal: !!all.umbilicalDopplerAbnormal },
        current_symptoms:  { headache: !!all.headache, visualDisturbance: !!all.visualDisturbance, epigastricPain: !!all.epigastricPain, decreasedUrineOutput: !!all.decreasedUrineOutput, bleedingPerVagina: !!all.bleedingPerVagina, convulsions: !!all.convulsions },
      }
    };

    try {
      const result = await registerVisit(payload);
      navigate(`/visits/${result.visitId}`, { state: result });
    } catch (e) {
      setErr(e.response?.data?.message || 'Failed to submit. Please try again.');
    } finally { setSubmitting(false); }
  };

  const onSubmit = step < 6 ? saveAndNext : submitAll;

  return (
    <div className="p-8 max-w-2xl animate-fade-in">
      <div className="mb-6">
        <p className="section-label">ANC Visit</p>
        <h1 className="font-display text-2xl font-bold text-slate-100">Register Visit</h1>
        <p className="text-xs text-slate-500 font-mono mt-0.5">Patient: {patientId?.slice(0,8)}...</p>
      </div>

      <StepWizard steps={STEPS} current={step} />

      {err && (
        <div className="flex items-center gap-2 mb-4 p-3 rounded-xl bg-risk-critical/10 border border-risk-critical/30 text-risk-critical text-sm">
          <AlertCircle size={16} /> {err}
        </div>
      )}

      <div className="glass-card p-6">
        <form onSubmit={handleSubmit(onSubmit)} noValidate>

          {/* Step 0: Patient Info */}
          {step === 0 && (
            <div>
              <p className="section-label mb-4">Patient Information</p>
              <div className="grid grid-cols-2 gap-x-4">
                <Input label="Age (years) *" type="number" placeholder="28"
                  error={errors.age?.message}
                  {...register('age', { required: 'Age is required', min: { value: 15, message: 'Min 15' }, max: { value: 55, message: 'Max 55' } })} />
                <Input label="Gestational Weeks *" type="number" placeholder="28"
                  error={errors.gestationalWeeks?.message}
                  {...register('gestationalWeeks', { required: 'Required', min: { value: 1, message: 'Min 1' }, max: { value: 42, message: 'Max 42' } })} />
              </div>
            </div>
          )}

          {/* Step 1: Vitals */}
          {step === 1 && (
            <div>
              <p className="section-label mb-4">Vitals</p>
              <div className="grid grid-cols-2 gap-x-4">
                <Input label="Height (cm)" type="number" placeholder="155" {...register('heightCm')} />
                <Input label="BMI" type="number" placeholder="24.5" step="0.1" {...register('bmi')} />
                <Input label="BP Systolic (mmHg)" type="number" placeholder="120" {...register('bpSystolic')} />
                <Input label="BP Diastolic (mmHg)" type="number" placeholder="80"  {...register('bpDiastolic')} />
              </div>
            </div>
          )}

          {/* Step 2: Lab Reports */}
          {step === 2 && (
            <div>
              <p className="section-label mb-4">Lab Reports</p>
              <Input label="Hemoglobin (g/dL)" type="number" placeholder="11.5" step="0.1" {...register('hemoglobin')} />
              <p className="text-xs text-slate-500 mb-3">Mark all that apply:</p>
              <div className="grid grid-cols-1 gap-2">
                <CheckRow label="Rh Negative"       name="rhNegative"       register={register} />
                <CheckRow label="HIV Positive"       name="hivPositive"      register={register} />
                <CheckRow label="Syphilis Positive"  name="syphilisPositive" register={register} />
                <CheckRow label="Urine Protein +"    name="urineProtein"     register={register} />
                <CheckRow label="Urine Sugar +"      name="urineSugar"       register={register} />
              </div>
            </div>
          )}

          {/* Step 3: Medical History */}
          {step === 3 && (
            <div>
              <p className="section-label mb-4">Medical History</p>
              <div className="grid grid-cols-1 gap-2 mb-4">
                <CheckRow label="Previous LSCS (C-Section)"       name="previousLSCS"           register={register} />
                <CheckRow label="Bad Obstetric History"            name="badObstetricHistory"     register={register} />
                <CheckRow label="Previous Stillbirth"              name="previousStillbirth"      register={register} />
                <CheckRow label="Previous Preterm Delivery"        name="previousPretermDelivery" register={register} />
                <CheckRow label="Previous Abortion"                name="previousAbortion"        register={register} />
                <CheckRow label="Chronic Hypertension"             name="chronicHypertension"     register={register} />
                <CheckRow label="Diabetes"                         name="diabetes"                register={register} />
                <CheckRow label="Thyroid Disorder"                 name="thyroidDisorder"         register={register} />
                <CheckRow label="Smoking"                          name="smoking"                 register={register} />
                <CheckRow label="Tobacco Use"                      name="tobaccoUse"              register={register} />
                <CheckRow label="Alcohol Use"                      name="alcoholUse"              register={register} />
              </div>
              <Input label="Systemic Illness (if any)" placeholder="e.g. Heart disease, or None" {...register('systemicIllness')} />
            </div>
          )}

          {/* Step 4: Obstetric History */}
          {step === 4 && (
            <div>
              <p className="section-label mb-4">Obstetric History</p>
              <div className="grid grid-cols-2 gap-x-4">
                <Input label="Birth Order (Gravida)" type="number" placeholder="2"  {...register('birthOrder')} />
                <Input label="Inter-Pregnancy Interval (months)" type="number" placeholder="24" {...register('interPregnancyInterval')} />
                <Input label="Stillbirth Count" type="number" placeholder="0" {...register('stillbirthCount')} />
                <Input label="Abortion Count"   type="number" placeholder="0" {...register('abortionCount')} />
              </div>
              <CheckRow label="Preterm History" name="pretermHistory" register={register} />
            </div>
          )}

          {/* Step 5: Pregnancy Details */}
          {step === 5 && (
            <div>
              <p className="section-label mb-4">Current Pregnancy Details</p>
              <div className="grid grid-cols-1 gap-2">
                <CheckRow label="Twin / Multiple Pregnancy"       name="twinPregnancy"           register={register} />
                <CheckRow label="Malpresentation"                 name="malpresentation"         register={register} />
                <CheckRow label="Placenta Previa"                 name="placentaPrevia"          register={register} />
                <CheckRow label="Reduced Fetal Movements"         name="reducedFetalMovement"    register={register} />
                <CheckRow label="Abnormal Umbilical Doppler"      name="umbilicalDopplerAbnormal" register={register} />
                <label className="flex items-center gap-3 p-3 rounded-xl border border-white/10 hover:border-teal-500/30 cursor-pointer transition-all group">
                  <input type="checkbox" defaultChecked
                    className="h-4 w-4 rounded border-slate-600 bg-navy-800 text-teal-500"
                    {...register('amnioticFluidNormal')} />
                  <span className="text-sm text-slate-300">Amniotic Fluid Normal</span>
                </label>
              </div>
            </div>
          )}

          {/* Step 6: Symptoms */}
          {step === 6 && (
            <div>
              <p className="section-label mb-1">Current Symptoms</p>
              <p className="text-xs text-slate-500 mb-4">Mark all symptoms the patient is currently experiencing</p>
              <div className="grid grid-cols-1 gap-2">
                <CheckRow label="🤕 Headache"                name="headache"             register={register} />
                <CheckRow label="👁 Visual Disturbance"     name="visualDisturbance"    register={register} />
                <CheckRow label="🫁 Epigastric Pain"        name="epigastricPain"       register={register} />
                <CheckRow label="💧 Decreased Urine Output" name="decreasedUrineOutput" register={register} />
                <CheckRow label="🩸 Bleeding Per Vagina"    name="bleedingPerVagina"    register={register} />
                <CheckRow label="⚡ Convulsions"            name="convulsions"           register={register} />
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-white/10">
            {step > 0 ? (
              <Button variant="secondary" onClick={() => { setStep(s => s - 1); reset(); }}>
                <ChevronLeft size={16} /> Back
              </Button>
            ) : (
              <Button variant="ghost" onClick={() => navigate(-1)}>Cancel</Button>
            )}
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 font-mono">{step + 1} / {STEPS.length}</span>
              <Button type="submit" loading={submitting && step === 6}>
                {step < 6 ? (<>Next <ChevronRight size={16} /></>) : (<><Zap size={16} /> Analyze Risk</>)}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
