import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Check,
  X,
  Scale,
  HeartHandshake,
  Building2,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';
import './WhySamarth.css';

interface ComparisonRow {
  dimension: string;
  samarth: string;
  urbanCompany: string;
  localContractor: string;
  isBoolean?: boolean;
}

const COMPARISON_DATA: ComparisonRow[] = [
  {
    dimension: 'Platform cut',
    samarth: '5%',
    urbanCompany: '25-30%',
    localContractor: '0%*',
  },
  {
    dimension: 'Price transparency',
    samarth: 'Fixed before booking',
    urbanCompany: 'Inspect-then-quote',
    localContractor: 'Verbal haggling',
  },
  {
    dimension: 'Lowest earner gets next job',
    samarth: 'Yes',
    urbanCompany: 'No',
    localContractor: 'No',
    isBoolean: true,
  },
  {
    dimension: 'Worker owns platform',
    samarth: 'Yes (cooperative)',
    urbanCompany: 'No (VC-backed)',
    localContractor: 'No',
  },
  {
    dimension: 'Dispute proof (photo)',
    samarth: 'Yes',
    urbanCompany: 'No',
    localContractor: 'No',
    isBoolean: true,
  },
  {
    dimension: 'Welfare fund',
    samarth: 'Yes (2.5% every job)',
    urbanCompany: 'No',
    localContractor: 'No',
  },
  {
    dimension: 'Government backing',
    samarth: 'Ministry of Cooperation',
    urbanCompany: 'None',
    localContractor: 'None',
  },
  {
    dimension: 'Dispatch audit trail',
    samarth: 'Yes',
    urbanCompany: 'No',
    localContractor: 'No',
    isBoolean: true,
  },
];

