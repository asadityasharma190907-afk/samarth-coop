import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { StatCounter } from '../components/StatCounter';
import { AuditTable } from '../components/AuditTable';
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
}

export function Federation() {
  const [selectedBookingId, setSelectedBookingId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterSkill, setFilterSkill] = useState('All Skills');
  const [filterStatus, setFilterStatus] = useState('All');

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

  return (
    <div className="federation-container animate-fade-in">
      <header className="federation-header">
        <h1>Ministry / NCCT Federation Dashboard</h1>
        <p>Live metrics and transparency audit logs</p>
      </header>

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
                    <strong>{booking.citizen_name}</strong> requested a <span>{booking.skill}</span>
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
    </div>
  );
}
