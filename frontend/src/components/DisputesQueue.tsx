import React, { useState } from 'react';
import { AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import './DisputesQueue.css';

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

interface DisputesQueueProps {
  bookings: FederationBooking[];
}

export function DisputesQueue({ bookings }: DisputesQueueProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const disputes = bookings.filter((b) => b.status === 'disputed');

  const toggleExpand = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="disputes-queue-container">
      <div className="disputes-queue-header">
        <AlertCircle className="disputes-icon" size={24} />
        <h2>Platform Dispute Oversight</h2>
      </div>

      {disputes.length === 0 ? (
        <div className="empty-disputes-state">
          <p>No active disputes. Cooperative operations nominal.</p>
        </div>
      ) : (
        <div className="disputes-table-container">
          <table className="disputes-table">
            <thead>
              <tr>
                <th>Booking ID</th>
                <th>Citizen</th>
                <th>Worker</th>
                <th>Service</th>
                <th>Status</th>
                <th>Date</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {disputes.map((dispute) => {
                const isExpanded = expandedId === dispute.id;
                return (
                  <React.Fragment key={dispute.id}>
                    <tr
                      className={`dispute-row ${isExpanded ? 'expanded' : ''}`}
                      onClick={() => toggleExpand(dispute.id)}
                    >
                      <td className="booking-id-cell">{dispute.id.substring(0, 8)}...</td>
                      <td>{dispute.citizen_name}</td>
                      <td>{dispute.worker_name || 'N/A'}</td>
                      <td>{dispute.skill}</td>
                      <td>
                        <span className="disputed-chip">Disputed</span>
                      </td>
                      <td>{new Date(dispute.created_at).toLocaleDateString()}</td>
                      <td className="expand-cell">
                        {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                      </td>
                    </tr>
                    {isExpanded && (
                      <tr className="dispute-details-row">
                        <td colSpan={7}>
                          <div className="dispute-details">
                            <div className="dispute-reason-box">
                              <strong>Dispute Reason:</strong>
                              <p>{dispute.dispute_reason || 'No reason provided.'}</p>
                            </div>
                            <div className="dispute-metadata">
                              <div>
                                <strong>Job Price:</strong> ₹{dispute.job_price}
                              </div>
                              <div>
                                <strong>Platform Fee:</strong> ₹{dispute.platform_fee}
                              </div>
                              <div>
                                <strong>Full ID:</strong> {dispute.id}
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