export function WhySamarth() {
  const navigate = useNavigate();

  const renderCellContent = (value: string) => {
    if (value === 'Yes') {
      return (
        <span className="table-tag tag-success">
          <Check size={14} /> Yes
        </span>
      );
    }
    if (value === 'No') {
      return (
        <span className="table-tag tag-neutral">
          <X size={14} /> No
        </span>
      );
    }
    return value;
  };

  return (
    <div className="why-samarth-page">
      {/* Navigation Header */}
      <nav className="why-samarth-nav">
        <Link to="/login" className="why-samarth-brand">
          <span>🌿 Samarth</span>
        </Link>
        <div className="why-samarth-nav-actions">
          <button onClick={() => navigate('/login')} className="nav-back-link">
            <ArrowLeft size={16} /> Back to Login
          </button>
          <Link to="/register" className="nav-cta-btn">
            Join Cooperative
          </Link>
        </div>
      </nav>

      <main className="why-samarth-container">
        {/* Hero Section */}
        <section className="why-samarth-hero">
          <div className="why-samarth-badge">
            <ShieldCheck size={14} /> SIH Problem #26089 | Ministry of Cooperation / NCCT
          </div>
          <h1 className="why-samarth-title">The platform Urban Company cannot build.</h1>
          <p className="why-samarth-subtitle">
            Samarth aligns incentives across citizens, workers, and government. A cooperative gig
            platform engineered for fair income distribution, complete price transparency, and
            worker ownership.
          </p>
        </section>

        {/* Comparison Table Section */}
        <section className="comparison-section">
          <div className="comparison-table-wrapper">
            <table className="comparison-table">
              <thead>
                <tr>
                  <th style={{ width: '28%' }}>Dimension</th>
                  <th className="col-samarth" style={{ width: '26%' }}>
                    🌿 Samarth
                  </th>
                  <th style={{ width: '23%' }}>Urban Company</th>
                  <th style={{ width: '23%' }}>Local Contractor</th>
                </tr>
              </thead>
              <tbody>
                {COMPARISON_DATA.map((row, index) => (
                  <tr key={index}>
                    <td className="dimension-name">{row.dimension}</td>
                    <td className="col-samarth">{renderCellContent(row.samarth)}</td>
                    <td>{renderCellContent(row.urbanCompany)}</td>
                    <td>{renderCellContent(row.localContractor)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="table-footnote">
              * "0% cut" hides worker exploitation: unpredictable price negotiations, zero
              insurance, zero social safety net, and unprotected dispute risks.
            </div>
          </div>
        </section>

        {/* Narrative Deep Dive Pillars */}
        <section className="pillars-grid">
          {/* Pillar 1 */}
          <div className="pillar-card">
            <div className="pillar-icon-wrapper icon-brand">
              <Scale size={24} />
            </div>
            <h2 className="pillar-title">Our Algorithm is Fairness</h2>
            <p className="pillar-desc">
              Extractive platforms optimize solely for distance and commission maximization.
              Samarth’s dispatch algorithm directly penalizes income inequality by prioritizing
              qualified workers who have earned the least this week.
            </p>
            <div className="formula-box">
              Score = (5000 − WeeklyEarnings) × 2 + (1000 × Rating) − (500 × Distance_km) − Penalty
            </div>
            <div className="case-study-box">
              <strong>Demo Proof Point:</strong> Meena Verma is closest (0.3 km) and highest rated
              (4.9★), but has earned ₹4,500 this week. Suresh Kumar (₹200 earnings) ranks #1. The
              closest worker doesn’t always win — the one who needs work most does.
            </div>
          </div>

          {/* Pillar 2 */}
          <div className="pillar-card">
            <div className="pillar-icon-wrapper icon-purple">
              <HeartHandshake size={24} />
            </div>
            <h2 className="pillar-title">The Cooperative Difference</h2>
            <p className="pillar-desc">
              Gig workers are not independent contractors with VC take-rates; they are member-owners
              of the cooperative. 95% of job revenue goes straight into the worker’s pocket.
            </p>
            <p className="pillar-desc">
              Every job automatically routes 2.5% into a transparent Cooperative Welfare Fund,
              providing accidental insurance, emergency medical relief, and skill certifications
              managed directly by the district cooperative union.
            </p>
            <div className="payout-breakdown-row">
              <div className="payout-stat-card">
                <div className="payout-stat-val-brand">95%</div>
                <div className="payout-stat-lbl">Worker Payout</div>
              </div>
              <div className="payout-stat-card">
                <div className="payout-stat-val-welfare">2.5%</div>
                <div className="payout-stat-lbl">Welfare Fund</div>
              </div>
              <div className="payout-stat-card">
                <div className="payout-stat-val-neutral">5%</div>
                <div className="payout-stat-lbl">Platform Cut</div>
              </div>
            </div>
          </div>

          {/* Pillar 3 */}
          <div className="pillar-card">
            <div className="pillar-icon-wrapper icon-amber">
              <Building2 size={24} />
            </div>
            <h2 className="pillar-title">Built for Bharat</h2>
            <p className="pillar-desc">
              Designed in alignment with the Ministry of Cooperation and the National Council for
              Cooperative Training (NCCT). Samarth connects Tier-2 and Tier-3 urban local bodies,
              primary cooperative societies, and self-help groups.
            </p>
            <p className="pillar-desc">
              With full photo dispute verification, fixed upfront quotes, Aadhaar verification, and
              immutable dispatch audit logs, citizens get dependable services while workers earn
              dignified, sustainable livelihoods.
            </p>
            <div className="district-scale-row">
              <TrendingUp size={20} color="var(--color-brand-accent)" />
              <span className="district-scale-text">Scalable across 750+ districts nationwide</span>
            </div>
          </div>
        </section>

        {/* Bottom CTA Banner */}
        <section className="why-samarth-cta-banner">
          <h2 className="cta-banner-title">Experience the Cooperative Advantage</h2>
          <p className="cta-banner-subtitle">
            Join thousands of citizens and service professionals building India's first fair,
            transparent gig cooperative.
          </p>
          <div className="cta-banner-actions">
            <Link to="/register" className="cta-button-white">
              Create an Account
            </Link>
            <Link to="/login" className="cta-button-outline">
              Sign In to Demo
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}

export default WhySamarth;
