import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import AppLayout from '@/components/AppLayout';
import VideoCall from '@/components/VideoCall';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { completeConsultation } from '@/services/api';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';

const VideoConsultation = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [showComplete, setShowComplete] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [notes, setNotes] = useState({
    doctorNotes: '',
    diagnosis: '',
    actionPlan: ''
  });

  const handleEndCall = () => {
    setShowComplete(true);
  };

  const handleComplete = async () => {
    if (!id) return;
    if (!notes.doctorNotes || !notes.diagnosis || !notes.actionPlan) {
      toast.error('Please fill in all fields');
      return;
    }

    setCompleting(true);
    try {
      await completeConsultation(id, notes);
      toast.success('Consultation completed successfully');
      navigate(`/doctor/consultations/${id}`);
    } catch (error) {
      toast.error('Failed to complete consultation');
    } finally {
      setCompleting(false);
    }
  };

  const handleCancel = () => {
    setShowComplete(false);
    navigate(`/doctor/consultations/${id}`);
  };

  if (!id) {
    return (
      <AppLayout>
        <div className="text-center py-12 text-muted-foreground">Invalid consultation ID</div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto animate-fade-in">
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate(`/doctor/consultations/${id}`)}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Consultation
          </Button>
          <h1 className="text-2xl font-bold text-foreground">Video Consultation</h1>
          <p className="text-muted-foreground mt-1">Live video call with patient/worker</p>
        </div>

        <VideoCall
          consultationId={id}
          isDoctor={true}
          onEnd={handleEndCall}
        />

        {/* Complete Consultation Dialog */}
        <Dialog open={showComplete} onOpenChange={setShowComplete}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Complete Consultation</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="doctorNotes">Doctor Notes *</Label>
                <Textarea
                  id="doctorNotes"
                  value={notes.doctorNotes}
                  onChange={e => setNotes(p => ({ ...p, doctorNotes: e.target.value }))}
                  placeholder="Examination findings, observations..."
                  rows={4}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="diagnosis">Diagnosis *</Label>
                <Input
                  id="diagnosis"
                  value={notes.diagnosis}
                  onChange={e => setNotes(p => ({ ...p, diagnosis: e.target.value }))}
                  placeholder="Clinical diagnosis..."
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="actionPlan">Action Plan *</Label>
                <Textarea
                  id="actionPlan"
                  value={notes.actionPlan}
                  onChange={e => setNotes(p => ({ ...p, actionPlan: e.target.value }))}
                  placeholder="Treatment plan, follow-up instructions..."
                  rows={4}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={handleCancel} disabled={completing}>
                Cancel
              </Button>
              <Button
                onClick={handleComplete}
                disabled={completing || !notes.doctorNotes || !notes.diagnosis || !notes.actionPlan}
              >
                {completing ? 'Completing...' : 'Complete Consultation'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </AppLayout>
  );
};

export default VideoConsultation;
