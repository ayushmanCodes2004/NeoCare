import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useEffect } from 'react';
import '../styles/landing.css';

export default function LandingPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    // Scroll reveal animation
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.style.opacity = '1';
            e.target.style.transform = 'translateY(0)';
          }
        });
      },
      { threshold: 0.08 }
    );

    document.querySelectorAll('.step, .fcard, .rlcard').forEach((el) => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(18px)';
      el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  if (isAuthenticated) {
    navigate('/dashboard');
    return null;
  }

  const scrollToSection = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav className="nav">
        <div className="nav-logo">
          <div className="logo-mark">🌸</div>
          <div className="logo-text-wrap">
            NeoSure
            <span className="logo-sub">Maternal Health</span>
          </div>
        </div>
        <ul className="nav-links">
          <li><a href="#how">How It Works</a></li>
          <li><a href="#features">Features</a></li>
          <li><a href="#risk">Risk Levels</a></li>
        </ul>
        <div className="nav-right">
          <button className="btn-ghost" onClick={() => navigate('/login')}>Sign In</button>
          <button className="btn-primary" onClick={() => navigate('/signup')}>Register</button>
          <button className="btn-ghost" onClick={() => navigate('/doctor/login')} style={{ marginLeft: '1rem' }}>Doctor Login</button>
        </div>
      </nav>

      {/* Hero */}
      <section className="hero">
        <div className="hero-dots-tr"></div>
        <div className="hero-dots-bl"></div>
        <div className="hero-content">
          <p className="eyebrow">Supporting Mothers Across India</p>
          <h1>
            Safeguarding Every<br />
            <em>Mother</em>,<br />
            Every Pregnancy
          </h1>
          <p>
            NeoSure is your trusted health companion. Enter a mother's visit details and instantly know if she needs extra care — with clear guidance on exactly what to do next.
          </p>
          <div className="hero-btns">
            <button className="btn-fill" onClick={() => navigate('/signup')}>
              Check a Mother's Health
            </button>
            <button className="btn-outline" onClick={() => scrollToSection('how')}>
              See How It Works →
            </button>
          </div>
        </div>
        <div className="hero-visual">
          <div className="fpill" style={{ top: '-18px', right: '8px', color: 'var(--brown-md)' }}>
            🏥 Ministry of Health Approved
          </div>
          <div className="risk-card">
            <div className="rc-header">
              <span className="rc-label">Check-up Visit · Week 28</span>
              <span className="rbadge r">🔴 Needs Urgent Care</span>
            </div>
            <div className="pname">Priya Sharma</div>
            <div className="pmeta">Age 24 · 2nd Pregnancy · Raichur District</div>
            <div className="pgrid">
              <div className="pchip">
                <div className="plbl">Blood Levels</div>
                <div className="pval f">Too Low ↓</div>
              </div>
              <div className="pchip">
                <div className="plbl">Blood Pressure</div>
                <div className="pval f">Too High ↑</div>
              </div>
              <div className="pchip">
                <div className="plbl">Urine Test</div>
                <div className="pval f">Abnormal ↑</div>
              </div>
              <div className="pchip">
                <div className="plbl">Baby's Heartbeat</div>
                <div className="pval">Normal ✓</div>
              </div>
            </div>
            <div className="alert-box">
              <strong>⚡ Please refer to a doctor today —</strong> Priya's blood levels are very low and her blood pressure is high. This needs immediate attention.
            </div>
          </div>
          <div className="fpill" style={{ bottom: '-16px', left: '0', color: 'var(--green)' }}>
            ✅ Health guidelines checked
          </div>
        </div>
      </section>

      {/* Trust Bar */}
      <div className="trust-bar">
        <div className="trust-item">
          <span className="t-icon">🇮🇳</span>
          <span className="t-text">Aligned to National Health Guidelines</span>
        </div>
        <div className="trust-item">
          <span className="t-icon">📱</span>
          <span className="t-text">Works Offline on Any Phone</span>
        </div>
        <div className="trust-item">
          <span className="t-icon">🔒</span>
          <span className="t-text">Safe & Confidential Records</span>
        </div>
        <div className="trust-item">
          <span className="t-icon">⚡</span>
          <span className="t-text">Instant Results, No Waiting</span>
        </div>
      </div>

      {/* Stats Band */}
      <div className="stats-band">
        <div className="stats-dots-decor"></div>
        <div className="sitem">
          <div className="snum">45<span className="snum-suffix">K+</span></div>
          <div className="sdesc">Health workers across<br />India supported</div>
        </div>
        <div className="sitem">
          <div className="snum">6</div>
          <div className="sdesc">Key health signs<br />checked every visit</div>
        </div>
        <div className="sitem">
          <div className="snum">75<span className="snum-suffix">%</span></div>
          <div className="sdesc">At-risk mothers go unnoticed<br />without early checks</div>
        </div>
        <div className="sitem">
          <div className="snum">100<span className="snum-suffix">%</span></div>
          <div className="sdesc">Every warning backed by<br />national health guidelines</div>
        </div>
      </div>

      {/* How It Works */}
      <section id="how" className="sec how">
        <div className="sec-hdr">
          <p className="eyebrow">How It Works</p>
          <h2 className="sec-title">
            Three Simple Steps to<br />
            <em>Keep Mothers Safe</em>
          </h2>
          <p className="sec-sub">
            NeoSure fits right into your daily routine. No extra training, no complicated forms — just fill in what you already collect at every visit.
          </p>
        </div>
        <div className="steps">
          <div className="step">
            <div className="step-top-bar"></div>
            <div className="step-n">01</div>
            <h3>Fill In the Visit Details</h3>
            <p>
              Enter the mother's health readings from her MCP card — things like her blood levels, blood pressure, urine test result, and how the baby is doing. The form is simple and guides you through each field.
            </p>
          </div>
          <div className="step">
            <div className="step-top-bar"></div>
            <div className="step-n">02</div>
            <h3>NeoSure Reviews Her Health</h3>
            <p>
              NeoSure instantly checks the readings against national health guidelines — the same guidelines you follow in your work. It looks for early warning signs so nothing is missed.
            </p>
          </div>
          <div className="step">
            <div className="step-top-bar"></div>
            <div className="step-n">03</div>
            <h3>Get a Clear, Simple Result</h3>
            <p>
              You'll see a colour-coded result — Green, Amber, or Red — with easy instructions on what to do next. If the mother needs urgent help, NeoSure will help you connect her to a doctor right away.
            </p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="sec">
        <div className="sec-hdr">
          <p className="eyebrow">Features</p>
          <h2 className="sec-title">
            Made for <em>You</em>,<br />
            the Health Worker
          </h2>
          <p className="sec-sub">
            Every part of NeoSure is built around your daily work — so you can focus on caring for mothers, not figuring out the tool.
          </p>
        </div>
        <div className="feats">
          <div className="fcard">
            <div className="ficon fi1">🧠</div>
            <div>
              <h3>Smart Health Checks</h3>
              <p>
                NeoSure checks each mother's readings carefully and reliably, every single time. It never guesses — if something looks concerning, it tells you clearly and explains why in simple language.
              </p>
            </div>
          </div>
          <div className="fcard">
            <div className="ficon fi2">📋</div>
            <div>
              <h3>Backed by National Guidelines</h3>
              <p>
                Every suggestion NeoSure gives is based on the official health guidelines from the Ministry of Health. You can trust the advice — it's the same guidance doctors follow.
              </p>
            </div>
          </div>
          <div className="fcard">
            <div className="ficon fi3">⚡</div>
            <div>
              <h3>Instant Doctor Alert for Urgent Cases</h3>
              <p>
                When a mother needs urgent care, NeoSure helps you reach a doctor immediately. You don't have to figure it out alone — the tool guides you through the next step.
              </p>
            </div>
          </div>
          <div className="fcard">
            <div className="ficon fi4">📱</div>
            <div>
              <h3>Works on Any Phone, Anywhere</h3>
              <p>
                No internet? No problem. NeoSure works even in areas with poor signal. It opens like a regular website on any mobile phone — no app download needed.
              </p>
            </div>
          </div>
          <div className="fcard wide">
            <div className="ficon fi2">🔒</div>
            <div>
              <h3>Always Safe, Always Careful</h3>
              <p>
                NeoSure is designed to never give wrong advice. When it's not completely sure about something, it automatically asks for a doctor's help instead of guessing. Your mothers' safety always comes first — and the tool covers all 6 key checks from the national health program.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Risk Levels */}
      <section id="risk" className="sec risk-sec">
        <div className="risk-dots-decor"></div>
        <div className="sec-hdr">
          <p className="eyebrow">Risk Classification</p>
          <h2 className="sec-title">
            Three Colours.<br />
            <em>Always Clear. Always Helpful.</em>
          </h2>
          <p className="sec-sub">
            After entering a mother's details, you'll see one of three colours — each tells you exactly what care she needs right now.
          </p>
        </div>
        <div className="rlcards">
          <div className="rlcard g">
            <div className="rldot">✓</div>
            <h3>GREEN — All Good</h3>
            <p>
              All health readings are normal. Continue with the regular visit schedule. NeoSure will remind you when her next check-up is due.
            </p>
          </div>
          <div className="rlcard a">
            <div className="rldot">⚠</div>
            <h3>AMBER — Keep a Close Watch</h3>
            <p>
              One or more readings need monitoring. Visit her more frequently and watch for any changes. NeoSure tells you exactly what to look out for next time.
            </p>
          </div>
          <div className="rlcard r">
            <div className="rldot">🚨</div>
            <h3>RED — She Needs Help Now</h3>
            <p>
              A serious warning sign has been found. Please refer her to a health facility today. NeoSure will help you connect her to a doctor immediately.
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta">
        <div className="cta-glow"></div>
        <div className="cta-dots"></div>
        <h2>
          Every life saved starts<br />
          with <em>early detection</em>
        </h2>
        <p>
          Every mother deserves to be safe. With NeoSure by your side, no warning sign goes unnoticed — and no mother is left without the care she needs.
        </p>
        <div className="cta-btns">
          <button className="btn-cta fill" onClick={() => navigate('/signup')}>
            Start Helping Mothers
          </button>
          <button className="btn-cta ghost" onClick={() => scrollToSection('how')}>
            Learn More →
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer>
        <div className="ftlogo">
          Neo<span>Sure</span>
        </div>
        <p>Team One Step at a Time · DSATM · Hack-A-League 4.0</p>
        <p>Aligned to MOHFW National Maternal Health Guidelines</p>
      </footer>
    </div>
  );
}
