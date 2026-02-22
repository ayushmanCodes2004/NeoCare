import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getVisit } from '@/services/api';
import AppLayout from '@/components/AppLayout';
import RiskBadge from '@/components/RiskBadge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, AlertTriangle, CheckCircle, Stethoscope } from 'lucide-react';

const VisitResult = () => {
  const { visitId } = useParams();
  const [visit, setVisit] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!visitId) return;
    getVisit(visitId).then(r => setVisit(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, [visitId]);

  if (loading) return <AppLayout><div className="text-center py-12 text-muted-foreground">Loading AI analysis...</div></AppLayout>;
  if (!visit) return <AppLayout><div className="text-center py-12 text-muted-foreground">Visit not found.</div></AppLayout>;

  const risk = visit.riskAssessment;
  
  // Format date properly
  const formatDate = (dateStr: string) => {
    if (!dateStr) return 'N/A';
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return 'N/A';
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'N/A';
    }
  };

  // Format status for display
  const formatStatus = (status: string) => {
    if (!status) return '';
    return status.replace(/_/g, ' ').toLowerCase()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <AppLayout>
      <div className="max-w-3xl mx-auto animate-fade-in">
        <Link to={`/worker/patients/${visit.patientId}`} className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />Back to Patient
        </Link>

        <div className="bg-card rounded-lg border shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-foreground">{visit.patientName}</h1>
              <p className="text-muted-foreground text-sm">Visit on {formatDate(visit.savedAt)}</p>
              {visit.status && (
                <span className="inline-block mt-1 text-xs px-2 py-1 rounded-full bg-success/10 text-success">
                  {formatStatus(visit.status)}
                </span>
              )}
            </div>
            {risk && <RiskBadge level={risk.risk_level} className="text-sm px-3 py-1" />}
          </div>

          {risk && (
            <>
              {/* Risk Score */}
              <div className="bg-muted rounded-lg p-4 mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-foreground">Risk Score</span>
                  <span className="text-2xl font-bold text-foreground">{risk.risk_score}/100</span>
                </div>
                <div className="w-full h-3 bg-border rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${risk.risk_score}%`,
                      backgroundColor: risk.risk_level === 'LOW' ? 'hsl(var(--risk-low))' : risk.risk_level === 'MEDIUM' ? 'hsl(var(--risk-medium))' : risk.risk_level === 'HIGH' ? 'hsl(var(--risk-high))' : 'hsl(var(--risk-critical))',
                    }}
                  />
                </div>
              </div>

              {/* Risk Factors */}
              {risk.risk_factors?.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-risk-high" />Risk Factors
                  </h3>
                  <ul className="space-y-2">
                    {risk.risk_factors.map((f: string, i: number) => (
                      <li key={i} className="text-sm text-foreground bg-muted rounded-md p-3">{f}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommendations */}
              {risk.recommendations?.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-success" />Recommendations
                  </h3>
                  <ul className="space-y-2">
                    {risk.recommendations.map((r: string, i: number) => (
                      <li key={i} className="text-sm text-foreground bg-muted rounded-md p-3">{r}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Doctor Consultation */}
              {risk.requires_doctor_consultation && (
                <div className="bg-primary/10 border border-primary/20 rounded-lg p-4 flex items-start gap-3">
                  <Stethoscope className="h-5 w-5 text-primary mt-0.5" />
                  <div>
                    <p className="font-medium text-foreground">Doctor Consultation Recommended</p>
                    <p className="text-sm text-muted-foreground mt-1">Urgency: <span className="font-medium capitalize">{risk.urgency}</span></p>
                  </div>
                </div>
              )}

              {risk.summary && (
                <p className="text-sm text-muted-foreground mt-6 italic">{risk.summary}</p>
              )}
            </>
          )}

          {!risk && (
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6 text-center">
              <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-3" />
              <h3 className="font-semibold text-foreground mb-2">AI Risk Assessment Not Available</h3>
              <p className="text-sm text-muted-foreground mb-4">
                The AI analysis could not be completed for this visit. This may be due to:
              </p>
              <ul className="text-sm text-muted-foreground text-left max-w-md mx-auto space-y-1 mb-4">
                <li>• RAG Pipeline service not running</li>
                <li>• Data validation errors (422 error)</li>
                <li>• Network connectivity issues</li>
                <li>• Missing required fields</li>
              </ul>
              <p className="text-sm text-foreground font-medium">
                Status: {formatStatus(visit.status || 'REGISTERED')}
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                Check the backend logs for more details or try registering a new visit.
              </p>
            </div>
          )}
        </div>

        <div className="flex gap-3">
          <Link to={`/worker/patients/${visit.patientId}`}>
            <Button variant="outline">Back to Patient</Button>
          </Link>
          <Link to={`/worker/visits/new?patientId=${visit.patientId}`}>
            <Button>Register Another Visit</Button>
          </Link>
        </div>
      </div>
    </AppLayout>
  );
};

export default VisitResult;
