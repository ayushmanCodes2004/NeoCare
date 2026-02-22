import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Heart, Shield, Activity, Video, Users, Brain } from 'lucide-react';

const Landing = () => {
  const features = [
    { icon: Users, title: 'Patient Management', desc: 'Register and track maternal patients with comprehensive health records.' },
    { icon: Brain, title: 'AI Risk Assessment', desc: 'Automated risk scoring powered by AI to identify high-risk pregnancies early.' },
    { icon: Activity, title: 'ANC Visit Tracking', desc: 'Record vitals, symptoms, and lab reports during antenatal care visits.' },
    { icon: Video, title: 'Doctor Consultations', desc: 'Priority-based consultation queue with video call support for specialists.' },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <header className="border-b bg-card/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <Heart className="h-7 w-7 text-primary" />
            <span className="text-xl font-bold text-foreground">NeoSure</span>
          </div>
          <div className="flex items-center gap-2">
            <Link to="/worker/login">
              <Button variant="ghost" size="sm">Worker Login</Button>
            </Link>
            <Link to="/doctor/login">
              <Button size="sm">Doctor Login</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="py-20 sm:py-32 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
            <Shield className="h-4 w-4" />
            AI-Powered Maternal Healthcare
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground leading-tight mb-6">
            Smarter Antenatal Care for{' '}
            <span className="text-primary">Every Mother</span>
          </h1>
          <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
            NeoSure empowers health workers with AI-driven risk assessments and connects them to specialists — ensuring no high-risk pregnancy goes unnoticed.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/worker/signup">
              <Button size="lg" className="w-full sm:w-auto text-base px-8">
                I'm a Health Worker
              </Button>
            </Link>
            <Link to="/doctor/signup">
              <Button variant="outline" size="lg" className="w-full sm:w-auto text-base px-8">
                I'm a Doctor
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-bold text-center text-foreground mb-12">
            Everything You Need for Better Outcomes
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((f) => (
              <div key={f.title} className="bg-card rounded-lg p-6 shadow-sm border hover:shadow-md transition-shadow">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <f.icon className="h-5 w-5 text-primary" />
                </div>
                <h3 className="font-semibold text-foreground mb-2">{f.title}</h3>
                <p className="text-sm text-muted-foreground">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8 px-4 text-center text-sm text-muted-foreground">
        © 2026 NeoSure. Built for better maternal health outcomes.
      </footer>
    </div>
  );
};

export default Landing;
