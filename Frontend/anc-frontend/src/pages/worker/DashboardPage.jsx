import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { getPatients } from '../../api/patientApi';
import { getHighRisk, getCritical } from '../../api/visitApi';
import StatCard from '../../components/ui/StatCard';
import RiskBadge from '../../components/ui/RiskBadge';
import RiskDonutChart from '../../components/charts/RiskDonutChart';
import Spinner from '../../components/ui/Spinner';
import Button from '../../components/ui/Button';
import { Users, AlertTriangle, Activity, TrendingUp, ChevronRight, Plus } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function DashboardPage() {
  const { user }    = useAuth();
  const navigate    = useNavigate();
  const [data,  setData]  = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getPatients(), getHighRisk(), getCritical()])
      .then(([patients, highRisk, critical]) => {
        const high   = highRisk.filter(v => v.riskLevel === 'HIGH');
        const medium = highRisk.filter(v => v.riskLevel === 'MEDIUM');
        setData({ patients, highRisk, critical, high, medium });
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex h-full items-center justify-center">
      <Spinner lg />
    </div>
  );

  const chartData = [
    { name: 'CRITICAL', value: data.critical.length },
    { name: 'HIGH',     value: data.high.length },
    { name: 'MEDIUM',   value: data.medium.length },
  ].filter(d => d.value > 0);

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <p className="section-label">Overview</p>
          <h1 className="font-display text-2xl font-bold text-slate-100">
            Good {new Date().getHours() < 12 ? 'morning' : 'afternoon'}, {user?.fullName?.split(' ')[0]}
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">{user?.healthCenter} · {user?.district}</p>
        </div>
        <Button onClick={() => navigate('/patients/new')} className="gap-2">
          <Plus size={16} /> New Patient
        </Button>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Patients"  value={data.patients.length}  icon={Users}          accent="slate" />
        <StatCard label="High Risk"       value={data.highRisk.length}  icon={TrendingUp}     accent="high" />
        <StatCard label="Critical"        value={data.critical.length}  icon={AlertTriangle}  accent="critical" />
        <StatCard label="All Visits"      value={data.highRisk.length}  icon={Activity}       accent="teal" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* CRITICAL alerts */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <p className="section-label flex items-center gap-1.5">
              <AlertTriangle size={12} /> Critical Cases
            </p>
            <span className="text-xs text-slate-500">{data.critical.length} total</span>
          </div>
          <div className="space-y-2">
            {data.critical.length === 0 ? (
              <div className="glass-card p-8 text-center text-slate-500 text-sm">
                ✓ No critical cases at this time
              </div>
            ) : data.critical.slice(0, 5).map(v => (
              <button
                key={v.id}
                onClick={() => navigate(`/visits/${v.id}`)}
                className="w-full glass-card p-4 flex items-center justify-between hover:border-risk-critical/40 transition-colors group"
              >
                <div className="flex items-center gap-3 text-left">
                  <div className="h-2 w-2 rounded-full bg-risk-critical animate-pulse flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-slate-200">{v.patientName || `Patient #${v.patientId?.slice(-6)}`}</p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {v.detectedRisks?.slice(0,2).join(' · ')}
                      {v.createdAt && ` · ${formatDistanceToNow(new Date(v.createdAt), { addSuffix: true })}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <RiskBadge level={v.riskLevel} />
                  <ChevronRight size={16} className="text-slate-600 group-hover:text-slate-300 transition-colors" />
                </div>
              </button>
            ))}
          </div>
          {data.critical.length > 5 && (
            <button onClick={() => navigate('/patients')}
              className="mt-2 w-full text-xs text-slate-500 hover:text-teal-400 py-2 transition-colors">
              View all {data.critical.length} critical cases →
            </button>
          )}
        </div>

        {/* Risk chart + quick actions */}
        <div className="space-y-4">
          {chartData.length > 0 && (
            <div className="glass-card p-4">
              <p className="section-label mb-2">Risk Distribution</p>
              <RiskDonutChart data={chartData} />
            </div>
          )}
          <div className="glass-card p-4 space-y-2">
            <p className="section-label">Quick Actions</p>
            <Button variant="outline" className="w-full justify-start gap-2" onClick={() => navigate('/patients/new')}>
              <Plus size={15} /> Register Patient
            </Button>
            <Button variant="secondary" className="w-full justify-start gap-2" onClick={() => navigate('/patients')}>
              <Users size={15} /> View All Patients
            </Button>
          </div>

          {/* Recent patients */}
          {data.patients.length > 0 && (
            <div className="glass-card p-4">
              <p className="section-label mb-3">Recent Patients</p>
              <div className="space-y-2">
                {data.patients.slice(0, 4).map(p => (
                  <button key={p.patientId}
                    onClick={() => navigate(`/patients/${p.patientId}`)}
                    className="w-full flex items-center justify-between hover:bg-white/5 rounded-lg p-1.5 -mx-1.5 transition-colors group">
                    <span className="text-sm text-slate-300 truncate">{p.fullName}</span>
                    <ChevronRight size={14} className="text-slate-600 group-hover:text-slate-400 flex-shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
