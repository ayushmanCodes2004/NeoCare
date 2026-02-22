import { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { registerVisit } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/AppLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, ChevronRight, ChevronLeft } from 'lucide-react';

const steps = ['Patient Info', 'Vitals', 'Symptoms', 'Obstetric History', 'Medical History', 'Pregnancy', 'Lab Reports'];

const VisitForm = () => {
  const [params] = useSearchParams();
  const patientId = params.get('patientId') || '';
  const { user } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [form, setForm] = useState({
    patientName: '', age: '', gestationalAge: '', gravida: '', para: '', abortions: '', livingChildren: '',
    bpSystolic: '', bpDiastolic: '', pulse: '', temp: '', weight: '', height: '', respRate: '',
    complaints: '', severity: 'mild', duration: '',
    prevPregnancies: '', prevDeliveries: '', prevComplications: '', lastDeliveryMode: '',
    chronicConditions: '', allergies: '', medications: '', pastSurgeries: '',
    lmpDate: '', eddDate: '', currentGA: '', complications: '',
    hemoglobin: '', bloodGroup: '', bloodSugar: '', urineProtein: '', hivStatus: '', hbsagStatus: '',
  });

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => setForm(p => ({ ...p, [k]: e.target.value }));

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    const w = parseFloat(form.weight) || 0;
    const h = parseFloat(form.height) || 0;
    const bmi = h > 0 ? parseFloat((w / ((h / 100) ** 2)).toFixed(1)) : 0;

    const body = {
      patientId,
      patientName: form.patientName,
      workerId: user?.workerId,
      phcId: 'PHC-001',
      structured_data: {
        patient_info: {
          patientId: patientId,
          name: form.patientName,
          age: parseInt(form.age) || 0,
          gravida: parseInt(form.gravida) || 0,
          para: parseInt(form.para) || 0,
          livingChildren: parseInt(form.livingChildren) || 0,
          gestationalWeeks: parseInt(form.gestationalAge) || 0,
          lmpDate: form.lmpDate,
          estimatedDueDate: form.eddDate
        },
        vitals: {
          weightKg: w,
          heightCm: h,
          bmi: bmi,
          bpSystolic: parseInt(form.bpSystolic) || 0,
          bpDiastolic: parseInt(form.bpDiastolic) || 0,
          pulseRate: parseInt(form.pulse) || 0,
          respiratoryRate: parseInt(form.respRate) || 0,
          temperatureCelsius: parseFloat(form.temp) || 0,
          pallor: false,
          pedalEdema: false
        },
        medical_history: {
          previousLSCS: false,
          badObstetricHistory: false,
          previousStillbirth: false,
          previousPretermDelivery: false,
          previousAbortion: parseInt(form.abortions) > 0,
          systemicIllness: form.chronicConditions || "None",
          chronicHypertension: false,
          diabetes: false,
          thyroidDisorder: false,
          smoking: false,
          tobaccoUse: false,
          alcoholUse: false
        },
        lab_reports: {
          hemoglobin: parseFloat(form.hemoglobin) || 0,
          plateletCount: null,
          bloodGroup: form.bloodGroup,
          rhNegative: false,
          urineProtein: form.urineProtein === 'Positive',
          urineSugar: false,
          fastingBloodSugar: parseFloat(form.bloodSugar) || null,
          ogtt2hrPG: null,
          hivPositive: form.hivStatus === 'Positive',
          syphilisPositive: false,
          serumCreatinine: null,
          ast: null,
          alt: null
        },
        obstetric_history: {
          birthOrder: null,
          interPregnancyInterval: null,
          stillbirthCount: 0,
          abortionCount: parseInt(form.abortions) || 0,
          pretermHistory: false
        },
        pregnancy_details: {
          twinPregnancy: false,
          malpresentation: false,
          placentaPrevia: false,
          reducedFetalMovement: false,
          amnioticFluidNormal: true,
          umbilicalDopplerAbnormal: false
        },
        current_symptoms: {
          headache: form.complaints.toLowerCase().includes('headache'),
          visualDisturbance: false,
          epigastricPain: false,
          decreasedUrineOutput: false,
          bleedingPerVagina: false,
          convulsions: false
        }
      },
    };

    try {
      const { data } = await registerVisit(body);
      navigate(`/worker/visits/${data.visitId}/result`);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to register visit');
    } finally { setLoading(false); }
  };

  const renderStep = () => {
    const inputCls = "space-y-2";
    switch (step) {
      case 0: return (
        <div className="grid sm:grid-cols-2 gap-4">
          <div className={inputCls}><Label>Patient Name</Label><Input value={form.patientName} onChange={set('patientName')} required /></div>
          <div className={inputCls}><Label>Age</Label><Input type="number" value={form.age} onChange={set('age')} /></div>
          <div className={inputCls}><Label>Gestational Age (weeks)</Label><Input type="number" value={form.gestationalAge} onChange={set('gestationalAge')} /></div>
          <div className={inputCls}><Label>Gravida</Label><Input type="number" value={form.gravida} onChange={set('gravida')} /></div>
          <div className={inputCls}><Label>Para</Label><Input type="number" value={form.para} onChange={set('para')} /></div>
          <div className={inputCls}><Label>Abortions</Label><Input type="number" value={form.abortions} onChange={set('abortions')} /></div>
          <div className={inputCls}><Label>Living Children</Label><Input type="number" value={form.livingChildren} onChange={set('livingChildren')} /></div>
        </div>
      );
      case 1: return (
        <div className="grid sm:grid-cols-2 gap-4">
          <div className={inputCls}><Label>BP Systolic</Label><Input type="number" value={form.bpSystolic} onChange={set('bpSystolic')} /></div>
          <div className={inputCls}><Label>BP Diastolic</Label><Input type="number" value={form.bpDiastolic} onChange={set('bpDiastolic')} /></div>
          <div className={inputCls}><Label>Pulse Rate</Label><Input type="number" value={form.pulse} onChange={set('pulse')} /></div>
          <div className={inputCls}><Label>Temperature (°F)</Label><Input type="number" step="0.1" value={form.temp} onChange={set('temp')} /></div>
          <div className={inputCls}><Label>Weight (kg)</Label><Input type="number" step="0.1" value={form.weight} onChange={set('weight')} /></div>
          <div className={inputCls}><Label>Height (cm)</Label><Input type="number" value={form.height} onChange={set('height')} /></div>
          <div className={inputCls}><Label>Respiratory Rate</Label><Input type="number" value={form.respRate} onChange={set('respRate')} /></div>
        </div>
      );
      case 2: return (
        <div className="space-y-4">
          <div className={inputCls}><Label>Complaints (comma separated)</Label><Textarea value={form.complaints} onChange={set('complaints')} placeholder="Mild headache, Fatigue" /></div>
          <div className={inputCls}>
            <Label>Severity</Label>
            <Select value={form.severity} onValueChange={v => setForm(p => ({ ...p, severity: v }))}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="mild">Mild</SelectItem>
                <SelectItem value="moderate">Moderate</SelectItem>
                <SelectItem value="severe">Severe</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className={inputCls}><Label>Duration (days)</Label><Input type="number" value={form.duration} onChange={set('duration')} /></div>
        </div>
      );
      case 3: return (
        <div className="grid sm:grid-cols-2 gap-4">
          <div className={inputCls}><Label>Previous Pregnancies</Label><Input type="number" value={form.prevPregnancies} onChange={set('prevPregnancies')} /></div>
          <div className={inputCls}><Label>Previous Deliveries</Label><Input type="number" value={form.prevDeliveries} onChange={set('prevDeliveries')} /></div>
          <div className={inputCls}><Label>Previous Complications</Label><Input value={form.prevComplications} onChange={set('prevComplications')} placeholder="None" /></div>
          <div className={inputCls}><Label>Last Delivery Mode</Label><Input value={form.lastDeliveryMode} onChange={set('lastDeliveryMode')} placeholder="Normal vaginal delivery" /></div>
        </div>
      );
      case 4: return (
        <div className="space-y-4">
          <div className={inputCls}><Label>Chronic Conditions (comma separated)</Label><Textarea value={form.chronicConditions} onChange={set('chronicConditions')} placeholder="None" /></div>
          <div className={inputCls}><Label>Allergies</Label><Input value={form.allergies} onChange={set('allergies')} placeholder="None" /></div>
          <div className={inputCls}><Label>Current Medications</Label><Textarea value={form.medications} onChange={set('medications')} placeholder="Folic acid, Iron supplements" /></div>
          <div className={inputCls}><Label>Past Surgeries</Label><Input value={form.pastSurgeries} onChange={set('pastSurgeries')} placeholder="None" /></div>
        </div>
      );
      case 5: return (
        <div className="grid sm:grid-cols-2 gap-4">
          <div className={inputCls}><Label>LMP Date</Label><Input type="date" value={form.lmpDate} onChange={set('lmpDate')} /></div>
          <div className={inputCls}><Label>EDD Date</Label><Input type="date" value={form.eddDate} onChange={set('eddDate')} /></div>
          <div className={inputCls}><Label>Current Gestational Age</Label><Input value={form.currentGA} onChange={set('currentGA')} placeholder="24 weeks" /></div>
          <div className={inputCls}><Label>Complications</Label><Input value={form.complications} onChange={set('complications')} placeholder="None" /></div>
        </div>
      );
      case 6: return (
        <div className="grid sm:grid-cols-2 gap-4">
          <div className={inputCls}><Label>Hemoglobin (g/dL)</Label><Input type="number" step="0.1" value={form.hemoglobin} onChange={set('hemoglobin')} /></div>
          <div className={inputCls}><Label>Blood Group</Label><Input value={form.bloodGroup} onChange={set('bloodGroup')} placeholder="O+" /></div>
          <div className={inputCls}><Label>Blood Sugar Fasting</Label><Input type="number" value={form.bloodSugar} onChange={set('bloodSugar')} /></div>
          <div className={inputCls}><Label>Urine Protein</Label><Input value={form.urineProtein} onChange={set('urineProtein')} placeholder="Negative" /></div>
          <div className={inputCls}><Label>HIV Status</Label><Input value={form.hivStatus} onChange={set('hivStatus')} placeholder="Negative" /></div>
          <div className={inputCls}><Label>HBsAg Status</Label><Input value={form.hbsagStatus} onChange={set('hbsagStatus')} placeholder="Negative" /></div>
        </div>
      );
    }
  };

  return (
    <AppLayout>
      <div className="max-w-3xl mx-auto animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground mb-2">Register ANC Visit</h1>
        <p className="text-muted-foreground mb-6">Step {step + 1} of {steps.length}: {steps[step]}</p>

        {/* Progress */}
        <div className="flex gap-1 mb-8">
          {steps.map((_, i) => (
            <div key={i} className={`h-1.5 flex-1 rounded-full transition-colors ${i <= step ? 'bg-primary' : 'bg-border'}`} />
          ))}
        </div>

        <div className="bg-card rounded-lg border shadow-sm p-6">
          {error && <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md mb-4">{error}</div>}
          {renderStep()}
          <div className="flex justify-between mt-6">
            <Button variant="outline" onClick={() => setStep(s => s - 1)} disabled={step === 0}>
              <ChevronLeft className="mr-1 h-4 w-4" />Previous
            </Button>
            {step < steps.length - 1 ? (
              <Button onClick={() => setStep(s => s + 1)}>
                Next<ChevronRight className="ml-1 h-4 w-4" />
              </Button>
            ) : (
              <Button onClick={handleSubmit} disabled={loading}>
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Submit & Get AI Analysis
              </Button>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default VisitForm;
