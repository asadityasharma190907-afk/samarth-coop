import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Download } from 'lucide-react';
import { api } from '../lib/api';
import { StatCounter } from '../components/StatCounter';
import { AuditTable } from '../components/AuditTable';
import { EarningsChart } from '../components/EarningsChart';
import { VerificationQueue } from '../components/VerificationQueue';
import { DisputesQueue } from '../components/DisputesQueue';
import { FairnessMetricsPanel } from '../components/FairnessMetricsPanel';
import { NetworkDensityPanel } from '../components/NetworkDensityPanel';
import { RevenueAnalyticsPanel } from '../components/RevenueAnalyticsPanel';
import './Federation.css';

interface FederationStats {
  registered_workers: number;
  completed_bookings: number;
  welfare_fund_total: number;
}

interface FederationBooking {
  id: string;
  citizen_name: string;
  skill: string;
  status: string;
  job_price: number;
  platform_fee: number;
  created_at: string;
  worker_name?: string | null;
  dispute_reason?: string | null;
}

export function Federation() {
  const [activeTab, setActiveTab] = useState<
    'overview' | 'impact' | 'density' | 'verifications' | 'disputes' | 'analytics'
  >('overview');
  const [selectedBookingId, setSelectedBookingId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterSkill, setFilterSkill] = useState('All Skills');
  const [filterStatus, setFilterStatus] = useState('All');
  const [isDownloading, setIsDownloading] = useState(false);

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['federationStats'],
    queryFn: async () => {
      const response = await api.get('/federation/stats');
      return response as FederationStats;
    },
    refetchInterval: 10000,
  });

  const { data: bookings, isLoading: bookingsLoading } = useQuery({
    queryKey: ['federationBookings'],
    queryFn: async () => {
      const response = await api.get('/federation/bookings');
      return response as FederationBooking[];
    },
    refetchInterval: 10000,
  });

  const uniqueSkills = useMemo(() => {
    if (!bookings) return [];
    return Array.from(new Set(bookings.map((b) => b.skill)));
  }, [bookings]);

  const filteredBookings = useMemo(() => {
    if (!bookings) return [];
    return bookings.filter((b) => {
      const matchesSearch = b.citizen_name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesSkill = filterSkill === 'All Skills' || b.skill === filterSkill;
      const matchesStatus = filterStatus === 'All' || b.status === filterStatus.toLowerCase();
      return matchesSearch && matchesSkill && matchesStatus;
    });
  }, [bookings, searchQuery, filterSkill, filterStatus]);

  const handleDownloadCSV = async () => {
    try {
      setIsDownloading(true);
      const token = localStorage.getItem('samarth_token');
      const response = await fetch('http://localhost:8000/federation/export-earnings', {
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });

      if (!response.ok) {
        throw new Error('Failed to download CSV');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'samarth_weekly_earnings_report.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download CSV error:', err);
      alert('Error downloading CSV report. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="federation-container animate-fade-in">
      <header className="federation-header">
        <h1>Ministry / NCCT Federation Dashboard</h1>
        <p>Live metrics, fairness analytics, and transparency audit logs</p>
      </header>

      <nav className="federation-nav-tabs" aria-label="Dashboard sections">
        <button
          className={`federation-tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview & Dispatch
        </button>
        <button
          className={`federation-tab-btn ${activeTab === 'density' ? 'active' : ''}`}
          onClick={() => setActiveTab('density')}
        >
          Network Density
        </button>
        <button
          className={`federation-tab-btn ${activeTab === 'impact' ? 'active' : ''}`}
          onClick={() => setActiveTab('impact')}
        >
          Impact & Income Fairness
        </button>
        <button
          className={`federation-tab-btn ${activeTab === 'verifications' ? 'active' : ''}`}
          onClick={() => setActiveTab('verifications')}
        >
          Verification Queue
        </button>
        <button
          className={`federation-tab-btn ${activeTab === 'disputes' ? 'active' : ''}`}
          onClick={() => setActiveTab('disputes')}
        >
          Disputes
        </button>
        <button
          className={`federation-tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          Business Analytics
        </button>
      </nav>

      {activeTab === 'density' && <NetworkDensityPanel />}

      {activeTab === 'impact' && <FairnessMetricsPanel />}

      {activeTab === 'verifications' && (
        <section className="verification-section">
          <VerificationQueue />
        </section>
      )}

      {activeTab === 'disputes' && (
        <section className="disputes-section">
          {bookingsLoading ? (
            <div className="loading-state">Loading active disputes...</div>
          ) : (
            <DisputesQueue bookings={bookings || []} />
          )}
        </section>
      )}

      {activeTab === 'analytics' && <RevenueAnalyticsPanel />}

      {activeTab === 'overview' && (
        <>
          <NetworkDensityPanel />
          {statsLoading ? (
            <div className="loading-state">Loading metrics...</div>
          ) : (
            <div className="stats-grid">
              <StatCounter label="Registered Workers" value={stats?.registered_workers || 0} />
              <StatCounter label="Completed Bookings" value={stats?.completed_bookings || 0} />
              <StatCounter
                label="Cooperative Welfare Fund"
                value={stats?.welfare_fund_total || 0}
                prefix="₹"
                isViolet={true}
              />
            </div>
          )}

          <section className="earnings-section">
            <div className="earnings-section-actions">
              <button
                className="btn-download-csv"
                onClick={handleDownloadCSV}
                disabled={isDownloading}
              >
                <Download size={16} />
                {isDownloading ? 'Generating CSV...' : 'Download CSV Report'}
              </button>
            </div>
            <EarningsChart />
          </section>

          <div className="dashboard-content">
            <section className="bookings-section">
              <h2>Recent Bookings</h2>

              <div className="filter-toolbar">
                <input
                  type="text"
                  placeholder="Search by citizen name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="search-input"
                />

                <div className="filter-controls">
                  <select
                    value={filterSkill}
                    onChange={(e) => setFilterSkill(e.target.value)}
                    className="skill-select"
                  >
                    <option value="All Skills">All Skills</option>
                    {uniqueSkills.map((skill) => (
                      <option key={skill} value={skill}>
                        {skill}
                      </option>
                    ))}
                  </select>

                  <div className="status-chips">
                    {['All', 'Completed', 'Assigned', 'Cancelled', 'Pending'].map((status) => (
                      <button
                        key={status}
                        className={`status-chip ${filterStatus === status ? 'active' : ''}`}
                        onClick={() => setFilterStatus(status)}
                      >
                        {status}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {bookingsLoading ? (
                <div className="loading-state">Loading bookings...</div>
              ) : (
                <div className="bookings-list">
                  {filteredBookings.map((booking) => (
                    <div
                      key={booking.id}
                      className={`booking-item ${selectedBookingId === booking.id ? 'active' : ''}`}
                      onClick={() => setSelectedBookingId(booking.id)}
                    >
                      <div className="booking-info">
                        <strong>{booking.citizen_name}</strong> requested a{' '}
                        <span>{booking.skill}</span>
                      </div>
                      <div className="booking-meta">
                        <span className={`status-badge status-${booking.status}`}>
                          {booking.status}
                        </span>
                        <span className="time">
                          {new Date(booking.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))}
                  {filteredBookings.length === 0 && <p>No matching bookings found.</p>}
                </div>
              )}
            </section>

            <section className="audit-section">
              <h2>Dispatch Audit Trail</h2>
              <p className="audit-subtitle">
                Click a booking on the left to see the dispatch algorithm decisions.
              </p>

              {selectedBookingId ? (
                <AuditTable bookingId={selectedBookingId} />
              ) : (
                <div className="empty-audit-state">
                  <p>Select a booking to view its audit trail.</p>
                </div>
              )}
            </section>
          </div>
        </>
      )}
    </div>
  );
}
