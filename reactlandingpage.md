# NeoSure — React Landing Page Specification

> **Goal:** Rebuild the NeoSure HTML landing page exactly in React. Every colour, font, spacing value, animation, component, and interaction must match the original pixel-for-pixel.

---

## Table of Contents

1. [Project Setup](#1-project-setup)
2. [Design Tokens & CSS Variables](#2-design-tokens--css-variables)
3. [Global Styles](#3-global-styles)
4. [Fonts](#4-fonts)
5. [File & Folder Structure](#5-file--folder-structure)
6. [Component Breakdown](#6-component-breakdown)
   - [App.jsx](#apjsx)
   - [Navbar](#navbar)
   - [Hero](#hero)
   - [TrustBar](#trustbar)
   - [StatsBand](#statsband)
   - [HowItWorks](#howitworks)
   - [Features](#features)
   - [RiskLevels](#risklevels)
   - [CTASection](#ctasection)
   - [Footer](#footer)
   - [AuthModal](#authmodal)
     - [AuthTop](#authtop)
     - [SignUpForm](#signupform)
     - [LoginForm](#loginform)
     - [Toast](#toast)
7. [All CSS — Exact Values](#7-all-css--exact-values)
   - [Landing Page CSS](#landing-page-css)
   - [Auth Modal CSS](#auth-modal-css)
8. [ANC Registry Data](#8-anc-registry-data)
9. [Animations & Scroll Reveal](#9-animations--scroll-reveal)
10. [Responsive Breakpoints](#10-responsive-breakpoints)
11. [Complete Component Code](#11-complete-component-code)

---

## 1. Project Setup

```bash
npx create-react-app neosure-landing
cd neosure-landing
npm install
```

No external libraries needed. Pure React + CSS Modules (or a single global CSS file).

**Dependencies (package.json additions — all optional):**
```json
{
  "dependencies": {
    "react": "^18.x",
    "react-dom": "^18.x"
  }
}
```

---

## 2. Design Tokens & CSS Variables

Define these in `src/index.css` under `:root`. Every component references these variables — do not hardcode hex values anywhere.

```css
:root {
  --terra:     #C4622D;   /* Primary terracotta — buttons, accents, hovers */
  --terra-dk:  #9E4A1E;   /* Dark terracotta — hover state for primary buttons */
  --terra-lt:  #E8835A;   /* Light terracotta — CTA italic text, gradients */
  --peach:     #F5E6D8;   /* Hero background, risk card chips, risk section bg */
  --peach-mid: #EDD5BF;   /* Trust bar background, tab pill background */
  --cream:     #FAF4EE;   /* Section backgrounds (How It Works, Features alt) */
  --warm-wh:   #FEFBF7;   /* Page body background */
  --brown-dk:  #2C1A0E;   /* Primary text, headings */
  --brown-md:  #5C3A1E;   /* Nav links, hero body text */
  --muted:     #8C6B52;   /* Subtitles, placeholder text, muted labels */
  --green:     #3A7D5C;   /* GREEN risk dot, green text */
  --amber:     #C4860A;   /* AMBER risk dot, amber text */
  --red:       #C03040;   /* RED risk, error states */
  --green-bg:  #E6F4ED;   /* GREEN risk card background */
  --amber-bg:  #FFF4DC;   /* AMBER risk card background */
  --red-bg:    #FDEAEB;   /* RED risk card background, alert box background */
  --dot:       rgba(196, 98, 45, 0.18); /* Dot pattern colour for decorative circles */
}
```

---

## 3. Global Styles

```css
/* src/index.css — add after :root */

*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: 'Jost', sans-serif;
  background: var(--warm-wh);
  color: var(--brown-dk);
  overflow-x: hidden;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

---

## 4. Fonts

Add to `public/index.html` inside `<head>`:

```html
<link
  href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Jost:wght@300;400;500;600&display=swap"
  rel="stylesheet"
/>
```

| Role | Font | Weight |
|---|---|---|
| Display headings (h1, h2, section titles) | Cormorant Garamond | 700 |
| Italic hero/CTA emphasis | Cormorant Garamond italic | 700 |
| Body text, labels, buttons, nav | Jost | 400, 500, 600 |
| Logo subtitle | Jost | 500 |
| ANC Worker ID input | monospace (system) | — |

---

## 5. File & Folder Structure

```
src/
├── index.css                  ← Global styles + CSS variables
├── index.js
├── App.jsx                    ← Root: renders all sections + AuthModal
├── components/
│   ├── Navbar/
│   │   ├── Navbar.jsx
│   │   └── Navbar.css
│   ├── Hero/
│   │   ├── Hero.jsx
│   │   └── Hero.css
│   ├── TrustBar/
│   │   ├── TrustBar.jsx
│   │   └── TrustBar.css
│   ├── StatsBand/
│   │   ├── StatsBand.jsx
│   │   └── StatsBand.css
│   ├── HowItWorks/
│   │   ├── HowItWorks.jsx
│   │   └── HowItWorks.css
│   ├── Features/
│   │   ├── Features.jsx
│   │   └── Features.css
│   ├── RiskLevels/
│   │   ├── RiskLevels.jsx
│   │   └── RiskLevels.css
│   ├── CTASection/
│   │   ├── CTASection.jsx
│   │   └── CTASection.css
│   ├── Footer/
│   │   ├── Footer.jsx
│   │   └── Footer.css
│   └── AuthModal/
│       ├── AuthModal.jsx
│       ├── AuthModal.css
│       ├── SignUpForm.jsx
│       ├── LoginForm.jsx
│       └── Toast.jsx
└── data/
    └── ancRegistry.js         ← Demo ANC worker registry object
```

---

## 6. Component Breakdown

---

### App.jsx

**Responsibilities:**
- Holds `authOpen` (boolean) and `authTab` ('signup' | 'login') state via `useState`
- Passes `openAuth(tab)` down to Navbar, Hero, CTASection
- Renders `<AuthModal>` at root level (portaled over everything)

```jsx
import { useState } from 'react';
import Navbar      from './components/Navbar/Navbar';
import Hero        from './components/Hero/Hero';
import TrustBar    from './components/TrustBar/TrustBar';
import StatsBand   from './components/StatsBand/StatsBand';
import HowItWorks  from './components/HowItWorks/HowItWorks';
import Features    from './components/Features/Features';
import RiskLevels  from './components/RiskLevels/RiskLevels';
import CTASection  from './components/CTASection/CTASection';
import Footer      from './components/Footer/Footer';
import AuthModal   from './components/AuthModal/AuthModal';

export default function App() {
  const [authOpen, setAuthOpen] = useState(false);
  const [authTab,  setAuthTab]  = useState('signup');

  const openAuth = (tab = 'signup') => {
    setAuthTab(tab);
    setAuthOpen(true);
    document.body.style.overflow = 'hidden';
  };
  const closeAuth = () => {
    setAuthOpen(false);
    document.body.style.overflow = '';
  };

  return (
    <>
      <Navbar     openAuth={openAuth} />
      <Hero       openAuth={openAuth} />
      <TrustBar   />
      <StatsBand  />
      <HowItWorks />
      <Features   />
      <RiskLevels />
      <CTASection openAuth={openAuth} />
      <Footer     />
      {authOpen && (
        <AuthModal
          tab={authTab}
          setTab={setAuthTab}
          onClose={closeAuth}
        />
      )}
    </>
  );
}
```

---

### Navbar

**File:** `components/Navbar/Navbar.jsx`

**Props:** `openAuth(tab)`

**Structure:**
```
<nav>
  ├── .nav-logo
  │   ├── .logo-mark  → 🌸 emoji in terracotta circle (36×36px, border-radius 50%)
  │   └── .logo-text-wrap
  │       ├── "NeoSure"  (Cormorant Garamond 700, 1.55rem)
  │       └── .logo-sub  "MATERNAL HEALTH" (Jost 500, 0.56rem, letter-spacing 1.5px, uppercase, var(--muted))
  ├── <ul>.nav-links
  │   ├── <li><a href="#how">How It Works</a>
  │   ├── <li><a href="#features">Features</a>
  │   └── <li><a href="#risk">Risk Levels</a>
  └── .nav-right
      ├── <button>.btn-ghost  "Sign In"   → openAuth('login')
      └── <button>.btn-primary "Register" → openAuth('signup')
```

**CSS (Navbar.css):**
```css
nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 200;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.9rem 6%;
  background: rgba(250, 244, 238, 0.93);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(196, 98, 45, 0.1);
}

.nav-logo {
  display: flex; align-items: center; gap: 0.6rem;
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.55rem; font-weight: 700; color: var(--brown-dk);
  text-decoration: none;
}

.logo-mark {
  width: 36px; height: 36px;
  background: var(--terra); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; flex-shrink: 0;
}

.logo-text-wrap {
  display: flex; flex-direction: column; line-height: 1;
}

.logo-sub {
  font-family: 'Jost', sans-serif;
  font-size: 0.56rem; font-weight: 500;
  letter-spacing: 1.5px; text-transform: uppercase;
  color: var(--muted); margin-top: 1px;
}

.nav-links {
  display: flex; gap: 2.2rem; list-style: none;
}

.nav-links a {
  text-decoration: none; font-size: 0.87rem; font-weight: 500;
  color: var(--brown-md); transition: color 0.2s;
}

.nav-links a:hover { color: var(--terra); }

.nav-right { display: flex; gap: 0.8rem; align-items: center; }

.btn-ghost {
  padding: 0.48rem 1.25rem;
  border: 1.5px solid var(--terra); border-radius: 4px;
  background: transparent; color: var(--terra);
  font-size: 0.84rem; font-weight: 600;
  cursor: pointer; font-family: 'Jost', sans-serif;
  transition: all 0.2s;
}
.btn-ghost:hover { background: var(--terra); color: #fff; }

.btn-primary {
  padding: 0.52rem 1.4rem; border: none; border-radius: 4px;
  background: var(--terra); color: #fff;
  font-size: 0.84rem; font-weight: 600;
  cursor: pointer; font-family: 'Jost', sans-serif;
  transition: background 0.2s, transform 0.15s;
}
.btn-primary:hover { background: var(--terra-dk); transform: translateY(-1px); }

@media (max-width: 900px) {
  .nav-links { display: none; }
}
```

---

### Hero

**File:** `components/Hero/Hero.jsx`

**Props:** `openAuth(tab)`

**Structure:**
```
<section>.hero
  ├── <div>.hero-dots-tr    (decorative dot pattern, top-right)
  ├── <div>.hero-dots-bl    (decorative dot pattern, bottom-left)
  ├── <div>.hero-content
  │   ├── <p>.eyebrow       "SUPPORTING MOTHERS ACROSS INDIA"
  │   ├── <h1>              "Safeguarding Every" <br/> <em>Mother</em>, <br/> "Every Pregnancy"
  │   ├── <p>               body text
  │   └── <div>.hero-btns
  │       ├── <button>.btn-fill    "Check a Mother's Health" → openAuth('signup')
  │       └── <button>.btn-outline "See How It Works →"      → scrollTo('#how')
  └── <div>.hero-visual
      ├── <div>.fpill (top pill)  "🏥 Ministry of Health Approved"
      ├── <div>.risk-card
      │   ├── .rc-header
      │   │   ├── .rc-label   "CHECK-UP VISIT · WEEK 28"
      │   │   └── .rbadge.r   "🔴 Needs Urgent Care"
      │   ├── .pname          "Priya Sharma"
      │   ├── .pmeta          "Age 24 · 2nd Pregnancy · Raichur District"
      │   ├── .pgrid (2×2 grid)
      │   │   ├── .pchip  Blood Levels    / Too Low ↓   (flagged)
      │   │   ├── .pchip  Blood Pressure  / Too High ↑  (flagged)
      │   │   ├── .pchip  Urine Test      / Abnormal ↑  (flagged)
      │   │   └── .pchip  Baby's Heartbeat/ Normal ✓    (normal)
      │   └── .alert-box  "⚡ Please refer to a doctor today — ..."
      └── <div>.fpill (bottom pill)  "✅ Health guidelines checked"
```

**CSS (Hero.css):**
```css
.hero {
  min-height: 100vh;
  background: var(--peach);
  display: flex; align-items: center;
  padding: 7.5rem 6% 5rem;
  position: relative; overflow: hidden;
}

/* Decorative dot circles */
.hero-dots-tr {
  position: absolute; top: 60px; right: 40px;
  width: 260px; height: 260px; border-radius: 50%;
  background-image: radial-gradient(var(--dot) 1.5px, transparent 1.5px);
  background-size: 16px 16px; pointer-events: none;
}
.hero-dots-bl {
  position: absolute; bottom: 40px; left: 30px;
  width: 180px; height: 180px; border-radius: 50%;
  background-image: radial-gradient(var(--dot) 1.5px, transparent 1.5px);
  background-size: 16px 16px; pointer-events: none;
}

.hero-content {
  max-width: 560px; position: relative; z-index: 1;
  animation: fadeUp 0.7s ease both;
}

.eyebrow {
  font-size: 0.72rem; font-weight: 600;
  letter-spacing: 2.5px; text-transform: uppercase;
  color: var(--terra); margin-bottom: 1rem;
}

.hero-content h1 {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2.9rem, 5.5vw, 4.5rem);
  font-weight: 700; line-height: 1.08;
  color: var(--brown-dk); margin-bottom: 1.3rem;
}
.hero-content h1 em { font-style: italic; color: var(--terra); }

.hero-content > p {
  font-size: 1rem; line-height: 1.8;
  color: var(--brown-md); max-width: 460px; margin-bottom: 2.2rem;
}

.hero-btns { display: flex; gap: 1rem; flex-wrap: wrap; }

.btn-fill {
  padding: 0.85rem 2rem; border-radius: 4px;
  background: var(--terra); color: #fff; border: none;
  font-size: 0.92rem; font-weight: 600;
  cursor: pointer; font-family: 'Jost', sans-serif;
  transition: background 0.2s, transform 0.15s, box-shadow 0.15s;
}
.btn-fill:hover {
  background: var(--terra-dk); transform: translateY(-2px);
  box-shadow: 0 8px 22px rgba(158, 74, 30, 0.3);
}

.btn-outline {
  padding: 0.85rem 2rem; border-radius: 4px;
  background: transparent; border: 1.5px solid var(--brown-md);
  color: var(--brown-dk); font-size: 0.92rem; font-weight: 600;
  cursor: pointer; font-family: 'Jost', sans-serif; transition: all 0.2s;
}
.btn-outline:hover { border-color: var(--terra); color: var(--terra); }

/* Hero visual card panel */
.hero-visual {
  position: absolute; right: 5%; top: 50%; transform: translateY(-50%);
  width: min(400px, 37vw); z-index: 1;
  animation: fadeUp 0.7s 0.18s ease both;
}

/* Floating pill badges */
.fpill {
  position: absolute;
  display: flex; align-items: center; gap: 0.4rem;
  background: #fff; border-radius: 50px; padding: 0.42rem 0.85rem;
  box-shadow: 0 4px 14px rgba(44, 26, 14, 0.12);
  font-size: 0.73rem; font-weight: 600; white-space: nowrap;
}
/* Top pill: top:-18px; right:8px; color:var(--brown-md) */
/* Bottom pill: bottom:-16px; left:0; color:var(--green) */

/* Risk card */
.risk-card {
  background: #fff; border-radius: 14px; padding: 1.6rem;
  box-shadow: 0 18px 55px rgba(44, 26, 14, 0.13);
}
.rc-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 1rem;
}
.rc-label {
  font-size: 0.7rem; font-weight: 600;
  color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px;
}
.rbadge {
  padding: 0.24rem 0.8rem; border-radius: 4px;
  font-size: 0.76rem; font-weight: 700;
}
.rbadge.r { background: var(--red-bg); color: var(--red); }
.rbadge.a { background: var(--amber-bg); color: var(--amber); }
.rbadge.g { background: var(--green-bg); color: var(--green); }

.pname {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.2rem; font-weight: 700;
}
.pmeta {
  font-size: 0.76rem; color: var(--muted); margin-bottom: 1.1rem;
}
.pgrid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 0.55rem; margin-bottom: 1.1rem;
}
.pchip {
  background: var(--peach); border-radius: 7px; padding: 0.55rem 0.75rem;
}
.plbl { font-size: 0.65rem; color: var(--muted); font-weight: 500; }
.pval { font-size: 0.88rem; font-weight: 700; color: var(--brown-dk); }
.pval.f { color: var(--red); }

.alert-box {
  background: var(--red-bg); border-left: 3px solid var(--red);
  border-radius: 0 7px 7px 0; padding: 0.65rem 0.85rem;
  font-size: 0.77rem; color: var(--red); line-height: 1.5;
}

@media (max-width: 900px) {
  .hero-visual { display: none; }
}
```

---

### TrustBar

**File:** `components/TrustBar/TrustBar.jsx`

**Data (hardcoded inline):**
```js
const items = [
  { icon: '🇮🇳', text: 'Aligned to National Health Guidelines' },
  { icon: '📱', text: 'Works Offline on Any Phone' },
  { icon: '🔒', text: 'Safe & Confidential Records' },
  { icon: '⚡', text: 'Instant Results, No Waiting' },
];
```

**CSS (TrustBar.css):**
```css
.trust-bar {
  background: var(--peach-mid); padding: 1.3rem 6%;
  display: flex; align-items: center; justify-content: center;
  gap: 3rem; flex-wrap: wrap;
  border-top: 1px solid rgba(196, 98, 45, 0.12);
  border-bottom: 1px solid rgba(196, 98, 45, 0.12);
}
.trust-item { display: flex; align-items: center; gap: 0.55rem; }
.trust-item .t-icon { font-size: 1.05rem; }
.trust-item .t-text { font-size: 0.81rem; font-weight: 500; color: var(--brown-md); }

@media (max-width: 900px) { .trust-bar { gap: 1rem; } }
```

---

### StatsBand

**File:** `components/StatsBand/StatsBand.jsx`

**Data:**
```js
const stats = [
  { num: '45', suffix: 'K+', desc: 'Health workers across\nIndia supported' },
  { num: '6',  suffix: '',   desc: 'Key health signs\nchecked every visit' },
  { num: '75', suffix: '%',  desc: 'At-risk mothers go unnoticed\nwithout early checks' },
  { num: '100',suffix: '%',  desc: 'Every warning backed by\nnational health guidelines' },
];
```

**CSS (StatsBand.css):**
```css
.stats-band {
  background: var(--terra); padding: 4rem 6%;
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem;
  position: relative; overflow: hidden;
}
/* Decorative dot watermark — top-right corner */
.stats-band::after {
  content: '';
  position: absolute; top: -60px; right: -60px;
  width: 320px; height: 320px; border-radius: 50%;
  background-image: radial-gradient(rgba(255,255,255,0.1) 1.5px, transparent 1.5px);
  background-size: 16px 16px; pointer-events: none;
}
/* In React, use a <div className="stats-dots-decor"> inside the component
   instead of ::after pseudo-element for easier portability */

.sitem { text-align: center; }
.snum {
  font-family: 'Cormorant Garamond', serif;
  font-size: 3.2rem; font-weight: 700; color: #fff;
  line-height: 1; margin-bottom: 0.4rem;
}
.snum-suffix { color: rgba(255,255,255,0.65); font-size: 2.2rem; }
.sdesc {
  font-size: 0.81rem; color: rgba(255,255,255,0.72); line-height: 1.5;
  white-space: pre-line;
}

@media (max-width: 900px) {
  .stats-band { grid-template-columns: repeat(2, 1fr); }
}
```

---

### HowItWorks

**File:** `components/HowItWorks/HowItWorks.jsx`

**Section id:** `how`

**Background:** `var(--cream)`

**Data:**
```js
const steps = [
  {
    num: '01',
    title: 'Fill In the Visit Details',
    body: "Enter the mother's health readings from her MCP card — things like her blood levels, blood pressure, urine test result, and how the baby is doing. The form is simple and guides you through each field.",
  },
  {
    num: '02',
    title: 'NeoSure Reviews Her Health',
    body: 'NeoSure instantly checks the readings against national health guidelines — the same guidelines you follow in your work. It looks for early warning signs so nothing is missed.',
  },
  {
    num: '03',
    title: 'Get a Clear, Simple Result',
    body: "You'll see a colour-coded result — Green, Amber, or Red — with easy instructions on what to do next. If the mother needs urgent help, NeoSure will help you connect her to a doctor right away.",
  },
];
```

**Section Header:**
- Eyebrow: `"How It Works"`
- Title: `"Three Simple Steps to"` + `<br/>` + `<em>Keep Mothers Safe</em>`
- Sub: `"NeoSure fits right into your daily routine. No extra training, no complicated forms — just fill in what you already collect at every visit."`

**CSS (HowItWorks.css):**
```css
/* Shared section styles — put in index.css or a shared file */
.sec { padding: 5.5rem 6%; }
.sec-hdr { margin-bottom: 3.5rem; }
.eyebrow {
  font-size: 0.72rem; font-weight: 600; letter-spacing: 2.5px;
  text-transform: uppercase; color: var(--terra); margin-bottom: 1rem;
}
.sec-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2rem, 3.5vw, 2.9rem); font-weight: 700; line-height: 1.18;
  color: var(--brown-dk); margin-bottom: 0.8rem;
}
.sec-title em { font-style: italic; color: var(--terra); }
.sec-sub { font-size: 0.93rem; color: var(--muted); max-width: 510px; line-height: 1.75; }

/* How It Works specific */
.how { background: var(--cream); }
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.8rem; }

.step {
  background: #fff; border-radius: 12px; padding: 2rem;
  border: 1px solid rgba(196, 98, 45, 0.1);
  position: relative; overflow: hidden;
  transition: transform 0.25s, box-shadow 0.25s;
  /* scroll reveal: starts at opacity:0, translateY(18px) */
}
/* Top terracotta bar */
.step::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0;
  height: 3px; background: var(--terra);
}
/* In React use a <div className="step-top-bar"> child instead */

.step:hover { transform: translateY(-4px); box-shadow: 0 14px 38px rgba(44,26,14,0.09); }

.step-n {
  font-family: 'Cormorant Garamond', serif;
  font-size: 4rem; font-weight: 700;
  color: var(--peach-mid); line-height: 1; margin-bottom: 0.8rem;
}
.step h3 { font-size: 1rem; font-weight: 600; margin-bottom: 0.55rem; }
.step p  { font-size: 0.86rem; color: var(--muted); line-height: 1.72; }

@media (max-width: 900px) {
  .steps { grid-template-columns: 1fr; }
}
```

---

### Features

**File:** `components/Features/Features.jsx`

**Section id:** `features`

**Background:** `var(--warm-wh)` (default page bg)

**Section Header:**
- Eyebrow: `"Features"`
- Title: `"Made for "` + `<em>You</em>` + `","` + `<br/>` + `"the Health Worker"`
- Sub: `"Every part of NeoSure is built around your daily work — so you can focus on caring for mothers, not figuring out the tool."`

**Data:**
```js
const features = [
  {
    icon: '🧠', iconBg: 'fi1', wide: false,
    title: 'Smart Health Checks',
    body: "NeoSure checks each mother's readings carefully and reliably, every single time. It never guesses — if something looks concerning, it tells you clearly and explains why in simple language.",
  },
  {
    icon: '📋', iconBg: 'fi2', wide: false,
    title: 'Backed by National Guidelines',
    body: "Every suggestion NeoSure gives is based on the official health guidelines from the Ministry of Health. You can trust the advice — it's the same guidance doctors follow.",
  },
  {
    icon: '⚡', iconBg: 'fi3', wide: false,
    title: 'Instant Doctor Alert for Urgent Cases',
    body: "When a mother needs urgent care, NeoSure helps you reach a doctor immediately. You don't have to figure it out alone — the tool guides you through the next step.",
  },
  {
    icon: '📱', iconBg: 'fi4', wide: false,
    title: 'Works on Any Phone, Anywhere',
    body: "No internet? No problem. NeoSure works even in areas with poor signal. It opens like a regular website on any mobile phone — no app download needed.",
  },
  {
    icon: '🔒', iconBg: 'fi-peach', wide: true,
    title: 'Always Safe, Always Careful',
    body: "NeoSure is designed to never give wrong advice. When it's not completely sure about something, it automatically asks for a doctor's help instead of guessing. Your mothers' safety always comes first — and the tool covers all 6 key checks from the national health program.",
  },
];
```

**CSS (Features.css):**
```css
.feats { display: grid; grid-template-columns: 1fr 1fr; gap: 1.3rem; }

.fcard {
  background: var(--cream); border-radius: 12px; padding: 1.75rem;
  display: flex; gap: 1.1rem;
  border: 1px solid rgba(196, 98, 45, 0.08);
  transition: transform 0.25s, box-shadow 0.25s, background 0.25s;
  /* scroll reveal: starts opacity:0 translateY(18px) */
}
.fcard:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 28px rgba(44, 26, 14, 0.08);
  background: #fff;
}
.fcard.wide { grid-column: 1 / -1; }

.ficon {
  width: 48px; height: 48px; flex-shrink: 0; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.25rem;
}
/* Icon background variants */
.fi1      { background: rgba(196, 98, 45, 0.12); }
.fi2      { background: var(--green-bg); }
.fi3      { background: var(--amber-bg); }
.fi4      { background: var(--peach); }
.fi-peach { background: var(--peach); }

.fcard h3 { font-size: 0.98rem; font-weight: 600; margin-bottom: 0.4rem; }
.fcard p  { font-size: 0.85rem; color: var(--muted); line-height: 1.7; }

@media (max-width: 900px) {
  .feats { grid-template-columns: 1fr; }
}
```

---

### RiskLevels

**File:** `components/RiskLevels/RiskLevels.jsx`

**Section id:** `risk`

**Background:** `var(--peach)` with decorative dot circle bottom-right

**Section Header:**
- Eyebrow: `"Risk Classification"`
- Title: `"Three Colours."` + `<br/>` + `<em>Always Clear. Always Helpful.</em>`
- Sub: `"After entering a mother's details, you'll see one of three colours — each tells you exactly what care she needs right now."`

**Data:**
```js
const risks = [
  {
    variant: 'g',
    dot: '✓',
    title: 'GREEN — All Good',
    body: 'All health readings are normal. Continue with the regular visit schedule. NeoSure will remind you when her next check-up is due.',
  },
  {
    variant: 'a',
    dot: '⚠',
    title: 'AMBER — Keep a Close Watch',
    body: 'One or more readings need monitoring. Visit her more frequently and watch for any changes. NeoSure tells you exactly what to look out for next time.',
  },
  {
    variant: 'r',
    dot: '🚨',
    title: 'RED — She Needs Help Now',
    body: 'A serious warning sign has been found. Please refer her to a health facility today. NeoSure will help you connect her to a doctor immediately.',
  },
];
```

**CSS (RiskLevels.css):**
```css
.risk-sec { background: var(--peach); position: relative; overflow: hidden; }
/* Dot watermark bottom-right — use a <div className="risk-dots-decor"> */
.risk-dots-decor {
  position: absolute; bottom: -50px; right: -50px;
  width: 300px; height: 300px; border-radius: 50%;
  background-image: radial-gradient(var(--dot) 1.5px, transparent 1.5px);
  background-size: 18px 18px; pointer-events: none;
}

.rlcards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }

.rlcard {
  border-radius: 12px; padding: 2rem; text-align: center;
  transition: transform 0.25s;
  /* scroll reveal: opacity:0 translateY(18px) */
}
.rlcard:hover { transform: translateY(-4px); }

.rlcard.g { background: var(--green-bg); border: 1px solid rgba(58,125,92,0.2); }
.rlcard.a { background: var(--amber-bg); border: 1px solid rgba(196,134,10,0.2); }
.rlcard.r { background: var(--red-bg);   border: 1px solid rgba(192,48,64,0.2); }

.rldot {
  width: 58px; height: 58px; border-radius: 50%;
  margin: 0 auto 1rem;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem;
}
.rlcard.g .rldot { background: var(--green); }
.rlcard.a .rldot { background: var(--amber); }
.rlcard.r .rldot { background: var(--red); }

.rlcard h3 {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.3rem; font-weight: 700; margin-bottom: 0.5rem;
}
.rlcard.g h3 { color: var(--green); }
.rlcard.a h3 { color: var(--amber); }
.rlcard.r h3 { color: var(--red); }

.rlcard p { font-size: 0.85rem; color: var(--muted); line-height: 1.65; }

@media (max-width: 900px) {
  .rlcards { grid-template-columns: 1fr; }
}
```

---

### CTASection

**File:** `components/CTASection/CTASection.jsx`

**Props:** `openAuth(tab)`

**Background:** `var(--brown-dk)` with radial gradient overlay + dot watermark

**Content:**
- h2: `"Every life saved starts"` + `<br/>` + `"with "` + `<em>early detection</em>`
- p: `"Every mother deserves to be safe. With NeoSure by your side, no warning sign goes unnoticed — and no mother is left without the care she needs."`
- Buttons:
  - `.btn-cta.fill` → `"Start Helping Mothers"` → `openAuth('signup')`
  - `.btn-cta.ghost` → `"Learn More →"` → `scrollTo('#how')`

**CSS (CTASection.css):**
```css
.cta {
  background: var(--brown-dk); padding: 6rem 6%; text-align: center;
  position: relative; overflow: hidden;
}
/* Radial glow overlay — use <div className="cta-glow"> */
.cta-glow {
  position: absolute; inset: 0; pointer-events: none;
  background: radial-gradient(ellipse 70% 80% at 50% 50%, rgba(196,98,45,0.18), transparent 70%);
}
/* Dot watermark — use <div className="cta-dots"> */
.cta-dots {
  position: absolute; top: -60px; left: -60px;
  width: 360px; height: 360px; border-radius: 50%;
  background-image: radial-gradient(rgba(255,255,255,0.055) 1.5px, transparent 1.5px);
  background-size: 18px 18px; pointer-events: none;
}

.cta h2 {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2.1rem, 4.5vw, 3.3rem); font-weight: 700;
  color: #fff; margin-bottom: 1rem; position: relative;
}
.cta h2 em { font-style: italic; color: var(--terra-lt); }

.cta > p {
  font-size: 0.97rem; color: rgba(255,255,255,0.6);
  max-width: 440px; margin: 0 auto 2.5rem; line-height: 1.75;
  position: relative;
}

.cta-btns { display: flex; gap: 1rem; justify-content: center; position: relative; flex-wrap: wrap; }

.btn-cta {
  padding: 0.85rem 2.2rem; border-radius: 4px;
  font-size: 0.9rem; font-weight: 600;
  cursor: pointer; font-family: 'Jost', sans-serif; transition: all 0.2s;
}
.btn-cta.fill { background: var(--terra); color: #fff; border: none; }
.btn-cta.fill:hover { background: var(--terra-lt); transform: translateY(-2px); }
.btn-cta.ghost {
  background: transparent; color: #fff;
  border: 1.5px solid rgba(255,255,255,0.3);
}
.btn-cta.ghost:hover { border-color: rgba(255,255,255,0.7); }
```

---

### Footer

**File:** `components/Footer/Footer.jsx`

**CSS (Footer.css):**
```css
footer {
  background: #180C06; padding: 2rem 6%;
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 1rem;
}
.ftlogo {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.2rem; font-weight: 700; color: #fff;
}
.ftlogo span { color: var(--terra-lt); }
footer p { font-size: 0.77rem; color: rgba(255,255,255,0.32); }
```

**Content:**
- Logo: `Neo` + `<span>Sure</span>` (Sure in `var(--terra-lt)`)
- p1: `"Team One Step at a Time · DSATM · Hack-A-League 4.0"`
- p2: `"Aligned to MOHFW National Maternal Health Guidelines"`

---

### AuthModal

**File:** `components/AuthModal/AuthModal.jsx`

**Props:** `tab` ('signup'|'login'), `setTab`, `onClose`

**State (inside AuthModal):**
- `step` (1 | 2) — for signup multi-step
- `formData` — object holding all field values
- `errors` — object holding validation error messages
- `loading` — boolean for submit button spinner
- `toastMsg` — string for toast notification

**Structure:**
```
<div>.auth-overlay  (onclick on overlay bg → onClose)
  └── <div>.auth-modal  (onclick stopPropagation)
      ├── <AuthTop tab={tab} setTab={setTab} onClose={onClose} />
      └── <div>.auth-body
          ├── <div>.auth-tab-pills
          │   ├── <button> Create Account (active if tab==='signup')
          │   └── <button> Sign In        (active if tab==='login')
          ├── {tab === 'signup' && <SignUpForm ... />}
          └── {tab === 'login'  && <LoginForm  ... />}
```

#### AuthTop

Terracotta gradient header inside the card. Content changes based on tab.

```js
const content = {
  signup: {
    title: <>Empowering Care,<br /><em>One Mother at a Time</em></>,
    sub: 'Register as a certified ANC Worker to monitor maternal health and protect every mother in your care.',
  },
  login: {
    title: <>Welcome Back,<br /><em>Care Provider</em></>,
    sub: 'Sign in to access your maternal health dashboard and ANC risk intelligence tools.',
  },
};
```

**CSS (AuthModal.css — AuthTop part):**
```css
.auth-top {
  background: linear-gradient(135deg, var(--terra-dk) 0%, var(--terra) 55%, var(--terra-lt) 100%);
  padding: 1.5rem 1.8rem 1.3rem;
  position: relative; text-align: center;
}
/* Dot overlay — use <div className="auth-top-dots"> */
.auth-top-dots {
  position: absolute; inset: 0; pointer-events: none;
  background-image: radial-gradient(rgba(255,255,255,0.1) 1.5px, transparent 1.5px);
  background-size: 18px 18px;
}
.auth-close {
  position: absolute; top: 0.85rem; right: 0.9rem;
  background: rgba(255,255,255,0.2); border: none; border-radius: 50%;
  width: 26px; height: 26px; display: flex; align-items: center; justify-content: center;
  font-size: 0.85rem; cursor: pointer; color: #fff; transition: background 0.2s;
}
.auth-close:hover { background: rgba(255,255,255,0.35); }
.auth-logo-row {
  display: flex; align-items: center; justify-content: center;
  gap: 0.4rem; margin-bottom: 0.55rem;
}
.auth-logo-dot {
  width: 24px; height: 24px; background: rgba(255,255,255,0.2);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 0.8rem;
}
.auth-logo-name {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1rem; font-weight: 700; color: rgba(255,255,255,0.92);
}
.auth-top-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.55rem; font-weight: 700; color: #fff; line-height: 1.2; margin-bottom: 0.2rem;
}
.auth-top-title em { font-style: italic; color: rgba(255,255,255,0.78); }
.auth-top-sub {
  font-size: 0.76rem; color: rgba(255,255,255,0.62); line-height: 1.5;
  max-width: 320px; margin: 0 auto;
}
```

#### SignUpForm

Two-step form:
- **Step 1:** First Name, Last Name, Age, Gender, Date of Birth, Email, Address, ANC Worker ID
- **Step 2:** Password (with strength meter), Confirm Password, Terms checkbox

**Step Indicator:**
```
[●1 Personal Info] ——— [○2 Set Password]
```
Step 1 active → terracotta circle. Done → green circle with ✓.

**ANC ID Validation regex:** `/^ANM\/[A-Z]{2}\/[A-Z]{3}\/\d{4}\/\d{4}$/`

**Password Strength Rules:**
- `r-len`: length ≥ 8
- `r-upper`: has uppercase letter
- `r-num`: has number
- Score 1 → red `#E53935` "Weak"
- Score 2 → orange `#FF9800` "Moderate"
- Score 3 → green `#2E7D32` "Strong"

#### LoginForm

- Social buttons (Google, Facebook) — decorative only
- Divider: `"or sign in with your ANC Worker ID"`
- ANC Worker ID field (monospace, auto-uppercase)
- Password field (with show/hide toggle)
- Forgot password link
- Remember me checkbox
- Submit button with loading spinner
- Trust badges row: 🔒 Secure Login · 🌿 Trusted by 45K+ · ⭐ 5-Star Rated · 🤱 ANC Focused

---

## 7. All CSS — Exact Values

### Landing Page CSS

> Full consolidated reference. All values taken directly from the HTML source.

```css
/* ═══ LAYOUT SHARED ═══ */
.sec { padding: 5.5rem 6%; }
.sec-hdr { margin-bottom: 3.5rem; }

/* ═══ EYEBROW ═══ */
.eyebrow {
  font-size: 0.72rem; font-weight: 600; letter-spacing: 2.5px;
  text-transform: uppercase; color: var(--terra); margin-bottom: 1rem;
}

/* ═══ SECTION TITLE ═══ */
.sec-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2rem, 3.5vw, 2.9rem); font-weight: 700; line-height: 1.18;
  color: var(--brown-dk); margin-bottom: 0.8rem;
}
.sec-title em { font-style: italic; color: var(--terra); }
.sec-sub { font-size: 0.93rem; color: var(--muted); max-width: 510px; line-height: 1.75; }
```

### Auth Modal CSS

```css
/* ═══ OVERLAY & MODAL SHELL ═══ */
.auth-overlay {
  display: flex; /* controlled by React conditional render */
  position: fixed; inset: 0; z-index: 500;
  background: rgba(44, 26, 14, 0.62); backdrop-filter: blur(10px);
  align-items: center; justify-content: center; padding: 1rem;
}
.auth-modal {
  width: 100%; max-width: 448px;
  background: var(--cream); border-radius: 22px;
  box-shadow: 0 28px 80px rgba(44, 26, 14, 0.25);
  border: 1px solid rgba(196, 98, 45, 0.1); overflow: hidden;
  animation: authFadeUp 0.38s cubic-bezier(0.22, 0.8, 0.36, 1) both;
}
@keyframes authFadeUp {
  from { opacity: 0; transform: translateY(20px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0)   scale(1); }
}

/* ═══ BODY ═══ */
.auth-body { padding: 1.3rem 1.8rem 1.6rem; }

/* ═══ TAB PILLS ═══ */
.auth-tab-pills {
  display: flex; background: var(--peach-mid); border-radius: 100px;
  padding: 3px; margin-bottom: 1.2rem; gap: 3px;
}
.auth-tab-pill {
  flex: 1; padding: 7px; border-radius: 100px; border: none;
  font-family: 'Jost', sans-serif; font-size: 0.83rem; font-weight: 600;
  cursor: pointer; transition: all 0.22s; color: var(--muted); background: transparent;
}
.auth-tab-pill.active {
  background: var(--terra); color: white;
  box-shadow: 0 3px 10px rgba(196, 97, 42, 0.3);
}

/* ═══ STEP INDICATOR ═══ */
.stp-indicator { display: flex; align-items: center; margin-bottom: 1rem; }
.stp-item { display: flex; flex-direction: column; align-items: center; gap: 3px; flex-shrink: 0; }
.stp-num {
  width: 26px; height: 26px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.75rem; font-weight: 700;
  border: 2px solid rgba(196, 98, 45, 0.2); color: var(--muted);
  background: white; transition: all 0.3s;
}
.stp-item.active .stp-num { background: var(--terra); border-color: var(--terra); color: white; box-shadow: 0 2px 8px rgba(196,97,42,0.3); }
.stp-item.done   .stp-num { background: #2E7D32; border-color: #2E7D32; color: white; }
.stp-lbl { font-size: 0.6rem; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }
.stp-item.active .stp-lbl { color: var(--terra); }
.stp-line { flex: 1; height: 2px; background: rgba(196,98,45,0.14); margin: 0 8px 13px; transition: background 0.3s; }
.stp-line.done { background: #2E7D32; }

/* ═══ FORM FIELDS ═══ */
.af { margin-bottom: 0.65rem; }
.af label {
  display: block; font-size: 0.68rem; font-weight: 600;
  color: var(--brown-dk); margin-bottom: 0.25rem;
  letter-spacing: 0.03em; text-transform: uppercase;
}
.af input, .af select {
  width: 100%; padding: 8px 12px;
  border: 1.5px solid rgba(196,98,45,0.17); border-radius: 8px;
  font-family: 'Jost', sans-serif; font-size: 0.86rem;
  color: var(--brown-dk); background: white;
  transition: all 0.2s; outline: none;
}
.af input::placeholder { color: #C4A898; }
.af input:focus, .af select:focus {
  border-color: var(--terra); box-shadow: 0 0 0 3px rgba(196,98,45,0.09);
}
.af input.aerr, .af select.aerr { border-color: #E53935; background: #FFF5F5; }
.af-err { font-size: 0.67rem; color: #C62828; margin-top: 2px; display: none; }
.af-err.show { display: block; }
.af-hint { font-size: 0.66rem; color: var(--muted); margin-top: 3px; line-height: 1.4; }
.af-row { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; }

/* ═══ PASSWORD TOGGLE ═══ */
.pwd-wrap { position: relative; }
.pwd-wrap input { padding-right: 38px; }
.pwd-toggle {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer; color: var(--muted);
  display: flex; padding: 3px;
}

/* ═══ PASSWORD STRENGTH ═══ */
.str-bar { height: 2px; border-radius: 2px; background: #E8D5C8; margin-top: 4px; overflow: hidden; }
.str-fill { height: 100%; border-radius: 2px; width: 0; transition: all 0.3s; }
.str-label { font-size: 0.65rem; color: var(--muted); margin-top: 2px; }
.pwd-rules { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
.pwd-rule { display: flex; align-items: center; gap: 3px; font-size: 0.65rem; color: var(--muted); }
.pwd-rule.pass { color: #2E7D32; }
.pwd-rdot { width: 5px; height: 5px; border-radius: 50%; border: 1.5px solid #CCC; flex-shrink: 0; }
.pwd-rule.pass .pwd-rdot { background: #2E7D32; border-color: #2E7D32; }

/* ═══ DIVIDER ═══ */
.auth-divider { display: flex; align-items: center; gap: 8px; margin: 0.7rem 0; font-size: 0.68rem; color: var(--muted); }
.auth-divider::before, .auth-divider::after { content: ''; flex: 1; height: 1px; background: rgba(196,98,45,0.13); }

/* ═══ SOCIAL BUTTONS ═══ */
.social-row { display: flex; gap: 8px; margin-bottom: 0.5rem; }
.social-btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 8px; border-radius: 8px; border: 1.5px solid rgba(196,98,45,0.15);
  background: white; cursor: pointer; font-family: 'Jost', sans-serif;
  font-size: 0.76rem; font-weight: 500; color: var(--brown-dk); transition: all 0.2s;
}
.social-btn:hover { border-color: var(--terra); background: rgba(196,98,45,0.04); }

/* ═══ CHECKBOX ═══ */
.chk-row { display: flex; align-items: flex-start; gap: 7px; margin-bottom: 0.8rem; }
.chk-row input[type="checkbox"] { width: 13px; height: 13px; margin-top: 2px; accent-color: var(--terra); cursor: pointer; flex-shrink: 0; }
.chk-row label { font-size: 0.75rem; color: var(--muted); line-height: 1.5; cursor: pointer; }
.chk-row a { color: var(--terra); text-decoration: none; font-weight: 500; }

/* ═══ FORGOT PASSWORD ═══ */
.forgot-row { display: flex; justify-content: flex-end; margin: -0.3rem 0 0.7rem; }
.forgot-row a { font-size: 0.73rem; color: var(--terra); text-decoration: none; font-weight: 500; }

/* ═══ SUBMIT BUTTON ═══ */
.auth-submit {
  width: 100%; padding: 10px; border-radius: 100px; border: none;
  background: var(--terra); color: white;
  font-family: 'Jost', sans-serif; font-size: 0.88rem; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  box-shadow: 0 4px 14px rgba(196,97,42,0.3);
}
.auth-submit:hover { background: var(--terra-dk); transform: translateY(-1px); box-shadow: 0 7px 20px rgba(196,97,42,0.36); }
.auth-submit:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

/* Spinner */
.aloader {
  width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white; border-radius: 50%;
  animation: aspin 0.7s linear infinite;
}
@keyframes aspin { to { transform: rotate(360deg); } }

/* ═══ BACK BUTTON ═══ */
.auth-back {
  padding: 9px 15px; border-radius: 100px; border: 1.5px solid rgba(196,98,45,0.17);
  background: transparent; color: var(--muted);
  font-family: 'Jost', sans-serif; font-size: 0.83rem; font-weight: 600;
  cursor: pointer; transition: all 0.2s; white-space: nowrap;
}
.auth-back:hover { border-color: var(--terra); color: var(--terra); }

/* ═══ VERIFIED BADGE ═══ */
.verified-badge {
  display: flex; align-items: center; gap: 9px;
  background: #F1FBF3; border: 1px solid #A5D6A7; border-radius: 8px;
  padding: 9px 13px; margin-bottom: 0.9rem;
}
.vb-icon { font-size: 1.2rem; line-height: 1; }
.vb-title { font-weight: 700; font-size: 0.8rem; color: #2E7D32; }
.vb-id { font-size: 0.68rem; color: #4CAF50; font-family: monospace; margin-top: 1px; letter-spacing: 0.05em; }

/* ═══ SWITCH TEXT ═══ */
.auth-switch { text-align: center; margin-top: 0.85rem; font-size: 0.78rem; color: var(--muted); }
.auth-switch a { color: var(--terra); font-weight: 600; text-decoration: none; cursor: pointer; }

/* ═══ TRUST BADGES (login) ═══ */
.trust-badges {
  margin-top: 0.9rem; padding-top: 0.9rem;
  border-top: 1px solid rgba(196,98,45,0.1);
  display: flex; align-items: center; justify-content: center; gap: 1.2rem;
}
.tb { text-align: center; }
.tb-icon { font-size: 0.95rem; }
.tb-label { font-size: 0.6rem; color: var(--muted); margin-top: 1px; font-weight: 500; }

/* ═══ TOAST ═══ */
.auth-toast {
  position: fixed; bottom: 28px; left: 50%;
  transform: translateX(-50%) translateY(80px);
  background: var(--brown-dk); color: white;
  padding: 9px 20px; border-radius: 100px; font-size: 0.82rem; font-weight: 500;
  z-index: 600; transition: transform 0.3s ease; white-space: nowrap;
}
.auth-toast.show { transform: translateX(-50%) translateY(0); }

/* ═══ RESPONSIVE ═══ */
@media (max-width: 480px) {
  .auth-body { padding: 1.1rem 1.1rem 1.4rem; }
  .auth-top  { padding: 1.2rem 1.1rem 1rem; }
  .af-row { grid-template-columns: 1fr; }
}
```

---

## 8. ANC Registry Data

**File:** `src/data/ancRegistry.js`

```js
export const REGISTRY = {
  'ANM/KA/BLR/2024/0178': { firstName: 'Priya',   lastName: 'Sharma'  },
  'ANM/KA/MYS/2023/0042': { firstName: 'Lakshmi', lastName: 'Nair'    },
  'ANM/MH/PUN/2022/0315': { firstName: 'Sneha',   lastName: 'Patil'   },
  'ANM/MH/MUM/2024/0089': { firstName: 'Anita',   lastName: 'Desai'   },
  'ANM/TN/CHE/2021/0201': { firstName: 'Kavitha', lastName: 'Rajan'   },
  'ANM/AP/VIZ/2022/0078': { firstName: 'Sunita',  lastName: 'Reddy'   },
  'ANM/GJ/AHM/2020/0067': { firstName: 'Heena',   lastName: 'Patel'   },
  'ANM/WB/KOL/2022/0222': { firstName: 'Rina',    lastName: 'Das'     },
};

export const ANC_REGEX = /^ANM\/[A-Z]{2}\/[A-Z]{3}\/\d{4}\/\d{4}$/;
```

---

## 9. Animations & Scroll Reveal

### Page load animations

Hero content and hero visual card both use `fadeUp` on mount:
```css
/* Hero content */
animation: fadeUp 0.7s ease both;

/* Hero visual card — delayed */
animation: fadeUp 0.7s 0.18s ease both;
```

### Scroll Reveal (IntersectionObserver)

Apply to: `.step`, `.fcard`, `.rlcard`

**Implementation in React:**
```jsx
import { useEffect, useRef } from 'react';

export function useScrollReveal() {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.opacity = '0';
    el.style.transform = 'translateY(18px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease, box-shadow 0.25s, background 0.25s';
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.style.opacity = '1';
          el.style.transform = 'translateY(0)';
          observer.disconnect();
        }
      },
      { threshold: 0.08 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);
  return ref;
}
```

**Usage in each card:**
```jsx
function StepCard({ num, title, body }) {
  const ref = useScrollReveal();
  return (
    <div className="step" ref={ref}>
      <div className="step-top-bar" />
      <div className="step-n">{num}</div>
      <h3>{title}</h3>
      <p>{body}</p>
    </div>
  );
}
```

---

## 10. Responsive Breakpoints

Single breakpoint at `900px`. At `≤900px`:

| Element | Change |
|---|---|
| `.hero-visual` | `display: none` |
| `.stats-band` | `grid-template-columns: repeat(2, 1fr)` |
| `.steps` | `grid-template-columns: 1fr` |
| `.feats` | `grid-template-columns: 1fr` |
| `.rlcards` | `grid-template-columns: 1fr` |
| `.nav-links` | `display: none` |
| `.trust-bar` | `gap: 1rem` |

Auth modal breakpoint at `480px`:
- `.auth-body` padding: `1.1rem 1.1rem 1.4rem`
- `.auth-top` padding: `1.2rem 1.1rem 1rem`
- `.af-row` → `grid-template-columns: 1fr`

---

## 11. Complete Component Code

### App.jsx — Full

```jsx
import { useState } from 'react';
import Navbar      from './components/Navbar/Navbar';
import Hero        from './components/Hero/Hero';
import TrustBar    from './components/TrustBar/TrustBar';
import StatsBand   from './components/StatsBand/StatsBand';
import HowItWorks  from './components/HowItWorks/HowItWorks';
import Features    from './components/Features/Features';
import RiskLevels  from './components/RiskLevels/RiskLevels';
import CTASection  from './components/CTASection/CTASection';
import Footer      from './components/Footer/Footer';
import AuthModal   from './components/AuthModal/AuthModal';

export default function App() {
  const [authOpen, setAuthOpen] = useState(false);
  const [authTab,  setAuthTab]  = useState('signup');

  const openAuth = (tab = 'signup') => {
    setAuthTab(tab);
    setAuthOpen(true);
    document.body.style.overflow = 'hidden';
  };
  const closeAuth = () => {
    setAuthOpen(false);
    document.body.style.overflow = '';
  };

  return (
    <>
      <Navbar     openAuth={openAuth} />
      <main>
        <Hero       openAuth={openAuth} />
        <TrustBar   />
        <StatsBand  />
        <HowItWorks />
        <Features   />
        <RiskLevels />
        <CTASection openAuth={openAuth} />
      </main>
      <Footer />
      {authOpen && (
        <AuthModal tab={authTab} setTab={setAuthTab} onClose={closeAuth} />
      )}
    </>
  );
}
```

### AuthModal.jsx — Full Logic

```jsx
import { useState } from 'react';
import { REGISTRY, ANC_REGEX } from '../../data/ancRegistry';
import './AuthModal.css';

export default function AuthModal({ tab, setTab, onClose }) {
  const [step, setStep]       = useState(1);
  const [loading, setLoading] = useState(false);
  const [toast, setToast]     = useState('');
  const [verifiedId, setVerifiedId] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [showPwd2, setShowPwd2] = useState(false);
  const [pwdStrength, setPwdStrength] = useState({ score: 0, label: 'Enter a password', color: '#E8D5C8', rules: { len: false, upper: false, num: false } });
  const [errors, setErrors]   = useState({});
  const [form, setForm]       = useState({
    fname: '', lname: '', age: '', gender: '', dob: '', email: '', address: '', ancid: '',
    pwd: '', pwd2: '', agree: false, liAncid: '', liPwd: '', remember: false,
  });

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3800);
  };

  const set = (field) => (e) => {
    const val = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setForm(f => ({ ...f, [field]: field === 'ancid' || field === 'liAncid' ? val.toUpperCase() : val }));
  };

  const checkStrength = (val) => {
    const len = val.length >= 8, upper = /[A-Z]/.test(val), num = /[0-9]/.test(val);
    const score = [len, upper, num].filter(Boolean).length;
    const clrs  = ['#E53935', '#FF9800', '#2E7D32'];
    const lbls  = ['Weak', 'Moderate', 'Strong'];
    setPwdStrength({
      score, rules: { len, upper, num },
      label: score ? lbls[score - 1] + ' password' : 'Enter a password',
      color: clrs[score - 1] || '#E8D5C8',
    });
  };

  // Step 1 submit
  const handleStep1 = async (e) => {
    e.preventDefault();
    const errs = {};
    if (!form.fname)  errs.fname   = 'First name required.';
    if (!form.lname)  errs.lname   = 'Last name required.';
    const age = parseInt(form.age);
    if (!age || age < 18 || age > 70) errs.age = 'Valid age (18–70) required.';
    if (!form.gender) errs.gender  = 'Select a gender.';
    if (!form.dob)    errs.dob     = 'Date of birth required.';
    if (!form.email || !/\S+@\S+\.\S+/.test(form.email)) errs.email = 'Valid email required.';
    if (!form.address) errs.address = 'Address required.';
    if (!ANC_REGEX.test(form.ancid)) {
      errs.ancid = 'Invalid ID format. Use ANM/XX/XXX/YYYY/NNNN.';
      showToast('❌ Invalid ANC Worker ID format.');
      setErrors(errs); return;
    }
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setErrors({});
    setLoading(true);
    await new Promise(r => setTimeout(r, 1400));
    setLoading(false);
    if (!REGISTRY[form.ancid]) {
      setErrors({ ancid: 'ID not found in official registry.' });
      showToast('❌ Worker not found in the official ANC registry.');
      return;
    }
    setVerifiedId(form.ancid);
    setStep(2);
  };

  // Step 2 submit
  const handleStep2 = async (e) => {
    e.preventDefault();
    const errs = {};
    const pwOk = form.pwd.length >= 8 && /[A-Z]/.test(form.pwd) && /[0-9]/.test(form.pwd);
    if (!pwOk)               errs.pwd  = "Password doesn't meet requirements.";
    if (form.pwd !== form.pwd2) errs.pwd2 = 'Passwords do not match.';
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setErrors({});
    setLoading(true);
    await new Promise(r => setTimeout(r, 1600));
    setLoading(false);
    showToast(`✅ Account created! Welcome to NeoSure, ${form.fname} 🌸`);
    setTimeout(() => { setTab('login'); setStep(1); }, 2200);
  };

  // Login submit
  const handleLogin = async (e) => {
    e.preventDefault();
    const errs = {};
    if (!ANC_REGEX.test(form.liAncid)) errs.liAncid = 'Invalid ANC Worker ID format.';
    if (!form.liPwd) errs.liPwd = 'Password is required.';
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setErrors({});
    setLoading(true);
    await new Promise(r => setTimeout(r, 1500));
    setLoading(false);
    showToast('🌿 Welcome back! Redirecting to your dashboard…');
  };

  const goBack = () => { setStep(1); setErrors({}); };

  const overlayClick = (e) => { if (e.target === e.currentTarget) onClose(); };

  return (
    <div className="auth-overlay" onClick={overlayClick}>
      <div className="auth-modal">

        {/* ── TERRACOTTA HEADER ── */}
        <div className="auth-top">
          <div className="auth-top-dots" />
          <button className="auth-close" onClick={onClose}>✕</button>
          <div className="auth-logo-row">
            <div className="auth-logo-dot">🌸</div>
            <div className="auth-logo-name">NeoSure</div>
          </div>
          <h2 className="auth-top-title">
            {tab === 'signup'
              ? <>Empowering Care,<br /><em>One Mother at a Time</em></>
              : <>Welcome Back,<br /><em>Care Provider</em></>}
          </h2>
          <p className="auth-top-sub">
            {tab === 'signup'
              ? 'Register as a certified ANC Worker to monitor maternal health and protect every mother in your care.'
              : 'Sign in to access your maternal health dashboard and ANC risk intelligence tools.'}
          </p>
        </div>

        {/* ── BODY ── */}
        <div className="auth-body">
          {/* Tab pills */}
          <div className="auth-tab-pills">
            <button className={`auth-tab-pill${tab === 'signup' ? ' active' : ''}`} onClick={() => { setTab('signup'); setStep(1); }}>Create Account</button>
            <button className={`auth-tab-pill${tab === 'login'  ? ' active' : ''}`} onClick={() => setTab('login')}>Sign In</button>
          </div>

          {/* ── SIGNUP ── */}
          {tab === 'signup' && (
            <>
              {/* Step indicator */}
              <div className="stp-indicator">
                <div className={`stp-item${step === 1 ? ' active' : ' done'}`}>
                  <div className="stp-num">{step > 1 ? '✓' : '1'}</div>
                  <div className="stp-lbl">Personal Info</div>
                </div>
                <div className={`stp-line${step > 1 ? ' done' : ''}`} />
                <div className={`stp-item${step === 2 ? ' active' : ''}`}>
                  <div className="stp-num">2</div>
                  <div className="stp-lbl">Set Password</div>
                </div>
              </div>

              {/* Step 1 */}
              {step === 1 && (
                <form onSubmit={handleStep1} noValidate>
                  <div className="af-row">
                    <div className="af">
                      <label>First Name <span className="req">*</span></label>
                      <input type="text" value={form.fname} onChange={set('fname')} placeholder="e.g. Priya" className={errors.fname ? 'aerr' : ''} />
                      {errors.fname && <div className="af-err show">{errors.fname}</div>}
                    </div>
                    <div className="af">
                      <label>Last Name <span className="req">*</span></label>
                      <input type="text" value={form.lname} onChange={set('lname')} placeholder="e.g. Sharma" className={errors.lname ? 'aerr' : ''} />
                      {errors.lname && <div className="af-err show">{errors.lname}</div>}
                    </div>
                  </div>
                  <div className="af-row">
                    <div className="af">
                      <label>Age <span className="req">*</span></label>
                      <input type="number" value={form.age} onChange={set('age')} placeholder="e.g. 28" min="18" max="70" className={errors.age ? 'aerr' : ''} />
                      {errors.age && <div className="af-err show">{errors.age}</div>}
                    </div>
                    <div className="af">
                      <label>Gender <span className="req">*</span></label>
                      <select value={form.gender} onChange={set('gender')} className={errors.gender ? 'aerr' : ''}>
                        <option value="">— Select —</option>
                        <option>Female</option><option>Male</option>
                        <option>Other</option><option>Prefer not to say</option>
                      </select>
                      {errors.gender && <div className="af-err show">{errors.gender}</div>}
                    </div>
                  </div>
                  <div className="af-row">
                    <div className="af">
                      <label>Date of Birth <span className="req">*</span></label>
                      <input type="date" value={form.dob} onChange={set('dob')} className={errors.dob ? 'aerr' : ''} />
                      {errors.dob && <div className="af-err show">{errors.dob}</div>}
                    </div>
                    <div className="af">
                      <label>Email <span className="req">*</span></label>
                      <input type="email" value={form.email} onChange={set('email')} placeholder="priya@example.com" className={errors.email ? 'aerr' : ''} />
                      {errors.email && <div className="af-err show">{errors.email}</div>}
                    </div>
                  </div>
                  <div className="af">
                    <label>Address <span className="req">*</span></label>
                    <input type="text" value={form.address} onChange={set('address')} placeholder="e.g. 123, MG Road, Bengaluru" className={errors.address ? 'aerr' : ''} />
                    {errors.address && <div className="af-err show">{errors.address}</div>}
                  </div>
                  <div className="af">
                    <label>ANC Worker ID <span className="req">*</span></label>
                    <input type="text" value={form.ancid} onChange={set('ancid')} placeholder="ANM/KA/BLR/2024/0178" style={{ fontFamily: 'monospace', letterSpacing: '0.05em' }} className={errors.ancid ? 'aerr' : ''} />
                    <div className="af-hint">Format: ANM / State / District / Year / Serial — e.g. <strong>ANM/KA/BLR/2024/0178</strong></div>
                    {errors.ancid && <div className="af-err show">{errors.ancid}</div>}
                  </div>
                  <button type="submit" className={`auth-submit${loading ? ' loading' : ''}`} disabled={loading}>
                    <span className="abtn-text">Verify &amp; Continue →</span>
                    {loading && <span className="aloader" />}
                  </button>
                </form>
              )}

              {/* Step 2 */}
              {step === 2 && (
                <form onSubmit={handleStep2} noValidate>
                  <div className="verified-badge">
                    <div className="vb-icon">✅</div>
                    <div>
                      <div className="vb-title">Identity Verified</div>
                      <div className="vb-id">{verifiedId}</div>
                    </div>
                  </div>
                  <div className="af">
                    <label>Password <span className="req">*</span></label>
                    <div className="pwd-wrap">
                      <input type={showPwd ? 'text' : 'password'} value={form.pwd} onChange={e => { set('pwd')(e); checkStrength(e.target.value); }} placeholder="Create a strong password" className={errors.pwd ? 'aerr' : ''} />
                      <button type="button" className="pwd-toggle" onClick={() => setShowPwd(v => !v)}>
                        <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" style={{ opacity: showPwd ? 0.5 : 1 }}><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                      </button>
                    </div>
                    <div className="str-bar"><div className="str-fill" style={{ width: `${(pwdStrength.score/3)*100}%`, background: pwdStrength.color }} /></div>
                    <div className="str-label" style={{ color: pwdStrength.color }}>{pwdStrength.label}</div>
                    <div className="pwd-rules">
                      {[['len','8+ chars'],['upper','Uppercase'],['num','Number']].map(([k,l]) => (
                        <div key={k} className={`pwd-rule${pwdStrength.rules[k] ? ' pass' : ''}`}>
                          <div className="pwd-rdot" />{l}
                        </div>
                      ))}
                    </div>
                    {errors.pwd && <div className="af-err show">{errors.pwd}</div>}
                  </div>
                  <div className="af">
                    <label>Confirm Password <span className="req">*</span></label>
                    <div className="pwd-wrap">
                      <input type={showPwd2 ? 'text' : 'password'} value={form.pwd2} onChange={set('pwd2')} placeholder="Repeat your password" className={errors.pwd2 ? 'aerr' : ''} />
                      <button type="button" className="pwd-toggle" onClick={() => setShowPwd2(v => !v)}>
                        <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" style={{ opacity: showPwd2 ? 0.5 : 1 }}><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                      </button>
                    </div>
                    {errors.pwd2 && <div className="af-err show">{errors.pwd2}</div>}
                  </div>
                  <div className="chk-row">
                    <input type="checkbox" id="agree" checked={form.agree} onChange={set('agree')} />
                    <label htmlFor="agree">I agree to NeoSure's <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>.</label>
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button type="button" className="auth-back" onClick={goBack}>← Back</button>
                    <button type="submit" className={`auth-submit${loading ? ' loading' : ''}`} disabled={loading} style={{ flex: 1 }}>
                      <span className="abtn-text">Create My Account</span>
                      {loading && <span className="aloader" />}
                    </button>
                  </div>
                </form>
              )}
              <div className="auth-switch" style={{ marginTop: '0.8rem' }}>Already have an account? <a onClick={() => setTab('login')}>Sign in here</a></div>
            </>
          )}

          {/* ── LOGIN ── */}
          {tab === 'login' && (
            <>
              <div className="social-row">
                {/* Google */}
                <button className="social-btn">
                  <svg viewBox="0 0 24 24" fill="none" width="15" height="15"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
                  Continue with Google
                </button>
                {/* Facebook */}
                <button className="social-btn">
                  <svg viewBox="0 0 24 24" fill="#1877F2" width="15" height="15"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                  Continue with Facebook
                </button>
              </div>
              <div className="auth-divider">or sign in with your ANC Worker ID</div>
              <form onSubmit={handleLogin} noValidate>
                <div className="af">
                  <label>ANC Worker ID <span className="req">*</span></label>
                  <input type="text" value={form.liAncid} onChange={set('liAncid')} placeholder="ANM/KA/BLR/2024/0178" style={{ fontFamily: 'monospace', letterSpacing: '0.05em' }} className={errors.liAncid ? 'aerr' : ''} />
                  <div className="af-hint">Format: ANM / State / District / Year / Serial</div>
                  {errors.liAncid && <div className="af-err show">{errors.liAncid}</div>}
                </div>
                <div className="af">
                  <label>Password</label>
                  <div className="pwd-wrap">
                    <input type={showPwd ? 'text' : 'password'} value={form.liPwd} onChange={set('liPwd')} placeholder="Your password" className={errors.liPwd ? 'aerr' : ''} />
                    <button type="button" className="pwd-toggle" onClick={() => setShowPwd(v => !v)}>
                      <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" style={{ opacity: showPwd ? 0.5 : 1 }}><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    </button>
                  </div>
                  {errors.liPwd && <div className="af-err show">{errors.liPwd}</div>}
                </div>
                <div className="forgot-row"><a href="#">Forgot your password?</a></div>
                <div className="chk-row">
                  <input type="checkbox" id="remember" checked={form.remember} onChange={set('remember')} />
                  <label htmlFor="remember">Remember me on this device</label>
                </div>
                <button type="submit" className={`auth-submit${loading ? ' loading' : ''}`} disabled={loading}>
                  <span className="abtn-text">Sign In to My Account</span>
                  {loading && <span className="aloader" />}
                </button>
              </form>
              <div className="trust-badges">
                {[['🔒','Secure Login'],['🌿','Trusted by 45K+'],['⭐','5-Star Rated'],['🤱','ANC Focused']].map(([icon, label]) => (
                  <div key={label} className="tb"><div className="tb-icon">{icon}</div><div className="tb-label">{label}</div></div>
                ))}
              </div>
              <div className="auth-switch">New to NeoSure? <a onClick={() => setTab('signup')}>Create a free account</a></div>
            </>
          )}
        </div>
      </div>

      {/* Toast */}
      <div className={`auth-toast${toast ? ' show' : ''}`}>{toast}</div>
    </div>
  );
}
```

---

*End of specification. Follow this document exactly — every pixel, colour value, font, spacing, animation delay, and interaction has been extracted directly from the live NeoSure HTML source.*
